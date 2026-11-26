"""Start rows.json from an EXISTING record in your own read-only export (a working template), under a new code.
It copies the template's rows from the CSVs you name, replaces the template key with your new code in every
column, drops audit columns (CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin) and
applies --set overrides. The template record itself is never changed or loaded.
Usage:
  python template_row.py --export <export.zip> --key-col <CSV>:<column> [--key-col ...] --template "<existing code>"
         --new <NEW_CODE> --out rows.json [--set <CSV>:<column>=<value> ...]
--key-col names, for each CSV to copy, the column that holds the record's code (for example
INV_INVENTORY_STATUS.csv:StatusCode and INV_INVENTORY_STATUS_TRANSACTION_CONTROL.csv:INV_INVENTORY_STATUS.StatusCode).
Read only. No sign-in, no network."""
import argparse, csv, io, json, re, sys, zipfile
AUDIT = re.compile(r"^(CreatedBy|CreationDate|LastUpdatedBy|LastUpdateDate|LastUpdateLogin)$")
ap = argparse.ArgumentParser(); ap.add_argument("--export", required=True); ap.add_argument("--key-col", action="append", required=True)
ap.add_argument("--template", required=True); ap.add_argument("--new", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--set", action="append", default=[]); a = ap.parse_args()
z = zipfile.ZipFile(a.export); out = {}
for kc in a.key_col:
    n, col = kc.split(":", 1)
    rows = list(csv.DictReader(io.StringIO(z.read(n).decode("utf-8-sig"))))
    sel = [r for r in rows if r.get(col) == a.template]
    if not sel: sys.exit(f"{n}: no row with {col} = template")
    new = []
    for r in sel:
        d = {k: (a.new if v == a.template else v) for k, v in r.items() if v != "" and not AUDIT.match(k)}
        new.append(d)
    out[n] = new
for s in a.set:
    left, val = s.split("=", 1); n, col = left.split(":", 1)
    for d in out.get(n, []): d[col] = val
json.dump(out, open(a.out, "w"), indent=1)
print("wrote", a.out, "|", ", ".join(f"{n}: {len(r)} row(s)" for n, r in out.items()))
