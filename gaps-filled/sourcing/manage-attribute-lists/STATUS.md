task_code: PON_MANAGE_ATTRIBUTE_LISTS
task_name: Manage Attribute Lists
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 8
minutes_to_test: 7
waiting_minutes: 5
fresh_claude_pass: yes (fresh F PASS; no wrong sentence)
route: FSM CSV (attribute list package: PON_LINE_ATTR_LISTS, ORA_PON_LIST_ATTRIBUTE_GROUPS, PON_LIST_ATTRIBUTES, PON_LIST_ATTR_SCORES), rows written in full; no REST resource (attributeLists, negotiationAttributeLists HTTP 404), export is the read-back
depends_on: none (SECTION = an enabled code of lookup type PON_LINE_ATTRIBUTE_GROUPS, read live)
test_records: GAPFILL_AB_S2_ATL1 (100004744440351, own test, try 2); GAPFILL_AB_S2_ATL2F (100004743466110, fresh F (v1.0.0))
notes: Sourcing batch 02 (sitting 1). Own test: export empty, rows written in full. Try 1 (ProcessId 100004743465828) refused: JBO-27014 AuctionHeaderId required in SourcingRequirementSectionEO and SourcingRequirementAndAttributeEO, 4 objects failed; export proved nothing created. Diagnosis: list rows are not tied to a negotiation, Oracle's placeholder id is -1. Try 2 with AuctionHeaderId=-1 and LineNumber=-1: 4 objects, 0 failed; export shows 1 list (ACTIVE, LINE), 1 group (GENERAL), 1 attribute (TXT, OPTIONAL), 0 scores. Fresh round F PASS with no wrong sentence. Suggestions NOT applied (no wrong sentence; each would need a re-test): add <text> (the description) to the placeholders; let Step 1's count script also count the metadata XML; add echo rc after the export and import. Suggestions NOT applied: a one-line command for the LIST-exists check after Step 1; a payload check that the ZIP holds only new rows.
