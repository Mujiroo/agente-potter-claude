#!/bin/bash
# Transcribe un audio / nota de voz de Telegram. Uso: tg_audio.sh <file_id>
#
# Orden de motores (1-ago-2026, pedido de Seba: "transcriban usando la api de
# openai o gemini"):
#   1. OpenAI  gpt-4o-transcribe   — el mejor en español, ~7s
#   2. Gemini  2.5-flash           — si no hay clave de OpenAI o esta falla
#   3. whisper LOCAL (faster-whisper, modelo base) — ULTIMO RECURSO
#
# El fallback local se queda a proposito: sin el, un agente sin clave o con la
# API caida deja a su dueño sin transcripcion, que es peor que una transcripcion
# mediocre. Si sale por local se avisa en la salida.
set -uo pipefail
FID="${1:?falta el file_id}"
SELFDIR="$(cd "$(dirname "$0")" && pwd)"
WS="$(dirname "$SELFDIR")"
AUDIO=$(bash "$SELFDIR/tg_file.sh" "$FID") || exit 1

# GOTCHA pagado el 24-jul: OpenAI RECHAZA la extension .oga que manda Telegram
# ("Invalid file format"), aunque el contenido sea ogg/opus valido. Renombrar
# basta; no hace falta reconvertir con ffmpeg.
case "$AUDIO" in
  *.oga) cp -f "$AUDIO" "${AUDIO%.oga}.ogg" && AUDIO="${AUDIO%.oga}.ogg" ;;
esac

# Claves desde el .env del workspace, sin exponerlas nunca por stdout.
OPENAI_API_KEY=""; GEMINI_API_KEY=""
if [ -f "$WS/.env" ]; then
  OPENAI_API_KEY=$(sed -n 's/^OPENAI_API_KEY=//p' "$WS/.env" | head -1 | tr -d '"'"'"'\r')
  GEMINI_API_KEY=$(sed -n 's/^GEMINI_API_KEY=//p' "$WS/.env" | head -1 | tr -d '"'"'"'\r')
  [ -z "$GEMINI_API_KEY" ] && GEMINI_API_KEY=$(sed -n 's/^GOOGLE_API_KEY=//p' "$WS/.env" | head -1 | tr -d '"'"'"'\r')
fi

emit() { [ -n "${1:-}" ] && { printf '%s\n' "$1"; exit 0; }; }

# ---------- 1) OpenAI gpt-4o-transcribe ----------
if [ -n "$OPENAI_API_KEY" ]; then
  RESP=$(curl -sS --max-time 180 https://api.openai.com/v1/audio/transcriptions \
           -H "Authorization: Bearer $OPENAI_API_KEY" \
           -F "file=@$AUDIO" -F "model=gpt-4o-transcribe" -F "language=es" 2>/dev/null)
  TXT=$(printf '%s' "$RESP" | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print((d.get("text") or "").strip())
except Exception: pass' 2>/dev/null)
  emit "$TXT"
fi

# ---------- 2) Gemini 2.5 flash ----------
if [ -n "$GEMINI_API_KEY" ]; then
  MIME=$(file -b --mime-type "$AUDIO" 2>/dev/null || echo audio/ogg)
  TXT=$(AUDIO="$AUDIO" MIME="$MIME" GK="$GEMINI_API_KEY" python3 - <<'PY' 2>/dev/null
import os, json, base64, urllib.request
try:
    raw = open(os.environ["AUDIO"], "rb").read()
    body = {"contents":[{"parts":[
        {"text":"Transcribe este audio en español. Devuelve SOLO la transcripción, sin comentarios."},
        {"inline_data":{"mime_type":os.environ["MIME"],"data":base64.b64encode(raw).decode()}}]}]}
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "gemini-2.5-flash:generateContent?key=" + os.environ["GK"])
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type":"application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=180))
    print("".join(p.get("text","") for p in
          d["candidates"][0]["content"]["parts"]).strip())
except Exception:
    pass
PY
)
  emit "$TXT"
fi

# ---------- 3) whisper LOCAL (ultimo recurso) ----------
# Gotcha 24-jul: /opt/stt/venv/bin/python existe pero NO trae faster_whisper;
# el paquete vive en /opt/stt/pylibs. Elegir por -x fallaba con el venv.
if [ -x /opt/stt/venv/bin/python ] && /opt/stt/venv/bin/python -c 'import faster_whisper' 2>/dev/null; then
  PY=/opt/stt/venv/bin/python; unset PYTHONPATH 2>/dev/null || true
elif [ -d /opt/stt/pylibs ] && PYTHONPATH=/opt/stt/pylibs python3 -c 'import faster_whisper' 2>/dev/null; then
  PY=python3; export PYTHONPATH=/opt/stt/pylibs
else
  echo "ERROR: no pude transcribir — sin clave de OpenAI/Gemini y sin whisper local en /opt/stt" >&2
  exit 1
fi

HF_HOME=/opt/stt/hf HF_HUB_OFFLINE=1 AUDIO="$AUDIO" "$PY" - <<'PY'
import os, sys
try:
    from faster_whisper import WhisperModel
except Exception as e:
    sys.exit("ERROR: motor de transcripcion no disponible (%s)" % e)
m = WhisperModel("base", device="cpu", compute_type="int8")
segs, _ = m.transcribe(os.environ["AUDIO"], language="es")
txt = "".join(s.text for s in segs).strip()
print(txt if txt else "(audio sin habla detectable)")
print("[aviso: transcrito con whisper local — calidad menor; revisa la clave de OpenAI/Gemini]",
      file=sys.stderr)
PY
