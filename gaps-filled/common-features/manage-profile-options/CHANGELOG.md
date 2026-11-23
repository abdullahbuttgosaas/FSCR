# CHANGELOG: manage-profile-options (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 2 part 1, filled by AB with Claude)
- Wrote SKILL.md on the batch 1 generic helpers (`manage-docseq-categories/scripts`) plus a new helper `scripts/copy_parent_rows.py` (used by the values card).
- Live test: export (91 options, 273 levels, 45 values) -> ModuleId from YES_NO -> REST before-read 0 rows -> import 1 attempt, 4 rows, 0 failed -> REST read-back PASS -> export compare PASS (only after giving all 3 level rows as --expect; the first compare run said FAIL for that reason).
- REST item form `profileOptions/<name>` gives HTTP 400 through rest_read.py (it adds limit); the `--q` form works.

## Fresh test 1, 2026-11-23 19:55-19:58: PASS
- Sub-agent given only the task name and this SKILL.md path. Created `GAPFILL_AB_PO2F`; 1 import, REST PASS, compare PASS, no help.
- Notes applied as wording after it: which FSCR copy to use when there are several; how to see column names (inspect_export prints counts only); dates are yyyy/mm/dd; export counts grow.

## Re-test after the wording fix, 2026-11-23 20:00-20:03: PASS
- New sub-agent, same rules. Created `GAPFILL_AB_PO5R`; 1 import, REST PASS, compare PASS.
- Notes NOT applied (to keep the tested wording): no example for the Description text; the export also prints `StatusCode: (unknown)`; the FSCR root may be the pack folder itself.

## Test records created (may not be deletable; no code reads them)
| When | Who | Record |
|---|---|---|
| live test | main session | option `GAPFILL_AB_PO1` (later: site value GAPFILL_AB_V1, categories PC1, PC2, PC3F, PC5R link to it) |
| prerequisite for the values fresh test | main session | option `GAPFILL_AB_PO3` |
| fresh test 1 | sub-agent | option `GAPFILL_AB_PO2F` |
| re-test | sub-agent | option `GAPFILL_AB_PO5R` |
