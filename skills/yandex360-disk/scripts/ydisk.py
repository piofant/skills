#!/usr/bin/env python3
"""Яндекс Диск через WebDAV. Только stdlib.

Пароль НИКОГДА не передаётся аргументом: Keychain, сервис yandex360-webdav,
account = полный адрес ящика. Алиасы ящиков — в ~/.config/yandex360/accounts.json
(карта «алиас → адрес», ключ default используется без --account).

Команды:
  ls [path]              содержимое папки
  tree [path] [--depth]  дерево на несколько уровней
  space                  сколько занято и свободно
  get <remote> [local]   скачать файл
  put <local> <remote>   загрузить файл
  mkdir <path>           создать папку
  find <подстрока>       поиск по именам, рекурсивно
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
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

BASE = "https://webdav.yandex.ru"
SERVICE = "yandex360-webdav"
ACCOUNTS_FILE = Path.home() / ".config/yandex360/accounts.json"


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
    pwd = os.environ.get("YANDEX360_WEBDAV_PASSWORD", "")
    if not pwd:
        try:
            pwd = subprocess.run(
                ["security", "find-generic-password", "-s", SERVICE, "-a", login, "-w"],
                capture_output=True, text=True, timeout=10, check=True).stdout.strip()
        except Exception:
            sys.exit(
                f"WebDAV-пароль для {login} не найден в Keychain.\n"
                "В Яндекс ID → Безопасность → Пароли приложений создай пароль\n"
                "именно под «Файлы · WebDAV» (почтовый сюда не подойдёт), затем:\n"
                f'  security add-generic-password -s {SERVICE} -a "{login}" -w')
    return login, pwd


# ── WebDAV ────────────────────────────────────────────────────────────────
def opener():
    # мимо сплит-прокси: ALL_PROXY из окружения роняет запрос к российским хостам
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def enc(path: str) -> str:
    p = "/" + path.strip("/") if path.strip("/") else "/"
    return urllib.parse.quote(p)


def request(login, pwd, path, method="PROPFIND", data=None, headers=None, raw=False):
    h = {"Authorization": "Basic " + base64.b64encode(f"{login}:{pwd}".encode()).decode()}
    h.update(headers or {})
    req = urllib.request.Request(BASE + enc(path), data=data, method=method, headers=h)
    try:
        r = opener().open(req, timeout=120)
        return r if raw else r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit("401 — пароль отвергнут. Проверь, что он создан под «Файлы · WebDAV».")
        if e.code == 404:
            sys.exit(f"404 — нет такого пути: {path}")
        sys.exit(f"HTTP {e.code}: {e.reason}")
    except Exception as e:
        sys.exit(f"{type(e).__name__}: {e}")


PROPS = ('<d:propfind xmlns:d="DAV:"><d:prop><d:displayname/><d:resourcetype/>'
         '<d:getcontentlength/><d:getlastmodified/></d:prop></d:propfind>')


def listdir(login, pwd, path, depth="1") -> list[dict]:
    xml = request(login, pwd, path, data=PROPS.encode(),
                  headers={"Depth": depth, "Content-Type": "application/xml; charset=utf-8"})
    out = []
    for block in re.split(r"</(?:D:|d:)?response>", xml):
        # Яндекс пишет теги с атрибутами (<href xmlns="DAV:">) — [^>]* обязателен
        href = re.search(r"<(?:D:|d:)?href[^>]*>([^<]+)</(?:D:|d:)?href>", block)
        if not href:
            continue
        p = urllib.parse.unquote(href.group(1))
        if p.rstrip("/") == ("/" + path.strip("/")).rstrip("/"):
            continue                       # сама папка, не содержимое
        size = re.search(r"<(?:D:|d:)?getcontentlength[^>]*>(\d+)<", block)
        mod = re.search(r"<(?:D:|d:)?getlastmodified[^>]*>([^<]+)<", block)
        try:
            when = parsedate_to_datetime(mod.group(1)).strftime("%d.%m.%Y %H:%M") if mod else "—"
        except Exception:
            when = "—"
        out.append({"path": p, "name": p.rstrip("/").split("/")[-1],
                    "dir": p.endswith("/"),
                    "size": int(size.group(1)) if size else 0, "mod": when})
    return sorted(out, key=lambda x: (not x["dir"], x["name"].lower()))


def human(n: int) -> str:
    for u in ("Б", "КБ", "МБ", "ГБ", "ТБ"):
        if n < 1024 or u == "ТБ":
            return f"{n:.0f} {u}" if u == "Б" else f"{n:.1f} {u}"
        n /= 1024
    return str(n)


# ── команды ───────────────────────────────────────────────────────────────
def cmd_ls(a, login, pwd):
    items = listdir(login, pwd, a.path)
    if not items:
        print("пусто")
        return
    for it in items:
        mark = "/" if it["dir"] else " "
        size = "—" if it["dir"] else human(it["size"])
        print(f"  {it['name'] + mark:<44} {size:>10}   {it['mod']}")
    d = sum(1 for i in items if i["dir"])
    print(f"\n{d} папок, {len(items) - d} файлов")


def cmd_tree(a, login, pwd):
    def walk(path, prefix, level):
        if level > a.depth:
            return
        for it in listdir(login, pwd, path):
            print(f"{prefix}{it['name']}{'/' if it['dir'] else ''}"
                  f"{'' if it['dir'] else '  ' + human(it['size'])}")
            if it["dir"]:
                walk(it["path"], prefix + "  ", level + 1)
    print(a.path or "/")
    walk(a.path, "  ", 1)


def cmd_space(a, login, pwd):
    xml = request(login, pwd, "/", data=(
        '<d:propfind xmlns:d="DAV:"><d:prop><d:quota-available-bytes/>'
        '<d:quota-used-bytes/></d:prop></d:propfind>').encode(),
        headers={"Depth": "0", "Content-Type": "application/xml; charset=utf-8"})
    used = re.search(r"quota-used-bytes[^>]*>(\d+)<", xml)
    free = re.search(r"quota-available-bytes[^>]*>(\d+)<", xml)
    u = int(used.group(1)) if used else 0
    f = int(free.group(1)) if free else 0
    print(f"  занято:   {human(u)}")
    print(f"  свободно: {human(f)}")
    if u + f:
        print(f"  всего:    {human(u + f)}  ({u / (u + f) * 100:.1f}% занято)")


def cmd_get(a, login, pwd):
    dest = Path(a.local or a.remote.rstrip("/").split("/")[-1])
    r = request(login, pwd, a.remote, method="GET", raw=True)
    data = r.read()
    dest.write_bytes(data)
    print(f"скачано: {dest}  ({human(len(data))})")


def cmd_put(a, login, pwd):
    src = Path(a.local)
    if not src.is_file():
        sys.exit(f"нет файла: {src}")
    data = src.read_bytes()
    remote = a.remote if not a.remote.endswith("/") else a.remote + src.name
    print(f"Загрузить {src}  ({human(len(data))})  →  Диск:{remote}")
    if not a.confirm:
        print("\nНЕ загружено. Перезапись на Диске необратима: покажи это пользователю,\n"
              "дождись «го» и повтори команду с --confirm.")
        return
    request(login, pwd, remote, method="PUT", data=data,
            headers={"Content-Type": "application/octet-stream"})
    print(f"✓ загружено: {remote}")


def cmd_mkdir(a, login, pwd):
    request(login, pwd, a.path, method="MKCOL")
    print(f"создана папка: {a.path}")


def cmd_find(a, login, pwd):
    hits, seen = [], 0

    def walk(path, level):
        nonlocal seen
        if level > a.depth:
            return
        for it in listdir(login, pwd, path):
            seen += 1
            if a.query.lower() in it["name"].lower():
                hits.append(it)
            if it["dir"]:
                walk(it["path"], level + 1)

    walk(a.path, 1)
    for it in hits:
        print(f"  {'📁' if it['dir'] else '📄'} {it['path']}"
              f"{'' if it['dir'] else '   ' + human(it['size'])}")
    print(f"\nнайдено {len(hits)} из {seen} просмотренных (глубина {a.depth})")


def main():
    p = argparse.ArgumentParser(description="Яндекс Диск через WebDAV")
    p.add_argument("--account", help="алиас ящика или полный адрес")
    sub = p.add_subparsers(dest="cmd", required=True)

    l = sub.add_parser("ls"); l.add_argument("path", nargs="?", default="/")
    t = sub.add_parser("tree"); t.add_argument("path", nargs="?", default="/")
    t.add_argument("--depth", type=int, default=2)
    sub.add_parser("space")
    g = sub.add_parser("get"); g.add_argument("remote"); g.add_argument("local", nargs="?")
    u = sub.add_parser("put"); u.add_argument("local"); u.add_argument("remote")
    u.add_argument("--confirm", action="store_true", help="реально загрузить")
    mk = sub.add_parser("mkdir"); mk.add_argument("path")
    f = sub.add_parser("find"); f.add_argument("query")
    f.add_argument("path", nargs="?", default="/"); f.add_argument("--depth", type=int, default=3)

    a = p.parse_args()
    login, pwd = creds(a.account)
    {"ls": cmd_ls, "tree": cmd_tree, "space": cmd_space, "get": cmd_get,
     "put": cmd_put, "mkdir": cmd_mkdir, "find": cmd_find}[a.cmd](a, login, pwd)


if __name__ == "__main__":
    main()
