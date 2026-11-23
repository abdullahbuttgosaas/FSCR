"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 3 (2026-11-20). Offline: no Oracle call.

Build an FSM setup-task CSV package that holds ONLY new rows, for any task whose export is a set of CSV
files plus ASM_SETUP_CSV_METADATA.xml. Layout (file names, headers, metadata XML) is copied from an
unzipped FSCR export of the same task. Every CSV of the export goes into the package; files you give no
rows for keep only their header row.

Usage:
  python -I build_fsm_package.py --export-dir <unz> --out-dir <run>/payload --zip-name new.zip \
      --prefix GAPFILL_ \
      --key "FILE_A.csv=KeyCol" --key "FILE_B.csv=ParentKeyCol,ChildCol" \
      --prefix-col "FILE_A.csv=KeyCol" --max-len "KeyCol=30" \
      --row "FILE_A.csv|KeyCol=GAPFILL_X|Description=Test row" \
      --row "FILE_B.csv|ParentKeyCol=GAPFILL_X|ChildCol=1"

  --row     "<file>|Col=Value|Col=Value...". Columns you do not name stay empty. Repeat for more rows.
  --key     key columns of a file. The builder refuses a row whose key already exists in the export
            (importing it would UPDATE that record) and refuses duplicate keys in the request.
  --prefix-col  columns that must start with --prefix.
  --max-len "Col=N" any column named Col (in any file) must be at most N characters.
  --max-rows    total new rows allowed (default 40).
Writes UTF-8, no BOM, every field quoted, "\\n" line ends (the shape that imported cleanly in our tests).
"""
import argparse, csv, shutil, sys, zipfile
from pathlib import Path

META = "ASM_SETUP_CSV_METADATA.xml"


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        h = next(r, [])
        return h, list(r)


def parse_map(items, what):
    out = {}
    for it in items:
        k, sep, v = it.partition("=")
        if not sep:
            sys.exit(f"STOP: bad {what} {it!r}; use Name=Value")
        out[k.strip()] = v.strip()
    return out


def main():
    ap = argparse.ArgumentParser(fromfile_prefix_chars="@")  # @file = read more arguments, one per line
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--zip-name", default="fsm_new_rows.zip")
    ap.add_argument("--prefix", default="GAPFILL_")
    ap.add_argument("--row", action="append", required=True)
    ap.add_argument("--key", action="append", default=[])
    ap.add_argument("--prefix-col", action="append", default=[])
    ap.add_argument("--max-len", action="append", default=[])
    ap.add_argument("--max-rows", type=int, default=40)
    a = ap.parse_args()

    src, out = Path(a.export_dir), Path(a.out_dir)
    if not (src / META).exists():
        sys.exit(f"STOP: {META} not in {src}. Unzip the export first; a package needs it unchanged.")
    files = sorted(p.name for p in src.glob("*.csv"))
    if not files:
        sys.exit("STOP: the export has no CSV files")
    heads, existing = {}, {}
    for f in files:
        heads[f], existing[f] = read(src / f)

    keys = {f: [c.strip() for c in cols.split(",")] for f, cols in parse_map(a.key, "--key").items()}
    pcols = {f: [c.strip() for c in cols.split(",")] for f, cols in parse_map(a.prefix_col, "--prefix-col").items()}
    maxlen = {c: int(n) for c, n in parse_map(a.max_len, "--max-len").items()}
    for f in list(keys) + list(pcols):
        if f not in heads:
            sys.exit(f"STOP: {f} is not a CSV in the export. Files: {', '.join(files)}")

    new = {f: [] for f in files}
    if len(a.row) > a.max_rows:
        sys.exit(f"STOP: {len(a.row)} rows > --max-rows {a.max_rows}")
    for spec in a.row:
        parts = spec.split("|")
        f = parts[0].strip()
        if f not in heads:
            sys.exit(f"STOP: {f!r} is not a CSV in the export. Files: {', '.join(files)}")
        vals = parse_map(parts[1:], "--row value")
        bad = [c for c in vals if c not in heads[f]]
        if bad:
            sys.exit(f"STOP: columns {bad} not in {f}. Columns: {', '.join(heads[f])}")
        for c, v in vals.items():
            if c in maxlen and len(v) > maxlen[c]:
                sys.exit(f"STOP: {c} longer than {maxlen[c]} characters: {v!r} ({len(v)})")
        for c in pcols.get(f, []):
            if not vals.get(c, "").startswith(a.prefix):
                sys.exit(f"STOP: {f} column {c} must start with {a.prefix}: {vals.get(c)!r}")
        new[f].append(vals)

    for f, cols in keys.items():
        for c in cols:
            if c not in heads[f]:
                sys.exit(f"STOP: key column {c} not in {f}")
        idx = [heads[f].index(c) for c in cols]
        have = {tuple(r[i].casefold() for i in idx) for r in existing[f]}
        seen = set()
        for v in new[f]:
            k = tuple(v.get(c, "").casefold() for c in cols)
            if not all(k):
                sys.exit(f"STOP: {f} row is missing a key column value {cols}: {v}")
            if k in have:
                sys.exit(f"STOP: {f} key {k} already exists in the export; importing it would UPDATE it. Pick a new name.")
            if k in seen:
                sys.exit(f"STOP: duplicate key {k} in your rows for {f}")
            seen.add(k)

    out.mkdir(parents=True, exist_ok=True)
    for f in files:
        with open(out / f, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writerow(heads[f])
            for v in new[f]:
                w.writerow([v.get(c, "") for c in heads[f]])
        print(f"{f}: {len(new[f])} new rows")
    shutil.copy(src / META, out / META)
    z = out / a.zip_name
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(out / META, META)
        for f in files:
            zf.write(out / f, f)
    print("wrote", z)


if __name__ == "__main__":
    main()
