#!/bin/bash
# Descarga un adjunto de Telegram por file_id.
# Uso: tg_file.sh <file_id> [dir_destino]
# Vars: TG_ENV_FILE (o AGENT_WORKSPACE/.env), TG_TOKEN_VAR (default TELEGRAM_BOT_TOKEN).
# No depende de ninguna API externa: solo el token del propio agente.
set -euo pipefail
FID="${1:?falta el file_id}"
SELFDIR="$(cd "$(dirname "$0")" && pwd)"
WS="${AGENT_WORKSPACE:-$(cd "$SELFDIR/.." && pwd)}"
ENV_FILE="${TG_ENV_FILE:-$WS/.env}"
DEST="${2:-${TG_DOWNLOAD_DIR:-$WS/incoming}}"
mkdir -p "$DEST"
TOKVAR="${TG_TOKEN_VAR:-TELEGRAM_BOT_TOKEN}"
TOK=$(grep -m1 "^${TOKVAR}=" "$ENV_FILE" | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"'"'"' \r')
[ -n "$TOK" ] || { echo "ERROR: sin token ($TOKVAR) en $ENV_FILE" >&2; exit 1; }
# getFile a veces se cuelga aunque el resto de la API responda (paso el 25-ago-2026:
# getMe al instante y getFile timeout una y otra vez, con file_id validos). Antes eso
# reventaba con un traceback de Python sobre respuesta vacia y parecia "file_id expirado",
# que es un diagnostico equivocado y manda a buscar por el lado que no es.
# 27-ago-2026: con 30s se rendia y una llamada identica a 45s SI respondia, en plena
# emergencia (Connie en la estacion de tren). getFile puede tardar >30s y responder bien:
# se sube el techo a 60s y se reintenta 3 veces antes de declarar caida la API.
# 28-ago-2026: fallaron los TRES intentos de 60s (Connie en el bus del parque) y una
# llamada manual inmediata SI respondio, en 19s. Midiendo las dos caras:
#   - cuando getFile falla, CUELGA hasta agotar el timeout completo (HTTP 000 exacto
#     a los 50s, 60s y 90s). Un techo alto NO ayuda: solo quema el presupuesto.
#   - cuando responde, responde rapido (19s hoy; el 27-ago fue >30s pero <45s).
# Entonces conviene al reves de lo que parecia: MUCHOS intentos CORTOS primero, para
# pillar la ventana buena, y un par largos al final por si toca una lenta de verdad.
# Mismo techo de tiempo que antes, pero 5 oportunidades en vez de 3.
RESP=""
for T in 20 20 45 45 75; do
  RESP=$(curl -s --max-time "$T" "https://api.telegram.org/bot${TOK}/getFile?file_id=${FID}" || true)
  [ -n "$RESP" ] && break
  echo "getFile no respondio en ${T}s, reintento..." >&2
  sleep 2
done
if [ -z "$RESP" ]; then
  echo "ERROR-RED: getFile no respondio tras 5 intentos (20/20/45/45/75s). OJO: proba \
getMe antes de declarar caida la API -- si getMe responde 200, el servicio esta vivo y \
es getFile el que cuelga; reintenta en un par de minutos y suele salir." >&2
  exit 2
fi
FP=$(printf '%s' "$RESP" | python3 -c 'import sys,json
try:
    print(json.load(sys.stdin).get("result",{}).get("file_path",""))
except Exception:
    print("")')
[ -n "$FP" ] || { echo "ERROR: file_id invalido o expirado -- respuesta: $(printf '%s' "$RESP" | head -c 200)" >&2; exit 1; }
OUT="$DEST/$(basename "$FP")"
curl -s --max-time 180 -o "$OUT" "https://api.telegram.org/file/bot${TOK}/${FP}"
echo "$OUT"
