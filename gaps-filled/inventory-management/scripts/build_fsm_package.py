"""Build an FSM CSV import package that holds ONLY your new rows.
It copies the export ZIP (metadata and every CSV header) and writes into each CSV only the rows you give.
Every row must contain --prefix in at least one value. Other CSVs keep their header and no rows, so no existing
record is re-sent.
Usage:
  python build_fsm_package.py --export <export.zip> --rows <rows.json> --prefix <PREFIX> --out <new.zip>
         [--max-len Column=N ...] [--audit-from-metadata]
rows.json: {"<CSV file name>": [{"<column>": "<value>", ...}, ...], ...}
--max-len stops the build when a value is longer than Oracle allows.
--audit-from-metadata fills empty CreatedBy / LastUpdatedBy columns with the export metadata's SubmittedBy value
(read at run time, never printed). Use it only after a generic insert error (JBO-26041).
Read only on Oracle: it only writes a local ZIP."""
import argparse, csv, io, json, re, sys, zipfile
ap = argparse.ArgumentParser()
ap.add_argument("--export", required=True); ap.add_argument("--rows", required=True)
ap.add_argument("--prefix", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--max-len", action="append", default=[]); ap.add_argument("--audit-from-metadata", action="store_true")
a = ap.parse_args()
if not a.prefix.startswith("FSCRT_"):
    sys.exit("--prefix must start with FSCRT_")
rows = json.load(open(a.rows, encoding="utf-8"))
limits = {k: int(v) for k, v in (x.split("=", 1) for x in a.max_len)}
z = zipfile.ZipFile(a.export); names = set(z.namelist())
submitted = None
if a.audit_from_metadata:
    for n in names:
        if n.lower().endswith(".xml"):
            m = re.search(r"<SubmittedBy>([^<]+)</SubmittedBy>", z.read(n).decode("utf-8", "ignore"))
            if m: submitted = m.group(1)
    if not submitted: sys.exit("SubmittedBy not found in the export metadata")
for n, rs in rows.items():
    if n not in names: sys.exit(f"{n} is not in the package. CSVs: {sorted(x for x in names if x.endswith('.csv'))}")
    for r in rs:
        if not any(a.prefix in str(v) for v in r.values()): sys.exit(f"{n}: a row has no value with {a.prefix}")
        for c, v in r.items():
            if c in limits and len(str(v)) > limits[c]: sys.exit(f"{n}: {c} '{v}' is longer than {limits[c]}")
with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as zo:
    for n in z.namelist():
        data = z.read(n)
        if n.endswith(".csv"):
            hdr = next(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
            for r in rows.get(n, []):
                bad = [c for c in r if c not in hdr]
                if bad: sys.exit(f"{n}: unknown column(s) {bad}")
            buf = io.StringIO(); w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(hdr)
            for r in rows.get(n, []):
                vals = dict(r)
                if submitted:
                    for c in ("CreatedBy", "LastUpdatedBy"):
                        if c in hdr and not vals.get(c): vals[c] = submitted
                w.writerow([vals.get(h, "") for h in hdr])
            data = buf.getvalue().encode("utf-8")
        zo.writestr(n, data)
print("wrote", a.out, "|", ", ".join(f"{n}: {len(r)} row(s)" for n, r in rows.items()), "| other CSVs header only")
