#!/usr/bin/env python3
"""Шаблон разовой рассылки ВСЕМ юзерам Люмена через клон-бота.
СКОПИРУЙ в scratchpad, впиши TEXT, прогони dry-run, покажи Вове, по «го» — --send.

  dry-run:  python3 template_broadcast.py
  send:     python3 template_broadcast.py --send   # ТОЛЬКО после явного «го»

Правила: web-preview off; только клон-токен (не личный ТГ Вовы); dry-run первым.
"""
import argparse, html, json, re, time, pathlib, urllib.request, urllib.parse

CLONE_TOKEN = "8737890560:AAECFG1bwaC9A34LbvxCawxJhhOVEXIbiQY"  # @lumen_charecter_bot (Stable)
BASE = pathlib.Path("/root/lumen-trendwatch-broadcast")
MATCHING = BASE / "matching.json"
BLOCKLIST = BASE / "blocklist.txt"

# ── ВПИШИ СВОЙ ТЕКСТ ЗДЕСЬ ──────────────────────────────────────────────
# HTML. Гиперссылка в слове:  <a href="URL">слово</a>. Обычный текст экранируй
# (& < >) — но НЕ ломай теги ссылок. lumen.yandex.ru и т.п. можно оставить голым
# текстом (preview всё равно off).
_JOIN = "https://messenger.360.yandex.ru/#/join/EXAMPLE"
TEXT = (
    "Привет! Пример анонса.\n\n"
    f'Пишите фидбек <a href="{_JOIN}">в чате</a>'
)
# ────────────────────────────────────────────────────────────────────────


def recipients():
    mj = json.loads(MATCHING.read_text(encoding="utf-8"))
    block = set()
    if BLOCKLIST.exists():
        block = {x.strip().lstrip("@") for x in BLOCKLIST.read_text().splitlines() if x.strip()}
    out, seen = [], set()
    for m in mj:
        un = (m.get("username") or "?").lstrip("@")
        d = re.search(r"(\d{6,})", str(m.get("peer_id", "")))
        if not d or un in block or d.group(1) in seen:
            continue
        seen.add(d.group(1))
        out.append((un, d.group(1)))
    return out


def send(cid, text):
    data = urllib.parse.urlencode({
        "chat_id": cid, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    url = f"https://api.telegram.org/bot{CLONE_TOKEN}/sendMessage"
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true")
    a = ap.parse_args()
    rcpts = recipients()

    if not a.send:
        print("=== DRY-RUN — НЕ отправлено ===")
        print(f"получателей: {len(rcpts)}\n")
        print("--- как увидит юзер (HTML, preview off) ---")
        print(TEXT)
        print("\n--- первые 8 адресатов ---")
        for un, cid in rcpts[:8]:
            print(f"  @{un}  ({cid})")
        print("\nПокажи Вове. Отправка ТОЛЬКО после явного «го»: --send")
        return

    ok = blocked = no_dialog = other = 0
    blk, nod = [], []
    for un, cid in rcpts:
        try:
            r = send(cid, TEXT)
            if r.get("ok"):
                ok += 1
            else:
                other += 1
        except urllib.error.HTTPError as e:
            desc = ""
            try:
                desc = json.loads(e.read()).get("description", "")
            except Exception:
                pass
            if "blocked" in desc or e.code == 403:
                blocked += 1; blk.append(un)
            elif "chat not found" in desc:
                no_dialog += 1; nod.append(un)
            else:
                other += 1
        except Exception:
            other += 1
        time.sleep(0.4)
    print(f"\n=== ОТПРАВЛЕНО: {ok} · заблокировали(403): {blocked} · "
          f"нет диалога(400): {no_dialog} · прочее: {other} (из {len(rcpts)}) ===")
    if blk: print(f"  заблокировали бота: {', '.join('@'+u for u in blk)}")
    if nod: print(f"  нет диалога (не блок): {', '.join('@'+u for u in nod)}")


if __name__ == "__main__":
    main()
