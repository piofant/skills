#!/usr/bin/env bash
# Wire the Ralph Stop-hook into ./.claude/settings.json (project scope).
# Idempotent. Requires jq. After this, setup-ralph-loop.sh activates the in-session loop.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="bash \"$SKILL_DIR/scripts/stop-hook.sh\""
SETTINGS=".claude/settings.json"
mkdir -p .claude
[[ -f "$SETTINGS" ]] || echo '{}' > "$SETTINGS"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found. Add this Stop hook to $SETTINGS manually:" >&2
  echo "  $HOOK" >&2
  exit 1
fi

tmp=$(mktemp)
jq --arg cmd "$HOOK" '
  .hooks = (.hooks // {}) |
  .hooks.Stop = (.hooks.Stop // []) |
  if any(.hooks.Stop[]?; (.hooks[]?.command // "") == $cmd)
  then .
  else .hooks.Stop += [ { "hooks": [ { "type":"command", "command":$cmd } ] } ]
  end
' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"

echo "Ralph Stop-hook installed into $SETTINGS"
echo "Now start a loop with: bash \"$SKILL_DIR/scripts/setup-ralph-loop.sh\" \"<your task>\" --max-iterations 30"
