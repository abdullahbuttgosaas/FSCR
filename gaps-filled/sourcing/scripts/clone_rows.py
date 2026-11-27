"""Added by GoSaaS, not part of official FSCR. Gap fill, Sourcing, 2026-11-27. Offline: no Oracle call.

Builds an FSM setup-task CSV import ZIP that holds ONE NEW record, made by copying the rows of an
existing record (the SOURCE) from a read-only task export and giving them a new key.

- Copies ASM_SETUP_CSV_METADATA.xml unchanged (never reads or prints it: it holds the submitting user).
- In every CSV file, takes the rows whose key column holds the SOURCE key, puts NEW in that column,
  empties the audit columns (CreationDate, CreatedBy, LastUpdateDate, LastUpdatedBy, LastUpdateLogin)
  and applies your --set changes. Other rows are not sent (files keep their header).
- Refuses: NEW not starting with --prefix, NEW already in the export, SOURCE not found.
- --who VALUE fills CreatedBy and LastUpdatedBy with VALUE instead of leaving them empty
  (the JBO-26041 fix; pass the export metadata's SubmittedBy, read with --print-who-into FILE first).

Usage:
  python -I clone_rows.py --export-dir <RUN>/export_before/unz --out <RUN>/payload/new.zip --prefix GAPFILL_AB_ \
     --key-col StyleCode --key-col PON_NEGOTIATION_STYLES.StyleCode --source Standard_Negotiation --new GAPFILL_AB_X1 \
     --set "PON_NEGOTIATION_STYLES.csv|StyleName=GAPFILL AB X1|SystemFlag=N" --set "PON_NEGOTIATION_STYLES_TRANSLATION.csv|StyleName=GAPFILL AB X1"
  python -I clone_rows.py --export-dir <RUN>/export_before/unz --print-who-into <RUN>/who.txt   (writes SubmittedBy to a file, prints nothing of it)
--set FILE|Col=value|... changes those columns on every cloned row of FILE (a value may contain '=' but not '|').
Prints only file names, row counts and the ZIP path.
"""
import argparse
import csv
import io
import re
import sys
import zipfile
from pathlib import Path

AUDIT = ("CreationDate", "CreatedBy", "LastUpdateDate", "LastUpdatedBy", "LastUpdateLogin")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--out")
    ap.add_argument("--prefix")
    ap.add_argument("--key-col", action="append", default=[])
    ap.add_argument("--source")
    ap.add_argument("--new")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--who-file", help="file holding the value for CreatedBy/LastUpdatedBy (from --print-who-into)")
    ap.add_argument("--print-who-into")
    a = ap.parse_args()
    ex = Path(a.export_dir)
    meta = ex / "ASM_SETUP_CSV_METADATA.xml"
    if not meta.exists():
        sys.exit("STOP: no ASM_SETUP_CSV_METADATA.xml in the export folder")
    if a.print_who_into:
        m = re.search(r"<SubmittedBy>([^<]+)</SubmittedBy>", meta.read_text(encoding="utf-8"))
        if not m:
            sys.exit("STOP: no SubmittedBy in the metadata")
        Path(a.print_who_into).write_text(m.group(1).strip(), encoding="utf-8")
        print("who value written to file (not printed)")
        return
    for need in ("out", "prefix", "source", "new"):
        if not getattr(a, need):
            sys.exit(f"STOP: --{need} is required")
    if not a.key_col:
        sys.exit("STOP: give at least one --key-col")
    if not a.new.startswith(a.prefix):
        sys.exit(f"STOP: {a.new} does not start with {a.prefix}")
    who = Path(a.who_file).read_text(encoding="utf-8").strip() if a.who_file else ""
    sets = {}
    for s in a.set:
        parts = s.split("|")
        sets.setdefault(parts[0], {}).update(dict(p.split("=", 1) for p in parts[1:]))

    out_files, found = {}, 0
    for p in sorted(ex.glob("*.csv")):
        with open(p, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        head, body = (rows[0], rows[1:]) if rows else ([], [])
        kidx = [i for i, h in enumerate(head) if h in a.key_col]
        new_rows = []
        for r in body:
            if any(r[i] == a.new for i in kidx):
                sys.exit(f"STOP: {a.new} is already in {p.name}: it would update an existing record")
            if kidx and any(r[i] == a.source for i in kidx):
                r = list(r)
                for i in kidx:
                    if r[i] == a.source:
                        r[i] = a.new
                for i, h in enumerate(head):
                    if h in AUDIT:
                        r[i] = who if (who and h in ("CreatedBy", "LastUpdatedBy")) else ""
                for col, val in sets.get(p.name, {}).items():
                    if col not in head:
                        sys.exit(f"STOP: no column {col} in {p.name}")
                    r[head.index(col)] = val
                new_rows.append(r)
        found += len(new_rows)
        out_files[p.name] = (head, new_rows)
    if not found:
        sys.exit(f"STOP: source {a.source} not found in any file")
    for fn in sets:
        if fn not in out_files:
            sys.exit(f"STOP: no file {fn} in the export")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(meta, meta.name)
        for fn, (head, body) in out_files.items():
            buf = io.StringIO()
            w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writerow(head)
            w.writerows(body)
            z.writestr(fn, buf.getvalue().encode("utf-8"))
            print(f"{fn}: {len(body)} row(s)")
    print(f"ZIP: {a.out}")


if __name__ == "__main__":
    sys.exit(main())
