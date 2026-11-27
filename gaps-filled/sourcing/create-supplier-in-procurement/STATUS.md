task_code: ORA_EGP_CREATE_SUPPLIER_IN_PRC
task_name: Create Supplier in Procurement
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-28
minutes_to_write: 5
minutes_to_test: 3
waiting_minutes: 1
fresh_claude_pass: yes (fresh F PASS; no wrong sentence)
route: REST suppliers POST (no FSM CSV: task export refused, CSVExportImportSupportedFlag N)
depends_on: none
test_records: GAPFILL_AB_S4_SUP1 (supplier number 12331, own test, HTTP 201); GAPFILL_AB_S4_SUP2F (supplier number 12332, fresh F (v1.0.0), HTTP 201)
notes: Sourcing batch 04 (sitting 2). Level "neither": the CSV export is refused (flag N), but REST suppliers has create (describe). New PROSPECTIVE supplier, tax organization type CORPORATION, no address, site or contact; created at once (Status ACTIVE, CreationSourceCode WEB_SERVICE), read back by REST. Duplicate check proved on a known supplier first. Suppliers cannot be deleted. Suggestions NOT applied: escape apostrophes in the control name or use SupplierId; encoding in Step 1's json.load; echo rc for every call; record the supplier number.
