# Checks 01_SOW_ONLY_WAVE_PLAN.xlsx: sheets, no formulas, coloured cells labelled, grid consistent with Activities.
import os, sys
from openpyxl import load_workbook
RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wb = load_workbook(os.path.join(RUN, "01_SOW_ONLY_WAVE_PLAN.xlsx"))
errs = []
need = ["Plan A - SOW 12wk", "Plan B - SUGGESTED 20wk", "Activities", "Assumptions & Open Questions", "Fit arithmetic"]
for n in need:
    if n not in wb.sheetnames: errs.append("missing sheet " + n)
for ws in wb:
    for row in ws.iter_rows():
        for c in row:
            if c.data_type == "f" or (isinstance(c.value, str) and c.value.startswith("=")):
                errs.append(f"formula {ws.title}!{c.coordinate}")
def colored(c):
    return c.fill is not None and c.fill.fill_type == "solid"
acts = {}
for r in wb["Activities"].iter_rows(min_row=2, values_only=True):
    acts.setdefault(r[0], []).append(r)
    if r[6] != r[5] - r[4] + 1: errs.append("bad week count " + str(r))
for sheet, plan in [("Plan A - SOW 12wk", "Plan A (SOW 12wk)"), ("Plan B - SUGGESTED 20wk", "Plan B (SUGGESTED 20wk)")]:
    ws = wb[sheet]
    wkcol = {int(c.value.split()[1]): c.column for c in ws[4] if isinstance(c.value, str) and c.value.startswith("Week ")}
    W = max(wkcol)
    envrow = {}; lanes = {}
    for r in range(5, ws.max_row + 1):
        a, b = ws.cell(r, 1).value, ws.cell(r, 2).value
        if a == "Environment": envrow[b.split(" - ")[0]] = r
        elif a in ("PROJECT", "DEV", "TEST", "PROD"): lanes[(a, b)] = r
        for w, col in wkcol.items():
            c = ws.cell(r, col)
            if colored(c) and not (c.value and str(c.value).strip()): errs.append(f"empty coloured {sheet}!{c.coordinate}")
    for act in acts[plan]:
        _, env, name, lab, f, t, n, _, _ = act
        lr = lanes.get((env, name))
        if lr is None: errs.append("no lane " + name); continue
        for w, col in wkcol.items():
            c = ws.cell(lr, col); inside = f <= w <= t
            if inside != (colored(c) and c.value == lab): errs.append(f"lane mismatch {sheet} {lab} wk{w}")
            ec = ws.cell(envrow[env], col)
            if inside and not (ec.value and lab in str(ec.value).split(" | ")): errs.append(f"env row missing {sheet} {env} {lab} wk{w}")
    for env, r in envrow.items():
        for w, col in wkcol.items():
            c = ws.cell(r, col)
            has = any(a[1] == env and a[4] <= w <= a[5] for a in acts[plan])
            if has != colored(c): errs.append(f"env colour mismatch {sheet} {env} wk{w}")
    print(sheet, "weeks", W, "env rows", list(envrow), "lanes", len(lanes))
print("sheets:", wb.sheetnames)
print("ERRORS:", errs if errs else "none")
sys.exit(1 if errs else 0)
