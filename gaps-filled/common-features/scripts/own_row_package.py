"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 14 (2026-11-26). Offline: no Oracle call.

Build an FSM CSV package that UPDATES one of YOUR OWN records (a record whose key starts with your
prefix), for example the tax profile Oracle made for your own test legal entity. Every other CSV of the
export goes in with its header only; the metadata XML is copied unchanged.

Usage:
  python -I own_row_package.py --export-dir <unz> --file ZX_LEGAL_ENTITY_TAX_PROFILE.csv \
      --match LegalEntityIdentifier=GAPFILL_AB_B14_LE1 --prefix GAPFILL_ \
      --set RoundingRuleCode=NEAREST --set RoundingLevelCode=HEADER \
      [--clear-who] --out-dir <run>/payload --zip-name upd.zip

  --match   Col=Value. Exactly ONE row of --file must match, and Value must start with --prefix:
            the helper refuses to touch anybody else's record.
  --set     Col=Value. Columns to change (the column must exist in the file header).
  --clear-who  empty the who columns (CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate,
            LastUpdateLogin) so the import does not carry export audit values. Default: keep.
Prints the changed columns (old -> new). Never prints user names (who columns are not printed).
Writes UTF-8, no BOM, every field quoted, "\\n" line ends.
"""
import argparse, csv, shutil, sys, zipfile
from pathlib import Path

META = "ASM_SETUP_CSV_METADATA.xml"
WHO = ("CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin")


def read(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        return next(r, []), list(r)


def write(p, header, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--export-dir", required=True)
    a.add_argument("--file", required=True)
    a.add_argument("--match", required=True)
    a.add_argument("--prefix", required=True)
    a.add_argument("--set", action="append", default=[])
    a.add_argument("--clear-who", action="store_true")
    a.add_argument("--copy", action="append", default=[],
                   help="FILE.csv|Col=Value: also put this one row in UNCHANGED (for example your own parent "
                        "row in a hierarchical package). Value must start with --prefix.")
    a.add_argument("--out-dir", required=True)
    a.add_argument("--zip-name", required=True)
    o = a.parse_args()
    src, out = Path(o.export_dir), Path(o.out_dir)
    mcol, _, mval = o.match.partition("=")
    if not mval.startswith(o.prefix):
        sys.exit(f"refused: match value must start with {o.prefix}")
    header, rows = read(src / o.file)
    if mcol not in header:
        sys.exit(f"refused: column {mcol} not in {o.file}")
    hit = [r for r in rows if r[header.index(mcol)] == mval]
    if len(hit) != 1:
        sys.exit(f"refused: {len(hit)} rows match {mcol}={mval} (need exactly 1)")
    row = list(hit[0])
    for s in o.set:
        c, _, v = s.partition("=")
        if c not in header:
            sys.exit(f"refused: column {c} not in {o.file}")
        if c in WHO:
            sys.exit("refused: do not set who columns")
        i = header.index(c)
        print(f"{c}: '{row[i]}' -> '{v}'")
        row[i] = v
    if o.clear_who:
        for c in WHO:
            if c in header:
                row[header.index(c)] = ""
    extra = {}
    for c in o.copy:
        fname, _, cv = c.partition("|")
        cc, _, vv = cv.partition("=")
        if not vv.startswith(o.prefix):
            sys.exit(f"refused: --copy value must start with {o.prefix}")
        h2, r2 = read(src / fname)
        m = [r for r in r2 if cc in h2 and r[h2.index(cc)] == vv]
        if len(m) != 1:
            sys.exit(f"refused: {len(m)} rows match {cc}={vv} in {fname} (need exactly 1)")
        extra.setdefault(fname, []).append(m[0])
        print(f"copied unchanged: {fname} {cc}={vv}")
    out.mkdir(parents=True, exist_ok=True)
    stage = out / "stage"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    for p in sorted(src.glob("*.csv")):
        h, _ = read(p)
        write(stage / p.name, h, extra.get(p.name, []) + ([row] if p.name == o.file else []))
    shutil.copy(src / META, stage / META)
    z = out / o.zip_name
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(stage.iterdir()):
            zf.write(p, p.name)
    print(f"wrote {z} (1 row in {o.file}, other files header only)")


if __name__ == "__main__":
    main()
