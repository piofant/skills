---
name: md-to-pdf-deck
description: Convert a markdown file into a polished PDF — either a presentation deck (A4 landscape, slide-per-heading, cover) or a single-page longread (continuous scroll, no pagination). Both share a dark GitHub theme, real dialog blockquotes, and rendered mermaid diagrams. Use deck mode for weekly syncs, board updates, product case studies. Use longread mode for reading-style docs (guides, memos, reference material) where the reader scrolls top-to-bottom like a web page.
---

# Markdown → Polished PDF

Pipeline: **Markdown → (pre-rendered mermaid SVG + GitHub alerts + cover/longread pre-processing) → pandoc HTML → WeasyPrint PDF**.

Two output modes share the same dark GitHub theme and formatting primitives:

| Mode | Shape | Use for |
|---|---|---|
| `--layout longread` | **Single continuous tall page**, no pagination, auto-fit height, portrait width 210mm | Product guides, intros, memos, reference docs — anything read top-to-bottom |
| `--layout deck` (default) | A4 landscape, slide-per-heading, centered cover | Weekly syncs, pitches, board updates, case studies |

Shared features (both modes):
- Dark GitHub palette (`#0d1117` background, `#58a6ff` headings)
- Colored emoji via Noto Color Emoji (without keycap-digit hijacking)
- Dialog blockquotes: blue left-border + golden italics for quoted speech
- GitHub alerts (`> [!NOTE]`, `> [!WARNING]`, etc.) as colored callouts
- Mermaid diagrams pre-rendered to SVG with node labels intact
- Tables with striped rows, code blocks with JetBrains Mono

## Quick recipe — longread intro doc

For a shareable intro doc (a functional guide, onboarding memo, product primer):

```bash
cd /path/to/skill/scripts
python3 build.py /path/to/your-doc.md /path/to/output.pdf \
  "Title"                          \
  "Subtitle · audience · tagline" \
  "Author · Date"                  \
  --layout longread
```

Source markdown should open with a `<div align="center">` block containing `# Title` and `### Subtitle` — in longread mode it renders inline as the document header (not a slide cover). The rest of the doc flows naturally with `#`/`##` headings, tables, blockquotes.

The skill auto-fits the page height via two-pass rendering: the first pass measures actual content extent using WeasyPrint's box-tree API, the second re-renders with `210mm × Nmm` where N matches content + 22mm bottom margin. No wasted empty space at the bottom.

## When to use

- User asks to "export as PDF" a markdown weekly sync, update, deck, case study, guide, or intro doc
- User says "make it look like a preza" / "нормальный PDF" / "такой же длинный как в прошлый раз"
- User wants to share a GitHub markdown document externally where readers may not know GitHub

**Do NOT use for:** short notes, single-page readmes, or documents that have no section structure. For those, GitHub's native markdown view is better.

## When NOT to use

- User wants a truly interactive slide deck (use reveal-md or marp instead)
- Document has heavy client-side interactivity assumptions
- User needs pixel-perfect corporate branding (commission a designer)

## The pipeline — why these choices

| Choice | Reason |
|--------|--------|
| **WeasyPrint, not Chrome headless** | Chrome injects print headers (`date, file://...`, page numbers) that are hard to disable reliably. WeasyPrint is silent. |
| **pandoc HTML, not direct markdown** | pandoc handles pipe tables, task lists, fenced code, and auto-IDs consistently. |
| **Mermaid pre-rendered to SVG via mmdc** | Neither pandoc nor WeasyPrint render mermaid. Pre-render to SVG and embed as `<img>`. Set `htmlLabels: false` or WeasyPrint can't render node labels (it doesn't support `<foreignObject>`). |
| **Emoji font scoped OUT of body stack** | Noto Color Emoji has keycap glyphs (`0️⃣ 1️⃣`) that hijack digit fallback in WeasyPrint — "2026" renders as "2 0 2 6". Keep emoji font resolved only via system fontconfig for emoji codepoints, not via CSS body stack. |
| **Pandoc default body CSS overridden** | Pandoc adds `body { max-width: 36em }` which squashes content into a narrow column. Must override with `!important`. |
| **Cover slide built from script, not markdown** | The first `# H1 + ### H3` block gets wrapped in `<div class="cover">` with subtitle/tagline/author classes. Lets us keep the markdown source clean. |

## Quick start — deck mode

For a presentation-style PDF (A4 landscape, slide-per-H2):

```bash
cd /path/to/skill/scripts
python3 build.py /path/to/deck.md /path/to/weekly-sync.pdf \
  "Project Weekly Sync" \
  "Что неделя значит для продукта" \
  "Author · 2026-04-23"
```

Default mode. Outputs A4 landscape, dark theme, one slide per `## H2`.

## Quick start — longread mode

For a guide / memo / intro doc (single tall page, auto-fit height):

```bash
python3 build.py /path/to/guide.md /path/to/guide.pdf \
  "Люмен" \
  "Telegram-бот, который ведёт себя как друг" \
  "Author · 2026-04-23" \
  --layout longread
```

Outputs a single-page PDF (portrait width 210mm, height auto-matched to content + bottom margin). Reader scrolls top-to-bottom like a web page.

## Install dependencies

### macOS (recommended one-liner)

```bash
bash scripts/setup-macos.sh
```

That script is idempotent and handles two macOS gotchas the manual install used to fall over:

1. **pyexpat ABI mismatch on Tahoe+.** Brew Python 3.13/3.14's bundled `pyexpat.so` links against `/usr/lib/libexpat.1.dylib` which lacks newer symbols. Without the fix, every SVG render fails with `Symbol not found: _XML_SetAllocTrackerActivationThreshold`. The script installs brew `expat` and creates a venv that `build.py` later runs under with `DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib` injected automatically.
2. **macOS only ships specialized Noto fonts** (Tamil, Myanmar, Yi…) but not the core `Noto Sans` / `Inter` / `Noto Color Emoji` that the skill's font stack references. Without them, Cyrillic text falls back per-character and renders with grotesque letter-spacing. The script installs the three brew casks.

After the first run, `build.py` auto-detects the sibling `.venv` and re-execs under it. No env vars at call time, no need to remember the flag.

### Linux (Debian/Ubuntu)

```bash
apt install -y pandoc weasyprint imagemagick \
  fonts-inter fonts-noto-color-emoji fonts-noto fonts-noto-cjk

npm install -g @mermaid-js/mermaid-cli
```

Running as root? Mermaid CLI (Puppeteer) needs sandbox disabled — `puppeteer-config.json` in `scripts/` handles that.

## Expected markdown structure

```markdown
<div align="center">

# 🌙 Title With Emoji

### Subtitle or date range

</div>

---

## First slide heading

Content for slide 1…

> 👤 *«user message»*
> 🌙 *«bot response»*

> [!IMPORTANT]
> callout block

---

## Second slide heading

| col | col |
|-----|-----|
| ... | ... |

` ``mermaid
flowchart LR
    A --> B
` ``
```

Every `## H2` becomes a new page. Every `---` between sections is harmless (they're hidden via CSS — page breaks do the work). The first block up to the first `## H2` becomes the cover.

## Script arguments

```
python3 build.py <source.md> <output.pdf> <title> [tagline] [author] [--layout deck|longread] [--break h1|h2]
```

- `source.md` — input markdown (required)
- `output.pdf` — output PDF path (required)
- `title` — slide title shown as giant H1 on cover (required; ignored in longread mode)
- `tagline` — italic line below subtitle (optional; ignored in longread mode)
- `author` — small byline at bottom of cover (optional; ignored in longread mode)
- `--layout` — `deck` (default, A4 landscape, slide-per-heading) or `longread` (single continuous page, no pagination)
- `--break` — slide-break level (deck only): `h2` (default) breaks on every `##`, `h1` breaks on every `#`

The subtitle under the title is auto-extracted from the first `### ` heading in the source.

### Choosing a layout

**`--layout deck` (default):** A4 landscape, centered cover slide, every heading = new slide. For presentations — weekly syncs, pitches, board updates, demos.

**`--layout longread`:** one tall page, no breaks, portrait width (210mm), smaller reading-density type. The `<div align="center">` intro block from the markdown source becomes the doc header (inline, not a slide). For reading-style docs — guides, memos, intros, reference material.

#### How longread auto-fit works (two-pass render)

Naive `@page { size: 210mm 5000mm }` leaves a lot of empty dark background below the content when the doc is shorter. The skill fixes this via two-pass rendering:

1. First pass: render into the Python API with 5000mm sentinel height
2. Walk the box tree (skipping `PageBox` and `MarginBox`), find the deepest bottom Y of actual content
3. Convert CSS px → mm, add 22mm bottom margin
4. Rewrite `override.css` with the fitted height and re-render

Result: the final PDF is exactly as tall as it needs to be — no wasted space, and the reader can scroll without hitting a long empty tail.

### Choosing a break level (deck only)

**`--break h2` (default):** every `##` heading = new slide. Good for sync-style decks where each sub-topic is a self-contained slide with rich content (table, diagram, 5+ bullets). Bad when source has many thin `##` sub-sections under a `#` chapter — produces mostly-empty slides.

**`--break h1`:** every `#` heading = new slide; `##` becomes an in-slide section separator (like a bold sub-header). Good for documentation/guides structured as chapters, where one chapter = one dense slide with multiple sub-sections, tables, and bullets.

Rule of thumb: if your thinnest `##` section is < 3 lines of content, use `--break h1` and consolidate. Or switch to `--layout longread` entirely — if the doc reads top-to-bottom anyway, pagination is fighting the content.

## Known rough edges

- WeasyPrint has limited flexbox support — use block layout for covers
- WeasyPrint doesn't support `@font-face unicode-range` — scope emoji via font-stack order, not `@font-face`
- Mermaid CLI requires Puppeteer, which requires Chromium — heavy dep for a side utility
- Long tables that don't fit on one page will split awkwardly; add `break-inside: avoid` selectively if needed

## Files in this skill

- `scripts/build.py` — the pipeline (single-pass for deck, two-pass auto-fit for longread)
- `scripts/preza.css` — dark base theme (both modes)
- `scripts/override.css` — generated per run; empty in deck/h2, h1-break rules in deck/h1, longread-mode overrides in longread (portrait + fitted page height)
- `scripts/head.html` — pandoc `<head>` injection linking preza.css + override.css
- `scripts/mermaid-config.json` — mermaid dark theme (with `htmlLabels: false`!)
- `scripts/puppeteer-config.json` — `--no-sandbox` for root
- `references/example-weekly-sync.md` — minimal working example
- `assets/preview-cover.png` — sample output

## Reference output

`assets/preview-cover.png`, `preview-slide.png` and `preview-mermaid.png` are
real output of this pipeline, built from `references/example-weekly-sync.md`.
Rebuild them any time with the deck recipe above — good for checking that a
theme or CSS change did not break the layout.
