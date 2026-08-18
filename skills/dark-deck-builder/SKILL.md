---
name: dark-deck-builder
description: Build dark, minimal, "active-headline" stakeholder & methodology decks — flat-black canvas, one purple accent, one-idea-per-slide, schemes/cards that carry the data, and an iterative build→render→read→simplify loop. Built programmatically with pptxgenjs (Node) and verified visually (PDF→PNG). Use when the user wants a clean dark presentation for stakeholders/teammates, a methodology or product walkthrough, an internal review deck, or says "сделай презу/дек в тёмном стиле", "тёмный минимал-дек", "активные заголовки", "stakeholder deck", "методологический дек". NOT for light McKinsey decks (see mckinsey-style-visualization), markdown→PDF longreads (see md-to-pdf-deck), or pure schemes (see scheme-dark).
---

# Dark Deck Builder

Build a **dark, minimal, takeaway-first** slide deck programmatically, then refine it by *looking at it* — render every change to PNG, read it, cut what's overloaded, repeat. This is how the deck stays clean instead of drifting into a wall of bullets.

The aesthetic: flat black background, white/grey text, one purple accent, big assertive headlines, lots of air. Diagrams and cards do the explaining; bullets only add the *insight*, never restate the picture.

---

## 1. Core principles (the whole philosophy in 6 lines)

1. **One idea per slide.** If a slide needs two breaths to explain, split it.
2. **Active headlines.** The title states the *conclusion*, not the topic. (Section 2.)
3. **The visual carries the data.** A chart already shows "tool-use is the weak spot" — don't repeat the numbers in bullets next to it.
4. **Bullets earn their place.** Each bullet adds something the diagram can't. 2–3 max. If it restates the headline or the chart, delete it.
5. **Whitespace is a feature.** Half-empty slides read as confident. Crowded slides read as anxious.
6. **No AI tells.** Muted accent bars (not neon), no rule-of-three slogans, no "не только… но и", no echo-footnotes that repeat the title.

> Reflex when you look at a rendered slide and feel "perегружен / busy": the fix is almost always **delete**, not rearrange. Drop the bullets that echo the visual, drop the footnote that repeats the headline, merge two bullets that say the same thing.

---

## 2. Active headlines (the single highest-leverage habit)

A headline should be a **full sentence that delivers the takeaway**, so a reader who only reads titles still gets the argument.

| Topic title (weak) | Active headline (strong) |
|---|---|
| "Метрика качества" | "Среднее N прячет M% провалов — поэтому смотрим на долю прошедших" |
| "Результаты бенчмарка" | "Прогнали 16 вариантов и выбрали по цифрам: качество выше, задержка меньше, цена та же" |
| "Архитектура" | "Качество определяет пара «модель + обвязка», а не только модель" |
| "Следующие шаги" | "Первые задачи — от главного долга до расширения" |

Rules:
- Put the **number / verdict in the title** when there is one.
- One line, two max. If it wraps to three, cut words.
- Lowercase after the first word; «ёлочки» for quotes.
- Pair a grey "topic" line with a white "takeaway" line for section/divider slides (two-line header).

Read the title row of the whole deck top to bottom — it should narrate the story by itself.

---

## 3. Visual system (theme)

Black canvas, one accent, muted everything else. Palette (hex):

```
bg      #000000   white   #FFFFFF   body    #D6D6D6   eyebrow #9A9A9A   faint #6E6E6E
card    #15161C   line    #2C2E38   hl(band)#2B3450   accent(purple) #9B87F5
blue #1E73D6   amber #D9920E   green #3FA56B   red #C44133   pink #D98FBE
```

- **Font:** Inter (or Arial as a safe PPTX fallback), Courier New for mono/IDs.
- **Layout:** 16:9 widescreen (pptxgenjs `LAYOUT_WIDE` = 13.333 × 7.5 in). Side margin ≈ 0.7 in.
- **Eyebrow** (top-left, tiny, letter-spaced, purple): section path like "Часть 1 · …".
- **Accent bars / coloured headers must be MUTED** — set fill `transparency: ~55–60`. Full-saturation rainbow stripes are the #1 "AI-generated" tell. Keep solid colour only for *semantic* status (PASS green / FAIL red badges).
- **Pill tags** (solid colour, white text) for category rows at the bottom.
- **Cards:** `#15161C` fill, `#2C2E38` border, ~16 px radius. Tinted dark cards for good/bad (`#0E1A12` green-ish / `#1A0E0E` red-ish).

This matches the companion `scheme-dark` skill — use it to render any standalone diagram as a PNG.

---

## 4. Slide-pattern library

Reach for these shapes; don't invent layout per slide.

- **Cover** — eyebrow, big two-line title (active), one-line subtitle, thin rule, author/date. Optional image on the right: on a **black-background** PNG it blends seamlessly into the canvas (great for a glow/mascot).
- **Agenda** — numbered full-width cards (big number + title + one-line gloss).
- **Section / transition divider** — near-empty slide: grey line ("Научились измерять.") + white line ("Теперь — как повышать →") + thin subtitle. Put one between every Part to keep momentum.
- **3-card overview** — three roles/pillars, one short line each; optionally highlight the "we're here" card (full accent bar + accent border).
- **Sequential trace / flow** — numbered steps top-to-bottom with ↓ arrows, label + short content per row. Best for "how X works end to end". Far clearer than parallel cards for a process. (Helper `traceFlow` in the template.)
- **Stat cards** — 2–4 big-number cards. Keep only the numbers that *prove the headline*; drop secondary metrics.
- **Comparison columns** — "Переносим / Адаптируем / Не переносим", "Сейчас / Дальше", etc.
- **Ladder / levers** — numbered rows with a right-aligned cost/priority pill.
- **Verdict table** — condition → PASS/FAIL badges (gate logic).
- **Worked example, two ways** — a PASS trace and a FAIL trace of the same pipeline; the FAIL one carries the lesson.
- **Image + insight** — chart/figure on one side, 2 qualitative bullets on the other (never restate the chart's numbers).
- **Highlight band** — full-width tinted band for the one sentence that matters.

---

## 5. Schemes / diagrams

Two reliable ways to get crisp Russian text in diagrams (browsers render Cyrillic perfectly; many chart libs don't):

1. **In-deck sequential flow** — the `traceFlow` helper draws numbered dark cards + ↓ arrows natively in pptx. Use for pipelines/traces.
2. **`scheme-dark` skill** — write an HTML fragment with the theme classes, render via headless Chrome → PNG, drop the PNG into a slide with `imgContain` (no white card frame — the PNG's black bg melts into the slide).

For data charts use dark-theme matplotlib (black face, light text) so they sit on the black canvas. A light/white chart on a black slide is jarring — either dark-theme it or frame it on a small white card (`imageCard`).

---

## 6. Narrative structure

A dependable arc for a methodology / product-review deck:

1. **Cover → Agenda** (what we'll cover, numbered).
2. **Framing slide early** — situate today's topic in the bigger picture (e.g. "metrics come in 3 kinds; today = this one").
3. **Part 1 — concepts → our concrete version.** Teach the building blocks generically, then a "теория → практика" divider, then the same blocks *as we built them*. (Watch for over-repetition — see §8.)
4. **Part 2 — how we act on it** (levers, automation, etc.), cheapest-first.
5. **Transition divider** between parts ("Научились X. Теперь — Y →").
6. **Part 3 — roadmap.** What transfers, what adapts, honest gaps, **first tasks (P0/P1/P2) and who owns each.** End on owners + a warm closer.

Each Part gets a transition divider in front of it. Honest "what's NOT closed yet" beats overclaiming — but phrase it in plain language, not jargon.

---

## 7. Tech: pptxgenjs build pipeline

Programmatic decks beat hand-clicking because you iterate in seconds and diff in git.

```
build.js (pptxgenjs)  →  node build.js  →  deck.pptx
deck.pptx  →  soffice --headless --convert-to pdf deck.pptx  →  deck.pdf
deck.pdf   →  pdftoppm -png -r 80 deck.pdf pg  →  pg-NN.png   →  READ the PNGs
```

- Use `template.js` in this skill folder as the starting skeleton: it has the theme palette + helper functions (`newSlide`, `headline`, `subhead`, `card`, `bullets`, `callout`, `highlightBlock`, `stat`, `imageCard`, `imgContain`, `traceFlow`, `sourceLine`) and a 3-slide demo.
- Keep the deck in a throwaway git repo so you can **keep/discard** each iteration (`git commit` good states, `git checkout` to roll back a bad edit).
- **Always verify visually.** After every build, render the changed pages to PNG and actually look. Corner page numbers: file `pg-NN.png` shows the printed number `NN-1` (cover has no number) — re-check after inserting/removing slides shifts everything.
- Image gotcha: very large PNGs (>~2000 px on a side) can fail to load into a viewer — downscale a preview with `sips -Z 1200 in.png --out prev.png` before reading.

Helper conventions worth keeping:
- `headline(s, text)` — the active title block.
- `card(s, x, y, w, h, fill, line)` — the base dark rectangle everything sits on.
- `imgContain(s, file, box, ar)` — place a dark-bg scheme PNG with no frame (melts into canvas).
- `traceFlow(s, steps, y0)` — the numbered sequential-flow pattern.
- `sourceLine(s, text)` — tiny grey footnote; **delete it if it just repeats the headline.**

---

## 8. Iterative review reflex (the loop that keeps it clean)

After building, walk the deck and for each slide ask:
- Does any bullet **restate** the diagram/chart/card next to it? → delete it.
- Is the footnote echoing the title? → delete it.
- Two bullets saying the same thing? → merge.
- More than ~3 bullets? → it's two slides, or half of them are noise.
- Coloured bar look neon? → add `transparency`.
- Same concept explained 3×+ across the deck (e.g. an overview slide **and** a concept slide **and** an "ours" slide for the same thing)? → that's the structure's biggest redundancy. Flag it; offer to drop the weakest layer.

Cutting a slide is cheap and almost always right. Decks die from accretion.

---

## 9. De-AI / humanize pass — ship a second `*-humanize` deck

Decks read crisp when headlines are punchy, but punchy reads *AI-generated* to some audiences. Keep **both**: the original (slogan style) and a humanized copy. Don't edit text in place — fork the build script so both versions stay reproducible.

**Recipe (the build is just code, so fork it):**

```bash
# 1. fork the build, point it at a new output file
cp build.js build-humanize.js
sed -i '' 's/deck\.pptx/deck-humanize.pptx/' build-humanize.js   # macOS sed
```

```python
# 2. apply humanizer-ru rules to build-humanize.js ONLY (strings live in the JS,
#    so a global dash swap is safe — there are no em-dashes in JS syntax)
import re
s = open("build-humanize.js", encoding="utf-8").read()

# 2a. targeted rewrites FIRST (while em-dashes still present), e.g. banned parallelisms:
fixes = [
  ("докручиваем не только промпты, но и модель", "докручиваем и промпты, и модель"),  # «не только…но и» is banned
  ("X — не A, а B",                              "X — это B, а не A"),                  # reword «не A, а B» slogans
  ('s.addText(c.e + "  " + c.t,',                's.addText(c.t,'),                     # drop decorative emoji from card titles
  ('"✅  СИГНАЛЫ"',                              '"СИГНАЛЫ"'),                          # strip ✓/✗ emoji from headers
]
for a, b in fixes: s = s.replace(a, b)

# 2b. global dash normalization (em/en/minus → hyphen)
for ch in ("—", "–", "−"): s = s.replace(ch, "-")

open("build-humanize.js", "w", encoding="utf-8").write(s)
```

```bash
# 3. build the humanized deck separately
node build-humanize.js && soffice --headless --convert-to pdf deck-humanize.pptx
```

**What the humanizer-ru pass enforces** (see the `humanizer-ru` skill for the full 21 patterns):
- `—` (long dash) → `-` everywhere.
- kill "не только X, но и Y" / "не просто X, а Y" / "это не просто…" (negative parallelisms).
- drop decorative emoji from headings/lists; keep only *semantic* ✓/✗ if they encode pass/fail.
- split "intro-word: list" colons into two sentences.
- canzelyarit out: «является» → «это/важно», passive → active, verb-nouns → verbs.
- plain spoken phrasing; vary sentence length; one opinion is fine.

**Verify:** after building, `grep -c "—" build-humanize.js` should be `0`, then render and read a couple of slides — the meaning must survive, only the AI-tells go. Ship `deck.pptx`/`.pdf` **and** `deck-humanize.pptx`/`.pdf` as two files.

---

## 10. Anti-patterns (don't)

- Topic-label headlines ("Метрика", "Архитектура").
- Bullets that narrate the diagram beside them.
- Full-saturation coloured stripes on every card (the rainbow tell).
- Rule-of-three slogans and triads for fake completeness.
- Footnotes that restate the title.
- A light/white chart dumped on a black slide.
- 5+ bullets. A "summary" slide that re-summarizes a summary.
- Shipping without rendering and *looking*.

---

## Confidentiality note

This skill is the **method only**. When the source deck is internal/under NDA, keep real figures, customer/case identifiers, internal infra names, model/prompt internals, and proprietary results **out** of the deck files you commit anywhere public — use generic placeholders (as in `template.js`). The reusable part is the style and pipeline, not the data.
