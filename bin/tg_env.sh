#!/bin/bash
# FEATURE 2 — /env: agrega/actualiza una variable en el .env desde Telegram.
# Uso: tg_env.sh <NOMBRE> <valfile> <force:yes|no> <msg_id>
# El valor sale del valfile (0600) que dejo el bridge: nunca pasa por argv, ni por el chat, ni por logs.
set -u
ENV_FILE=${AGENT_WORKSPACE:-/home/agent/workspace}/.env
NAME="${1:?falta nombre}"; VALFILE="${2:?falta valfile}"; FORCE="${3:-no}"; MSGID="${4:-}"
TG=$(grep -m1 "^${TG_TOKEN_VAR:-TELEGRAM_BOT_TOKEN}=" "$ENV_FILE" | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"'"'"' \r')

cleanup() {
  # borrar el mensaje del chat (el secreto no queda en el historial) y destruir el valfile
  [ -n "$MSGID" ] && curl -s --max-time 15 -X POST "https://api.telegram.org/bot${TG}/deleteMessage" \
      -d chat_id=$TG_OWNER_ID -d message_id="$MSGID" >/dev/null 2>&1
  [ -f "$VALFILE" ] && { shred -u "$VALFILE" 2>/dev/null || rm -f "$VALFILE"; }
}
trap cleanup EXIT

if ! [[ "$NAME" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "RECHAZADO: nombre de variable invalido"; exit 2
fi
[ -s "$VALFILE" ] || { echo "RECHAZADO: valor vacio o valfile inexistente"; exit 2; }

# existe ya una linea ACTIVA (no comentada) con esa variable?
if grep -qE "^${NAME}=" "$ENV_FILE"; then
  EXISTS=1
else
  EXISTS=0
fi

if [ "$EXISTS" = 1 ] && [ "$FORCE" != "yes" ]; then
  echo "YA_EXISTE"   # el caller avisa por Telegram y pide --force
  exit 3
fi

BAK="${ENV_FILE}.bak-$(date +%Y%m%d-%H%M%S)"
n=0
while [ -e "$BAK" ]; do n=$((n+1)); BAK="${ENV_FILE}.bak-$(date +%Y%m%d-%H%M%S)-$n"; done  # no pisar un backup del mismo segundo
cp -p "$ENV_FILE" "$BAK" && chmod 600 "$BAK"

NAME="$NAME" VALFILE="$VALFILE" ENV_FILE="$ENV_FILE" python3 - <<'PY'
import os
name = os.environ["NAME"]
env_file = os.environ["ENV_FILE"]
value = open(os.environ["VALFILE"]).read().strip()

# Valores con # o espacios van entre comillas: una extracción que corte en '#'
# clippearía el valor (passwords con # se cortan). Comillas dobles no soportadas.
if '"' in value or "\n" in value:
    print("RECHAZADO: el valor contiene comillas dobles o saltos de linea")
    raise SystemExit(2)
rendered = f'{name}="{value}"' if (" " in value or "#" in value) else f"{name}={value}"

with open(env_file) as f:
    content = f.read()
lines = content.split("\n")

replaced = False
for i, l in enumerate(lines):
    if l.startswith(name + "="):
        lines[i] = rendered
        replaced = True
        break   # solo la primera activa

if not replaced:
    while lines and lines[-1] == "":
        lines.pop()
    lines.append(rendered)
    lines.append("")

with open(env_file, "w") as f:
    f.write("\n".join(lines))
print("ACTUALIZADA" if replaced else "AGREGADA")
PY

chmod 600 "$ENV_FILE"
echo "BACKUP=$BAK"

# Doble escritura: también al .env del panel de Hostinger (montado en el contenedor).
# Escritura IN-PLACE (truncate, sin os.replace): es un bind-mount de archivo único
# y un replace cambiaría el inode rompiendo el mount.
PANEL="${PANEL_ENV_FILE:-/home/agent/panel.env}"
if [ -f "$PANEL" ] && [ -w "$PANEL" ]; then
  NAME="$NAME" VALFILE="$VALFILE" ENV_FILE="$PANEL" python3 - <<'PY'
import os
name = os.environ["NAME"]
env_file = os.environ["ENV_FILE"]
value = open(os.environ["VALFILE"]).read().strip()
rendered = f'{name}="{value}"' if (" " in value or "#" in value) else f"{name}={value}"
lines = open(env_file).read().split("\n")
replaced = False
for i, l in enumerate(lines):
    if l.startswith(name + "="):
        lines[i] = rendered
        replaced = True
        break
if not replaced:
    while lines and lines[-1] == "":
        lines.pop()
    lines.append(rendered)
    lines.append("")
with open(env_file, "w") as f:
    f.write("\n".join(lines))
print("PANEL_HOSTINGER=" + ("ACTUALIZADA" if replaced else "AGREGADA"))
PY
else
  echo "PANEL_HOSTINGER=no-montado"
fi
