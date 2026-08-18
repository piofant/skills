#!/usr/bin/env bash
# Ralph Loop — standalone CLI driver (Geoffrey Huntley's original form).
# Runs an agent headless on the SAME prompt in a while-true loop until done.
# No Claude Code hooks needed — works with Claude CLI, Codex, on a VPS, in cron.
#
# Usage:
#   ralph-run.sh --prompt PROMPT.md [--max 50] [--agent claude|codex] [--sleep 2]
#                [--promise 'ALL TESTS PASS']
#
# Stop conditions:
#   * reached --max iterations
#   * `touch .ralph-stop` sentinel appears
#   * agent output contains <promise>YOUR_PHRASE</promise> (if --promise set)
#   * Ctrl-C
set -euo pipefail

PROMPT_FILE="PROMPT.md"
MAX=0                 # 0 = unlimited
AGENT="claude"
SLEEP=2
PROMISE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)  PROMPT_FILE="$2"; shift 2;;
    --max)     MAX="$2"; shift 2;;
    --agent)   AGENT="$2"; shift 2;;
    --sleep)   SLEEP="$2"; shift 2;;
    --promise) PROMISE="$2"; shift 2;;
    -h|--help)
      sed -n '2,20p' "$0"; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done

[[ -f "$PROMPT_FILE" ]] || { echo "prompt file not found: $PROMPT_FILE" >&2; exit 1; }
rm -f .ralph-stop

# Build the per-iteration command for the chosen agent CLI.
run_agent() {
  local prompt="$1"
  case "$AGENT" in
    claude) claude -p "$prompt" --dangerously-skip-permissions 2>&1;;
    codex)  codex exec "$prompt" 2>&1;;
    *) echo "unknown agent: $AGENT (use claude|codex)" >&2; exit 1;;
  esac
}

i=0
echo "🔄 Ralph standalone loop — agent=$AGENT prompt=$PROMPT_FILE max=$([[ $MAX -gt 0 ]] && echo $MAX || echo unlimited)"
while :; do
  i=$((i+1))
  if [[ $MAX -gt 0 && $i -gt $MAX ]]; then echo "🛑 Reached max iterations ($MAX)."; break; fi
  if [[ -f .ralph-stop ]]; then echo "🛑 .ralph-stop sentinel found — stopping."; rm -f .ralph-stop; break; fi

  echo "──────── Ralph iteration $i ($(date -u +%H:%M:%SZ)) ────────"
  PROMPT=$(cat "$PROMPT_FILE")
  OUT=$(run_agent "$PROMPT" || true)
  echo "$OUT"

  if [[ -n "$PROMISE" ]] && echo "$OUT" | grep -qF "<promise>$PROMISE</promise>"; then
    echo "✅ Completion promise detected — task done at iteration $i."
    break
  fi
  sleep "$SLEEP"
done
