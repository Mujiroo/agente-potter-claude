#!/bin/bash
# Mantiene vivo tg_poller.py. Se lanza UNA vez, desasido de cualquier sesion
# Claude (setsid), para que sobreviva a /new, a la rotacion de sesion y a que la
# sesion se cuelgue. Eso es todo el punto: el que escucha no debe morir con el
# que consume.
#
#   setsid nohup bash bin/tg_poller_keep.sh >/dev/null 2>&1 &
#
# El entrypoint lo llama en cada arranque del contenedor. Es idempotente: si ya
# hay un keeper o un poller vivo, sale sin hacer nada (candado de tg_poller.py).
set -uo pipefail

SELFDIR="$(cd "$(dirname "$0")" && pwd)"
SD="${TG_STATE_DIR:-$HOME/tgstate}"
mkdir -p "$SD"
LOG="$SD/tg_poller_keep.log"
KEEPLOCK="$SD/tg_poller_keep.lock.d"

say() { echo "$(date +%H:%M:%S) $*" >> "$LOG"; }

# --- un solo keeper ---
if ! mkdir "$KEEPLOCK" 2>/dev/null; then
  OLD=$(cat "$KEEPLOCK/pid" 2>/dev/null || echo "")
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    say "ya hay un keeper vivo (pid $OLD); salgo"
    exit 0
  fi
  rm -rf "$KEEPLOCK"
  mkdir "$KEEPLOCK" 2>/dev/null || { say "no pude tomar el candado del keeper; salgo"; exit 0; }
fi
echo $$ > "$KEEPLOCK/pid"
trap 'rm -rf "$KEEPLOCK"' EXIT INT TERM

say "keeper arrancado (pid $$)"
FALLOS=0
while true; do
  python3 "$SELFDIR/tg_poller.py" >> "$LOG" 2>&1
  RC=$?
  if [ "$RC" -eq 2 ]; then
    # 409: otro getUpdates tiene el token. Reintentar seria pelearse con el y
    # dejar huecos en la conversacion. Mejor rendirse ruidosamente.
    say "poller salio 409 (otro dueno del token). NO reintento. Revisar tg_bridge.sh vivo."
    exit 2
  fi
  if [ "$RC" -eq 0 ]; then
    say "poller salio limpio (rc=0); salgo tambien"
    exit 0
  fi
  FALLOS=$((FALLOS + 1))
  ESPERA=$(( FALLOS < 5 ? 5 : 30 ))
  say "poller murio rc=$RC (falla #$FALLOS); reintento en ${ESPERA}s"
  sleep "$ESPERA"
done
