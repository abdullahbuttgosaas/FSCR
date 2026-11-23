"""Static, offline scan of FSCR skill folders for read routes (no Oracle calls).
For each skill: skill_id, execution_mode, task code, CSV export flag, script count, read-like scripts,
declared GET/read endpoints. Output: evidence/F/coverage_scan.json and a printed table.
Why: FSCR has no coverage index of read routes; this answers question F from the skill files themselves."""
import json, re
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_02_understand\fscr-work2")
OUT = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_02_understand\evidence\F\coverage_scan.json")
SKILLS = {
    # 8 areas of this test
    "A1 Business units (ERP)": "pillars/erp/financials/organization-structures/manage-business-unit.md",
    "A2 Price lists (SCM)": "pillars/scm/order-management/pricing/import-price-lists",
    "A3 Payment terms (ERP)": "pillars/erp/financials/customer-billing/manage-receivables-payment-terms",
    "A4 Lookup types/codes (SCM)": "core/fusion-api/apps-common/lookups",
    "A5 Order types (SCM)": "pillars/scm/order-management/orders/manage-order-lookups",
    "A6 Org customers (ERP)": "pillars/erp/financials/customers/manage-customer-uploads",
    "A7 Person customers (ERP)": "pillars/erp/financials/customers/manage-customer-uploads",
    "A8 Address purposes (ERP)": "pillars/erp/financials/customers/manage-customer-uploads",
    # 10 further tasks in other areas
    "F1 Inventory orgs (SCM Inventory)": "pillars/scm/manufacturing-and-supply-chain-materials-management/facilities/manage-inventory-organizations",
    "F2 Advanced inventory parameters (SCM Inventory)": "pillars/scm/manufacturing-and-supply-chain-materials-management/advanced-inventory-management/advanced-inventory-parameters",
    "F3 Procurement agents (SCM Procurement)": "pillars/scm/procurement/procurement-foundation/manage-procurement-agents",
    "F4 Supplier registration (SCM Procurement)": "pillars/scm/procurement/suppliers/configure-supplier-registration",
    "F5 Functional area catalogs (SCM Product Mgmt)": "pillars/scm/product-management/catalogs/manage-functional-area-catalogs",
    "F6 Catalog mappings (SCM Product Mgmt)": "pillars/scm/product-management/advanced-catalogs/manage-catalog-mappings",
    "F7 Ship confirm rules (SCM Shipping)": "pillars/scm/manufacturing-and-supply-chain-materials-management/shipping/ship-confirm-rules",
    "F8 Pick wave release rules (SCM Shipping)": "pillars/scm/manufacturing-and-supply-chain-materials-management/shipping/pick-wave-release-rules",
    "F9 Departments (HCM)": "pillars/hcm/global-human-resources/departments/manage-departments",
    "F10 Collective agreements (HCM)": "pillars/hcm/global-human-resources/collective-agreements/manage-collective-agreements",
}
READ_WORDS = re.compile(r"(read|export|snapshot|reconcil|inspect|find|list|get_|query|compare)", re.I)
ENDPOINT = re.compile(r"(?:GET|get|`)\s*`?(/(?:fscmRestApi|crmRestApi|hcmRestApi)/resources/[^\s`'\")|,]+)")
rows = {}
for label, rel in SKILLS.items():
    p = W / rel
    folder = p if p.is_dir() else p.parent
    manifest = p / "SKILL.md" if p.is_dir() else p
    text = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    files = [f for f in (folder.rglob("*") if p.is_dir() else [p]) if f.is_file()]
    alltext = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files if f.suffix in (".md", ".json", ".py"))
    scripts = [f.name for f in files if f.suffix in (".py", ".sh")]
    g = lambda pat: (re.search(pat, text) or [None, None])[1]
    rows[label] = {
        "path": rel,
        "exists": manifest.exists(),
        "skill_id": g(r'skill_id:\s*"([^"]+)"'),
        "execution_mode": g(r'execution_mode:\s*"([^"]+)"'),
        "task_code": g(r"Task code: `([^`]+)`"),
        "csv_export_supported": g(r"CSV export/import supported: `([^`]+)`"),
        "dataloader_mode": g(r"Data Loader import mode: `([^`]+)`"),
        "scripts": len(scripts),
        "read_like_scripts": [s for s in scripts if READ_WORDS.search(s)],
        "declared_rest_endpoints": sorted(set(ENDPOINT.findall(alltext)))[:15],
        "files_scanned": len(files),
    }
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=1), encoding="utf-8")
for k, r in rows.items():
    print(f"{k} | {r['skill_id']} | mode={r['execution_mode']} | task={r['task_code']} | csv={r['csv_export_supported']} "
          f"| scripts={r['scripts']} read-like={len(r['read_like_scripts'])} | endpoints={len(r['declared_rest_endpoints'])}")
