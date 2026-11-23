"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 1 (2026-11-20).

Offline compare of two unzipped standard-lookup exports (before / after) of the same task.
PASS = only the expected lookup type and codes were added; nothing removed; no existing row changed
(audit columns ignored). Standard library only (python -I).

Usage:
  python -I compare_lookup_exports.py <before unz> <after unz> --expect-type GAPFILL_XX_TYPE \
      --expect-code GAPFILL_A --expect-code GAPFILL_B
"""
import argparse, csv, sys
from pathlib import Path

TYPE_F, CODE_F = "FND_APP_STANDARD_LOOKUP.csv", "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv"
AUDIT = {"CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin"}


def load(d, f, keycols):
    with open(Path(d) / f, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {tuple(r[k] for k in keycols): {k: v for k, v in r.items() if k not in AUDIT} for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--expect-type", required=True)
    ap.add_argument("--expect-code", action="append", default=[])
    a = ap.parse_args()
    ok = True
    for f, keys, exp in ((TYPE_F, ["LookupType"], {(a.expect_type,)}),
                         (CODE_F, ["FND_APP_STANDARD_LOOKUP.LookupType", "LookupCode"],
                          {(a.expect_type, c) for c in a.expect_code})):
        b, af = load(a.before, f, keys), load(a.after, f, keys)
        added, removed = set(af) - set(b), set(b) - set(af)
        changed = [k for k in set(b) & set(af) if b[k] != af[k]]
        print(f"{f}: before {len(b)}, after {len(af)}, added {sorted(added)}, removed {len(removed)}, changed {len(changed)}")
        if added != exp or removed or changed:
            ok = False
            if added != exp:
                print("  expected added:", sorted(exp))
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
