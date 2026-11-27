task_code: PON_MANAGE_SOURCING_VALUE_SETS
task_name: Manage Sourcing Value Sets
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 5
minutes_to_test: 10
waiting_minutes: 5
fresh_claude_pass: yes (fresh F PASS, re-test R PASS; v1.0.0 compare line was wrong, fixed in v1.0.1 and re-tested)
route: FSM CSV (FND_APP_FLEX_VALUE_SET package scoped to moduleKey PrcPonCommon; ModuleId read live from lookup PON_LINE_ATTRIBUTE_GROUPS) + REST valueSets read-back
depends_on: none (module id read live)
test_records: GAPFILL_AB_S2_SVS1 (100004743465550, own test); GAPFILL_AB_S2_SVS2F (100004744441184, fresh F (v1.0.0)); GAPFILL_AB_S2_SVS3R (100004743466262, re-test R (v1.0.1))
notes: Sourcing batch 02 (sitting 1). Own test: new INDEP VARCHAR2(20) value set with values GAPFILL_A, GAPFILL_B; ModuleId from PON_LINE_ATTRIBUTE_GROUPS lands it in the task scope; import 3 rows, 0 failed; REST PASS; export compare PASS (0 -> 1 value set, 0 -> 2 values). Round F (v1.0.0): record created and REST PASS, but both testers reported a wrong line: the Step 4 compare keyed values on Value alone, so the same value names in another test value set showed as 'changed' (false FAIL), and the sentence 'the values show as added too' was false. Fixed in v1.0.1: key FND_APP_FLEX_VALUE_SET.ValueSetCode+Value with an --expect per value, <text> placeholder, first-run note in Step 1. Round R (v1.0.1) GAPFILL_AB_S2_SVS3R: PASS, no wrong sentence. Suggestions NOT applied (no wrong sentence; each would need a re-test): add <text> (the description) to the placeholders; let Step 1's count script also count the metadata XML; add echo rc after the export and import.
