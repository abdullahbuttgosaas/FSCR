"""One-off: apply the follow-up 2 corrections to ledger.csv, mapping.csv and ledger.md, and add the price-list approval rows."""
import csv
from pathlib import Path

E = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01")

# ledger.csv: correct existing rows in place, then append approval rows
p = E / "ledger.csv"
with open(p, encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f)
    hdr, rows = rd.fieldnames, list(rd)

LOOKUP_NOTE = ("CORRECTED: FSCR gave endpoint (core/fusion-api/apps-common/lookups/references/standard-lookups.md:16/18), "
               "client (core/fusion-api/rest-api-client/scripts/fusion_rest_client.py), discovery order and approval rule "
               "(core/fusion-api/apps-common/lookups/SKILL.md); no body fields. Body fields from Oracle describe "
               "(evidence/standardLookups_describe.json); EnabledFlag Y/N and omitted DisplaySequence = mine")
for r in rows:
    m = r["module"]
    if r["row_type"] == "record" and m.startswith("4 Lookup Types"):
        r["script_origin"] = "FSCR route + client; request body mine"
        r["non_fscr_reliance"] = (LOOKUP_NOTE + "; view standardLookups chosen by me (ORA_DOO_ORDER_TYPES found there); "
                                  "ModuleId 61ECAF4A... copied from existing ORA_DOO_ORDER_TYPES (discovery; 'Order Management' meaning inferred); "
                                  + r["non_fscr_reliance"])
    elif r["row_type"] == "record" and m.startswith("4 Lookup Codes"):
        r["script_origin"] = "FSCR route + client; request body mine"
        r["non_fscr_reliance"] = LOOKUP_NOTE + ("; " + r["non_fscr_reliance"] if r["non_fscr_reliance"] else "")
    elif r["row_type"] == "record" and m.startswith("5 Order Types"):
        r["script_origin"] = "FSCR route + client; request body mine"
        r["non_fscr_reliance"] = (LOOKUP_NOTE + "; view found by FSCR discovery order (run by me)"
                                  + ("; " + r["non_fscr_reliance"] if r["non_fscr_reliance"] else ""))
    elif r["row_type"] == "module" and (m.startswith("4 Lookup") or m.startswith("5 Order")):
        r["route_used"] = "REST via FSCR route + client; request bodies mine (not FSCR end to end)"
    elif m.startswith("3 Payment Terms"):
        if r["row_type"] == "record":
            r["script_origin"] = ("FSCR payment_terms_fsm_package.py, LOCALLY PATCHED 2026-10-28 15:59 (order check); "
                                  "original failed on this pod 2026-10-28 (payment_terms_object_order_mismatch); original not re-tested in this run")
            r["non_fscr_reliance"] = (r["non_fscr_reliance"]
                                      .replace("15-char name limit inferred from existing data (max 15) + Oracle knowledge",
                                               "15-char name limit: Oracle describe paymentTermsLOV Name maxLength 15 (evidence/pt_limit/paymentTermsLOV_describe.json) and FSCR ora_input_validation.md:69"))
        else:
            r["route_used"] = "FSM CSV, FSCR end to end on a locally patched script (with a patch)"

APPROVE = [
    {"row_type": "record", "module": "2 Price Lists (status change)", "area": "SCM",
     "record_value": "Approve FSCRT_Quillon Ridge Wholesale Tents USD F01",
     "created_value": "PriceListId 300000394622041 StatusCode IN_PROGRESS -> APPROVED",
     "fscr_task_code": "CUSTOM_IMPORT_PRICE_LISTS",
     "fscr_skill_path": "import-price-lists/SKILL.md sets STATUS_CODE only in FBDI workbook; no route for existing lists",
     "route_used": "Oracle REST PATCH /fscmRestApi/resources/11.13.18.05/priceLists/300000394622041 body {\"StatusCode\":\"APPROVED\"}",
     "script_origin": "mine (rest_diag.py)", "files_read": "evidence/pricelists/describe.json",
     "start": "06:59:10", "end": "06:59:11", "minutes": "<1", "tool_calls": "1", "retries": "0", "errors": "",
     "approval_stops": "user instruction (follow-up 2)", "oracle_ids": "300000394622041",
     "rows_processed": "1", "rows_failed": "0",
     "readback": "APPROVED; only Status, StatusCode, LastUpdateDate, ETag changed; access sets unchanged",
     "final_status": "approved and verified", "non_fscr_reliance": "Oracle describe (StatusCode updatable)"},
    {"row_type": "record", "module": "2 Price Lists (status change)", "area": "SCM",
     "record_value": "Approve FSCRT_Brindle Harbor Dock Equipment EUR F01",
     "created_value": "PriceListId 300000394623080 StatusCode IN_PROGRESS -> APPROVED",
     "fscr_task_code": "CUSTOM_IMPORT_PRICE_LISTS", "fscr_skill_path": "same",
     "route_used": "Oracle REST PATCH /fscmRestApi/resources/11.13.18.05/priceLists/300000394623080 body {\"StatusCode\":\"APPROVED\"}",
     "script_origin": "mine (rest_diag.py)", "start": "06:59:17", "end": "06:59:18", "minutes": "<1",
     "tool_calls": "1", "retries": "0", "oracle_ids": "300000394623080", "rows_processed": "1", "rows_failed": "0",
     "readback": "APPROVED; only Status, StatusCode, LastUpdateDate, ETag changed", "final_status": "approved and verified"},
]
with open(p, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=hdr)
    w.writeheader()
    w.writerows(rows)
    for r in APPROVE:
        w.writerow({h: r.get(h, "") for h in hdr})

# mapping.csv
m = E / "mapping.csv"
t = m.read_text(encoding="utf-8")
t = t.replace("shortened: Oracle payment term name max 15 chars",
              "shortened: Name maxLength 15 per Oracle describe paymentTermsLOV (evidence/pt_limit/paymentTermsLOV_describe.json)")
t = t.replace("shortened: max 15 chars",
              "shortened: Name maxLength 15 per Oracle describe paymentTermsLOV")
t = t.replace("FSCRT_Quillon Ridge Wholesale Tents USD F01,created 300000394622041",
              "FSCRT_Quillon Ridge Wholesale Tents USD F01,created 300000394622041; approved 2026-11-03 06:59")
t = t.replace("FSCRT_Brindle Harbor Dock Equipment EUR F01,created 300000394623080",
              "FSCRT_Brindle Harbor Dock Equipment EUR F01,created 300000394623080; approved 2026-11-03 06:59")
t = t.replace("30 chars = max 30", "30 chars = max 30 (not verified against describe)")
m.write_text(t, encoding="utf-8")

# ledger.md
(E / "ledger.md").open("a", encoding="utf-8").write("""
## Follow-up 2, 2026-11-03 06:55–07:10 +05:00: approve price lists and correct the records
- The token was still valid (2,638 s left), so no login was needed.
- FSCR route for approving an existing price list: none. `import-price-lists/SKILL.md` sets STATUS_CODE only in the FBDI workbook.
- The read-only `priceLists/describe` shows StatusCode is updatable and the item supports update.
- PATCH StatusCode=APPROVED: 300000394622041 at 06:59:10 returned HTTP 200 APPROVED; 300000394623080 at 06:59:17 returned HTTP 200 APPROVED. One approach, no retries.
- Read-back: only Status, StatusCode, LastUpdateDate and ETag changed. No records created.
- Correction C1: payment terms ran on the copy of `payment_terms_fsm_package.py` locally patched 2026-10-28 15:59. The original failed on this pod on 2026-10-28 (`payment_terms_object_order_mismatch`, `project/draft-impl-project-20261028/state/runs/20261028-payment-term-create-blocked.json`). This run did not re-test the original. Verdict changed from "as is" to "with a patch".
- Correction C2: the 8 lookup and order-type records are "FSCR route and client, my request bodies", not "FSCR end to end". Provenance per part is in RUN_REPORT section 3a.
- Correction C3: the payment-term Name limit of 15 is confirmed by Oracle's describe (`paymentTermsLOV` Name maxLength 15, `evidence/pt_limit/`). It is also stated in FSCR `ora_input_validation.md:69`, which the earlier report missed.
- Correction C4: recount. REST main run: 8 creates and 3 rejected price-list POSTs (earlier "10" was wrong). SOAP: 20 calls, 12 succeeded and 8 faulted (earlier "7" was wrong). Follow-ups: 2 price-list POSTs and 2 PATCHes.
- Usage reading 07:05: context 166,294 (17%; after auto-summary, not comparable); 5-hour 6% (new window); weekly 25%.
- Correction C6: added a report section listing pod changes outside the run's records: the FSCR Run Book, created by FSCR, and the user-granted Pricing Administrator data access.
- Originals of the 4 files before this pass: `evidence/corrections_backup/`.
""")
print("ledger.csv, mapping.csv, ledger.md updated")
