"""Step 6 - Screenshots. Build the 4 table images straight from the run's files, so no number is typed by hand.

Usage:
  python make_images.py --work work/Procurement
  python make_images.py --work work/Procurement --browser "C:/Program Files/Google/Chrome/Application/chrome.exe"

Reads from --work (all written by the other kit scripts, plus six_tasks.csv and tracker_row.md that you fill):
  01_coverage.png          coverage.csv + coverage_by_area.csv
  02_plan_result.png       plan_summary.json (+ runbook_summary.json if present)
  03_six_task_table.png    six_tasks.csv  (columns: task_code, task, area, group, result, record_or_reason)
  04_tracker_row_values.png tracker_row.md
Writes PNGs at 2x resolution into --work/images. Each has a title, a clean table and a footer naming the source file.
At most these 4 images. The text is checked with secret_scan.py first; if a token, sign-in name, e-mail or
machine path is found, no image is made.
Needs Microsoft Edge or Google Chrome (used headless, closed when each image is done). No sign-in, no network.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from kitlib import GROUP_NEITHER, GROUP_ROUTE_ONLY, GROUP_SKILL_ROUTE, Path, read_csv
import secret_scan
import tracker_row

RESULTS = {"Done": "ok", "Done with a fix": "ok", "Not done": "bad", "Not counted": "mid"}
CSS = """body{margin:0;background:#fff;font-family:'Segoe UI',Arial,sans-serif;color:#1b2a3a}
.w{width:1400px;padding:28px 32px 20px}h1{font-size:26px;margin:0 0 6px}.sub{color:#5a6b7d;font-size:14px;margin-bottom:16px}
table{border-collapse:collapse;width:100%;font-size:15px}th{background:#1f3b57;color:#fff;text-align:left;padding:8px 10px}
td{padding:7px 10px;border-bottom:1px solid #d9e0e7;vertical-align:top}tr:nth-child(even) td{background:#f5f8fb}
.f{margin-top:14px;color:#5a6b7d;font-size:12.5px;border-top:1px solid #d9e0e7;padding-top:8px}
.ok{color:#1a7f37;font-weight:600}.bad{color:#b42318;font-weight:600}.mid{color:#9a6700;font-weight:600}
ul{margin:0;padding-left:18px}li{margin:1px 0}"""
e = html.escape


def find_browser(given: str | None) -> str:
    cands = [given] if given else []
    cands += [os.path.expandvars(p) for p in (
        r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe", r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
        r"%ProgramFiles%\Google\Chrome\Application\chrome.exe", r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
        r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")]
    cands += [shutil.which(n) or "" for n in ("msedge", "microsoft-edge", "google-chrome", "chrome", "chromium", "chromium-browser")]
    for c in cands:
        if c and Path(c).is_file():
            return c
    sys.exit("No Edge or Chrome found. Install one, or pass --browser <path to msedge.exe or chrome.exe>.")


def page(title, sub, head, rows, foot, widths, raw=()):
    th = "".join(f"<th>{e(h)}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c if i in raw else e(str(c))}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    cg = "".join(f"<col style='width:{w}%'>" for w in widths)
    return (f"<!doctype html><meta charset=utf-8><title>x</title><style>{CSS}</style><div class=w><h1>{e(title)}</h1>"
            f"<div class=sub>{e(sub)}</div><table><colgroup>{cg}</colgroup><tr>{th}</tr>{body}</table>"
            f"<div class=f>{e(foot)}</div></div><script>document.title=document.querySelector('.w').offsetHeight</script>")


def shot(browser: str, tmp: Path, out: Path, name: str, doc: str) -> None:
    f = tmp / f"{name}.html"
    f.write_text(doc, encoding="utf-8")
    base = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
            "--disable-extensions", "--disable-sync", "--disable-background-networking", f"--user-data-dir={tmp / 'profile'}"]
    d = subprocess.run(base + ["--window-size=1464,3000", "--dump-dom", f.as_uri()], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120).stdout
    m = re.search(r"<title>(\d+)</title>", d)
    if not m:
        sys.exit(f"{name}: the browser did not render the page")
    png = out / f"{name}.png"
    if png.exists():
        png.unlink()  # never report an old image as new
    shot_file = tmp / "shot.png"  # written to the temp folder first (the browser may not write into the pack folder)
    if shot_file.exists():
        shot_file.unlink()
    subprocess.run(base + [f"--window-size=1464,{int(m.group(1)) + 4}", "--force-device-scale-factor=2", f"--screenshot={shot_file}",
                           f.as_uri()], capture_output=True, timeout=120)
    if not shot_file.is_file():
        sys.exit(f"{name}: no image written")
    shutil.move(str(shot_file), png)
    print(f"{png.name}: {png.stat().st_size // 1024} KB")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", type=Path, required=True, help="the module's work folder")
    ap.add_argument("--browser", help="path to msedge/chrome (found automatically if not given)")
    ap.add_argument("--env", default="", help="environment label for the footer, for example 'test environment, 26D'")
    ap.add_argument("--names", default="", help="comma-separated names that must not appear in any image")
    a = ap.parse_args()
    W = a.work
    need = ["coverage.csv", "coverage_by_area.csv", "plan_summary.json", "six_tasks.csv", "tracker_row.md"]
    miss = [n for n in need if not (W / n).is_file()]
    if miss:
        sys.exit(f"Missing in {W.name}: {', '.join(miss)}")
    cov = read_csv(W / "coverage.csv")[0]
    module = cov["module"]
    when = dt.date.today().strftime("%d/%m/%Y")
    foot = f"FSCR module test · {module} · {a.env + ' · ' if a.env else ''}{when} · Source: "
    docs = {}

    areas = read_csv(W / "coverage_by_area.csv")
    docs["01_coverage"] = page(
        f"{module}: FSCR coverage", "a = FSCR skill or guide · b = CSV route, no skill · c = neither · Missing = b + c (no skill or guide)",
        ["Functional area", "Tasks", "a: skill/guide", "b: route only", "c: neither", "Missing (N/total)"],
        [(r["functional_area"], r["tasks"], r["a_skill_or_guide"], r["b_route_no_skill"], r["c_neither"], r["missing_N_of_total"]) for r in areas]
        + [("Proposed FSCR coverage", cov["proposed_coverage"], cov["coverage_basis"], "", "", "")],
        foot + "coverage.csv, coverage_by_area.csv (from module_scope_map.csv)", [36, 8, 26, 11, 9, 10])

    ps = json.loads((W / "plan_summary.json").read_text(encoding="utf-8"))
    rows = [("Tasks planned", f"{ps['tasks']} (main offering: {ps['primary_offering']})"),
            ("(a) Oracle-sourced links in order (URL + quote checked)", f"{ps['a_respected']} of {ps['a_sourced_links']}"
             + (" · out of order: " + "; ".join(f"#{x[1]} {x[0]} after #{x[3]} {x[2]}" for x in ps["a_violations"]) if ps["a_violations"] else "")),
            ("(b) Unverified links out of order", f"{ps['b_unverified_out_of_order']} of {ps['b_unverified']} (not counted as verified)"),
            ("(c) FSCR-stated prerequisites out of order", f"{ps['c_out_of_order']} of {ps['c_fscr_skill_prereqs']}"),
            ("Sourced links FSCR's own skills state", f"{ps['a_stated_by_fscr_skills']} of {ps['a_sourced_links']}")]
    src = "plan_summary.json"
    if (W / "runbook_summary.json").is_file():
        rs = json.loads((W / "runbook_summary.json").read_text(encoding="utf-8"))
        rows += [("Run Book steps", f"{rs['steps']}: {rs['with_route']} with a route, {rs['manual']} manual "
                  f"({rs['manual_with_csv_route']} of them have a CSV), {rs['with_prerequisite']} with a prerequisite"),
                 ("Run Book order vs the same sourced links", f"{rs['respected_in_runbook']} of {rs['sourced_links_found_in_runbook']}")]
        src += ", runbook_summary.json"
    docs["02_plan_result"] = page("Plan result: FSCR order vs Oracle dependency links",
                                  "FSCR task-dependency-resolver method · release catalog order", ["Measure", "Result"], rows,
                                  foot + src + ", oracle_links.csv", [38, 62])

    six = read_csv(W / "six_tasks.csv")
    if not 1 <= len(six) <= 6:
        sys.exit(f"six_tasks.csv must have 1 to 6 rows (has {len(six)})")
    for s in six:
        if s["group"] not in (GROUP_SKILL_ROUTE, GROUP_ROUTE_ONLY, GROUP_NEITHER):
            sys.exit(f"six_tasks.csv: group '{s['group']}' must be one of {GROUP_SKILL_ROUTE}, {GROUP_ROUTE_ONLY}, {GROUP_NEITHER}")
        if s["result"] not in RESULTS:
            sys.exit(f"six_tasks.csv: result '{s['result']}' must be one of {', '.join(RESULTS)}")
    docs["03_six_task_table"] = page(
        "Six sample tasks on the test environment (FSCRT_ records only)", "Every record created was read back from Oracle",
        ["#", "Task", "Area", "Group", "Result", "Record or reason"],
        [(i + 1, s["task"], s["area"], s["group"], f"<span class={RESULTS[s['result']]}>{e(s['result'])}</span>", s["record_or_reason"])
         for i, s in enumerate(six)], foot + "six_tasks.csv", [3, 19, 12, 9, 10, 47], raw=(4,))

    cols = tracker_row.parse((W / "tracker_row.md").read_text(encoding="utf-8"))
    docs["04_tracker_row_values"] = page(
        f"Tracker row: {module}", "Final values, ready to paste (same as tracker_row.md)", ["Column", "Value"],
        [(k, "<ul>" + "".join(f"<li>{e(x[2:] if x.startswith('• ') else x)}</li>" for x in v) + "</ul>"
          if len(v) > 1 or (v and v[0].startswith("• ")) else e(v[0] if v else "")) for k, v in cols],
        foot + "tracker_row.md", [24, 76], raw=(1,))

    names = [x.strip() for x in a.names.split(",") if x.strip()]
    bad = [(n, k, m) for doc in docs.values() for n, k, m in secret_scan.scan_text(re.sub(r"<[^>]+>", " ", doc), names)]
    if bad:
        for n, k, m in bad:
            print(f"BLOCKED: {k} found ({m})")
        sys.exit("No images made. Remove the text above from the source files and run again.")

    out = W / "images"
    out.mkdir(exist_ok=True)
    browser = find_browser(a.browser)
    tmp = Path(tempfile.mkdtemp(prefix="kitimg_"))
    try:
        for name, doc in docs.items():
            shot(browser, tmp, out, name, doc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
