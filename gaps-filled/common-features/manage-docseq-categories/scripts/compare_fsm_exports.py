"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 3 (2026-11-20). Offline: no Oracle call.

Compare an unzipped export taken BEFORE an import with one taken AFTER it, for any FSM CSV package.

Usage:
  python -I compare_fsm_exports.py <before unz> <after unz> \
      --key "FILE_A.csv=KeyCol" [--key "FILE_B.csv=Col1,Col2"] \
      --expect "FILE_A.csv=GAPFILL_X" [--expect "FILE_B.csv=GAPFILL_X,1" ...] [--rows-out added.csv]

  --key     key columns per file (files without --key are compared on the whole row).
  --expect  key value(s) (comma-separated, in --key order) you expect to be ADDED. Files you give no
            --expect for must show no additions.
Columns named Last* (LastUpdateDate, LastUpdatedBy, LastUpdateLogin) are ignored when checking "changed".
RESULT: PASS (exit 0) = exactly the expected rows added, none removed, no existing row changed.
"""
import argparse, csv, sys
from pathlib import Path


def load(d, f):
    p = Path(d) / f
    if not p.exists():
        return [], []
    with open(p, encoding="utf-8", newline="") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames or [], list(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--key", action="append", default=[])
    ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--rows-out")
    a = ap.parse_args()
    keys = {}
    for k in a.key:
        f, _, cols = k.partition("=")
        keys[f.strip()] = [c.strip() for c in cols.split(",")]
    exp = {}
    for e in a.expect:
        f, _, v = e.partition("=")
        exp.setdefault(f.strip(), set()).add(tuple(x.strip() for x in v.split(",")))
    files = sorted({p.name for p in Path(a.before).glob("*.csv")} | {p.name for p in Path(a.after).glob("*.csv")})
    ok, added_rows = True, []
    for f in files:
        hb, b = load(a.before, f)
        ha, n = load(a.after, f)
        cols = keys.get(f) or ha or hb
        kf = lambda r: tuple(r.get(c, "") for c in cols)
        cmpc = [c for c in (ha or hb) if not c.startswith("Last")]
        kb, kn = {kf(r): r for r in b}, {kf(r): r for r in n}
        added = sorted(set(kn) - set(kb))
        removed = sorted(set(kb) - set(kn))
        changed = [k for k in kb if k in kn and any(kb[k].get(c) != kn[k].get(c) for c in cmpc)]
        want = exp.get(f, set())
        fok = not removed and not changed and set(added) == want
        ok = ok and fok
        show = (lambda ks: [k if len(k) < 4 else k[:3] + ("...",) for k in ks])
        print(f"{f}: before {len(b)} after {len(n)} | added {show(added)} | removed {len(removed)} | changed {len(changed)} | {'ok' if fok else 'PROBLEM'}")
        if not fok and set(added) != want:
            print(f"   expected added: {sorted(want)}")
        for k in added:
            added_rows.append({"file": f, **kn[k]})
    if a.rows_out and added_rows:
        allc = ["file"] + sorted({c for r in added_rows for c in r if c != "file"})
        with open(a.rows_out, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=allc)
            w.writeheader()
            w.writerows(added_rows)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
