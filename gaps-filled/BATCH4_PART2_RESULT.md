# Batch 4, part 2: tax fiscal classifications (3 tasks) and resource note type mapping (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-24. Tested on one test environment only (release 11.13.26.10.0).
- The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`. No FSCR file was edited.
- Plan and rules: `BATCH4_PLAN.md` (RULES 1 to 26). Reused Part 1's driver pattern and log summary, the batch 1 to 3 helpers (`build_fsm_package.py`, `compare_fsm_exports.py`, `copy_parent_rows.py`, `text_png.py`).
- Work folder `E:\GoSaaS\gw\b4p2` (outside the repo; exports there hold user names).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 17:38 | 17:40 | 2 | Read plan, Part 1 result, rules (plan time, not in any task) |
| 17:39:50 | 17:39:53 | 0 | Sign-in on port 8765 (browser was still signed in; not counted in any task) |
| 17:40 | 17:53 | 13 | Task 5 live: export, helper, 3 imports, after-export, compare |
| 17:54 | 18:01 | 7 | Task 6 live (helper fix, 1 import) |
| 18:01 | 18:04 | 3 | Task 7 live (builder key fix, 1 import) |
| 18:04 | 18:10 | 6 | Task 8 live (1 import) |
| 18:10 | 18:14 | 4 | Skills 5 and 8, cards 6 and 7 |
| 18:10 | 18:37 | 27 | Fresh tests: 5 and 8 in parallel (different scopes), then 6, then 7 (same package and scope, rule 26); my re-check of each record |
| 18:14 | 18:40 | 26 | Evidence, STATUS, CHANGELOG, this report, index, cleanup (while the testers ran) |

**Waiting for your approvals:** 0 minutes (the brief was the approval). No second sign-in.

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 5 | Manage Transaction Fiscal Classifications (`ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS`) | tested (try 3) | 21 | 9 | PASS | 7 |
| 6 | Manage Transaction-Based Fiscal Classifications (`ORA_ZX_MANAGE_TRANSACTION_BASED_FISCAL_CLASSIFICATIONS`) | tested | 11 | 6 | PASS | 7 |
| 7 | Manage Product-Based Fiscal Classifications (`ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS`) | tested | 6 | 5 | PASS | 7 |
| 8 | Manage Resource Note Type Mapping (`HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING`) | tested | 11 | 2 | PASS | 3 |
| | **Total** | **4 of 4 tested** | **49** | **22** | 4 of 4 | **24** |

- **No `retest_after_wording_fix` is pending.** No SKILL.md changed after its fresh test. The testers' notes are in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested.
- `rebuild_index.py`: see the end of this report.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (ProcessId) | Fresh test (ProcessId) |
|---|---|---|
| 5 transaction business category code | try 1 nothing created (100004742413180); `GAPFILL_AB_P2_TBC1` code + translation only, no denormalized row (100004741417628); `GAPFILL_AB_P2_TBC2` all 4 rows (100004741418933) | `GAPFILL_AB_P2_TBC3F` (100004741422201) |
| 6 user-defined code (type USER_DEFINED) | `GAPFILL_AB_P2_UDC1` (100004741419343) | `GAPFILL_AB_P2_UDC2F` (100004741424199) |
| 7 product category code (type PRODUCT_CATEGORY) | `GAPFILL_AB_P2_PCC1` (100004742413617) | `GAPFILL_AB_P2_PCC2F` (100004741424344) |
| 8 note type mapping | `TESTOBJECT1_C` -> `GENERAL` (100004741419676) | `DSOAKTESTCUSTOMOBJECT_C` -> `GENERAL` (100004741415996) |

Nothing uses them: no tax rule or exception points to the new codes; the mappings only add the seeded note type GENERAL to two test objects. The TBC codes sit under the seeded parent PURCHASE_PREPAYMENTTRANSACTION.

Evidence: `evidence/batch-04/<TASK_CODE>/01_missing` to `05_fresh_test` (.png) for all 4. Rendered text, checked: no tokens, server addresses, environment names or user names.

## Problems and findings
1. **Parent type row needed (task 5, try 1):** a package with only the code rows processed 0 objects: `Parent row is missing in file ORA_ZX_TRANSACTION.csv`. FSM packages are hierarchical; a child row is read only when its parent row is in the same ZIP.
2. **Seeded parent sent unchanged (departs from rule 17, "own parents only"):** the type rows (`TRX_BUSINESS_CATEGORY`, `USER_DEFINED`, `PRODUCT_CATEGORY`, and the note type object rows) are seeded and cannot be ours. They are copied byte for byte with `copy_parent_rows.py`; every after-export compare shows the parent row **changed 0**. Keep this as a rule for child-only tasks: a seeded parent may go in only unchanged, and the compare must prove it.
3. **Denormalized rows needed (task 5, try 2):** code + translation alone created the code but no `ORA_ZX_TRAN_DENORM_CLASS_CODE` row, which the screens and rules read. Try 3 sent all 4 rows (code, translation, denorm, denorm translation). New helper `manage-transaction-fiscal-classifications/scripts/fiscal_code_rows.py` writes these 4 rows from a template code (families trx, user, product).
4. **The import log counts only the top object** (for example `UserDefinedFiscalClassificationType 1 row`). The after-export compare is the proof that each child row went in.
5. **Builder keys for level-1 codes (task 7):** a key with the parent column stops the builder (empty key value). Use keys without it for level-1 codes.
6. **No name on a note type mapping (task 8):** the mapping row has only object, type and lookup codes, so it cannot carry the GAPFILL prefix. The test rule is "map only to an object whose code or name contains TEST and has no mapping yet". The plan's prerequisite (`HZ_MANAGE_RESOURCE_NOTE_TYPE`) was not needed: the seeded note type GENERAL was used. Oracle filled `SourceObjectCode` itself.
7. **Tester notes, not applied (each needs a re-test if applied):** template choice now picks earlier GAPFILL codes (6) or is hidden by `head -40` (5); worked-example counts grow with each run; object pick rule for task 8 (case, soak-test objects); FSCR export file names hold the environment name (never copy them into evidence); the note type parent row carries audit user names (hide them when printing). Task 7 tester: give a command for the '0 new rows' check; Step 6 should repeat `--rows-out`.
8. **Part 1 follow-up still open:** the `manage-profile-options` Step 5 log one-liner prints a `Submitted By` user name (see `BATCH4_PART1_RESULT.md` finding 6). The Part 2 skills use the filtered one-liner.

## What Part 3 can reuse
- **`fiscal_code_rows.py`** and the 3 fiscal classification skills, if Part 3 needs a fiscal classification code (for example a tax rule or exception test).
- **Child-only tasks:** send the seeded parent row unchanged with `copy_parent_rows.py`, and prove "changed 0" in the compare (finding 2).
- **Run fresh tests one at a time when tasks share a package and scope;** in parallel when scopes differ (5 and 8 ran together without trouble).
- **Timing:** fiscal classification export about 2 to 2.5 min, import about 1.5 min; note type mapping export about 40 s. A fiscal classification fresh test takes about 7 minutes.
- **Token life:** one sign-in (17:39) covered all live tests and all 4 fresh tests.

## Index and cleanup
- `python rebuild_index.py` in `gaps-filled`: 40 cards applied, **No problems**. Common Features: 38 tested of 148. All 19 modules: 40 tested of 935, 0 failed.
- All 4 fresh-test sub-agents have finished. The sign-in listener exited right after sign-in (17:39:53). No Python process or server started by this session is left, and nothing listens on port 8765.
- The work folder `E:\GoSaaS\gw\b4p2` stays outside the repo (exports, payloads, logs, fresh-test folders); it is not in git.
- Nothing is committed or pushed.
