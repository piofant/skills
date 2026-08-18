#!/usr/bin/env bash
# judge.sh — popularity/trust signals for GitHub skill candidates (skill-scout helper).
# Usage: judge.sh <owner/repo> [<owner/repo> ...]
# Prints a markdown table: stars, forks, issues, last push date, license, flags.
set -uo pipefail

if [ $# -lt 1 ]; then
  echo "usage: judge.sh <owner/repo> [<owner/repo> ...]" >&2
  exit 1
fi

echo "| Repo | ⭐ | Forks | Issues | Updated | License | Flags |"
echo "|---|---|---|---|---|---|---|"

for repo in "$@"; do
  # gh api prints the error JSON to stdout on 404 — judge by exit code, not output
  if row=$(gh api "repos/$repo" --jq '
    "| \(.full_name)" +
    " | \(.stargazers_count)" +
    " | \(.forks_count)" +
    " | \(.open_issues_count)" +
    " | \(.pushed_at[:10])" +
    " | \(.license.spdx_id // "none")" +
    " | \([(if .archived then "ARCHIVED" else empty end),
          (if .fork then "fork" else empty end)] | join(" ") // "") |"
  ' 2>/dev/null) && [ -n "$row" ]; then
    echo "$row"
  else
    echo "| $repo | — | — | — | — | — | not found / no access |"
  fi
done
