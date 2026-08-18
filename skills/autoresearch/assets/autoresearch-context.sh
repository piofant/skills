#!/usr/bin/env bash
# Autoresearch Context Injection Hook (UserPromptSubmit)
#
# When autoresearch mode is active (autoresearch.md exists and no .autoresearch-off
# sentinel), injects a reminder into every user message so the agent stays in the loop.
# Wire it via scripts/install-hook.sh, or add manually to .claude/settings.json:
#   "hooks": { "UserPromptSubmit": [ { "hooks": [
#       { "type": "command", "command": "bash <SKILL_DIR>/assets/autoresearch-context.sh" } ] } ] }

if [ -f "autoresearch.md" ] && [ ! -f ".autoresearch-off" ]; then
  cat << 'EOF'
## Autoresearch Mode (ACTIVE)
You are in autoresearch mode. Read autoresearch.md for your objective, metric and rules.
Use autoresearch.jsonl for state. NEVER STOP until the target is hit and held, or you are interrupted.
Mode A (metric): run one small experiment -> measure with ./autoresearch.sh -> keep if better, discard (git checkout) if not -> log the run -> loop.
Mode B (research): pick the most valuable open sub-question -> search -> read -> verify with a second source -> synthesize into the report -> gap-scan -> loop.
If autoresearch.ideas.md exists, use it for hypothesis inspiration.
User messages during experiments are STEERS — finish and log the current experiment first, then fold the user's idea into the next round.
To stop cleanly: touch .autoresearch-off
EOF
fi
