"""Build the identified-task-mapping JSON for the Run 04 FSCR project (15 skills, worked-out creation order).
Task names come from FSCR's catalog (knowledge/setup-task-catalog/effective/setupTasksAll.json); offering and
functional area from each skill's "Setup Task Skill Contract". Same shape as Run 01's mapping file.
Why: FSCR's own resolver (task_to_skill_mapping.py) crashes (Run 01 finding F4), so the sequence is set here."""
import json, re
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_04_create16\fscr-work4")
OUT = W.parent / "identified-task-mapping-run04.json"
ORDER = [  # creation order (worked out; see RUN_REPORT section 4)
    "AP_MANAGE_PAYABLES_CALENDARS", "AP_MANAGE_PAYMENT_TERMS", "ORA_AP_MANAGE_BANK_CHARGES",
    "AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT", "AP_MANAGE_INVOICE_OPTIONS", "AP_MANAGE_PAYMENT_OPTIONS",
    "EXM_MANAGE_CONVERSION_RATES_AND_POLICIES", "AR_MANAGE_AUTOINVOICE_GROUPING_RULES", "AR_MANAGE_REMIT_TO_ADDRESSES",
    "AR_MANAGE_RECEIPT_CLASSES_AND_METHODS", "AR_MANAGE_TRANSACTION_TYPES", "AR_MANAGE_AUTOACCOUNTING_RULES",
    "AR_MANAGE_TRANSACTION_SOURCES", "AR_MANAGE_RECEIPT_SOURCES", "AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS",
]
cat = json.loads((W / "knowledge/setup-task-catalog/effective/setupTasksAll.json").read_text(encoding="utf-8"))
items = cat if isinstance(cat, list) else (cat.get("items") or cat.get("tasks") or list(cat.values())[0])
items = [i for i in items if isinstance(i, dict) and "TaskCode" in i]
names = {i["TaskCode"]: i["TaskName"] for i in items}
skills = {}
for a in W.glob("pillars/erp/financials/**/e2e-adapter.json"):
    s = (a.parent / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    task = json.loads(a.read_text(encoding="utf-8"))["task"]
    skills[task["code"]] = (str((a.parent / "SKILL.md").relative_to(W)).replace("\\", "/"),
                            task["offering"], task["functionalArea"])
tasks = []
for seq, code in enumerate(ORDER, 1):
    path, off, fa = skills[code]
    tasks.append({"ID": code, "Source Task Name": names[code], "Task Code": code, "Offering": off,
                  "Functional Area": fa, "Pillar": "ERP", "Phase": "build", "Resolver Sequence": seq,
                  "Match Method": "exact-name", "Match Status": "matched", "Source Reference": "FSCR run 04 brief (15 create skills)",
                  "Skill Path": path, "Data Paths": [], "Confidence": 1.0, "Matched Task Code": code,
                  "Matched Task Name": names[code], "Match Rationale": "Exact task code from the skill's e2e adapter and catalog"})
OUT.write_text(json.dumps({"source": "FSCR run 04 (2026-11-03): one FSCRT test record per create skill on ETIA-TEST",
                           "sequence_source": "worked out in Run 04 (task_to_skill_mapping.py fails; Run 01 F4)",
                           "selection_counts": {"selected": 15, "included": 15, "excluded": 0}, "tasks": tasks}, indent=1), encoding="utf-8")
for t in tasks:
    print(t["Resolver Sequence"], t["Task Code"], "|", t["Source Task Name"], "|", t["Functional Area"])
