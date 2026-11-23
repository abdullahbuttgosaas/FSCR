"""Build the Twelve wave plan workbook (paper only). Usage: python build_wave_plan.py out.xlsx"""
import sys
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.comments import Comment

out = sys.argv[1]
F = "Arial"
C = {"Configure": "4472C4", "Data Load / Delta": "ED7D31", "CRP1": "70AD47", "CRP2": "FFC000", "UAT": "7030A0",
     "Go-Live": "C00000", "Fix / Load / Validate": "BDD7EE", "Oracle update": "808080", "Not in SOW": "D9D9D9"}
DARK_TEXT = {"Fix / Load / Validate", "Not in SOW", "CRP2"}
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def fill(kind):
    return PatternFill("solid", fgColor=C[kind])


def grid(ws, title, weeks, rows, notes):
    ws["A1"] = title
    ws["A1"].font = Font(name=F, bold=True, size=13)
    ws["A2"] = "Relative weeks only: the SOW gives no start date (open question W1). Week 1 = project start."
    ws["A2"].font = Font(name=F, italic=True, size=9)
    ws.cell(4, 1, "Environment").font = Font(name=F, bold=True)
    ws.cell(4, 2, "Source").font = Font(name=F, bold=True)
    for w in range(1, weeks + 1):
        c = ws.cell(4, 2 + w, f"W{w}")
        c.font = Font(name=F, bold=True, size=8)
        c.alignment = Alignment(horizontal="center")
        ws.column_dimensions[c.column_letter].width = 5.2
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 34
    r = 5
    for env, src, blocks in rows:
        ws.cell(r, 1, env).font = Font(name=F, bold=True)
        ws.cell(r, 2, src).font = Font(name=F, size=8)
        ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
        for w in range(1, weeks + 1):
            ws.cell(r, 2 + w).border = BORDER
        for kind, a, b, label in blocks:
            for w in range(a, b + 1):
                c = ws.cell(r, 2 + w)
                c.fill = fill(kind)
                c.font = Font(name=F, size=7, color="000000" if kind in DARK_TEXT else "FFFFFF")
                c.alignment = Alignment(wrap_text=True, vertical="center")
            ws.cell(r, 2 + a).value = label
        ws.row_dimensions[r].height = 60
        r += 1
    r += 1
    ws.cell(r, 1, "Legend").font = Font(name=F, bold=True)
    r += 1
    for k in C:
        ws.cell(r, 1, k).font = Font(name=F)
        ws.cell(r, 2).fill = fill(k)
        r += 1
    r += 1
    ws.cell(r, 1, "Notes").font = Font(name=F, bold=True)
    r += 1
    for n in notes:
        ws.cell(r, 1, n).font = Font(name=F, size=9)
        r += 1
    ws.freeze_panes = "C5"


RULES = [
    ("DEV (development platform)",
     "SOW E.6 names 'development and production platforms'. Pod name/type not recorded. CRP/UAT shown here because no other non-prod environment is given.",
     [("Configure", 1, 4, "Design + Configure (4 wk ASSUMED)"),
      ("CRP1", 5, 6, "CRP1: partial data, no security, no custom."),
      ("Fix / Load / Validate", 7, 10, "Fix, load, validate (7 wk total)"),
      ("Data Load / Delta", 11, 13, "Full data load + security + PO report"),
      ("CRP2", 14, 15, "CRP2: full data, security, custom."),
      ("Fix / Load / Validate", 16, 20, "Fix, load, validate (7 wk total)"),
      ("Data Load / Delta", 21, 22, "Delta load"),
      ("UAT", 23, 24, "UAT: full data + delta")]),
    ("PROD (production platform)",
     "SOW E.6. Approved configuration is migrated to PROD by Twelve (SOW C.10).",
     [("Configure", 22, 23, "Config migration (Twelve, C.10)"),
      ("Data Load / Delta", 24, 24, "Supplier load"),
      ("Go-Live", 25, 25, "Go-Live")]),
    ("TEST / UAT environment",
     "NOT IN SOW. Open question W2: is a separate test pod available? If none, CRP/UAT run on DEV as shown.",
     [("Not in SOW", 1, 25, "No environment given in SOW (open question W2)")]),
    ("Oracle quarterly update",
     "NOT IN FSCR, NOT IN SOW. No update calendar and no start date, so update weeks cannot be placed (W3).",
     [("Oracle update", 1, 1, "?")]),
]

SOW12 = [
    ("DEV (development platform)", "SOW E.6",
     [("Configure", 1, 4, "Design + Configure"), ("CRP1", 5, 6, "CRP1"), ("Data Load / Delta", 7, 7, "Load"),
      ("CRP2", 8, 9, "CRP2"), ("UAT", 10, 11, "UAT")]),
    ("PROD (production platform)", "SOW E.6; C.10",
     [("Configure", 11, 11, "Migrate"), ("Go-Live", 12, 12, "Go-Live")]),
    ("Oracle quarterly update", "Not recorded", [("Oracle update", 1, 1, "?")]),
]

wb = Workbook()
ws = wb.active
ws.title = "Wave Plan (rules)"
grid(ws, "Twelve SCM: wave plan built from our practice rules (25 weeks)", 25, RULES, [
    "Rule sources: CRP1 2 wk partial data, no security, no customizations; CRP2 2 wk full data, full security and customizations; "
    "UAT 2 wk full data + delta; go-live 1 wk; ~7 wk fix/load/validate between cycles = OUR PRACTICE (stated in the run prompt). FSCR holds none of these rules.",
    "Design + Configure = 4 weeks before CRP1 is a CLAUDE ASSUMPTION (not verified). No source gives it. Change it on the Arithmetic sheet.",
    "No gap is shown between UAT and go-live because the practice list gives none. Cutover length is open question W5.",
    "Customizations in this SOW = 1 report (printable PO) and 1 conversion (suppliers); no integrations or extensions (SOW RICE).",
    "The Oracle update row is a placeholder: FSCR has no update calendar and the SOW has no dates, so test cycles cannot be checked against update windows.",
])
ws2 = wb.create_sheet("SOW 12 weeks (does not fit)")
grid(ws2, "Twelve SCM: the SOW's 12 weeks forced onto the same cycles", 12, SOW12, [
    "Fits only by breaking the practice rules: 1 week between CRP1 and CRP2 (rule ~7) and 0 weeks between CRP2 and UAT (rule ~7).",
    "With the 7-week gaps kept, 12 weeks is not enough even with zero design/configure time: 2+7+2+7+2+1 = 21 weeks.",
])

a = wb.create_sheet("Arithmetic")
for i, h in enumerate(["Component", "Weeks", "Source"], 1):
    a.cell(1, i, h).font = Font(name=F, bold=True)
items = [("Design + Configure before CRP1", 4, "Claude assumption (not verified): no rule in FSCR, SOW or the practice list"),
         ("CRP1", 2, "Our practice (run prompt)"),
         ("Fix / load / validate after CRP1", 7, "Our practice (~7 wk)"),
         ("CRP2", 2, "Our practice"),
         ("Fix / load / validate after CRP2", 7, "Our practice (~7 wk)"),
         ("UAT", 2, "Our practice"),
         ("Go-Live", 1, "Our practice")]
for i, (n, w, s) in enumerate(items, 2):
    a.cell(i, 1, n).font = Font(name=F)
    a.cell(i, 2, w).font = Font(name=F, color="0000FF")
    a.cell(i, 3, s).font = Font(name=F, size=9)
a.cell(2, 2).fill = PatternFill("solid", fgColor="FFFF00")
a.cell(2, 2).comment = Comment("Key assumption: change this to test other design/configure lengths.", "Claude")
last = len(items) + 1          # row 8
r = last + 2                   # row 10
rows = [
    ("Total, rules-based plan (weeks)", f"=SUM(B2:B{last})", "Formula"),
    ("Total, cycles only, no design/configure (weeks)", f"=SUM(B3:B{last})", "Formula"),
    ("SOW duration (weeks)", 12, "SOW C.8"),
    ("Gap: rules plan minus SOW (weeks)", f"=B{r}-B{r+2}", "Formula"),
    ("Gap: cycles only minus SOW (weeks)", f"=B{r+1}-B{r+2}", "Formula"),
    ("SOW hours", 3820, "SOW D, sum of the role table (DRIVE_REFERENCE's ~4,800 not used)"),
    ("Hours per week over 12 weeks", f"=B{r+5}/B{r+2}", "Formula"),
    ("Hours per week over the rules plan", f"=B{r+5}/B{r}", "Formula"),
    ("Approx. FTE over 12 weeks at 40 h/week", f"=B{r+6}/40", "Formula; 40 h/week is a Claude assumption"),
    ("Approx. FTE over the rules plan at 40 h/week", f"=B{r+7}/40", "Formula; 40 h/week is a Claude assumption"),
]
for i, (n, v, s) in enumerate(rows, r):
    a.cell(i, 1, n).font = Font(name=F, bold=n.startswith(("Total", "Gap")))
    c = a.cell(i, 2, v)
    c.font = Font(name=F, color="000000" if str(v).startswith("=") else "0000FF")
    if "week" in n.lower() and ("Hours per" in n or "FTE" in n):
        c.number_format = "0.0"
    a.cell(i, 3, s).font = Font(name=F, size=9)
a.column_dimensions["A"].width = 48
a.column_dimensions["B"].width = 10
a.column_dimensions["C"].width = 75

q = wb.create_sheet("Open questions")
qs = [("W1", "Project start date and go-live date (SOW gives only the 12-week duration, C.8)"),
      ("W2", "Which environments exist besides development and production (SOW E.6)? Is there a separate TEST/UAT pod? How many?"),
      ("W3", "Which Oracle quarterly update dates apply to Twelve's pods (non-prod and prod)? None are in FSCR or the SOW."),
      ("W4", "How long is design + configure before CRP1? No rule is given; 4 weeks is assumed."),
      ("W5", "Cutover and hypercare length after UAT (intake S7)"),
      ("W6", "Is Expenses in scope (Fin 5.1)? If yes, it must be configured by CRP2 at the latest."),
      ("W7", "Who requests environment refreshes/clones between cycles, and how long does each take?"),
      ("W8", "Does the 12-week SOW cover the full lifecycle to go-live, or only design and build?")]
q.cell(1, 1, "ID").font = Font(name=F, bold=True)
q.cell(1, 2, "Question").font = Font(name=F, bold=True)
for i, (k, v) in enumerate(qs, 2):
    q.cell(i, 1, k).font = Font(name=F)
    q.cell(i, 2, v).font = Font(name=F)
q.column_dimensions["B"].width = 110
wb.save(out)
print("saved", out)
