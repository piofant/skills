#!/usr/bin/env bash
# self-brief.sh — what the user ALREADY has installed: inventory + overlap with the query.
# Run this BEFORE fanning out to registries: half the finds are usually already covered.
# Usage:
#   self-brief.sh "<query>"   — show only overlaps with the query (main mode)
#   self-brief.sh --all       — full inventory, grouped by directory
set -uo pipefail

QUERY="${1:-}"
[ "$QUERY" = "--all" ] && QUERY=""

QUERY="$QUERY" python3 <<'PY'
import os, re, sys
from pathlib import Path

query = os.environ.get("QUERY", "").strip().lower()
terms = [t for t in query.split() if len(t) > 2]

roots = [("global", Path.home() / ".claude" / "skills")]
cwd = Path.cwd()
for rel in (".claude/skills", ".agents/skills"):
    p = cwd / rel
    if p.is_dir():
        roots.append((f"project:{rel}", p))

def read_meta(skill_md):
    try:
        txt = skill_md.read_text(encoding="utf-8", errors="replace")[:4000]
    except Exception:
        return None, ""
    m = re.match(r"\A---\n(.*?)\n---", txt, re.DOTALL)
    fm = m.group(1) if m else ""
    name = None
    nm = re.search(r"^name:\s*(.+)$", fm, re.M)
    if nm:
        name = nm.group(1).strip().strip("\"'")
    desc = ""
    dm = re.search(r"^description:\s*(.*)$", fm, re.M)
    if dm:
        first = dm.group(1).strip()
        if first in (">", "|", ">-", "|-", ""):
            lines = []
            for ln in fm[dm.end():].split("\n"):
                if ln.startswith(" ") or ln.strip() == "":
                    lines.append(ln.strip())
                else:
                    break
            desc = " ".join(x for x in lines if x)
        else:
            desc = first.strip("\"'")
    return name, desc

inventory = []
for label, root in roots:
    if not root.is_dir():
        continue
    for d in sorted(root.iterdir()):
        sm = d / "SKILL.md"
        if sm.is_file():
            name, desc = read_meta(sm)
            inventory.append((label, name or d.name, desc))

by_root = {}
for label, name, desc in inventory:
    by_root.setdefault(label, []).append((name, desc))

counts = ", ".join(f"{k}: {len(v)}" for k, v in by_root.items())
print(f"# Already installed: {len(inventory)} skills ({counts})\n")

if not terms:
    for label, items in by_root.items():
        print(f"## {label}")
        for name, desc in items:
            short = (desc[:100] + "…") if len(desc) > 100 else desc
            print(f"- `{name}` — {short}")
        print()
    sys.exit(0)

def score(name, desc):
    s = 0
    for t in terms:
        if t in name.lower():
            s += 3
        elif t in desc.lower():
            s += 1
    return s

hits = sorted([h for h in ((score(n, d), l, n, d) for l, n, d in inventory) if h[0] > 0],
              key=lambda x: -x[0])[:12]

if not hits:
    print(f"## Nothing installed overlaps '{os.environ['QUERY']}' — the topic is uncovered, go search outside.")
    sys.exit(0)

print(f"## Already covering '{os.environ['QUERY']}' — check before installing anything new ({len(hits)}):\n")
for s, lbl, name, desc in hits:
    mark = "STRONG" if s >= 3 else "partial"
    short = (desc[:130] + "…") if len(desc) > 130 else desc
    print(f"- [{mark}] `{name}` ({lbl}) — {short}")

print("\n> For every registry candidate ask: does it do something none of these already do?")
print("> If not, it belongs in the table as 'already covered: <skill>', not in the top picks.")
PY
