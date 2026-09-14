#!/usr/bin/env python3
"""Avisa «tu ticket quedó resuelto» desde cualquier agente, tenga o no `tg.sh`.

Se ejecuta DENTRO del contenedor del agente:

    python3 - "<nombre del agente>"     # por stdin, sin dejar el archivo

Existe porque el script de los Claude usa `bin/tg.sh`, que los Codex no tienen, y
porque **montarle un reloj propio a cada agente implica tocarle la imagen o el
arranque** — trabajo de infraestructura, uno por uno, en contenedores de clientes.

Acá el mensaje lo sigue mandando **el bot del propio agente**: el cliente ve lo
mismo de siempre, en su chat de siempre. Lo único que viene de afuera es el
disparo, que lo hace el vigía central cada media hora.

El token se lee del entorno del propio contenedor (`TELEGRAM_TOKEN_VAR` dice cuál
es la variable, que cambia por agente) y el destinatario de `TELEGRAM_OWNER_ID`.
Nada de eso sale del contenedor.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

CMS = "https://cms.gopointagency.com/api/agent-tickets"


def token():
    var = os.environ.get("TELEGRAM_TOKEN_VAR", "TELEGRAM_BOT_TOKEN")
    valor = os.environ.get(var) or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not valor:
        # Los Codex guardan el token en un archivo cuando no va por entorno.
        for ruta in ("~/.codex/telegram-bridge/token", "~/.claude/tgstate/token"):
            try:
                with open(os.path.expanduser(ruta), encoding="utf-8") as fh:
                    valor = fh.read().strip()
                    if valor:
                        break
            except OSError:
                continue
    return valor


def clave():
    """La busca en el workspace primero, que es lo que sobrevive.

    Estuvo sólo en `~` y varios agentes la perdieron al recrearse el contenedor:
    el home no siempre es un volumen, el workspace sí. Se mira en los dos por si
    alguno todavía la tiene del lado viejo.
    """
    for ruta in (".agent-tickets.key",
                 os.path.join(os.environ.get("AGENT_WORKSPACE", ""), ".agent-tickets.key"),
                 "/workspace/.agent-tickets.key",
                 os.path.expanduser("~/.agent-tickets.key")):
        if not ruta:
            continue
        try:
            with open(ruta, encoding="utf-8") as fh:
                valor = fh.read().strip()
                if valor:
                    return valor
        except OSError:
            continue
    sys.exit("no encuentro mi clave de tickets (.agent-tickets.key)")


def api(ruta, metodo="GET", cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(
        CMS + ruta, data=datos, method=metodo,
        headers={"X-Agent-Key": clave(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def telegram(texto):
    tok, destino = token(), dueno()
    if not tok or not destino:
        return False
    datos = urllib.parse.urlencode({
        "chat_id": destino, "text": texto, "parse_mode": "HTML",
    }).encode()
    try:
        with urllib.request.urlopen(
            "https://api.telegram.org/bot%s/sendMessage" % tok, data=datos, timeout=30
        ) as r:
            return json.loads(r.read().decode()).get("ok", False)
    except Exception:
        return False


def dueno():
    """Un solo lugar para el destinatario, con las fuentes viejas de respaldo.

    `.agent-owner` lo deja igual en toda la flota (`agente_owner_emparejar.py`).
    Las otras fuentes quedan porque un agente nuevo puede llegar sin el archivo, y
    quedarse sin avisar por eso sería el mismo error que esto vino a arreglar.
    """
    for ruta in (".agent-owner",
                 os.path.join(os.environ.get("AGENT_WORKSPACE", ""), ".agent-owner"),
                 "/workspace/.agent-owner"):
        if not ruta:
            continue
        try:
            v = open(ruta, encoding="utf-8").read().strip()
            if v:
                return v
        except OSError:
            continue
    for var in ("TELEGRAM_OWNER_ID", "TG_OWNER_ID"):
        v = (os.environ.get(var) or "").strip()
        if v:
            return v
    return (os.environ.get("TELEGRAM_ALLOWED_USERS") or "").split(",")[0].strip()


def main():
    nombre = sys.argv[1]
    tickets = api("?agentName=" + urllib.parse.quote(nombre))["tickets"]
    for t in tickets:
        if t.get("status") != "resuelto" or t.get("resolvedNotifiedAt"):
            continue
        texto = ("✅ <b>Se resolvió lo que te comenté</b>\n\n"
                 "El ticket <b>#%s</b> que abrí en GoPoint por «%s» quedó resuelto.\n\n"
                 "Si el problema sigue, decímelo y lo reabro." % (t["id"], t["title"]))
        if not telegram(texto):
            print("no pude avisar del #%s" % t["id"])
            continue
        api("/%s/avisado" % t["id"], "POST", {"agentName": nombre})
        print("avisado el #%s" % t["id"])


if __name__ == "__main__":
    main()
