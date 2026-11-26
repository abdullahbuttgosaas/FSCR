#!/usr/bin/env python3
"""Compare two FSM task export ZIPs (before and after your import) for each CSV.

Usage: python3 compare_fsm_exports.py --before <before.zip> --after <after.zip> --prefix <PREFIX>

For every CSV: rows before / after, rows added, removed and changed (ignoring who/date columns), and the
added rows' keys. Proof of a clean load: only rows with your prefix are added; removed 0; changed 0.
Exit code 0 when that holds, 1 otherwise. Prints keys (first column values) only, never user names.
Local files only: no sign-in, no network.
"""
import argparse
import csv
import io
import re
import zipfile

SKIP = re.compile(r"(By|UpdateLogin|Date)$")


def load(path):
    out = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.lower().endswith(".csv"):
                rows = list(csv.reader(io.StringIO(z.read(n).decode("utf-8-sig"))))
                out[n] = (rows[0], rows[1:]) if rows else ([], [])
    return out


def norm(header, rows):
    keep = [i for i, h in enumerate(header) if not SKIP.search(h)]
    res = {}
    for r in rows:
        sig = tuple(r[i] if i < len(r) else "" for i in keep)
        res[sig] = res.get(sig, 0) + 1
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--prefix", required=True)
    a = ap.parse_args()
    b, af = load(a.before), load(a.after)
    ok = True
    for n in sorted(set(b) | set(af)):
        hb, rb = b.get(n, ([], []))
        ha, ra = af.get(n, ([], []))
        head = ha or hb
        nb, na = norm(head, rb), norm(head, ra)
        added = [k for k in na if k not in nb]
        removed = [k for k in nb if k not in na]
        foreign_added = [k for k in added if not any(a.prefix in v for v in k)]
        own_removed = [k for k in removed if any(a.prefix in v for v in k)]
        changed = len(removed) - len(own_removed)
        keys = sorted({k[0] for k in added if k})
        print(f"{n}: before {len(rb)}, after {len(ra)}, added {len(added)} {keys if keys else ''}, "
              f"existing removed or changed {changed}, added without prefix {len(foreign_added)}")
        if changed or foreign_added:
            ok = False
    print("RESULT:", "only prefix rows added; existing rows unchanged" if ok else "CHECK: existing rows changed or non-prefix rows added")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
