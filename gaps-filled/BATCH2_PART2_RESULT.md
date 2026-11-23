# Batch 2, part 2: document sequences, withholding tax calendars, tax zone types (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-23. Tested on ETIA-TEST only (release 11.13.26.10.0). The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack` and no FSCR file was edited (checked: `git status` shows no change or new file under `fscr-main`). Plan and rules: `BATCH2_PLAN.md`. Part 1 learnings were reused (see `BATCH2_PART1_RESULT.md`).

| Start | Finish | Note |
|---|---|---|
| 20:13:05 | about 20:33 | 3 read-only exports, 3 live loads (T7 tried 3 times), 3 skills (1 marked failed), 2 fresh tests, wording fixes, 2 re-tests, evidence, index, this report. |

**Sign-in (not counted in any task):** port 8765, 20:13:05 to 20:13:10 (5 seconds; the browser session was still signed in, so you had nothing to do). No second sign-in. **Waiting for your approvals:** 0 minutes (the brief was the approval).

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min (test + re-test) |
|---|---|---|---:|---:|---|---:|
| 5 | Manage Document Sequences (`FND_MANAGE_DOCUMENT_SEQUENCES`) | tested | 5 | 2 | PASS, re-test PASS | 6 (3 + 3) |
| 6 | Manage Withholding Tax Calendars (`ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS`) | tested | 5 | 2 | FAIL (skill bug), re-test PASS | 4 (2 + 2) |
| 7 | Manage Tax Zone Types (`ZX_MANAGE_TAX_ZONE_TYPES`) | **failed** | 6 | 5 | not run (nothing works yet) | 0 |
| | **Total** | 2 of 3 tested | **16** | **9** | 2 of 2 run | **10** |

- Minutes come from the run's time log. The `STATUS.md` cards hold the same numbers.
- The 3 tasks use 3 different packages, so their exports, live loads and fresh tests ran in parallel.
- **No `retest_after_wording_fix` is pending.** Every wording change was made before the re-tests. Re-test notes are written in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested.
- `rebuild_index.py`: **No problems.** Common Features went from 14 to **16 tested** of 148. Task 7 shows as `failed`.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (main session) | Fresh test 1 | Re-test |
|---|---|---|---|
| 5 sequences (type A, no assignment) | `GAPFILL_AB_DS1` | `GAPFILL_AB_DS2F` | `GAPFILL_AB_DS3R` |
| 6 calendars (GENERAL, monthly) | `GAPFILL_AB_WHT1` + 12 periods of 2027 | none (`GAPFILL_AB_WHT2F` rejected) | `GAPFILL_AB_WT3R` + 12 periods of 2028 |
| 7 zone types | none (`GAPFILL_AB_ZT1` tried 3 times, never created; checked by new exports) | - | - |

At the end the main session checked the records itself:
- It read back DS1, DS2F and DS3R by REST: 3 rows, all type A. PASS.
- It re-ran the calendar compare on the re-tester's exports with all 13 expects. PASS.

No assignment was created, so no real document gets a number from these sequences. No supplier or tax uses the calendars.

Evidence: `evidence/batch-02/<TASK_CODE>/`. Tasks 5 and 6 each have 5 images: `01_missing` to `05_fresh_test`. Task 7 has 4 images (01 to 04), and its 04 shows the failed imports. All images are rendered text with no tokens, server addresses or user names.

## Problems and findings
1. **Tax zone types: the import fails at the database insert.**
   - Attempt 1 failed with `JBO-27014: Attribute CreatedByModule ... is required`.
   - Attempt 2 added `CreatedByModule=HZ_GEO_HIERARCHY`. The row then validated (`1 rows processed, 0 failed`), but the object ended with `JBO-26041 Failed to post data ... Insert` into `HZ_GEOGRAPHY_TYPES_B`.
   - Attempt 3 also copied the country limit from the existing zone type. It failed the same way.
   - I stopped at 3 attempts. `manage-tax-zone-types/SKILL.md` is kept as a failed recipe with the 9-file package, the attempts, and 4 ideas for the next try:
     1. a name with spaces and mixed case;
     2. create one zone type on the screen and copy every row it adds;
     3. leave out the translation row;
     4. read the full ESS log for the ORA- error.
   - **Needs your decision:** whether a screen-created zone type in a test environment is acceptable as the reference.
2. **The withholding tax calendar name can be at most 15 characters** (`JBO-27040`). My first skill said nothing about it, so the fresh tester picked a 16-character name and failed, though nothing was created. The skill now says so, and the builder stops first (`--max-len "CalendarName=15"`). Lesson: check every key column's length in the live test, and count the fresh tester's likely name (`PREFIX` + about 4 characters) against it.
3. **REST read-back:**
   - `documentSequences` works with `--q "Name='...'"`, but `documentSequencesLOV` returns 404.
   - No REST resource was found for calendars (`payablesCalendars`, `payablesCalendarsLOV`, `specialCalendarsLOV`) or zone types (`geographyTypes`, `taxZoneTypes`, `zoneTypes`); all return 404.
   - CRM `geographies` returns 400 on the filter.
   - For tasks 6 and 7, the after-export compare is the proof.
4. **Document sequence source row:** ApplicationId, ModuleId and TableName must come together from one existing type A row with a TableName. The export also has a type A row with an empty TableName; the re-tester noted the skill could warn about it. That note is not applied.
5. **The calendar package has 2 files** (calendar type plus periods). The new helper `period_rows.py` writes the 12 period rows offline. Leap years are handled correctly (Feb-28 ends 2028/02/29).
6. Small run issue: `text_png.py` needs Pillow, so it must run without `python -I`.

## What is reusable for Part 3
- **Batch 1 generic helpers** (`common-features/manage-docseq-categories/scripts`): they worked unchanged for 3 more packages.
- **`manage-withholding-tax-calendars/scripts/period_rows.py`**: for any FSM package with dated monthly periods.
- **Check REST first, with a short list of names.** Expect 404 for most tax and geography objects. Fall back to the after-export compare, giving every added row as `--expect`.
- **Name-length check before the fresh test:** find the shortest key-column limit in the live test and write it into the skill's placeholders and the builder's `--max-len`.
- **Task 7 lesson for the tax tasks in Part 3:** a row that validates (`1 rows processed, 0 failed`) can still fail at the database insert. Always read the object status and `Total Objects Failed`, then confirm with a new export.
- **Work wrappers:**
  - `export_one.sh` (export plus unzip) and `import_one.sh` (import plus the key log lines). They were throwaway files in the work folder; rebuild them from the commands in any skill's Steps 2 and 5.
  - Exports took 28 to 165 seconds here.

## Cleanup
- The work folder `gaps-filled/_work_b2p2` was deleted after this report. It held the exports, payloads, import logs, read-back JSON and the time log.
- All 4 sub-agents (2 fresh tests, 2 re-tests) have finished.
- The sign-in listener exited after sign-in. No Python process or server started by this session is left, and nothing listens on port 8765.
- Nothing is committed or pushed. Part 1 and Part 3 tasks were not touched.
