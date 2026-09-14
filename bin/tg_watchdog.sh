#!/bin/bash
# Watchdog del puente de Telegram (agentes Claude Code en tmux).
#
# Por qué existe: el puente lo levanta el AGENTE con la herramienta Monitor, y la
# única orden que se lo pide es el prompt de despertar que el entrypoint inyecta una
# sola vez. Si ese turno muere —el 29-jul-2026 fue un `API Error: 529 Overloaded` en
# edo1 y edo3— el prompt ya se consumió, nadie reintenta, y el agente queda SORDO con
# el contenedor en `Up`, la sesión viva y en bypass. Los mensajes se acumulan en la
# cola de Telegram y quien escribe cree que el agente está caído.
#
# Qué hace: cada INTERVAL segundos comprueba que haya un `bin/tg_bridge.sh` corriendo.
# Si no hay, limpia el lock huérfano y le reinyecta al agente, por tmux, la orden de
# levantar el puente. Corre DENTRO del contenedor, sin acceso al host.
#
# Deliberadamente NO levanta el puente él mismo: un tg_bridge.sh fuera de la sesión
# consumiría los updates y los mensajes se perderían de verdad. Tiene que ser el
# agente, con Monitor.
set -u

# Contexto: env del exec/entrypoint y, como respaldo, el del pid 1 (así el script
# sirve igual lanzado a mano con `docker exec` que desde el entrypoint).
pid1_env() { tr '\0' '\n' < /proc/1/environ 2>/dev/null | sed -n "s/^$1=//p" | head -1; }

WS="${AGENT_WORKSPACE:-$(pid1_env AGENT_WORKSPACE)}"
SESSION="${AGENT_TMUX:-$(pid1_env AGENT_TMUX)}"
[ -n "${SESSION:-}" ] || SESSION=$(tmux ls 2>/dev/null | head -1 | cut -d: -f1)
SD="${TG_STATE_DIR:-$(pid1_env TG_STATE_DIR)}"
if [ -z "${SD:-}" ]; then
  # Sin TG_STATE_DIR en el entorno, el puente usa $HOME/tgstate; pero hay agentes
  # (jesus2) donde el estado vive en el workspace. Se elige el que exista de verdad.
  for cand in "$WS/tgstate" "$HOME/.claude/tgstate" "$HOME/tgstate"; do
    [ -n "$cand" ] && [ -d "$cand" ] && { SD="$cand"; break; }
  done
fi
[ -n "${SD:-}" ] || SD="$HOME/.claude/tgstate"
LOG="${TG_WATCHDOG_LOG:-$HOME/.claude/tg_watchdog.log}"

GRACE="${TG_WATCHDOG_GRACE:-300}"        # margen inicial: que el despertar tenga su turno
INTERVAL="${TG_WATCHDOG_INTERVAL:-120}"
COOLDOWN="${TG_WATCHDOG_COOLDOWN:-600}"  # tras reinyectar, no insiste antes de esto

# El watchdog sirve en los DOS mundos. En un agente sin migrar, vigilar
# "tg_tail.sh main" seria vigilar algo que no existe, y lo estaria mandando a
# levantar un consumidor sin cola cada dos minutos. El centinela
# MIGRADO_A_POLLER decide, y es el MISMO que usan el entrypoint y el guard del
# puente, asi que los tres cambian de mundo juntos.
if [ -f "$SD/MIGRADO_A_POLLER" ]; then
PROMPT="WATCHDOG: nadie esta consumiendo los mensajes de tu duena o dueno, o sea si te escribe va a creer que estas caido. TRES prohibiciones antes de actuar: (a) JAMAS levantes bin/tg_bridge.sh -- esta muerto, y un token admite un solo getUpdates, asi que le darias 409 al poller y quedarias sordo de verdad; (b) JAMAS levantes bin/tg_tail_all.py; (c) JAMAS levantes un tg_tail.sh topic-<numero> -- esos son de las sesiones de tema y les robarias los mensajes, porque el cursor es por destino y lo avanza el primero que lee. Lo tuyo es SOLO el chat privado y el General. Haz esto: 1) Si no hay un tg_poller.py corriendo, relanzalo desasido con 'setsid nohup bash bin/tg_poller_keep.sh >/dev/null 2>&1 &' (NO va con Monitor: no debe morir con tu sesion). 2) Levanta con la herramienta Monitor, persistentes, los DOS consumidores que te tocan, y nada mas en este turno (jamas un Bash en background; el footer debe decir monitor): 'bash bin/tg_tail.sh main' y 'bash bin/tg_tail.sh topic-general'. 3) Al arrancar te entregan lo que quedo sin leer, con la etiqueta del destino y el comando exacto para responder ahi; usa ese comando. Si estuviste caido un buen rato, pide disculpas en una linea por la demora, sin tecnicismos. 4) Si necesitas reiniciar una sesion tmux usa SIEMPRE 'tmux kill-session -t <nombre>', JAMAS kill-server: se llevaria todas las sesiones del contenedor, incluida la tuya y las de los temas."
PAT_DEF="[t]g_tail.sh main"
else
PROMPT="WATCHDOG: tu puente de Telegram no esta corriendo, o sea nadie esta leyendo los mensajes de tu duena o dueno y quien te escriba va a creer que estas caido. Levantalo AHORA con la herramienta Monitor y nada mas en este turno (jamas un Bash en background; el footer debe decir monitor): bash bin/tg_bridge.sh. Despues revisa si quedaron mensajes sin leer en la cola y respondelos; si estuviste caido un buen rato, pide disculpas en una linea por la demora, sin tecnicismos."
PAT_DEF="[t]g_bridge.sh"
fi

log() { printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >> "$LOG"; }

# Patrón en bracket: si no, el propio grep/subshell se autocuenta y el puente
# parecería vivo siempre (así me equivoqué en el primer barrido de la flota).
# TG_WATCHDOG_PAT existe para poder ensayar el camino de "puente ausente" sin tener
# que matar el puente real (se apunta a un patrón que no existe).
BRIDGE_PAT="${TG_WATCHDOG_PAT:-$PAT_DEF}"
bridge_up() { [ "$(ps -eo args 2>/dev/null | grep -c "$BRIDGE_PAT")" -gt 0 ]; }

# Heurístico de la TUI: mientras el agente trabaja, el footer dice "esc to interrupt".
# Inyectar ahí solo encolaría mensajes; mejor esperar a que quede libre. Si el footer
# cambia en una versión futura, el peor caso es volver a inyectar siempre — el
# cooldown sigue conteniendo el ruido.
agent_busy() {
  tmux capture-pane -p -t "$SESSION" -S -3 2>/dev/null | grep -q 'esc to interrupt'
}

[ -n "${SESSION:-}" ] || { echo "tg_watchdog: no hay sesion tmux, salgo" >&2; exit 1; }
cd "${WS:-$HOME}" 2>/dev/null || true

sleep "$GRACE"
log "watchdog arriba (sesion=$SESSION ws=${WS:-?} grace=${GRACE}s interval=${INTERVAL}s cooldown=${COOLDOWN}s)"

LAST_FIX=0
while true; do
  if ! bridge_up; then
    NOW=$(date +%s)
    if [ $((NOW - LAST_FIX)) -lt "$COOLDOWN" ]; then
      :
    elif agent_busy; then
      log "puente ausente pero el agente esta ocupado: espero a que termine el turno"
    else
      PIDL=$(cat "$SD/tg_bridge.lock.d/pid" 2>/dev/null || true)
      # El lock vive en un bind mount y sobrevive al reinicio del contenedor. Tras un
      # reinicio los PIDs arrancan bajos, así que un pid huérfano puede coincidir con
      # otro proceso vivo y el puente se negaría a arrancar ("ya hay un puente activo").
      if [ -n "$PIDL" ] && ! kill -0 "$PIDL" 2>/dev/null; then
        rm -rf "$SD/tg_bridge.lock.d" && log "lock huerfano (pid $PIDL) eliminado"
      fi
      tmux send-keys -t "$SESSION" -l "$PROMPT"
      sleep 1
      tmux send-keys -t "$SESSION" Enter
      LAST_FIX=$NOW
      log "puente ausente -> orden de levantarlo reinyectada en tmux '$SESSION'"
    fi
  fi
  sleep "$INTERVAL"
done
