# CHANGELOG: manage-document-sequences (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 2 part 2, filled by AB with Claude)
- Wrote SKILL.md on the batch 1 generic helpers (`manage-docseq-categories/scripts`). No new script.
- Live test: export (35 sequences, 36 assignments, 64 s) -> REST before-read 0 rows -> import 1 attempt, 1 row, 0 failed -> REST read-back PASS -> export compare PASS (added 1, removed 0, changed 0).
- REST `documentSequences` exists and filters by `Name`; `documentSequencesLOV` gives HTTP 404.
- The assignment file goes in header-only; no assignment is made in a test (it would number real documents).

## Fresh test 1, 2026-11-23 20:21-20:24: PASS
- Sub-agent given only the task name and this SKILL.md path. Created `GAPFILL_AB_DS2F`; 1 import, REST PASS, compare PASS, no help.
- Notes applied as wording after it: show ModuleId in the Step 2 columns; prefer a source row that is not an earlier test row; export counts grow with every test.

## Re-test after the wording fix, 2026-11-23 20:26-20:29: PASS
- New sub-agent, same rules. Created `GAPFILL_AB_DS3R` (source row: an existing type A customer-account sequence); 1 import, REST PASS, compare PASS (37 -> 38 sequences, assignments 36 -> 36).
- Notes NOT applied (to keep the tested wording): the skill does not say which StartDate to pick (tester used today); it could say outright to skip type A rows with an empty TableName.
- Main-session REST read-back at 20:29: DS1, DS2F and DS3R all present, type A, initial value 1: PASS.

## Test records created (may not be deletable; no assignment, so they number no document)
| When | Who | Record |
|---|---|---|
| live test | main session | sequence `GAPFILL_AB_DS1` |
| fresh test 1 | sub-agent | sequence `GAPFILL_AB_DS2F` |
| re-test | sub-agent | sequence `GAPFILL_AB_DS3R` |
