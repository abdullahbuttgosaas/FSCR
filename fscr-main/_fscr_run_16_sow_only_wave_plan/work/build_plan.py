# Builds 01_SOW_ONLY_WAVE_PLAN.xlsx from the data below (plain values, no formulas).
import os
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RUN, "01_SOW_ONLY_WAVE_PLAN.xlsx")
CL, FC = "Claude alone", "FSCR + Claude"
ENVS = ["PROJECT", "DEV", "TEST", "PROD"]
ENV_DESC = {
    "PROJECT": "PROJECT - project phase / team activities (not tied to one pod)",
    "DEV": "DEV - configuration & build pod (SUGGESTED separate non-prod pod; SOW E.6 names 'development ... platforms')",
    "TEST": "TEST - SIT / UAT / training pod (SUGGESTED; not named in SOW)",
    "PROD": "PROD - existing Production pod (SOW A: 'production Financials modules'; SOW C.10)",
}
COL = {"mob": "BFBFBF", "des": "9DC3E6", "cfg": "A9D08E", "bld": "70C1B3", "dat": "F4B183",
       "sit": "B4A7D6", "fix": "D9D9D9", "uat": "FFE699", "trn": "F8CBAD", "cut": "FF7C80",
       "hyp": "FFC7CE", "dec": "FFD966"}
PRIO = ["cut", "hyp", "uat", "sit", "fix", "dat", "cfg", "bld", "trn", "des", "dec", "mob"]

# (env, activity, short label, from, to, category, source, producer)
A = [
    ("PROJECT", "Mobilize, kickoff, environment access for GoSaaS", "Mobilize", 1, 1, "mob",
     "SOW cover: \"GoSaaS will commence the services ... after the Client-executed copy of this SOW has been received\"; SOW E.6/E.7 access. Week placement SUGGESTED", CL),
    ("PROJECT", "Design workshops: Business Scenarios, Requirements, Process Flows, Key Design Decisions, Configuration Templates (common design)", "Design", 1, 3, "des",
     "SOW B Scope: \"Scope includes the documentation of supporting Business Scenarios, Requirements, Process Flows, Key Design Decisions and Configurations Templates\"; SOW C.3 \"Common Design for all modules\". Length (3 wks) SUGGESTED", CL),
    ("PROJECT", "Expenses design session - decide in/out of scope", "Expenses decision", 2, 2, "dec",
     "SOW B Financials 5.1: \"A design session will be conducted for the Expenses module ... confirm if it will be in or out of scope\". Week SUGGESTED", CL),
    ("PROJECT", "Reporting Approach (OTBI / BIP / FDI / EPM)", "Reporting approach", 2, 5, "des",
     "SOW B Financials 6.1: \"Establish the future reporting usage between ... (OTBI), (BIP), Fusion Data Intelligence and (EPM)\". Timing SUGGESTED", CL),
    ("PROJECT", "Training material creation (new modules)", "Training materials", 7, 10, "trn",
     "SOW B Change Management 1: \"The creation of training material for newly implemented modules\"; SOW C.6. Timing SUGGESTED", CL),
    ("PROJECT", "Go / No-Go decision against refined Go-Live & Ready-to-Use criteria", "Go/No-Go", 11, 11, "dec",
     "SOW C.2.1: \"Go-Live & Ready to Use criteria will be refined during the project\". Week SUGGESTED", CL),
    ("DEV", "Base configuration: enterprise/BU updates, inventory orgs (2 plants), costing org & cost books", "Base config", 3, 3, "cfg",
     "SOW B Financials 3.1 (Requisitioning/Purchasing BUs), SOW B Scope 2.2 (Plant locations as Inventory Organizations), 2.3 (Costing Organization Structure and Cost Books), SOW C.7 (2 plants). Timing SUGGESTED", FC),
    ("DEV", "Module configuration & unit test: PIM, Self-Service Procurement, Purchasing, Supplier Portal, Inventory & Cost, Manufacturing, Maintenance, Sustainability, Expenses (if in), Payables / GL-SLA / Projects incremental, Security & Roles", "Configure + unit test", 4, 6, "cfg",
     "SOW B Configurations Scope items 1-12. Length (3 wks) SUGGESTED; sizing informed by FSCR setup-task catalog counts", FC),
    ("DEV", "Printable Purchase Order report: FDD, TDD, code & unit test", "PO report build", 4, 7, "bld",
     "SOW B RICE 1.1.1 \"A Printable Purchase Order\"; 1.2 FDD/TDD; 1.3.2 \"Creation of Technical Design, Code & Unit Test\". Timing SUGGESTED", CL),
    ("DEV", "Supplier conversion: FDD, TDD, build load template", "Supplier conv design", 3, 5, "bld",
     "SOW B RICE 2.1.1 \"Suppliers\"; 2.2 FDD/TDD. Timing SUGGESTED", CL),
    ("DEV", "Supplier mock load 1", "Mock load 1", 6, 6, "dat",
     "SOW C.5 \"Data migration efforts will be minimal\"; the mock load itself is SUGGESTED", CL),
    ("TEST", "Migrate approved configuration DEV -> TEST; supplier mock load 2", "Migrate + mock load 2", 7, 7, "dat",
     "SUGGESTED (SOW silent on non-production migration)", CL),
    ("TEST", "SIT round 1 (SCM end-to-end + Financials regression)", "SIT 1", 8, 8, "sit",
     "SOW E.1 Twelve responsible for \"testing functionality\"; SOW B Financials remediation scope (GL, AR, PPM, Grants, AP, CM, FA). Rounds & length SUGGESTED", CL),
    ("TEST", "SIT round 2 (regression + retest), no gap after SIT 1", "SIT 2", 9, 9, "sit",
     "SUGGESTED", CL),
    ("TEST", "UAT (Twelve-led) incl. retest of SIT defects", "UAT", 10, 11, "uat",
     "SOW E.1 \"testing functionality\" by Twelve. Length SUGGESTED", CL),
    ("TEST", "Train-the-Trainer sessions", "Train-the-trainer", 10, 11, "trn",
     "SOW B Change Management 2: \"GoSaaS will adopt the Train-the-Trainer approach\"; SOW C.6. Timing & pod SUGGESTED", CL),
    ("PROD", "Configuration migration to Production (by Twelve) + supplier load", "Prod migration + load", 12, 12, "cut",
     "SOW C.10: \"Approved configurations will be migrated to Production by Twelve\"; SOW B RICE 2.1.1 Suppliers. Week SUGGESTED", CL),
    ("PROD", "Go-live (end of SOW 12-week duration)", "Go-live", 12, 12, "cut",
     "SOW C.8 \"Duration - 12 weeks\". Go-live in Week 12 is SUGGESTED (SOW does not state a go-live week)", CL),
    ("PROD", "Hypercare / post-go-live support", "Hypercare", 13, 16, "hyp",
     "SUGGESTED - not in SOW scope, duration or hours", CL),
]
B = [
    ("PROJECT", "Mobilize, kickoff, environment access", "Mobilize", 1, 1, "mob", "SOW cover + SOW E.6/E.7. Timing SUGGESTED", CL),
    ("PROJECT", "Design workshops (Business Scenarios, Requirements, Process Flows, KDDs, Config Templates)", "Design", 1, 4, "des", "SOW B Scope; SOW C.3. Length (4 wks) SUGGESTED", CL),
    ("PROJECT", "Expenses design session - decide in/out of scope", "Expenses decision", 2, 2, "dec", "SOW B Financials 5.1. Week SUGGESTED", CL),
    ("PROJECT", "Reporting Approach (OTBI / BIP / FDI / EPM)", "Reporting approach", 3, 7, "des", "SOW B Financials 6.1, 6.2. Timing SUGGESTED", CL),
    ("PROJECT", "Training material creation", "Training materials", 11, 16, "trn", "SOW B Change Management 1; SOW C.6. Timing SUGGESTED", CL),
    ("PROJECT", "Go / No-Go decision", "Go/No-Go", 19, 19, "dec", "SOW C.2.1. Week SUGGESTED", CL),
    ("DEV", "Prototype / conference-room-pilot base config (enterprise/BU, inventory orgs, cost org & books)", "CRP base config", 3, 4, "cfg", "SOW B Financials 3.1, SOW B Scope 2.2, 2.3; SOW C.7. CRP approach SUGGESTED", FC),
    ("DEV", "Module configuration & unit test (Configurations Scope items 1-12)", "Configure + unit test", 5, 9, "cfg", "SOW B Configurations Scope 1-12. Length SUGGESTED; sizing informed by FSCR catalog counts", FC),
    ("DEV", "Printable PO report: FDD, TDD, code & unit test", "PO report build", 6, 9, "bld", "SOW B RICE 1. Timing SUGGESTED", CL),
    ("DEV", "Supplier conversion: FDD, TDD, load template", "Supplier conv design", 5, 8, "bld", "SOW B RICE 2. Timing SUGGESTED", CL),
    ("DEV", "Supplier mock load 1", "Mock load 1", 9, 9, "dat", "SOW C.5; mock load SUGGESTED", CL),
    ("TEST", "Migrate configuration DEV -> TEST; supplier mock load 2", "Migrate + mock load 2", 10, 10, "dat", "SUGGESTED", CL),
    ("TEST", "SIT round 1 (SCM end-to-end + Financials regression)", "SIT 1", 11, 12, "sit", "SOW E.1; SOW B Financials remediation scope. Length SUGGESTED", CL),
    ("DEV", "Defect fix and re-migrate to TEST (gap between SIT rounds)", "Fix + re-migrate", 13, 13, "fix", "SUGGESTED", CL),
    ("TEST", "SIT round 2 (regression + retest)", "SIT 2", 14, 15, "sit", "SUGGESTED", CL),
    ("TEST", "UAT (Twelve-led)", "UAT", 16, 18, "uat", "SOW E.1. Length SUGGESTED", CL),
    ("TEST", "Train-the-Trainer sessions", "Train-the-trainer", 17, 18, "trn", "SOW B Change Management 2; SOW C.6. Timing SUGGESTED", CL),
    ("TEST", "Cutover dress rehearsal incl. supplier mock load 3", "Dress rehearsal", 19, 19, "dat", "SUGGESTED", CL),
    ("PROD", "Configuration migration to Production (by Twelve)", "Prod config migration", 19, 19, "cut", "SOW C.10. Week SUGGESTED", CL),
    ("PROD", "Supplier load, cutover and Go-live", "Cutover + Go-live", 20, 20, "cut", "SOW B RICE 2.1.1. Week SUGGESTED", CL),
    ("PROD", "Hypercare / post-go-live support", "Hypercare", 21, 24, "hyp", "SUGGESTED - not in SOW", CL),
]

thin = Side(style="thin", color="808080")
BOR = Border(left=thin, right=thin, top=thin, bottom=thin)
HB = Font(bold=True)
WR = Alignment(wrap_text=True, vertical="top")


def grid(ws, acts, weeks, title, sow_end=12):
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = ("Weeks are relative (Week 1 = start after the signed SOW is received). No dates given. "
                "Thick red line after Week 12 = end of SOW 12-week duration (SOW C.8). "
                "Week placements are SUGGESTED unless the Activities sheet says otherwise.")
    hdr = 4
    ws.cell(hdr, 1, "Row type").font = HB
    ws.cell(hdr, 2, "Environment / activity").font = HB
    for w in range(1, weeks + 1):
        c = ws.cell(hdr, 2 + w, f"Week {w}")
        c.font = HB
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(2 + w)].width = 14
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 48
    r = hdr + 1
    for env in ENVS:
        ws.cell(r, 1, "Environment").font = HB
        ws.cell(r, 2, ENV_DESC[env]).alignment = WR
        for w in range(1, weeks + 1):
            act = [a for a in acts if a[0] == env and a[3] <= w <= a[4]]
            c = ws.cell(r, 2 + w)
            if act:
                act.sort(key=lambda a: PRIO.index(a[5]))
                c.value = " | ".join(a[2] for a in act)
                c.fill = PatternFill("solid", fgColor=COL[act[0][5]])
                c.alignment = WR
            c.border = BOR
        ws.row_dimensions[r].height = 60
        r += 1
    r += 1
    ws.cell(r, 1, "Detail lanes (one row per activity)").font = HB
    r += 1
    for a in acts:
        ws.cell(r, 1, a[0])
        ws.cell(r, 2, a[1]).alignment = WR
        for w in range(1, weeks + 1):
            c = ws.cell(r, 2 + w)
            if a[3] <= w <= a[4]:
                c.value = a[2]
                c.fill = PatternFill("solid", fgColor=COL[a[5]])
                c.alignment = WR
            c.border = BOR
        r += 1
    for rr in range(hdr, r):
        c = ws.cell(rr, 2 + sow_end)
        c.border = Border(left=thin, top=thin, bottom=thin, right=Side(style="thick", color="C00000"))
    ws.freeze_panes = "C5"
    r += 1
    ws.cell(r, 1, "Legend").font = HB
    r += 1
    for k, n in [("mob", "Mobilize"), ("des", "Design / approach"), ("dec", "Decision point"), ("cfg", "Configure"),
                 ("bld", "Report / conversion build"), ("dat", "Data load / migration"), ("sit", "System integration test"),
                 ("fix", "Fix gap"), ("uat", "User acceptance test"), ("trn", "Training"),
                 ("cut", "Production cutover / go-live"), ("hyp", "Hypercare")]:
        c = ws.cell(r, 1, n)
        c.fill = PatternFill("solid", fgColor=COL[k])
        r += 1


def style(ws, widths):
    for i, wd in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = wd
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = WR
    for c in ws[1]:
        c.font = HB


wb = Workbook()
ws = wb.active
ws.title = "Plan A - SOW 12wk"
grid(ws, A, 16, "PLAN A - fitted to SOW 12-week duration (SOW C.8), go-live Week 12, plus SUGGESTED 4-week hypercare (Weeks 13-16, outside SOW)")
grid(wb.create_sheet("Plan B - SUGGESTED 20wk"), B, 24, "PLAN B (SUGGESTED alternative) - 20 weeks to go-live + 4 weeks hypercare = 24 weeks")

ws = wb.create_sheet("Activities")
ws.append(["Plan", "Environment", "Activity", "Short label", "From week", "To week", "Number of weeks",
           "Source (SOW section quote, or SUGGESTED)", "Who produced it"])
for plan, acts in [("Plan A (SOW 12wk)", A), ("Plan B (SUGGESTED 20wk)", B)]:
    for a in acts:
        ws.append([plan, a[0], a[1], a[2], a[3], a[4], a[4] - a[3] + 1, a[6], a[7]])
style(ws, [20, 10, 60, 22, 10, 10, 10, 90, 16])

ws = wb.create_sheet("Assumptions & Open Questions")
ws.append(["ID", "SUGGESTED assumption", "Reasoning", "Open question for Twelve / GoSaaS", "Who produced it"])
AS = [
    ("S1", "Week 1 starts when GoSaaS receives the signed SOW; the plan uses relative weeks only.", "No start date given; SOW cover says services commence after the executed copy is received (signatures dated January 28, 2025).", "What is the actual project start date, and is there a fixed go-live target date?", CL),
    ("S2", "Three environments: DEV (configuration/build), TEST (SIT/UAT/training), PROD (existing).", "SOW E.6 names only 'development and production platforms'. Separating build from test avoids testing on a moving configuration.", "How many non-production pods does Twelve subscribe to? Is the existing Financials test pod shared with this project? Is a separate DEV pod available, or must DEV and TEST be one pod?", CL),
    ("S3", "Design: 3 weeks (Plan A) / 4 weeks (Plan B), overlapping mobilization.", "About 11 new or changed module areas plus Financials remediation; a common design (SOW C.3) needs cross-module key design decisions.", "Can Twelve SMEs for procurement, inventory, costing, manufacturing, maintenance and finance attend workshops nearly full-time in Weeks 1-3?", CL),
    ("S4", "Expenses in/out decision in Week 2.", "SOW B Financials 5.1 requires a design session; an early decision protects the build window.", "Who decides on Expenses and by when? If in scope, does it fit inside the 12 weeks and the budget?", CL),
    ("S5", "Configuration + unit test: Weeks 3-6 (Plan A) / Weeks 3-9 incl. CRP (Plan B).", "12 configuration areas (SOW B Configurations Scope). FSCR catalog lists 266 (Product Management) + 648 (Manufacturing and Supply Chain Materials Management) + 577 (Procurement) = 1,491 setup tasks across the 3 new SCM offerings; only a subset applies, but the breadth is large.", "Are configuration templates and Coupa values (SOW B Scope 3.5) available at kickoff?", FC),
    ("S6", "Two SIT rounds. Plan A: 1 week + 1 week, no gap. Plan B: 2 weeks + 1-week fix gap + 2 weeks.", "Two integrated test cycles is common practice; Plan A has only 2 weeks left for SIT.", "How many test rounds does Twelve expect? Who writes the test scripts?", CL),
    ("S7", "Gap between test rounds: 0 weeks (Plan A), 1 week (Plan B).", "Defect fixing and re-migration DEV -> TEST takes time.", "Is a defect-fix window acceptable to Twelve?", CL),
    ("S8", "UAT: 2 weeks (Plan A) / 3 weeks (Plan B), executed by Twelve.", "SOW E.1 makes Twelve responsible for testing; the length is not in the SOW.", "How many Twelve testers are available for UAT, and who signs off?", CL),
    ("S9", "Financials regression testing (GL, AR, Projects, Grants, AP, Cash, Fixed Assets) runs inside SIT and UAT.", "SOW B Financials scope says these production modules need remediation; they are live, so regression is needed.", "Which live Financials processes must be regression-tested, and by whom?", CL),
    ("S10", "Data load = Suppliers only; 2 mock loads (Plan A) / 3 incl. dress rehearsal (Plan B), then the Production load.", "SOW B RICE 2.1.1 lists only Suppliers; SOW C.5 says migration is minimal.", "Are items, inventory balances or open POs really not migrated? Are suppliers already in Production Payables, making this an update rather than a new load?", CL),
    ("S11", "Printable PO report built Weeks 4-7 (A) / 6-9 (B), ready before SIT.", "The report needs PO configuration and an approved FDD first.", "Is a sample PO layout available? Who approves the FDD?", CL),
    ("S12", "Training materials built during the test phases; Train-the-Trainer during the UAT window in TEST.", "SOW B Change Management 1-2 and C.6; timing not given. End-user training is Twelve's (SOW C.4).", "How many trainers, and when must Twelve's end-user training finish relative to go-live?", CL),
    ("S13", "Production configuration migration by Twelve in Week 12 (A) / Week 19 (B), using Oracle setup-data export/import.", "SOW C.10 assigns the migration to Twelve; the week is not given.", "Does Twelve have staff able to run configuration migration? Is GoSaaS support for it included?", CL),
    ("S14", "Go-live at the end of Week 12 (Plan A).", "SOW C.8 gives a 12-week duration but never states a go-live week; SOW C.2.1 says criteria will be refined.", "Does the 12-week duration end at go-live, or at a configured 'Ready to Use' state with go-live done later by Twelve?", CL),
    ("S15", "Hypercare of 4 weeks after go-live.", "Not in SOW scope or hours; common practice.", "Is hypercare wanted, and under which budget or addendum?", CL),
    ("S16", "One Oracle quarterly update will probably land inside the project; non-production pods get it about 2 weeks before production.", "Quarterly cadence over a 12-24 week project. Cohort not given, so it is not drawn on the grid.", "Which update cohort is Twelve on, and which weekends are the update windows? Avoid SIT/UAT starts and cutover on those weekends.", CL),
    ("S17", "Security & roles configured within module configuration and tested in SIT.", "SOW B Configurations Scope item 12.", "Will role designs (segregation of duties) change in Production Financials?", CL),
    ("S18", "Reporting Approach: Weeks 2-5 (A) / 3-7 (B).", "SOW B Financials 6.1-6.2 is a strategy deliverable, not report build; Reporting Architect has 80 hours (SOW D).", "Is the reporting approach needed before go-live?", CL),
    ("S19", "Capacity check uses 40-hour weeks.", "Standard full-time week, used to test SOW D hours against 12 weeks.", "Are consultants expected to work more than 40 hours per week?", CL),
    ("S20", "Twelve SMEs are available for design, testing, decisions and production migration.", "SOW C.1 says the estimate excludes Twelve's productive effort, yet SOW E.1 and C.10 assign work to Twelve.", "Who is Twelve's project lead (SOW E.9), and what share of time can SMEs give?", CL),
    ("S21", "Go/No-Go one week before go-live.", "Gives one week to react; SOW C.2.1 criteria refined in the project.", "Who attends Go/No-Go, and what are the criteria?", CL),
    ("S22", "Plan B length of 20 weeks to go-live (+4 hypercare).", "Sum of SUGGESTED phase lengths with a 1-week fix gap and a dress rehearsal (see Fit arithmetic).", "Would Twelve accept a longer timeline, or reduce scope (e.g. defer Expenses, Sustainability, Maintenance Programs) to keep 12 weeks?", CL),
]
for a in AS:
    ws.append(list(a))
style(ws, [6, 60, 70, 70, 16])

ws = wb.create_sheet("Fit arithmetic")
F = [
    ["Item", "Plan A (SOW 12 weeks)", "Plan B (SUGGESTED)", "Source / note"],
    ["SOW duration", "12 weeks", "-", "SOW C.8 \"Duration - 12 weeks\""],
    ["Mobilize + Design", "3 (Weeks 1-3)", "4 (Weeks 1-4)", "SUGGESTED"],
    ["Configure / build", "3 (Weeks 4-6; base config Week 3 overlaps design)", "5 (Weeks 5-9; CRP Weeks 3-4 overlap design)", "SUGGESTED"],
    ["Migrate to TEST + mock load", "1 (Week 7)", "1 (Week 10)", "SUGGESTED"],
    ["SIT round 1", "1 (Week 8)", "2 (Weeks 11-12)", "SUGGESTED"],
    ["Gap / fix between SIT rounds", "0", "1 (Week 13)", "SUGGESTED"],
    ["SIT round 2", "1 (Week 9)", "2 (Weeks 14-15)", "SUGGESTED"],
    ["UAT (+ train-the-trainer in parallel)", "2 (Weeks 10-11)", "3 (Weeks 16-18)", "SUGGESTED; SOW E.1 testing by Twelve"],
    ["Prod migration, cutover, go-live", "1 (Week 12)", "2 (Weeks 19-20)", "SUGGESTED; SOW C.10 migration by Twelve"],
    ["Weeks to go-live", "3+3+1+1+0+1+2+1 = 12", "4+5+1+2+1+2+3+2 = 20", ""],
    ["Contingency inside plan", "0 weeks", "1-week fix gap + 1 dress-rehearsal week", ""],
    ["Hypercare (outside SOW)", "4 (Weeks 13-16)", "4 (Weeks 21-24)", "SUGGESTED, not in SOW"],
    ["Total weeks drawn", "16", "24", ""],
    ["SOW hours check (SOW D), 40 h/week", "Hours / 12 weeks", "Full-time weeks needed (hours / 40)", ""],
    ["SCM Architect 640 h", "53.3 h/week", "16.0 weeks", "SOW D table"],
    ["Inventory Consultant 560 h", "46.7 h/week", "14.0 weeks", "SOW D table"],
    ["Manufacturing / Maintenance Consultant 560 h", "46.7 h/week", "14.0 weeks", "SOW D table"],
    ["Procurement Consultant 560 h", "46.7 h/week", "14.0 weeks", "SOW D table"],
    ["Product Information Management 400 h", "33.3 h/week", "10.0 weeks", "SOW D table"],
    ["PMO Analyst 320 h", "26.7 h/week", "8.0 weeks", "SOW D table"],
    ["DEV Consultant 280 h / Finance Consultant 280 h", "23.3 h/week each", "7.0 weeks each", "SOW D table"],
    ["Finance Architect 140 h / Reporting Architect 80 h", "11.7 / 6.7 h/week", "3.5 / 2.0 weeks", "SOW D table"],
    ["Total hours", "3,820 h (140+640+80+560+320+280+280+560+560+400)", "$360,300 total (matches SOW D)", "SOW D table"],
    ["Scope breadth", "12 configuration areas (8 new, 3 incremental, security & roles); 1 report; 1 conversion", "FSCR catalog: 1,491 setup tasks in the 3 new SCM offerings (266+648+577)", "SOW B; FSCR catalog (FSCR + Claude)"],
    ["VERDICT",
     "12 weeks is NOT realistic for a full go-live with two SIT rounds, UAT, training and production cutover. It only adds up with zero contingency, 1-week SIT rounds and production migration plus go-live in the same week; and SOW D hours for 4 key roles need 14-16 full-time weeks (SCM Architect 640 h / 12 weeks = 53.3 h/week).",
     "SUGGESTED 20 weeks to go-live (+4 weeks hypercare = 24) is realistic under the stated assumptions.",
     "12 weeks is plausible only if 'Duration' means a configured 'Ready to Use' state (SOW B Manufacturing 6.1 / Maintenance 7.1, C.2) with go-live run later by Twelve (C.10). The SOW B Note itself calls it 'an aggressive plan'."],
]
for r in F:
    ws.append(r)
style(ws, [42, 60, 50, 60])
ws.cell(len(F), 1).font = HB

ws = wb.create_sheet("Provenance")
for r in [["Part", "Who produced it"],
          ["Plan A and Plan B timelines, environments, test rounds, assumptions, fit arithmetic", "Claude alone"],
          ["Configuration sizing note (setup-task counts per offering from FSCR knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json)", "FSCR + Claude"],
          ["FSCR implementation-wave-planner and instance-strategy skills", "Checked: generic placeholder text only (no method or data); not used"],
          ["Any part produced by FSCR alone", "None"]]:
    ws.append(r)
style(ws, [90, 60])
wb.save(OUT)
print("saved", OUT)
