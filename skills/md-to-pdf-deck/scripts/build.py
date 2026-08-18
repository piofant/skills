"""v6: mermaid + alerts + cover slide + pandoc HTML + WeasyPrint PDF.

Two layouts:
  --layout deck (default): A4 landscape, slide-per-heading, cover slide.
  --layout longread: single continuous tall page, no breaks, portrait width.

Deck layout supports two break strategies:
  --break h2 (default): every ## = new slide
  --break h1: every # = new slide; ## becomes in-slide section header

Use longread for reading-style docs (guides, memos). Use deck for
presentations / syncs. Use h1 break for dense decks when source is
structured as chapters (# Chapter) with sub-sections (## Sub).

macOS bootstrap: on import we self-heal:
  1) If a sibling .venv exists, re-exec under it (so weasyprint import works
     even when system python is wrong).
  2) Inject DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib for pyexpat on
     Tahoe+ where the bundled libexpat misses newer symbols.
Run scripts/setup-macos.sh once to provision the venv + brew deps + fonts.
"""
import os
import sys
import platform
import pathlib


def _bootstrap_macos():
    """On macOS: re-exec under sibling .venv with DYLD path fixed for expat."""
    if platform.system() != "Darwin":
        return
    if os.environ.get("_MD_TO_PDF_BOOTSTRAPPED") == "1":
        return

    here = pathlib.Path(__file__).resolve().parent
    venv_py = here.parent / ".venv" / "bin" / "python3"
    expat_lib = pathlib.Path("/opt/homebrew/opt/expat/lib")

    env = os.environ.copy()
    env["_MD_TO_PDF_BOOTSTRAPPED"] = "1"
    if expat_lib.exists():
        existing = env.get("DYLD_LIBRARY_PATH", "")
        env["DYLD_LIBRARY_PATH"] = (
            f"{expat_lib}:{existing}" if existing else str(expat_lib)
        )

    target_py = str(venv_py) if venv_py.exists() else sys.executable
    if target_py == sys.executable and "DYLD_LIBRARY_PATH" not in os.environ:
        # Just set DYLD and continue in-process (no need to re-exec)
        os.environ.update(env)
        return
    os.execve(target_py, [target_py, *sys.argv], env)


_bootstrap_macos()

import argparse
import re
import subprocess
import hashlib

parser = argparse.ArgumentParser(description="Markdown → presentation/longread PDF")
parser.add_argument("src", help="source markdown")
parser.add_argument("out", help="output pdf path")
parser.add_argument("title", nargs="?", default="Deck", help="cover title")
parser.add_argument("tagline", nargs="?", default="", help="cover tagline (italic)")
parser.add_argument("author", nargs="?", default="", help="cover author/date byline")
parser.add_argument(
    "--break", dest="break_level", choices=["h1", "h2"], default="h2",
    help="slide-break level (deck layout only): h2=every ## (default), h1=every # (denser slides)",
)
parser.add_argument(
    "--layout", choices=["deck", "longread"], default="deck",
    help="deck=A4 landscape slides (default), longread=single tall page, no pagination",
)
args = parser.parse_args()

src_path = pathlib.Path(args.src)
out_pdf = pathlib.Path(args.out)
title = args.title
tagline = args.tagline
author = args.author
break_level = args.break_level
layout = args.layout

src = src_path.read_text()
work = pathlib.Path(".")
mermaid_idx = 0


def render_mermaid(code: str) -> str:
    """Render a mermaid block to PNG via mmdc. PNG (not SVG) because some
    WeasyPrint+macOS combos fail to parse the SVG node tree (expat ABI mismatch
    on Tahoe). PNG round-trips cleanly through any image loader."""
    global mermaid_idx
    mermaid_idx += 1
    h = hashlib.md5(code.encode()).hexdigest()[:8]
    mmd = work / f"m_{mermaid_idx}_{h}.mmd"
    img = work / f"m_{mermaid_idx}_{h}.png"
    mmd.write_text(code)
    subprocess.run(
        ["mmdc", "-i", str(mmd), "-o", str(img),
         "-t", "dark", "-b", "#0d1117",
         "-c", "mermaid-config.json",
         "-p", "puppeteer-config.json",
         "-w", "1800", "-s", "2"],
        check=True, capture_output=True,
    )
    return f'\n<p class="mermaid-wrap"><img src="./{img.name}" alt="diagram"></p>\n'


src = re.sub(r"```mermaid\n(.*?)\n```", lambda m: render_mermaid(m.group(1)), src, flags=re.DOTALL)


def gh_alert(match):
    kind = match.group(1).lower()
    body = match.group(2)
    cleaned = re.sub(r"^> ?", "", body, flags=re.MULTILINE).rstrip()
    icons = {"note": "📝", "tip": "💡", "important": "❗", "warning": "⚠️", "caution": "🚨"}
    label = {"note": "NOTE", "tip": "TIP", "important": "IMPORTANT", "warning": "WARNING", "caution": "CAUTION"}
    return (
        f'\n<div class="gh-alert gh-alert-{kind}">\n'
        f'<div class="gh-alert-title">{icons.get(kind,"")} {label.get(kind,kind.upper())}</div>\n\n'
        f'{cleaned}\n\n'
        f'</div>\n'
    )


src = re.sub(
    r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n((?:> .*(?:\n|$))+)",
    gh_alert, src, flags=re.MULTILINE,
)

# Strip double HRs
src = re.sub(r"^---\n---\s*$", "---", src, flags=re.MULTILINE)

# ---------- Longread layout: no cover, no pagination ----------
if layout == "longread":
    final = src
    # One tall page, portrait width, no forced breaks anywhere. Tall enough
    # for any reasonable doc; unused space at the bottom is just blank.
    override_css = """
/* --layout longread: single continuous tall page, no slide breaks */
@page {
  size: 210mm 5000mm;
  margin: 18mm 22mm;
  background: #0d1117;
}
h1, h2, h3, h4 { page-break-before: auto !important; break-before: auto !important; }
.cover { display: none !important; }

body { font-size: 10.5pt !important; line-height: 1.6 !important; }
h1 { font-size: 22pt; font-weight: 800; color: #58a6ff; border-bottom: 1.5pt solid #21262d; padding-bottom: 8pt; margin: 28pt 0 14pt; }
h1:first-of-type { margin-top: 6pt; }
h2 { font-size: 15pt; font-weight: 700; color: #79c0ff; border: none; padding: 0; margin: 18pt 0 6pt; }
h3 { font-size: 12.5pt; font-weight: 600; color: #a5d6ff; margin: 12pt 0 4pt; }
h4 { font-size: 11pt; font-weight: 600; color: #c9d1d9; margin: 10pt 0 3pt; }
p, li { font-size: 10.5pt; }
table { font-size: 10pt; margin: 10pt 0; }
th, td { padding: 5pt 10pt; }
blockquote { font-size: 10.5pt; padding: 10pt 16pt; margin: 10pt 0; }
pre, code { font-size: 9.5pt; }

/* Centered doc-intro block (from <div align="center"> in source) */
div[align="center"] h1 { font-size: 30pt; border: none; padding: 0; margin: 0 0 8pt; }
div[align="center"] h3 { font-size: 14pt; color: #8b949e; margin: 0 0 20pt; }
"""
# ---------- Deck layout: cover slide + slide breaks ----------
else:
    # Extract cover content: everything from start up to (but not including) the first ## heading
    # (or first # heading in h1-break mode, since H1s become slide boundaries)
    if break_level == "h1":
        # First # is the cover title, we want the next # after it
        matches = list(re.finditer(r"^# ", src, re.MULTILINE))
        cover_match = matches[1] if len(matches) >= 2 else None
    else:
        cover_match = re.search(r"^## ", src, re.MULTILINE)

    if cover_match:
        cover_src = src[:cover_match.start()]
        rest_src = src[cover_match.start():]
    else:
        cover_src = src
        rest_src = ""

    h1_match = re.search(r"^# (.+)$", cover_src, re.MULTILINE)
    h3_match = re.search(r"^### (.+)$", cover_src, re.MULTILINE)
    cover_title = h1_match.group(1).strip() if h1_match else title
    cover_subtitle = h3_match.group(1).strip() if h3_match else ""

    cover_html = f"""
<div class="cover">
<h1>{cover_title}</h1>
<p class="subtitle">{cover_subtitle}</p>
"""
    if tagline:
        cover_html += f'<p class="tagline">{tagline}</p>\n'
    if author:
        cover_html += f'<p class="author">{author}</p>\n'
    cover_html += "</div>\n\n"

    rest_src = re.sub(r"^---\s*\n", "", rest_src, count=1, flags=re.MULTILINE)
    final = cover_html + rest_src

    if break_level == "h1":
        override_css = """
/* --break h1 mode: # becomes slide boundary, ## stays in-flow */
h2 { page-break-before: auto !important; }
h1 { page-break-before: always !important; font-size: 28pt; border-bottom: 2pt solid #21262d; padding-bottom: 10pt; margin: 0 0 14pt; }
.cover h1 { page-break-before: avoid !important; font-size: 46pt; border: none; padding: 0; margin: 0 0 18pt; }
h2 { font-size: 17pt; color: #79c0ff; border: none; padding: 0; margin: 12pt 0 6pt; font-weight: 600; }
"""
    else:
        override_css = ""

proc = work / "processed.md"
proc.write_text(final)
print(f"✓ {mermaid_idx} mermaid diagrams, layout={layout}, break-level={break_level}")

(work / "override.css").write_text(override_css)

subprocess.run([
    "pandoc", str(proc),
    "-f", "markdown+raw_html+pipe_tables+fenced_code_blocks+task_lists+auto_identifiers+lists_without_preceding_blankline",
    "-t", "html5",
    "-o", "out.html",
    "--standalone",
    "--metadata", f"title={title}",
    "-H", "head.html",
], check=True)
print("✓ HTML generated")

if layout == "longread":
    # Two-pass render: first with tall page to measure content extent,
    # then re-render with page height that matches content + bottom margin.
    # This avoids the "empty dark space at the bottom" when the tall page
    # sentinel height exceeds what the content actually needs.
    from weasyprint import HTML

    def max_content_bottom(box, exclude_types, acc):
        cls = box.__class__.__name__
        if cls not in exclude_types:
            try:
                y_end = float(box.position_y) + float(box.margin_height())
                if y_end > acc[0]:
                    acc[0] = y_end
            except Exception:
                pass
        for ch in getattr(box, "children", ()) or ():
            max_content_bottom(ch, exclude_types, acc)
        return acc[0]

    doc = HTML(filename="out.html", base_url=str(work)).render()
    # Exclude PageBox (covers full page height) and MarginBox (decorative
    # margin boxes) from the measurement — we only care about actual content.
    excluded = {"PageBox", "MarginBox"}
    acc = [0.0]
    for page in doc.pages:
        max_content_bottom(page._page_box, excluded, acc)
    content_bottom_px = acc[0]

    if content_bottom_px > 0:
        # WeasyPrint uses CSS px (1px = 1/96 inch = 0.2646mm).
        content_bottom_mm = content_bottom_px * 25.4 / 96
        # +18mm bottom margin (matches our @page margin), +4mm buffer.
        new_height_mm = int(content_bottom_mm + 18 + 4)
        # Rewrite override.css with fitted page height and re-render.
        fitted = override_css.replace("5000mm", f"{new_height_mm}mm")
        (work / "override.css").write_text(fitted)
        doc = HTML(filename="out.html", base_url=str(work)).render()
        print(f"✓ fitted page height: {new_height_mm}mm (content {content_bottom_mm:.0f}mm)")

    doc.write_pdf(str(out_pdf))
else:
    # Deck layout: prefer Python API too (same DYLD env carries over), so we
    # don't depend on the brew weasyprint CLI which may have a broken python.
    from weasyprint import HTML
    HTML(filename="out.html", base_url=str(work)).write_pdf(str(out_pdf))

print(f"✓ PDF → {out_pdf}")
