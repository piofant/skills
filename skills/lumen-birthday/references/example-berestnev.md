# Worked example — Dmitry Berestnev (2026-09-02)

The first run of this skill. Use as a pattern for how personalization drives the draft.

## Who
- `@daberestnev`, telegram id `238565135`, Lumi calls him "Дмитрий".
- Lumen | Prototype tester; Yandex-adjacent (has his own team).

## Honcho peer card (the hook source)
```
TRAIT: Честный скептик (Honest skeptic)
PREFERENCE: Любит амбиент, рок, панк музыку
BACKGROUND: Недавно начал новую работу и адаптируется
METHODOLOGY: Предпочитает контент, который бьёт прямо в лоб, без размытых краёв
```
Recent session thread (the real rabbit-hole): all summer Lumi fed him the **history of
Factory Records** — Joy Division, New Order, Hacienda, Tony Wilson, Durutti Column. That
recurring thread + the "честный скептик / без размытых краёв" trait were the personalization.

## Three variants shown to Vova
1. **New Order — Temptation** — warm/metaphorical: "from Joy Division grew something alive" as a
   metaphor for a new year of life.
2. **24 Hour Party People — "Tony Doesn't Sell Out" scene** — cinematic homage to the exact figure
   he studied all summer + a mirror of his no-compromise trait. **(chosen)**
3. **Chat Pile — Deep Blue (2026)** — no-sentiment, fresh heavy track the way Lumi texts him weekly;
   critics had literally compared him to Chat Pile in his own session.

## What shipped
- Card: nano-banana card featuring the Lumen neon creature, Factory/Peter-Saville art direction,
  caption «С ДНЁМ РОЖДЕНИЯ, ДМИТРИЙ» (PIL overlay after the model garbled it as «РОЖДЕНИIЯ»).
- Video: 24HPP scene, downloaded with `player_client=android` (8MB, 2:29).
- Delivery: 8 bubbles via the clone token — opener, card, two build-up lines, video lead-in,
  video, two closing lines. message_ids 18236–18243.
- Continuity: greeting recorded as `is_nudge` assistant turn (51 -> 52), clone restarted.
- Honcho: `BIRTHDAY: 2 сентября (день рождения)` added to his peer card (4 -> 5 entries).

## Lesson
The greeting worked because it named something only *he* had been doing (the Factory dive) and
tied it to *his* self-image (no compromise). Generic "с днём рождения, желаю счастья" would have
been the failure mode. Always mine step 1 before drafting.
