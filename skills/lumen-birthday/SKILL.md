---
name: lumen-birthday
description: Use when Vova wants to send a personalized proactive greeting (birthday or milestone) to a Lumen/Lumi user THROUGH the bot — e.g. "поздравь Диму с др через Люми", "у X сегодня др, придумай поздравление и вышли", "отправь юзеру Y открытку от Люмена", or /lumen-birthday. Grounds the message in the user's Honcho memory, optionally builds a Lumen character card (nano-banana) and downloads a taste-relevant video (yt-dlp), delivers it as multi-bubble via the CLONE bot token (never Vova's account), then records continuity into the session and writes the occasion to the Honcho peer card. NOT for mass nudges (that is the heartbeat nudge pipeline) and NOT for sending from Vova's personal Telegram.
user-invocable: true
allowed-tools: Read, Write, Bash, Glob, Grep, AskUserQuestion, SendUserFile
---

# lumen-birthday — personalized greeting to a Lumen user, via the bot

## Trigger
`/lumen-birthday <who + occasion>` or any natural request to congratulate / send a
personal message to a specific Lumen user through the bot.

## Why this skill exists
A birthday greeting to a real user is an outbound, hard-to-reverse action with three
traps that a naive "just send a nice message" gets wrong:
1. Sending from Vova's Telegram account is forbidden — it pollutes prod user history and
   acts as him. Always send with the CLONE bot's own token.
2. A raw Bot-API send bypasses the SessionManager, so the bot answers the user's "спасибо"
   cold. You must record the greeting into the session and restart the clone.
3. Image models garble Cyrillic and YouTube blocks most yt-dlp clients — both have known fixes.

The personalization comes from the user's Honcho peer card + their recent session, so the
message hooks their actual taste, not a generic template.

## Hard rules
- CLONE only. Real users live on `nanobot-clone` (`@lumen_charecter_bot`,
  `HOME=/root/nanobot-clone-home`). Never touch Vova's account or the dev bot.
- Show Vova the draft (text + card + video) BEFORE sending. Sending is his call.
- Run every script with `/root/nanobot-venv/bin/python` (bare `python3` misses deps).
- Do NOT print secrets. The scripts read tokens/keys from config/service-env internally.

## Steps

### 1. Identify the user and read their memory (personalization)
Find their telegram id and their Honcho profile. The peer card is the gold source.
```bash
# find id + name from any prod artifact (reactions, pappie threads, sessions)
grep -rIl -i "<name-or-username>" /root/nanobot-clone-home/.nanobot /root/nanobot-honcho/workspace/dumps 2>/dev/null
# read their live Honcho peer card + recent session
HOME=/root/nanobot-clone-home /root/nanobot-venv/bin/python -c "import sys;sys.path.insert(0,'/root/nanobot-honcho');\
from nanobot.honcho.client import get_honcho_client as g;import subprocess,shlex,os;\
[os.environ.setdefault(*t.split('=',1)) for t in shlex.split(subprocess.run(['systemctl','show','nanobot-clone','-p','Environment','--value'],capture_output=True,text=True).stdout) if '=' in t];\
print(g().peer('user-telegram-<ID>').get_card())"
```
Also skim the tail of `/root/nanobot-clone-home/.nanobot/sessions/telegram_<ID>.jsonl` for
their running threads (what Lumi has been talking to them about). Pull out: their trait, taste,
and any recurring rabbit-hole — that is the hook.

### 2. Draft the greeting (in Lumi's voice)
Write 3 short distinct variants and show Vova; let him pick or tweak. Match Lumi's texting
register (direct, warm, no fluff, avoid the banned cliches плотн/цепк/многослойн/густ). Ground
every variant in a real fact from step 1. See `references/example-berestnev.md` for a worked case.

### 3. (optional) Build a Lumen character card — nano-banana
```bash
cd <scratchpad>
PY=/root/nanobot-venv/bin/python
S=~/.claude/skills/lumen-birthday/scripts/lumen_greeting.py
$PY $S avatar --out lumen_avatar.jpg                       # canonical Lumen face
$PY $S card --avatar lumen_avatar.jpg --out card.png \
     --style "<art direction from THEIR taste, e.g. Factory Records / neon-noir>" \
     --caption "«С ДНЁМ РОЖДЕНИЯ, ИМЯ»"                     # Cyrillic overlaid deterministically
```
The caption is drawn by PIL, not the model, so it is always correct. View the PNG and
`SendUserFile` it to Vova.

### 4. (optional) Download a taste-relevant video — yt-dlp
```bash
YT=/root/nanobot-venv/bin/yt-dlp
$YT "ytsearch5:<query from their taste>" --skip-download --no-warnings \
    --print "%(title)s | %(duration)s | %(channel)s | https://youtu.be/%(id)s"
# YouTube blocks most clients; player_client=android works:
$YT "<url>" --extractor-args "youtube:player_client=android" \
    -f "b[height<=720]/18/best" --merge-output-format mp4 -o clip.mp4
```
Keep it under ~45MB (Bot API sendVideo limit).

### 5. Get Vova's approval, then send (CLONE token, multi-bubble)
Write the ordered plan (Lumi texts in bubbles, media interleaved):
```bash
cat > plan.json <<'JSON'
[ {"kind":"text","text":"Имя, с днём рождения"},
  {"kind":"photo","path":"card.png"},
  {"kind":"text","text":"...короткая реплика..."},
  {"kind":"text","text":"...подводка к видео..."},
  {"kind":"video","path":"clip.mp4","caption":"..."},
  {"kind":"text","text":"...закрывашка..."} ]
JSON
/root/nanobot-venv/bin/python $S send --chat-id <ID> --plan plan.json   # prints message_ids
```

### 6. Record continuity + write the occasion to Honcho, then restart
```bash
printf '%s' "<the full greeting text, joined>" > greeting.txt
/root/nanobot-venv/bin/python $S remember --chat-id <ID> --text-file greeting.txt \
    --occasion "BIRTHDAY: <день месяц>"
systemctl restart nanobot-clone && systemctl is-active nanobot-clone
```
`remember` appends the greeting as an `is_nudge` assistant turn to the local session AND adds
the occasion to the Honcho peer card. The restart clears the SessionManager cache so the bot
re-reads the appended turn (a live append would be clobbered on the user's next reply otherwise).

### 7. Report with evidence
message_ids from step 5, the `before -> after` session count and peer-card diff from step 6,
and `systemctl is-active` = active. Evidence, not assertions.

## Gotchas (all fixed in the script — do not re-derive)
- nano-banana model id is `google/gemini-2.5-flash-image`; the `-preview` id 404s.
- Image models garble Cyrillic — the card caption is a deterministic PIL overlay (DejaVuSans-Bold).
- yt-dlp: `player_client=android` downloads when `android_vr`/`tv`/`ios` give 403 / "page needs reload".
- `OPENROUTER_API_KEY` is deep in the clone config; `HONCHO_API_KEY` is in the clone service env.
- The Lumen face for the card is the clone bot's own Telegram avatar (a glowing neon creature).

## Deliverables
- If Vova wants the card as a link: commit it into `piofant/nanobot-workspace`
  under `docs/assets/` with an explicit pathspec (parallel sessions live in that repo),
  push, and give the `github.com/.../blob/main/...` URL (repo is private → blob opens for the owner).
