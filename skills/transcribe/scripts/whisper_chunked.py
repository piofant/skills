#!/usr/bin/env python3
"""Whisper по кускам с детектором зацикливания и авто-перегоном битых кусков.

Зачем существует. whisper.cpp на файле длиннее ~20 минут уходит в петлю:
повторяет одну строку сотнями раз и дописывает несуществующие титры
(«Субтитры сделал DimaTorzok»). Ни --vad, ни -mc 0 это не лечат — проверено
на записи 126 мин: полный прогон дал 1949 повторов одной фразы, тот же кусок
в 200 секунд отдельным файлом — ноль повторов с любыми флагами.

Значит ломает длина. Скрипт режет вход на куски, гонит каждый как отдельный
файл, считает повторы внутри куска, залипшие перегоняет мельче и сшивает всё
обратно со сдвигом таймкодов.

Использование:
    python3 whisper_chunked.py <вход.wav> <выходная_папка> <имя> [--chunk 600] [--refix 150]

Вход должен быть уже нормализован (16 kHz mono) — см. шаг 1 в SKILL.md.
"""
import argparse, collections, os, subprocess, sys
from pathlib import Path

MODEL = os.path.expanduser("~/.cache/whisper/ggml-large-v3-turbo-q5_0.bin")
VAD   = os.path.expanduser("~/.cache/whisper/ggml-silero-v5.1.2.bin")
LOOP  = 0.25   # доля, которую занимает одна строка, чтобы счесть кусок залипшим


def parse_srt(p):
    out = []
    for b in Path(p).read_text(encoding="utf-8").strip().split("\n\n"):
        L = b.split("\n")
        if len(L) >= 3 and " --> " in L[1]:
            a, z = L[1].split(" --> ")
            out.append((a.strip(), z.strip(), " ".join(L[2:]).strip()))
    return out


def sec(t):
    h, m, r = t.split(":"); s, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def ts(x):
    return (f"{int(x//3600):02d}:{int(x%3600//60):02d}:"
            f"{int(x%60):02d},{int(round((x-int(x))*1000)):03d}")


def looped(texts):
    """Одна строка занимает больше четверти куска — это петля, а не речь."""
    if not texts:
        return False
    top = collections.Counter(texts).most_common(1)[0][1]
    return top > max(3, len(texts) * LOOP)


def run(src, off, length, work, tag, lang):
    """Гонит один кусок. Возвращает (сегменты со сдвигом, залип ли)."""
    wav, base = work / f"{tag}.wav", work / tag
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(off), "-t", str(length),
                    "-i", src, str(wav)], check=True)
    if wav.stat().st_size < 50_000:          # практически тишина
        return [], False
    subprocess.run(["whisper-cli", "-m", MODEL, "-f", str(wav), "-l", lang,
                    "--vad", "-vm", VAD, "-osrt", "-of", str(base)],
                   capture_output=True)
    srt = Path(str(base) + ".srt")
    if not srt.exists():
        return [], True
    part = parse_srt(srt)
    bad = looped([t for _, _, t in part])
    return [(sec(a) + off, sec(z) + off, t) for a, z, t in part], bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("outdir"); ap.add_argument("name")
    ap.add_argument("--chunk", type=int, default=600, help="длина куска, сек")
    ap.add_argument("--refix", type=int, default=150, help="длина при перегоне залипших")
    ap.add_argument("--lang", default="ru")
    a = ap.parse_args()

    for path, what in ((MODEL, "модель whisper"), (VAD, "модель VAD")):
        if not Path(path).exists():
            sys.exit(f"нет {what}: {path}")

    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    work = Path("/tmp") / f"wchunk_{a.name}"; work.mkdir(exist_ok=True)

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of", "csv=p=0", a.src],
                               capture_output=True, text=True).stdout.strip())
    n = int(dur // a.chunk) + 1
    print(f"{dur/60:.1f} мин → {n} кусков по {a.chunk//60} мин\n", flush=True)

    subs, bad = [], []
    for i in range(n):
        off = i * a.chunk
        part, loop = run(a.src, off, a.chunk, work, f"c{i:02d}", a.lang)
        subs += part
        if loop:
            bad.append(i)
        print(f"  кусок {i:02d}  {off//60:>3}–{min(off+a.chunk,int(dur))//60:>3} мин  "
              f"сегментов {len(part):>4}" + ("   ПЕТЛЯ" if loop else ""), flush=True)

    # залипшие перегоняем мельче
    for i in bad:
        lo, hi = i * a.chunk, (i + 1) * a.chunk
        subs = [s for s in subs if not (lo <= s[0] < hi)]
        print(f"\nперегон куска {i} по {a.refix} сек:", flush=True)
        for j in range(a.chunk // a.refix):
            off = lo + j * a.refix
            part, loop = run(a.src, off, a.refix, work, f"r{i}_{j}", a.lang)
            subs += part
            print(f"   {off//60:>3}:{off%60:02d}  сегментов {len(part):>3}"
                  + ("   ВСЁ ЕЩЁ ПЕТЛЯ" if loop else ""), flush=True)

    subs.sort(key=lambda x: x[0])
    with open(out / f"{a.name}.srt", "w", encoding="utf-8") as f:
        for k, (s, e, t) in enumerate(subs, 1):
            f.write(f"{k}\n{ts(s)} --> {ts(e)}\n{t}\n\n")
    with open(out / f"{a.name}.txt", "w", encoding="utf-8") as f:
        f.write(" ".join(t for _, _, t in subs))

    texts = [t for _, _, t in subs]
    words = len((out / f"{a.name}.txt").read_text(encoding="utf-8").split())
    print(f"\nслов {words}, сегментов {len(subs)}, уникальных {len(set(texts))}")
    print("частые строки:")
    for s, c in collections.Counter(texts).most_common(3):
        print(f"  {c:>4}×  {s[:60]}")
    if looped(texts):
        print("\nВНИМАНИЕ: петля осталась даже после перегона — уменьшить --refix")


if __name__ == "__main__":
    main()
