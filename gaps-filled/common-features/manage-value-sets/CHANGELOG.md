# CHANGELOG: manage-value-sets (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-20 (batch 1 part 3, filled by AB with Claude)
- Wrote the short card over FSCR's value-sets skill. FSCR's REST resource cannot create a value set, so creation uses the task's FSM CSV package; FSCR's REST resources are used for the read-back. Uses the generic helpers in `manage-docseq-categories/scripts`.
- Found: the Applications Core ModuleId is read by REST from the seeded `YES_NO` lookup (no value copied into the skill). With it, the new value set also shows in the scoped task export.
- Found: the REST key of a value set is its code; the numeric `ValueSetId` gives HTTP 404 on `valueSets/{id}/child/values`.
- Live test: export 0 rows (scoped) -> before-read 0 rows -> import attempt 1 **failed** (`ORA-01400`: my command deleted the module-id file before reading it, so ModuleId was empty) -> attempt 2, 3 rows, 0 failed -> REST read-back of value set and values PASS -> export compare PASS (0 -> 1 value set, 0 -> 2 values).
- During the read-back the saved token expired (about an hour old). The REST client then waits silently for a browser sign-in; the call hung for about 7 minutes until stopped. Sign-in again, then PASS. The card now says to put `timeout 120` in front of REST calls and what a hang means.

## Fresh test, 2026-11-20: PASS
- Sub-agent given only the task name and this SKILL.md path. Created `GAPFILL_VSF1_FRESH1` with `GAPFILL_F1A`, `GAPFILL_F1B`; 1 import attempt, both REST READBACKs PASS, export compare PASS (1 -> 2 value sets, 2 -> 4 values), about 3 min, no help. Confirmed again by the main session (REST PASS).
- Its notes (not applied): `--fscr` given as a Git Bash `$PWD` (`/e/...`) fails; the before-export is no longer empty; the FSCR folder could be confused with other copies nearby; the log shows "In progress" before the final line.

## Test records created (may not be deletable)
| When | Who | Value set | Values |
|---|---|---|---|
| 2026-11-20 live test | Claude (main session) | `GAPFILL_VS_T1` (independent, character, 20, upper case) | `GAPFILL_A`, `GAPFILL_B` |
| 2026-11-20 fresh test | fresh sub-agent | `GAPFILL_VSF1_FRESH1` (same settings) | `GAPFILL_F1A`, `GAPFILL_F1B` |
Neither is used by any flexfield segment.

## Re-test after wording fix, 2026-11-24: PASS
- Fresh sub-agent given only the task name and the current SKILL.md: value set + 2 values, 1 import, REST READBACK PASS and export compare PASS, about 6 min; the tester first picked an unconfigured FSCR copy (export refused), then the configured one; no help. Main session read the record back from Oracle. Evidence: `gaps-filled/evidence/batch-01-retest/FND_MANAGE_APPLCORE_VALUE_SETS/`.
- Notes not applied (wording unchanged after this test): which FSCR folder to use is not obvious when several copies exist; worked-example counts go out of date; the log one-liner leaves `\t` and `\/`.
