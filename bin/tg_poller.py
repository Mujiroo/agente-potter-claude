#!/usr/bin/env python3
"""Poller Telegram multi-destino: UN solo dueno del token, fan-out por tema.

Por que existe (y por que no es tg_bridge.sh):
  Un token de bot admite un solo getUpdates a la vez -- dos pollers y Telegram
  corta a uno con 409 Conflict. Con un grupo de temas queremos N sesiones Claude
  en paralelo, asi que el que escucha se separa del que consume:

      tg_poller.py  (1, dueno del token)  ->  inbox/main.jsonl
                                              inbox/topic-<id>.jsonl
                                              inbox/control.jsonl
      tg_tail.sh    (1 por sesion)        ->  lee SU archivo y nada mas

  Beneficio extra: el poller sobrevive a la muerte de cualquier sesion. Lo que
  llega mientras una sesion esta caida queda en SU archivo y lo recupera al
  volver, en vez de quedar colgado en la cola de Telegram.

La logica de formato de cada mensaje es la de tg_bridge.sh, a proposito: ahi
viven arreglos ya pagados (citas con saltos de linea, /env redactado, sellos de
tiempo, file_id de adjuntos). No reescribir de cero.

AUTORIZACION -- el cambio critico frente a tg_bridge.sh:
  El puente viejo valida chat.id == OWNER. En un grupo, chat.id es el GRUPO, asi
  que eso dejaria pasar a cualquiera que este adentro. Aca se valida from.id.

Uso:
  TG_ENV_FILE=... TG_TOKEN_VAR=... TG_STATE_DIR=... [TG_GROUP_ID=-100...] \
    python3 bin/tg_poller.py
"""
import atexit
import datetime
import json
import os
import re
import stat
import subprocess
import sys
import time
import urllib.parse
import urllib.request

SELFDIR = os.path.dirname(os.path.abspath(__file__))
SD = os.environ.get("TG_STATE_DIR") or os.path.join(os.path.expanduser("~"), "tgstate")
ENV_FILE = os.environ.get("TG_ENV_FILE") or os.path.join(
    os.environ.get("AGENT_WORKSPACE") or "/home/agent/workspace", ".env")
TOKVAR = os.environ.get("TG_TOKEN_VAR") or "TELEGRAM_BOT_TOKEN"
# Sin dueno no hay autorizacion posible: mejor no arrancar que arrancar
# atendiendo a cualquiera.
if not (os.environ.get("TG_OWNER_ID") or "").strip():
    raise SystemExit("falta TG_OWNER_ID: el poller no sabria a quien autorizar")
OWNER = int(os.environ["TG_OWNER_ID"])
OWNER_NAME = os.environ.get("TG_OWNER_NAME") or "el usuario"

INBOX = os.path.join(SD, "inbox")
OFF_FILE = os.path.join(SD, "tg_offset")
LOCKD = os.path.join(SD, "tg_poller.lock.d")
ERRF = os.path.join(SD, "tg_poller.err")

os.makedirs(INBOX, exist_ok=True)
os.makedirs(os.path.join(SD, "env_pending"), exist_ok=True)
os.chmod(os.path.join(SD, "env_pending"), 0o700)


def log(msg):
    line = "%s %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), msg)
    with open(ERRF, "a") as f:
        f.write(line)
    sys.stderr.write(line)
    sys.stderr.flush()


def read_env(var):
    """Mismo criterio de extraccion que tg.sh / host-ssh-mac.sh.

    GOTCHA heredado: el env-merge escribe con comillas simples o dobles, y un
    valor puede traer '#' adentro. Nunca cortar en '#' sin mirar las comillas.
    """
    try:
        f = open(ENV_FILE)
    except OSError:
        return ""
    with f:
        for line in f:
            m = re.match(r"^%s=(.*)$" % re.escape(var), line.rstrip("\n"))
            if not m:
                continue
            v = m.group(1)
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            else:
                v = re.sub(r"\s+#.*$", "", v).strip()
            return v.strip()
    return ""


# Grupo con temas (negativo, -100...). Vacio = solo chat privado, como hoy.
# Se lee del entorno o, si no esta, del .env: asi sobrevive a un reinicio sin
# depender de que el comando de arranque lo pase.
GROUP_ID = os.environ.get("TG_GROUP_ID") or read_env("TELEGRAM_GROUP_ID")

# Chat privado apagado: el agente vive SOLO en los temas del grupo.
# Se apaga ACA, en el poller, y no sacandole el consumidor a la sesion: el
# watchdog de la flota vigila justamente `tg_tail.sh main`, asi que si la sesion
# soltara ese monitor el watchdog creeria que el agente quedo sordo y le
# reinyectaria ordenes en loop. Con esto el monitor sigue en pie -- simplemente
# no le llega nada.
_dm_raw = (os.environ.get("TG_DISABLE_DM") or read_env("TELEGRAM_DISABLE_DM") or "").strip().lower()
DM_ENABLED = _dm_raw not in ("1", "true", "yes", "si", "sí", "on")
DM_AVISO_PATH = os.path.join(SD, "dm-aviso-ts")
DM_AVISO_CADA = 600  # un aviso cada 10 min, ni spam ni silencio

TOKEN = read_env(TOKVAR)
if not TOKEN:
    log("FATAL: sin %s en %s" % (TOKVAR, ENV_FILE))
    sys.exit(1)
API = "https://api.telegram.org/bot%s/" % TOKEN


# ---- candado atomico: un solo poller por token/estado ----
def take_lock():
    try:
        os.mkdir(LOCKD)
    except FileExistsError:
        return False
    with open(os.path.join(LOCKD, "pid"), "w") as f:
        f.write(str(os.getpid()))
    return True


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


if not take_lock():
    old = ""
    try:
        with open(os.path.join(LOCKD, "pid")) as f:
            old = f.read().strip()
    except OSError:
        pass
    if old.isdigit() and pid_alive(int(old)):
        print("[POLLER] Ya hay un poller activo (pid %s). No levanto otro." % old)
        sys.exit(0)
    # candado huerfano (contenedor reiniciado): lo limpio y reintento
    try:
        os.remove(os.path.join(LOCKD, "pid"))
    except OSError:
        pass
    try:
        os.rmdir(LOCKD)
    except OSError:
        pass
    if not take_lock():
        print("[POLLER] no pude tomar el candado; salgo para no duplicar.")
        sys.exit(0)

def _release():
    try:
        os.remove(os.path.join(LOCKD, "pid"))
    except OSError:
        pass
    try:
        os.rmdir(LOCKD)
    except OSError:
        pass


atexit.register(_release)


def api(method, params=None, timeout=70):
    url = API + method
    data = None
    if params:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def fmt_delta(seg):
    seg = int(seg)
    if seg < 60:
        return "%ds" % seg
    if seg < 3600:
        return "%dm" % (seg // 60)
    if seg < 86400:
        h, mm = seg // 3600, (seg % 3600) // 60
        return "%dh%02dm" % (h, mm) if mm else "%dh" % h
    dd, h = seg // 86400, (seg % 86400) // 3600
    return "%dd%dh" % (dd, h) if h else "%dd" % dd


def dest_of(m):
    """A que archivo va este mensaje. None = no es para nosotros."""
    chat = m.get("chat") or {}
    cid = chat.get("id")
    if cid is None:
        return None
    if str(cid) == str(OWNER):
        return "main"                       # chat privado: comportamiento historico
    if GROUP_ID and str(cid) == str(GROUP_ID):
        # GOTCHA: message_thread_id NO alcanza para identificar un tema. Al
        # responder a un mensaje del tema General, Telegram igual manda
        # message_thread_id, pero con el id del mensaje raiz -- no de un tema.
        # Tomarlo como tema crearia un topic-<msgid> fantasma. El campo que
        # distingue de verdad es is_topic_message.
        tid = m.get("message_thread_id")
        if tid and m.get("is_topic_message"):
            return "topic-%s" % tid
        return "topic-general"
    return None                            # chat/grupo desconocido


def write_line(dest, line):
    path = os.path.join(INBOX, "%s.jsonl" % dest)
    with open(path, "a") as f:
        f.write(json.dumps({"ts": int(time.time()), "line": line}) + "\n")


def last_sent_for(dest):
    suf = ""
    if dest.startswith("topic-"):
        tid = dest[len("topic-"):]
        if tid != "general":
            suf = "." + tid
    try:
        with open(os.path.join(SD, "last_sent%s" % suf)) as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def fire_typing(dest):
    """Enciende 'escribiendo...' en el destino correcto (grupo+tema o privado)."""
    env = dict(os.environ)
    if dest.startswith("topic-"):
        env["TG_CHAT_ID"] = str(GROUP_ID)
        tid = dest[len("topic-"):]
        if tid != "general":
            env["TG_TOPIC_ID"] = tid
        else:
            env.pop("TG_TOPIC_ID", None)
    else:
        env.pop("TG_CHAT_ID", None)
        env.pop("TG_TOPIC_ID", None)
    try:
        subprocess.run(["bash", os.path.join(SELFDIR, "tg.sh"), "typing", "on"],
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=20)
    except Exception:
        pass


def aviso_dm_corresponde():
    """Un aviso cada tanto, no en cada mensaje.

    Silencio total NO: un agente que no contesta se ve igual que uno caido.
    """
    ahora = time.time()
    try:
        with open(DM_AVISO_PATH) as f:
            ultimo = float(f.read().strip())
    except (OSError, ValueError):
        ultimo = 0.0
    if ahora - ultimo < DM_AVISO_CADA:
        return False
    try:
        with open(DM_AVISO_PATH, "w") as f:
            f.write(str(ahora))
    except OSError:
        pass
    return True


def avisar_dm_apagado():
    """Le dice por el privado que ahora se habla por los temas."""
    env = dict(os.environ)
    env.pop("TG_CHAT_ID", None)
    env.pop("TG_TOPIC_ID", None)
    texto = ("Ahora trabajo por <b>los temas del grupo</b>, no por acá. "
             "Escribime en el tema que corresponda y te contesto ahí.")
    try:
        subprocess.run(["bash", os.path.join(SELFDIR, "tg.sh"), "send", texto],
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=25)
    except Exception:
        pass


def handle(m):
    """Formatea un mensaje y lo entrega. Devuelve el dest, o None si se descarto."""
    dest = dest_of(m)
    frm = (m.get("from") or {}).get("id")

    # ---- AUTORIZACION: se valida QUIEN escribe, no DONDE ----
    # En un grupo chat.id es el grupo entero; validar por chat dejaria entrar a
    # cualquier miembro. El contenido de un no-autorizado nunca se imprime.
    if frm != OWNER:
        if dest is not None:
            write_line("control", "[TG-ALERT] escribio alguien que no es el dueno: "
                                  "from_id=%s en %s (contenido ignorado)" % (frm, dest))
        return None
    if dest is None:
        write_line("control", "[TG-ALERT] chat no autorizado: id=%s (contenido ignorado)"
                   % (m.get("chat") or {}).get("id"))
        return None

    # ---- chat privado apagado: se avisa, no se procesa ----
    # GUARDA: solo se puede apagar si hay grupo. Sin canal alternativo el agente
    # quedaria incomunicado, y eso no lo arregla ningun aviso.
    if dest == "main" and not DM_ENABLED:
        if not GROUP_ID:
            log("DM apagado PERO no hay TELEGRAM_GROUP_ID: lo ignoro y entrego "
                "igual, si no el agente queda sin ningun canal")
        else:
            log("mensaje al privado descartado (DM apagado); se atiende por los temas")
            if aviso_dm_corresponde():
                avisar_dm_apagado()
            return None

    # ---- eventos de tema (lo que permite abrir/cerrar sesiones solas) ----
    # OJO: forum_topic_deleted NO existe en la Bot API. Borrar un tema no avisa;
    # solo cerrarlo (forum_topic_closed). Por eso la convencion es CERRAR.
    tid = m.get("message_thread_id")
    # forum_topic_closed/reopened llegan como objeto VACIO ({}), que es falsy:
    # hay que preguntar por la CLAVE, no por el valor.
    if "forum_topic_created" in m:
        name = (m.get("forum_topic_created") or {}).get("name", "")
        write_line("control", "[TG-TOPIC] created thread_id=%s name=%s" % (tid, name))
        return "control"
    if "forum_topic_closed" in m:
        write_line("control", "[TG-TOPIC] closed thread_id=%s" % tid)
        return "control"
    if "forum_topic_reopened" in m:
        write_line("control", "[TG-TOPIC] reopened thread_id=%s" % tid)
        return "control"
    if "forum_topic_edited" in m:
        name = (m.get("forum_topic_edited") or {}).get("name", "")
        write_line("control", "[TG-TOPIC] edited thread_id=%s name=%s" % (tid, name))
        return "control"

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
        write_line(dest, "[TG] [TG-CMD] env msg_id=%s var=%s force=%s valfile=%s "
                         "(valor REDACTADO, no imprimir)" % (mid, name, force, path))
        return dest
    if re.match(r"^/env\b", text):
        write_line(dest, "[TG] [TG-CMD] env-malformado msg_id=%s "
                         "(sintaxis: /env [--force] NOMBRE=valor)" % mid)
        return dest

    if re.match(r"^/newagent(?:@\S+)?\s*$", text):
        write_line(dest, "[TG] [TG-CMD] newagent msg_id=%s" % mid)
        return dest
    if re.match(r"^/new(?:@\S+)?\s*$", text):
        write_line(dest, "[TG] [TG-CMD] new msg_id=%s" % mid)
        return dest
    mt = re.match(r"^/(model|effort)(?:@\S+)?\s+(\S+)\s*$", text)
    if mt:
        write_line(dest, "[TG] [TG-CMD] %s msg_id=%s arg=%s" % (mt.group(1), mid, mt.group(2)))
        return dest

    # ---- mensaje normal (formato heredado de tg_bridge.sh, no tocar) ----
    parts = []
    rt = m.get("reply_to_message") or {}
    if rt:
        rtxt = (rt.get("text") or rt.get("caption") or "").strip()
        if not rtxt:
            for k in ("voice", "audio", "photo", "document", "video", "video_note"):
                if rt.get(k):
                    rtxt = "(%s)" % k
                    break
        if rtxt:
            if len(rtxt) > 4000:
                rtxt = rtxt[:4000] + "..."
            rtxt = rtxt.replace("\n", " ⏎ ")
            de_quien = "tu mensaje" if (rt.get("from") or {}).get("is_bot") else "su mensaje"
            parts.append("citando %s (msg %s): %s" % (de_quien, rt.get("message_id"), rtxt))
    if text:
        parts.append("text=" + text.replace("\n", " ⏎ "))
    if m.get("caption"):
        parts.append("caption=" + m["caption"].replace("\n", " ⏎ "))
    for k in ("voice", "audio", "photo", "document", "video", "video_note"):
        if m.get(k):
            obj = m[k]
            fid = obj[-1]["file_id"] if isinstance(obj, list) else obj.get("file_id")
            parts.append("%s file_id=%s" % (k, fid))
    if not parts:
        parts.append("(mensaje sin contenido soportado)")

    _d = m.get("date") or 0
    _sello = ""
    if _d:
        _sello = " · " + datetime.datetime.fromtimestamp(_d).strftime("%H:%M")
        _ls = last_sent_for(dest)
        if _ls and _d > _ls:
            _sello += " · respondio " + fmt_delta(_d - _ls) + " despues"
        _atraso = int(time.time()) - _d
        if _atraso > 90:
            _sello += " · lo leo " + fmt_delta(_atraso) + " tarde"
    write_line(dest, "[TG] %s (msg %s%s): %s" % (OWNER_NAME, mid, _sello, " | ".join(parts)))
    return dest


def main():
    try:
        with open(OFF_FILE) as f:
            offset = int(f.read().strip() or 0)
    except (OSError, ValueError):
        offset = 0
    log("poller arrancado offset=%s group=%s inbox=%s" % (offset, GROUP_ID or "(sin grupo)", INBOX))
    backoff = 3
    while True:
        try:
            d = api("getUpdates", {
                "timeout": 50,
                "offset": offset,
                "allowed_updates": json.dumps(["message", "edited_message"]),
            })
            backoff = 3
        except Exception as e:
            # 409 = otro poller con el mismo token. Es fatal por diseno: si nos
            # quedamos, los dos nos robamos los mensajes y el usuario ve huecos.
            txt = str(e)
            if "409" in txt:
                log("FATAL 409: otro getUpdates tiene este token. Salgo.")
                sys.exit(2)
            log("error getUpdates: %s (reintento en %ss)" % (txt, backoff))
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
            continue
        if not d.get("ok"):
            log("respuesta no-ok: %s" % str(d)[:200])
            time.sleep(3)
            continue
        touched = set()
        for u in d.get("result", []):
            offset = max(offset, u["update_id"] + 1)
            m = u.get("message") or u.get("edited_message") or {}
            try:
                dest = handle(m)
            except Exception as e:
                log("error procesando update %s: %s" % (u.get("update_id"), e))
                continue
            if dest and dest != "control":
                touched.add(dest)
        if d.get("result"):
            with open(OFF_FILE, "w") as f:
                f.write(str(offset))
        for dest in touched:
            fire_typing(dest)


if __name__ == "__main__":
    main()
