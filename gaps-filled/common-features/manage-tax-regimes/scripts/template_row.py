"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 2 part 3 (2026-11-23). Offline: no Oracle call.

Turn ONE existing row of an FSM export CSV into a "--row" argument for build_fsm_package.py, so a new
record can copy every setting of a known-good record and change only its key, name and dates.

Usage:
  python -I template_row.py --export-dir <RUN>/export_before/unz --file ZX_TAX_REGIME.csv \
     --match "TaxRegimeCode=<existing code>" \
     --set "TaxRegimeCode=<NEW>" --set "TaxRegimeName=<new name>" --set "EffectiveFrom=2026/01/01" \
     [--clear EffectiveTo] [--keep-audit] --out <RUN>/rows_regime.txt [--append]
Then: build_fsm_package.py ... @<RUN>/rows_regime.txt

Rules:
- --match must select exactly one row (several --match are ANDed); otherwise STOP.
- Audit columns (CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin) are left empty
  unless --keep-audit. Empty source values stay empty. --clear empties more columns.
- Every --set column must exist in the file; --set may give a value to a column that was empty.
- Prints only the column names it wrote, never the values (rows may hold internal ids).
"""
import argparse, csv, sys
from pathlib import Path

AUDIT = {"CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin"}


def kv(s):
    if "=" not in s:
        sys.exit(f"STOP: expected Column=Value, got {s!r}")
    k, v = s.split("=", 1)
    return k.strip(), v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--match", action="append", required=True)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--clear", action="append", default=[])
    ap.add_argument("--keep-audit", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--append", action="store_true")
    a = ap.parse_args()
    path = Path(a.export_dir) / a.file
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    cols = list(rows[0].keys()) if rows else []
    match = [kv(m) for m in a.match]
    for k, _ in match:
        if k not in cols:
            sys.exit(f"STOP: --match column {k} not in {a.file}")
    hits = [r for r in rows if all(r.get(k) == v for k, v in match)]
    if len(hits) != 1:
        sys.exit(f"STOP: --match selected {len(hits)} rows in {a.file}; need exactly 1")
    row = dict(hits[0])
    if not a.keep_audit:
        for c in AUDIT & set(cols):
            row[c] = ""
    for c in a.clear:
        if c not in cols:
            sys.exit(f"STOP: --clear column {c} not in {a.file}")
        row[c] = ""
    for s in a.set:
        k, v = kv(s)
        if k not in cols:
            sys.exit(f"STOP: --set column {k} not in {a.file}")
        row[k] = v
    for k, v in row.items():
        if "|" in v:
            sys.exit(f"STOP: value of {k} holds '|', which the builder uses as separator")
    parts = [f"{k}={v}" for k, v in row.items() if v != ""]
    text = "--row\n" + a.file + "|" + "|".join(parts) + "\n"
    out = Path(a.out)
    with open(out, "a" if a.append else "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote 1 row for {a.file} to {out} ({len(parts)} columns: {', '.join(k for k, v in row.items() if v != '')})")


if __name__ == "__main__":
    main()
