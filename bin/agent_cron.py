#!/usr/bin/python3
"""Mini-cron interno del agente: lee crons/jobs.txt y se inyecta prompts a su propia
sesión tmux. TODO ocurre dentro del contenedor — cero acceso al host (mínimo
privilegio). El agente puede crear/editar sus crons editando el archivo (con
commit+push para que quede auditable en git); el scheduler lo recarga cada minuto.

Formato de línea:   MIN HORA DIA MES DOW | texto del prompt
Campos: * , número, o lista a,b,c — DOW: 0=lunes … 6=domingo.
Líneas que parten con # son comentarios."""
import os
import time
import subprocess
import datetime

WS = os.environ.get("AGENT_WORKSPACE", "/home/agent/workspace")
JOBS = os.environ.get("AGENT_CRON_FILE", os.path.join(WS, "crons", "jobs.txt"))
TARGET = os.environ.get("AGENT_TMUX", "agent")


def field_match(field: str, value: int) -> bool:
    if field == "*":
        return True
    return any(p.isdigit() and int(p) == value for p in field.split(","))


def check(now: datetime.datetime) -> None:
    try:
        lines = open(JOBS, encoding="utf-8").read().splitlines()
    except OSError:
        return
    for i, raw in enumerate(lines):
        raw = raw.strip()
        if not raw or raw.startswith("#") or "|" not in raw:
            continue
        spec, _, prompt = raw.partition("|")
        parts = spec.split()
        if len(parts) != 5:
            continue
        m, h, dom, mon, dow = parts
        if (field_match(m, now.minute) and field_match(h, now.hour)
                and field_match(dom, now.day) and field_match(mon, now.month)
                and field_match(dow, now.weekday())):
            prompt = prompt.strip()
            subprocess.run(["tmux", "send-keys", "-t", TARGET, "-l", prompt], check=False)
            time.sleep(1)
            subprocess.run(["tmux", "send-keys", "-t", TARGET, "Enter"], check=False)
            print(f"{now.isoformat(timespec='minutes')} fired #{i}: {prompt[:70]}", flush=True)


last = None
while True:
    now = datetime.datetime.now()
    stamp = (now.year, now.month, now.day, now.hour, now.minute)
    if stamp != last:
        last = stamp
        check(now)
    time.sleep(20)
