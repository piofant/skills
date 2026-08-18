#!/usr/bin/env bash
# Append one experiment line to autoresearch.jsonl.
# Usage:
#   ar-log.sh --run 4 --metric 7 --status keep --desc "lore-specific openers" \
#             [--metrics '{"aggregate":4.97}'] [--commit abc1234] [--file autoresearch.jsonl]
set -euo pipefail

RUN="" METRIC="" STATUS="" DESC="" METRICS="{}" COMMIT="" FILE="autoresearch.jsonl"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run)     RUN="$2"; shift 2;;
    --metric)  METRIC="$2"; shift 2;;
    --status)  STATUS="$2"; shift 2;;     # keep | discard
    --desc)    DESC="$2"; shift 2;;
    --metrics) METRICS="$2"; shift 2;;    # JSON object of secondary metrics
    --commit)  COMMIT="$2"; shift 2;;
    --file)    FILE="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done

[[ -z "$RUN" || -z "$METRIC" || -z "$STATUS" ]] && { echo "need --run --metric --status" >&2; exit 1; }
[[ -z "$COMMIT" ]] && COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "nogit")
TS=$(date +%s)
# escape double quotes in description
DESC_ESC=${DESC//\"/\\\"}

printf '{"run":%s,"commit":"%s","metric":%s,"metrics":%s,"status":"%s","description":"%s","timestamp":%s}\n' \
  "$RUN" "$COMMIT" "$METRIC" "$METRICS" "$STATUS" "$DESC_ESC" "$TS" >> "$FILE"
echo "logged run $RUN ($STATUS, metric=$METRIC) -> $FILE"
