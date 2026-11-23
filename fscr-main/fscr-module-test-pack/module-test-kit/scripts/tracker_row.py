"""tracker_row.md - write a starting file, or check a finished one against SHEET_FILL_GUIDE.md.

Usage:
  python tracker_row.py template --module "Procurement" --coverage work/Procurement/coverage.csv \
      --initials AB --out work/Procurement/tracker_row.md
  python tracker_row.py check work/Procurement/tracker_row.md [--names "Your Name"]

tracker_row.md has one "## <column>" heading per tracker column, in the tracker's order, with the value under it.
Columns with several items use one "• " bullet per line. "template" fills the columns that come straight from
the CSV files (Pillar, Module, FSCR coverage, Total Tasks, Missing) and marks the rest TODO.
"check" fails (exit 1) on any rule break and lists each one. Nobody edits the tracker itself: Abdullah pastes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys

from kitlib import COUNTS, Path, read_csv, resolve_module
import secret_scan

COLUMNS = ["Pillar", "Module", "FSCR coverage", "Fit rating", "Contact Person/Owner", "Plan accuracy (1–5)",
           "Total Tasks", "Missing", "Gaps filled", "Runbook quality (1–5)", "Execution & validation (1–5)", "Status",
           "Target Completion Date", "FSCR skills / workflows used", "Test scenario", "Fusion env / release", "Tester",
           "Last tested", "Key findings", "GoSaaS gap / build needed", "Evidence link"]
BULLETS = {"FSCR skills / workflows used", "Test scenario", "Key findings", "GoSaaS gap / build needed"}
SCORES = {"Plan accuracy (1–5)", "Runbook quality (1–5)", "Execution & validation (1–5)"}
FIXED = {  # columns the tester does not decide; Abdullah keeps or fills them
    "Contact Person/Owner": "(no change)",
    "Target Completion Date": "(no change)",
    "Gaps filled": "(leave empty)",
    "Evidence link": "(Drive folder link, added by Abdullah)",
}
OWNER_WORDS = re.compile(r"(?i)\b(owner|owned by|assigned to|assignee|responsible:|contact person)\b|@")


def parse(text: str) -> list[tuple[str, list[str]]]:
    cols, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = (line[3:].strip(), [])
            cols.append(cur)
        elif cur is not None and line.strip():
            cur[1].append(line.rstrip())
    return cols


def template(module: str, coverage: Path, initials: str) -> str:
    c = read_csv(coverage)[0]
    v = {k: ["TODO"] for k in COLUMNS}
    v.update({"Pillar": [c["pillar"]], "Module": [module], "FSCR coverage": [c["proposed_coverage"]],
              "Total Tasks": [c["total_tasks"]], "Missing": [c["missing_N_of_total"]], "Status": ["Completed"],
              "Tester": [initials.upper()], "Last tested": [dt.date.today().strftime("%d/%m/%Y")]})
    for k, x in FIXED.items():
        v[k] = [x]
    for k in BULLETS:
        v[k] = ["• TODO"]
    out = [f"# Tracker row: {module}", "",
           "Values ready to paste into the FSCR Module Test Tracker. Abdullah pastes them; the tracker is view only.", ""]
    for k in COLUMNS:
        out += [f"## {k}", *v[k], ""]
    return "\n".join(out)


def check(path: Path, names: list[str]) -> list[str]:
    err = []
    cols = parse(path.read_text(encoding="utf-8"))
    got = [k for k, _ in cols]
    if got != COLUMNS:
        missing = [k for k in COLUMNS if k not in got]
        extra = [k for k in got if k not in COLUMNS]
        err.append(f"columns differ from the tracker (missing {missing}, extra {extra}, or wrong order)")
    v = {k: lines for k, lines in cols}
    one = lambda k: (v.get(k) or [""])[0].strip()
    for k, lines in v.items():
        if any("TODO" in x for x in lines):
            err.append(f"{k}: still has TODO")
        if not lines:
            err.append(f"{k}: empty (write the value, or the marker the guide gives)")
    for k, x in FIXED.items():
        if k in v and one(k) != x:
            err.append(f"{k}: must be exactly '{x}'")
    if one("Pillar") not in ("ERP", "HCM", "SCM"):
        err.append("Pillar: must be ERP, HCM or SCM")
    module = one("Module")
    try:
        exact = resolve_module(module)
    except SystemExit:
        exact = None
        err.append(f"Module: '{module}' is not a tracker row in module_scope_map.csv")
    if one("FSCR coverage") not in ("Full", "Partial", "None", "Unknown"):
        err.append("FSCR coverage: must be Full, Partial, None or Unknown")
    if one("Fit rating") not in ("High", "Medium", "Low", "None"):
        err.append("Fit rating: must be High, Medium, Low or None")
    for k in SCORES:
        if k in v and (len(v[k]) != 1 or not re.fullmatch(r"[1-5]", one(k))):
            err.append(f"{k}: one whole number 1-5 only (reasons go in RESULT.md)")
    total = one("Total Tasks")
    if not total.isdigit():
        err.append("Total Tasks: whole number")
    m = re.fullmatch(r"(\d+)/(\d+)", one("Missing"))
    if not m:
        err.append("Missing: must be N/total, for example 26/41")
    elif total.isdigit() and m.group(2) != total:
        err.append("Missing: total after the slash must equal Total Tasks")
    if exact:
        ref = [r for r in read_csv(COUNTS) if r["row"] == exact]
        if ref:
            r = ref[0]
            if total != r["total_tasks"]:
                err.append(f"Total Tasks: {total} but module_counts.csv says {r['total_tasks']}")
            if one("Missing") != r["missing_N_of_total"]:
                err.append(f"Missing: {one('Missing')} but module_counts.csv says {r['missing_N_of_total']}")
            if one("Pillar") != r["pillar"]:
                err.append(f"Pillar: {one('Pillar')} but module_counts.csv says {r['pillar']}")
            if one("FSCR coverage") != r["proposed_coverage"]:
                err.append(f"FSCR coverage: {one('FSCR coverage')} but the scope map proposes {r['proposed_coverage']} "
                           "(only change it with a reason in RESULT.md, and say so in verify)")
    if one("Status") not in ("Completed", "Blocked"):
        err.append("Status: 'Completed' (or 'Blocked' with the reason in Key findings)")
    for k in ("Last tested",):
        try:
            dt.datetime.strptime(one(k), "%d/%m/%Y")
            if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", one(k)):
                raise ValueError
        except ValueError:
            err.append(f"{k}: date as dd/mm/yyyy, for example 17/11/2026")
    for k in BULLETS:
        bad = [x for x in v.get(k, []) if not x.startswith("• ")]
        if bad:
            err.append(f"{k}: every line must start with '• ' (found '{bad[0][:40]}')")
    for k in ("Pillar", "Module", "FSCR coverage", "Fit rating", "Total Tasks", "Missing", "Status", "Fusion env / release",
              "Tester", "Last tested"):
        if len(v.get(k, [])) > 1:
            err.append(f"{k}: one line only")
    if not re.fullmatch(r"[A-Z]{2,3}", one("Tester")):
        err.append("Tester: your initials only (2-3 capital letters); Abdullah writes the name")
    for x in v.get("GoSaaS gap / build needed", []):
        if OWNER_WORDS.search(x) or any(n.lower() in x.lower() for n in names):
            err.append(f"GoSaaS gap / build needed: no owners or names ('{x[:50]}')")
    for n, kind, mk in secret_scan.scan_text(path.read_text(encoding="utf-8"), names):
        err.append(f"line {n}: {kind} found ({mk})")
    return err


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template", help="write a starting tracker_row.md")
    t.add_argument("--module", required=True)
    t.add_argument("--coverage", type=Path, required=True)
    t.add_argument("--initials", required=True)
    t.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("check", help="check a finished tracker_row.md")
    c.add_argument("file", type=Path)
    c.add_argument("--names", default="", help="comma-separated names that must not appear")
    a = ap.parse_args()
    if a.cmd == "template":
        if not re.fullmatch(r"[A-Za-z]{2,3}", a.initials):
            sys.exit("--initials: 2 or 3 letters")
        module = resolve_module(a.module)
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(template(module, a.coverage, a.initials), encoding="utf-8")
        print(f"written {a.out.name}; fill every TODO, then run: python tracker_row.py check {a.out.name}")
        return 0
    errs = check(a.file, [x.strip() for x in a.names.split(",") if x.strip()])
    for e in errs:
        print("FAIL", e)
    print("tracker_row.md: " + ("PASS" if not errs else f"{len(errs)} problem(s)"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
