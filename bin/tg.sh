#!/bin/bash
# Helper Telegram (instancia VPS). Parametrizado por env: TG_TOKEN_VAR + estado por-HOME.
#   tg.sh typing on   -> loop "escribiendo..." refrescado cada 4s (~10 min)
#   tg.sh typing off  -> corta el loop
#   tg.sh send "<markdown>" -> corta el typing y envia como rich message nativo (sendRichMessage).
#                              Si el texto trae tags HTML, usa el modo legacy sendMessage+HTML.
SD="${TG_STATE_DIR:-$HOME/tgstate}"; mkdir -p "$SD"
# Mismo cuento que el token: el respaldo era la ruta FIJA del workspace de
# MacClaude. En cualquier otro agente, una llamada sin TG_ENV_FILE iba a buscar
# un .env que no existe y el token salia vacio -- envio fallido con un mensaje
# que no dice nada del problema real. El script sabe donde vive.
SELFDIR_TG="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${TG_ENV_FILE:-$(dirname "$SELFDIR_TG")/.env}"
# De que variable sale el token. El respaldo era el nombre FIJO del token de
# MacClaude, y eso mordio el 2026-08-02: al fusionar tres agentes, el .env quedo
# con los tres tokens, y cualquier llamada sin TG_TOKEN_VAR salio **firmada como
# MacClaude** -- un agente apagado hacia horas. Seba lo vio y pregunto por que le
# escribia un agente muerto.
#
# Lo peor es que antes fallaba bien: sin esa variable en el .env, el token
# quedaba vacio y el envio no salia. Al existir, empezo a funcionar mal en
# silencio, que es la unica forma en que esto se vuelve peligroso.
#
# Ahora: si nadie dice cual, se acepta SOLO si hay un unico token en el .env.
# Si hay varios es ambiguo, y ante la ambiguedad no se adivina: se corta.
TOKVAR="${TG_TOKEN_VAR:-}"
if [ -z "$TOKVAR" ]; then
  CANDIDATOS=$(grep -oE '^TELEGRAM_[A-Z0-9_]*TOKEN' "$ENV_FILE" 2>/dev/null | sort -u)
  CUANTOS=$(printf '%s\n' "$CANDIDATOS" | grep -c . || true)
  if [ "$CUANTOS" = "1" ]; then
    TOKVAR="$CANDIDATOS"
  else
    echo "ERROR: no se cual bot soy. Hay $CUANTOS tokens en $ENV_FILE y nadie" >&2
    echo "       exporto TG_TOKEN_VAR. NO mando el mensaje: saldria firmado por" >&2
    echo "       el agente equivocado. Candidatos:" >&2
    printf '%s\n' "$CANDIDATOS" | sed 's/^/         /' >&2
    exit 1
  fi
fi
TG=$(grep -m1 "^${TOKVAR}=" "$ENV_FILE" | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"'"'"' \r')
# Destino: por defecto el chat privado de Sebastian (comportamiento historico).
# En un grupo con temas, cada sesion exporta TG_CHAT_ID (el grupo, negativo) y
# TG_TOPIC_ID (su message_thread_id) para que su respuesta caiga en SU tema.
CHAT="${TG_CHAT_ID:-8715555558}"
TOPIC="${TG_TOPIC_ID:-}"
THREAD=(); [ -n "$TOPIC" ] && THREAD=(-d "message_thread_id=$TOPIC")
# Por-tema: si dos sesiones comparten SD, el typing de una no debe matar el de la
# otra, ni el sello "respondio Xm despues" mezclar temas distintos.
SUF="${TOPIC:+.$TOPIC}"
PIDF="$SD/tg_typing${SUF}.pid"
SENTF="$SD/last_sent${SUF}"

typing_off() { [ -f "$PIDF" ] && kill "$(cat "$PIDF")" 2>/dev/null; rm -f "$PIDF"; }

send_html() {
  if [ -n "${REPLY_TO:-}" ]; then
    curl -s --max-time 20 -X POST "https://api.telegram.org/bot${TG}/sendMessage" \
      -d chat_id=$CHAT "${THREAD[@]}" -d parse_mode=HTML --data-urlencode "text=$1" \
      -d reply_to_message_id="$REPLY_TO" -d allow_sending_without_reply=true \
      | python3 -c "import sys,json;d=json.load(sys.stdin);print('enviado ok (html, citando), msg_id',d['result']['message_id']) if d.get('ok') else print('ERROR',d)"
  else
    curl -s --max-time 20 -X POST "https://api.telegram.org/bot${TG}/sendMessage" \
      -d chat_id=$CHAT "${THREAD[@]}" -d parse_mode=HTML --data-urlencode "text=$1" \
      | python3 -c "import sys,json;d=json.load(sys.stdin);print('enviado ok (html), msg_id',d['result']['message_id']) if d.get('ok') else print('ERROR',d)"
  fi
}

mark_sent() { date +%s > "$SENTF" 2>/dev/null || true; }

send_msg() {
  if printf '%s' "$1" | grep -qE '</?(b|i|u|s|code|pre|blockquote|a|tg-spoiler)( [^>]*)?>'; then
    send_html "$1"; return
  fi
  # OJO: el chat_id iba hardcodeado aca. Con temas eso mandaba la respuesta al chat
  # privado en vez del tema. Si sendRichMessage no soporta message_thread_id, la
  # llamada no sale ok y cae sola al fallback HTML de abajo.
  PAYLOAD=$(CHAT="$CHAT" TOPIC="$TOPIC" python3 -c '
import json, os, sys
p = {"chat_id": int(os.environ["CHAT"]), "rich_message": {"markdown": sys.argv[1]}}
if os.environ.get("TOPIC"):
    p["message_thread_id"] = int(os.environ["TOPIC"])
print(json.dumps(p))
' "$1")
  RESP=$(curl -s --max-time 35 -X POST "https://api.telegram.org/bot${TG}/sendRichMessage" \
    -H 'Content-Type: application/json' -d "$PAYLOAD")
  OK=$(printf '%s' "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin).get('ok'))" 2>/dev/null)
  if [ "$OK" = "True" ]; then
    printf '%s' "$RESP" | python3 -c "import sys,json;d=json.load(sys.stdin);print('enviado ok (rich), msg_id',d['result']['message_id'])"
  else
    send_html "$1"
  fi
}

# tg.sh ask '<pregunta HTML>' 'Etiqueta1|dato1' 'Etiqueta2|dato2' ...
# Manda la pregunta con botones debajo. El toque vuelve como un evento [TG-BTN].
# Para que sirva de verdad: el dato es lo que identifica la opcion, y el puente
# saca los botones al primer clic para que no se pueda contestar dos veces.
send_ask() {
  local TEXTO="$1"; shift
  BOTONES="$(python3 - "$@" <<'PY'
import json, sys
fila = []
for arg in sys.argv[1:]:
    etiqueta, _, dato = arg.partition("|")
    fila.append({"text": etiqueta, "callback_data": (dato or etiqueta)[:64]})

# Cuantos por fila. Iban SIEMPRE de a dos y Seba no podia leerlos (2-ago-2026):
# dos botones se reparten el ancho de la pantalla, asi que una etiqueta larga
# queda cortada con "..." y la opcion no se entiende. Telegram no achica la letra
# ni parte la linea: simplemente trunca.
#
# Asi que manda la etiqueta mas larga: solo se ponen dos por fila si TODAS son
# cortas de verdad. Ante la duda, uno por fila -- ocupa mas alto, que sobra, en
# vez de ancho, que es lo que falta.
por_fila = 2 if all(len(b["text"]) <= 12 for b in fila) else 1
filas = [fila[i:i + por_fila] for i in range(0, len(fila), por_fila)]
print(json.dumps({"inline_keyboard": filas}))
PY
)"
  PAYLOAD=$(CHAT="$CHAT" TOPIC="$TOPIC" TEXTO="$TEXTO" BOTONES="$BOTONES" python3 -c '
import json, os
p = {"chat_id": int(os.environ["CHAT"]), "parse_mode": "HTML",
     "text": os.environ["TEXTO"],
     "reply_markup": json.loads(os.environ["BOTONES"])}
if os.environ.get("TOPIC"):
    p["message_thread_id"] = int(os.environ["TOPIC"])
print(json.dumps(p))')
  curl -s --max-time 20 -X POST "https://api.telegram.org/bot${TG}/sendMessage" \
    -H 'Content-Type: application/json' -d "$PAYLOAD" \
    | python3 -c "import sys,json;d=json.load(sys.stdin);print('preguntado ok, msg_id',d['result']['message_id']) if d.get('ok') else print('ERROR',d)"
}

# --- Envio de imagenes (agregado 30-ago-2026) ---
# OJO con el caption: va con --form-string y NO con -F. En curl, un valor -F que
# empieza con '<' o '@' significa "leer el contenido de este archivo", y todos
# nuestros captions empiezan con <b>. Con -F curl buscaba un archivo llamado
# "b>Texto..." y devolvia RESPUESTA VACIA -- que parece un problema de red y no
# lo es. Se perdio un rato diagnosticandolo mal.
# Dos variantes a proposito, porque NO son intercambiables:
#   foto    -> sendPhoto. Telegram RECOMPRIME. Comodo de ver en el chat, pero
#              pierde calidad: no sirve si ella va a resubir la imagen.
#   archivo -> sendDocument. Llega el JPEG EXACTO, byte por byte. Es el que se
#              usa cuando el destino es Instagram o cualquier reposteo.
THREAD_F=(); [ -n "$TOPIC" ] && THREAD_F=(-F "message_thread_id=$TOPIC")

send_foto() {
  curl -s --max-time 90 -X POST "https://api.telegram.org/bot${TG}/sendPhoto" \
    -F chat_id=$CHAT "${THREAD_F[@]}" -F parse_mode=HTML \
    -F "photo=@$1" --form-string "caption=${2:-}" \
    | python3 -c "import sys,json;d=json.load(sys.stdin);print('foto enviada ok, msg_id',d['result']['message_id']) if d.get('ok') else print('ERROR',d)"
}

send_archivo() {
  curl -s --max-time 90 -X POST "https://api.telegram.org/bot${TG}/sendDocument" \
    -F chat_id=$CHAT "${THREAD_F[@]}" -F parse_mode=HTML \
    -F "document=@$1" --form-string "caption=${2:-}" \
    | python3 -c "import sys,json;d=json.load(sys.stdin);print('archivo enviado ok, msg_id',d['result']['message_id']) if d.get('ok') else print('ERROR',d)"
}

# Editar un mensaje YA enviado. Sirve para arreglar una errata sin mandarle otro
# mensaje encima: Telegram no notifica de nuevo al editar, asi que corregir sale
# gratis y disculparse en un mensaje aparte sale caro (le suena el telefono).
send_editar() {
  curl -s --max-time 20 -X POST "https://api.telegram.org/bot${TG}/editMessageText" \
    -d chat_id=$CHAT -d message_id="$1" -d parse_mode=HTML --data-urlencode "text=$2" \
    | python3 -c "import sys,json;d=json.load(sys.stdin);print('editado ok, msg_id',d['result']['message_id']) if d.get('ok') else print('ERROR',d)"
}

case "$1" in
  ask)
    typing_off
    mark_sent
    shift
    send_ask "$@"
    ;;
  typing)
    if [ "$2" = "off" ]; then
      typing_off
    else
      typing_off
      # Cuantos ciclos de 4s dura el indicador. Por defecto 150 (~10 min), que
      # sirve para un pedido largo. Para un TOQUE DE BOTON se usa un tope corto:
      # si el toque no termina en respuesta, el "escribiendo..." no puede quedar
      # colgado diez minutos -- eso se lee como "se colgo", peor que el silencio.
      CICLOS="${2:-150}"
      case "$CICLOS" in ''|*[!0-9]*) CICLOS=150;; esac
      ( for _ in $(seq 1 "$CICLOS"); do
          curl -s --max-time 8 -X POST "https://api.telegram.org/bot${TG}/sendChatAction" \
            -d chat_id=$CHAT "${THREAD[@]}" -d action=typing >/dev/null 2>&1 || true
          sleep 4
        done ) >/dev/null 2>&1 &
      echo $! > "$PIDF"
      echo "typing on (pid $(cat "$PIDF"))"
    fi
    ;;
  send)
    mark_sent
    typing_off
    REPLY_TO="${3:-}" send_msg "$2"
    ;;
  reply)
    mark_sent
    typing_off
    REPLY_TO="$2" send_msg "$3"
    ;;
  avance)
    mark_sent
    REPLY_TO="${3:-}" send_msg "$2"
    "$0" typing on >/dev/null 2>&1
    ;;
  editar)
    send_editar "$2" "$3"
    ;;
  foto)
    mark_sent
    typing_off
    send_foto "$2" "${3:-}"
    ;;
  archivo)
    mark_sent
    typing_off
    send_archivo "$2" "${3:-}"
    ;;
  *)
    echo "uso: tg.sh typing on|off | send '<txt>' | reply <id> '<txt>' | foto <archivo> ['<caption>'] | archivo <archivo> ['<caption>']" >&2; exit 1;;
esac
