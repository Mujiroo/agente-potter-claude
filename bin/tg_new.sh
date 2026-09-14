#!/bin/bash
# /new desde Telegram: sesión Claude limpia via reinicio del contenedor.
# Mata el tmux DESACOPLADO (la Victoria está corriendo dentro; el kill directo la
# cortaría a mitad del tool). El watchdog del entrypoint ve tmux muerto -> exit ->
# docker restart -> boot completo (sesión nueva + bridge + 🟢). La memoria git persiste.
SELFDIR="$(cd "$(dirname "$0")" && pwd)"
bash "$SELFDIR/tg.sh" send "🔄 Ok — abriendo sesión nueva. Me reinicio; en ~1 minuto llega el 🟢. La memoria persistente se mantiene." >/dev/null 2>&1
nohup bash -c 'sleep 2; tmux kill-server' >/dev/null 2>&1 &
echo "OK: sesión nueva programada (reinicio en ~2s)"
