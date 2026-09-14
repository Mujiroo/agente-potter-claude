#!/usr/bin/env python3
"""Deja el id de la dueña o dueño del agente en UN lugar, siempre el mismo.

Se ejecuta DENTRO del contenedor, con W (workspace) en el entorno.

Hoy ese dato está en cuatro sitios distintos según el agente: `TELEGRAM_OWNER_ID`,
`TELEGRAM_ALLOWED_USERS`, `TG_OWNER_ID` o el `config.json` del puente de Codex.
Mientras eso siga así, cualquier aviso automático tiene que adivinar dónde mirar,
y cuando no acierta **falla en silencio**: el mensaje simplemente no sale. Ya pasó
dos veces el 7-ago-2026, con los agentes de Jesús y de Estefanía.

Esto no cambia la configuración de nadie: **lee** de donde esté y lo **copia** a
`<workspace>/.agent-owner`, que es el lugar que van a mirar los scripts. Va al
workspace y no al home porque el home no siempre sobrevive a que recreen el
contenedor.
"""
import json
import os
import pathlib

W = pathlib.Path(os.environ["W"])


def buscar():
    for var in ("TELEGRAM_OWNER_ID", "TG_OWNER_ID"):
        v = (os.environ.get(var) or "").strip()
        if v.isdigit():
            return v, var
    v = (os.environ.get("TELEGRAM_ALLOWED_USERS") or "").split(",")[0].strip()
    if v.isdigit():
        return v, "TELEGRAM_ALLOWED_USERS"
    # Algunos lo tienen escrito a mano en su propio puente (`OWNER=123...`), que
    # es de donde de verdad lo lee ese agente: si no se mira ahí, el emparejado
    # falla justo en los que más costó encontrarlo.
    for guion in ("bin/tg_bridge.sh", str(W / "bin" / "tg_bridge.sh")):
        try:
            for linea in open(guion, encoding="utf-8"):
                if linea.startswith("OWNER="):
                    v = linea.split("=", 1)[1].strip().strip('"').strip("'")
                    if v.isdigit():
                        return v, "OWNER de su tg_bridge.sh"
        except OSError:
            continue
    for ruta in ("~/.codex/telegram-bridge/config.json", "~/.claude/telegram-bridge/config.json"):
        try:
            d = json.load(open(os.path.expanduser(ruta), encoding="utf-8"))
        except Exception:
            continue
        v = str(d.get("owner_telegram_id") or "").strip()
        if v.isdigit():
            return v, "config.json del puente"
    return "", ""


valor, origen = buscar()
destino = W / ".agent-owner"

if not valor:
    print("NO ENCONTRE el dueño en ninguna de las fuentes conocidas")
elif destino.exists() and destino.read_text(encoding="utf-8").strip() == valor:
    print("ya estaba (%s)" % valor)
else:
    destino.write_text(valor + "\n", encoding="utf-8")
    destino.chmod(0o600)
    print("emparejado: %s (venía de %s)" % (valor, origen))
