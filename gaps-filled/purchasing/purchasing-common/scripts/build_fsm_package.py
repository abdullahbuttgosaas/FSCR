#!/usr/bin/env python3
"""Build an FSM setup CSV import ZIP that holds ONLY your new rows.

Usage:
  python3 build_fsm_package.py --export <task export.zip> --rows <rows.json> --prefix <PREFIX> --out <new.zip>
         [--who-from-export] [--max-len COLUMN=N ...]

rows.json: {"<CSV file name in the export>": [{"<column>": "<value>", ...}, ...], ...}
  Optional key "_unchanged_parents": {"<CSV>": [row, ...]} for EXISTING parent rows that a hierarchical package
  needs (an FSM child row is skipped when its parent row is not in the same ZIP). Copy those rows exactly as Oracle
  holds them (read live by REST); they are written first and are not checked for the prefix. The after-export must
  show them unchanged.

- Copies the export ZIP (including ASM_SETUP_CSV_METADATA.xml) and replaces every CSV with its header plus only
  the rows you give. CSVs you do not name keep their header and no rows. An FSM import merges rows by key, so
  re-sending the full export could change existing records; this script prevents that.
- Every row must contain --prefix in at least one value; otherwise nothing is written.
- Columns must exist in that CSV's header (exact spelling).
- --who-from-export fills empty CreatedBy / LastUpdatedBy columns with the SubmittedBy value of the export's
  ASM_SETUP_CSV_METADATA.xml (read at run time, never printed). Use it when the import fails with a generic
  database error at insert (JBO-26041 or similar).
- --max-len COLUMN=N stops when a value in COLUMN is longer than N characters.
Local files only: no sign-in, no network. Prints counts only.
"""
import argparse
import csv
import io
import json
import re
import sys
import zipfile


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--who-from-export", action="store_true")
    ap.add_argument("--max-len", action="append", default=[])
    a = ap.parse_args()

    new_rows = json.load(open(a.rows, encoding="utf-8"))
    parents = new_rows.pop("_unchanged_parents", {})
    limits = {}
    for item in a.max_len:
        col, _, n = item.partition("=")
        limits[col] = int(n)

    with zipfile.ZipFile(a.export) as src:
        names = src.namelist()
        submitted_by = ""
        if a.who_from_export and "ASM_SETUP_CSV_METADATA.xml" in names:
            m = re.search(r"<SubmittedBy>([^<]+)</SubmittedBy>", src.read("ASM_SETUP_CSV_METADATA.xml").decode("utf-8", "replace"))
            submitted_by = m.group(1).strip() if m else ""
            if not submitted_by:
                print("ERROR: --who-from-export but no SubmittedBy in the export metadata", file=sys.stderr)
                return 2
        for f in new_rows:
            if f not in names:
                print(f"ERROR: {f} is not in the export ZIP. CSVs: {[n for n in names if n.endswith('.csv')]}", file=sys.stderr)
                return 2
        out_files = {}
        counts = {}
        for name in names:
            data = src.read(name)
            if not name.lower().endswith(".csv"):
                out_files[name] = data
                continue
            rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
            header = rows[0] if rows else []
            buf = io.StringIO()
            w = csv.writer(buf, lineterminator="\n")
            w.writerow(header)
            n = 0
            for r in parents.get(name, []):
                bad = [c for c in r if c not in header]
                if bad:
                    print(f"ERROR: {name}: unknown column(s) {bad}", file=sys.stderr)
                    return 2
                w.writerow([str(r.get(h, "")) for h in header])
                n += 1
            for r in new_rows.get(name, []):
                bad = [c for c in r if c not in header]
                if bad:
                    print(f"ERROR: {name}: unknown column(s) {bad}", file=sys.stderr)
                    return 2
                if not any(a.prefix in str(v) for v in r.values()):
                    print(f"ERROR: {name}: a row has no value containing {a.prefix}", file=sys.stderr)
                    return 2
                for c, lim in limits.items():
                    if c in r and len(str(r[c])) > lim:
                        print(f"ERROR: {name}: {c} is {len(str(r[c]))} characters, limit {lim}", file=sys.stderr)
                        return 2
                full = {h: str(r.get(h, "")) for h in header}
                if submitted_by:
                    for h in ("CreatedBy", "LastUpdatedBy"):
                        if h in full and not full[h]:
                            full[h] = submitted_by
                w.writerow([full[h] for h in header])
                n += 1
            counts[name] = n
            out_files[name] = buf.getvalue().encode("utf-8")
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as dst:
        for name, data in out_files.items():
            dst.writestr(name, data)
    print("wrote", a.out.split("/")[-1] + ":", ", ".join(f"{k} {v} row(s)" for k, v in counts.items() if v),
          "; all other CSVs header only" + ("; who-columns filled from export metadata" if submitted_by else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
