#!/bin/bash
# Consumidor de UN destino del poller. Esto es lo que cada sesion Claude corre
# con la herramienta Monitor, en lugar de tg_bridge.sh.
#
#   bash bin/tg_tail.sh main          -> chat privado (comportamiento historico)
#   bash bin/tg_tail.sh topic-42      -> su tema del grupo
#   bash bin/tg_tail.sh control       -> eventos de temas (para el supervisor)
#
# Diferencia clave contra tg_bridge.sh: NO habla con Telegram. Solo lee el
# archivo que le llena el poller. Por eso puede morir y revivir sin perder nada
# y sin pelearse por el token (un token = un getUpdates, si no Telegram da 409).
#
# El cursor por destino es lo que recupera lo perdido: al arrancar emite todo lo
# que entro mientras la sesion estaba caida, en vez de dejarlo colgado en la cola
# de Telegram como hacia el puente viejo.
set -uo pipefail

DEST="${1:?uso: tg_tail.sh <main|topic-N|topic-general|control>}"
SD="${TG_STATE_DIR:-$HOME/tgstate}"
INBOX="$SD/inbox"
FILE="$INBOX/$DEST.jsonl"
CUR="$SD/cursor.$DEST"

mkdir -p "$INBOX"
[ -f "$FILE" ] || : > "$FILE"

# --- con que comando se responde a ESTE destino ---
# Sin esta linea el agente tiene que deducir el ruteo, y deducirlo mal significa
# contestar en el tema de otra sesion: el usuario no ve la respuesta donde la
# espera y la otra sesion recibe un mensaje que no es suyo. Paso el 2026-07-31
# con Growth, que termino leyendo tg_poller.py para no equivocarse.
# La guia se repite en CADA evento a proposito: si se emitiera solo al arrancar,
# se perderia en la primera compactacion de contexto.
GID="${TG_GROUP_ID:-}"
if [ -z "$GID" ]; then
  ENVF="${TG_ENV_FILE:-${AGENT_WORKSPACE:-$PWD}/.env}"
  GID=$(grep -m1 '^TELEGRAM_GROUP_ID=' "$ENVF" 2>/dev/null | cut -d= -f2- | tr -d '"'"'"' \r')
fi
case "$DEST" in
  main)          RESP="bash bin/tg.sh send '<respuesta con tags HTML>'" ;;
  topic-general) RESP="TG_CHAT_ID=$GID bash bin/tg.sh send '<respuesta con tags HTML>'" ;;
  topic-*)       RESP="TG_CHAT_ID=$GID TG_TOPIC_ID=${DEST#topic-} bash bin/tg.sh send '<respuesta con tags HTML>'" ;;
  *)             RESP="" ;;
esac
# Si el grupo no esta configurado, decirlo en vez de emitir un comando con el
# chat_id vacio, que fallaria en silencio.
case "$DEST" in
  topic-*) [ -n "$GID" ] || RESP="(NO hay TELEGRAM_GROUP_ID en el .env: avisa, no adivines el destino)" ;;
esac

# Cursor = cuantas lineas de este destino ya entregamos.
read_cursor() { cat "$CUR" 2>/dev/null || echo 0; }
POS=$(read_cursor)
case "$POS" in ''|*[!0-9]*) POS=0;; esac

# Si el archivo fue rotado/truncado (menos lineas que el cursor), volver a 0 en
# vez de quedarse mudo para siempre esperando una linea que no va a llegar.
TOTAL=$(wc -l < "$FILE" | tr -d ' ')
[ "$TOTAL" -lt "$POS" ] && POS=0

emit() {
  # Cada linea del jsonl trae {"ts":..,"line":".."}. Emitimos la linea, que es
  # exactamente el formato que ya consumen las sesiones ([TG] / [TG-CMD]), y
  # debajo el comando con que se responde a ESTE destino.
  DEST="$DEST" RESP="$RESP" python3 -c '
import json, os, re, sys, time

# La herramienta Monitor entrega a la sesion SOLO los primeros ~500 caracteres de
# cada linea y reemplaza el resto por "(truncated)". El corte es POR LINEA: varias
# lineas seguidas se agrupan en un mismo aviso y ahi el tope medido es ~3.000. Por
# eso un mensaje largo no se corta, se PARTE en trozos numerados que llegan juntos
# y completos; lo que sobra queda en un archivo cuya ruta va en la ultima linea.
CORTE, PARTE, MAXP = 470, 380, 12
MSGS = os.path.join(os.path.expanduser("~"), ".claude", "tgstate", "msgs")


def emitir(linea):
    if len(linea) <= CORTE:
        print(linea, flush=True)
        return
    os.makedirs(MSGS, exist_ok=True)
    marca = re.search(r"\(msg (\d+)", linea)
    mid = marca.group(1) if marca else str(int(time.time()))
    ruta = os.path.join(MSGS, "%s.txt" % mid)
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(linea.replace(" \u23ce ", "\n"))
    corte = re.match(r"^(.*?\(msg \d+[^)]*\): )(.*)$", linea, re.S)
    cabeza, cuerpo = (corte.group(1), corte.group(2)) if corte else ("", linea)
    trozos, pend = [], cuerpo
    while pend:
        if len(pend) <= PARTE:
            trozos.append(pend)
            break
        c = pend.rfind(" ", 0, PARTE)
        if c < PARTE // 2:
            c = PARTE
        trozos.append(pend[:c])
        pend = pend[c:].lstrip()
    # La cabecera entera va solo en el primer trozo: repetirla en los seis gasta
    # presupuesto del aviso y es justo lo que deja la ultima parte afuera.
    print("[TG] Mensaje LARGO (msg %s): %d caracteres en %d partes. "
          "Si abajo no llegan las %d, o si alguna dice (truncated), leelo COMPLETO "
          "con Read en %s ANTES de responder."
          % (mid, len(cuerpo), len(trozos), len(trozos), ruta), flush=True)
    for i, tz in enumerate(trozos[:MAXP], 1):
        pre = (cabeza + "[%d/%d] " % (i, len(trozos))) if i == 1 else \
              "[TG] (msg %s . %d/%d) " % (mid, i, len(trozos))
        print(pre + tz, flush=True)
    if len(trozos) > MAXP:
        print("[TG] (msg %s) faltan %d de %d partes: el texto COMPLETO esta en %s"
              " - leelo con Read ANTES de responder"
              % (mid, len(trozos) - MAXP, len(trozos), ruta), flush=True)
    ahora = time.time()
    for v in os.listdir(MSGS):
        p = os.path.join(MSGS, v)
        try:
            if ahora - os.path.getmtime(p) > 7 * 86400:
                os.remove(p)
        except OSError:
            pass
dest = os.environ.get("DEST", "")
resp = os.environ.get("RESP", "")
dest = os.environ.get("DEST", "")
resp = os.environ.get("RESP", "")
for raw in sys.stdin:
    raw = raw.strip()
    if not raw:
        continue
    try:
        linea = json.loads(raw)["line"]
    except Exception:
        continue
    emitir(linea)
    # los comandos (/new, /model...) no se contestan con tg.sh: la guia solo
    # confundiria, y para esos el CLAUDE.md tiene su propio procedimiento.
    if resp and "[TG-CMD]" not in linea[:24]:
        print("[TG] [TAIL] responder a %s con: %s" % (dest, resp), flush=True)
'
}

# --- catch-up: lo que llego mientras esta sesion no estaba ---
if [ "$TOTAL" -gt "$POS" ]; then
  ATRASO=$((TOTAL - POS))
  echo "[TG] [TAIL] recuperando $ATRASO mensaje(s) que llegaron mientras no estaba ($DEST)"
  tail -n "+$((POS + 1))" "$FILE" | emit
  POS=$TOTAL
  echo "$POS" > "$CUR"
fi

# --- seguimiento en vivo ---
while true; do
  TOTAL=$(wc -l < "$FILE" 2>/dev/null | tr -d ' ')
  case "$TOTAL" in ''|*[!0-9]*) TOTAL=0;; esac
  if [ "$TOTAL" -lt "$POS" ]; then      # truncado en caliente
    POS=0
    echo "$POS" > "$CUR"
  fi
  if [ "$TOTAL" -gt "$POS" ]; then
    tail -n "+$((POS + 1))" "$FILE" | emit
    POS=$TOTAL
    echo "$POS" > "$CUR"
  fi
  sleep 2
done

