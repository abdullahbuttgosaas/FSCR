"""Safe look at one CSV of an FSM task export: row count, whether a code exists, and value counts.

Usage: python inspect_export.py <export folder> <CSV name> <key column> <your code> [<column to count> ...]
The newest ZIP in the folder is used, so the environment-named file never has to be typed or printed.
Rows whose key contains "FSCRT_" (earlier test records) are left out of the value counts, so the counts show what
predefined and customer rows use. No row and no who-column (CreatedBy, LastUpdatedBy, ...) is ever printed.
Local files only; no sign-in, no network.
"""
import collections
import csv
import io
import sys
import zipfile
from pathlib import Path


def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    folder, name, key, code, cols = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
    if any(s in c for c in cols for s in ("CreatedBy", "LastUpdatedBy", "LastUpdateLogin", "SubmittedBy")):
        sys.exit("Refused: who-columns hold user names and are never counted or printed.")
    zips = sorted(Path(folder).glob("*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        sys.exit(f"No export ZIP in {folder}")
    rows = list(csv.DictReader(io.TextIOWrapper(zipfile.ZipFile(zips[-1]).open(name), encoding="utf-8-sig")))
    print(f"{name}: {len(rows)} rows")
    print(f"{code} already exists: {any(r.get(key) == code for r in rows)}")
    base = [r for r in rows if "FSCRT_" not in (r.get(key) or "")]
    for c in cols:
        counts = collections.Counter(r.get(c, "") for r in base).most_common()
        print(f"{c} (excluding FSCRT_ test rows, {len(base)} rows): " + ", ".join(f"{v or '(empty)'} x{n}" for v, n in counts))


if __name__ == "__main__":
    main()
