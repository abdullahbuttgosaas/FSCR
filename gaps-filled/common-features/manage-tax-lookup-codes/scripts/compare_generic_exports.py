"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 2 (2026-11-20).

Offline compare of two unzipped Financials generic lookup exports (before / after) of the same task.
PASS = nothing removed, no existing row changed (audit columns ignored), and every added row belongs to
--expect-type (rows of other types added between the two exports are listed as FAIL so a person can look).
Because the export is scoped (it may not list new TYPES, only codes, or nothing), the added rows are
reported, and --require-codes makes the expected codes mandatory. Standard library only (python -I).

Usage:
  python -I compare_generic_exports.py <before unz> <after unz> --expect-type GAPFILL_XX [--require-codes GAPFILL_XX_A ...]
"""
import argparse, csv, sys
from pathlib import Path

AUDIT = {"CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin", "ChangeSinceLastRefresh"}
FILES = {
    "ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv": ["LookupType", "ViewApplicationId"],
    "ORA_FINANCIALS_GENERIC_LOOKUP_TYPE_TRANSLATION.csv": ["LookupType", "ViewApplicationId", "Language"],
    "FUN_APP_GENERIC_LOOKUP.csv": ["LookupType", "LookupCode", "ViewApplicationId", "SetCode"],
    "FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv": ["FUN_APP_GENERIC_LOOKUP.LookupType", "LookupCode",
                                               "FUN_APP_GENERIC_LOOKUP.SetCode", "Language"],
}


def load(d, f, keycols):
    with open(Path(d) / f, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {tuple(r.get(k, "") for k in keycols): {k: v for k, v in r.items() if k not in AUDIT} for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--expect-type", required=True)
    ap.add_argument("--require-codes", nargs="*", default=[])
    a = ap.parse_args()
    ok = True
    added_codes = set()
    for f, keys in FILES.items():
        b, af = load(a.before, f, keys), load(a.after, f, keys)
        added, removed = set(af) - set(b), set(b) - set(af)
        changed = [k for k in set(b) & set(af) if b[k] != af[k]]
        foreign = [k for k in added if k[0] != a.expect_type]
        print(f"{f}: before {len(b)}, after {len(af)}, added {sorted(added)}, removed {len(removed)}, changed {len(changed)}")
        if f == "FUN_APP_GENERIC_LOOKUP.csv":
            added_codes = {k[1] for k in added if k[0] == a.expect_type}
        if removed or changed or foreign:
            ok = False
            if foreign:
                print("  rows of another type were added (someone else's change?):", sorted(foreign))
    missing = set(a.require_codes) - added_codes
    if missing:
        ok = False
        print("  expected codes not in the after export:", sorted(missing))
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
