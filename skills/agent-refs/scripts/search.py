#!/usr/bin/env python3
"""Ищет фичу сразу во всех референсных агентах: в коде и в истории коммитов.

Использование:
  python3 search.py 'remind|напомин|schedule'            # код: топ файлов по совпадениям в каждом репо
  python3 search.py 'remind|напомин' --log                 # + коммиты по теме (заголовок и первая строка тела)
  python3 search.py 'remind|напомин' --log --fix --no-tests # только fix-коммиты, код без тестов
  python3 search.py 'reply_to|mention' --only mia,osinara  # только выбранные
  python3 search.py 'dedup' --top 15 --show 3              # больше файлов, по 3 строки-примера на файл
  python3 search.py -- '-flag'                              # шаблон, начинающийся с минуса

Шаблон — регулярное выражение (Python re, без учёта регистра). Вендорные и сгенерированные
каталоги пропускаются. Код референсов только читается.
"""
import argparse
import os
import re
import sys
import subprocess
from pathlib import Path

from sync import git_env, load_refs

SKIP_DIRS = {".git", ".agents", ".claude", ".codex", "node_modules", "dist", "build", "coverage", ".next", "vendor", "__pycache__",
             ".venv", "venv", ".turbo", ".cache", "out"}
SKIP_FILES = re.compile(r"(\.lock$|lock\.json$|lock\.yaml$|\.min\.js$|\.map$|\.(png|jpe?g|gif|webp|ico|svg|pdf|woff2?|ttf|mp3|ogg|wav|mp4|zip|gz|sqlite|db)$)", re.I)
MAX_BYTES = 400_000


def walk(root):
    # Символические ссылки пропускаем: чужой репозиторий может сослаться на ~/.bashrc или ключи.
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            p = Path(dirpath) / f
            if p.is_symlink() or SKIP_FILES.search(f):
                continue
            try:
                if p.is_file() and p.stat().st_size <= MAX_BYTES:
                    yield p
            except OSError:
                continue


TEST_RX = re.compile(r"(^|/)(tests?|__tests__|e2e|fixtures|stress)(/|$)|[._-](test|spec)\.[a-z]+$|(^|/)(test_[^/]+|tests\.py|conftest\.py)$", re.I)
FIX_RX = r"^(fix|hotfix|revert|bugfix)\b|исправ|почин|чиню|чиним|не теря|не пропада|не дубл|не застрев"


def search_code(root, rx, top, show, no_tests=False):
    hits = []
    for p in walk(root):
        if no_tests and TEST_RX.search(str(p.relative_to(root))):
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        found = [(i + 1, l.strip()[:160]) for i, l in enumerate(lines) if rx.search(l)]
        if found:
            hits.append((len(found), str(p.relative_to(root)), found[:show]))
    hits.sort(key=lambda h: (-h[0], h[1]))
    return hits[:top], len(hits)


def search_log(root, pattern, limit=20, fix=False):
    """Коммиты, где шаблон встречается в заголовке или теле. Сначала Perl-регулярки (как у Python re),
    если git собран без PCRE — POSIX ERE."""
    for flag in ("--perl-regexp", "--extended-regexp"):
        r = subprocess.run(
            ["git", "-C", str(root), "log", "--no-merges", "-i", flag, f"--grep={pattern}",
             "--format=%x1e%h %cs %s%x1f%b", f"-n{limit * (5 if fix else 1)}"],
            capture_output=True, text=True, env=git_env(root.parent), timeout=60,
        )
        if r.returncode == 0:
            out = []
            for rec in r.stdout.split("\x1e"):
                if not rec.strip():
                    continue
                head, _, body = rec.partition("\x1f")
                head = head.strip()
                body = next((l.strip() for l in body.splitlines() if l.strip()), "")[:140]
                subject = head.split(" ", 2)[-1]
                if fix and not re.search(FIX_RX, subject, re.I):
                    continue
                out.append(head + (f"\n        {body}" if body else ""))
            return out[:limit], None
        err = r.stderr.strip().splitlines()[-1:] or ["?"]
    return [], err[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("--only", default="")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--show", type=int, default=1)
    ap.add_argument("--log", action="store_true", help="добавить коммиты по теме")
    ap.add_argument("--fix", action="store_true", help="с --log: только исправления, без релизов и слияний")
    ap.add_argument("--no-tests", action="store_true", help="не искать в тестах и фикстурах")
    a = ap.parse_args()
    try:
        rx = re.compile(a.pattern, re.I)
    except re.error as e:
        sys.exit(f"неверная регулярка {a.pattern!r}: {e}")
    if a.fix and not a.log:
        a.log = True  # --fix имеет смысл только для истории коммитов
    only = {x for x in a.only.split(",") if x}
    cache, agents = load_refs()
    for ag in agents:
        if only and ag["name"] not in only:
            continue
        root = cache / ag["name"]
        if not (root / ".git").is_dir():
            print(f"\n## {ag['name']}: нет копии — запусти scripts/sync.py")
            continue
        hits, total = search_code(root, rx, a.top, a.show, a.no_tests)
        print(f"\n## {ag['name']} — файлов с совпадениями: {total}")
        for n, path, sample in hits:
            print(f"  {n:4d}  {path}")
            for ln, text in sample:
                print(f"        :{ln}  {text}")
        if a.log:
            commits, err = search_log(root, a.pattern, fix=a.fix)
            if err:
                print(f"  коммиты: git не понял шаблон ({err})")
            shallow = subprocess.run(["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
                                     capture_output=True, text=True, env=git_env(root.parent)).stdout.strip() == "true"
            note = " — история обрезана, запусти sync.py" if shallow else ""
            print(f"  коммиты по теме ({len(commits)}, показан заголовок; текст — git show <sha>){note}:")
            for c in commits:
                print(f"    {c}")


if __name__ == "__main__":
    main()
