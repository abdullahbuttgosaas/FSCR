"""Step 7 - Evidence folder. Copy a finished module run into the folder you upload to Drive, then check it.

Usage:
  python build_evidence.py --module "Procurement" --work work/Procurement --out evidence
  python build_evidence.py ... --names "Your Name,yourlogin"     (extra words that must not appear)

Layout made (this is what you upload):
  evidence/<Module>/RESULT.md
  evidence/<Module>/tracker_row.md
  evidence/<Module>/plan.csv
  evidence/<Module>/oracle_links.csv
  evidence/<Module>/images/        at most 4 PNG tables from make_images.py
  evidence/<Module>/data/          the CSV/JSON the numbers come from, and the saved Oracle pages (oracle_docs/)
  evidence/<Module>/INDEX.md       list of every file with its size and a short checksum
Checks (exit 1 if one fails; the folder is still written so you can fix it):
  required files present; at most 4 images; tracker_row.md passes "tracker_row.py check";
  RESULT.md has a Start/Finish/Minutes table; secret_scan.py finds nothing.
Local files only. No sign-in, no network.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import shutil
import sys

from kitlib import Path, resolve_module, safe_folder_name
import secret_scan
import tracker_row

TOP = ["RESULT.md", "tracker_row.md", "plan.csv", "oracle_links.csv"]
DATA = ["scope_tasks.csv", "coverage.csv", "coverage_by_area.csv", "sample_candidates.csv", "plan_summary.json",
        "links_input.csv", "runbook_summary.json", "runbook_step_check.csv", "runbook_tasks_oracle_clean.json", "six_tasks.csv"]
IMAGES = ["01_coverage.png", "02_plan_result.png", "03_six_task_table.png", "04_tracker_row_values.png"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True, help="evidence root folder")
    ap.add_argument("--names", default="")
    a = ap.parse_args()
    module = resolve_module(a.module)
    names = [x.strip() for x in a.names.split(",") if x.strip()]
    W = a.work
    D = a.out / safe_folder_name(module)
    if D.exists():
        shutil.rmtree(D)
    (D / "images").mkdir(parents=True)
    (D / "data").mkdir()
    problems = []

    for n in TOP:
        if (W / n).is_file():
            shutil.copy2(W / n, D / n)
        else:
            problems.append(f"missing {n}")
    for n in DATA:
        if (W / n).is_file():
            shutil.copy2(W / n, D / "data" / n)
    if (W / "oracle_docs").is_dir():
        shutil.copytree(W / "oracle_docs", D / "data" / "oracle_docs")
    imgs = sorted(p.name for p in (W / "images").glob("*.png")) if (W / "images").is_dir() else []
    extra = [i for i in imgs if i not in IMAGES]
    if extra:
        problems.append(f"images not made by make_images.py (not copied): {extra}")
    for i in IMAGES:
        if (W / "images" / i).is_file():
            shutil.copy2(W / "images" / i, D / "images" / i)
        else:
            problems.append(f"missing image {i}")

    if (D / "tracker_row.md").is_file():
        problems += [f"tracker_row.md: {x}" for x in tracker_row.check(D / "tracker_row.md", names)]
    if (D / "RESULT.md").is_file():
        txt = (D / "RESULT.md").read_text(encoding="utf-8")
        if not re.search(r"\|\s*Start\s*\|\s*Finish\s*\|\s*Minutes\s*\|", txt):
            problems.append("RESULT.md: no '| Start | Finish | Minutes |' time table")
        for word in ("Plan accuracy", "Runbook quality", "Execution & validation", "Fit rating"):
            if word not in txt:
                problems.append(f"RESULT.md: no '{word}' score with its reason")

    found, _, _ = secret_scan.scan([D], names, [])
    grouped = {}
    for r, n, k, m in found:
        grouped.setdefault((r, k), []).append(str(n))
    problems += [f"secret scan: {k} in {r}, line(s) {', '.join(ns[:5])}{' ...' if len(ns) > 5 else ''}"
                 for (r, k), ns in grouped.items()]

    files = sorted(p for p in D.rglob("*") if p.is_file())
    lines = [f"# Evidence: {module}", "", f"Built {dt.datetime.now():%d/%m/%Y %H:%M} by build_evidence.py. "
             "Upload this whole folder to Drive and send Abdullah the folder link.", "",
             "| File | Size (KB) | SHA-256 (first 12) |", "|---|---:|---|"]
    for p in files:
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
        lines.append(f"| {p.relative_to(D).as_posix()} | {max(1, p.stat().st_size // 1024)} | {h} |")
    lines += ["", "Checks: " + ("all passed." if not problems else f"{len(problems)} problem(s):")]
    lines += [f"- {x}" for x in problems]
    (D / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Evidence folder: {D.name} ({len(files) + 1} files)")
    for x in problems:
        print("FAIL", x)
    print("PASS" if not problems else f"{len(problems)} problem(s) - fix them in the work folder and run again")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
