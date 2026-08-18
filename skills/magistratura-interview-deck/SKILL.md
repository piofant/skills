---
name: magistratura-interview-deck
description: Build a dark minimalist 10-slide pitch deck for a 3-minute master's-program interview (Russian admission committees - ИТМО, ВШЭ, МФТИ, etc.). Active headlines, real project avatars extracted from your past decks, one idea per slide, flow diagrams and stat cards, never bullet walls. Use when the user is invited to a master's program interview ("конкурс портфолио", собеседование, "питч в магу", защита заявки), needs a 2-3 min self-presentation deck following the structure "учебный → научный → профессиональный бэкграунд + план проекта в магистратуре + почему именно эта программа". Built programmatically with pptxgenjs (Node) and verified visually (PDF→PNG). NOT for diploma defense (see diploma-defense), light McKinsey decks (mckinsey-style-visualization), or general dark stakeholder decks (dark-deck-builder - this skill is the magistratura interview specialization of that one).
---

# Magistratura Interview Deck Builder

A **3-minute self-presentation deck** for a Russian master's-program admission interview, in the dark minimalist style. The hard constraint: the committee asked for 2-3 minutes of self-presentation followed by 7 minutes of Q&A. So the deck must be **scannable in seconds**: active headlines, real photos/avatars of your projects, flow diagrams, stat cards. **No bullet walls.**

This is a specialization of `dark-deck-builder` for the specific genre of «собеседование в магистратуру» (Russian master's interview).

---

## 1. The committee's regulation (memorize it)

Russian master's interviews follow a fixed structure that the committee reads from a script:

> 2-3 минуты - **самопрезентация**: учебный, научный и профессиональный бэкграунд, **планы на реализацию проекта/исследования** в течение обучения в магистратуре, **мотивация к поступлению**.
> До 7 минут - ответы на вопросы.

The deck must mirror this structure in the same order. Don't reinvent the layout - the committee already has it cached.

---

## 2. The 10-slide canonical structure

Reach for this skeleton every time. Adjust content, not order.

| # | Slide | Role in the narrative | Time |
|---|---|---|---|
| 1 | **Cover** | «[Имя] - планы в магистратуре [программа] [факультет]» + author chip with photo | 5 s |
| 2 | **Кто я** | 5 round avatars of your main projects (real images, not letter badges where possible) + short role + 2-3 lines description per project | 15 s |
| 3 | **Учебный + Научный** | Two big cards side-by-side: **ВКР** (theme + bullets + научрук) and **публикация / КМУ** (with the **real certificate image** if you have one) | 20 s |
| 4 | **Профессиональный** | Horizontal timeline of work roles, badge-per-year, **one metric line under each role** (e.g. "+1 млн ₽ EBITDA", "-15 млн ₽ OPEX/год") | 30 s |
| 5 | **Итог бэкграунда** | Two columns: «В НАЙМЕ» (2 big numbers) and «СВОИ ПЕТ-ПРОЕКТЫ» (2 big numbers). Bottom CTA: «Хочу превратить свои проекты в полноценные бизнесы →». **This slide is the pivot** - it ties the past to the master's project. | 25 s |
| 6 | **Свой проект 1** | Flow diagram («Источники → AI → Канал») + stat-cards underneath. Real numbers from the project. Footer with GitHub link. | 25 s |
| 7 | **Свой проект 2** | Same shape as 6: flow + stats. If the project has a mascot/logo, embed it in the «бот» card of the flow. | 25 s |
| 8 | **План в магистратуре** | Two project avatars on top + 4-semester timeline (4 colored circles, one word under each: Custdev / Юнит-экономика / Пилоты / Раунд + ВКР). | 25 s |
| 9 | **Почему именно эта программа** | Three cards with big numbers 01/02/03: курсы и научрук / комьюнити / партнёрства. Each card: title + 2-3 sentences. | 25 s |
| 10 | **Спасибо** | «Спасибо. / Готов к вопросам.» + author photo chip + contacts | 5 s |

**Total**: ~2:50 at 140-150 words/min spoken pace. Leaves 10 seconds of breathing room.

---

## 3. Active headlines (the highest-leverage habit)

Every slide title must state a **conclusion**, not a topic. A reader who only reads titles must still get the argument.

| Topic title (weak) | Active headline (strong) |
|---|---|
| «Мои проекты» | «Я делаю AI-продукты в Яндексе и свои пет-проекты.» |
| «Опыт работы» | «4 продакт-роли в Яндексе и ВкусВилле.» |
| «Проект Псайко» | «Псайко - дневник рефлексии в Telegram, уже два года в прибыли.» |
| «План в магистратуре» | «Масштабирую @kompege и Псайко в бизнес за 4 семестра магистратуры.» |
| «Мотивация» | «УВБ закрывает три моих конкретных пробела.» |
| «Итог» | «Опыт в найме и в своих проектах - дальше масштабирую пет-проекты в бизнес.» |

Rules:
- **Put the number / verdict in the title** when there is one ("ERR в 1.5 раза", "−10 ч/нед").
- One line, two max. If it wraps to three, cut words.
- Lowercase after the first word; «ёлочки» for quotes.
- Read the title row top-to-bottom - it should narrate the whole story.

---

## 4. Real avatars > letter badges (always)

The single biggest visual win in this genre: **extract real project avatars from your past decks** rather than synthesizing letter-in-circle badges. The audience sees you're a real person with real products, not a generic candidate.

### How to harvest avatars from existing PDFs

```bash
# Step 1: render the source page at high DPI
pdftoppm -r 300 -f <page> -l <page> -png "path/to/source.pdf" raw_avatar

# Step 2: crop + circle-mask in Python (PIL)
python3 <<'PY'
from PIL import Image, ImageDraw

# (a) crop a square around the avatar in the rendered page
src = Image.open('raw_avatar-1.png')
square = src.crop((x1, y1, x2, y2))  # x2-x1 == y2-y1

# (b) resize to 500×500
square = square.resize((500, 500))

# (c) circle mask with transparent PNG output
mask = Image.new('L', (500, 500), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 500, 500), fill=255)
square = square.convert('RGBA')
out = Image.new('RGBA', (500, 500), (0, 0, 0, 0))
out.paste(square, (0, 0))
out.putalpha(mask)
out.save('avatar_circle.png', 'PNG')
PY
```

**Sources to mine first** (Russian student/PM typical):
- Old pitch decks from past competitions (ITMOTECH, КМУ, conferences) - usually have author photo on slide 2.
- Project landing pages (your `piofant.github.io/curation`, etc.) - download the OG image.
- Telegram channel avatars (download from the channel info page).
- Existing project files (`vova_photo.png`, `shiba_avatar.png` lying in `~/Downloads/`).

**If a real avatar isn't available**, fall back to a colored letter badge (one capital letter, brand color, single-letter token). Keep the visual rhythm: same diameter across the 5 cards on slide 2.

### Certificate / diploma images on slide 3

The **КМУ certificate** (or analogous publication confirmation) becomes the right-side image on slide 3. Extract page 1 of `Сертификат_участника_КМУ_*.pdf` at 200 dpi and embed as-is - the certificate is itself proof, no need to describe it in words.

---

## 5. Slide 5 is the pivot - don't skip it

Most candidates jump from «here's my background» straight to «here's my plan», and the committee misses the *why*. Slide 5 explicitly ties past to future:

```
В НАЙМЕ                      |    СВОИ ПЕТ-ПРОЕКТЫ
[40M+ users] [-15 млн ₽]     |    [3 000+ active] [5 000+ subs]
+ MVP X · +1 млн EBITDA      |    + Кейсеры · ITMO.STARS
                                                                
   ↓ Хочу превратить свои проекты в полноценные бизнесы →
```

The bottom line tells the committee what the next 5 slides are about. Without slide 5, slides 6-9 feel disconnected from your background.

---

## 6. Visual system (same as dark-deck-builder)

Palette (hex):
```
bg      #000000   white   #FFFFFF   body    #D6D6D6   eyebrow #9A9A9A   faint #6E6E6E
card    #15161C   line    #2C2E38
purple(accent) #9B87F5  blue #1E73D6  amber #D9920E  green #3FA56B  red #C44133
yandex(brand)  #FFCC00  vkusvill #5BAA50
```

- 16:9 widescreen (pptxgenjs `LAYOUT_WIDE`), MX margin ≈ 0.7 in.
- Eyebrow (top-left, purple, letter-spaced): «Часть 1 · Бэкграунд · учёба».
- Coloured headers/borders **always at transparency ~55-60** - the rainbow tell is the #1 «AI-generated» giveaway.
- Cards: `#15161C` fill, `#2C2E38` border, ~16 px radius.
- Big numbers (`bigNum` helper): 44-60pt depending on label width. Always make them fit on one line - if a number wraps, the slide looks broken.

---

## 7. Build pipeline (programmatic, verified visually)

```
build.js (pptxgenjs)  →  node build.js  →  deck.pptx
deck.pptx  →  soffice --headless --convert-to pdf deck.pptx  →  deck.pdf
deck.pdf   →  pdftoppm -png -r 80 deck.pdf pg  →  pg-NN.png   →  READ the PNGs
```

After every build, **render the changed pages to PNG and read them in the model context**. A page-number reflex: `pg-NN.png` shows printed `NN-1` after the cover (cover has no page number) - re-check after inserting/removing slides shifts everything.

### Critical gotchas (encountered in production)

1. **`pptx.ShapeType.oval` does not exist** - use `pptx.ShapeType.ellipse`. (Common misread of `dark-deck-builder` examples.)
2. **`pptx.ShapeType.line` with h=0** silently corrupts. Use a thin `rect` (h=0.02) plus a `›` glyph as arrowhead - see `arrow()` helper in template.
3. **PIL crop ranges**: `Image.crop((x1, y1, x2, y2))` is in pixels of the rendered PDF page at the dpi you chose. At 300 dpi, a 6 cm × 6 cm avatar is ~700 px wide. Verify with `Image.size` before saving.
4. **Wikipedia / brand-logo CDNs are unreliable** - they often return HTML 403 disguised as PNG. Always `file <name>.png` after download. Don't trust the extension. Falling back to a colored letter badge is fine.
5. **«не только X, но и Y»** - the dreaded Russian negative parallelism. Banned in headlines and CTAs. If you catch yourself writing it, rewrite as two sentences or join with «и».

---

## 8. Iterative review reflex

After building, walk the deck and for each slide ask:

- Does any bullet **restate** the diagram/chart/card next to it? → delete.
- Footnote echoes the title? → delete.
- More than ~3 bullets on a slide? → split into two slides, or half is noise.
- Number wraps to two lines (`5 000\n+`)? → smaller font or rephrase the value.
- Coloured bar looks neon? → add `transparency: 55-60`.
- The cover title is a topic ("Презентация") not a conclusion ("[Имя] - планы в [программа]")? → fix.
- Slide 5 is missing? → add it. **The deck doesn't work without the pivot.**

Cutting is cheap. Decks die from accretion.

---

## 9. Companion text artifacts (always ship together)

A 3-minute deck is the visual half. Always pair it with **two more files**:

1. **`БРИФ.md`** - the speaker brief. Contains:
   - The single main message of the pitch (one sentence).
   - Slide-by-slide hronometrage (~18 s/slide for 3 min).
   - **Full speech text** at ~430 words (3-min spoken pace 140-150 wpm).
   - Anchor numbers to memorize (e.g. «5 660 вакансий», «−10 ч/нед», «×1.5 ERR»).
   - **Q&A bank** of ~7 likely questions with prepared answers (зачем B2B / почему именно эта программа / есть ли LOI / конкуренты / финансирование / pet-проект не отвлекает? / что если не взлетит).
   - Delivery tips (темп, пауза после цифр, контакт глазами).
   - Pre-flight checklist (30 minutes before Zoom).

2. **`БРИФ-humanize.md`** *(optional)* - same brief passed through `humanizer-ru` to strip AI-tells if the original feels too punchy.

The deck without the brief is half the work. Without rehearsing the speech once aloud, the slides don't save you on camera.

---

## 10. Tech: pptxgenjs starter

See `template.js` in this skill folder for the full skeleton: theme palette, helper functions (`newSlide`, `headline`, `card`, `badge`, `imgCircle`, `bigNum`, `arrow`, `traceFlow`), and a 10-slide demo deck.

Run:
```bash
cd <skill-folder>
npm init -y && npm install pptxgenjs
node template.js                                # → deck.pptx
soffice --headless --convert-to pdf deck.pptx   # → deck.pdf
pdftoppm -png -r 80 deck.pdf pg                 # → pg-NN.png to read
```

---

## 11. Anti-patterns (don't)

- Topic-label headlines («Опыт работы», «Мотивация»).
- Letter badges for projects where you actually have a real logo/avatar lying in your Downloads.
- Bullet walls on the «Кто я» slide. Five round avatars with 2-3 line descriptions read in 8 seconds. Bullets read in 30.
- Skipping slide 5 (the pivot). The committee will silently lose the thread.
- Number that wraps to two lines because you crammed too many on a row.
- «ИТМО уже родной» / «Мой родной вуз» - feels sycophantic to the committee that runs that vuz. Demonstrate it through facts (научрук from this faculty, KMУ in this faculty, channel was conceived here).
- Cover headline that's the project name («AI-агрегатор контента - магистерский B2B-проект»). The deck is about *you applying to a program*, not about the project. Cover headline = «[Имя] - планы в магистратуре [программа] [факультет]».
- Shipping without rendering PNGs and **actually looking**.

---

## Confidentiality

The method is the reusable part. When the source decks you mine for avatars are under NDA (internal startup decks, work projects), **keep their data out of any file you commit to a public repo**. Use placeholders in the template. The skill ships the structure, you ship your own content.
