"""Build 02_WAVE_PLAN.xlsx (Twelve) in the GoSaaS instance-plan layout. Paper planning only."""
import datetime as dt, sys
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = sys.argv[1]
START = dt.date(2025, 2, 17)            # given input (Monday)
NWEEKS = 24                              # show through week of 28 Jul 2025
WEEKS = [START + dt.timedelta(weeks=i) for i in range(NWEEKS)]

FILL = {
    "Design":    "D9D9D9",  # design / workshops (SUGGESTED)
    "Configure": "9BC2E6",  # blue
    "Load":      "F4B183",  # orange  (Data Load / Delta)
    "CRP":       "A9D08E",  # green
    "UAT":       "B4A7D6",  # purple
    "GoLive":    "FF6666",  # red
    "Update":    "BF9000",  # dark gold (Oracle quarterly update)
    "Refresh":   "FFE699",  # light yellow
    "Hyper":     "E2EFDA",  # pale green (hypercare)
    "Calendar":  "F2F2F2",
}
LEGEND = [("Design", "Design workshops / sign-off (SUGGESTED length)"), ("Configure", "Configure (build / migrate configuration)"),
          ("Load", "Data Load / Delta (supplier conversion, partial or full, delta)"), ("CRP", "CRP test cycle"),
          ("UAT", "UAT test cycle"), ("GoLive", "Go-Live / cutover week"), ("Update", "Oracle quarterly update week (cohort key)"),
          ("Refresh", "Environment refresh (SUGGESTED)"), ("Hyper", "Hypercare (SUGGESTED, not in SOW)")]

thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
BOLD = Font(bold=True)


def nth_friday(y, m, n):
    d = dt.date(y, m, 1)
    d += dt.timedelta((4 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def week_of(date):
    """1-based week index in plan (Monday-start); may be <1 or >NWEEKS."""
    return (date - START).days // 7 + 1


COHORTS = {"A": [(2025, 2, "25A"), (2025, 5, "25B"), (2025, 8, "25C")],
           "B": [(2025, 3, "25A"), (2025, 6, "25B")],
           "C": [(2025, 1, "24D"), (2025, 4, "25A"), (2025, 7, "25B")]}
UPDATES = {}  # cohort -> list of (env, date, week, release)
for c, months in COHORTS.items():
    UPDATES[c] = []
    for y, m, rel in months:
        for env, n in (("Non-prod (Dev/Test)", 1), ("Prod", 3)):
            f = nth_friday(y, m, n)
            UPDATES[c].append((env, f, week_of(f), rel))

# ---------------- plans ----------------
# Each activity: (row, kind, label, first_week, last_week)
PLAN_12 = {
    "name": "12-week plan (SOW C.8)",
    "acts": [
        ("Project phase", "Design", "Kickoff + design workshops (SUGGESTED 3 wks, parallel streams)", 1, 3),
        ("Project phase", "Design", "Design sign-off (SUGGESTED)", 3, 3),
        ("Development (SUGGESTED)", "Configure", "Configure CRP1 build", 2, 3),
        ("Development (SUGGESTED)", "Load", "Partial data load (suppliers subset)", 3, 3),
        ("Development (SUGGESTED)", "CRP", "CRP1: partial data, no security, no customizations", 4, 5),
        ("Development (SUGGESTED)", "Configure", "Fix config from CRP1", 6, 6),
        ("Refresh (SUGGESTED)", "Refresh", "P2T refresh before Test build (SR lead time)", 5, 5),
        ("Test (SUGGESTED)", "Configure", "Migrate config + security + PO print report", 6, 6),
        ("Test (SUGGESTED)", "Load", "Full supplier load + validate + smoke test", 6, 6),
        ("Test (SUGGESTED)", "CRP", "CRP2: full data, full security + customizations", 7, 8),
        ("Test (SUGGESTED)", "Configure", "Fix config from CRP2", 9, 9),
        ("Test (SUGGESTED)", "Load", "Delta load + validate", 9, 9),
        ("Test (SUGGESTED)", "UAT", "UAT: full data + delta; cutover rehearsal", 10, 11),
        ("Production", "Configure", "Twelve migrates approved config to Prod (SOW C.10)", 9, 11),
        ("Production", "Load", "Full supplier load + delta", 11, 12),
        ("Production", "GoLive", "Go-Live (cutover, 1 wk)", 12, 12),
        ("Production", "Hyper", "Hypercare (SUGGESTED, not in SOW)", 13, 14),
    ],
}
PLAN_16 = {
    "name": "16-week alternative (SUGGESTED, 2-week gaps)",
    "acts": [
        ("Project phase", "Design", "Kickoff + design workshops (SUGGESTED 3 wks)", 1, 3),
        ("Development (SUGGESTED)", "Configure", "Configure CRP1 build", 3, 5),
        ("Development (SUGGESTED)", "Load", "Partial data load", 5, 5),
        ("Development (SUGGESTED)", "CRP", "CRP1: partial data, no security, no customizations", 6, 7),
        ("Development (SUGGESTED)", "Configure", "Fix config from CRP1", 8, 9),
        ("Refresh (SUGGESTED)", "Refresh", "P2T refresh before Test build", 8, 8),
        ("Test (SUGGESTED)", "Configure", "Migrate config + security + PO print", 9, 9),
        ("Test (SUGGESTED)", "Load", "Full load + validate + smoke", 9, 9),
        ("Test (SUGGESTED)", "CRP", "CRP2: full data, security, customizations", 10, 11),
        ("Test (SUGGESTED)", "Configure", "Fix config from CRP2", 12, 13),
        ("Test (SUGGESTED)", "Load", "Delta load + validate", 13, 13),
        ("Test (SUGGESTED)", "UAT", "UAT: full data + delta", 14, 15),
        ("Production", "Configure", "Twelve migrates config to Prod (C.10)", 13, 15),
        ("Production", "Load", "Full load + delta", 15, 16),
        ("Production", "GoLive", "Go-Live (1 wk)", 16, 16),
        ("Production", "Hyper", "Hypercare (SUGGESTED)", 17, 18),
    ],
}
ROWS = ["Project phase", "Production", "Test (SUGGESTED)", "Development (SUGGESTED)", "Refresh (SUGGESTED)"]
CAL = [  # calendar notes (verifiable dates; relevance SUGGESTED)
    (dt.date(2025, 2, 17), "US holiday: Presidents' Day = given start date"),
    (dt.date(2025, 3, 31), "Calendar Q1 end (fiscal year not stated)"),
    (dt.date(2025, 5, 1), "April month-end close (live Financials)"),
    (dt.date(2025, 5, 26), "US holiday: Memorial Day"),
    (dt.date(2025, 6, 30), "Calendar Q2 end"),
    (dt.date(2025, 7, 4), "US holiday: Independence Day"),
]


def env_of(row):
    return "Prod" if row == "Production" else ("Non-prod (Dev/Test)" if row.startswith(("Test", "Development")) else None)


def conflicts(plan, cohort):
    res = []
    for env, date, wk, rel in UPDATES[cohort]:
        for row, kind, label, a, b in plan["acts"]:
            if kind in ("Design",) or env_of(row) != env:
                continue
            if kind not in ("CRP", "UAT", "Load", "GoLive", "Configure", "Hyper"):
                continue
            if a <= wk <= b:
                rel_pos = "IN update week"
            elif wk == a - 1 or wk == b + 1:
                rel_pos = "NEXT TO update week"
            else:
                continue
            res.append((cohort, env, date, wk, rel, row, kind, label, a, b, rel_pos))
    return res


def header(ws, title, first_col=3):
    ws["A1"] = title; ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = "Week #"; ws["A3"] = "Week of (Mon)"; ws["A4"] = "Plan week"
    for i, w in enumerate(WEEKS):
        c = first_col + i
        ws.cell(2, c, f"W{i+1}" if i < 12 else f"W{i+1}")
        ws.cell(3, c, w).number_format = "d-mmm"
        ws.cell(4, c, "in SOW 12" if i < 12 else "beyond 12")
        for r in (2, 3, 4):
            ws.cell(r, c).alignment = Alignment(horizontal="center"); ws.cell(r, c).font = BOLD; ws.cell(r, c).border = BORDER
        ws.column_dimensions[get_column_letter(c)].width = 11
    ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 16
    ws.freeze_panes = ws.cell(5, first_col)


def paint(ws, r, wk, kind, text, first_col=3):
    if 1 <= wk <= NWEEKS:
        cell = ws.cell(r, first_col + wk - 1)
        cell.fill = PatternFill("solid", fgColor=FILL[kind])
        cell.value = (cell.value + " / " + text) if cell.value else text
        cell.alignment = Alignment(wrap_text=True, vertical="top", horizontal="center")
        cell.font = Font(size=8); cell.border = BORDER


def plan_sheet(wb, plan):
    ws = wb.create_sheet(plan["name"][:31])
    header(ws, f"Twelve – Oracle Cloud SCM – Instance Plan – {plan['name']} (start Mon 17-Feb-2025, given)")
    r = 5
    rowidx = {}
    for row in ROWS:
        ws.cell(r, 1, row).font = BOLD
        ws.cell(r, 2, {"Production": "prod (live Financials)", "Test (SUGGESTED)": "-test (not in SOW)",
                       "Development (SUGGESTED)": "-dev (SOW E.6 'development')", "Project phase": "",
                       "Refresh (SUGGESTED)": "SR to Oracle"}[row])
        ws.row_dimensions[r].height = 42
        rowidx[row] = r; r += 1
    for row, kind, label, a, b in plan["acts"]:
        short = {"Design": "Sign-off" if "sign-off" in label.lower() else "Design", "Configure": "Configure", "Load": "Load", "CRP": label.split(":")[0],
                 "UAT": "UAT", "GoLive": "GO-LIVE", "Refresh": "Refresh", "Hyper": "Hypercare"}[kind]
        for wk in range(a, b + 1):
            paint(ws, rowidx[row], wk, kind, short)
    r += 1
    ws.cell(r, 1, "Oracle update weeks (cohort key from GoSaaS template; NOT confirmed for Twelve)").font = BOLD; r += 1
    for c in "ABC":
        for env in ("Non-prod (Dev/Test)", "Prod"):
            ws.cell(r, 1, f"Cohort {c} – {env}")
            ws.cell(r, 2, "1st Friday" if env.startswith("Non") else "3rd Friday")
            for e, date, wk, rel in UPDATES[c]:
                if e == env:
                    paint(ws, r, wk, "Update", f"{rel} {date:%d-%b}")
            r += 1
    r += 1
    ws.cell(r, 1, "Calendar notes (SUGGESTED relevance)").font = BOLD
    for date, text in CAL:
        paint(ws, r, week_of(date), "Calendar", text)
    ws.row_dimensions[r].height = 60
    ws = wb.create_sheet(("Activities " + plan["name"].split(" ")[0])[:31])
    r = 1
    ws.cell(r, 1, f"Activity list – {plan['name']}").font = BOLD; r += 1
    for col, w in zip("ABCDEFGH", [26, 11, 60, 10, 10, 14, 14, 7]):
        ws.column_dimensions[col].width = w
    for col, h in enumerate(["Environment", "Block", "Activity", "From week", "To week", "From (Mon)", "To (Fri)", "Weeks"], 1):
        ws.cell(r, col, h).font = BOLD
    r += 1
    for row, kind, label, a, b in plan["acts"]:
        vals = [row, kind, label, f"W{a}", f"W{b}", WEEKS[a-1], WEEKS[b-1] + dt.timedelta(days=4), b - a + 1]
        for col, v in enumerate(vals, 1):
            cell = ws.cell(r, col, v)
            if isinstance(v, dt.date): cell.number_format = "dd-mmm-yyyy"
        ws.cell(r, 2).fill = PatternFill("solid", fgColor=FILL[kind])
        r += 1
    return ws


wb = Workbook()
ws0 = wb.active; ws0.title = "README"
readme = [
    "Twelve – Oracle Cloud SCM Implementation – Wave / Instance Plan (FSCR Run 15, paper planning only)",
    "Produced by: Claude alone (FSCR implementation-wave-planner, readiness-checklist-generator and instance-strategy skills are empty placeholders).",
    "Inputs: SOW dated 24-Jan-2025 (Doc 50513scm); Run 14 intake outputs; GoSaaS Scoping Checklist + methodology capture (01_checklists_capture.txt); instance plan TEMPLATES section + cohort key (02 capture, top section only).",
    "Layout follows the GoSaaS instance plan template: one row per environment (Production, Test, Development), one column per week, coloured blocks, Oracle update rows.",
    "Test and Development rows are SUGGESTED: the SOW (E.6) names only 'development and production platforms'; the checklist recommends Dev/Test/Production = 3.",
    "Start date Monday 17-Feb-2025 is a given input (not in the SOW). Note: it is the US Presidents' Day holiday.",
    "Every duration not fixed by the GoSaaS cycle rules is labelled SUGGESTED and listed on the 'Assumptions & Open Qs' sheet.",
    "Oracle update weeks use the template key (A=Feb/May/Aug/Nov, B=Mar/Jun/Sep/Dec, C=Apr/Jul/Oct/Jan; non-prod 1st Friday, prod 3rd Friday). Twelve's cohort is NOT known: all three are shown. Release labels (24D/25A/25B/25C) are Claude's inference. A person must confirm the cohort and dates against Oracle's published schedule (SR).",
    "Sheets: '12-week plan (SOW C.8)' = main plan; '16-week alternative' = SUGGESTED fallback; 'Fit arithmetic'; 'Update conflicts'; 'Assumptions & Open Qs'; 'Legend'.",
]
for i, t in enumerate(readme, 1):
    ws0.cell(i, 1, t)
ws0.column_dimensions["A"].width = 160

plan_sheet(wb, PLAN_12)
plan_sheet(wb, PLAN_16)

# ---- fit arithmetic
ws = wb.create_sheet("Fit arithmetic")
fit = [
    ("Item", "Weeks", "Source / label"),
    ("A. Checklist-faithful model", "", ""),
    ("Design workshops (parallel streams)", 3, "SUGGESTED (checklist: 1 wk per module, 11 modules + Security + DM + Reports + Sign-off; run in parallel)"),
    ("Configure + partial load for CRP1", 2, "SUGGESTED"),
    ("CRP1", 2, "GoSaaS cycle rule"),
    ("Between CRP1 and CRP2 (fix config 3, fix/cleanse data 3, config new env 1, extract 0, validate 1, load 2, smoke 1; checklist total)", 7, "Scoping Checklist"),
    ("CRP2", 2, "GoSaaS cycle rule"),
    ("Between CRP2 and UAT", 7, "Scoping Checklist"),
    ("UAT", 2, "GoSaaS cycle rule"),
    ("Between UAT and Go-Live", 7, "Scoping Checklist"),
    ("Go-Live", 1, "GoSaaS cycle rule"),
    ("TOTAL A = 3+2+2+7+2+7+2+7+1", "=SUM(B3:B11)", "33 weeks → does NOT fit 12 (over by 21)"),
    ("", "", ""),
    ("B. Test cycles alone (no design, no gaps)", "=B5+B7+B9+B11", "7 weeks of the 12"),
    ("Remaining for design + config + 3 gaps = 12 − 7", "=12-B14", "5 weeks"),
    ("", "", ""),
    ("C. 12-week plan drawn on main sheet", "", ""),
    ("Design (incl. config start W2–W3)", 3, "SUGGESTED"),
    ("CRP1 W4–W5", 2, "rule"),
    ("Gap 1 W6 (fix + Test build + full load)", 1, "SUGGESTED (checklist says 7)"),
    ("CRP2 W7–W8", 2, "rule"),
    ("Gap 2 W9 (fix + delta)", 1, "SUGGESTED (checklist says 7)"),
    ("UAT W10–W11", 2, "rule"),
    ("Go-Live W12 (Prod config by Twelve W9–W11, overlapping)", 1, "rule"),
    ("TOTAL C", "=SUM(B18:B24)", "12 weeks → fits only with 1-week gaps (checklist 7) and 3-week design"),
    ("", "", ""),
    ("D. 16-week alternative (2-week gaps)", "", ""),
    ("3 design + 2 config + 2 CRP1 + 2 gap + 2 CRP2 + 2 gap + 2 UAT + 1 go-live (Prod config overlaps gap 2/UAT)", 16, "SUGGESTED"),
    ("", "", ""),
    ("Hours check (SOW D)", "", ""),
    ("Total SOW hours", 3820, "SOW D (sum verified)"),
    ("SCM Architect 640 h / 40 h per wk", "=640/40", "16 weeks of one full-time architect → exceeds 12 weeks at 40 h/wk (needs >53 h/wk or > 1 person)"),
    ("PMO Analyst 320 h / 12 wks", "=320/12", "≈26.7 h/wk"),
    ("Inventory, Mfg/Maint, Procurement consultants 560 h each / 12 wks", "=560/12", "≈46.7 h/wk each"),
    ("Conclusion", "", "12 weeks fits ONLY the compressed plan C (gaps 1 wk vs checklist 7; no CRP3; single Test env). SCM Architect hours imply ~16 weeks at 40 h/wk. Risk flagged; see open questions."),
]
for i, row in enumerate(fit, 1):
    for j, v in enumerate(row, 1):
        ws.cell(i, j, v)
    if i == 1 or (row[1] == "" and row[0]):
        ws.cell(i, 1).font = BOLD
ws.column_dimensions["A"].width = 95; ws.column_dimensions["B"].width = 12; ws.column_dimensions["C"].width = 110

# ---- update conflicts
ws = wb.create_sheet("Update conflicts")
hdr = ["Plan", "Cohort", "Update env", "Update Friday", "Plan week", "Release (inferred)", "Activity env", "Block", "Activity", "Activity weeks", "Position"]
for j, h in enumerate(hdr, 1):
    ws.cell(1, j, h).font = BOLD
r = 2
all_conf = {}
for plan in (PLAN_12, PLAN_16):
    for c in "ABC":
        cs = conflicts(plan, c)
        all_conf[(plan["name"], c)] = cs
        if not cs:
            ws.cell(r, 1, plan["name"]); ws.cell(r, 2, c); ws.cell(r, 9, "no test cycle / load / go-live in or next to an update week"); r += 1
        for (co, env, date, wk, rel, row, kind, label, a, b, pos) in cs:
            vals = [plan["name"], co, env, date, f"W{wk}", rel, row, kind, label, f"W{a}–W{b}", pos]
            for j, v in enumerate(vals, 1):
                cell = ws.cell(r, j, v)
                if isinstance(v, dt.date): cell.number_format = "ddd dd-mmm-yyyy"
            ws.cell(r, 8).fill = PatternFill("solid", fgColor=FILL[kind])
            r += 1
r += 1
ws.cell(r, 1, "Recommended shifts – 12-week plan (Claude, SUGGESTED; confirm cohort first)").font = BOLD; r += 1
RECS = [
    ("A", "Prod 21-Feb (W1, 25A): no project activity in Prod; regression-check live Financials only. "
          "Non-prod 02-May (W11, 25B): last day of UAT. Close UAT sign-off by Thu 01-May; do not run cutover rehearsal on 02-May. "
          "Prod 16-May (W13, 25B): first week of hypercare, Test already on 25B from 02-May → plan a 25B regression in Test W12 and keep go-live W12 (Prod still 25A at cutover). "
          "Alternative: request Oracle to align Test update with Prod or move go-live to after 16-May (W14)."),
    ("B", "Non-prod 07-Mar (W3, 25A): last week of Dev configuration, next to CRP1 (W4). Freeze Dev config Thu 06-Mar, smoke-test Mon 10-Mar, start CRP1 Tue 11-Mar. "
          "Prod 21-Mar (W5): no project load in Prod yet; no shift. Next updates Jun (W16/W18) are after go-live. B is the lowest-risk cohort for this plan."),
    ("C", "Non-prod 04-Apr (W7, 25A): end of CRP2 week 1 in Test. Shift: move the full Test load to Mon 07-Apr after the update, run CRP2 W8–W9 and compress gap 2 into CRP2 (fixes in Dev during CRP2), UAT W10–W11 unchanged. "
          "Prod 18-Apr (W9, 25A): first week of Prod config migration by Twelve → start Prod migration Mon 21-Apr (W10). "
          "If no compression is acceptable, push UAT/go-live by 1 week (go-live W13)."),
]
for c, t in RECS:
    ws.cell(r, 1, f"Cohort {c}"); ws.cell(r, 2, t); r += 1
r += 1
ws.cell(r, 1, "16-week alternative: conflicts are listed above; shifts not worked out (alternative only).")
for col, w in zip("ABCDEFGHIJK", [30, 8, 18, 18, 9, 10, 22, 10, 50, 12, 20]):
    ws.column_dimensions[col].width = w

# ---- assumptions
ws = wb.create_sheet("Assumptions & Open Qs")
AQ = [
    ("ID", "Assumption / question", "Label", "Basis"),
    ("WP-1", "Project start Monday 17-Feb-2025. It is the US Presidents' Day holiday: kickoff Tue 18-Feb?", "GIVEN input; holiday note verified (calendar)", "User input"),
    ("WP-2", "Three environments Prod/Test/Dev. SOW E.6 names only development and production. Does Twelve have (or will it buy) a Test pod?", "SUGGESTED", "Checklist: Dev/Test/Production = 3 recommended"),
    ("WP-3", "Design workshops 3 weeks in parallel streams (checklist: 1 wk per module ≈ 11 modules + Security + DM + Reports + Sign-off).", "SUGGESTED", "Checklist Planning; open question"),
    ("WP-4", "Configure for CRP1 in Dev W2–W3, overlapping design.", "SUGGESTED", "Claude"),
    ("WP-5", "CRP1 in Dev (partial data, no security, no customizations); CRP2 and UAT in Test.", "SUGGESTED", "GoSaaS cycle rules + Claude env choice"),
    ("WP-6", "Gaps between cycles 1 week each (checklist total 7 weeks each). Accept the risk or extend to 16 weeks?", "SUGGESTED", "Fit arithmetic"),
    ("WP-7", "No CRP3 / mock migration: data migration is 'minimal' (suppliers only, SOW C.5, RICE 2).", "SUGGESTED", "SOW + checklist"),
    ("WP-8", "P2T refresh of Test from live Prod (Financials) before Test build in W5; lead time via SR. Is Prod data allowed in Test?", "SUGGESTED", "Checklist mentions refresh; Claude"),
    ("WP-9", "Twelve migrates approved config to Prod W9–W11 (SOW C.10). Twelve's capacity and method (FSM export/import vs manual) not stated.", "SOW fact + SUGGESTED timing", "SOW C.10"),
    ("WP-10", "Go-live W12 (5–9 May 2025) collides with April month-end close in live Financials. Move cutover to after close?", "SUGGESTED", "Claude (live Financials in Prod)"),
    ("WP-11", "Hypercare 2 weeks after go-live; not in SOW.", "SUGGESTED", "Checklist 'Post Go-Live: extended hypercare'"),
    ("WP-12", "Expenses decision (design session) by end of W2; if in, it joins CRP2 at the latest.", "SUGGESTED", "SOW Fin 5.1"),
    ("WP-13", "Twelve's Oracle update cohort and exact dates: open an SR (PM checklist) and confirm. Release labels are inferred.", "NOT KNOWN", "Template key"),
    ("WP-14", "Concurrent patching (Test and Prod same weekend) requested?", "SUGGESTED question", "Pre-sales checklist 'Move to concurrent patching'"),
    ("WP-15", "Quarter-end months / freeze periods (calendar Q1 ends 31-Mar in W7; fiscal year not stated).", "NOT KNOWN", "Checklist question"),
    ("WP-16", "Training (Train-the-Trainer, SOW B/C.6) placed during UAT W10–W11.", "SUGGESTED", "Claude"),
    ("WP-17", "SCM Architect 640 h ÷ 12 wks = 53 h/wk: confirm staffing or duration.", "Claude analysis", "SOW D arithmetic"),
]
for i, row in enumerate(AQ, 1):
    for j, v in enumerate(row, 1):
        ws.cell(i, j, v)
    if i == 1:
        for j in range(1, 5): ws.cell(i, j).font = BOLD
for col, w in zip("ABCD", [8, 120, 30, 50]):
    ws.column_dimensions[col].width = w

ws = wb.create_sheet("Legend")
for i, (k, t) in enumerate(LEGEND, 1):
    ws.cell(i, 1, "").fill = PatternFill("solid", fgColor=FILL[k]); ws.cell(i, 2, t)
ws.column_dimensions["B"].width = 70
wb.save(OUT)

for k, v in all_conf.items():
    print(k, len(v))
    for x in v:
        print("   ", x[1], x[2], "W%d" % x[3], x[4], "|", x[5], x[6], x[7][:45], "W%d-W%d" % (x[8], x[9]), "|", x[10])
