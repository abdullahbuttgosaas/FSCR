# CHANGELOG: manage-withholding-tax-calendars (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 2 part 2, filled by AB with Claude)
- Wrote SKILL.md on the batch 1 generic helpers plus a new helper `scripts/period_rows.py` (writes the 12 monthly period rows for the builder, offline).
- Live test: export (7 calendars, 48 periods, 28 s) -> import 1 attempt, 0 failed -> export compare PASS (added 1 calendar + 12 periods, removed 0, changed 0).
- No REST resource found (`payablesCalendars`, `payablesCalendarsLOV`, `specialCalendarsLOV`: HTTP 404); the after-export compare is the read-back.

## Fresh test 1, 2026-11-23 20:22-20:24: FAIL (skill bug)
- Sub-agent given only the task name and this SKILL.md path. Chose `GAPFILL_AB_WHT2F` (16 characters); Oracle rejected the calendar with `JBO-27040` (CalendarName is at most 15 characters). Nothing was created.
- Wording fixed after it: NAME max 15 characters (VERIFIED), `--max-len "CalendarName=15"` in the build so the builder stops first, and a `JBO-27040` note in the import step.

## Re-test after the wording fix, 2026-11-23 20:26-20:28: PASS
- New sub-agent, same rules. Created `GAPFILL_AB_WT3R` (15 characters) with periods Jan-28 to Dec-28; 1 import, compare PASS (8 -> 9 calendars, 60 -> 72 periods). Feb-28 ends 2028/02/29.
- Notes NOT applied (to keep the tested wording): the free-name step could also remind about the 15-character limit; `<yy>` is only explained by the example; Step 2 prints the file summary twice; the inspect note mentions `render_readback.py`, which the skill never uses.
- Main-session check at 20:30: compare re-run on the re-tester's exports with all 13 expects: PASS.

## Test records created (may not be deletable; no supplier or tax uses them)
| When | Who | Record |
|---|---|---|
| live test | main session | calendar `GAPFILL_AB_WHT1`, 12 periods of 2027 |
| fresh test 1 | sub-agent | none (`GAPFILL_AB_WHT2F` rejected) |
| re-test | sub-agent | calendar `GAPFILL_AB_WT3R`, 12 periods of 2028 |
