#!/usr/bin/env bash
# neuraldeep.sh — search the neuraldeep.ru/skills catalog (Russian-service skills and MCPs).
# The catalog has no public API: fetch the page and pull the JSON embedded in it.
# Usage: neuraldeep.sh "<query>" [--type skill|mcp]
set -uo pipefail

QUERY="${1:-}"
shift 2>/dev/null || true
TYPE_FILTER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --type) TYPE_FILTER="${2:-}"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$QUERY" ]; then
  echo "usage: neuraldeep.sh \"<query>\" [--type skill|mcp]" >&2
  exit 1
fi

CACHE="${TMPDIR:-/tmp}/neuraldeep_skills.html"
# cache for an hour — the catalog is small and changes rarely
if [ ! -s "$CACHE" ] || [ -n "$(find "$CACHE" -mmin +60 2>/dev/null)" ]; then
  curl -s --max-time 25 "https://neuraldeep.ru/skills" -o "$CACHE" || {
    echo "ERR: could not reach neuraldeep.ru (network/geo-block?)" >&2; exit 2; }
fi

QUERY="$QUERY" TYPE_FILTER="$TYPE_FILTER" CACHE="$CACHE" python3 <<'PY'
import json, os, re, sys

html = open(os.environ["CACHE"], encoding="utf-8", errors="replace").read()
query = os.environ["QUERY"].lower()
type_filter = os.environ.get("TYPE_FILTER", "").strip().lower()

# The catalog ships inside the Next.js RSC payload: self.__next_f.push([1,"...json..."])
decoded = []
for m in re.finditer(r'self\.__next_f\.push\(', html):
    start = html.find('[', m.end() - 1)
    depth, i, in_str, esc = 0, start, False, False
    while i < len(html):
        c = html[i]
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0: break
        i += 1
    try:
        chunk = json.loads(html[start:i + 1])
    except Exception:
        continue
    for part in chunk:
        if isinstance(part, str):
            decoded.append(part)

blob = "".join(decoded)
pos = blob.find('"initialSkills":')
if pos == -1:
    sys.exit("ERR: catalog not found in the page — neuraldeep's markup probably changed")

start = blob.find('[', pos)
depth, i, in_str, esc = 0, start, False, False
while i < len(blob):
    c = blob[i]
    if in_str:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': in_str = False
    else:
        if c == '"': in_str = True
        elif c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0: break
    i += 1

items = json.loads(blob[start:i + 1])
terms = [t for t in query.split() if t]

def haystack(it):
    return " ".join([
        str(it.get("name", "")), str(it.get("description", "")),
        str(it.get("category", "")), " ".join(it.get("tags") or []),
        str(it.get("owner", "")), str(it.get("repo", "")),
    ]).lower()

hits = [it for it in items
        if (not type_filter or str(it.get("type", "")).lower() == type_filter)
        and all(t in haystack(it) for t in terms)]
hits.sort(key=lambda it: -(it.get("installs") or 0))

print(f"# neuraldeep.ru — '{os.environ['QUERY']}' ({len(items)} entries in catalog, {len(hits)} matched)\n")
if not hits:
    print("No matches. Try a synonym or a single word — substring matching, no semantics.")
    print("Descriptions are mostly Russian: try both the English and Russian spelling.")
    sys.exit(0)

print("| Type | Skill | What it does | Installs | ⭐ GH | Category | Install |")
print("|---|---|---|---|---|---|---|")
for it in hits[:25]:
    desc = (it.get("description") or "").replace("\n", " ").replace("|", "/")
    if len(desc) > 90:
        desc = desc[:90] + "…"
    slug = f"{it.get('owner')}/{it.get('repo')}"
    cmd = f"`npx skillsbd add {slug}`" if it.get("type") == "skill" else "MCP — see the card"
    print(f"| {it.get('type','?')} | `{it.get('name','?')}` | {desc} "
          f"| {it.get('installs',0)} | {it.get('githubStars') or '-'} "
          f"| {it.get('category','-')} | {cmd} |")
print("\n> Every skill here is just a GitHub repo: run judge.sh and the security scan "
      "as you would for any external skill.")
PY
