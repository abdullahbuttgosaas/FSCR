"""Run 24: build a CSV package with only 3 new FSCRT_ journal categories.
Layout copied from the ETIA-TEST export (same files, same columns, same metadata XML)."""
import csv, zipfile, shutil, sys
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
SRC = RUN / "export_existing" / "unz"
OUT = RUN / "payload"
ROWS = [
    ("FSCRT_Run24 Accrual", "FSCR test category for accrual journals. Run 24."),
    ("FSCRT_Run24 Payroll", "FSCR test category for payroll journals. Run 24."),
    ("FSCRT_Run24 Reclass", "FSCR test category for reclass journals. Run 24."),
]
assert len(ROWS) <= 3 and all(n.startswith("FSCRT_") and len(n) <= 25 for n, _ in ROWS)
def header(name):
    with open(SRC / name, encoding="utf-8", newline="") as f: return next(csv.reader(f))
OUT.mkdir(exist_ok=True)
def write(name, dicts):
    h = header(name)
    with open(OUT / name, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(h)
        for d in dicts: w.writerow([d.get(c, "") for c in h])
write("GL_JOURNAL_CATEGORY_DEF.csv", [dict(JeCategoryName=n, UserJeCategoryName=n, JeCategoryKey=n, Description=d) for n, d in ROWS])
write("GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv", [{"GL_JOURNAL_CATEGORY_DEF.JeCategoryName": n, "JeCategoryName": n, "UserJeCategoryName": n, "Language": "US", "SourceLang": "US", "Description": d} for n, d in ROWS])
shutil.copy(SRC / "ASM_SETUP_CSV_METADATA.xml", OUT / "ASM_SETUP_CSV_METADATA.xml")
z = OUT / (sys.argv[1] if len(sys.argv) > 1 else "gl_journal_categories_fscrt.zip")
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for n in ("ASM_SETUP_CSV_METADATA.xml", "GL_JOURNAL_CATEGORY_DEF.csv", "GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv"):
        zf.write(OUT / n, n)
print("wrote", z)
