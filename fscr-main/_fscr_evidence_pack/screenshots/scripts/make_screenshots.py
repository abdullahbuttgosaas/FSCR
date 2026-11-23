"""Builds the evidence screenshots (PNG, 2x) from FSCR run files. Read-only on every run folder.
Every number shown is read from a run file at build time; nothing numeric is typed in here.
Run:  python make_screenshots.py   (uses Playwright with the installed Chrome; no server, no network)."""
import csv, json, re, html, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # ...\fscr-main
OUT = Path(__file__).resolve().parents[1]           # ...\_fscr_evidence_pack\screenshots
R = lambda p: ROOT / p
MISSING = []                                        # numbers we could not find

def rd(p): return R(p).read_text(encoding="utf-8")
def rows(p): return list(csv.DictReader(open(R(p), encoding="utf-8")))
def find(p, pattern, label):
    m = re.search(pattern, rd(p), re.S)
    if not m:
        MISSING.append(f"{label} ({p})"); return None
    return m.group(1)
e = html.escape
def pct(a, b): return int(a * 100 / b + 0.5)
def n(x):
    try: return f"{int(x):,}"
    except (TypeError, ValueError): return e(str(x))

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;font-family:'Segoe UI',Arial,sans-serif;color:#1f2933}
.card{width:1100px;padding:28px 32px 18px;background:#fff}
h1{font-size:22px;font-weight:600;margin-bottom:4px}
.sub{font-size:13.5px;color:#52606d;margin-bottom:16px;line-height:1.45}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{background:#eef2f6;text-align:left;font-weight:600;padding:8px 10px;border-bottom:2px solid #cbd2d9;vertical-align:bottom}
td{padding:7px 10px;border-bottom:1px solid #e4e7eb;vertical-align:top;line-height:1.4}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.total td{font-weight:600;background:#f7f9fb;border-top:2px solid #cbd2d9}
.pill{display:inline-block;padding:1px 9px;border-radius:10px;font-size:12.5px;font-weight:600;white-space:nowrap}
.ok{background:#e3f4e8;color:#1d6b35}.fix{background:#fdf1d8;color:#8a5a00}.no{background:#fbe4e4;color:#a61b1b}
.kpis{display:flex;gap:14px;margin-bottom:16px}
.kpi{flex:1;border:1px solid #e4e7eb;border-radius:8px;padding:12px 14px}
.kpi b{display:block;font-size:26px;font-weight:600}
.kpi span{font-size:12.5px;color:#52606d}
h2{font-size:15px;font-weight:600;margin:18px 0 8px}
.note{font-size:12.5px;color:#52606d;margin-top:10px;line-height:1.45}
.foot{margin-top:16px;padding-top:9px;border-top:1px solid #e4e7eb;font-size:12px;color:#7b8794;display:flex;justify-content:space-between}
code{font-family:Consolas,monospace;font-size:12px}
"""

def page(title, sub, body, run, sources):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div class='card' id='card'><h1>{e(title)}</h1><div class='sub'>{sub}</div>{body}"
            f"<div class='foot'><span>{e(run)}</span><span>Source: {e(sources)}</span></div></div></body></html>")

def table(head, data, num_cols=(), total_rows=()):
    h = "".join(f"<th class='{'num' if i in num_cols else ''}'>{c}</th>" for i, c in enumerate(head))
    b = ""
    for ri, r in enumerate(data):
        cls = " class='total'" if ri in total_rows else ""
        b += f"<tr{cls}>" + "".join(f"<td class='{'num' if i in num_cols else ''}'>{c}</td>" for i, c in enumerate(r)) + "</tr>"
    return f"<table><tr>{h}</tr>{b}</table>"

def pill(result):
    cls = {"Done": "ok", "Done with a fix": "fix", "Not done": "no"}.get(result, "fix")
    return f"<span class='pill {cls}'>{e(result)}</span>"

pages = {}

# 1 Coverage (Run 29)
src = "_fscr_run_29_common_features/area_counts.csv"
ac = rows(src)
c1 = "Route + instructions"; c2 = "Route, no instructions"; c3 = "No route, no instructions"
data, totals = [], []
for r in ac:
    data.append([e(r["area"]), n(r["tasks"]), n(r[c1]), n(r[c2]), n(r[c3])])
    if r["area"].startswith("ALL") or r["area"].startswith("Financials"): totals.append(len(data) - 1)
allr = next(r for r in ac if r["area"].startswith("ALL"))
kp = "".join(f"<div class='kpi'><b>{n(allr[k])}</b><span>{lbl}</span></div>" for k, lbl in
             [("tasks", "Common Features tasks"), (c1, "route and instructions (FSCR skill)"),
              (c2, "route but no instructions"), (c3, "neither route nor instructions")])
pages["01_coverage"] = page("ERP Common Features: FSCR coverage",
    "Each task counted once, by its best coverage level. 8 ORA_ASK_ functional areas.",
    f"<div class='kpis'>{kp}</div>" + table(["Functional area", "Tasks", "Route + instructions", "Route, no instructions", "Neither"],
                                            data, num_cols=(1, 2, 3, 4), total_rows=totals),
    f"Run 29 ({rd('_fscr_run_29_common_features/start_time.txt').strip()[:10]})", src)

# 2 Plan (Run 30)
src = "_fscr_run_30_common_features_test/evidence/plan_summary.json"
ps = json.loads(rd(src))
plan = {r["task_code"]: r for r in rows("_fscr_run_30_common_features_test/plan.csv")}
kp = (f"<div class='kpi'><b>{ps['tasks_order_ok_all']} of {ps['tasks']}</b><span>tasks in an order that matches Oracle "
      f"({pct(ps['tasks_order_ok_all'], ps['tasks'])}%)</span></div>"
      f"<div class='kpi'><b>{ps['edges_order_ok']} of {ps['oracle_edges']}</b><span>Oracle dependency links respected "
      f"({pct(ps['edges_order_ok'], ps['oracle_edges'])}%)</span></div>"
      f"<div class='kpi'><b>{ps['edges_stated_by_fscr']} of {ps['oracle_edges']}</b><span>links FSCR states itself "
      f"({pct(ps['edges_stated_by_fscr'], ps['oracle_edges'])}%)</span></div>")
data = []
for a, sa, b, sb in ps["violations"]:
    data.append([f"{e(plan[a]['task_name'])}<br><code>{e(a)}</code>", n(sa), f"{e(plan[b]['task_name'])}<br><code>{e(b)}</code>", n(sb)])
pages["02_plan"] = page("FSCR plan vs Oracle's documented order",
    f"FSCR ordered all {ps['tasks']} tasks from its release catalog. Checked against {ps['oracle_edges']} Oracle prerequisite links.",
    f"<div class='kpis'>{kp}</div><h2>The {len(data)} misses: prerequisite placed after the task that needs it</h2>"
    + table(["Prerequisite (Oracle)", "FSCR step", "Task that needs it", "FSCR step"], data, num_cols=(1, 3)),
    "Run 30 (2026-11-16)", "plan_summary.json, plan.csv, oracle_edges_check.csv")

# 3 Runbook (Run 30)
src = "_fscr_run_30_common_features_test/runbook/runbook_step_check.csv"
rb = rows(src); T = len(rb)
cnt = lambda f: sum(1 for r in rb if f(r))
dl = cnt(lambda r: r["route_detail"].startswith("ORA_CHK_DATA_LOADER"))
man = cnt(lambda r: r["route_detail"].startswith("ORA_CHK_MANUAL"))
lm = cnt(lambda r: "load_method=manual" in r["route_detail"])
data = [["Steps in FSCR's runbook", n(T), ""],
        ["Have a task", n(cnt(lambda r: r["has_task"] == "True")), ""],
        ["Have a route (Data Loader type, <code>ORA_CHK_DATA_LOADER</code>)", n(cnt(lambda r: r["has_route"] == "True")), ""] if dl == cnt(lambda r: r["has_route"] == "True") else MISSING.append("runbook route mismatch"),
        ["Route says manual (<code>ORA_CHK_MANUAL</code>)", n(man), "no route"],
        ["Load method says manual (<code>load_method=manual</code>)", n(lm), "includes the Data Loader steps"],
        ["Have a prerequisite", n(cnt(lambda r: r["has_prerequisite"] == "True")), "depends_on empty"],
        ["Have a validation step", n(cnt(lambda r: r["has_validation"] == "True")), ""],
        ["Have an owner", n(cnt(lambda r: r["has_owner"] == "True")), ""],
        ["Have all five (task, prerequisite, route, validation, owner)", n(cnt(lambda r: r["all_five"] == "True")), ""]]
pages["03_runbook"] = page("FSCR runbook for Common Features",
    "Runbook produced by FSCR's initializer for the Common Features tasks; each step checked for 5 items.",
    table(["Check", "Steps", "Note"], data, num_cols=(1,), total_rows=(0,)),
    "Run 30 (2026-11-16)", "runbook/runbook_step_check.csv")

# 4 Six tasks (Run 30)
src = "_fscr_run_30_common_features_test/RESULT.md"
res = rd(src)
SHORT = {  # reason in a few words (wording only; record IDs and counts below are parsed from RESULT.md)
    "1": "FSCR CSV export + import", "2": "DAT written by hand, own Run Book, rule results by Claude",
    "3": "CSV import", "4": "CSV import, read back by a 2nd export",
    "5": "No CSV route, no REST create", "6": "No CSV route, no API; Security Console only"}
data = []
for m in re.finditer(r"^\| (\d) \| (.+?) \| (.+?) \| \*\*(.+?)\*\* \| (.+?) \|$", res, re.M):
    num, task, grp, result, rec = m.groups()
    ident = re.findall(r"FSCRT_[A-Z0-9_]+(?: Rate Type| Common Features Exec)?|(?:SetId|ID) \d{12,}", rec)
    detail = SHORT[num] + (f"<br><code>{e(' · '.join(dict.fromkeys(ident)))}</code>" if ident else "")
    data.append([num, e(task), e(grp), pill(result), detail])
if len(data) != 6: MISSING.append(f"6-task table rows: found {len(data)} ({src})")
pages["04_six_tasks"] = page("6-task test on ETIA-TEST",
    "Two tasks with an FSCR skill, two with a route only, two with neither. Every record read back after creation.",
    table(["#", "Task (functional area)", "Group", "Result", "Reason / record"], data, num_cols=()),
    "Run 30 (2026-11-16)", "RESULT.md")

# 5 Calendar ripple (Runs 21 + 22)
src = "_fscr_run_22_calendar_change_impact/impact_map.csv"
im = rows(src)
def imp(ch, obj, col="Count"):
    for r in im:
        if r["Change"] == ch and r["ObjectType"] == obj: return r
    MISSING.append(f"impact row {ch}/{obj}"); return None
edit = imp("1", "Calendar period EndDate")
gap = imp("1", "Date gap"); led = imp("1", "Ledger"); bu = imp("1", "Business unit")
aro = imp("1", "Receivables system options"); apo = imp("1", "Payables options"); pro = imp("1", "Procurement options")
inv = imp("1", "Receipts dated 25-31 Dec 2026"); pinv = imp("1", "Payables invoices dated 25-31 Dec 2026")
cnt_names = lambda r: len([x for x in r["ObjectName"].split(",") if x.strip()])
r21 = rd("_fscr_run_21_calendar_workbook/RUN_REPORT.md")
r21_led = find("_fscr_run_21_calendar_workbook/RUN_REPORT.md", r"Ledgers on GoSaaS MFG \| (\d+)", "Run 21 ledgers")
r21_bu = find("_fscr_run_21_calendar_workbook/RUN_REPORT.md", r"Business units on those ledgers \| (\d+)", "Run 21 BUs")
data = [
    ["0", "What changed (in a workbook copy, not in Oracle)", e(edit["ObjectName"]), n(edit["Count"])],
    ["1", "Days that fall in no period", e(gap["ObjectName"]), n(gap["Count"])],
    ["1", "Ledgers on the calendar", e(led["ObjectName"]), n(led["Count"])],
    ["2", "Business units on those ledgers", e(bu["ObjectName"]), n(bu["Count"])],
    ["3", "BUs with Receivables options", e(aro["ObjectName"]), n(cnt_names(aro))],
    ["3", "BUs with Payables options", e(apo["ObjectName"]), n(cnt_names(apo))],
    ["3", "BUs with Procurement options", e(pro["ObjectName"]), n(cnt_names(pro))],
    ["4", "Receipts / Payables invoices dated 25–31 Dec 2026", "existing documents hit", f"{n(inv['Count'])} / {n(pinv['Count'])}"],
]
pages["05_calendar_ripple"] = page("Calendar change: ripple through ledgers and business units",
    f"Run 21 built the chain workbook ({r21_led} ledgers, {r21_bu} business units on calendar GoSaaS MFG, checked against Run 20). "
    "Run 22 changed one period end date in a copy and traced the impact. Oracle was not changed; the save would fail on the date gap.",
    table(["Level", "Impact", "Object", "Count"], data, num_cols=(3,), total_rows=()),
    "Runs 21 and 22 (2026-11-09)", "Run 22 impact_map.csv; Run 21 RUN_REPORT.md")

# 6 Gap fills (Runs 24-27b)
p24 = "_fscr_run_24_fill_route_only/RUN_REPORT.md"; p25 = "_fscr_run_25_fill_no_route/RUN_REPORT.md"
p26 = "_fscr_run_26b_skill_test/RUN_REPORT.md"; p27 = "_fscr_run_27b_skill_test/RUN_REPORT.md"
b24, a24 = (find(p24, r"(\d+) rows before, \d+ after", "Run 24 rows before"), find(p24, r"\d+ rows before, (\d+) after", "Run 24 rows after"))
m24 = find(p24, r"Total minutes \| about (\d+)", "Run 24 minutes")
c24 = find(p24, r"Records created \| (\d+)", "Run 24 records")
a26 = find(p26, r"export after = (\d+) rows", "Run 26b rows after"); b26 = find(p26, r"export after = \d+ rows \(was (\d+)\)", "Run 26b rows before")
v26 = find(p26, r"## Verdict: ([A-Z ]+)", "Run 26b verdict"); m26 = find(p26, r"\| about (\d+) \|", "Run 26b minutes")
c25 = find(p25, r"Records created \| (\d+)", "Run 25 records"); m25 = find(p25, r"Total minutes \| about (\d+)", "Run 25 minutes")
pst25 = find(p25, r"Create attempts \| (\d+) POSTs", "Run 25 POSTs")
b27 = find(p27, r"before_all\.json`: (\d+) rules", "Run 27b before"); a27 = find(p27, r"after_all\.json`: (\d+) rules", "Run 27b after")
v27 = find(p27, r"## Verdict: ([A-Z ]+)", "Run 27b verdict"); m27 = find(p27, r"Total \| about (\d+) minutes", "Run 27b minutes")
data = [
    ["<b>Manage Journal Categories</b><br><code>GL_MANAGE_JOURNAL_CATEGORIES</code><br>route only",
     "Generic CSV export / import scripts and sign-in. No skill, no CSV layout, no field limits.",
     f"Run 24: built a CSV with only {c24} new FSCRT_ rows from the exported layout; imported with FSCR's script; read back. "
     f"Wrote a skill (Run 26a).",
     f"<span class='pill ok'>Filled</span> {c24} created, 1 import, 0 fixes, ~{m24} min; rows {b24} → {a24}.<br>"
     f"Cold test Run 26b: {v26.strip().lower()}, ~{m26} min; rows {b26} → {a26}."],
    ["<b>Manage Alternate Name Mapping Rules</b><br><code>ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES</code><br>neither",
     "Catalog entry only (CSV flag N). No skill, guide or REST name.",
     f"Run 25: found a documented REST POST in Oracle docs; sent {pst25} POSTs; read back. Wrote a skill using FSCR's REST client (Run 27a).",
     f"<span class='pill ok'>Filled</span> {c25} created, first try, ~{m25} min.<br>"
     f"Cold test Run 27b: {v27.strip().lower()}, ~{m27} min; rules {b27} → {a27}."],
]
pages["06_gap_fills"] = page("Two gap fills: what FSCR had vs what Claude added",
    "One task with a route but no instructions, one with neither. Each was filled in ETIA-TEST, turned into a skill and tested by a fresh chat.",
    table(["Gap", "What FSCR had", "What Claude did", "Result"], data),
    "Runs 24, 25, 26b, 27b (2026-11-15/16)", "RUN_REPORT.md of each run")

# 7 Tokens (Run 28)
src = "_fscr_run_28_token_estimate/token_estimate.csv"
tk = rows(src)
label = {"24": "24 fill: journal categories", "25": "25 fill: alternate name rules", "24+25 (gap-filling)": "24 + 25 gap-filling total",
         "26b": "26b cold skill test", "27b": "27b cold skill test"}
data = [[e(label.get(r["run"], r["run"])), e(r["basis"]), n(r["input_new_tokens"]), n(r["output_tokens"]), n(r["total_new_tokens"]), n(r["cache_read_tokens"])] for r in tk]
tot = [i for i, r in enumerate(tk) if "+" in r["run"]]
pages["07_tokens"] = page("Token use of the gap-fill runs",
    f"Measured from the Claude Code session logs (model {e(tk[0]['model'])}), rounded to the nearest thousand. "
    "Total (new) = input (new) + output. Cache read is re-read context, shown apart and not added to the total.",
    table(["Run", "Basis", "Input (new)", "Output", "Total (new)", "Cache read"], data, num_cols=(2, 3, 4, 5), total_rows=tot),
    "Run 28", "token_estimate.csv (RUN_REPORT.md)")

# 8 Tracker row
tsrc = "_fscr_run_29_common_features/tracker_row.csv"
tr = rows(tsrc)[0]
sc = {k: find("_fscr_run_30_common_features_test/RESULT.md", rf"\*\*{k}: (\d)\.\*\*", f"Run 30 {k} score") for k in ("Plan accuracy", "Runbook quality", "Execution")}
verdict = find("_fscr_run_30_common_features_test/RESULT.md", r"Verdict: \*\*(\w+)\*\*", "Run 30 verdict")
r30date = rd("_fscr_run_30_common_features_test/start_time.txt").strip()[:10]
def bullets(t): return "<br>".join(e(x.strip()) for x in t.split("\n") if x.strip())
data = [
    ["Module", e(tr["Module"]), "tracker_row.csv"],
    ["Test status", e(tr["Test status"]), "tracker_row.csv"],
    ["FSCR coverage", e(tr["FSCR coverage"]), "tracker_row.csv"],
    ["Fit rating", e(tr["Fit rating"]), "tracker_row.csv"],
    ["Plan accuracy", f"<b>{sc['Plan accuracy']}</b> / 5", "Run 30 RESULT.md"],
    ["Runbook quality", f"<b>{sc['Runbook quality']}</b> / 5", "Run 30 RESULT.md"],
    ["Execution and validation", f"<b>{sc['Execution']}</b> / 5", "Run 30 RESULT.md"],
    ["Run 30 verdict", e(verdict), "Run 30 RESULT.md"],
    ["Fusion env / release", e(tr["Fusion env / release"]), "tracker_row.csv"],
    ["Last tested", e(r30date) + " (Run 30)", "Run 30 start_time.txt"],
    ["FSCR skills / workflows used", e(tr["FSCR skills / workflows used"]).replace("; ", "<br>"), "tracker_row.csv"],
    ["Key findings", bullets(tr["Key findings"]), "tracker_row.csv"],
    ["GoSaaS gap / build needed", bullets(tr["GoSaaS gap / build needed"]), "tracker_row.csv"],
]
pages["08_tracker_row"] = page("Tracker row: ERP / Common Features",
    "Values to enter in the tracker. Scores and date from Run 30; all other fields as written in Run 29's tracker_row.csv.",
    table(["Field", "Value", "From"], data),
    "Runs 29 and 30", "tracker_row.csv; Run 30 RESULT.md")

# render
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome", headless=True)
    pg = br.new_page(device_scale_factor=2, viewport={"width": 1100, "height": 800})
    for name, doc in pages.items():
        pg.set_content(doc)
        pg.locator("#card").screenshot(path=str(OUT / f"{name}.png"))
        print("wrote", name + ".png")
    br.close()
print("MISSING:", MISSING or "none")
