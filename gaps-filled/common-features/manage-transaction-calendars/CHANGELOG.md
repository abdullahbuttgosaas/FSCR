# CHANGELOG: manage-transaction-calendars (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-20 (batch 1 part 3, filled by AB with Claude)
- Wrote SKILL.md and `scripts/calendar_rows.py` (writes the date rows as an argument file). Uses the generic helpers in `manage-docseq-categories/scripts`; `build_fsm_package.py` got `@file` argument support for this (backward compatible).
- The pod had no transaction calendar, so the package was built from the export headers only.
- No REST resource for transaction calendars (5 likely names, all HTTP 404): the second export is the read-back.
- Live test:
  - `GAPFILL_TC_T1`: header only (Mon to Fri business days), 1 attempt, 0 failed. Oracle generated no date rows.
  - `GAPFILL_TC_T2` attempt 1: header + 7 date rows without `DayOfWeek` -> rejected (`JBO-27014: Attribute DayOfWeek ... is required`); nothing created.
  - `GAPFILL_TC_T2` attempt 2: with `DayOfWeek` MON..SUN (taken from the old GL table's 3-letter day codes; a REST lookup search found no GL day lookup) -> 0 failed.
  - Export compare PASS: 0 -> 2 calendars, 0 -> 7 dates, nothing removed or changed. Date format `yyyy/mm/dd` accepted.
- Checked offline that `calendar_rows.py` + `@file` rebuilds byte-identical CSVs to the package that imported.

## Fresh test, 2026-11-20: PASS
- Sub-agent given only the task name and this SKILL.md path. Created `GAPFILL_TCF1_DEC07` with 7 dates (2026/12/07 to 2026/12/13, Mon to Fri business days); 1 import attempt, export compare PASS (2 -> 3 calendars, 7 -> 14 dates), about 2 min, no help. Confirmed again by the main session with a further export (3 calendars, 14 dates).
- Its notes (not applied): the starting export is no longer empty; the FSCR path is only described; one `--expect` per date must be typed or looped (a helper could print them); the export prints a harmless "No matching pillar setup-task metadata found" line.

## Test records created (may not be deletable)
| When | Who | Calendar | Dates |
|---|---|---|---|
| 2026-11-20 live test | Claude (main session) | `GAPFILL_TC_T1` (Mon to Fri) | none |
| 2026-11-20 live test | Claude (main session) | `GAPFILL_TC_T2` (Mon to Fri) | 2026/11/23 to 2026/11/29 (Thursday 2026/11/26 set as not a business day) |
| 2026-11-20 fresh test | fresh sub-agent | `GAPFILL_TCF1_DEC07` (Mon to Fri) | 2026/12/07 to 2026/12/13 |
None is assigned to a ledger.
