"""Run-14 offline classifier helper.

Applies FSCR router.project-objective-classifier "Offering-Scope Resolution" rules
to the SOW module list, using ONLY the repo copy's effective catalog. No Fusion calls.
The SOW-text -> functional-area-code mapping (SOW_MAP) is Claude's reading of the SOW;
the catalog lookups, name resolution and ambiguity checks are FSCR's catalog.
Usage: python -I classify_scope.py <repo_root> <out_json>
"""
import json, sys, os

repo, out = sys.argv[1], sys.argv[2]
eff = os.path.join(repo, "knowledge", "setup-task-catalog", "effective")
cat = json.load(open(os.path.join(eff, "offering-functional-area-task-catalog.json"), encoding="utf-8"))["offerings"]
pmap = {i["offeringShortName"]: i["pillar"] for i in
        json.load(open(os.path.join(eff, "pillars-offerings-mapping.json"), encoding="utf-8"))["items"]}

# (sow_ref, sow_text, requested_offering_or_None, [functional-area codes])
SOW_MAP = [
    ("SCM-1", "Product Information Management (items, structures)", "PIM_PROD_MNG",
     ["ORA_EGP_FA_ITEMS", "EGO_ADVANCED_PRODUCT_STRUCT", "ORA_EGP_FA_ITEM_ORGANIZATIONS"]),
    ("SCM-2", "Inventory and Cost Management", "ORA_MANUFACTURING_AND_SUPPLY_C",
     ["ORA_RCS_FACILITIES", "ORA_WSH_INVENTORY_MGMT", "WSH_ENABLE_RECEIVING",
      "CST_DEFINE_COST_MANAGEMENT", "CMR_RECEIPT_ACCOUNTING"]),
    ("SCM-3", "Self-Service Procurement", "PO_PROCUREMENT",
     ["PO_SSP_DEPLOYED", "ORA_PO_APPROVAL_MANAGEMENT_FA", "ORA_PO_PRC_TRX_ACC_RULES_FA"]),
    ("SCM-4", "Purchasing", "PO_PROCUREMENT",
     ["ORA_PO_PROC_FOUNDATION_FA", "ORA_PO_PURCHASING_FOUNDATION"]),
    ("SCM-5", "Supplier Portal", "PO_PROCUREMENT", ["PO_SUP_PORTAL_DEPLOYED", "ORA_EGP_SUPPLIERS"]),
    ("SCM-6", "Manufacturing (process-based)", "ORA_MANUFACTURING_AND_SUPPLY_C", ["ORA_WIS_COMMON_MFG_WORK_SETUP"]),
    ("SCM-7", "Maintenance", "ORA_MANUFACTURING_AND_SUPPLY_C", ["ORA_MNT_MGMT"]),
    ("FIN-ES", "Confirm Enterprise (BU) Structure", None,
     ["ORA_ASK_LEGAL_STRUCTURES", "ORA_ASK_FIN_REPORTING_STRUCT", "ORA_ASK_ORGANIZATION_STRUCTURE"]),
    ("FIN-GL", "General Ledger / Subledger Accounting (incremental)", "XLE_FINANCIALS_JUR", ["ORA_FIN_GENERAL_LEDGER"]),
    ("FIN-AP", "Payables (incremental)", None, ["FIN_PAYABLES_DEPLOYED"]),
    ("FIN-AR", "Receivables (remediation, TBD)", "XLE_FINANCIALS_JUR", ["FIN_RECEIVABLES_DEPLOYED"]),
    ("FIN-CE", "Cash Management (remediation, TBD)", None, ["ORA_CE_CASH_MGMT_BANK"]),
    ("FIN-FA", "Fixed Assets (remediation, TBD)", "XLE_FINANCIALS_JUR", ["FIN_FIXED_ASSETS_DEPLOYED"]),
    ("FIN-PJ", "Project Cost Management (incremental)", "PJF_PROJ_MNG", ["ORA_PJC_PROJ_COSTING_BASE_FA"]),
    ("FIN-GM", "Grants Management (remediation, TBD)", "ORA_GMS_GRANTS_MANAGEMENT", ["ORA_GMS_GRANTS_BASE_FA"]),
    ("FIN-SUS", "Supply Chain Sustainability", None, ["ORA_SUS_SUSTAINABILITY"]),
    ("FIN-EXM", "Expenses (conditional on design session)", "XLE_FINANCIALS_JUR", ["FIN_EXPENSES_DEPLOYED"]),
    ("FIN-RPT", "Reporting approach (OTBI/BIP/FDI/EPM)", "XLE_FINANCIALS_JUR", ["ORA_FIN_REPORT_CENTER"]),
    ("CFG-12", "Security and Roles", None, ["ORA_ASK_USERS_AND_SECURITY"]),
]

rows, diags = [], []
for ref, text, off, fas in SOW_MAP:
    for fa in fas:
        cands = sorted(oc for oc, v in cat.items() if fa in v.get("functionalAreas", {}))
        if off:
            if off not in cat:
                status, chosen = "pending", None
                diags.append({"sow_ref": ref, "fa": fa, "class": "catalog_or_metadata_mismatch",
                              "msg": f"offering {off} not in effective catalog"})
            elif off in cands:
                status, chosen = "resolved", off
            else:
                status, chosen = "pending", None
                diags.append({"sow_ref": ref, "fa": fa, "class": "catalog_or_metadata_mismatch",
                              "msg": f"FA not under requested offering {off}", "candidates": cands})
        else:
            status = "resolved" if len(cands) == 1 else "pending"
            chosen = cands[0] if len(cands) == 1 else None
            if status == "pending":
                diags.append({"sow_ref": ref, "fa": fa, "class": "input_validation",
                              "msg": "no offering supplied and FA belongs to multiple offerings; human review",
                              "candidates": cands})
        fa_name = next((cat[c]["functionalAreas"][fa]["functionalAreaName"] for c in cands), None)
        task_count = cat[chosen]["functionalAreas"][fa]["taskCount"] if chosen else None
        rows.append({"sow_ref": ref, "sow_text": text, "functional_area_code": fa,
                     "functional_area_name": fa_name, "offering_scope_status": status,
                     "offering_short_code": chosen,
                     "offering_name": cat[chosen]["offeringName"] if chosen else None,
                     "pillar": pmap.get(chosen) if chosen else None,
                     "candidate_offerings": cands, "effective_task_count": task_count})

gaps = [
    {"sow_ref": "SCM-6.2", "item": "Process Manufacturing (vs discrete)", "finding": "no separate effective functional area; process-vs-discrete is a plant/work-definition choice inside ORA_WIS_COMMON_MFG_WORK_SETUP (not verified in catalog task list)"},
    {"sow_ref": "SCM-7.5/7.7", "item": "Meters, Installed Base tracking", "finding": "no separate functional area found by name; assumed inside ORA_MNT_MGMT (not verified)"},
    {"sow_ref": "FIN-RPT 6.1", "item": "FDI / EPM reporting strategy", "finding": "no FSCR offering or skill for Fusion Data Intelligence or EPM"},
    {"sow_ref": "RICE-R1", "item": "Printable Purchase Order (BIP)", "finding": "no FSCR setup task; custom report development"},
    {"sow_ref": "RICE-C1", "item": "Supplier conversion", "finding": "FSCR shared/data-conversion skills exist but were not exercised (planning only)"},
]

res = {"classifier_skill": "router.project-objective-classifier",
       "catalog_path": "knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json",
       "pillar_map_path": "knowledge/setup-task-catalog/effective/pillars-offerings-mapping.json",
       "fusion_calls": 0, "functional_area_scope": rows, "scope_diagnostics": diags, "catalog_gaps": gaps}
res["resolved_offerings"] = sorted({(r["offering_short_code"], r["offering_name"], r["pillar"])
                                     for r in rows if r["offering_short_code"]})
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(res, open(out, "w", encoding="utf-8"), indent=2)
print("rows", len(rows), "resolved", sum(r["offering_scope_status"] == "resolved" for r in rows),
      "pending", len(diags))
for o in res["resolved_offerings"]:
    print("OFFERING", o)
for dg in diags:
    print("DIAG", dg)
