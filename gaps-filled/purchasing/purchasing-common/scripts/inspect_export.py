#!/usr/bin/env python3
"""Show the CSV files, headers and row counts of an FSM task export ZIP.

Usage: python3 inspect_export.py <export.zip> [--rows N] [--match TEXT]

Prints at most N sample rows per CSV (default 3). Who-columns and e-mail columns (CreatedBy, LastUpdatedBy, EmailAddress,
LastUpdateLogin and anything ending in "By") are masked, so no user name is printed.
--match TEXT prints only rows that contain TEXT (for example your prefix).
Local file only: no sign-in, no network.
"""
import argparse
import csv
import io
import re
import zipfile

WHO = re.compile(r"(By|UpdateLogin|Email\w*|EmailAddress)$", re.I)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zip")
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--match", default="")
    a = ap.parse_args()
    with zipfile.ZipFile(a.zip) as z:
        for name in z.namelist():
            if not name.lower().endswith(".csv"):
                print(f"[file] {name}")
                continue
            rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
            head, body = (rows[0], rows[1:]) if rows else ([], [])
            print(f"[csv] {name}: {len(body)} row(s)")
            print("  header:", head)
            shown = 0
            for r in body:
                if a.match and not any(a.match in v for v in r):
                    continue
                if shown >= a.rows:
                    break
                print("  row:", {h: ("<who>" if WHO.search(h) and v else v) for h, v in zip(head, r) if v != ""})
                shown += 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
