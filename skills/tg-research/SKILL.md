---
name: tg-research
description: Use when the user wants research that combines Telegram chat mining with deep research agents — e.g. "исследуй мои тг-чаты про X", "research my telegram about Y", "вытащи контекст из чатов с Z и сделай ресерч", or the slash form /tg-research. Pulls history/search from telegram-remote MCP, crystallizes findings into outline.yaml + fields.yaml, runs parallel research-deep agents with TG context baked in, then produces a markdown report and optionally delivers it back to Saved Messages. Do NOT use for plain web research (use /research instead) or for pure chat reading without synthesis.
user-invocable: true
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion, Task, WebSearch, mcp__telegram-remote__list_chats, mcp__telegram-remote__get_chats, mcp__telegram-remote__get_history, mcp__telegram-remote__search_messages, mcp__telegram-remote__resolve_username, mcp__telegram-remote__get_me, mcp__telegram-remote__send_file, mcp__telegram-remote__send_message, mcp__telegram-remote__list_messages
---

# TG Research — Telegram + Deep Research combo

## Trigger
`/tg-research <topic or question>` — or any natural-language request that mentions исследование/research with Telegram chats as primary data source.

## Why this skill exists
The canonical `/research → /research-deep → /research-report` pipeline assumes structured, web-searchable objects. When the **data source is the user's own Telegram chats** (personal DMs, group chats, channels), two failure modes appear:

1. **Lossy handoff** — TG messages get copy-pasted into the prompt as unstructured text, so parallel research agents have no deterministic context to work from.
2. **Skipped outline** — assistant bypasses `outline.yaml` because "this is just a direct query", and you lose resumability, per-item structure, and the report step.

This skill formalizes the bridge: **TG MCP pull → outline.yaml items with embedded tg_context → research-deep → report → (optional) deliver back to Saved Messages**.

## Workflow

### Step 1 — Scope interview (AskUserQuestion)
Ask the user ONLY the questions you can't answer from the request. Defaults in brackets; skip a question if the answer is obvious:

1. **Topic / central question** — one sentence ([use the slash arg]).
2. **Chats to mine** — names, @usernames, or "let me list them". If "list them", call `mcp__telegram-remote__list_chats` and present the top 30 by activity via AskUserQuestion (multi-select).
3. **Time range** — e.g. "last 30 days", "since 2025-01-01", "all". Default: last 90 days.
4. **Keyword queries** (optional) — words/phrases to `search_messages` for in addition to `get_history`. Default: none.
5. **Deliver report back to Telegram?** — yes → Saved Messages; no → local only. Default: no.
6. **Output dir** — default `~/research/<topic-slug>/`.

Do NOT ask questions the user already answered in the invocation. Treat the slash arg as load-bearing.

### Step 2 — TG mining (parallel)
Create `<output-dir>/tg_data/`. For each chat resolved in Step 1, in parallel:

- `mcp__telegram-remote__get_history` with `limit` sized to the time range (start at 200 messages per chat; if time range is wider, loop with `offset_id` until you cross the lower bound).
- For each keyword query from Step 1: `mcp__telegram-remote__search_messages` scoped to that chat.
- De-duplicate by message_id.
- Write to `<output-dir>/tg_data/<chat-slug>.json` with this shape:

```json
{
  "chat_id": 123,
  "chat_name": "...",
  "chat_type": "private|group|channel",
  "range": {"from": "...", "to": "..."},
  "message_count": 234,
  "messages": [
    {"id": 1, "date": "2026-04-01T12:00:00", "from": "<sender name>", "text": "..."}
  ]
}
```

**Resume rule**: if `tg_data/<chat-slug>.json` already exists AND `mtime < 24h`, skip re-pull unless user asked "refresh".

**Chat ID gotcha**: `"me"` is rejected by `send_file` / some endpoints. Always resolve the user's own ID up front via `mcp__telegram-remote__get_me` and cache it.

### Step 3 — Crystallize into outline.yaml + fields.yaml
Call **the model's own judgment** to group the pulled data into research **items**. Three valid grouping strategies — pick the one that fits the topic and confirm with the user in one AskUserQuestion:

- **By chat** — each chat is one item. Best when user compares communication across people (e.g. "how do I write to X vs Y").
- **By theme** — cluster messages across chats into 3–10 themes. Best when exploring a question across all chats (e.g. "my humor style").
- **By person/entity** — each person mentioned becomes an item. Best for biographical/relational research.

Write `<output-dir>/outline.yaml`:

```yaml
topic: "<topic>"
source: tg-research
items:
  - id: <slug>
    name: "<human name>"
    category: "<chat|theme|person>"
    description: "<one-line why this item matters>"
    tg_context_file: "tg_data/<chat-slug>.json"   # or list of files if theme spans chats
    tg_context_snippets: |
      # 3–8 short verbatim excerpts, each prefixed with date + speaker
      # These give the research-deep agent grounding without forcing it to load megabytes
execution:
  batch_size: 3           # ask user; default 3
  items_per_agent: 1      # default 1 — tg-research items are rich, one per agent is right
  output_dir: "./results"
```

Write `<output-dir>/fields.yaml` — start from this template tuned for chat analysis, then ask user if they want to add/remove:

```yaml
categories:
  observations:
    - name: key_patterns
      description: "Recurring communication patterns observed in the TG context (what, not why)"
      detail_level: detailed
    - name: emotional_tone
      description: "Dominant emotional register(s) with evidence quotes"
      detail_level: moderate
    - name: notable_moments
      description: "3–5 turning-point messages with date + verbatim quote"
      detail_level: detailed
  interpretation:
    - name: hypotheses
      description: "Interpretive hypotheses about what drives the patterns; each hypothesis must cite a TG excerpt AND a supporting web source"
      detail_level: detailed
    - name: contradictions
      description: "Places where TG evidence disagrees with the working hypothesis"
      detail_level: moderate
  external_context:
    - name: relevant_frameworks
      description: "Theoretical frameworks / research / literature that illuminate the patterns (use WebSearch)"
      detail_level: moderate
    - name: sources
      description: "List of [title](url) citations used"
      detail_level: detailed
  actionables:
    - name: open_questions
      description: "Questions the TG data alone cannot answer — for follow-up"
      detail_level: brief
    - name: next_steps
      description: "Concrete next actions the user could take"
      detail_level: brief
uncertain: []
```

Show both files to the user, ask for confirmation before Step 4.

### Step 4 — Deep research (hard-constrained prompt)
For each item, launch a parallel `Task` agent (prefer subagent_type `general-purpose` or `web-search-agent`). **Reproduce the prompt template verbatim, only substituting `{variables}`. Do not paraphrase.**

```python
prompt = f"""## Task
Research item {item_related_info}. Produce structured JSON at {output_path}.

## Primary data (TELEGRAM — ground truth)
You have two sources of TG data for this item:
1. Full message dump: {tg_context_file_abs_path}  (JSON, read it first)
2. Curated excerpts below — use these as anchors, but the full dump is authoritative:

{tg_context_snippets}

## Secondary data (WEB)
Use WebSearch to find frameworks, research, literature, or public context that illuminates the TG patterns. Cite every web source as [title](url). Do NOT invent sources.

## Field definitions
Read {fields_path} to get the complete field schema for this item.

## Output rules
1. Output JSON covering every field in fields.yaml.
2. Every interpretive claim must cite either (a) a TG excerpt (include date + short quote) or (b) a web source (include URL). Unsupported claims → mark [uncertain].
3. Add an "uncertain" array at JSON root listing all uncertain field names.
4. If the TG data contradicts a common framework, flag it under `contradictions`, don't smooth it over.
5. Field values in the same language the user asked the question in (default: Russian if user wrote in Russian).

## Output path
{output_path}

## Validation
After writing JSON run:
python ~/.claude/skills/research/validate_json.py -f {fields_path} -j {output_path}
Only mark the task done after validation passes.
"""
```

Variables:
- `{item_related_info}` — the item's full yaml block
- `{tg_context_file_abs_path}` — absolute path to the chat dump(s); if multiple, comma-joined
- `{tg_context_snippets}` — the item's `tg_context_snippets` field, verbatim
- `{fields_path}` — absolute path to `fields.yaml`
- `{output_path}` — `<output-dir>/results/<item-id>.json`

Batch by `execution.batch_size`. After each batch, show progress. Never auto-continue to next batch — ask the user (they may want to inspect one result before spending more turns).

### Step 5 — Report
Delegate to `/research-report` or run its logic inline:
- Read every `results/*.json`, merge into `<output-dir>/report.md`.
- TOC lists items with one-line hooks.
- Each item section: observations → interpretation → external_context → actionables.
- **Appendix**: under each item, add a collapsible-style "Raw TG excerpts" block containing the `tg_context_snippets` verbatim — so the reader can verify citations without opening the JSON.
- Skip any field marked `[uncertain]` or present in the item's `uncertain` array.

### Step 6 — Optional delivery (only if user said yes in Step 1)
- Resolve user id: `mcp__telegram-remote__get_me` → `self_id`.
- `mcp__telegram-remote__send_file` with `chat_id=self_id`, file = `<output-dir>/report.md` (convert to PDF via `pandoc` first if user prefers — ask).
- If MCP returns "roots deny-all" or similar, fall back: leave the file at `<output-dir>/report.md` and tell the user the exact path with a link-style reference.
- NEVER send the report to any chat other than Saved Messages without explicit user confirmation — the file may contain third-party private messages.

## Hard rules

1. **Privacy** — the report and raw dumps contain private messages from people who did not consent to AI analysis. Do not upload them to web services (no pastebins, no gists, no cloud renderers, no web diagram tools). Keep everything under `~/research/<topic-slug>/` locally.
2. **No third-party delivery** — only Saved Messages, and only with explicit confirmation.
3. **Quote accurately** — every TG quote in the report must be verbatim (emoji preserved, typos preserved). If paraphrased, mark `[paraphrased]`.
4. **Cite or mark uncertain** — interpretive claims without a TG excerpt or web source = `[uncertain]`.
5. **Respect context window** — if a chat dump is > 500 KB, don't put it in the prompt directly; just pass the file path plus `tg_context_snippets`. The agent reads the file.
6. **Resume-safe** — re-running the skill on the same topic must not re-pull TG data (unless user said refresh), not re-run completed items (check for results/<id>.json), and not overwrite the existing outline without confirmation.

## Error handling

| Error | Response |
|---|---|
| `telegram-remote` MCP not connected | Tell the user, stop. Don't silently fall back to web-only. |
| `chat_id="me"` rejected | Resolve self-id via `get_me` first, retry. |
| `send_file` returns roots-deny | Skip delivery, report local path. Don't retry — this is a known config issue. |
| `get_history` returns empty | Verify `chat_id` with `resolve_username` or `list_chats`; check time range. |
| A research-deep agent returns incomplete JSON | The validate_json.py step catches this; the agent should retry. If it fails twice, mark the item `[failed]` in the report and continue. |

## Output layout

```
~/research/<topic-slug>/
├── outline.yaml
├── fields.yaml
├── tg_data/
│   ├── <chat-slug>.json
│   └── ...
├── results/
│   ├── <item-id>.json
│   └── ...
└── report.md
```

## Example invocations

- `/tg-research как меняется мой тон в рабочих чатах за год` — by-chat grouping, 2-3 work chats, keywords like "дедлайн", "успеваем", "давай созвон".
- `/tg-research мой стендап-стиль по всем чатам` — by-theme grouping, all active chats, keywords "ахаха", "шутка", "😂".
- `/tg-research как я договариваюсь о встречах` — by-theme, all chats, web-grounded in negotiation and coordination frameworks.

## Related skills
- `/research` — use for pure web research; no TG involved.
- `/research-deep`, `/research-report` — this skill delegates to their logic, don't duplicate.
- `notebooklm` — complements this skill when there is separate diary/voice data that should be queried in parallel.
