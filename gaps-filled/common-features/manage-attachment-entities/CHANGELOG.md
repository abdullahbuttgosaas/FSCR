# CHANGELOG: manage-attachment-entities (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-24 (batch 4 part 1, AB with Claude)
- Read-only export: see `evidence/batch-04/FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES/02_found.png`.
- Live test: try 1 `GAPFILL_AB_P1_AE1` without DataObjectCode (ProcessId 100004741418453): JBO-27014, 0 rows, not created. Read-only export of FND_MANAGE_ATTACHMENT_ENTITIES: working entities use DataObjectCode = upper-case EntityName. Try 2 `GAPFILL_AB_P1_AE2` (ProcessId 100004741416829): 1 row, 0 failed; export compare added 1, removed 0, changed 0: PASS.
- Fresh test (task name + SKILL.md only): PASS, `GAPFILL_AB_P1_AE3F`, ProcessId 100004741416861, about 3 minutes, no guesses. Added row checked in the main session (table, key, DataObjectCode): PASS.
- Tester notes, **not applied** (tested wording stays on disk): 'export may be empty' should say 'or hold earlier test entities'; environment name in FSCR output file names; Step 3 relies on the cd of Step 2 (harmless with --fscr); how to count minutes.

## Test records created
- GAPFILL_AB_P1_AE2 (live); GAPFILL_AB_P1_AE3F (fresh test); entities on FND_LOOKUP_TYPES / LOOKUP_TYPE, no category link. GAPFILL_AB_P1_AE1 was refused, not created.
