#!/bin/bash
# FEATURE 1 — aplica /model o /effort a la propia sesion de Claude Code via tmux send-keys.
# Uso: tg_model.sh model <alias>   |   tg_model.sh effort <nivel>
# Allowlist estricta: NUNCA se le pasa texto arbitrario de Telegram al REPL (seria auto-inyeccion).
set -u
TARGET="${AGENT_TMUX:-agent}:0.0"
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$SELF_DIR/tg_model.log"
KIND="${1:-}"; ARG="$(printf '%s' "${2:-}" | tr '[:upper:]' '[:lower:]')"

case "$KIND" in
  model)
    case "$ARG" in
      fable|fable5|"claude-fable-5")            VAL=claude-fable-5 ;;
      opus|opus4.8|"claude-opus-4-8")           VAL=claude-opus-4-8 ;;
      sonnet|"claude-sonnet-5")                 VAL=claude-sonnet-5 ;;
      haiku|"claude-haiku-4-5-20251001")        VAL=claude-haiku-4-5-20251001 ;;
      *) echo "RECHAZADO: modelo '$ARG' no esta en la allowlist (fable|opus|sonnet|haiku)"; exit 2 ;;
    esac
    CMD="/model $VAL" ;;
  effort)
    case "$ARG" in
      low|medium|high|xhigh|max) VAL="$ARG" ;;
      *) echo "RECHAZADO: effort '$ARG' invalido (low|medium|high|xhigh|max)"; exit 2 ;;
    esac
    CMD="/effort $VAL" ;;
  *)
    echo "uso: tg_model.sh model|effort <valor>"; exit 1 ;;
esac

# Watcher totalmente desacoplado (setsid) para que sobreviva al fin del turno/tool del agente.
# 1) encola el comando en el REPL (se aplica al cerrar el turno actual)
# 2) /model abre dialogo modal "Switch model?" -> hay que confirmar con Enter (opcion 1 = default),
#    si no la sesion headless queda trabada. Poll del pane hasta 60s y confirma.
# 3) /effort normalmente cambia directo (sin dialogo): el poll ve "Set ... effort" y sale.
setsid bash -c '
  T="'"$TARGET"'"; CMD="'"$CMD"'"; LOG="'"$LOG"'"
  echo "[$(date -u +%H:%M:%S)] enviando: $CMD" >> "$LOG"
  sleep 2
  tmux send-keys -t "$T" -l "$CMD"
  sleep 0.4
  tmux send-keys -t "$T" Enter
  # Poll SOLO por el dialogo de confirmacion (model o effort). No salir por texto residual
  # tipo "Set effort to X" de un comando anterior: en el flujo por Telegram el comando se
  # encola y el dialogo aparece con retraso (al cerrar el turno del agente), asi que hay que
  # seguir esperandolo. Si en toda la ventana no aparece dialogo, fue aplicacion directa.
  for i in $(seq 1 45); do
    sleep 1
    PANE=$(tmux capture-pane -t "$T" -p 2>/dev/null)
    if printf "%s" "$PANE" | grep -qiE "switch model\?|change effort level\?|yes, switch to"; then
      sleep 0.4
      tmux send-keys -t "$T" Enter
      echo "[$(date -u +%H:%M:%S)] dialogo (model/effort) detectado en iter $i -> Enter enviado" >> "$LOG"
      sleep 1.5
      tmux capture-pane -t "$T" -p 2>/dev/null | grep -iE "set model to|set effort level to|kept" | tail -1 >> "$LOG"
      exit 0
    fi
  done
  echo "[$(date -u +%H:%M:%S)] ventana cerrada sin dialogo (aplicacion directa o sin cambio)" >> "$LOG"
' >/dev/null 2>&1 &

echo "OK: encolado '$CMD' en $TARGET (valor=$VAL) — watcher setsid con auto-confirmacion"
