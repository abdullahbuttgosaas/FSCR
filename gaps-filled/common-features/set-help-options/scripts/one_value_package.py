"""Build a help-settings package: the single ATK_KRH_CONFIG row from the export with ONE column changed
(who-columns blanked); every other CSV header only; metadata unchanged. Added by GoSaaS, not part of official FSCR. Gap fill batch 13 (2026-11-25). Offline: no Oracle call.
Usage: python -I one_value_package.py <export unz> <out dir> <zip name> <Column> <NewValue>"""
import csv, sys, zipfile
from pathlib import Path
if len(sys.argv) != 6:
    sys.exit(__doc__)
src, out, zname, col, val = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
WHO = {"CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin"}
out.mkdir(parents=True, exist_ok=True)
for p in sorted(src.glob("*.csv")):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.reader(f); h = next(r); rows = list(r)
    keep = []
    if p.name == "ATK_KRH_CONFIG.csv":
        if len(rows) != 1 or col not in h:
            sys.exit(f"STOP: expected 1 row with column {col}")
        row = dict(zip(h, rows[0]))
        print(f"{col}: {row[col]!r} -> {val!r}")
        row[col] = val
        keep = [[("" if c in WHO else row[c]) for c in h]]
    with open(out / p.name, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(h); w.writerows(keep)
with zipfile.ZipFile(out / zname, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(src / "ASM_SETUP_CSV_METADATA.xml", "ASM_SETUP_CSV_METADATA.xml")
    for p in sorted(out.glob("*.csv")):
        z.write(p, p.name)
print("wrote", out / zname)
