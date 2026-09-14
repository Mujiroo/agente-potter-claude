#!/usr/bin/env python3
"""Una sesion Claude por tema de Telegram: paralelismo real.

Que resuelve: con un solo consumidor (tg_tail_all.py) TODOS los temas los
atiende una sesion, asi que si esta en un turno largo el resto espera -- que era
justo el problema que Sebastian queria evitar. Aca cada tema tiene su propia
sesion tmux, entonces el tema A trabaja mientras el B trabaja.

Como funciona:
  - descubre temas por inbox/topic-<id>.jsonl y por los [TG-TOPIC] de control
  - por cada tema sin sesion, levanta tmux `tema-<id>` con claude adentro
  - le inyecta un prompt de arranque que le dice a QUE tema atiende y como
    responder ahi
  - [TG-TOPIC] closed  -> mata esa sesion
  - [TG-TOPIC] reopened -> la vuelve a levantar

Reparto de cursores (importante): cada sesion consume SU topic-<id>.jsonl con su
propio cursor. La sesion principal debe quedarse con `main` y `topic-general`
NADA MAS -- si sigue corriendo tg_tail_all.py se roban los mensajes entre ellas,
porque el cursor es por destino y lo avanza el primero que lee.

GOTCHAS respetados (pagados en otros montajes):
  - `tmux kill-server` mata TODOS los agentes del contenedor: jamas usarlo, solo
    `kill-session -t <sesion>`.
  - `tmux info` sale con codigo 1 si no hay cliente adjunto: para saber si tmux
    vive se usa `list-sessions`.
  - el prompt de arranque va en UNA sola linea: un \\n en `send-keys -l` manda el
    mensaje a medias.
  - el entorno se exporta DENTRO del comando de tmux, asi lo heredan claude y
    todo lo que ejecute (sus Bash, su tail). Los scripts quedan iguales para todos.

Uso:  TG_STATE_DIR=... TG_GROUP_ID=... python3 bin/tg_topic_spawner.py
"""
import json
import os
import re
import subprocess
import sys
import time

# El respaldo era "/home/victoria/victoria" fijo. Eso funciona solo para
# MacClaude: en cualquier otro agente, si AGENT_WORKSPACE no viene en el entorno
# (el entrypoint lo exporta en tiempo de ejecucion, asi que un `docker exec` NO
# lo hereda), el spawner apuntaba al workspace equivocado, no encontraba el .env,
# se quedaba sin TELEGRAM_GROUP_ID y moria con FATAL. Costo el spawner de Growth
# el 2026-08-01. El script SABE donde vive: <workspace>/bin/este_archivo.py.
WS = os.environ.get("AGENT_WORKSPACE") or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
SD = os.environ.get("TG_STATE_DIR") or os.path.join(os.path.expanduser("~"), "tgstate")
INBOX = os.path.join(SD, "inbox")
ENV_FILE = os.environ.get("TG_ENV_FILE") or os.path.join(WS, ".env")
LOG = os.path.join(SD, "tg_spawner.log")
LOCKD = os.path.join(SD, "tg_spawner.lock.d")
CURSOR_CTRL = os.path.join(SD, "spawner.cursor.control")

# Quien es el agente y quien es su dueno. Van al prompt de arranque de cada
# sesion de tema: sin esto el spawner solo servia para MacClaude, y cualquier
# otro agente de la flota nacia presentandose con el nombre equivocado.
AGENT_NAME = os.environ.get("TG_AGENT_NAME") or "MacClaude"
OWNER_NAME = os.environ.get("TG_OWNER_NAME") or "Sebastian"

# SIN techo fijo de sesiones (decision de Seba, 2026-08-01). Antes habia un tope
# duro de 4-5 temas por agente, calculado a mano contra un mem_limit de 4 GB. Ese
# numero envejecia mal: rechazaba un tema aunque sobrara memoria, y no protegia
# nada cuando el mem_limit subia. Lo reemplaza el guard de memoria REAL de mas
# abajo, que mira cuanta RAM hay de verdad -- en el contenedor Y en el host.
# Se puede volver a poner un tope con TG_MAX_TOPIC_SESSIONS=<n>; 0 = sin tope.
MAX_SESIONES = int(os.environ.get("TG_MAX_TOPIC_SESSIONS") or 0)

# Nota: topic-general no aparece aca porque el descubrimiento matchea solo
# topic-<numero>. El General lo atiende la sesion principal.


def log(msg):
    line = "%s %s\n" % (time.strftime("%H:%M:%S"), msg)
    try:
        with open(LOG, "a") as f:
            f.write(line)
    except OSError:
        pass
    sys.stdout.write(line)
    sys.stdout.flush()


def sh(args, timeout=25):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        log("error corriendo %s: %s" % (" ".join(args[:3]), e))
        return None


def leer_env(var):
    try:
        for line in open(ENV_FILE):
            m = re.match(r"^%s=(.*)$" % re.escape(var), line.rstrip("\n"))
            if m:
                v = m.group(1)
                if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                    v = v[1:-1]
                return v.strip()
    except OSError:
        pass
    return ""


GROUP_ID = os.environ.get("TG_GROUP_ID") or leer_env("TELEGRAM_GROUP_ID")


# ---------------- tmux ----------------
def sesiones_vivas():
    """list-sessions, NO `tmux info` (sale 1 sin cliente adjunto)."""
    r = sh(["tmux", "list-sessions", "-F", "#{session_name}"])
    if not r or r.returncode != 0:
        return set()
    return {l.strip() for l in r.stdout.splitlines() if l.strip()}


def matar_sesion(nombre):
    """kill-session, JAMAS kill-server (se llevaria a todos los agentes)."""
    sh(["tmux", "kill-session", "-t", nombre])
    log("sesion %s terminada" % nombre)


def esperar_listo(sesion, intentos=40):
    """Contesta los dialogos de arranque igual que entrypoint-interactive.sh."""
    for _ in range(intentos):
        r = sh(["tmux", "capture-pane", "-t", sesion, "-p"])
        pane = (r.stdout if r else "") or ""
        low = pane.lower()
        if "bypass permissions mode" in low:
            sh(["tmux", "send-keys", "-t", sesion, "2"])
            time.sleep(0.5)
            sh(["tmux", "send-keys", "-t", sesion, "Enter"])
        elif "? for shortcuts" in low or "bypass permissions on" in low:
            return True
        else:
            sh(["tmux", "send-keys", "-t", sesion, "Enter"])
        time.sleep(2)
    return False


def prompt_arranque(tid, nombre):
    """UNA sola linea: un \\n en send-keys -l manda el mensaje a medias."""
    resp = "TG_CHAT_ID=%s TG_TOPIC_ID=%s bash bin/tg.sh send '<respuesta con tags HTML>'" % (GROUP_ID, tid)
    return (
        "Eres %s. Esta sesion atiende UN solo tema del grupo de Telegram: "
        "el tema \"%s\" (topic-%s). No atiendes ningun otro tema ni el chat privado: "
        "esos los cubren otras sesiones. Haz esto en orden: "
        "(1) Levanta AHORA con la herramienta Monitor (persistente, JAMAS un Bash en background) "
        "el comando: bash %s/bin/tg_tail.sh topic-%s -- cada linea que emita es un evento tuyo. "
        "(2) Para responder usa SIEMPRE: %s -- si omites TG_TOPIC_ID tu respuesta cae en otro tema "
        "y %s no la ve donde la espera. tg.sh reply <msg_id> y tg.sh avance funcionan igual. "
        "(3) Formato: tags HTML, nunca Markdown; parrafos cortos con linea en blanco; negritas en "
        "cifras, nombres y la decision; enumera con punto medio cuando hay mas de dos items. "
        "(4) Lee %s/memory/MEMORY.md antes de asumir contexto, y CONFIRMA con %s antes de "
        "tocar produccion (Make, CRM, WhatsApp, VPS de clientes). "
        "(5) NO mandes saludo ni aviso de arranque: responde solo cuando llegue un evento. "
        "(6) Si no hay nada pendiente en tu tema, no escribas nada y espera."
        % (AGENT_NAME, nombre, tid, WS, tid, resp, OWNER_NAME, WS, OWNER_NAME)
    )


def memoria_mb():
    """(usado, techo) del contenedor en MB. (None, None) si no se puede leer.

    cgroup v2 primero, v1 de respaldo.
    """
    pares = [
        ("/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max"),
        ("/sys/fs/cgroup/memory/memory.usage_in_bytes",
         "/sys/fs/cgroup/memory/memory.limit_in_bytes"),
    ]
    for fu, fl in pares:
        try:
            usado = int(open(fu).read().strip())
            crudo = open(fl).read().strip()
            if crudo == "max":
                return usado // 1048576, None
            techo = int(crudo)
            # v1 sin limite reporta un numero absurdo (~8 EB)
            if techo > (1 << 62):
                return usado // 1048576, None
            return usado // 1048576, techo // 1048576
        except (OSError, ValueError):
            continue
    return None, None


def memoria_host_mb():
    """MB realmente disponibles en el HOST, o None si no se puede leer.

    Truco a favor: dentro de un contenedor Docker (sin lxcfs) `/proc/meminfo` NO
    esta namespaceado -- muestra la memoria de la MAQUINA. Eso, que suele ser una
    molestia, aca es justo lo que hace falta: es la unica forma que tiene el
    agente de saber si el VPS esta apretado sin salir a preguntarle al host.

    Se usa MemAvailable, no MemFree: MemFree ignora el cache reclamable y en un
    host con trabajo real da casi cero siempre, lo que bloquearia todo tema nuevo.
    """
    try:
        for linea in open("/proc/meminfo"):
            if linea.startswith("MemAvailable:"):
                return int(linea.split()[1]) // 1024   # viene en kB
    except (OSError, ValueError, IndexError):
        pass
    return None


# Margen que se deja libre. Una sesion Claude trabajando con contexto largo pasa
# el giga (medido: 1.5 GB en otro agente de la flota), asi que el margen tiene
# que alcanzar para que la que ya corre crezca, no solo para la que nace.
MARGEN_MB = int(os.environ.get("TG_SPAWN_MARGEN_MB") or 1800)

# Margen del HOST. Es el que manda ahora que los contenedores estan en 10 GB
# sobre un host de 16: la suma de los mem_limit excede por lejos la RAM fisica,
# asi que ningun contenedor va a tocar su tope -- se acaba antes la memoria de la
# maquina. Y cuando eso pasa, al que mata lo elige el kernel: puede ser el agente
# de otro cliente. Este margen es lo unico que separa "un tema mas" de "se cayo
# otro agente".
MARGEN_HOST_MB = int(os.environ.get("TG_SPAWN_MARGEN_HOST_MB") or 2500)


def levantar(tid, nombre):
    sesion = "tema-%s" % tid
    vivas = sesiones_vivas()
    if sesion in vivas:
        return False
    propias = [s for s in vivas if s.startswith("tema-")]
    if MAX_SESIONES and len(propias) >= MAX_SESIONES:
        # Solo si alguien puso un tope a mano. No recortar en silencio: que se
        # vea que un tema quedo sin sesion.
        log("RECHAZO tema %s (%s): ya hay %d sesiones de tema y hay un tope "
            "puesto a mano de %d (TG_MAX_TOPIC_SESSIONS). Ese tema NO tiene "
            "sesion propia; lo tiene que cubrir la sesion principal."
            % (tid, nombre, len(propias), MAX_SESIONES))
        return False

    # Guard de memoria REAL, en dos niveles. Reemplaza al techo fijo de sesiones:
    # el limite ya no es un numero inventado sino cuanta RAM hay.
    #
    #   1) el contenedor, para no morir nosotros;
    #   2) el HOST, que es el que manda de verdad -- con los mem_limit en 10 GB
    #      sobre 16 GB fisicos, nadie llega a su tope: se acaba antes la memoria
    #      de la maquina, y ahi el kernel elige a quien matar. Puede tocarle al
    #      agente de otro cliente, que no tiene nada que ver con este tema.
    usado, techo = memoria_mb()
    if usado is not None and techo:
        libre = techo - usado
        if libre < MARGEN_MB:
            log("RECHAZO tema %s (%s): memoria justa en el contenedor -- %d MB "
                "usados de %d, quedan %d y el margen exigido es %d. NO levanto "
                "la sesion. Ese tema lo cubre la sesion principal."
                % (tid, nombre, usado, techo, libre, MARGEN_MB))
            return False

    libre_host = memoria_host_mb()
    if libre_host is not None and libre_host < MARGEN_HOST_MB:
        log("RECHAZO tema %s (%s): el HOST esta apretado -- quedan %d MB "
            "disponibles y el margen exigido es %d. No es un tope de sesiones: "
            "es que no hay RAM en el VPS. Levantar una sesion mas aca puede "
            "hacer que el kernel mate a OTRO agente. Ese tema lo cubre la "
            "sesion principal; cuando se libere memoria, el proximo mensaje al "
            "tema vuelve a intentarlo."
            % (tid, nombre, libre_host, MARGEN_HOST_MB))
        return False

    # El entorno se exporta DENTRO del comando de tmux para que claude y todo lo
    # que ejecute lo herede. Asi los bin/*.sh quedan identicos entre sesiones.
    cmd = ("cd %s && export TG_STATE_DIR=%s TG_CHAT_ID=%s TG_TOPIC_ID=%s "
           "AGENT_TOPIC=%s AGENT_WORKSPACE=%s && exec claude --dangerously-skip-permissions"
           % (WS, SD, GROUP_ID, tid, tid, WS))
    r = sh(["tmux", "new-session", "-d", "-s", sesion, "-x", "220", "-y", "50", cmd])
    if not r or r.returncode != 0:
        log("FALLO al crear la sesion %s: %s" % (sesion, (r.stderr if r else "?")))
        return False
    log("sesion %s creada para el tema \"%s\"" % (sesion, nombre))

    if not esperar_listo(sesion):
        log("OJO: %s no llego a estar lista (dialogos de arranque); la dejo igual "
            "y reintento el prompt" % sesion)
    time.sleep(1)
    sh(["tmux", "send-keys", "-t", sesion, "-l", prompt_arranque(tid, nombre)])
    time.sleep(1)
    sh(["tmux", "send-keys", "-t", sesion, "Enter"])
    log("prompt de arranque enviado a %s (tema \"%s\")" % (sesion, nombre))
    return True


# ---------------- descubrimiento ----------------
def temas_del_inbox():
    out = {}
    try:
        for f in os.listdir(INBOX):
            m = re.match(r"^topic-(\d+)\.jsonl$", f)
            if m:
                out[m.group(1)] = None
    except OSError:
        pass
    return out


def nombres_conocidos():
    """Escaneo COMPLETO de control.jsonl solo para sacar los nombres de los temas.

    Por que existe: el mapa tid->nombre vivia solo en memoria, y el cursor de
    control se persiste. Si el spawner se reinicia (o muere y vuelve), los
    eventos `created` ya estan consumidos y los nombres se pierden: las sesiones
    arrancaban creyendo atender "tema 3" en vez de "SEO". Paso en vivo.
    Los nombres son idempotentes, asi que releerlos entero no tiene costo.
    """
    out = {}
    path = os.path.join(INBOX, "control.jsonl")
    try:
        for raw in open(path):
            try:
                l = json.loads(raw)["line"]
            except Exception:
                continue
            m = re.search(r"\[TG-TOPIC\] (?:created|edited) thread_id=(\d+) name=(.*)$", l)
            if m and m.group(2).strip():
                out[m.group(1)] = m.group(2).strip()
    except OSError:
        pass
    return out


def eventos_control_nuevos():
    """Lee control.jsonl con cursor PROPIO (no el del agente, o se lo robamos)."""
    path = os.path.join(INBOX, "control.jsonl")
    try:
        pos = int(open(CURSOR_CTRL).read().strip() or 0)
    except (OSError, ValueError):
        pos = 0
    lineas, total = [], 0
    try:
        with open(path) as f:
            for i, raw in enumerate(f):
                total = i + 1
                if i < pos:
                    continue
                try:
                    lineas.append(json.loads(raw)["line"])
                except Exception:
                    pass
    except OSError:
        return []
    if total < pos:                     # truncado
        pos = 0
    with open(CURSOR_CTRL, "w") as f:
        f.write(str(total))
    return lineas


def tomar_candado():
    """Un solo spawner: dos levantarian la misma sesion dos veces."""
    try:
        os.mkdir(LOCKD)
    except FileExistsError:
        viejo = ""
        try:
            viejo = open(os.path.join(LOCKD, "pid")).read().strip()
        except OSError:
            pass
        if viejo.isdigit():
            try:
                os.kill(int(viejo), 0)
                log("ya hay un spawner vivo (pid %s); salgo" % viejo)
                return False
            except OSError:
                pass
        # candado huerfano
        try:
            os.remove(os.path.join(LOCKD, "pid"))
        except OSError:
            pass
        try:
            os.rmdir(LOCKD)
        except OSError:
            pass
        try:
            os.mkdir(LOCKD)
        except OSError:
            log("no pude tomar el candado; salgo")
            return False
    with open(os.path.join(LOCKD, "pid"), "w") as f:
        f.write(str(os.getpid()))
    import atexit

    def _soltar():
        try:
            os.remove(os.path.join(LOCKD, "pid"))
        except OSError:
            pass
        try:
            os.rmdir(LOCKD)
        except OSError:
            pass

    atexit.register(_soltar)
    return True


def una_pasada(nombres, cerrados):
    """Un ciclo completo. Separado de main() a proposito: asi se puede probar.

    (Antes el cuerpo vivia dentro del while y una pasada nunca se ejecutaba en
    las pruebas -- se colo un NameError que mato el proceso en produccion sin
    dejar rastro, porque con `docker exec -d` stdout va a la nada.)
    """
    for l in eventos_control_nuevos():
        m = re.search(r"\[TG-TOPIC\] created thread_id=(\d+) name=(.*)$", l)
        if m:
            nombres[m.group(1)] = m.group(2).strip() or ("tema %s" % m.group(1))
            cerrados.discard(m.group(1))
            log("tema nuevo detectado: %s = %s" % (m.group(1), nombres[m.group(1)]))
            continue
        m = re.search(r"\[TG-TOPIC\] closed thread_id=(\d+)", l)
        if m:
            tid = m.group(1)
            cerrados.add(tid)
            log("tema %s cerrado por Sebastian -> bajo su sesion" % tid)
            if ("tema-%s" % tid) in sesiones_vivas():
                matar_sesion("tema-%s" % tid)
            continue
        m = re.search(r"\[TG-TOPIC\] reopened thread_id=(\d+)", l)
        if m:
            cerrados.discard(m.group(1))
            log("tema %s reabierto -> vuelvo a levantar su sesion" % m.group(1))
            continue
        m = re.search(r"\[TG-TOPIC\] edited thread_id=(\d+) name=(.*)$", l)
        if m and m.group(2).strip():
            nombres[m.group(1)] = m.group(2).strip()

    creadas = 0
    for tid in sorted(temas_del_inbox(), key=int):
        if tid in cerrados:
            continue
        if levantar(tid, nombres.get(tid, "tema %s" % tid)):
            creadas += 1
    return creadas


def main():
    os.makedirs(INBOX, exist_ok=True)
    if not GROUP_ID:
        log("FATAL: sin TELEGRAM_GROUP_ID; sin grupo no hay temas que atender")
        sys.exit(1)
    if not tomar_candado():
        sys.exit(0)
    log("spawner arrancado ws=%s grupo=%s techo=%s (margen contenedor %d MB, "
        "margen host %d MB, host con %s MB libres)"
        % (WS, GROUP_ID,
           ("%d sesiones" % MAX_SESIONES) if MAX_SESIONES else "sin tope",
           MARGEN_MB, MARGEN_HOST_MB, memoria_host_mb()))

    # Los nombres se reconstruyen del historial completo, NO del cursor: si no,
    # tras un reinicio del spawner las sesiones nacen sin saber a que tema
    # atienden (arrancaron como "tema 3" en vez de "SEO").
    nombres = nombres_conocidos()
    cerrados = set()      # temas cerrados a proposito: no relevantar
    if nombres:
        log("nombres recuperados del historial: %s"
            % ", ".join("%s=%s" % (k, v) for k, v in sorted(nombres.items(), key=lambda x: int(x[0]))))

    while True:
        try:
            una_pasada(nombres, cerrados)
        except Exception:
            # Sin esto, cualquier excepcion mata el proceso en silencio: con
            # `docker exec -d` no hay terminal donde se vea el traceback.
            import traceback
            log("EXCEPCION en la pasada:\n%s" % traceback.format_exc())
        time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        import traceback
        log("EXCEPCION FATAL:\n%s" % traceback.format_exc())
        raise
