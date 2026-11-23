"""Offline facts about a Run 04 candidate ZIP, used as evidence for the Task Hook rule results.
Prints per CSV: row count, non-blank fields of the first rows, non-blank audit columns, non-ISO (slash) dates, and,
if given, whether the key values already exist in the baseline export (duplicate check).
Usage: inspect_candidate.py <candidate.zip> <baseline.zip> [KeyCol,KeyCol ...]"""
import csv, io, re, sys, zipfile

cand, base = zipfile.ZipFile(sys.argv[1]), zipfile.ZipFile(sys.argv[2])
keys = sys.argv[3].split(",") if len(sys.argv) > 3 else []
AUD = ("LastUpdateDate", "LastUpdatedBy", "CreationDate", "CreatedBy", "LastUpdateLogin")


def rows(z, n):
    return list(csv.DictReader(io.StringIO(z.read(n).decode("utf-8-sig")))) if n in z.namelist() else []


for n in cand.namelist():
    if not n.endswith(".csv"):
        continue
    r = rows(cand, n)
    aud = sorted({k for x in r for k in AUD if x.get(k)})
    slash = sorted({k for x in r for k, v in x.items() if v and re.fullmatch(r"\d{4}/\d{2}/\d{2}.*", v)})
    print(f"{n}: rows={len(r)} audit_nonblank={aud} slash_dates={slash}")
    for x in r[:3]:
        print("   ", {k: v for k, v in x.items() if v})
    k = [c for c in keys if r and c in r[0]]
    if k:
        b = {tuple(y.get(c) for c in k) for y in rows(base, n)}
        dup = [tuple(x.get(c) for c in k) for x in r if tuple(x.get(c) for c in k) in b]
        print(f"    key {k}: baseline rows={len(rows(base, n))} duplicates_in_baseline={dup}")
