# Batch taxfix2: Tax Zone Types (result)

GoSaaS work, not official FSCR. AB with Claude, 2026-11-24, ETIA-TEST only (release 11.13.26.10.0). FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`; no FSCR file edited. Nothing deleted, nothing committed or pushed.

## Result in short
| Task | Before | Now | Real cause |
|---|---|---|---|
| Manage Tax Zone Types (`ZX_MANAGE_TAX_ZONE_TYPES`) | failed (6 tries, `JBO-26041`) | **tested**: fresh test + re-test PASS | our row left **`CreatedBy` and `LastUpdatedBy` empty**. Oracle's own export fills them; with them empty the row validates and then the database insert into `HZ_GEOGRAPHY_TYPES_B` fails |

**Not an Oracle defect and not an access limit**: the batch taxfix conclusion ("needs an Oracle SR") was wrong. No SR is needed.

Index (`python rebuild_index.py`): **No problems**; all 19 modules **32 tested** of 935 (was 31), 0 failed cards left.

## Time log
| Start | Finish | Minutes | What |
|---|---|---:|---|
| 15:36 | 15:39 | 3 | Read CONTEXT, BATCH_TAXFIX_RESULT, zone type skill, evidence |
| 15:39 | 15:41 | 2 | Read-only export (saved sign-in still valid; no sign-in needed) |
| 15:41 | 15:44 | 3 | Step 1 round trip: build, import, after-export |
| 15:44 | 15:48 | 4 | Step 2 compare, try F1, after-export + compare |
| 15:48 | 15:52 | 4 | Helper `zone_type_rows.py`, SKILL.md rewrite (during fresh test) |
| 15:48 | 15:52 | 4 | Fresh test (sub-agent) + my read-back |
| 15:52 | 15:56 | 4 | Wording fixes, re-test (sub-agent) + my read-back |
| 15:56 | 16:02 | 6 | STATUS, CHANGELOG, evidence, this report, index, cleanup |

Card numbers (this batch only, earlier batches in the CHANGELOG): write 24, test 8, wait 14.

## Step 1: round trip (diagnosis written before the try)
- Read-only export `100004742409723`: 2 zone types, `GAPFILL_AB_TF_ZT1` (made on the screen by AB) and `US Zone Type`.
- Package = that export's own files and metadata, only the ZT1 row and its translation row, code `GAPFILL_AB_TF2_ZT2`, name `Gapfill Ab Tf2 Zt2` (screen style), every other value unchanged (who columns as exported). `US Zone Type` left out so nothing existing is updated.
- Import ProcessId **100004741416084** (request 4,483,732): `Completed successfully`, `GeographyType: 1 rows processed, 0 failed`. After-export `100004741416143`: `GAPFILL_AB_TF2_ZT2` exists (TAX, N, HZ_GEO_HIERARCHY, US translation).
- **Proved: the setup CSV import path works for this object.** Step 3 (other routes: REST, HDL/FBDI) was not needed and not tried.

## Step 2: compare and fix
- Same values built with our builder (`build_fsm_package.py`), compared byte by byte with the round-trip package: **only `CreatedBy` and `LastUpdatedBy`** (type row and translation row) differ, filled vs empty; plus the zip member order. Metadata XML and the 7 other files identical. All 6 earlier failed tries had those two columns empty.
- Try F1 (diagnosis written before): builder package (sorted zip order kept) + both columns = the export metadata's `SubmittedBy` (the signed-in user, the one who imports). `GAPFILL_AB_TF2_ZT3`, ProcessId **100004742412123**: `Completed successfully`, 1 processed 0 failed. After-export `100004741415297`, `compare_fsm_exports`: **RESULT: PASS** (1 zone type + 1 translation row added, nothing else changed).
- So zip order does not matter; the who columns are the cause. Mechanism (GUESS): empty values reach the insert as null and the table refuses them.
- 2 import tries used in this step (RT1 counted in step 1): F1 only.

## Step 4: skill and tests
- `common-features/manage-tax-zone-types/SKILL.md` v0.1.0 rewritten (generic, no environment names, placeholders, 6 steps, depends_on = FSCR auth/export/import + generic helpers; **no Oracle prerequisite**).
- New helper `common-features/manage-tax-zone-types/scripts/zone_type_rows.py`: writes the zone type and translation rows, fills the who columns from `SubmittedBy` without printing it, stops if the code exists. Optional `--limit-like` (country limit) **not tested**.

| Test | Who | Record | Import ProcessId | Result |
|---|---|---|---|---|
| fixed row | me | `GAPFILL_AB_TF2_ZT3` | 100004742412123 | created, compare PASS |
| fresh test | fresh sub-agent, task name + SKILL.md only | `GAPFILL_AB_TF2_ZT4F` | 100004742411691 | PASS, read back by me |
| re-test after wording fix | fresh sub-agent | `GAPFILL_AB_TF2_ZT5R` | 100004742412240 | PASS, read back by me |

Wording fixed after the fresh test: the log read printed a `Submitted By` user line (now filtered), re-run export folder, what a good Step 2 looks like, name style for `ZT4F`. Re-test notes are in the CHANGELOG and were not applied, so no re-test is pending.

**Records created (none edited, none deleted):** `GAPFILL_AB_TF2_ZT2`, `GAPFILL_AB_TF2_ZT3`, `GAPFILL_AB_TF2_ZT4F`, `GAPFILL_AB_TF2_ZT5R` (zone types, use TAX, no country limit, no zones; no tax uses them).

Evidence: `evidence/batch-taxfix2/ZX_MANAGE_TAX_ZONE_TYPES/` (`01_cause`, `04_test_result`, `05_fresh_test`, .txt and .png). No tokens, server addresses or user names.

## Lesson for other gap skills
Some FSM objects need the who columns (`CreatedBy`, `LastUpdatedBy`) filled, though most accept them empty. If a row validates (`1 rows processed, 0 failed`) and then fails with `JBO-26041` at the insert, first fill the who columns from the export's `SubmittedBy`. A round trip of a screen-made record's own export is the fastest way to split "file problem" from "import problem".

## Cleanup
- 2 fresh-test sub-agents, both finished. No sign-in was started (the saved one was still valid); nothing listens on port 8765; no Python process left. No server or browser was opened.
- Work folder `gaps-filled/_work_taxfix2` (exports with user names, payloads, logs) moved out of the repo to Claude's scratchpad (not deleted, not in git).
- The "Oracle defect / needs an SR" conclusion in `BATCH_TAXFIX_RESULT.md` and `evidence/batch-taxfix/.../06_screen_reference.txt` is superseded by this report (files left as history).
