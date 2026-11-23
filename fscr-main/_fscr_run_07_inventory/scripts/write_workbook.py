"""Run 07: write FSCR_Inventory.xlsx from out/tasks.csv, out/skills_leaf.csv, out/summary.json
and the fixed facts below (copied from earlier run reports). Read-only apart from the output file."""
import csv, json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

RUN = r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_07_inventory"
OUT = os.path.join(RUN, "out")
S = json.load(open(os.path.join(OUT, "summary.json"), encoding="utf-8"))
tasks = list(csv.DictReader(open(os.path.join(OUT, "tasks.csv"), encoding="utf-8")))
skills = list(csv.DictReader(open(os.path.join(OUT, "skills_leaf.csv"), encoding="utf-8")))

AREAS = ["ERP", "SCM", "HCM", "CX", "Common", "Multiple", "Unmapped offering", "No offering"]
NOW = "computed now (Run 07 join)"
HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="305496")

wb = Workbook()

def sheet(title, header, rows, widths=None):
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font, c.fill = HEAD, FILL
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for r in rows:
        ws.append(r)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i, w in enumerate(widths or [], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    return ws

# --- README
ws = wb.active
ws.title = "README"
for line in [
    ["FSCR inventory (Run 07)", ""],
    ["Built", "2026-11-04, read-only. No Oracle call, no sign-in, original repo unchanged."],
    ["Method", "Join of files and outputs that already existed; no new analysis. Scripts: scripts/build_inventory.py (join) and scripts/write_workbook.py (this file)."],
    ["Sources", "Catalog: knowledge/setup-task-catalog/effective/setupTasksAll.json, offering-functional-area-task-catalog.json, pillars-offerings-mapping.json (original repo)."],
    ["", "Route audit 2026-11-02: _fscr_spec/ROUTE_AUDIT/02_route_audit.out.json (route per skill file, 931 files)."],
    ["", "Run 04 ledger (16 adapter scorecard); Run 05 ledger (40-skill sample); Run 01-06 reports (measured times)."],
    ["Labels", "Source: 'earlier result (Run NN / route audit)' or 'computed now'. Quality: verified / not verified / unclear."],
    ["Area rule (computed now)", "Task area = pillar of its FSCR skill file(s); else the pillar(s) of the catalog offerings that contain it. 12 offerings have no pillar in FSCR's mapping: their 81 tasks show 'Unmapped offering'. 220 tasks are in no enabled offering."],
    ["Own script (computed now)", "The skill file's folder has a scripts/ folder with .py or .sh files."],
    ["Adapter (computed now)", "The skill file's folder has e2e-adapter.json (16 tasks; matches route audit and Run 04)."],
    ["Sheets", "1_Tasks, 2_Automation_today, 3_Routes, 4_Skills, 5_Support_summary, 6_Effort, 6b_Measured_times, 7_Not_already_known"],
]:
    ws.append(line)
ws.column_dimensions["A"].width = 26
ws.column_dimensions["B"].width = 140
ws["A1"].font = Font(bold=True, size=14)

# --- 1 Tasks
cols = list(tasks[0])
sheet("1_Tasks", cols, [[t[c] for c in cols] for t in tasks],
      [38, 40, 12, 30, 22, 9, 11, 11, 14, 8, 22, 8, 8, 20, 40, 40, 60])

# --- 2 Automation today
STAT = sorted(S["status_by_area"])
rows = []
for st in STAT:
    c = S["status_by_area"][st]
    rows.append([st] + [c.get(a, 0) for a in AREAS] + [sum(c.values())])
rows.append(["Total"] + [sum(S["status_by_area"][st].get(a, 0) for st in STAT) for a in AREAS] + [S["tasks"]])
ws2 = sheet("2_Automation_today", ["Status (2,616 catalog tasks, each in one status)"] + AREAS + ["Total"], rows,
            [52] + [11] * len(AREAS) + [9])
notes = [
    [],
    ["Source", "Statuses 1-3: Run 04 scorecard (earlier result, Run 04; verified on ETIA-TEST). Statuses 4-7: computed now from the route audit (earlier result) and the catalog flag."],
    ["Status 1", "6 adapters created a record: S1 AR payment terms (Run 01, patched), S2 Payables calendars, S3 AP payment terms (1-line patch), S8 AutoInvoice grouping rules, S12 Transaction types, S14 Transaction sources. Verified."],
    ["Status 2", "S4 Bank charges, S9 Remit-to, S11 Conversion rates (blocked by FSCR guards), S10 Receipt classes (failed, release drift). Verified."],
    ["Status 3", "S5, S6, S7, S13, S15, S16 need a business unit with a ledger; none safe on the pod. Not tested."],
    ["Status 4", "A skill or task guide names a route (FSM CSV, REST, HDL, FBDI, ESS, CX import) but no create recipe; Run 05 found 0 of 40 sampled skills with a complete recipe (earlier result, Run 05). Includes DOO_MANAGE_ORCHESTRATION_LOOKUPS, whose REST route we used with our own request bodies (Runs 01, 03, 06) and FUN_MANAGE_BUSINESS_UNIT (our builder, Run 01)."],
    ["Status 6", "No skill, but the catalog CSV flag is Y, so FSCR's generic task-level export can read it. Not verified per task: the export worked for every task we tried (20 of 20 sampled in Run 05, plus the Run 01-04/06 tasks)."],
    ["Status 7", "No skill and CSV flag N or UNKNOWN: FSCR offers nothing for these tasks."],
    ["Area 'Multiple'", "Task sits in offerings of several pillars (or has skills in two pillars); 'Unmapped offering' and 'No offering' see README."],
]
for n in notes:
    ws2.append(n)

# --- 3 Routes
ROUTE_FILES = {"FSM_CSV": 739, "REST": 473, "HDL": 43, "ESS": 27, "FBDI": 9, "CX_IMPORT": 5, "MANUAL_ONLY": 12, "NONE_DECLARED": 17, "UNCLEAR": 1}
rows = []
for r in ["FSM_CSV", "REST", "HDL", "FBDI", "ESS", "CX_IMPORT", "MANUAL_ONLY", "NONE_DECLARED", "UNCLEAR"]:
    c = S["route_tasks_by_area"].get(r, {})
    rows.append([r, ROUTE_FILES[r], "earlier result (route audit)"] + [c.get(a, 0) for a in AREAS] + [sum(c.values()), NOW])
rows.append(["SOAP", "not a route-audit category", "-"] + ["-"] * len(AREAS) +
             ["-", "Not already known. FSCR's only SOAP code is the customer reader (read only; Runs 01-02). Our customer creates/updates used our own SOAP (Runs 01, 03)."])
rows.append(["Browser / UI automation", 0, "earlier result (route audit; 47 files forbid it)"] + ["-"] * len(AREAS) + [0, "earlier result"])
ws3 = sheet("3_Routes", ["Route", "Skill files declaring it", "Source (files)"] + AREAS + ["Tasks declaring it", "Source (tasks)"], rows,
            [22, 16, 26] + [10] * len(AREAS) + [12, 50])
for n in [
    [],
    ["Notes", "A task or file can declare several routes, so rows do not add up (route audit: 384 files have more than one route)."],
    ["REST", "Of 473 REST files, 201 count only because depends_on names a REST client (may be reads only) and 227 are a Data Loader business-object import (earlier result, route audit). Accuracy sample: 2 of 10 REST files name a POST for the setup object (earlier result, route audit)."],
    ["Tasks with no skill", f"{sum(S['no_skill_by_flag'].values())} tasks have no skill: CSV flag Y {S['no_skill_by_flag'].get('Y', 0)}, N {S['no_skill_by_flag'].get('N', 0)}, UNKNOWN {S['no_skill_by_flag'].get('UNKNOWN', 0)} ({NOW}). For flag Y, FSM CSV export/import is Oracle's own option even without FSCR guidance."],
    ["FBDI on the pod", "ETIA-TEST's Data Loader has 353 objects, 0 FBDI (earlier result, Run 01; verified)."],
    ["HDL", "No HDL builder ships with FSCR (earlier result, Run 05)."],
]:
    ws3.append(n)

# --- 4 Skills (934 leaf)
cols = list(skills[0])
sheet("4_Skills", cols, [[s[c] for c in cols] for s in skills], [70, 40, 9, 14, 12, 40, 40, 24, 9, 9, 20])

# --- 5 Support summary
L = S["status_by_area"]
def tot(k):
    return sum(L[k].values())
st = {k[0]: tot(k) for k in L}
rows = [
    ["Supports today (create through FSCR's own chain)", st["1"], "tasks whose adapter created a record in our tests (6 of 16 adapters)", "earlier result (Run 04)", "verified"],
    ["Supports today, with our request bodies", 1, "task DOO_MANAGE_ORCHESTRATION_LOOKUPS: FSCR REST route and client, our bodies (8 creates R01, 5 changes R03, 3 R06)", "earlier result (Runs 01, 03, 06)", "verified"],
    ["Adapter exists but did not work here", st["2"], "2 blocked by FSCR guards + 1 FSCR guard after a defect + 1 failed on release drift", "earlier result (Run 04)", "verified"],
    ["Adapter exists, untested", st["3"], "need a business unit with a ledger", "earlier result (Run 04)", "not verified"],
    ["Can only read (generic export)", S["csv_flag"]["Y"], "catalog tasks with CSV flag Y; FSCR's task-level export reads them", "catalog count: earlier result (route audit); per task: not verified, 20 of 20 sampled worked (Run 05)", "not verified"],
    ["...of which no skill at all (read only, nothing else)", st["6"], "no skill, CSV flag Y", NOW, "not verified"],
    ["Only advises (route named, no create recipe)", st["4"], "skill or task guide names a route; Run 05: 0 of 40 had a complete recipe, median template-field coverage 0%", "count computed now; recipe finding earlier result (Run 05)", "verified (count); sample-based (recipe)"],
    ["Only advises (manual steps or no route)", st["5"], "skill gives UI steps or declares no route", NOW, "verified (count)"],
    ["Cannot do: no skill and no CSV route", st["7"], "no skill, CSV flag N or UNKNOWN", NOW, "verified (count)"],
    ["Cannot do: HDL tasks (no builder)", S["hdl_tasks"], "tasks declaring HDL; FSCR ships no HDL builder", "count computed now; no builder: earlier result (Run 05)", "verified"],
    ["Cannot do on this pod: FBDI tasks", S["fbdi_tasks"], "tasks declaring FBDI; pod has 0 FBDI loader objects", "count computed now; pod: earlier result (Run 01)", "verified"],
    ["Cannot do: price lists (read or create)", 1, "only task CUSTOM_IMPORT_PRICE_LISTS (FBDI import); no read route, no REST route", "earlier result (Runs 01, 02)", "verified"],
    ["Cannot do: customers (create/update), person customers", 3, "AR_MANAGE_CUSTOMERS, AR_CREATE_CUSTOMER, ORA_FOS_IMPORT_CUSTOMER have no skill; FBDI customer skill self-blocked", "earlier result (route audit, Run 01)", "verified"],
    ["Cannot do: business-unit update", 1, "FUN_MANAGE_BUSINESS_UNIT rule registry is create-only", "earlier result (Run 03)", "verified"],
]
sheet("5_Support_summary", ["Statement", "Number", "What the number counts", "Source", "Label"], rows, [48, 9, 70, 50, 20])

# --- 6 Effort
E = [
    ["FSM CSV file builder for tasks with an FSM route but no adapter", S["fsm_no_adapter"], NOW,
     "2-12 min per task (one-off builder, single object)", "measured: BU builder R01 4.4 min of calls, 12 min wall incl. ~5 min gate; BU update builder R03 ~2 min (adapted)",
     f"estimate: {S['fsm_no_adapter']} x 2-12 min = {S['fsm_no_adapter']*2/60:.0f}-{S['fsm_no_adapter']*12/60:.0f} h", "extrapolates from 2 single-object BU builders; multi-object tasks and a reusable adapter (~1,800 lines, Run 05) were never built: unclear"],
    ["Request bodies for tasks with a REST route but no adapter", S["rest_no_adapter"], NOW,
     "1-5 min per task (1-2 with a known endpoint; up to ~5 with discovery)", "measured: 8 lookup creates R01 ~2 min (1.9 min of calls) after ~3 min discovery; 5 PATCHes R03 ~2 min; R06 R1-R3 inside ~8 min",
     f"estimate: {S['rest_no_adapter']} x 1-5 min = {S['rest_no_adapter']/60:.0f}-{S['rest_no_adapter']*5/60:.0f} h", "extrapolates from lookups only; route audit: only 2 of 10 sampled REST files name a POST, so endpoint discovery time is unclear"],
    ["Patch adapters with release drift", 6, "earlier result (Run 04: 6 of 16 built on 26.04/26.07/27.01)",
     "0.6-4.1 min per patch", "measured: S3 1-line reconcile patch 4.1 min segment; S9 host-check patch 0.6 min; S10 patch 0.7 min (did not resolve)",
     "measured range, per patch", "S10 could not be fixed without bypassing an FSCR safety rule"],
    ["Price lists REST adapter (create, approve, update)", 1, "earlier result (route audit: only CUSTOM_IMPORT_PRICE_LISTS)",
     "~6 min for create + approve + update", "measured: create 4.0 min of calls R01 (incl. 3 rejected); approve PATCH ~1 min R01 follow-up 2; update PATCH ~1 min R03 C5",
     "measured (one-off code)", "needs Pricing BU data access first (security change, R01)"],
    ["Customers SOAP adapter (org + person + address purposes)", 3, "earlier result (route audit: 3 customer tasks, no skill)",
     "~18 min create; ~1 min update", "measured: customers_soap.py R01 17.8 min of calls (18 min) incl. live debugging; soap_update.py R03 C6 ~1 min",
     "measured (one-off code)", "making it FSCR-style (preview, approval, reconcile) not built: estimate not possible"],
    ["Gap analysis: new requirements vs current setup", "per request", "earlier result (Run 06)",
     "~8 min for 6 requirements incl. apply and verify", "measured: R06 22:07-22:14 after sign-in", "measured", "6 small requirements in two areas only"],
    ["Builders for tasks with no skill but CSV flag Y", st["6"], NOW,
     "2-12 min per task", "same basis as row 1 (BU builders)", f"estimate: {st['6']} x 2-12 min = {st['6']*2/60:.0f}-{st['6']*12/60:.0f} h",
     "estimate; these tasks have no FSCR rules either, so field discovery time is unclear"],
    ["HDL builder", S["hdl_tasks"], NOW, "-", "never built", "not already known", "no measured time"],
    ["FBDI route (needs pod FBDI registration + Oracle templates)", S["fbdi_tasks"], NOW, "-", "never built", "not already known", "no measured time; pod has 0 FBDI objects"],
    ["ESS job routes", sum(S["route_tasks_by_area"].get("ESS", {}).values()), NOW, "-", "never built", "not already known", "no measured time"],
    ["Unblock FSCR guards (Bank charges, Remit-to, Conversion rates)", 3, "earlier result (Run 04)", "-", "not built (bypassing guards was not allowed)", "not already known", "needs FSCR design changes"],
    ["Safe test business unit with a ledger (6 untested adapters)", 6, "earlier result (Run 04)", "-", "not built", "not already known", "pod setup / security, outside our tests"],
]
sheet("6_Effort", ["Missing piece", "Tasks affected", "Source of task count", "Time per task (measured)", "What was measured", "Total", "Limits"], E,
      [46, 10, 34, 28, 60, 30, 50])

# --- 6b Measured times
M = [
    ["Run 01", "BU file builder + FSCR import (2 BUs)", "4.4 min of calls; 12 min wall (~5 min Task Hook / Run Book gate)", "FSCR_Creation_Tokens.md; Run 01 report"],
    ["Run 01", "Payment terms through FSCR chain (2 terms)", "2.7 min of calls; ~7 min wall", "same"],
    ["Run 01", "Lookup types, codes, order types by REST (8 records)", "1.9 min of calls (0.2+0.3+0.3+1.1 shared); ~2 min after ~3 min discovery", "same"],
    ["Run 01", "Price lists by own REST (incl. 3 rejected)", "4.0 min of calls", "same"],
    ["Run 01", "Customers, persons, purposes by own SOAP (10 records)", "17.8 min of calls; 18 min wall", "same"],
    ["Run 01", "Whole run active", "51 min (98 wall, 47 sign-in wait)", "Run 01 report"],
    ["Run 02", "Read 8 areas, whole run", "24 min", "Run 02 report"],
    ["Run 03", "C2 lookups 3 PATCH / C3 order types 2 PATCH", "~1 min each (ledger, approximate)", "Run 03 ledger"],
    ["Run 03", "C4 BU update builder (adapted)", "~2 min (ledger, approximate)", "Run 03 ledger"],
    ["Run 03", "C5 price-list PATCH script / C6 SOAP update script", "~1 min each (ledger, approximate)", "Run 03 ledger"],
    ["Run 03", "Whole run active", "24 min (about 28 with final compare; 60 elapsed)", "Run 03 report"],
    ["Run 04", "S2 / S3 / S8 / S12 / S14 create segments", "4.3 / 4.1 / 2.9 / 6.2 / 3.5 min", "FSCR_Creation_Tokens.md"],
    ["Run 04", "S9 / S10 patch segments", "0.6 / 0.7 min", "same"],
    ["Run 04", "Whole run", "about 33 min; 4-7 min per working skill", "Run 04 report"],
    ["Run 05", "Sample and grade 40 skills, 40 exports", "28 min", "Run 05 report"],
    ["Route audit", "Classify routes for 931 skill files", "29 min", "ROUTE_AUDIT/REPORT.md"],
    ["Run 06", "6 requirements: read, gap analysis, 4 applies, verify", "~8 min after sign-in (14 min wall)", "Run 06 report"],
]
sheet("6b_Measured_times", ["Run", "What was built or done", "Time", "Source"], M, [12, 56, 60, 34])

# --- 7 Not already known
NK = [
    ["Whether FSCR's export works for every CSV-flag task", f"Only the {sum(bool(t['Tested in our runs']) for t in tasks)} tasks marked in 1_Tasks 'Tested in our runs' were exported or used (20 in Run 05); the rest were never tried."],
    ["Build time for a reusable FSCR-style adapter", "We never built one; we only patched existing adapters and wrote one-off builders."],
    ["Build time for HDL, FBDI or ESS routes", "Never built or run in Runs 01-06."],
    ["Whether 'route named' REST skills have working endpoints", "Route audit checked only 10 REST files (2 named a POST)."],
    ["Template-field coverage for all skills", "Measured only for 20 tasks in Run 05 (median 0%)."],
    ["Area of 81 tasks in 12 offerings with no pillar", "FSCR's pillars-offerings-mapping.json leaves those offerings blank; assigning one would be a guess."],
    ["Area of 220 tasks in no enabled offering", "Not in the offering catalog, so no pillar can be joined."],
    ["SOAP routes per task", "The route audit has no SOAP category; finding them needs a new repo scan."],
    ["Whether the 6 no-safe-target adapters work", "Not run: no business unit with a ledger could be used safely."],
    ["Whether customer and price-list FBDI routes work on a pod with FBDI registered", "ETIA-TEST has 0 FBDI objects; not testable here."],
]
sheet("7_Not_already_known", ["Item", "Why it is not known"], NK, [60, 100])

wb.save(os.path.join(RUN, "FSCR_Inventory.xlsx"))
print("saved")
