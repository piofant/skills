#!/usr/bin/env python3
"""Качает аудио по ссылке и нормализует его под расшифровку.

Существует из-за одной грабли: в окружении живёт сплит-прокси
(all_proxy=socks5://127.0.0.1:1080), и он душит RU-домены. yt-dlp падает на
этапе получения метаданных с 'Read timed out', хотя ссылка в браузере открывается.
Лечится снятием прокси-переменных плюс --proxy "".

Проверено 05.09.2026 на rutube (467 фрагментов HLS, 31 мин, скачалось за пару минут).

Использование:
    python3 fetch.py <url> <имя> [--keep-video]

На выходе:
    /tmp/<имя>.mp3        исходное аудио
    /tmp/<имя>_norm.wav   16 kHz mono, нормализованное — его и скармливать
                          whisper_chunked.py из скилла transcribe
"""
import argparse, os, subprocess, sys
from pathlib import Path

PROXY_VARS = ["http_proxy", "https_proxy", "all_proxy",
              "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "no_proxy", "NO_PROXY"]


def clean_env():
    """Окружение без прокси — иначе RU-домены отваливаются по таймауту."""
    env = os.environ.copy()
    for v in PROXY_VARS:
        env.pop(v, None)
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("name")
    ap.add_argument("--keep-video", action="store_true",
                    help="не удалять исходный контейнер после извлечения аудио")
    a = ap.parse_args()

    mp3 = Path(f"/tmp/{a.name}.mp3")
    wav = Path(f"/tmp/{a.name}_norm.wav")

    print(f"качаю {a.url}", flush=True)
    r = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--no-warnings", "--proxy", "",
         "-f", "ba/b", "-x", "--audio-format", "mp3",
         "-o", f"/tmp/{a.name}.%(ext)s", a.url],
        env=clean_env(), capture_output=True, text=True)

    if not mp3.exists():
        tail = (r.stderr or r.stdout or "")[-600:]
        sys.exit(f"не скачалось.\n{tail}")

    print(f"аудио: {mp3.stat().st_size/1024/1024:.1f} МБ", flush=True)

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3),
                    "-ar", "16000", "-ac", "1",
                    "-af", "highpass=f=80,dynaudnorm=f=150:g=15", str(wav)],
                   check=True)

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(wav)],
        capture_output=True, text=True).stdout.strip())

    if not a.keep_video:
        for ext in (".mp4", ".webm", ".m4a"):
            Path(f"/tmp/{a.name}{ext}").unlink(missing_ok=True)

    print(f"\nготово: {wav}  ({int(dur//60)} мин {int(dur%60)} сек)")
    print("дальше:")
    print(f"  python3 ~/.claude/skills/transcribe/scripts/whisper_chunked.py \\")
    print(f"    {wav} <куда> {a.name} --chunk 480")


if __name__ == "__main__":
    main()
