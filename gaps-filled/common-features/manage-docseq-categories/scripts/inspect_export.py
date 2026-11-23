"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 3 (2026-11-20). Offline: no Oracle call.

Show what an unzipped FSCR setup-task CSV export holds: every CSV, its column count and row count, and
(optionally) the distinct value combinations of some columns in one file. Use it to pick valid values
(for example a table name with its ApplicationId and ModuleId) from rows that already exist.

Usage:
  python -I inspect_export.py <unzipped export dir>
  python -I inspect_export.py <dir> --file FND_APP_DOCSEQ_CATEGORY.csv --cols TableName,ApplicationId,ModuleId
  python -I inspect_export.py <dir> --file X.csv --cols A,B --where "A=SOME VALUE" [--json-out rows.json]
--json-out writes the matching rows in the same JSON shape as rest_read.py, so render_readback.py can draw
an export-based read-back (for objects that have no REST resource).
"""
import argparse, collections, csv, sys
from pathlib import Path


def rows(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        h = next(r, [])
        return h, list(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--file")
    ap.add_argument("--cols")
    ap.add_argument("--where", action="append", default=[], help="Col=Value (exact)")
    ap.add_argument("--json-out", help="also write the matching rows (only --cols) to this JSON file")
    a = ap.parse_args()
    d = Path(a.dir)
    if not d.is_dir():
        sys.exit(f"STOP: {d} is not a folder")
    for p in sorted(d.glob("*")):
        if p.suffix.lower() == ".csv":
            h, r = rows(p)
            print(f"{p.name}: {len(h)} columns, {len(r)} rows")
        else:
            print(f"{p.name}")
    if a.file and a.cols:
        h, r = rows(d / a.file)
        cols = [c.strip() for c in a.cols.split(",")]
        for c in cols + [w.partition("=")[0] for w in a.where]:
            if c not in h:
                sys.exit(f"STOP: column {c!r} not in {a.file}. Columns: {', '.join(h)}")
        for w in a.where:
            c, _, v = w.partition("=")
            r = [x for x in r if x[h.index(c)] == v]
        cnt = collections.Counter(tuple(x[h.index(c)] for c in cols) for x in r)
        print(f"\nDistinct {', '.join(cols)} in {a.file} ({len(r)} rows):")
        for combo, n in cnt.most_common():
            print(f"  {n:>4}  " + " | ".join(combo))
        if a.json_out:
            import json
            items = [{c: x[h.index(c)] for c in cols} for x in r]
            json.dump({"resource": f"export file {a.file}", "q": " AND ".join(a.where) or None, "count": len(items),
                       "items": items}, open(a.json_out, "w", encoding="utf-8"), indent=2)
            print("wrote", a.json_out, "(same shape as rest_read.py output; render_readback.py can draw it)")


if __name__ == "__main__":
    main()
