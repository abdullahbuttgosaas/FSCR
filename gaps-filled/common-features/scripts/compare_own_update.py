"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 14 (2026-11-26). Offline: no Oracle call.

Prove that an import UPDATED only your own record: compare one CSV of an unzipped export taken
BEFORE the import with the same CSV of an export taken AFTER it.

Usage:
  python -I compare_own_update.py <before unz> <after unz> --file X.csv --key KeyCol[,KeyCol2] \
      --own GAPFILL_AB_B14_LE1 --expect RoundingRuleCode=NEAREST --expect RoundingLevelCode=LINE

RESULT: PASS (exit 0) = same row count, no row added or removed, no other row changed, and the own
row shows every --expect value. Who columns (Created*, LastUpdate*) and ObjectVersionNumber are ignored.
Prints only key values and column names / values of the own row (never who columns).
"""
import argparse, csv, sys
from pathlib import Path

IGN = ("CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin", "ObjectVersionNumber")


def load(d, f, keys):
    with open(Path(d) / f, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for r in rows:
        out.setdefault(tuple(r.get(k, "") for k in keys), []).append(r)
    return rows, out


def main():
    a = argparse.ArgumentParser()
    a.add_argument("before"); a.add_argument("after")
    a.add_argument("--file", required=True); a.add_argument("--key", required=True)
    a.add_argument("--own", required=True); a.add_argument("--expect", action="append", default=[])
    o = a.parse_args()
    keys = o.key.split(",")
    rb, b = load(o.before, o.file, keys)
    ra, af = load(o.after, o.file, keys)
    ok = True
    print(f"{o.file}: before {len(rb)} rows, after {len(ra)} rows")
    added = [k for k in af if k not in b]; removed = [k for k in b if k not in af]
    if added or removed:
        ok = False; print(f"added {added} removed {removed}")
    other = 0
    for k, rows in b.items():
        if k not in af or o.own in k:
            continue
        x = [{c: v for c, v in r.items() if not c.endswith(IGN)} for r in rows]
        y = [{c: v for c, v in r.items() if not c.endswith(IGN)} for r in af[k]]
        if x != y:
            other += 1
    print(f"other rows changed: {other}")
    ok = ok and other == 0
    own = [k for k in af if o.own in k]
    if len(own) != 1:
        print(f"own rows found: {len(own)} (need 1)"); ok = False
    else:
        old, new = b.get(own[0], [{}])[0], af[own[0]][0]
        diff = [c for c in new if not c.endswith(IGN) and new.get(c) != old.get(c)]
        print(f"own row {own[0]} changed columns: {diff}")
        for e in o.expect:
            c, _, v = e.partition("=")
            got = new.get(c)
            print(f"  {c} = '{got}' (expected '{v}')")
            ok = ok and got == v
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
