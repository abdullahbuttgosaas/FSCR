task_code: ORA_POQ_MANAGE_STANDARDS_ORGANIZATION_LOOKUP
task_name: Manage Standards Organization Lookup
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 4
minutes_to_test: 9
waiting_minutes: 4
fresh_claude_pass: yes (fresh F PASS, re-test R2 PASS; final round on v1.0.2 found no wrong sentence)
route: FSM CSV (standard lookup package: FND_APP_STANDARD_LOOKUP + ORA_FND_APP_STANDARD_LOOKUP_CODE) + REST standardLookups read-back
depends_on: none (seeded user-extensible lookup type POQ_STDS_ORG)
test_records: GAPFILL_AB_S1_SO1 (100004744439771, own test); GAPFILL_AB_S1_SO2F (100004744440224, fresh F); GAPFILL_AB_S1_SO3R (100004744439975, re-test R2 (v1.0.2))
notes: Sourcing batch 01 (sitting 1). New code on lookup type POQ_STDS_ORG; type row copied unchanged from REST (lookup_type_row.py); scope read from the export metadata (scope_lookup_types.py). Own test PASS: 2 rows processed, 0 failed; REST codes 4 -> 5, type unchanged; export compare PASS. Round F (v1.0.0) testers reported a wrong sentence: Step 4 said 'repeat the two export commands of Step 1' (Step 1 has four); also MEANING check placed after the build, stale worked-example counts. Fixed in v1.0.1 (export_after wording, MEANING check before build, counts note, RUN git check, import.out note). Round R (v1.0.1) found: READBACK check crashed with KeyError if CODE missing; Step 1 said to read the level in Step 2 but Step 2 did not print it; 'first two commands' ambiguous; MEANING check not chained. Fixed in v1.0.2 (cb.get, level + count printed, MEANING check stops the build with &&, after-export written out in full). Round R2 (v1.0.2): PASS, no wrong sentence. Suggestions NOT applied (no wrong sentence; each would need a re-test): print the full expected import result lines in Step 3; a small env file for placeholders; say whether the export holds every code or only changed ones (testers saw the export count equal the REST count); Step 1 could print each type's level; check CODE in the MEANING check too. Minutes are this task's share of a 5-task batch that shared one skill template.
