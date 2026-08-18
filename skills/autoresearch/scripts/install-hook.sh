#!/usr/bin/env bash
# Wire the autoresearch reminder hook into ./.claude/settings.json (project scope).
# Idempotent: safe to run twice. Requires jq.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="bash \"$SKILL_DIR/assets/autoresearch-context.sh\""
SETTINGS=".claude/settings.json"
mkdir -p .claude
[[ -f "$SETTINGS" ]] || echo '{}' > "$SETTINGS"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found. Add this UserPromptSubmit hook to $SETTINGS manually:" >&2
  echo "  $HOOK" >&2
  exit 1
fi

tmp=$(mktemp)
jq --arg cmd "$HOOK" '
  .hooks = (.hooks // {}) |
  .hooks.UserPromptSubmit = (.hooks.UserPromptSubmit // []) |
  if any(.hooks.UserPromptSubmit[]?; (.hooks[]?.command // "") == $cmd)
  then .
  else .hooks.UserPromptSubmit += [ { "hooks": [ { "type":"command", "command":$cmd } ] } ]
  end
' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"

echo "autoresearch reminder hook installed into $SETTINGS"
