"""Added by GoSaaS, not part of official FSCR. Gap fill, Procurement, 2026-11-25. Offline: no Oracle call.

Builds an FSM setup-task CSV import ZIP that holds ONLY new rows, from a read-only task export.

- Copies ASM_SETUP_CSV_METADATA.xml from the export unchanged.
- For every CSV file you give rows for, writes the export's header and your rows only
  (every field quoted, UTF-8, no BOM). Columns you do not give stay empty.
- CSV files of the export that get no rows are written with the header only (so the
  package keeps every file of the export), unless --only is used.
- Refuses a row whose key value (--key FILE=COLUMN) is already in the export
  (that row would UPDATE an existing record), and a key that does not start with --prefix.

Usage:
  python -I build_csv_package.py --export-dir <RUN>/export_before/unz --out <RUN>/payload/new.zip \
     --prefix GAPFILL_AB_ \
     --key ORA_PO_SPECIAL_HANDLING.csv=SpecialHandlingTypeCode \
     --row "ORA_PO_SPECIAL_HANDLING.csv|SpecialHandlingTypeCode=GAPFILL_AB_X1|SpecialHandlingType=GAPFILL AB X1|EnabledFlag=Y" \
     [--row ...] [--only]
A row is: FILE|Column=value|Column=value ... (a value may contain '=' but not '|').
Prints the files, row counts and the ZIP path. Never prints user names (the metadata XML is copied, not read).
"""
import argparse
import csv
import io
import sys
import zipfile
from pathlib import Path


def read_csv(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        r = list(csv.reader(f))
    return (r[0], r[1:]) if r else ([], [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--key", action="append", default=[], help="FILE=COLUMN that must be new and start with the prefix")
    ap.add_argument("--new", action="append", default=[], help="FILE=COLUMN that must be new (no prefix check), e.g. a GUID-style code")
    ap.add_argument("--row", action="append", default=[])
    ap.add_argument("--copy-row", action="append", default=[],
                    help="FILE|Column=value: copy the export row whose Column has this value UNCHANGED (a parent row)")
    ap.add_argument("--edit-row", action="append", default=[],
                    help="FILE|KeyCol=value[&KeyCol2=value]|Col=new|...: copy the ONE export row matching the key(s), change only "
                         "the named columns, empty the audit columns (for test-and-restore of an existing row)")
    ap.add_argument("--only", action="store_true", help="write only the CSV files that get rows")
    a = ap.parse_args()

    ex = Path(a.export_dir)
    meta = ex / "ASM_SETUP_CSV_METADATA.xml"
    if not meta.exists():
        sys.exit("STOP: no ASM_SETUP_CSV_METADATA.xml in the export folder")
    files = {p.name: read_csv(p) for p in sorted(ex.glob("*.csv"))}

    keys = {}
    for k in a.key:
        fn, _, col = k.partition("=")
        keys.setdefault(fn, []).append(col)

    new = {fn: [] for fn in files}
    for spec in a.copy_row:
        fn, _, cond = spec.partition("|")
        col, _, val = cond.partition("=")
        head, rows = files[fn]
        hit = [r for r in rows if r[head.index(col)] == val]
        if len(hit) != 1:
            sys.exit(f"STOP: --copy-row {fn} {col}={val}: found {len(hit)} rows, need exactly 1")
        new[fn].append(list(hit[0]))

    audit = {"CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin"}
    for spec in a.edit_row:
        parts = spec.split("|")
        fn = parts[0]
        head, rows = files[fn]
        conds = [c.partition("=")[::2] for c in parts[1].split("&")]  # KeyCol=v or KeyCol=v&Col2=v2
        for c, _ in conds:
            if c not in head:
                sys.exit(f"STOP: key column {c!r} is not in {fn}")
        kc, kv = "&".join(c for c, _ in conds), "&".join(v for _, v in conds)
        hit = [r for r in rows if all(r[head.index(c)] == v for c, v in conds)]
        if len(hit) != 1:
            sys.exit(f"STOP: --edit-row {fn} {kc}={kv}: found {len(hit)} rows, need exactly 1")
        row = list(hit[0])
        for p in parts[2:]:
            c, sep, v = p.partition("=")
            if not sep or c not in head:
                sys.exit(f"STOP: column {c!r} is not in {fn}")
            print(f"{fn} {kc}={kv}: {c} {row[head.index(c)]!r} -> {v!r}")
            row[head.index(c)] = v
        for c in audit & set(head):
            row[head.index(c)] = ""
        new[fn].append(row)

    for spec in a.row:
        parts = spec.split("|")
        fn = parts[0]
        if fn not in files:
            sys.exit(f"STOP: {fn} is not a CSV of the export ({', '.join(files)})")
        head, rows = files[fn]
        vals = {}
        for p in parts[1:]:
            c, sep, v = p.partition("=")
            if not sep or c not in head:
                sys.exit(f"STOP: column {c!r} is not in {fn}")
            vals[c] = v
        for col in keys.get(fn, []):
            v = vals.get(col, "")
            if not v.startswith(a.prefix):
                sys.exit(f"STOP: {fn} {col}={v!r} does not start with {a.prefix}")
            if any(r[head.index(col)] == v for r in rows):
                sys.exit(f"STOP: {fn} {col}={v} is already in the export: importing it would UPDATE it")
        for k in a.new:
            kfn, _, col = k.partition("=")
            if kfn == fn and vals.get(col) and any(r[head.index(col)] == vals[col] for r in rows):
                sys.exit(f"STOP: {fn} {col}={vals[col]} is already in the export: importing it would UPDATE it")
        new[fn].append([vals.get(c, "") for c in head])

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(meta, meta.name)
        for fn, (head, _) in files.items():
            if a.only and not new[fn]:
                continue
            buf = io.StringIO()
            w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writerow(head)
            w.writerows(new[fn])
            z.writestr(fn, buf.getvalue().encode("utf-8"))
            print(f"{fn}: {len(new[fn])} row(s)")
    print(f"ZIP: {out}")


if __name__ == "__main__":
    main()
