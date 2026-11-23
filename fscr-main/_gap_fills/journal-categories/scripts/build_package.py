"""Added by GoSaaS, not part of official FSCR. Origin: Run 24, ETIA-TEST.
Build a journal-category CSV package that holds ONLY new rows.
Reads the layout (columns + metadata XML) from an unzipped FSCR export of the same task.
Makes no Oracle call.

Usage:
  python -I build_package.py --export-dir <unzipped export folder> --out-dir <run folder>/payload \
      --row "FSCRT_RunNN Accrual|FSCR test category for accrual journals. Run NN." [--row ...] [--zip-name x.zip]
"""
import argparse, csv, sys, zipfile, shutil
from pathlib import Path

DEF, TR, META = "GL_JOURNAL_CATEGORY_DEF.csv", "GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv", "ASM_SETUP_CSV_METADATA.xml"
MAX_NAME, PREFIX, MAX_ROWS = 25, "FSCRT_", 3

def read_rows(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.reader(f); h = next(r); return h, list(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--row", action="append", required=True, help='"Name|Description"')
    ap.add_argument("--zip-name", default="gl_journal_categories_new.zip")
    ap.add_argument("--prefix", default=PREFIX)
    ap.add_argument("--max-rows", type=int, default=MAX_ROWS)
    a = ap.parse_args()
    src, out = Path(a.export_dir), Path(a.out_dir)
    for n in (DEF, TR, META):
        if not (src / n).exists(): sys.exit(f"Missing {n} in export folder (a package needs all 3 files).")
    rows = []
    for item in a.row:
        name, _, desc = item.partition("|"); name, desc = name.strip(), desc.strip()
        rows.append((name, desc))
    if len(rows) > a.max_rows: sys.exit(f"Too many rows ({len(rows)} > {a.max_rows}).")
    names = [n for n, _ in rows]
    if len(set(n.casefold() for n in names)) != len(names): sys.exit("Duplicate names in request.")
    for n in names:
        if not n.startswith(a.prefix): sys.exit(f"Name must start with {a.prefix}: {n!r}")
        if len(n) > MAX_NAME: sys.exit(f"Name longer than {MAX_NAME} characters: {n!r} ({len(n)})")
    hdef, exist = read_rows(src / DEF)
    existing = {r[hdef.index("JeCategoryName")].casefold() for r in exist}
    clash = [n for n in names if n.casefold() in existing]
    if clash: sys.exit(f"Already exist in the export, refusing (would update): {clash}")
    htr, _ = read_rows(src / TR)
    out.mkdir(parents=True, exist_ok=True)
    def write(name, header, dicts):
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(header)
            for d in dicts: w.writerow([d.get(c, "") for c in header])
    write(DEF, hdef, [dict(JeCategoryName=n, UserJeCategoryName=n, JeCategoryKey=n, Description=d) for n, d in rows])
    write(TR, htr, [{"GL_JOURNAL_CATEGORY_DEF.JeCategoryName": n, "JeCategoryName": n, "UserJeCategoryName": n,
                     "Language": "US", "SourceLang": "US", "Description": d} for n, d in rows])
    shutil.copy(src / META, out / META)
    z = out / a.zip_name
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in (META, DEF, TR): zf.write(out / n, n)
    print("wrote", z)

if __name__ == "__main__":
    main()
