task_code: PON_MANAGE_NEGOTIATION_STYLES
task_name: Manage Negotiation Styles
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 6
minutes_to_test: 7
waiting_minutes: 4
fresh_claude_pass: yes (fresh F PASS; no wrong sentence)
route: FSM CSV (negotiation style package: PON_NEGOTIATION_STYLES, PON_DOCTYPE_STYLES and translations); no REST resource (negotiationStyles, supplierNegotiationStyles, sourcingNegotiationStyles HTTP 404), export compare is the read-back
depends_on: none (seeded style Standard_Negotiation is copied)
test_records: GAPFILL_AB_S2_STY1 (100004743464567, own test); GAPFILL_AB_S2_STY2F (100004744442096, fresh F (v1.0.0))
notes: Sourcing batch 02 (sitting 1). Own test: clone of Standard_Negotiation (clone_rows.py, new helper): 1 style + 1 translation + 3 document types + 3 translations; import 2 objects, 0 failed; export 5 -> 6 styles, 15 -> 18 document-type rows; compare PASS; ACTIVE, SystemFlag N, 3 document types enabled. Fresh round F PASS with no wrong sentence. Suggestions NOT applied (no wrong sentence; each would need a re-test): add <text> (the description) to the placeholders; let Step 1's count script also count the metadata XML; add echo rc after the export and import. Suggestion NOT applied: print the source style's document types in Step 4.
