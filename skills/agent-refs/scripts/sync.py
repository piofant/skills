#!/usr/bin/env python3
"""Клонирует или обновляет репозитории референсных агентов и показывает, что у них нового.

Использование:
  python3 sync.py            # обновить все; сколько нового с прошлого отчёта и насколько устарели карты
  python3 sync.py mia iva    # только выбранные
  python3 sync.py --news     # то же + список новых коммитов с прошлого отчёта; отметка отчёта сдвигается
  python3 sync.py --status   # без сети: где лежат копии, какой коммит, насколько устарели карты

Код референсов чужой: скрипт только клонирует и читает git, ничего из репозиториев не запускает.
"""
import fcntl
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REFS = SKILL_DIR / "refs.yaml"
STALE_COMMITS = 100
NET_TIMEOUT = 300
NAME_RX = re.compile(r"^[a-z0-9_-]+$")
REPO_RX = re.compile(r"^[\w.-]+/[\w.-]+$")
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "true"}


def _value(line):
    v = line.split(":", 1)[1].split(" #", 1)[0].strip()
    return v.strip("'\"")


def load_refs():
    """Минимальный разбор refs.yaml: cache_dir и у каждого агента name + repo."""
    cache, agents, cur = None, [], None
    for raw in REFS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0] if raw.lstrip().startswith("#") else raw
        s = line.strip()
        if s.startswith("cache_dir:"):
            cache = _value(s)
        elif s.startswith("- "):
            cur = {}
            agents.append(cur)
            s = s[2:].strip()
        if cur is not None and re.match(r"^(name|repo):", s):
            cur[s.split(":", 1)[0]] = _value(s)
    valid = []
    for a in agents:
        name, repo = a.get("name", ""), a.get("repo", "")
        if not NAME_RX.match(name) or not REPO_RX.match(repo):
            print(f"refs.yaml: пропускаю запись name={name!r} repo={repo!r} — неверный формат", file=sys.stderr)
            continue
        valid.append({"name": name, "repo": repo})
    return Path(os.path.expanduser(cache or "~/.cache/agent-refs")), valid


def git(cwd, *args, check=True, timeout=60):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=GIT_ENV, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def has_commit(dest, sha):
    return subprocess.run(["git", "-C", str(dest), "cat-file", "-e", f"{sha}^{{commit}}"],
                          capture_output=True, env=GIT_ENV).returncode == 0


def map_sha(name):
    path = SKILL_DIR / "references" / f"{name}.md"
    if not path.exists():
        return None
    m = re.search(r"Снято с коммита:\s*`?([0-9a-f]{7,40})", path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def map_lag(dest, sha):
    if not sha:
        return "карты нет — собрать по references/map-prompt.md"
    if not has_commit(dest, sha):
        return f"коммит карты {sha} не найден в копии — сверять пути грепом, карту пересобрать"
    n = int(git(dest, "rev-list", "--count", f"{sha}..HEAD"))
    flag = " — ПОРА ОБНОВИТЬ КАРТУ" if n >= STALE_COMMITS else ""
    return f"карта отстаёт на {n} коммитов{flag}"


def update(dest, repo):
    url = f"https://github.com/{repo}"
    if not dest.exists():
        subprocess.run(["git", "clone", "-q", url, str(dest)], check=True, env=GIT_ENV, timeout=NET_TIMEOUT)
        return
    git(dest, "remote", "set-url", "origin", url)
    head_ref = git(dest, "ls-remote", "--symref", "origin", "HEAD", timeout=NET_TIMEOUT)
    m = re.search(r"ref: refs/heads/(\S+)\s+HEAD", head_ref)
    if not m:
        raise RuntimeError("не удалось узнать ветку по умолчанию (репозиторий удалён или закрыт?)")
    branch = m.group(1)
    fetch = ["fetch", "-q", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}"]
    if git(dest, "rev-parse", "--is-shallow-repository") == "true":
        fetch.insert(2, "--unshallow")
    git(dest, *fetch, timeout=NET_TIMEOUT)
    git(dest, "reset", "-q", "--hard", f"origin/{branch}")


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    status_only = "--status" in sys.argv
    news = "--news" in sys.argv
    cache, agents = load_refs()
    unknown = set(names) - {a["name"] for a in agents}
    if unknown:
        print(f"нет в refs.yaml: {', '.join(sorted(unknown))}", file=sys.stderr)
    cache.mkdir(parents=True, exist_ok=True)
    lock = open(cache / ".lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)  # две сессии не синхронизируют одновременно

    state_path = cache / ".state.json"
    try:
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
    except (ValueError, OSError):
        print("состояние .state.json повреждено — начинаю заново", file=sys.stderr)
        state = {}

    for a in agents:
        if names and a["name"] not in names:
            continue
        dest = cache / a["name"]
        print(f"\n## {a['name']} ({a['repo']}) → {dest}")
        try:
            if status_only and not dest.exists():
                print("  нет копии — запусти без --status")
                continue
            if not status_only:
                update(dest, a["repo"])
            head = git(dest, "rev-parse", "--short", "HEAD")
            print(f"  HEAD {head} от {git(dest, 'log', '-1', '--format=%cs')}")
            reported = state.get(a["name"], {}).get("reported") if isinstance(state.get(a["name"]), dict) else None
            if reported and reported != head:
                if not has_commit(dest, reported):
                    print(f"  коммит прошлого отчёта {reported} не найден (история переписана?)")
                else:
                    lines = git(dest, "log", "--format=  %h %cs %s", f"{reported}..HEAD").splitlines()
                    print(f"  нового с прошлого отчёта: {len(lines)} коммитов" + ("" if news else " (список — с --news)"))
                    if news:
                        for line in lines[:30]:
                            print(line)
                        if len(lines) > 30:
                            print(f"  … ещё {len(lines) - 30}: git -C {dest} log {reported}..HEAD")
            elif reported == head:
                print("  нового с прошлого отчёта нет")
            print(f"  {map_lag(dest, map_sha(a['name']))}")
            if news or not reported:
                state[a["name"]] = {"reported": head}
        except subprocess.TimeoutExpired:
            print("  ОШИБКА: git не ответил вовремя (сеть?)")
        except Exception as e:  # сеть, удалённый или переименованный репозиторий
            print(f"  ОШИБКА: {e}")

    state_path.write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
