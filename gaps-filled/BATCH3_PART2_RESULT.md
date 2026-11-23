# Batch 3, part 2: tax rates, jurisdictions, condition sets, rules (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-24 (Oracle clock 2026-11-23). Tested on ETIA-TEST only (release 11.13.26.10.0).
- The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`. No FSCR file was edited.
- Plan and rules: `BATCH3_PLAN.md` (RULES 1 to 18, and the "Update after Part 1" note). Reused Part 1's helpers, its test tax `GAPFILL_AB_P1_TX1`, batch 2's regime `GAPFILL_AB_TR1` and factor set `GAPFILL_AB_FS1`.

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 00:39 | 00:40 | 1 | Reading plan and Part 1 result |
| 00:40:02 | 00:40:10 | 0 | Sign-in on port 8765 (browser was still signed in; not counted in any task) |
| 00:40 | 01:00 | 20 | 6 read-only exports, 7 live imports (2 created), read-back exports and compares |
| 00:59 | 01:05 | 6 | 4 skills, cards, changelogs, evidence 01 to 04 |
| 01:01 | 01:14 | 13 | 2 fresh tests in parallel, 1 wording fix, 1 re-test |
| 01:14 | 01:18 | 4 | Evidence 05, index, this report, cleanup |

**Waiting for your approvals:** 0 minutes (the brief was the approval). No second sign-in was needed.

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 4 | Manage Tax Rates and Tax Recovery Rates (`ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES`) | **failed** (blocked by `ZX_MANAGE_TAX_STATUSES`) | 4 | 2 | not run | 0 |
| 5 | Manage Tax Jurisdictions (`ZX_MANAGE_TAX_JURISDICTIONS`) | tested | 12 | 7 | PASS with a guess (skill bug), re-test PASS | 11 (6 + 5) |
| 6 | Manage Tax Condition Sets (`ZX_MANAGE_TAX_CONDITION_SETS`) | tested | 9 | 5 | PASS | 6 |
| 7 | Manage Tax Rules (`ZX_MANAGE_TAX_RULES`) | **failed** (3 attempts, the limit) | 8 | 8 | not run | 0 |
| | **Total** | 2 of 4 tested | **33** | **22** | 2 of 2 run | **17** |

- The `STATUS.md` cards hold the same numbers.
- **No `retest_after_wording_fix` is pending.** Only the jurisdictions skill changed after its fresh test, and it was re-tested (PASS, no deviation). Notes from the last test of each task are in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested.
- `rebuild_index.py`: **No problems.** 29 cards applied. Common Features went from 21 to **23 tested** of 148 (failed cards: Tax Zone Types, Tax Statuses, Tax Rates, Tax Rules). All 19 modules: 25 tested of 935.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test | Fresh test | Re-test |
|---|---|---|---|
| 5 jurisdictions (test tax `GAPFILL_AB_P1_TX1`, not live) | `GAPFILL_AB_P2_JR1` (NY, precedence 300) | `GAPFILL_AB_P2_JR2F` (CA, 310) | `GAPFILL_AB_P2_JR3R` (GA, 320) |
| 6 condition sets (factor set `GAPFILL_AB_FS1`) | `GAPFILL_AB_P2_CS1` (STATE = NY) | `GAPFILL_AB_P2_CS2F` (STATE = CA) | - |
| 7 rules | none (`GAPFILL_AB_P2_RL1` rejected 3 times, not created) | - | - |
| 4 rates | none (no import) | - | - |

No rule uses the condition sets, and the jurisdictions sit on a tax that is not live, so no transaction can change. Batch 2 and Part 1 records were not changed (taxes, regime and subscription files unchanged in every compare).

Evidence: `evidence/batch-03/<TASK_CODE>/`: `01_missing` to `05_fresh_test` for condition sets and jurisdictions, `01` to `04` for rates and rules (their 04 shows the block / the rejections). Rendered text with no tokens, server addresses or user names.

## Problems and findings
1. **Rates blocked, as the plan expected.** A rate needs a status; no status exists on any `GAPFILL_` tax (the rates export shows 4 statuses and 5 percentage rates, none ours). No import. `manage-tax-rates/SKILL.md` keeps what is known.
2. **Rules: rejected 3 times** with `ZX_RECRATE_DATE_INVALID` ("Enter a date range that's within the date range of the parent tax of {TAX_START_DATE} to {TAX_END_DATE}", placeholders not filled, so Oracle did not find the tax). This is a different message from the statuses one, so I tried: (1) owner GCO from the tax start date (ProcessId 100004741398794), (2) one month later (100004741399835), (3) owned by the test BU `ZZ_TEST_BU_1932`, which already subscribes the test regime (100004742403274). A rules export after attempt 3 shows nothing created. Most likely the same root cause as statuses (the tax is not live on a GCO-subscribed regime). Fixing that changes real tax setup, so it is left for your decision; see `manage-tax-rules/SKILL.md` "How to finish it".
3. **Jurisdictions did accept the test tax.** Live test took 3 attempts, all about the geography: a full state name (`New York`) and then `GeographyCode=NY` both ended "0 rows processed" with `Geography ... has to be imported prior to import of this Tax Jurisdiction BO`; copying the style of existing jurisdictions (`GeographyName=NY`, elements `United States` / `NY`, no code) worked.
4. **The jurisdictions export lists no jurisdictions** (0 rows, although 5 existed). They are in the **taxes** package (`ORA_ZX_TRAN_TAX_JURISDICTION.csv`), so the skill reads back with a taxes export compare.
5. **Jurisdictions skill bug, found by the fresh tester:** the skill hard-coded `PrecedenceLevel=300`; a second jurisdiction on the same tax is refused ("This precedence level already exists..."). The tester guessed 310. Fixed (placeholder PREC: 300 if the tax has none, else highest + 10) and re-tested (PASS, no deviation).
6. **Condition sets: the plan's "non-geography factor" was not possible**: `GAPFILL_AB_FS1` has only a GEOGRAPHY / BILL_FROM / STATE line. The state is written by name (`NY`), and Oracle fills the geography ID itself, so no ID is taken from an export (rule 16 kept).
7. **My own path slip:** two exports were started with a `/e/...` path (`$PWD` in Git Bash), and FSCR wrote them to `E:\e\GoSaaS\...`. I moved the files back; the **empty folder tree `E:\e\GoSaaS\Configuration Automation v2.1\gaps-filled\_work_b3p2\{cs,tax}` is left**, because the safety check blocked removing `E:\e`. Please delete `E:\e` by hand (it holds no files). Both new skills now warn against `$PWD`.
8. Exports were stable: 14 exports by me, none dropped; the condition-set fresh tester had 1 drop and retried as the skill says. Exports took 44 to 121 s, imports 40 to 99 s.

## What Part 3 can reuse
- Nothing from Part 2 is needed (Part 3's tasks are stand-alone). Helpers: batch 1 generic helpers (`manage-docseq-categories/scripts`), `manage-tax-regimes/scripts/template_row.py`.
- Lesson: in Git Bash never pass `$PWD` (it is `/e/...`) to FSCR; write `E:/...`.
- Lesson: when an export package shows 0 rows of a thing that exists, look for it in a related package (jurisdictions are in the taxes package).

## Index and cleanup
- `python rebuild_index.py` in `gaps-filled`: 29 cards applied, **No problems**.
- The work folder `gaps-filled/_work_b3p2` (exports, payloads, import logs, fresh-test folders) is deleted after this report.
- All 3 sub-agents (2 fresh tests, 1 re-test) have finished. The sign-in listener exited after sign-in; no Python process or server started by this session is left, and nothing listens on port 8765.
- Nothing is committed or pushed. Part 3's tasks were not touched.
