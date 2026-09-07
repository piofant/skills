#!/usr/bin/env python3
"""lumen_greeting — operator toolkit for sending a personalized proactive
greeting (birthday/milestone) to a Lumen user THROUGH the bot, not from
Vova's account.

Run with the clone venv so nanobot + PIL + requests import cleanly:
    /root/nanobot-venv/bin/python lumen_greeting.py <subcommand> ...

Subcommands
  avatar   Fetch the clone bot's own avatar (canonical Lumen face) via Bot API.
  card     Generate a greeting card via OpenRouter nano-banana using the avatar
           as an image reference, then overlay a correct Cyrillic caption (image
           models garble Cyrillic — the overlay is deterministic).
  send     Deliver an ordered plan of bubbles (text / photo / video) via the
           clone bot token. Prints message_ids. This is the outbound action.
  remember Record the greeting as an assistant turn in the user's local session
           (so the bot has continuity on their reply) AND add the occasion to
           their Honcho peer card. After this: restart the clone.

Paths are clone-specific (this is Vova's VPS). Override via flags/env if needed.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

CLONE_HOME = os.environ.get("LUMEN_CLONE_HOME", "/root/nanobot-clone-home")
CLONE_CONFIG = f"{CLONE_HOME}/.nanobot/config.json"
CLONE_SERVICE = os.environ.get("LUMEN_CLONE_SERVICE", "nanobot-clone")


# ── config helpers ───────────────────────────────────────────────────
def _config() -> dict:
    return json.load(open(CLONE_CONFIG))


def _bot_token() -> str:
    return _config()["channels"]["telegram"]["token"]


def _find_key(obj, name: str):
    """Deep-search a nested dict/list for a key (OPENROUTER_API_KEY lives in an
    mcp env block, not top level)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == name and isinstance(v, str) and v.strip():
                return v.strip()
            r = _find_key(v, name)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_key(v, name)
            if r:
                return r
    return None


def _openrouter_key() -> str:
    k = _find_key(_config(), "OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not k:
        sys.exit("OPENROUTER_API_KEY not found in clone config or env")
    return k


def _service_env() -> dict:
    """Pull the clone service environment (HONCHO_API_KEY etc.) without printing."""
    out = subprocess.run(
        ["systemctl", "show", CLONE_SERVICE, "-p", "Environment", "--value"],
        capture_output=True, text=True,
    ).stdout.strip()
    env = {}
    for tok in shlex.split(out):
        if "=" in tok:
            k, v = tok.split("=", 1)
            env[k] = v
    return env


# ── telegram Bot API ─────────────────────────────────────────────────
def _api(method: str, files=None, **data):
    import requests
    r = requests.post(f"https://api.telegram.org/bot{_bot_token()}/{method}",
                      data=data, files=files, timeout=120)
    return r.json()


def cmd_avatar(a):
    """Download the clone bot's profile photo — the canonical Lumen face."""
    me = _api("getMe")["result"]
    print(f"bot: @{me.get('username')} · {me.get('first_name')} · id {me.get('id')}")
    ph = _api("getUserProfilePhotos", user_id=me["id"], limit=1)["result"]
    if not ph.get("total_count"):
        sys.exit("bot has no avatar set")
    big = max(ph["photos"][0], key=lambda s: s["width"])
    f = _api("getFile", file_id=big["file_id"])["result"]
    import requests
    url = f"https://api.telegram.org/file/bot{_bot_token()}/{f['file_path']}"
    Path(a.out).write_bytes(requests.get(url, timeout=60).content)
    print(f"saved {a.out}  ({big['width']}x{big['height']})")


# ── card generation (nano-banana + deterministic Cyrillic overlay) ────
NANO_MODELS = [
    "google/gemini-2.5-flash-image",            # GA (works)
    "google/gemini-2.5-flash-image:free",
    "google/gemini-2.5-flash-image-preview",    # legacy id — often 404
]


def cmd_card(a):
    import requests
    key = _openrouter_key()
    avatar_b64 = base64.b64encode(Path(a.avatar).read_bytes()).decode()
    style = a.style or (
        "moody neon, minimal, elegant, high-contrast, tasteful, not childish"
    )
    prompt = (
        "Create a greeting card (vertical portrait poster). "
        "Feature the glowing creature from the reference image as the central hero, "
        "keeping its exact glowing-neon style on a deep black background. "
        f"Art direction: {style}. "
        "Add a small tasteful birthday/celebration cue (a single candle or a neon spark). "
        "Leave the bottom third clean and empty — a caption is added later; "
        "do NOT render any Cyrillic text yourself. No watermark, no clutter."
    )
    body = {
        "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{avatar_b64}"}},
        ]}],
    }
    saved_art = None
    for model in NANO_MODELS:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                          headers={"Authorization": f"Bearer {key}"},
                          json={"model": model, **body}, timeout=180)
        if r.status_code != 200:
            print(f"  {model}: {r.status_code} {r.text[:120]}")
            continue
        imgs = r.json()["choices"][0]["message"].get("images") or []
        if not imgs:
            print(f"  {model}: no image in response")
            continue
        b64 = imgs[0]["image_url"]["url"].split(",", 1)[1]
        saved_art = Path(a.out)
        saved_art.write_bytes(base64.b64decode(b64))
        print(f"  art via {model}")
        break
    if saved_art is None:
        sys.exit("all nano-banana models failed")
    if a.caption:
        _overlay_caption(a.out, a.caption)
    print(f"saved {a.out}")


def _overlay_caption(path: str, caption: str):
    """Cover the bottom band and render correct Cyrillic with a neon glow.
    DejaVuSans-Bold (matplotlib) supports Cyrillic."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import glob
    import matplotlib
    font_path = glob.glob(os.path.join(
        os.path.dirname(matplotlib.__file__),
        "mpl-data", "fonts", "ttf", "DejaVuSans-Bold.ttf"))[0]
    im = Image.open(path).convert("RGBA")
    W, H = im.size
    px = im.load()
    import statistics as st
    samples = [px[10, H - 15], px[W - 10, H - 15], px[10, 15], px[W - 10, 15]]
    bg = tuple(int(st.mean(c[i] for c in samples)) for i in range(3)) + (255,)
    d = ImageDraw.Draw(im)
    top, bot = int(H * 0.795), int(H * 0.935)
    d.rectangle([0, top, W, bot], fill=bg)
    size = 64
    while size > 20:
        f = ImageFont.truetype(font_path, size)
        bb = d.textbbox((0, 0), caption, font=f)
        if bb[2] - bb[0] <= int(W * 0.80):
            break
        size -= 2
    f = ImageFont.truetype(font_path, size)
    bb = d.textbbox((0, 0), caption, font=f)
    x = W // 2 - (bb[2] - bb[0]) // 2 - bb[0]
    y = (top + bot) // 2 - (bb[3] - bb[1]) // 2 - bb[1]
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((x, y), caption, font=f, fill=(80, 210, 235, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(7))
    im = Image.alpha_composite(im, glow)
    im = Image.alpha_composite(im, glow)
    ImageDraw.Draw(im).text((x, y), caption, font=f, fill=(111, 216, 230, 255))
    im.convert("RGB").save(path, "PNG")


# ── send an ordered plan ─────────────────────────────────────────────
def cmd_send(a):
    plan = json.load(open(a.plan)) if a.plan != "-" else json.load(sys.stdin)
    chat = str(a.chat_id)
    results = []
    for i, step in enumerate(plan):
        kind = step["kind"]
        if kind == "text":
            j = _api("sendMessage", chat_id=chat, text=step["text"])
        elif kind == "photo":
            with open(step["path"], "rb") as fh:
                j = _api("sendPhoto", files={"photo": fh}, chat_id=chat,
                         **({"caption": step["caption"]} if step.get("caption") else {}))
        elif kind == "video":
            with open(step["path"], "rb") as fh:
                j = _api("sendVideo", files={"video": fh}, chat_id=chat,
                         supports_streaming="true",
                         **({"caption": step["caption"]} if step.get("caption") else {}))
        else:
            sys.exit(f"unknown step kind: {kind}")
        ok = j.get("ok")
        mid = j.get("result", {}).get("message_id") if ok else None
        results.append((kind, ok, mid, None if ok else j.get("description")))
        print(f"[{i}] {kind}: ok={ok} id={mid} {'' if ok else j.get('description')}")
        time.sleep(a.delay)
    okc = sum(1 for r in results if r[1])
    print(f"\n{okc}/{len(results)} delivered")
    if okc != len(results):
        sys.exit("some sends failed — see above")


# ── record continuity + write occasion to Honcho ─────────────────────
def cmd_remember(a):
    # 1) local session assistant turn (continuity on the user's next reply)
    os.environ["HOME"] = CLONE_HOME
    sys.path.insert(0, "/root/nanobot-honcho")
    from nanobot.session.manager import SessionManager
    sm = SessionManager(Path(f"{CLONE_HOME}/.nanobot/workspace"))
    key = f"telegram:{a.chat_id}"
    s = sm.get_or_create(key)
    before = len(s.messages)
    text = Path(a.text_file).read_text()
    s.add_message("assistant", text, is_nudge=True, proactive=True, topic=a.topic)
    sm.save(s)
    print(f"session {key}: {before} -> {len(s.messages)} (is_nudge)")

    # 2) Honcho peer card occasion (e.g. 'BIRTHDAY: 2 сентября')
    if a.occasion:
        for k, v in _service_env().items():
            os.environ.setdefault(k, v)
        from nanobot.honcho.client import get_honcho_client
        from nanobot.honcho.peer_card import dedup_and_set_card
        peer = get_honcho_client().peer(f"user-telegram-{a.chat_id}")
        cur = peer.get_card() or []
        added = dedup_and_set_card(peer, list(cur) + [a.occasion])
        print(f"peer card: +{added} -> {peer.get_card()}")
    print(f"\nNOW RESTART THE CLONE:  systemctl restart {CLONE_SERVICE}")


def main():
    p = argparse.ArgumentParser(description="Lumen greeting operator toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("avatar"); s.add_argument("--out", default="lumen_avatar.jpg"); s.set_defaults(fn=cmd_avatar)
    s = sub.add_parser("card")
    s.add_argument("--avatar", required=True)
    s.add_argument("--caption", default="", help="Cyrillic caption overlaid deterministically, e.g. «С ДНЁМ РОЖДЕНИЯ, ИМЯ»")
    s.add_argument("--style", default="", help="art direction from the user's taste (Honcho card)")
    s.add_argument("--out", default="card.png"); s.set_defaults(fn=cmd_card)
    s = sub.add_parser("send")
    s.add_argument("--chat-id", required=True)
    s.add_argument("--plan", required=True, help="JSON file (or '-') of [{kind:text|photo|video, ...}]")
    s.add_argument("--delay", type=float, default=0.9); s.set_defaults(fn=cmd_send)
    s = sub.add_parser("remember")
    s.add_argument("--chat-id", required=True)
    s.add_argument("--text-file", required=True, help="the greeting text (what Lumi 'said')")
    s.add_argument("--occasion", default="", help="peer-card entry, e.g. 'BIRTHDAY: 2 сентября'")
    s.add_argument("--topic", default="birthday-greeting"); s.set_defaults(fn=cmd_remember)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
