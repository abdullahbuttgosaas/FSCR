"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 3 part 1 (2026-11-23). Offline: no Oracle call.

Render a plain text file (or stdin) into a PNG for evidence images (01_missing ... 05_fresh_test).
Write only safe text into it: no tokens, headers, server addresses or user names. Needs Pillow,
so run it WITHOUT python -I (Pillow is in the user site-packages on Windows).

Usage:
  python -B text_png.py --title "Test result (live): <TASK_CODE>" --in notes.txt --png 04_test_result.png [--width 1400]
"""
import argparse, sys
from PIL import Image, ImageDraw, ImageFont


def font(size):
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "Menlo.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--in", dest="inp")
    ap.add_argument("--png", required=True)
    ap.add_argument("--width", type=int, default=1400)
    a = ap.parse_args()
    text = open(a.inp, encoding="utf-8").read() if a.inp else sys.stdin.read()
    f, ft = font(15), font(19)
    cw = max(8, int(f.getlength("M")))
    maxc = (a.width - 40) // cw
    lines = []
    for ln in text.splitlines():
        while len(ln) > maxc:
            lines.append(ln[:maxc]); ln = "    " + ln[maxc:]
        lines.append(ln)
    h = 70 + 22 * len(lines) + 20
    img = Image.new("RGB", (a.width, h), "white")
    d = ImageDraw.Draw(img)
    d.text((20, 18), a.title, fill="black", font=ft)
    for i, ln in enumerate(lines):
        d.text((20, 62 + 22 * i), ln, fill="black", font=f)
    img.save(a.png)
    print(f"wrote {a.png} ({a.width}x{h})")


if __name__ == "__main__":
    main()
