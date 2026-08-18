#!/usr/bin/env bash
# skill-scout — the ClawHub layer (clawhub.ai): the public OpenClaw agent-skill registry.
# Three subcommands: search (find + metrics), judge (metrics / scan verdict per candidate),
# read (print SKILL.md or any skill file WITHOUT installing — for the security pass).
#
# Usage:
#   clawhub.sh search "<query>" [limit]      # limit defaults to 20
#   clawhub.sh judge @owner/slug [...]       # owner/slug also accepted
#   clawhub.sh read  @owner/slug [file]      # no file argument — list the files first
#
# ENV: CLAWHUB_API (defaults to https://clawhub.ai/api/v1)
# No auth needed: read and search endpoints are public.
set -uo pipefail

API="${CLAWHUB_API:-https://clawhub.ai/api/v1}"
CLI=(npx -y clawhub@latest)
CMD="${1:-}"; shift || true

norm() { printf '%s' "${1#@}"; }   # @owner/slug -> owner/slug

case "$CMD" in
search)
  Q="${1:-}"; LIM="${2:-20}"
  [ -z "$Q" ] && { echo "usage: clawhub.sh search \"<query>\" [limit]" >&2; exit 1; }
  TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
  curl -sS --max-time 30 --get "$API/search" --data-urlencode "q=$Q" --data-urlencode "limit=$LIM" -o "$TMP" 2>/dev/null
  if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if isinstance(d.get("results"),list) else 1)' "$TMP" 2>/dev/null; then
    python3 - "$Q" "$TMP" <<'PY'
import json, sys
q, path = sys.argv[1], sys.argv[2]
d = json.load(open(path))
rows = d.get("results") or []
print(f"# ClawHub: '{q}' — {len(rows)} result(s)\n")
if not rows:
    print("_Nothing found. Try a synonym or a single word — search is embedding-based but misses on short slugs._")
    sys.exit()
print("| Skill | Owner | Source | ⬇ downloads | installs/60d | ⭐ | Flags | Install |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    st = ((r.get("native") or {}).get("skill") or {}).get("stats") or {}
    tr = r.get("trust") or {}
    sc = tr.get("upstreamScanners") or {}
    flags = []
    if r.get("official"):
        flags.append("official")
    if ((r.get("native") or {}).get("skill") or {}).get("isSuspicious"):
        flags.append("⚠ suspicious")
    if tr.get("clawHubVerdict"):
        flags.append(f"scan:{tr['clawHubVerdict']}")
    for name, v in sc.items():
        flags.append(f"{name}:{(v or {}).get('status', '?')}")
    src = r.get("source") or "clawhub"
    ref = (r.get("install") or {}).get("reference") or f"{r.get('ownerHandle')}/{r.get('slug')}"
    if src == "skills-sh":
        inst = "clawhub install " + (ref if ref.startswith("skills-sh:") else f"skills-sh:{ref}")
    else:
        inst = f"clawhub install @{ref}"
    life = (r.get("sourceIdentity") or {}).get("lifetimeInstalls")
    i60 = (r.get("metrics") or {}).get("rolling60DayInstalls")
    print("| `{}` | @{} | {} | {} | {} | {} | {} | `{}` |".format(
        r.get("slug"), r.get("ownerHandle"), src,
        r.get("downloads") or "n/a",
        i60 if i60 is not None else (f"{life} lifetime" if life else "n/a"),
        st.get("stars", "n/a"), ", ".join(flags) or "—", inst))
print("\n> Source `skills-sh` = a mirror of the skills.sh registry (Layer 2) — dedupe when merging.")
print("> Candidate details: `clawhub.sh judge @owner/slug`; skill body: `clawhub.sh read @owner/slug`.")
PY
  else
    echo "# ClawHub: '$Q' — API unavailable (rate limit?), falling back to the CLI" >&2
    "${CLI[@]}" search "$Q" --limit "$LIM"
  fi
  ;;

judge)
  [ $# -eq 0 ] && { echo "usage: clawhub.sh judge @owner/slug [...]" >&2; exit 1; }
  echo "| Skill | Owner | ⬇ downloads | installs | ⭐ | Versions | Updated | ClawHub scan | Files |"
  echo "|---|---|---|---|---|---|---|---|---|"
  TMPJ="$(mktemp)"; trap 'rm -f "$TMPJ"' EXIT
  for S in "$@"; do
    N="$(norm "$S")"
    "${CLI[@]}" inspect "@$N" --files --json 2>/dev/null > "$TMPJ"
    SLUG="$N" python3 -c '
import json, os, sys, datetime
slug = os.environ["SLUG"]
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print(f"| `{slug}` | ? | — | — | — | — | — | not found / API error | — |"); sys.exit()
sk = d.get("skill") or {}
st = sk.get("stats") or {}
ver = d.get("version") or d.get("latestVersion") or {}
sec = ver.get("security") or {}
upd = sk.get("updatedAt")
upd = datetime.datetime.fromtimestamp(upd/1000, datetime.timezone.utc).strftime("%Y-%m-%d") if upd else "n/a"
verdict = sec.get("status") or "not scanned"
if sec.get("hasWarnings"):
    verdict += " + warnings"
vt = ((sec.get("scanners") or {}).get("vt") or {}).get("status")
if vt and vt != sec.get("status"):
    verdict += f" (VirusTotal: {vt})"
files = ver.get("files") or []
print("| `{}` | @{} | {} | {} | {} | {} | {} | {} | {} |".format(
    sk.get("slug", slug), (d.get("owner") or {}).get("handle", "?"),
    st.get("downloads", "n/a"), st.get("installs", "n/a"), st.get("stars", "n/a"),
    st.get("versions", "n/a"), upd, verdict,
    ", ".join(f.get("path", "?") for f in files[:6]) + (" …" if len(files) > 6 else "") or "n/a"))
' "$TMPJ"
  done
  echo
  echo "> Tiering: official / large owner + scan clean with no warnings + updated <6 months → T2;"
  echo "> warnings / VirusTotal suspicious / 0 installs / ships scripts → T3-T4 →"
  echo "> read every file with \`clawhub.sh read @owner/slug <file>\` before installing."
  ;;

read)
  S="${1:-}"; F="${2:-}"
  [ -z "$S" ] && { echo "usage: clawhub.sh read @owner/slug [file]" >&2; exit 1; }
  N="$(norm "$S")"
  if [ -z "$F" ]; then
    "${CLI[@]}" inspect "@$N" --files
    echo
    echo "> Skill body: clawhub.sh read @$N SKILL.md (do the same for every script listed)."
  else
    "${CLI[@]}" inspect "@$N" --file "$F"
  fi
  ;;

*)
  echo "usage: clawhub.sh {search \"<q>\" [limit] | judge @owner/slug ... | read @owner/slug [file]}" >&2
  exit 1
  ;;
esac
