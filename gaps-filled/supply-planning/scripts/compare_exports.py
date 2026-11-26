"""Compare two FSM task exports (before / after an import) and print counts and your new rows only.

Usage: python compare_exports.py <before folder> <after folder> <PREFIX>
Each folder holds the export ZIP (the newest ZIP in the folder is used, so the environment-named file never has to be
typed or printed). Who-columns (CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin) are ignored
and never printed, because they hold user names. Local files only; no sign-in, no network.
Last line: PASS only when at least one row of yours was added and nothing else was added, removed or changed;
FAIL when none of your rows was added; CHECK when something else changed.
"""
import csv
import io
import sys
import zipfile
from pathlib import Path

WHO = ("CreatedBy", "CreationDate", "LastUpdate", "SubmittedBy")


def load(folder):
    zips = sorted(Path(folder).glob("*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        sys.exit(f"No export ZIP in {folder}")
    z = zipfile.ZipFile(zips[-1])
    out = {}
    for n in z.namelist():
        if n.endswith(".csv"):
            rows = list(csv.reader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig")))
            if not rows:
                continue
            keep = [i for i, c in enumerate(rows[0]) if not any(s in c for s in WHO)]
            out[n] = [tuple(r[i] for i in keep if i < len(r)) for r in rows[1:]]
    return out


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    before, after, prefix = load(sys.argv[1]), load(sys.argv[2]), sys.argv[3]
    bad = 0
    yours = 0
    for n in sorted(after):
        sb, sa = set(before.get(n, [])), set(after[n])
        added, removed = sa - sb, sb - sa
        mine = [r for r in added if any(prefix in v for v in r)]
        bad += len(removed) + (len(added) - len(mine))
        yours += len(mine)
        print(f"{n}: before {len(sb)} after {len(sa)} | added {len(added)} (yours {len(mine)}) | removed/changed {len(removed)}")
        for r in mine:
            print("   +", [v for v in r if v][:8])
    if yours == 0:
        print("FAIL: none of your rows were added (the import created nothing)")
    elif bad:
        print(f"CHECK: {bad} row(s) added or changed that are not yours")
    else:
        print(f"PASS: {yours} row(s) of yours added, nothing else added or changed")


if __name__ == "__main__":
    main()
