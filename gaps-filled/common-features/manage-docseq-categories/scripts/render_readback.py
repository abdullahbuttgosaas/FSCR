"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 3 (2026-11-20).

Render a rest_read.py JSON file (before or after) into a PNG for evidence. Shows only the resource name,
the filter and the returned columns; no token, header, server address or user name. Needs Pillow.

Usage:
  python -B render_readback.py --json <readback.json> --title "After import" --png <out.png> [--note "..."] [--cols A,B,C]
"""
import argparse, json
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
    ap.add_argument("--json", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--png", required=True)
    ap.add_argument("--note", default="")
    ap.add_argument("--cols")
    a = ap.parse_args()
    d = json.load(open(a.json, encoding="utf-8"))
    items = d.get("items", [])
    cols = [c.strip() for c in a.cols.split(",")] if a.cols else (list(items[0].keys()) if items else [])
    lines = [a.title, "", f"REST GET {d.get('resource')} (read-only)", f"filter: {d.get('q') or '(none)'}",
             f"rows returned: {d.get('count')}", ""]
    if items:
        wid = {c: min(34, max(len(c), *(len(str(i.get(c))) for i in items)) + 2) for c in cols}
        lines.append("".join(f"{c:<{wid[c]}}" for c in cols))
        lines.append("-" * sum(wid.values()))
        for i in items[:40]:
            lines.append("".join(f"{str(i.get(c))[:wid[c]-2]:<{wid[c]}}" for c in cols))
    else:
        lines.append("(no rows: NOT FOUND)")
    if a.note:
        lines += ["", a.note]
    f, fb = font(18), font(22)
    w = 40 + max(int(f.getlength(l)) for l in lines)
    h = 40 + 30 * len(lines)
    img = Image.new("RGB", (max(w, 700), h), "white")
    dr = ImageDraw.Draw(img)
    for n, l in enumerate(lines):
        dr.text((20, 20 + 30 * n), l, fill="black", font=fb if n == 0 else f)
    img.save(a.png)
    print("wrote", a.png)


if __name__ == "__main__":
    main()
