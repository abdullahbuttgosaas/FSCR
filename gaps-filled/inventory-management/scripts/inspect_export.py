"""Show what an FSM task-level CSV export ZIP holds: each CSV, its row count, its columns and a few sample rows.
Audit columns (CreatedBy, LastUpdatedBy, ...) are never printed, because they hold user names.
Usage: python inspect_export.py <export.zip> [--rows 3] [--grep TEXT]
Read only. No sign-in, no network."""
import argparse, csv, io, re, sys, zipfile
AUDIT = re.compile(r"(Created|LastUpdated|Updated)(By|Date|Login)|SubmittedBy|ObjectVersion|UserName", re.I)
ap = argparse.ArgumentParser(); ap.add_argument("zip"); ap.add_argument("--rows", type=int, default=3); ap.add_argument("--grep")
a = ap.parse_args()
z = zipfile.ZipFile(a.zip)
for n in sorted(z.namelist()):
    if not n.endswith(".csv"):
        print(f"[file] {n}"); continue
    rows = list(csv.reader(io.StringIO(z.read(n).decode("utf-8-sig"))))
    hdr, body = (rows[0], rows[1:]) if rows else ([], [])
    keep = [i for i, h in enumerate(hdr) if not AUDIT.search(h)]
    print(f"\n== {n}: {len(body)} row(s)")
    print("   columns:", ", ".join(hdr))
    sample = [r for r in body if not a.grep or any(a.grep in v for v in r)][: a.rows]
    for r in sample:
        print("   row:", {hdr[i]: r[i] for i in keep if i < len(r) and r[i] != ""})
