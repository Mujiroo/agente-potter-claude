#!/bin/bash
# Puente Telegram Victoria VPS: long-poll getUpdates, emite 1 linea por mensaje.
# Los valores de /env NUNCA se imprimen: se guardan en un archivo 0600 y se emite solo el nombre.
# Parametrizado por instancia via env: TG_TOKEN_VAR (que token del .env leer) + estado por-HOME.
SELFDIR="$(cd "$(dirname "$0")" && pwd)"
SD="${TG_STATE_DIR:-$HOME/tgstate}"
mkdir -p "$SD"
ENV_FILE=${AGENT_WORKSPACE:-/home/agent/workspace}/.env
TOKVAR="${TG_TOKEN_VAR:-TELEGRAM_BOT_TOKEN}"
TG=$(grep -m1 "^${TOKVAR}=" "$ENV_FILE" | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"'"'"' \r')
OFF_FILE=$SD/tg_offset
OWNER="${TG_OWNER_ID:?falta TG_OWNER_ID}"
OWNER_NAME="${TG_OWNER_NAME:-el usuario}"  # nombre con que se etiqueta al dueño en los eventos [TG]
mkdir -p "$SD/env_pending" && chmod 700 "$SD/env_pending"
[ -f "$OFF_FILE" ] || echo 0 > "$OFF_FILE"

# ---- este agente ya migro al poller? entonces este puente NO debe arrancar ----
# Un token admite un solo getUpdates: arrancar los dos da 409 y deja al agente
# sordo con el contenedor en "Up". El centinela es un ARCHIVO, no un proceso,
# para cubrir tambien la ventana en que el poller todavia no tomo su candado.
# En un agente sin migrar no existe y este bloque no hace nada.
if [ -f "$SD/MIGRADO_A_POLLER" ]; then
  echo "[BRIDGE] Este agente ya migro al esquema multi-tema: tg_bridge.sh quedo obsoleto."
  echo "[BRIDGE] NO arranco (arrancar los dos da 409 y te deja sordo)."
  echo "[BRIDGE] Usa la herramienta Monitor con:  bash bin/tg_tail.sh main"
  echo "[BRIDGE] y un Monitor por cada tema que atiendas (p.ej. tg_tail.sh topic-general)."
  echo "[BRIDGE] Si el poller esta caido, revivilo con:  bash bin/tg_poller_keep.sh"
  exit 0
fi

PLOCK="$SD/tg_poller.lock.d"
if [ -d "$PLOCK" ]; then
  PPID_=$(cat "$PLOCK/pid" 2>/dev/null || echo "")
  if [ -n "$PPID_" ] && kill -0 "$PPID_" 2>/dev/null; then
    echo "[BRIDGE] Hay un POLLER vivo (pid $PPID_): este agente ya migro al esquema"
    echo "[BRIDGE] multi-tema y tg_bridge.sh quedo obsoleto. NO arranco: arrancar los"
    echo "[BRIDGE] dos da 409 y te deja sordo."
    echo "[BRIDGE] Usa la herramienta Monitor con:  bash bin/tg_tail.sh main"
    exit 0
  fi
  rm -rf "$PLOCK"   # candado huerfano: el poller murio sin limpiar
fi

# ---- candado atomico: un solo puente por agente ----
# mkdir es atomico: si dos puentes arrancan a la vez, solo uno lo logra. Sin esto,
# dos procesos hacen long-poll del mismo bot y se ROBAN los mensajes entre si
# (Telegram entrega cada update una sola vez): el usuario ve respuestas perdidas.
LOCKD="$SD/tg_bridge.lock.d"
take_lock() { mkdir "$LOCKD" 2>/dev/null && { echo $$ > "$LOCKD/pid"; trap 'rm -rf "$LOCKD"' EXIT INT TERM; return 0; }; return 1; }
if ! take_lock; then
  OLD=$(cat "$LOCKD/pid" 2>/dev/null)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "[BRIDGE] Ya hay un puente activo (pid $OLD). No levanto otro: el que corre sigue entregando los mensajes."
    exit 0
  fi
  rm -rf "$LOCKD"   # candado huerfano de un proceso muerto
  take_lock || { echo "[BRIDGE] no pude tomar el candado; salgo para no duplicar."; exit 0; }
fi

while true; do
  OFFSET=$(cat "$OFF_FILE" 2>/dev/null || echo 0)
  RESP=$(curl -s --max-time 65 "https://api.telegram.org/bot${TG}/getUpdates?timeout=50&offset=${OFFSET}&allowed_updates=%5B%22message%22%2C%22edited_message%22%2C%22callback_query%22%5D" || true)
  [ -z "$RESP" ] && sleep 3 && continue
  NEW=$(printf '%s' "$RESP" | OWNER="$OWNER" TGTOKEN="$TG" OWNER_NAME="$OWNER_NAME" SD="$SD" LAST_SENT="$(cat "$SD/last_sent" 2>/dev/null || echo 0)" python3 -c '
import sys, json, os, re, stat
import time as _t, datetime as _dt
owner = int(os.environ["OWNER"])
owner_name = os.environ.get("OWNER_NAME", "el usuario")
SD = os.environ["SD"]
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not d.get("ok"):
    sys.exit(0)
maxid = 0

def fmt_delta(seg):
    seg = int(seg)
    if seg < 60: return "%ds" % seg
    if seg < 3600: return "%dm" % (seg // 60)
    if seg < 86400:
        h, mm = seg // 3600, (seg % 3600) // 60
        return "%dh%02dm" % (h, mm) if mm else "%dh" % h
    dd, h = seg // 86400, (seg % 86400) // 3600
    return "%dd%dh" % (dd, h) if h else "%dd" % dd

_last_sent = int(os.environ.get("LAST_SENT", "0") or 0)
for u in d.get("result", []):
    maxid = max(maxid, u["update_id"])
    # ---- toque de boton: NO es un mensaje, viene como callback_query ----
    cq = u.get("callback_query")
    if cq:
        _de = cq.get("from") or {}
        if _de.get("id") != owner:
            continue
        _tok = os.environ.get("TGTOKEN", "")
        if _tok:
            # Sin esto el boton se queda girando en el telefono del duenzo.
            try:
                import urllib.parse as _up, urllib.request as _ur
                _ur.urlopen(
                    "https://api.telegram.org/bot%s/answerCallbackQuery" % _tok,
                    data=_up.urlencode({"callback_query_id": cq.get("id"), "text": "Anotado"}).encode(),
                    timeout=10,
                ).read()
            except Exception:
                pass
        _m = cq.get("message") or {}
        print("[TG] [TG-BTN] %s toco un boton (data=%s) en el msg %s"
              % (_de.get("first_name") or "el usuario", cq.get("data"), _m.get("message_id")))
        continue

    m = u.get("message") or u.get("edited_message") or {}
    chat = m.get("chat", {})
    cid = chat.get("id")
    if cid is None:
        continue
    if cid != owner:
        print("[TG-ALERT] chat no autorizado escribio: id=%s (contenido ignorado)" % cid)
        continue
    mid = m.get("message_id")
    text = (m.get("text") or "").strip()

    # ---- /env: el valor NUNCA se imprime ----
    mt = re.match(r"^/env(?:@\S+)?\s+(--force\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$", text, re.S)
    if mt:
        force = "yes" if mt.group(1) else "no"
        name, value = mt.group(2), mt.group(3)
        path = os.path.join(SD, "env_pending", "%s.val" % mid)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, "w") as f:
            f.write(value)
        print("[TG] [TG-CMD] env msg_id=%s var=%s force=%s valfile=%s (valor REDACTADO, no imprimir)"
              % (mid, name, force, path))
        continue
    if re.match(r"^/env\b", text):
        print("[TG] [TG-CMD] env-malformado msg_id=%s (sintaxis: /env [--force] NOMBRE=valor)" % mid)
        continue

    # ---- /new: sesion limpia ----
    if re.match(r"^/new(?:@\S+)?\s*$", text):
        print("[TG] [TG-CMD] new msg_id=%s" % mid)
        continue

    # ---- /model y /effort ----
    mt = re.match(r"^/(model|effort)(?:@\S+)?\s+(\S+)\s*$", text)
    if mt:
        print("[TG] [TG-CMD] %s msg_id=%s arg=%s" % (mt.group(1), mid, mt.group(2)))
        continue

    parts = []
    # ---- mensaje citado (reply): sin esto la cita se pierde y el contexto llega descolgado ----
    rt = m.get("reply_to_message") or {}
    if rt:
        rtxt = (rt.get("text") or rt.get("caption") or "").strip()
        if not rtxt:
            for k in ("voice", "audio", "photo", "document", "video", "video_note"):
                if rt.get(k):
                    rtxt = "(%s)" % k
                    break
        if rtxt:
            if len(rtxt) > 4096:
                rtxt = rtxt[:4096] + "\u2026"
            rtxt = rtxt.replace("\n", " ")
            de_quien = "tuyo" if (rt.get("from") or {}).get("is_bot") else "de " + owner_name
            parts.append("citando %s (msg %s): %s" % (de_quien, rt.get("message_id"), rtxt))
    if text: parts.append("text=" + text.replace("\n", " \u23ce "))
    if m.get("caption"): parts.append("caption=" + m["caption"].replace("\n", " \u23ce "))
    for k in ("voice", "audio", "photo", "document", "video", "video_note"):
        if m.get(k):
            obj = m[k]
            fid = obj[-1]["file_id"] if isinstance(obj, list) else obj.get("file_id")
            parts.append("%s file_id=%s" % (k, fid))
    if not parts:
        parts.append("(mensaje sin contenido soportado)")
    # ---- sello de tiempo: hora del mensaje, cuanto tardo en contestar y si lo leo tarde ----
    # Sin esto el agente no percibe el paso del tiempo: contesta un "buenos dias" de
    # hace 6 horas como si acabara de llegar.
    _d = m.get("date") or 0
    _sello = ""
    if _d:
        _sello = " · " + _dt.datetime.fromtimestamp(_d).strftime("%H:%M")
        if _last_sent and _d > _last_sent:
            _sello += " · respondio " + fmt_delta(_d - _last_sent) + " despues"
        _atraso = int(_t.time()) - _d
        if _atraso > 90:
            _sello += " · lo leo " + fmt_delta(_atraso) + " tarde"
    # ---- como se entrega: el aviso al agente tiene un tope y hay que respetarlo ----
    # La herramienta Monitor, que es la que le pasa cada linea al agente, entrega
    # SOLO los primeros ~500 caracteres de cada linea y reemplaza el resto por
    # "(truncated)". Como el mensaje viene aplanado en una sola linea, todo lo que
    # el dueno escriba por encima de eso no llega, y el agente contesta lo que
    # alcanzo a leer sin saber que le faltaba texto.
    #
    # El corte es POR LINEA: varias lineas emitidas seguidas se agrupan en un mismo
    # aviso y ahi el tope medido es ~3.000 caracteres. Por eso un mensaje largo no
    # se corta, se PARTE en trozos numerados que llegan juntos y completos.
    #
    # El texto nuevo va primero y la cita al final: si algo igual no entra, que sea
    # lo que el agente ya escribio y no la orden que tiene que cumplir. Lo que
    # sobra queda en ~/.claude/tgstate/msgs/<msg_id>.txt, con la ruta en la ultima
    # linea, y esos archivos se borran solos a los 7 dias.
    #
    # OJO: esto vale para el puente que levanta el AGENTE con Monitor. Si el puente
    # corre con --direct-tmux (el evento entra como turno escrito en la sesion) no
    # hay tope de 500 y partir seria empeorar: ahi este bloque no va.
    _PARTE, _MAXP = 380, 12
    _citas = [p for p in parts if p.startswith("citando ")]
    _resto = [p for p in parts if not p.startswith("citando ")]
    _cabeza = "[TG] %s (msg %s%s): " % (owner_name, mid, _sello)
    _cuerpo = " | ".join(_resto + _citas)
    _linea = _cabeza + _cuerpo
    if len(_linea) <= 470:
        print(_linea)
    else:
        _dir = os.path.join(os.path.expanduser("~"), ".claude", "tgstate", "msgs")
        os.makedirs(_dir, exist_ok=True)
        _ruta = os.path.join(_dir, "%s.txt" % mid)
        with open(_ruta, "w", encoding="utf-8") as _fh:
            _fh.write((_cabeza + "\n\n" + "\n\n".join(_resto + _citas)).replace(" \u23ce ", "\n"))
        _tz, _pend = [], _cuerpo
        while _pend:
            if len(_pend) <= _PARTE:
                _tz.append(_pend)
                break
            _c = _pend.rfind(" ", 0, _PARTE)
            if _c < _PARTE // 2:
                _c = _PARTE
            _tz.append(_pend[:_c])
            _pend = _pend[_c:].lstrip()
        # La cabecera entera va solo en el primer trozo: repetirla en los seis gasta
        # presupuesto del aviso y es justo lo que deja la ultima parte afuera.
        print("[TG] Sebastian mando un mensaje LARGO (msg %s): %d caracteres en %d partes. "
              "Si abajo no llegan las %d, o si alguna dice (truncated), leelo COMPLETO "
              "con Read en %s ANTES de responder."
              % (mid, len(_cuerpo), len(_tz), len(_tz), _ruta))
        for _i, _tt in enumerate(_tz[:_MAXP], 1):
            _pre = (_cabeza + "[%d/%d] " % (_i, len(_tz))) if _i == 1 else \
                   "[TG] (msg %s . %d/%d) " % (mid, _i, len(_tz))
            print(_pre + _tt)
        if len(_tz) > _MAXP:
            print("[TG] (msg %s) faltan %d de %d partes: el texto COMPLETO esta en %s"
              " - leelo con Read ANTES de responder"
                  % (mid, len(_tz) - _MAXP, len(_tz), _ruta))
        _ahora = _t.time()
        for _v in os.listdir(_dir):
            _p = os.path.join(_dir, _v)
            try:
                if _ahora - os.path.getmtime(_p) > 7 * 86400:
                    os.remove(_p)
            except OSError:
                pass
if maxid:
    print("OFFSET:%d" % (maxid + 1), file=sys.stderr)
' 2>>$SD/tg_bridge.err)
  # Dispara "escribiendo..." apenas llega un mensaje/comando del owner (independiente de
  # cuanto tarde la Victoria en empezar a responder). tg.sh typing corta el loop previo.
  printf '%s' "$NEW" | grep -qE '^\[TG\]|^\[TG-CMD\]' && bash "$SELFDIR/tg.sh" typing on >/dev/null 2>&1
  [ -n "$NEW" ] && printf '%s\n' "$NEW"
  LAST=$(grep -o 'OFFSET:[0-9]*' $SD/tg_bridge.err 2>/dev/null | tail -1 | cut -d: -f2)
  [ -n "$LAST" ] && echo "$LAST" > "$OFF_FILE"
done

