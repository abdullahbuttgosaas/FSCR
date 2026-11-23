# Batch 2, part 3: transaction tax roots (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-23. Tested on ETIA-TEST only (release 11.13.26.10.0).
- The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`. No FSCR file was edited: `git status` shows no change and no new file under `fscr-main`.
- Plan and rules: `BATCH2_PLAN.md`. This part reused what Parts 1 and 2 learned (`BATCH2_PART1_RESULT.md`, `BATCH2_PART2_RESULT.md`).

| Start | Finish | Note |
|---|---|---|
| 21:06:57 | about 21:41 | 3 read-only exports (with network retries), 3 live loads, 3 skills, 3 fresh tests, 1 wording fix, 1 re-test, evidence, index, this report. |

**Sign-in (not counted in any task):** I first checked that nothing was listening on port 8765, then signed in from 21:07:13 to 21:07:24 (11 seconds; the browser session was still signed in, so you had nothing to do). There was no second sign-in.

**Waiting for your approvals:** 0 minutes (the brief was the approval).

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min (test + re-test) |
|---|---|---|---:|---:|---|---:|
| 8 | Manage Tax Regimes (`ZX_MANAGE_TAX_REGIMES`) | tested | 7 | 5 | PASS, re-test PASS | 6 (3 + 3) |
| 9 | Manage Tax Reporting Types (`ZX_MANAGE_TAX_REPORTING_TYPES`) | tested | 5 | 4 | PASS | 5 |
| 10 | Manage Tax Determining Factor Sets (`ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS`) | tested | 4 | 3 | PASS | 4 |
| | **Total** | 3 of 3 tested | **16** | **12** | 3 of 3 | **15** |

- Minutes come from the run's time log; the `STATUS.md` cards hold the same numbers. The network retries on the first exports (about 8 minutes of wall clock, 21:07 to 21:19) are counted as Oracle waiting, split across the 3 tasks.
- The 3 tasks use 3 different packages, so the 3 fresh tests ran in parallel (21:30 to 21:35).
  - The reporting-type tester used the live-test regime `GAPFILL_AB_TR1`, which already existed, so the order rule "8 before 9" held.
- **No `retest_after_wording_fix` is pending.**
  - Only the regime skill changed after its fresh test, and it was re-tested (PASS).
  - Notes from the last test of each task are written in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested.
- `rebuild_index.py`: **No problems.** Common Features went from 16 to **19 tested** of 148. Batch 2 total: 9 of 10 tested; Manage Tax Zone Types (Part 2) is still failed.
- Plan estimate (`BATCH2_PLAN.md` section 3): 5 to 11 minutes for a first skill (#8) and 1 to 4 for the others. Actual: 7, 5 and 4.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (main session) | Fresh test 1 | Re-test |
|---|---|---|---|
| 8 regimes (no subscription) | `GAPFILL_AB_TR1` | `GAPFILL_AB_TR2F` | `GAPFILL_AB_TR3R` |
| 9 reporting types (TEXT, regime level, no usage) | `GAPFILL_AB_RT1` + code `GAPFILL_AB_C1` on TR1 | `GAPFILL_AB_RT2F` + code `GAPFILL_AB_C2F` on TR1 | - |
| 10 factor sets (no regime, no condition set) | `GAPFILL_AB_FS1` | `GAPFILL_AB_FS2F` | - |

At the end the main session checked the records itself:
- It read back TR1, TR2F and TR3R by REST (`taxRegimesLOV`): 3 rows, PASS.
- It re-ran both testers' compares: PASS. The export now holds exactly RT1 and RT2F, and FS1 and FS2F, as test records.

No subscription, usage, association, condition set or rule was created, so no real transaction or tax result can change. The no-regime template set was copied, not changed.

Evidence: `evidence/batch-02/<TASK_CODE>/` holds 5 images per task, `01_missing` to `05_fresh_test`. They are rendered text with no tokens, server addresses or user names.

## Problems and findings
1. **The network dropped often on tax exports.**
   - The 3 first exports ran in parallel. All 3 failed: `The read operation timed out` or `Remote end closed connection without response`.
   - The 2 retries also failed.
   - The third round, run one export at a time, worked.
   - The fresh testers' exports (3 testers in parallel) all worked first time, so the drops seem to come and go rather than follow a pattern.
   - All 3 skills now say to re-run a failed export into a new folder, one at a time, up to 3 tries.
2. **The live regime import lost its connection after the process started.** No process log was written. I did **not** import again: REST showed the regime 1 minute later, and the compare confirmed it. The regime skill says to check before any retry, and the other 2 skills say the same.
3. **A `/e/...` path makes FSCR write to the wrong place.** My export wrapper passed a Git Bash `/e/...` output path, and the export script wrote the ZIP under `E:\e\...`. I moved the ZIP into the work folder and removed the empty stray folders. All 3 skills now require `E:/...` paths.
4. **Reporting types: a TEXT type needs a minimum length.** Import 1 failed with `ZX_MIN_LENGTH_VALUE` and created nothing. Import 2, with MinLength 1 and MaxLength 30, passed. The test environment has **no** reporting types to copy, so the skill writes the rows out in full. Only the `TEXT` data type is tested.
5. **The builder rejects empty key columns.** A regime-level reporting type has `Tax` empty, so `Tax` is not part of the keys.
6. **REST:**
   - `taxRegimesLOV` works and gives the regime a REST read-back.
   - These return HTTP 404: `taxRegimes`, `taxReportingTypes`, `taxReportingTypesLOV`, `taxReportingTypeCodes`, `taxReportingCodesLOV`, `taxDeterminingFactorSets`, `taxDeterminingFactorSetsLOV`, `taxRuleTemplates`.
   - The ZX lookups (reporting data types) are not in `standardLookupsLOV`.
7. **The import log is hard to read.** It repeats the same detail lines many times, and the real row count sits under another business object's name (for example, `TaxRegime` under a subscription object). The skills give a one-liner that prints only the detail objects that processed rows, the error texts and the totals.

## What is reusable later
- **`common-features/manage-tax-regimes/scripts/template_row.py`** (new, generic, offline). It turns one existing export row into a `--row` for the builder, with `--set` and `--clear`. It empties audit columns and prints column names only. It fits any task where a new record can copy a known-good one: other ZX objects, and also non-tax setups.
- **The import-log summary one-liner** in the 3 tax skills. It works for any FSM import.
- **The next tax tasks** depend on these test records:
  - Manage Taxes, Tax Statuses and Tax Rates can hang off `GAPFILL_AB_TR1`.
  - Manage Tax Condition Sets can use `GAPFILL_AB_FS1`.
  - Their exports failed during planning (no ZIP), so retry them one at a time.
- **Open for you:** subscriptions, reporting-type usages and associations, and condition sets or rules on these records are **untested**. They change real tax behaviour and need your decision on a safe test.

## Cleanup
- The work folder `gaps-filled/_work_b2p3` (exports, payloads, import logs, read-back JSON, time log) was deleted after this report.
- All 4 sub-agents (3 fresh tests and 1 re-test) have finished.
- The sign-in listener exited after sign-in. No Python process or server started by this session is left, and nothing listens on port 8765.
- Nothing is committed or pushed. Part 1 and Part 2 tasks were not touched.
