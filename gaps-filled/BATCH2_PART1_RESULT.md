# Batch 2, part 1: Applications Core profiles (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-23. Tested on ETIA-TEST only (release 11.13.26.10.0). No FSCR file was changed (checked: no new file in the 3 FSCR copies after the run). Plan and rules: `BATCH2_PLAN.md`.

| Start | Finish | Note |
|---|---|---|
| 19:46:07 | 20:08 | 4 live loads, 4 skills, 4 fresh tests, wording fixes, 4 re-tests, evidence, index, this report. The planning before it (19:26 to 19:46) is in `BATCH2_PLAN.md`. |

**Sign-in (not counted in any task):** one browser sign-in on port 8765, 19:31:40 to 19:34:27 (about 3 minutes, waiting for you). The token lasted the whole part; no second sign-in. **Waiting for your approvals:** 0 minutes (the brief was the approval).

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min (test + re-test) |
|---|---|---|---:|---:|---|---:|
| 1 | Manage Applications Core Profile Options (`FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS`) | tested | 5 | 2 | PASS, re-test PASS | 6 (3 + 3) |
| 2 | Manage Applications Core Administrator Profile Values (`FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES`) | tested | 4 | 2 | PASS, re-test PASS | 5 (3 + 2) |
| 3 | Manage Applications Core Profile Categories (`FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES`) | tested | 4 | 1 | own rows OK*, re-test PASS | 6 (3 + 3) |
| 4 | Manage Profile Categories (`FND_MANAGE_PROFILE_CATEGORIES`) | tested | 2 | 2 | own rows OK*, re-test PASS | 6 (3 + 3) |
| | **Total** | 4 of 4 tested | **15** | **7** | 4 of 4 | **23** |

\* First fresh tests of 3 and 4 ran at the same time on the same package, so each compare also saw the other tester's category and printed FAIL. Their own rows were correct. Both were re-tested alone after the wording fix and passed.

- Minutes are from the run's time log (`STATUS.md` cards hold the same numbers), with export, import and REST times split out as Oracle waiting. The wording-fix round (about 3 minutes) is shared across the 4 write times.
- Fresh tests ran in the background, in two lanes (options then values; categories then categories), so the 8 tests took about 11 minutes of wall clock.
- **No `retest_after_wording_fix` is pending.** Every wording change was made before the re-tests; notes from the re-tests were written in each CHANGELOG and **not** applied, so the tested wording is the wording on disk.
- Plan estimate (`BATCH2_PLAN.md` section 3): first skill 5 to 11, card 1 to 3. Actual: 5 and 4 for the two full skills, 4 and 2 for the two cards.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (main session) | Fresh test 1 | Re-test |
|---|---|---|---|
| 1 options | `GAPFILL_AB_PO1`; `GAPFILL_AB_PO3` (prerequisite for task 2's fresh test) | `GAPFILL_AB_PO2F` | `GAPFILL_AB_PO5R` |
| 2 values (SITE) | `GAPFILL_AB_V1` on PO1 | `GAPFILL_AB_V3F` on PO3 | `GAPFILL_AB_V2R` on PO2F |
| 3 categories | `GAPFILL_AB_PC1` -> PO1 | `GAPFILL_AB_PC3F` -> PO1 | `GAPFILL_AB_PC5R` -> PO1 |
| 4 categories | `GAPFILL_AB_PC2` -> PO1 | `GAPFILL_AB_PC4F` -> PO3 | `GAPFILL_AB_PC6R` -> PO3 |

At the end the main session read back all 4 options and all 3 site values by REST (PASS) and re-ran both category re-test compares on the testers' exports (PASS). No seeded option or category was touched; all values and links point at `GAPFILL_AB_` options, which no Oracle code reads.

Evidence: `evidence/batch-02/<TASK_CODE>/` with 5 images each: `01_missing.png` (gap index row + FSCR search: no skill), `02_found.png` (read-only export: files, rows, scope), `03_skill.png` (SKILL.md outline), `04_test_result.png` (live read-back), `05_fresh_test.png` (fresh tests + main-session read-back). These are rendered text with no tokens, server addresses or user names.

## Problems and findings
1. **Hierarchical package: child rows need their parent row.** Task 2's first import (value row only) said `A total of 0 rows were processed`, with status "Completed successfully", and created nothing. Copying the existing parent option row unchanged into the ZIP fixed it (2 rows processed). New generic helper: `common-features/manage-profile-options/scripts/copy_parent_rows.py` (refuses parents without your prefix). **`0 rows were processed` must be treated as a failure**; both skills say so.
2. **ModuleId: use `YES_NO`, not the export.** The seeded profile categories carry a different Applications Core module id than the seeded `YES_NO` lookup. My first wording ("all application-0 rows share one ModuleId") was wrong; two fresh testers caught it. Every test row made with the `YES_NO` id shows in the scoped exports, so the skills now say: always `YES_NO`.
3. **No REST resource for profile categories** (`profileCategories`, `profileOptionCategories`, `applicationProfileCategories`: HTTP 404). The after-export compare is the proof for tasks 3 and 4. Profile options and values have REST read-back (`profileOptions`, `.../child/siteProfileOptionValues`, from FSCR's profile-options skill).
4. **`profileOptions/<name>` item GET gives HTTP 400** through the batch 1 `rest_read.py` (it always adds `limit`). The `--q "ProfileOptionName='<name>'"` form works; the child collection URL works.
5. **The compare needs every added row as `--expect`** (3 level rows for one option). My first compare said FAIL for that reason only.
6. **Concurrent testers on one package break the compare.** My scheduling mistake. The category skills now say how to judge it (your rows added, removed 0, changed 0). Lesson: run fresh tests of tasks that share a package one after the other.
7. **Several FSCR copies on the machine** (3 hold `core\auth\fusionEnv.properties`). Testers picked different ones and both worked with the one sign-in. The skills now say to use the copy the person names.
8. **Rest reads print user names** unless `--fields` is given; every read-back command in the skills passes `--fields`.
9. **Exports during planning:** Manage Taxes, Manage Tax Statuses and Manage Applications Core Attachment Entities exports failed (no ZIP); they were left out of batch 2.

## What is reusable for Parts 2 and 3
- **Batch 1 generic helpers** (`common-features/manage-docseq-categories/scripts`): build, inspect, compare, REST read, render. They worked unchanged for 3 new packages.
- **`copy_parent_rows.py`** for any FSM package where you add child rows under an existing parent. Likely needed in Part 3 for Tax Reporting Types (codes under a reporting type, which hangs off the test regime) and anywhere a header already exists.
- **The `0 rows were processed` rule** and **"give every added row as `--expect`"**: put them in every new skill from the start.
- **Fresh-test scheduling:** never run two testers on the same package at once. Part 2's 3 tasks have 3 different packages, so they can run in parallel. In Part 3, Tax Regimes and Tax Reporting Types are different packages, but the reporting-type tester needs the regime first.
- **Evidence script pattern:** `01_missing` to `05_fresh_test`. The renderer used here was a throwaway in the work folder; for Parts 2 and 3, copy the idea or add a `text_png.py` beside the batch 1 helpers.
- **Timing:** tax exports took 78 to 270 seconds in planning, so Parts 2 and 3 will have far more Oracle waiting than this part (about 1 minute per export here). Plan a second sign-in after about 50 minutes.
- **Open for you:** setting values on seeded profile options (the real use of task 2) and linking seeded options to categories (tasks 3 and 4) are **untested** and need your decision on a safe test.

## Cleanup
The work folder `gaps-filled/_work_b2` (exports, payloads, import logs, read-back JSON, time log) was deleted after this report. All sub-agents have finished. The sign-in listener exited after the sign-in, and no Python process or server started by this session is left running. Nothing is committed or pushed.
