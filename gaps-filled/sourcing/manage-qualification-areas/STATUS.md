task_code: ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS
task_name: Manage Qualification Areas
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 7
minutes_to_test: 7
waiting_minutes: 4
fresh_claude_pass: yes (fresh F PASS; no wrong sentence)
route: FSM CSV (qualification area package: ORA_POQ_QUAL_AREAS, _OUTCOMES, _QUESTIONS, _BU_ACCESSES) + REST supplierQualificationAreas read-back
depends_on: a procurement business unit (own test unit: common-features test-business-unit + procurement configure-procurement-business-function, function 110); optional own outcome code (ORA_POQ_MANAGE_QUALIFICATION_OUTCOME_LOOKUP)
test_records: GAPFILL_AB_S2_QA1 on own unit GAPFILL_AB_B15_BU1 (100004744440374, own test); GAPFILL_AB_S2_QA2F on own unit GAPFILL_AB_B15_BU2F (100004743464667, fresh F (v1.0.0))
notes: Sourcing batch 02 (sitting 1). Own test: new DRAFT area with 1 outcome ("GAPFILL AB Qualification Outcome 1") on our own test procurement unit, no questions; import 1 row, 0 failed (log counts only the area); REST 1 area DRAFT revision 0 BU ok; export 19 -> 20 areas, 48 -> 49 outcomes, compare PASS. Fresh round F PASS with no wrong sentence. Suggestions NOT applied (no wrong sentence; each would need a re-test): add <text> (the description) to the placeholders; let Step 1's count script also count the metadata XML; add echo rc after the export and import. Suggestion NOT applied: say the description must avoid '|'.
