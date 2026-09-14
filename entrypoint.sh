#!/bin/bash
# Entrypoint del agente (variante Claude Code): sesión Claude Code VIVA en tmux.
# El agente levanta su propio puente de Telegram al despertar (herramienta Monitor).
set -u
export PATH="$HOME/.local/bin:$PATH"
WS="${AGENT_WORKSPACE:-/home/agent/workspace}"
SESSION="${AGENT_TMUX:-agent}"
TGSD="${TG_STATE_DIR:-$HOME/.claude/tgstate}"
mkdir -p "$TGSD"

# --- contexto del esquema multi-tema (poller + spawner) ---
# Van como export porque los dos arrancan DESASIDOS: heredan este entorno y nada
# mas. Sin TG_ENV_FILE el poller busca el .env por su default, y sin
# AGENT_WORKSPACE el spawner nace apuntando al workspace equivocado; ninguno de
# los dos avisa, fallan en silencio con el contenedor en "Up".
export AGENT_WORKSPACE="$WS"
export AGENT_TMUX="$SESSION"
export TG_ENV_FILE="${TG_ENV_FILE:-$WS/.env}"
export TG_STATE_DIR="$TGSD"
# Techo de sesiones de tema. Cada sesion Claude pesa medio giga largo: con 4 GB
# de mem_limit entran ~3, con 10 GB unas 5. El spawner ademas mira la RAM viva
# del cgroup y se planta antes de dejar el contenedor sin aire, y LOGUEA lo que
# rechaza en vez de recortar en silencio.
export TG_MAX_TOPIC_SESSIONS="${TG_MAX_TOPIC_SESSIONS:-3}"

# 1) Memoria del proyecto -> workspace (symlink idempotente; el slug replica la ruta)
SLUG=$(echo "$WS" | sed 's/[^a-zA-Z0-9]/-/g')
PROJ="$HOME/.claude/projects/$SLUG"
mkdir -p "$PROJ"
if [ ! -L "$PROJ/memory" ]; then
  rm -rf "$PROJ/memory"
  mkdir -p "$WS/memory"
  ln -s "$WS/memory" "$PROJ/memory"
fi

# 2) Merge de variables de entorno del contenedor (p.ej. panel del hosting via
#    env_file) hacia el .env del workspace, para usarlas también como archivo.
python3 - <<'PY'
import os, re
ws = os.environ.get("AGENT_WORKSPACE", "/home/agent/workspace")
env_path = os.path.join(ws, ".env")
BLOCK = {"PATH","HOME","HOSTNAME","TERM","PWD","OLDPWD","SHLVL","LANG","TZ","_",
         "AGENT_WORKSPACE","AGENT_TMUX","TG_TOKEN_VAR","TG_STATE_DIR","TG_OWNER_ID",
         "PANEL_ENV_FILE","DEBIAN_FRONTEND"}
try:
    lines = open(env_path).read().splitlines()
except OSError:
    lines = []
merged = []
for name, value in sorted(os.environ.items()):
    if (name in BLOCK or name.startswith("LC_")
            or not re.fullmatch(r"[A-Z][A-Z0-9_]*", name)
            or not value.strip() or "\n" in value or '"' in value):
        continue
    rendered = f'{name}="{value}"' if (" " in value or "#" in value) else f"{name}={value}"
    for i, line in enumerate(lines):
        if line.startswith(name + "="):
            if line != rendered:
                lines[i] = rendered
                merged.append(name)
            break
    else:
        lines.append(rendered)
        merged.append(name)
if merged:
    tmp = env_path + ".tmp-merge"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(tmp, 0o600)
    os.replace(tmp, env_path)
    print("env-merge:", ", ".join(merged), flush=True)
else:
    print("env-merge: sin cambios", flush=True)
PY

# 3) Primera vez: inicializar el offset de Telegram al presente (sin backlog viejo)
if [ ! -s "$TGSD/tg_offset" ]; then
  TOKVAR="${TG_TOKEN_VAR:-TELEGRAM_BOT_TOKEN}"
  TG=$(grep -m1 "^${TOKVAR}=" "$WS/.env" | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"'"'"' \r')
  OFF=$(curl -s --max-time 20 "https://api.telegram.org/bot${TG}/getUpdates?offset=-1&timeout=1" \
    | python3 -c "import sys,json; r=json.load(sys.stdin).get('result',[]); print(r[-1]['update_id']+1 if r else 0)" 2>/dev/null || echo 0)
  echo "${OFF:-0}" > "$TGSD/tg_offset"
  echo "tg_offset inicializado en ${OFF:-0}"
fi

# 4) Claude Code interactivo en tmux, auto-manejando los diálogos iniciales
# Poller de Telegram (solo si el agente migro al esquema multi-tema). Es el
# unico dueno del token -- uno admite un solo getUpdates -- y arranca DESASIDO
# para sobrevivir a /new, a la rotacion y a que la sesion se cuelgue; con la
# herramienta Monitor moriria con ella, que es justo lo que vino a resolver.
# Va antes de la sesion a proposito: lo que llegue durante el boot queda en el
# inbox y el agente lo recupera al enganchar su consumidor.
# El SPAWNER no va aca: crea sesiones tmux y el kill-server de abajo se las
# llevaria recien nacidas.
if [ -f "$TGSD/MIGRADO_A_POLLER" ]; then
  pgrep -f "[t]g_poller" >/dev/null \
    || setsid nohup bash "$WS/bin/tg_poller_keep.sh" >/dev/null 2>&1 < /dev/null &
  echo "poller lanzado (esquema multi-tema)"
fi

# OJO: kill-server aca es correcto porque el contenedor arranca limpio. En
# caliente JAMAS: se llevaria tambien las sesiones tema-* de los temas.
tmux kill-server 2>/dev/null || true
tmux new-session -d -s "$SESSION" -x 220 -y 50 "cd $WS && claude --dangerously-skip-permissions"

for _ in $(seq 1 45); do
  sleep 2
  PANE=$(tmux capture-pane -t "$SESSION" -p 2>/dev/null || true)
  if printf '%s' "$PANE" | grep -qi "bypass permissions mode"; then
    tmux send-keys -t "$SESSION" "2"; sleep 0.5; tmux send-keys -t "$SESSION" Enter; continue
  fi
  if printf '%s' "$PANE" | grep -qiE "choose the text style|press enter to continue|trust this folder|quick safety check|1\. Yes"; then
    tmux send-keys -t "$SESSION" Enter; continue
  fi
  if printf '%s' "$PANE" | grep -qE '\? for shortcuts|bypass permissions on'; then
    break
  fi
done

# 5) Prompt de arranque (UNA sola línea; personalizable via STARTUP.txt en el workspace)
sleep 2
if [ -f "$WS/STARTUP.txt" ]; then
  STARTUP=$(tr '\n' ' ' < "$WS/STARTUP.txt")
elif [ -f "$TGSD/MIGRADO_A_POLLER" ]; then
  # Esquema multi-tema: el puente viejo se NIEGA a arrancar, asi que el prompt
  # de siempre dejaria al agente sin ningun consumidor -- sordo con el
  # contenedor en "Up".
  STARTUP="Despertar: eres el agente 24/7 de este contenedor. Haz esto en orden: (1) cd $WS y lee CLAUDE.md completo -- ahi estan tu identidad, objetivo y reglas. (2) Levanta AHORA con la herramienta Monitor (persistentes, JAMAS un Bash en background; el footer debe decir monitor) los DOS consumidores que te tocan: bash bin/tg_tail.sh main y bash bin/tg_tail.sh topic-general. TRES prohibiciones: JAMAS bin/tg_bridge.sh (esta muerto; un token admite un solo getUpdates y le darias 409 al poller, quedandote sordo de verdad), JAMAS bin/tg_tail_all.py y JAMAS un tg_tail.sh topic-<numero> (esos temas los atienden OTRAS sesiones y les robarias los mensajes: el cursor es por destino y lo avanza el primero que lee). (3) Cada evento trae su destino y el comando exacto para responder ahi: USA ESE COMANDO, no lo deduzcas, o tu respuesta cae en otro tema y el dueno no la ve donde la espera. Formato SIEMPRE tags HTML (<b>, <i>, <code>, <a>), NUNCA Markdown: los ## y ** llegan crudos al telefono. Parrafos cortos, negritas en cifras y nombres, listas con punto medio. (4) [TG-CMD] model o effort: bash bin/tg_model.sh <tipo> <arg>. [TG-CMD] new: bash bin/tg_new.sh y nada mas ese turno. [TG-CMD] env: bash bin/tg_env.sh <VAR> <valfile> <force> <msg_id> y reporta SIN mencionar el valor. (5) NO envies ningun mensaje de saludo ni aviso de reinicio: arranca EN SILENCIO. Si al arrancar te entregan mensajes atrasados y estuviste caido un buen rato, pide disculpas en una linea por la demora, sin tecnicismos. Lo que te entregue tu consumidor al arrancar son los mensajes que quedaron SIN LEER mientras no estabas: ATIENDELOS, no los descartes por ser anteriores a tu arranque (el cursor por destino ya garantiza que ninguna otra sesion los contesto). Si estuviste caido un buen rato, reconocelo en una linea y sigue directo con lo que te pidieron. Fuera de eso, no inventes actividad previa."
else
  STARTUP="Despertar: eres el agente 24/7 de este contenedor. Haz esto en orden: (1) cd $WS y lee CLAUDE.md completo — ahí están tu identidad, objetivo y reglas. (2) Levanta AHORA el puente de Telegram con la herramienta Monitor (JAMAS un Bash en background; el footer debe decir monitor): bash $WS/bin/tg_bridge.sh — cada línea que emita es un evento: [TG] mensaje del dueño, [TG-CMD] comando, [TG-ALERT] chat no autorizado (reportar sin contenido). (3) Responde los [TG] con: bash bin/tg.sh send '<respuesta con tags HTML>' — SIEMPRE tags HTML (<b>, <i>, <code>, <a>), NUNCA Markdown: los ## y ** llegan crudos al teléfono. Párrafos cortos, negritas en cifras y nombres, listas con punto medio. (4) [TG-CMD] model o effort: bash bin/tg_model.sh <tipo> <arg>. [TG-CMD] new: bash bin/tg_new.sh y nada más ese turno. [TG-CMD] env: bash bin/tg_env.sh <VAR> <valfile> <force> <msg_id> y reporta SIN mencionar el valor. (5) NO envíes ningún mensaje de saludo ni aviso de reinicio: arranca EN SILENCIO. Un reinicio no es noticia para el dueño y le molesta recibirlo cada día. Responde solo cuando (a) llegue un [TG] suyo, o (b) un cron o loop programado te haga trabajar y ese trabajo amerite avisarle. Si el arranque falla, eso sí se reporta. Lo que te entregue tu consumidor al arrancar son los mensajes que quedaron SIN LEER mientras no estabas: ATIENDELOS, no los descartes por ser anteriores a tu arranque (el cursor por destino ya garantiza que ninguna otra sesion los contesto). Si estuviste caido un buen rato, reconocelo en una linea y sigue directo con lo que te pidieron. Fuera de eso, no inventes actividad previa."
fi
tmux send-keys -t "$SESSION" -l "$STARTUP"
sleep 1
tmux send-keys -t "$SESSION" Enter

# 5b) Spawner de temas: DESPUES de la sesion principal, para que el kill-server de
#     arriba no se lleve las sesiones tema-* recien creadas. Abre una sesion
#     Claude por cada tema del grupo, o sea una conversacion paralela por tema.
if [ -f "$TGSD/MIGRADO_A_POLLER" ] && grep -q "^TELEGRAM_GROUP_ID=" "$WS/.env" 2>/dev/null; then
  pgrep -f "[t]g_topic_spawner" >/dev/null \
    || setsid nohup python3 "$WS/bin/tg_topic_spawner.py" >/dev/null 2>&1 < /dev/null &
  echo "spawner de temas lanzado"
fi

# 5b) Scheduler interno de crons del agente (self-service sin acceso al host)
pgrep -f agent_cron.py >/dev/null || setsid python3 "$WS/bin/agent_cron.py" >> "$HOME/.claude/agent_cron.log" 2>&1 < /dev/null &

# 5c) Watchdog del puente de Telegram: el prompt de arranque es la UNICA orden que
#     levanta el puente; si ese turno muere (p.ej. "API Error: 529 Overloaded") nadie
#     reintenta y el agente queda sordo con el contenedor en "Up".
pgrep -f tg_watchdog.sh >/dev/null || setsid bash "$WS/bin/tg_watchdog.sh" >/dev/null 2>&1 < /dev/null &


# 6) Mantener vivo el contenedor; si tmux muere, salir para que restart: unless-stopped relance todo
while true; do
  sleep 30
  tmux has-session -t "$SESSION" 2>/dev/null || exit 1
  pgrep -f tg_watchdog.sh >/dev/null || setsid bash "$WS/bin/tg_watchdog.sh" >/dev/null 2>&1 < /dev/null &
  pgrep -f agent_cron.py >/dev/null || setsid python3 "$WS/bin/agent_cron.py" >> "$HOME/.claude/agent_cron.log" 2>&1 < /dev/null &
done
