"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 05 (2026-11-25). Offline: no Oracle call.

Read-only viewer for an unzipped FSCR setup-task CSV export: shows, file by file, every row in which
some column equals one of the given values (exact match, case-insensitive). Use it for "view" and
"search" setup tasks (legal entities, reporting units, ledgers, service providers), where the task
creates nothing and the guide is: export, then look the record up.

Audit and person columns (CreatedBy, LastUpdatedBy, LastUpdateLogin, SubmittedBy, *UserName*, *Email*,
the dates of creation/update, and person columns such as PersonNumber, FirstName, LastName, MiddleNames,
ManagerListName, *Phone*) are never printed, so the output holds no user or person names. Empty
columns are left out.

Usage:
  python -I view_record.py <unz dir> --value "<name or code>" [--value ...] [--file X.csv ...]
         [--cols A,B,C] [--match-cols K1,K2] [--max-rows 20] [--out summary.txt]
  --match-cols  look for the value only in these columns (for example the business key columns), so rows
                of OTHER records that merely mention the value (a registration number) are not shown.
The summary is printed to the screen and, with --out, also written to that file.
Exit 0 = at least one row found; 1 = nothing found (check spelling, or the export scope); 2 = bad input.
"""
import argparse, csv, re, sys
from pathlib import Path

HIDE = re.compile(r"(CreatedBy|LastUpdatedBy|LastUpdateLogin|SubmittedBy|UserName|Email|CreationDate|LastUpdateDate"
                  r"|PersonNumber|FirstName|LastName|MiddleNames|ManagerListName|PersonName|Phone)", re.I)


def clean(v):
    """One line per value: multi-line values (account segments) are joined with '.', long ones cut at 80."""
    parts = [x.strip() for x in v.replace("\r", "\n").split("\n") if x.strip()]
    s = ".".join(parts)
    return s if len(s) <= 80 else s[:77] + "..."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("unz")
    ap.add_argument("--value", action="append", required=True)
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--cols")
    ap.add_argument("--match-cols", help="comma list: match --value only in these columns (default: any column)")
    ap.add_argument("--max-rows", type=int, default=20)
    ap.add_argument("--out")
    a = ap.parse_args()
    d = Path(a.unz)
    if not d.is_dir():
        print(f"STOP: {d} is not a folder (unzip the export first)")
        return 2
    want = {v.strip().lower() for v in a.value}
    only = set(a.file)
    cols = [c.strip() for c in a.cols.split(",")] if a.cols else None
    lines, found = [], 0
    for p in sorted(d.glob("*.csv")):
        if only and p.name not in only:
            continue
        with open(p, encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            mc = [c.strip() for c in a.match_cols.split(",")] if a.match_cols else None
            hits = [row for row in r if any((v or "").strip().lower() in want
                                            for k, v in row.items() if mc is None or k in mc)]
        lines.append(f"== {p.name}: {len(hits)} matching row(s)")
        for row in hits[: a.max_rows]:
            keep = [(k, clean(v)) for k, v in row.items() if v and v.strip() and not HIDE.search(k) and (cols is None or k in cols)]
            lines.append("   " + " | ".join(f"{k}={v}" for k, v in keep))
        if len(hits) > a.max_rows:
            lines.append(f"   ... {len(hits) - a.max_rows} more")
        found += len(hits)
    lines.append(f"TOTAL matching rows: {found}")
    text = "\n".join(lines)
    print(text)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main())
