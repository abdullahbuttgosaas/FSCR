#!/usr/bin/env python3
"""Update one row of MODULE_TRACKER.csv.

Usage: python3 tracker_set.py <MODULE_TRACKER.csv> <TASK_CODE> key=value [key=value ...]
If the file is locked (open elsewhere), writes MODULE_TRACKER_NEW.csv beside it instead.
"""
import csv
import os
import sys


def main() -> int:
    path, code, *pairs = sys.argv[1:]
    alt = os.path.join(os.path.dirname(path), "MODULE_TRACKER_NEW.csv")
    src = alt if os.path.exists(alt) else path
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    fields = list(rows[0].keys())
    hit = False
    for r in rows:
        if r["task_code"] == code:
            for p in pairs:
                k, _, v = p.partition("=")
                if k not in fields:
                    raise SystemExit(f"unknown column {k}")
                r[k] = v
            hit = True
    if not hit:
        raise SystemExit(f"no row for {code}")
    for target in (src, alt):
        try:
            with open(target, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
            print("updated", os.path.basename(target), code)
            return 0
        except OSError:
            continue
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
