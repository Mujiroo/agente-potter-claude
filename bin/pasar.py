#!/usr/bin/env python3
"""Pasarle un encargo a otro agente del MISMO cliente, sin abrir un ticket.

    python3 bin/pasar.py --de Menta --para Melisa --cliente "Cafe Diario" \
        --mensaje "Faltan dos facturas en la planilla de Paulina: ..."

    python3 bin/pasar.py --buzon --para Melisa --cliente "Cafe Diario"
    python3 bin/pasar.py --recibido 12 --para Melisa

Nació el 11-ago-2026. Los agentes estaban **abriendo tickets de soporte para
hablarse entre ellos**: Menta abrió el #55 y el #66 para pedirle a Melisa, su
compañera del mismo cliente, que actualizara una planilla. Eso no es soporte, es
un encargo, y pasaba por GoPoint sólo porque no había otra vía. Sebastián:
*«mejor arregla eso para que no dependa de crear un ticket»*.

**Un ticket sigue siendo lo correcto** cuando lo que falta lo tiene que resolver
una persona de GoPoint: un acceso, una credencial, algo roto de la
infraestructura. Esto es para lo otro.

**Lo leído no es lo recibido.** El buzón no marca nada: el destinatario confirma
con `--recibido` cuando ya lo tiene. Si se marcara al leer, una caída entre la
lectura y el trabajo se llevaría el encargo sin que nadie se entere.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

CMS = "https://cms.gopointagency.com/api/agent-messages"


def clave():
    # Las mismas rutas que busca tickets_avisar_universal.py: cada agente la tiene
    # en un lugar distinto segun como quedo armado su contenedor.
    for ruta in (".agent-tickets.key",
                 os.path.join(os.environ.get("AGENT_WORKSPACE", ""), ".agent-tickets.key"),
                 "/workspace/.agent-tickets.key",
                 os.path.expanduser("~/.agent-tickets.key")):
        try:
            with open(ruta, encoding="utf-8") as f:
                v = f.read().strip()
                if v:
                    return v
        except FileNotFoundError:
            pass
    v = os.getenv("AGENT_TICKETS_KEY", "").strip()
    if v:
        return v
    sys.exit("falta la clave de agente (~/.agent-tickets.key o AGENT_TICKETS_KEY)")


def api(ruta="", metodo="GET", cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(
        CMS + ruta, data=datos, method=metodo,
        headers={"X-Agent-Key": clave(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        # El cuerpo del error dice el motivo; el código solo dice que falló.
        sys.exit("HTTP %s: %s" % (e.code, e.read().decode()[:300]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--de")
    p.add_argument("--para", required=True)
    p.add_argument("--cliente")
    p.add_argument("--mensaje")
    p.add_argument("--buzon", action="store_true", help="lo que tenes sin recibir")
    p.add_argument("--recibido", type=int, metavar="ID")
    a = p.parse_args()

    if a.recibido:
        api("/%d/recibido" % a.recibido, "POST", {"para": a.para})
        print("recibido #%d" % a.recibido)
        return

    if a.buzon:
        if not a.cliente:
            sys.exit("--buzon necesita --cliente")
        r = api("?para=%s&cliente=%s" % (
            urllib.request.quote(a.para), urllib.request.quote(a.cliente)))
        if not r["mensajes"]:
            print("no tenes nada pendiente")
            return
        for m in r["mensajes"]:
            print("#%d de %s (%s)\n%s\n" % (m["id"], m["de"], m["createdAt"], m["mensaje"]))
        print("cuando lo tengas: python3 bin/pasar.py --recibido <id> --para %s" % a.para)
        return

    if not (a.de and a.cliente and a.mensaje):
        sys.exit("para mandar hacen falta --de, --para, --cliente y --mensaje")
    r = api("", "POST", {"de": a.de, "para": a.para, "cliente": a.cliente, "mensaje": a.mensaje})
    print("le quedo a %s el mensaje #%d" % (a.para, r["id"]))


if __name__ == "__main__":
    main()
