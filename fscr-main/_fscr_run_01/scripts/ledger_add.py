"""Append ledger rows (CSV) from a JSON file (object or list). Keys = ledger.csv header columns."""
import csv, json, sys
p = r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01\ledger.csv"
hdr = next(csv.reader(open(p, encoding="utf-8")))
rows = json.load(open(sys.argv[1], encoding="utf-8"))
rows = rows if isinstance(rows, list) else [rows]
with open(p, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    for r in rows:
        bad = set(r) - set(hdr)
        if bad:
            sys.exit(f"unknown keys {bad}")
        w.writerow([r.get(h, "") for h in hdr])
print(len(rows), "rows added")
