"""Build the Twelve offering task map from the FSCR effective catalog (read-only, offline).

Selection = Run 14 intake scope (01_SCOPE.md section 2). Sequence = offline resolver:
offering order as listed below, FA order from catalog functionalAreaOrder, task order from
catalog displaySequence; consecutive Resolver Sequence numbers. No FSM/BOSS call (paper run).
Skill paths come from FSCR's own matcher core/runbook/scripts/task_context._skill_path.
"""
import csv, json, sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(repo / "core/runbook/scripts"))
import task_context as tc  # FSCR code

cat = json.load(open(repo / "knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json", encoding="utf-8"))
policy = tc._task_context_policy(repo)

# (offering, FA, SOW ref, scope class, resolution note)
# scope class: NEW = expand all tasks; INCR = expand, review only (incremental change to production);
# COND = expand, conditional on design session; TBD = FA listed, tasks not expanded (scope decided in project)
SEL = [
    ("XLE_FINANCIALS_JUR", "ORA_ASK_ORGANIZATION_STRUCTURE", "Fin 3.1-3.2", "INCR", "pending in Run 14 classifier; SUGGESTED owner Financials (Run 14 Q-S4)"),
    ("XLE_FINANCIALS_JUR", "ORA_ASK_USERS_AND_SECURITY", "Cfg 12", "NEW", "pending in Run 14 classifier (21 offerings); SUGGESTED owner Financials (Run 14 Q-S4)"),
    ("PIM_PROD_MNG", "ORA_EGP_FA_ITEM_ORGANIZATIONS", "B 1.1-1.3", "NEW", "resolved"),
    ("PIM_PROD_MNG", "ORA_EGP_FA_ITEMS", "B 1.1-1.2", "NEW", "resolved"),
    ("PIM_PROD_MNG", "EGO_ADVANCED_PRODUCT_STRUCT", "B 1.3", "NEW", "resolved"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "ORA_RCS_FACILITIES", "B 2.2", "NEW", "resolved"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "ORA_WSH_INVENTORY_MGMT", "B 2.1-2.2", "NEW", "resolved"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "WSH_ENABLE_RECEIVING", "B 2.1", "NEW", "resolved"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "CMR_RECEIPT_ACCOUNTING", "B 2.1, 3.4", "NEW", "resolved"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "CST_DEFINE_COST_MANAGEMENT", "B 2.3-2.6", "NEW", "resolved"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "ORA_WIS_COMMON_MFG_WORK_SETUP", "B 6.1-6.4", "NEW", "resolved; process vs discrete not separated in catalog"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "ORA_MNT_MGMT", "B 7.1-7.7", "NEW", "resolved"),
    ("ORA_MANUFACTURING_AND_SUPPLY_C", "ORA_SUS_SUSTAINABILITY", "Fin 4.1-4.3", "NEW", "pending in Run 14 (3 offerings); SUGGESTED owner MSCMM (Run 14 Q-S4)"),
    ("PO_PROCUREMENT", "ORA_PO_PROC_FOUNDATION_FA", "B 4.1", "NEW", "resolved"),
    ("PO_PROCUREMENT", "ORA_EGP_SUPPLIERS", "B 5.4, RICE 2", "NEW", "resolved"),
    ("PO_PROCUREMENT", "ORA_PO_APPROVAL_MANAGEMENT_FA", "B 3.3, 4.2", "NEW", "resolved"),
    ("PO_PROCUREMENT", "ORA_PO_PURCHASING_FOUNDATION", "B 4.1-4.2", "NEW", "resolved"),
    ("PO_PROCUREMENT", "ORA_PO_PRC_TRX_ACC_RULES_FA", "B 3.4", "NEW", "resolved"),
    ("PO_PROCUREMENT", "PO_SSP_DEPLOYED", "B 3.1-3.5", "NEW", "resolved"),
    ("PO_PROCUREMENT", "PO_SUP_PORTAL_DEPLOYED", "B 5.1-5.5", "NEW", "resolved"),
    ("XLE_FINANCIALS_JUR", "ORA_FIN_GENERAL_LEDGER", "Fin 7, Cfg 7", "INCR", "resolved"),
    ("XLE_FINANCIALS_JUR", "FIN_PAYABLES_DEPLOYED", "Cfg 5", "INCR", "pending in Run 14 (Financials or Procurement); SUGGESTED owner Financials"),
    ("PJF_PROJ_MNG", "ORA_PJC_PROJ_COSTING_BASE_FA", "Fin 1, Cfg 8", "INCR", "resolved"),
    ("XLE_FINANCIALS_JUR", "FIN_FIXED_ASSETS_DEPLOYED", "Fin 2", "INCR", "resolved"),
    ("XLE_FINANCIALS_JUR", "FIN_EXPENSES_DEPLOYED", "Fin 5.1-5.4", "COND", "resolved; in/out decided by Expenses design session"),
    ("XLE_FINANCIALS_JUR", "FIN_RECEIVABLES_DEPLOYED", "Fin intro", "TBD", "remediation; extent 'determined during the project'"),
    ("XLE_FINANCIALS_JUR", "ORA_CE_CASH_MGMT_BANK", "Fin intro", "TBD", "remediation; pending owner in Run 14; SUGGESTED Financials"),
    ("ORA_GMS_GRANTS_MANAGEMENT", "ORA_GMS_GRANTS_BASE_FA", "Fin intro", "TBD", "remediation; extent TBD"),
    ("XLE_FINANCIALS_JUR", "ORA_FIN_REPORT_CENTER", "Fin 6", "TBD", "reporting approach is a strategy deliverable, not configuration"),
]

rows, fa_rows, seq = [], [], 0
seen_codes = {}
for off, fa, ref, cls, note in SEL:
    o = cat["offerings"][off]
    f = o["functionalAreas"][fa]
    tasks = sorted(f.get("tasks", []), key=lambda t: int(t.get("displaySequence") or 0))
    fa_rows.append({"offering_code": off, "offering": o["offeringName"], "fa_code": fa, "functional_area": f["functionalAreaName"],
                    "sow_ref": ref, "scope_class": cls, "catalog_tasks": len(tasks),
                    "tasks_in_map": 0 if cls == "TBD" else len(tasks), "note": note})
    if cls == "TBD":
        continue
    for t in tasks:
        seq += 1
        code = t["taskShortName"]
        skill, sel = tc._skill_path(repo, code, t["taskName"], policy=policy, offering=o["offeringName"],
                                     functional_area=f["functionalAreaName"], offering_code=off)
        dup = seen_codes.get(code)
        seen_codes.setdefault(code, seq)
        rows.append({
            "Resolver Sequence": seq,
            "ID": f"TW-{seq:04d}",
            "Offering": o["offeringName"], "Offering Code": off,
            "Functional Area": f["functionalAreaName"], "FA Code": fa,
            "Catalog displaySequence": t.get("displaySequence"),
            "Matched Task Code": code, "Matched Task Name": t["taskName"],
            "Task List Item": t.get("taskListItemShortName"),
            "Mandatory (catalog)": t.get("MandatoryFlag"),
            "FSM export/import": t.get("exportImportSupportedFlag"),
            "Scope Class": cls, "SOW Ref": ref,
            "FSCR Skill Path": skill or "", "Skill Match": sel.get("selected_by"),
            "Duplicate Of Sequence": dup or "",
            "Phase": "Configure (Build)",
            "Sequence Source": "catalog-offline (FA order x displaySequence); no FSM/BOSS discovery",
        })

out.mkdir(parents=True, exist_ok=True)
with open(out / "task_map_tasks.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
with open(out / "task_map_fa_summary.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(fa_rows[0].keys()))
    w.writeheader(); w.writerows(fa_rows)

# initializer-format mapping (schema of project/_template/.../identified-task-mapping.example.json)
mapping = {"tasks": [{
    "ID": r["ID"], "Phase": r["Phase"], "Oracle Setup Task / Activity": r["Matched Task Name"],
    "Evidence": f"SOW {r['SOW Ref']}; Run 14 01_SCOPE.md section 2", "Source Task Name": r["Matched Task Name"],
    "Match Status": "matched", "Match Method": "catalog-exact (offering+FA membership)", "Confidence": 1.0,
    "Matched Task Code": r["Matched Task Code"], "Matched Task Name": r["Matched Task Name"],
    "Match Rationale": "Task is a member of the selected offering/functional area in the FSCR effective catalog.",
    "Data Paths": [], "Notes": f"Scope class {r['Scope Class']}; sequence source {r['Sequence Source']}",
    "Offering": r["Offering"], "Functional Area": r["Functional Area"],
    "Source Reference": f"effective catalog {r['Offering Code']}/{r['FA Code']} displaySequence {r['Catalog displaySequence']}",
    "Resolver Sequence": r["Resolver Sequence"], "Skill Path": r["FSCR Skill Path"],
} for r in rows]}
json.dump(mapping, open(out / "identified-task-mapping.json", "w", encoding="utf-8"), indent=1)

with_skill = sum(1 for r in rows if r["FSCR Skill Path"])
print("FA pairs", len(fa_rows), "expanded", sum(1 for x in fa_rows if x["scope_class"] != "TBD"))
print("tasks", len(rows), "unique codes", len(seen_codes), "with FSCR skill", with_skill)
from collections import Counter
print(Counter(r["Scope Class"] for r in rows))
seqs = [r["Resolver Sequence"] for r in rows]
print("sequence unique positive:", len(set(seqs)) == len(seqs) and min(seqs) == 1)
