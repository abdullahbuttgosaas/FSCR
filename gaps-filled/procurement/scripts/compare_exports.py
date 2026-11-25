"""Added by GoSaaS, not part of official FSCR. Gap fill, Procurement, 2026-11-25. Offline: no Oracle call.

Compares two unzipped FSM task exports (before / after) file by file.
Rows are matched on --key FILE=COLUMN[+COLUMN] (default: the whole row).
Audit columns (CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin) are ignored
when deciding "changed". Prints added / removed / changed counts per file and the added keys.
RESULT: PASS when nothing was removed or changed and every --expect value is among the added keys.
Checks both folders hold a metadata XML first (a missing after-export gives false "removed" rows).

Usage: python -I compare_exports.py <before/unz> <after/unz> --key F.csv=Col [--expect F.csv=VALUE ...]
"""
import argparse
import csv
import sys
from pathlib import Path

AUDIT = {"CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin", "ObjectVersionNumber"}


def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        r = list(csv.reader(f))
    return (r[0], r[1:]) if r else ([], [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--key", action="append", default=[])
    ap.add_argument("--expect", action="append", default=[])
    a = ap.parse_args()
    b, f = Path(a.before), Path(a.after)
    for d in (b, f):
        if not (d / "ASM_SETUP_CSV_METADATA.xml").exists():
            print(f"RESULT: FAIL (no export in {d.name}: run the export again before comparing)")
            return 1
    keys = {}
    for k in a.key:
        fn, _, cols = k.partition("=")
        keys[fn] = cols.split("+")
    added_all = {}
    bad = False
    for p in sorted(f.glob("*.csv")):
        hb, rb = load(b / p.name) if (b / p.name).exists() else ([], [])
        ha, ra = load(p)
        cols = keys.get(p.name)
        def kf(h, r):
            return tuple(r[h.index(c)] for c in cols) if cols else tuple(r)
        def body(h, r):
            return tuple(v for c, v in zip(h, r) if c not in AUDIT)
        mb = {kf(hb, r): body(hb, r) for r in rb}
        ma = {kf(ha, r): body(ha, r) for r in ra}
        added = [k for k in ma if k not in mb]
        removed = [k for k in mb if k not in ma]
        changed = [k for k in ma if k in mb and ma[k] != mb[k] and hb == ha]
        added_all[p.name] = ["+".join(k) for k in added]
        print(f"{p.name}: before {len(rb)}, after {len(ra)}; added {len(added)}, removed {len(removed)}, changed {len(changed)}")
        for k in added[:10]:
            print("   added:", "+".join(k)[:120])
        if removed or changed:
            bad = True
            for k in (removed + changed)[:5]:
                print("   removed/changed:", "+".join(k)[:120])
    for e in a.expect:
        fn, _, v = e.partition("=")
        if not any(v == x or x.startswith(v + "+") or v in x.split("+") for x in added_all.get(fn, [])):
            print(f"   expected added {fn} {v}: NOT FOUND")
            bad = True
    print("RESULT:", "FAIL" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
