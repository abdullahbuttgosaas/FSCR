"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 2 (2026-11-20).

Render a read_generic_lookup.py JSON (before or after) into a PNG for evidence. Shows only lookup type,
meanings, codes, sets and flags; no token, header, URL, server or user name. Needs Pillow (run without -I).

Usage:
  python -B render_readback.py --json <readback.json> --title "After import" --png <out.png> [--note "..."]
"""
import argparse, json
from PIL import Image, ImageDraw, ImageFont

RES = {"set-enabled": "setEnabledLookups", "standard": "standardLookups"}


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
    a = ap.parse_args()
    d = json.load(open(a.json, encoding="utf-8"))
    if "found_in" in d:
        lines = [a.title, "", "REST GET setEnabledLookups / standardLookups / commonLookups /{LookupType} (read-only)", "",
                 f"LookupType: {d.get('LookupType')}",
                 "Result: " + ("FOUND in " + ", ".join(d["found_in"]) if d.get("found") else "NOT FOUND (HTTP 404 in all three)")]
    else:
        lines = [a.title, "", f"REST GET {RES.get(d.get('view'), '?')}/{{LookupType}}?expand=lookupCodes (read-only)", ""]
        if not d.get("found"):
            lines += [f"LookupType: {d.get('LookupType')}", "Result: NOT FOUND (HTTP 404)"]
        else:
            lines += [f"LookupType: {d['LookupType']}", f"Meaning:    {d['Meaning']}",
                      f"Description: {d.get('Description') or ''}", f"Level:      {d.get('CustomizationLevel')}",
                      f"Ref group:  {d.get('ReferenceGroupName') or '-'}", "",
                      f"{'LookupCode':<24}{'Meaning':<32}{'Set':<10}{'Enabled':<9}Seq", "-" * 80]
            for c in d.get("lookupCodes", []):
                lines.append(f"{str(c['LookupCode']):<24}{str(c['Meaning'])[:30]:<32}{str(c.get('SetCode') or '-'):<10}"
                             f"{str(c['EnabledFlag']):<9}{c['DisplaySequence']}")
    if a.note:
        lines += ["", a.note]
    f, fb = font(18), font(22)
    w = 40 + max(int(f.getlength(l)) for l in lines)
    h = 40 + 30 * len(lines)
    img = Image.new("RGB", (max(w, 700), h), "white")
    dr = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        dr.text((20, 20 + 30 * i), l, fill="black", font=fb if i == 0 else f)
    img.save(a.png)
    print("wrote", a.png)


if __name__ == "__main__":
    main()
