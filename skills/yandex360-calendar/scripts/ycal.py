#!/usr/bin/env python3
"""Личный Яндекс Календарь через CalDAV. Только stdlib.

Пароль НИКОГДА не передаётся аргументом: Keychain, сервис yandex360-caldav,
account = полный адрес ящика. Алиасы ящиков — в ~/.config/yandex360/accounts.json
(карта «алиас → адрес», ключ default используется без --account).

Команды:
  calendars                      список календарей
  events [--days N] [--past N]   события в диапазоне (по умолчанию 7 дней вперёд)
  today                          события на сегодня
  week                           события на 7 дней
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = "https://caldav.yandex.ru"
SERVICE = "yandex360-caldav"
ACCOUNTS_FILE = Path.home() / ".config/yandex360/accounts.json"
LOCAL_TZ = ZoneInfo("Europe/Moscow")


# ── учётка ────────────────────────────────────────────────────────────────
def load_accounts() -> dict:
    if ACCOUNTS_FILE.is_file():
        try:
            return json.loads(ACCOUNTS_FILE.read_text())
        except Exception:
            pass
    single = os.environ.get("YANDEX360_LOGIN", "")
    return {"default": single} if single else {}


def resolve_login(account: str | None) -> str:
    accs = load_accounts()
    if not accs:
        sys.exit("Ящики не заведены. Создай ~/.config/yandex360/accounts.json вида\n"
                 '  {"личный": "you@yandex.ru", "работа": "you@your-domain.ru"}')
    if not account:
        if "default" in accs:
            return accs["default"]
        if len(accs) == 1:
            return next(iter(accs.values()))
        sys.exit(f"Несколько ящиков — укажи --account: {', '.join(accs)}")
    if account in accs:
        return accs[account]
    if "@" in account:
        return account
    sys.exit(f"Алиас '{account}' неизвестен. Есть: {', '.join(accs)}")


def creds(account: str | None) -> tuple[str, str]:
    login = resolve_login(account)
    pwd = os.environ.get("YANDEX360_CALDAV_PASSWORD", "")
    if not pwd:
        try:
            pwd = subprocess.run(
                ["security", "find-generic-password", "-s", SERVICE, "-a", login, "-w"],
                capture_output=True, text=True, timeout=10, check=True).stdout.strip()
        except Exception:
            sys.exit(
                f"CalDAV-пароль для {login} не найден в Keychain.\n"
                "В Яндекс ID → Безопасность → Пароли приложений создай пароль\n"
                "именно под «Календарь · CalDAV» (почтовый пароль сюда не подойдёт), затем:\n"
                f'  security add-generic-password -s {SERVICE} -a "{login}" -w')
    return login, pwd


# ── DAV ───────────────────────────────────────────────────────────────────
def dav(login, pwd, path, body, depth="0", method="PROPFIND") -> str:
    auth = base64.b64encode(f"{login}:{pwd}".encode()).decode()
    req = urllib.request.Request(
        BASE + path, data=body.encode("utf-8"), method=method,
        headers={"Authorization": f"Basic {auth}", "Depth": depth,
                 "Content-Type": "application/xml; charset=utf-8"})
    # мимо сплит-прокси: ALL_PROXY из окружения роняет запрос к российским хостам
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        return op.open(req, timeout=30).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit("401 — пароль отвергнут. Проверь, что он создан под «Календарь · CalDAV».")
        sys.exit(f"HTTP {e.code}: {e.reason}")
    except Exception as e:
        sys.exit(f"{type(e).__name__}: {e}")


def home(login: str) -> str:
    return f"/calendars/{urllib.parse.quote(login)}/"


def calendars(login, pwd) -> list[tuple[str, str]]:
    """[(href, displayname)] — только коллекции типа VEVENT."""
    xml = dav(login, pwd, home(login),
              '<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">'
              '<d:prop><d:displayname/><d:resourcetype/>'
              '<c:supported-calendar-component-set/></d:prop></d:propfind>', depth="1")
    out = []
    for block in re.split(r"</D:response>|</response>", xml):
        # Яндекс пишет <href xmlns="DAV:"> — тег с атрибутом, [^>]* обязателен
        href = re.search(r"<(?:D:)?href[^>]*>([^<]+)</(?:D:)?href>", block)
        if not href or "calendar" not in block.lower():
            continue
        h = urllib.parse.unquote(href.group(1))
        if h.rstrip("/") == home(login).rstrip("/"):
            continue
        if 'name="VEVENT"' not in block:
            continue
        name = re.search(r"<(?:D:)?displayname>([^<]*)</(?:D:)?displayname>", block)
        out.append((href.group(1), (name.group(1) if name else h.strip("/").split("/")[-1])))
    return out


# ── iCalendar ─────────────────────────────────────────────────────────────
def unfold(text: str) -> list[str]:
    """RFC 5545: строка, начинающаяся с пробела/таба, продолжает предыдущую."""
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def ical_dt(value: str, params: str):
    """Вернёт (datetime, весь_день?) в локальной зоне."""
    tz = LOCAL_TZ
    m = re.search(r"TZID=([^;:]+)", params)
    if m:
        try:
            tz = ZoneInfo(m.group(1))
        except Exception:
            pass
    v = value.strip()
    try:
        if v.endswith("Z"):
            return datetime.strptime(v, "%Y%m%dT%H%M%SZ").replace(
                tzinfo=timezone.utc).astimezone(LOCAL_TZ), False
        if "T" in v:
            return datetime.strptime(v, "%Y%m%dT%H%M%S").replace(
                tzinfo=tz).astimezone(LOCAL_TZ), False
        return datetime.strptime(v, "%Y%m%d").replace(tzinfo=LOCAL_TZ), True
    except ValueError:
        return None, False


def parse_events(ics: str) -> list[dict]:
    ev, cur = [], None
    for line in unfold(ics):
        if line.startswith("BEGIN:VEVENT"):
            cur = {}
            continue
        if line.startswith("END:VEVENT"):
            if cur:
                ev.append(cur)
            cur = None
            continue
        if cur is None or ":" not in line:
            continue
        head, _, val = line.partition(":")
        key, _, params = head.partition(";")
        key = key.upper()
        val = val.replace("\\,", ",").replace("\\n", " ").replace("\\;", ";")
        if key in ("DTSTART", "DTEND"):
            dt, allday = ical_dt(val, params)
            cur[key] = dt
            cur["ALLDAY"] = cur.get("ALLDAY") or allday
        elif key in ("SUMMARY", "LOCATION", "DESCRIPTION", "STATUS", "ORGANIZER", "URL"):
            cur[key] = val
    return ev


def fetch_events(login, pwd, href, start: datetime, end: datetime) -> list[dict]:
    body = ('<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">'
            '<d:prop><c:calendar-data/></d:prop><c:filter>'
            '<c:comp-filter name="VCALENDAR"><c:comp-filter name="VEVENT">'
            f'<c:time-range start="{start.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}" '
            f'end="{end.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}"/>'
            '</c:comp-filter></c:comp-filter></c:filter></c:calendar-query>')
    path = href if href.startswith("/") else "/" + href
    xml = dav(login, pwd, path, body, depth="1", method="REPORT")
    out = []
    for blob in re.findall(r"<(?:C:|c:)?calendar-data[^>]*>(.*?)</(?:C:|c:)?calendar-data>",
                           xml, re.S):
        import html
        out.extend(parse_events(html.unescape(blob)))
    return out


# ── команды ───────────────────────────────────────────────────────────────
def cmd_calendars(a, login, pwd):
    cals = calendars(login, pwd)
    if not cals:
        print("календарей не найдено")
        return
    for href, name in cals:
        print(f"  {name:<34} {urllib.parse.unquote(href)}")


def cmd_events(a, login, pwd):
    now = datetime.now(LOCAL_TZ)
    start = (now - timedelta(days=a.past)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=a.past + a.days)
    print(f"# {start:%d.%m} — {end:%d.%m.%Y}\n")
    rows = []
    for href, name in calendars(login, pwd):
        for e in fetch_events(login, pwd, href, start, end):
            if e.get("DTSTART"):
                rows.append((e["DTSTART"], name, e))
    if not rows:
        print("событий нет")
        return
    rows.sort(key=lambda r: r[0])
    day = None
    for dt, cal, e in rows:
        d = dt.strftime("%d.%m %a")
        if d != day:
            day, = (d,)
            print(f"\n## {d}")
        when = "весь день" if e.get("ALLDAY") else (
            f"{dt:%H:%M}" + (f"–{e['DTEND']:%H:%M}" if e.get("DTEND") else ""))
        line = f"  {when:<13} {e.get('SUMMARY', '(без названия)')}"
        if e.get("LOCATION"):
            line += f"   📍 {e['LOCATION'][:40]}"
        print(line)
        if a.verbose and e.get("DESCRIPTION"):
            print(f"                {e['DESCRIPTION'][:200]}")


def main():
    p = argparse.ArgumentParser(description="Яндекс Календарь через CalDAV")
    p.add_argument("--account", help="алиас ящика или полный адрес")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("calendars")
    for name, days in (("events", 7), ("today", 1), ("week", 7)):
        sp = sub.add_parser(name)
        sp.add_argument("--days", type=int, default=days)
        sp.add_argument("--past", type=int, default=0, help="сколько дней назад захватить")
        sp.add_argument("--verbose", action="store_true", help="показывать описания")

    a = p.parse_args()
    login, pwd = creds(a.account)
    (cmd_calendars if a.cmd == "calendars" else cmd_events)(a, login, pwd)


if __name__ == "__main__":
    main()
