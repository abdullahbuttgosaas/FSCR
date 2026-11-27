# Changelog: Manage Sourcing Value Sets

- 2026-11-27, Sourcing batch 02 (AB with Claude, sitting 1). Skill written from the read-only export and the own live test.
- Own test: new INDEP VARCHAR2(20) value set with values GAPFILL_A, GAPFILL_B; ModuleId from PON_LINE_ATTRIBUTE_GROUPS lands it in the task scope; import 3 rows, 0 failed; REST PASS; export compare PASS (0 -> 1 value set, 0 -> 2 values).
- fresh F (v1.0.0): GAPFILL_AB_S2_SVS2F (ProcessId 100004744441184) PASS.
- re-test R (v1.0.1): GAPFILL_AB_S2_SVS3R (ProcessId 100004743466262) PASS.
- Round F (v1.0.0): record created and REST PASS, but both testers reported a wrong line: the Step 4 compare keyed values on Value alone, so the same value names in another test value set showed as 'changed' (false FAIL), and the sentence 'the values show as added too' was false. Fixed in v1.0.1: key FND_APP_FLEX_VALUE_SET.ValueSetCode+Value with an --expect per value, <text> placeholder, first-run note in Step 1. 
- Suggestions NOT applied (no wrong sentence; each would need a re-test): add <text> (the description) to the placeholders; let Step 1's count script also count the metadata XML; add echo rc after the export and import. 
