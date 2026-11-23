"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 2 part 1 (2026-11-23). Offline: no Oracle call.

FSM setup-task packages are hierarchical: a child row (for example a profile VALUE) is only processed when
its parent row (the profile OPTION) is in the parent file of the same ZIP. When you add children to a
parent that already exists, copy the parent row UNCHANGED from the export into the payload, then re-zip.

Usage (after build_fsm_package.py has written <payload>):
  python -I copy_parent_rows.py --export-dir <RUN>/export_before/unz --payload-dir <RUN>/payload \
      --zip-name profile_value_new.zip --file FND_APP_PROFILE_OPTION.csv \
      --where ProfileOptionName=GAPFILL_X --where ApplicationId=0 [--prefix GAPFILL_]

- Exactly one export row must match all --where pairs, or it stops (no guessing).
- With --prefix, the parent's first --where value must start with that prefix (so you only ever touch
  your own test parents, never a seeded or shared one).
- The row is copied byte-for-byte in content (all columns, same header), every field quoted, UTF-8, "\n".
"""
import argparse, csv, sys, zipfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--payload-dir", required=True)
    ap.add_argument("--zip-name", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--where", action="append", required=True)
    ap.add_argument("--prefix")
    a = ap.parse_args()

    want = []
    for w in a.where:
        k, sep, v = w.partition("=")
        if not sep:
            sys.exit(f"STOP: bad --where {w!r}; use Col=Value")
        want.append((k.strip(), v.strip()))
    if a.prefix and not want[0][1].startswith(a.prefix):
        sys.exit(f"STOP: parent {want[0][1]!r} does not start with {a.prefix!r}; only copy your own test parents")

    src = Path(a.export_dir) / a.file
    dst = Path(a.payload_dir) / a.file
    with open(src, encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        head = next(r)
        rows = [x for x in r if all(x[head.index(k)] == v for k, v in want if k in head)]
    missing = [k for k, _ in want if k not in head]
    if missing:
        sys.exit(f"STOP: columns {missing} not in {a.file}")
    if len(rows) != 1:
        sys.exit(f"STOP: {len(rows)} rows in the export match {dict(want)}; need exactly 1")

    with open(dst, encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        phead = next(r)
        prows = list(r)
    if phead != head:
        sys.exit("STOP: payload header differs from the export header")
    if rows[0] in prows:
        sys.exit("STOP: that parent row is already in the payload")
    prows.append(rows[0])
    with open(dst, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(head)
        w.writerows(prows)

    pdir = Path(a.payload_dir)
    z = pdir / a.zip_name
    files = [p for p in sorted(pdir.iterdir()) if p.is_file() and p.suffix.lower() in (".csv", ".xml")]
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, p.name)
    print(f"{a.file}: copied 1 parent row unchanged ({dict(want)}); re-zipped {z} with {len(files)} files")


if __name__ == "__main__":
    main()
