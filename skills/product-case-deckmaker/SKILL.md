---
name: product-case-deckmaker
description: >-
  Solve product case interviews, test tasks, and strategy assignments end-to-end: frame the business
  goal, run discovery and competitor analysis, define the MVP and pilot, build a consulting-style
  deck, and add a lightweight prototype when it helps explain the product. Use for PM test tasks, case
  studies, product strategy homework, discovery writeups, and executive-ready slide decks.
---

# Product Case Deckmaker

Use this skill when the task is not just "make slides" and not just "solve a product problem", but both:
- understand the business goal
- do product reasoning
- turn it into a strong deck
- optionally add a simple prototype to make the product legible

This skill is optimized for:
- PM test tasks
- product strategy case studies
- take-home assignments
- internal product proposals
- decks where the audience is hiring managers, heads of product, founders, or strategy-minded stakeholders

## Companion Skills

Use the minimum set that fits the task:
- `market-analysis` for MECE, framing, SCPR, TAM/SAM/SOM, RICE
- `competitive-teardown` for competitor jobs, strengths, weaknesses, UX gaps, positioning
- `product-manager-toolkit` for discovery, hypotheses, MVP, validation, metrics
- `product-strategist` for business goal, metric tree, org-level reasoning, why this matters for the company
- `board-deck-builder` for answer-first structure and executive clarity
- `pitch-deck-builder` for narrative sequencing and presentation arc
- `research-summarizer` when you need clean synthesis and source handling
- `pr-review-expert` for final red-team review of the deck and argumentation

Recommended order:
1. `market-analysis` or `product-strategist`
2. `competitive-teardown`
3. `product-manager-toolkit`
4. `board-deck-builder`
5. `pitch-deck-builder`
6. `pr-review-expert`

## Core Principles

### 1. Start from the business goal

Do not start with "there is a user pain"

Start with:
- what business outcome matters
- why this case matters for the company
- what role the product plays in getting that outcome

Good pattern:
- `Business goal -> product role -> user problem -> MVP -> pilot -> decision`

Bad pattern:
- `Interesting idea -> market overview -> long user research -> maybe a feature`

### 2. Use answer-first headlines

Slide headlines should contain the conclusion, not the topic

Bad:
- `Problem`
- `Research results`
- `Competitors`
- `MVP`

Good:
- `Чтобы привлечь больше сильных олимпиадников в воронку, ЦУ может снять боль с выбором олимпиад через сервис подбора под поступление`
- `50% активных участников путаются в льготах, а около 85% уже теряли этапы`
- `Рынок уже решает поиск, но не помогает выбрать олимпиады под конкретную цель поступления`

### 3. Keep claims proportional to evidence

Do not overclaim from weak evidence

If the evidence is:
- polls in one channel
- exploratory interviews
- public signals
- rough desk research

Then say:
- `exploratory research`
- `signal for hypothesis`
- `enough to justify a cheap pilot`

Do not say:
- `we proved demand`
- `statistically significant`
- `the market clearly wants X`

unless you can actually defend that

### 4. MECE or it gets muddy

Separate different types of dimensions

Common mistake:
- mix user segment, benefit type, target university, product category, and use case in one list

For example, in a selection interface, split:
- profile or direction
- target university level
- specific target university
- benefit type
- grade or timing

Do not mix:
- `ЦУ`
- `AI и CS`
- `топ-вуз`

in one dimension

### 5. Show the object, not just the reasoning

If the product essence is hard to grasp from slides alone, add a lightweight prototype

Use a prototype when:
- readers keep asking "what is the thing"
- the product is more about flow than about one feature
- a mock interface can explain the idea faster than 3 slides

For a product-case prototype, fake data is fine

Do not wait for backend or parsing

### 6. Make the deck sound human

Anti-AI writing rules:
- avoid filler like `значит`, `таким образом`, `в рамках`, `при этом`, if not needed
- avoid long abstract nouns where a simple verb works
- avoid long dashes when a comma or colon is cleaner
- avoid overpolished consultant-speak if the user’s style is more direct
- cut duplicate lines aggressively
- prefer short, spoken-sounding Russian
- do not end every bullet with a period unless the style clearly needs it
- if a sentence sounds like it is trying too hard, shorten it

### 7. Sources should support, not clutter

When facts matter:
- include links
- keep sources in the footer or source line
- do not overload the body text with blue hyperlinks

Evidence hierarchy:
- public facts with links
- screenshots if they add credibility
- short source footer

## Workflow

### Phase 1. Frame the case

Before doing research, extract:
- company objective
- why this case matters now
- target segment
- likely business mechanism

Output:
- 1-sentence business goal
- 1-sentence product role
- draft metric tree

Template:
- `Business goal: ...`
- `Product role: ...`
- `North-star or primary success metric: ...`
- `Supporting metrics: ...`

If the product is a lead magnet, say it directly

Example:
- `Business goal: attract more strong applicants`
- `Product role: useful utility that becomes a high-intent entry point`
- `Primary metric: qualified leads or high-intent sign-ups, not pageviews`

### Phase 2. Research the problem

Work from strongest to weakest sources:
1. internal brief or notebook
2. public product surfaces
3. user evidence
4. competitor evidence

For user evidence:
- prefer problems over feature wishlists
- if the existing poll asks about features, treat it as weak evidence
- when possible, normalize results to the active or relevant subgroup

Always separate:
- whole sample
- active sample
- exploratory signal

Output:
- 2-3 core user pains
- what is known
- what is only hypothesized
- what still needs pilot validation

### Phase 3. Analyze the market and competitors

Do not make a feature checklist first

Start with jobs:
- what job each player already solves
- what they do well
- what the user still does manually
- where the white space is

Recommended competitor table:

| Player | Job already solved | What it does well | What the user still does manually |
|---|---|---|---|
| X | ... | ... | ... |

Good competitor insight sounds like:
- `Player A already solves search and aggregation`
- `Player B explains the category`
- `Player C helps compare options`
- `Our white space is choose + act`

If one incumbent is strong, say it

Do not pretend the market is empty just because you need room for your idea

### Phase 4. Define the product wedge

The wedge is the narrow product entry point that:
- maps to the business goal
- addresses the strongest user pain
- does not require building the full platform

Use this formula:
- `We are not building X, we are building Y for Z`

Example:
- not another olympiad catalog
- but a selection and deadline guidance service for applicants aiming at specific admission outcomes

Output:
- product one-liner
- wedge
- not-in-scope statement

### Phase 5. Define MVP

MVP should be framed as:
- what the user does
- what the product must do
- what you deliberately do not build

Avoid infrastructure-first wording like:
- Airtable
- bot
- parser
- CRM tags

unless the slide is specifically about technical implementation

Prefer:
- choose goal
- see relevant options
- save track
- get reminders

For each MVP element, answer:
- what pain does it close
- why is it first-version material
- what happens if we remove it

### Phase 6. Define pilot and decision logic

A strong case does not end with "launch MVP"

It ends with:
- pilot scope
- what signals mean success
- what signals mean rebuild
- how risk is mitigated

Use signals, not fake precision

Prefer:
- users save their track
- users return to their calendar
- users enable reminders
- usefulness leads into the target funnel

Be careful with exact thresholds if you cannot justify them

If needed, say:
- `first directional validation`
- `meaningful early sample`
- `strict comparison requires more traffic`

### Phase 7. Make the deck

Default deck order for PM cases:
1. Cover
2. Contents
3. Executive summary
4. Business goal and metric tree
5. Problem and research
6. Market and competitors
7. Positioning or wedge
8. Why this company can win
9. MVP
10. Technical implementation, only if helpful
11. Pilot and decision logic
12. Risks and mitigation
13. Call to action

If using a prototype:
- place it in the solution section
- optionally right after MVP or right after the wedge
- explain why the prototype exists: to make the product legible quickly

## Slide Production Workflow

When the deck needs to be both:
- carefully laid out
- and editable later in Google Slides

use this workflow:

1. build a real `.pptx` locally
2. import that `.pptx` into Google Drive as a Google Slides file
3. continue editing in Google Slides

Preferred pipeline:

```text
deck narrative -> local .pptx builder -> .pptx file -> import to Google Slides -> manual polish in Slides
```

### Why this workflow is preferred

Direct generation into Google Slides often produces weak layout:
- text-heavy slides
- broken spacing
- fragile formatting
- poor table and callout composition

Building `.pptx` first gives much better control over:
- coordinates
- spacing
- type hierarchy
- tables
- cards
- screenshots
- colors
- links

Then importing into Google Slides converts it into a natively editable Google presentation

### Recommended implementation

Use a local JS builder such as `PptxGenJS`

What to define in code:
- slide order
- reusable slide helpers
- title and body text blocks
- tables
- callouts
- big numbers
- image cards
- source lines
- theme colors

Output:
- one `.pptx` file that already looks close to final

### How to make it editable in Google Slides

Do not upload the `.pptx` as a plain file if you want a fully editable Google deck

Instead, import it into Drive with:
- target mime type: `application/vnd.google-apps.presentation`

That tells Google Drive to convert the PowerPoint into a native Google Slides presentation

After conversion:
- open the returned `webViewLink`
- continue editing in Google Slides normally

### Practical recommendation

Use this rule:
- if speed matters more than layout, direct Slides generation may be fine
- if the deck must look intentional, build `.pptx` first and import it

For high-stakes PM case decks, prefer:
- `.pptx` first
- Google Slides second

### Validation after import

Always review the imported deck slide by slide

Common things to check:
- text overflow
- font substitutions
- moved screenshots
- table row heights
- callout padding
- footer/source overlap
- section color consistency

If the imported version drifts:
- fix the local builder
- re-export
- re-import as a new version

Do not patch dozens of layout bugs manually in Slides if they originate from the builder

## Slide-by-Slide Guidance

### Executive Summary

One headline plus 3-5 numbered points

Rules:
- should not repeat every next slide verbatim
- should summarize the argument
- should already contain the recommendation

Good summary structure:
1. business goal
2. main pain
3. market gap
4. product recommendation
5. pilot logic

### Business Goal Slide

Show:
- business goal
- role of product
- main metric
- supporting metrics

Do not hide the business logic until slide 7

### Research Slide

If you have real screenshots, use them

For poll-heavy evidence:
- use screenshots or evidence cards
- keep one short answer-first headline
- add one short box: `What this means for the product`

If you normalize to active users, say so clearly

### Competitor Slide

Avoid long bullet lists

Prefer:
- table by jobs
- or 3-column comparison
- or one white-space framing slide

Headline should answer:
- why the company should not copy the incumbent
- where the company can still add value

### Why We Can Win Slide

Use proof blocks, not a wall of text

Good patterns:
- `Base of trust`
- `Clear offer for this segment`
- `Own distribution`

### MVP Slide

If the product is flow-heavy, use a flow diagram

Show:
- `goal -> options -> track -> reminders`

If another slide explains why each piece is included, make it a compact table

If not, keep the MVP slide simple

### Technical Slide

Use only if technical feasibility is a real concern

Do not make it backend-heavy

Best pattern:
- `sources -> data layer -> user layer`

Message:
- the technical problem is manageable
- the value is not in raw aggregation
- the value is in helping users decide and act

### Pilot Slide

Do not bury the decision logic in tiny text

Good pattern:
- `Week`
- `What we do`
- `What we learn`
- `Decision`

or

- 3 cards for 3 weeks
- one clear bottom band: `What we do if signals are weak`

### Risks Slide

Never just list risks

Format:
- `Risk`
- `Why it matters`
- `How we mitigate it`

Examples:
- narrow audience -> start with a narrow segment intentionally
- biased channel -> compare across at least 2 traffic sources
- data accuracy -> manually validate critical fields during pilot

### Call to Action Slide

Keep it light

Do not end with another overloaded plan slide

Good format:
- one line about the next step
- one line about what you can do after approval
- name and role

Example:
- `Готов обсудить следующие шаги`
- `После апрува могу собрать прототип и помочь с пилотной проверкой`
- `Имя, роль, контакт`

## Prototype Guidance

If a prototype is needed, keep it fake and focused

Default prototype pattern for product cases:
1. input screen
2. output screen
3. retention or follow-up screen

For example:
1. choose target goal
2. see relevant options
3. save track and reminders

Rules:
- no backend
- no real parsing required
- fake data is fine
- make the object of the product obvious in 10 seconds
- use the company’s visual language lightly, do not overspend effort on full design system fidelity

## Writing Rules

### Use this tone
- direct
- calm
- answer-first
- not too polished
- not too startup-bro
- not too consultant-robot

### Avoid this tone
- empty abstraction
- overconfident evidence language
- generic AI phrasing
- feature soup
- repeated “therefore / thus / значит” constructions

### Editing checklist

Before finalizing, remove:
- duplicated slides
- duplicated arguments
- topic headlines instead of conclusion headlines
- claims stronger than evidence
- paragraphs that should be diagrams
- blue links inside dense text blocks

### Human-style checklist

- Could a person say this aloud in a meeting
- Is the sentence shorter than it was before
- Can one noun be replaced with a verb
- Is the recommendation obvious by slide 3
- Does the deck show the product as an object, not only as a theory

## Deliverables

When the task is complete, aim to produce:
- one main document or memo
- one main deck
- optional appendix
- optional lightweight prototype
- one short defense script or Q&A doc if the task is interview-like

## Final Validation

Before shipping:
1. Red-team the deck with `pr-review-expert` if possible
2. Check whether the main recommendation is visible by slide 3
3. Check whether each slide headline is a conclusion
4. Check whether the product essence is obvious without narration
5. Check whether the pilot can actually produce a decision
6. Check whether business goal and metric logic are explicit

If the deck still feels fuzzy, the missing thing is usually one of these:
- the business goal is hidden
- the wedge is too broad
- the product object is not visualized
- the pilot does not have a decision rule
- the headlines are topics, not conclusions

## Appendix

### Appendix A. Minimal `build-pptx.js` skeleton

Use this as a starting point when you want a code-generated deck that later stays editable in Google Slides

```js
const path = require("path")
const pptxgen = require("pptxgenjs")

const pptx = new pptxgen()
pptx.layout = "LAYOUT_WIDE"
pptx.author = "Your Name"
pptx.company = "Your Company"
pptx.subject = "Product case deck"
pptx.title = "Case deck"
pptx.lang = "ru-RU"
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "ru-RU",
}

const COLORS = {
  ink: "141414",
  muted: "5D5D5D",
  line: "D6D6D6",
  bg: "FAFAFA",
  bgSoft: "E6E6E6",
  white: "FFFFFF",
  accent: "00A651",
  accentSoft: "E9F7EF",
}

function addFrame(slide, eyebrow) {
  slide.background = { color: COLORS.bg }
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 13.333, h: 0.45,
    fill: { color: COLORS.bgSoft },
    line: { color: COLORS.line, pt: 1 },
  })
  slide.addText(eyebrow, {
    x: 0.8, y: 0.13, w: 4, h: 0.15,
    fontFace: "Aptos", fontSize: 11, bold: true,
    color: COLORS.accent, margin: 0,
  })
}

function addHeadline(slide, text) {
  slide.addText(text, {
    x: 0.7, y: 0.82, w: 11.8, h: 0.72,
    fontFace: "Aptos Display", fontSize: 22, bold: true,
    color: COLORS.ink, margin: 0,
  })
}

function addCallout(slide, title, body, { x, y, w = 4.2, h = 1.4 } = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: COLORS.white },
    line: { color: COLORS.line, pt: 1.2 },
  })
  slide.addText(title, {
    x: x + 0.2, y: y + 0.16, w: w - 0.4, h: 0.18,
    fontFace: "Aptos", fontSize: 12, bold: true,
    color: COLORS.accent, margin: 0,
  })
  slide.addText(body, {
    x: x + 0.2, y: y + 0.42, w: w - 0.4, h: h - 0.55,
    fontFace: "Aptos", fontSize: 14,
    color: COLORS.ink, margin: 0, fit: "shrink",
  })
}

function addSourceLine(slide, runs, y = 6.55) {
  slide.addText(runs, {
    x: 0.95, y, w: 11.2, h: 0.2,
    fontFace: "Aptos", fontSize: 9,
    color: COLORS.muted, margin: 0, fit: "shrink",
  })
}

{
  const slide = pptx.addSlide()
  addFrame(slide, "Раздел 1 / Executive summary")
  addHeadline(slide, "Short answer-first headline")
  addCallout(slide, "What matters", "Short body text", { x: 0.95, y: 2.0 })
  addSourceLine(slide, [
    { text: "Source: ", options: { bold: true } },
    { text: "example.com", options: { hyperlink: { url: "https://example.com" } } },
  ])
}

pptx.writeFile({ fileName: path.join(__dirname, "case-deck.pptx") })
```

Use helpers aggressively

Do not hand-code each slide from scratch if:
- the deck has repeated callouts
- the deck has repeated section headers
- the deck has repeated number cards
- the deck has repeated source footers

### Appendix B. Minimal Drive API import to editable Google Slides

This pattern imports a local `.pptx` into Google Drive as a native Google Slides file

Requirement:
- valid OAuth token with `drive.file`

```python
import json
import uuid
from pathlib import Path
import requests

token = json.loads(Path("/path/to/token.json").read_text())["access_token"]
file_path = Path("/path/to/case-deck.pptx")

url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType,webViewLink"
boundary = "----codex" + uuid.uuid4().hex

metadata = {
    "name": "Case deck",
    "mimeType": "application/vnd.google-apps.presentation",
}

file_bytes = file_path.read_bytes()
body = []
body.append(
    f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(metadata, ensure_ascii=False)}\r\n".encode("utf-8")
)
body.append(
    f"--{boundary}\r\nContent-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation\r\n\r\n".encode("utf-8")
)
body.append(file_bytes)
body.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))

resp = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/related; boundary={boundary}",
    },
    data=b"".join(body),
    timeout=120,
)

print(resp.status_code)
print(resp.json())
```

If the response includes:
- `mimeType = application/vnd.google-apps.presentation`
- `webViewLink`

then the file is already a native Google Slides deck

To open access with link sharing:

```python
import json
from pathlib import Path
import requests

token = json.loads(Path("/path/to/token.json").read_text())["access_token"]
file_id = "GOOGLE_FILE_ID"

resp = requests.post(
    f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
    params={"fields": "id"},
    json={"type": "anyone", "role": "reader"},
    timeout=120,
)

print(resp.status_code)
print(resp.json())
```

### Appendix C. Pre-send checklist

Run this before sending the deck

#### Story

- Is the business goal explicit before deep research begins
- Is the recommendation obvious by slide 3
- Does the deck answer `why this matters for the business`
- Does the deck answer `what exactly the product is`
- Does the deck answer `why this company can win`
- Does the deck answer `how we will know if the hypothesis worked`

#### Evidence

- Are all quantitative claims supported by a source
- Are source links present for factual statements
- Are weak signals labeled as exploratory, not proven
- If polling is used, is the denominator clear
- If percentages are normalized, is that logic defensible
- Are competitors described honestly, without pretending the market is empty

#### Slides

- Does every slide have an answer-first headline
- Are there any topic headlines left
- Are there too many words on any slide
- Can any dense paragraph become a diagram, table, or 3-block structure
- Are there repeated slides saying the same thing
- Are appendix-level details polluting core slides
- Are section colors and accents consistent

#### Language

- Does the text sound like a real person speaking
- Did you remove filler like `значит`, `таким образом`, `в рамках`
- Did you cut obvious AI phrasing
- Are there any long sentences that can be split
- Are there any abstractions that can be replaced with plain language
- Are you overusing jargon where a user-facing term is clearer

#### Product logic

- Is the wedge narrow enough
- Is the MVP truly minimal
- Did you avoid shipping the full platform in the story
- Is the pilot small enough to run cheaply
- Does each risk have a mitigation, not just a label
- Does the deck show what happens if the pilot fails

#### Prototype

- Does the prototype explain the product in under 10 seconds
- Is the first screen MECE
- Does it show user-facing language, not internal product language
- Does it clarify the object of the product faster than the deck alone
- Is fake data good enough to demonstrate the flow

#### Google Slides import

- Did you verify the imported deck, not just the local `.pptx`
- Are fonts acceptable after import
- Did any text overflow after conversion
- Did screenshots move or crop badly
- Did table heights or callout paddings break
- Are footer links still readable
- If import drifted badly, did you fix the builder instead of patching everything manually

### Appendix D. Auth and local credentials

When this workflow touches:
- GitHub
- Google Drive
- Google Slides

always check whether Codex is already logged in before starting a fresh auth flow

#### GitHub

First check:

```bash
gh auth status
```

If GitHub CLI is already logged in, prefer reusing that session

Typical local metadata path:

```text
~/.config/gh/hosts.yml
```

What it is useful for:
- confirming the active GitHub user
- confirming the git protocol
- confirming that a GitHub session already exists

What not to do:
- do not paste tokens into the skill
- do not echo secrets into logs unnecessarily
- do not re-auth if `gh auth status` already shows a healthy session

Practical use cases:
- create a repo for a prototype
- push a static mock to GitHub
- enable GitHub Pages

Recommended sequence:

```bash
gh auth status
gh repo create ...
git push
gh api repos/<owner>/<repo>/pages ...
```

#### Google Slides / Drive

First check whether local Google MCP auth already exists

Typical local paths:

```text
~/.google-mcp-server/config.json
~/.google-mcp-server/token.json
```

What these are useful for:
- `config.json` usually tells you which scopes and redirect URI were used
- `token.json` usually stores the access token and refresh token for the current local session

What not to do:
- do not copy the access token or refresh token into docs or chat summaries
- do not expose `client_secret` values in a skill
- do not assume the token is fresh; verify by actually making a request or using the MCP tool

Recommended checks:

```bash
ls -la ~/.google-mcp-server
sed -n '1,200p' ~/.google-mcp-server/config.json
```

If using MCP:
- try a small Drive or Slides action first

If using direct API:
- use the existing token file
- upload the `.pptx` to Drive as `application/vnd.google-apps.presentation`
- then create an `anyone` or specific-user permission only if sharing is needed

#### Rule of thumb

Before any auth-heavy task, check in this order:
1. existing CLI auth
2. existing MCP auth
3. existing token/config files
4. only then start a new login flow

This avoids:
- duplicate auth
- broken parallel sessions
- unnecessary token churn
- wasting time on flows that are already solved
