# Batch 3, part 1: taxes, tax statuses, tax formulas (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-23. Tested on ETIA-TEST only (release 11.13.26.10.0).
- The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`. No FSCR file was edited.
- Plan and rules: `BATCH3_PLAN.md` (RULES 1 to 18). This part reused batch 2's helpers and lessons.

| Start | Finish | Note |
|---|---|---|
| 22:38 | 23:08 | Start session, sign-in, Tax Zone Types check, 16 read-only planning exports, `BATCH3_PLAN.md` |
| 23:02 | about 23:27 | 3 live loads (1 rejected), 3 skills (1 marked failed), 2 fresh tests, 1 wording fix, 1 re-test, evidence, index, this report |
| 23:26 | about 23:38 | Your follow-up "Use a simulation tax": 1 new simulation tax, statuses attempt 2 (rejected again), cards and this report updated |
| 23:44 | about 00:02 | Your follow-up "Approve subscription": second sign-in (23:49:29 to 23:49:32, 3 s, not counted), regime subscribed by a test BU (2 tries), statuses attempt 3 (rejected again), cards and this report updated |

**Sign-in (not counted in any task):** port 8765, 22:43:25 to about 22:44 (the browser session was still signed in, so you had nothing to do). No second sign-in. **Waiting for your approvals:** 0 minutes (the brief was the approval).

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min (test + re-test) |
|---|---|---|---:|---:|---|---:|
| 1 | Manage Taxes (`ZX_MANAGE_TAXES`) | tested | 8 | 5 | PASS with a workaround (skill bug), re-test PASS | 9 (5 + 4) |
| 2 | Manage Tax Statuses (`ZX_MANAGE_TAX_STATUSES`) | **failed** (3 attempts, the limit) | 11 | 21 | not run (nothing works yet) | 0 |
| 3 | Manage Tax Formulas (`ORA_ZX_MANAGE_TAX_FORMULAS`) | tested | 5 | 3 | PASS | 5 |
| | **Total** | 2 of 3 tested | **24** | **29** | 2 of 2 run | **14** |

- Minutes come from the run's clock times; the `STATUS.md` cards hold the same numbers. Taxes and formulas use different packages, so their fresh tests ran in parallel (23:14 to 23:19).
- **No `retest_after_wording_fix` is pending.** Only the taxes skill changed after its fresh test, and it was re-tested (PASS, no deviation). Notes from the last test of each task are written in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested.
- `rebuild_index.py`: **No problems.** 25 cards. Common Features went from 19 to **21 tested** of 148 (2 failed: Tax Zone Types, Tax Statuses).

## Tax Zone Types (batch 2 leftover): settled as failed, "cannot do by CSV (as tested)"
- The 3 failed import requests (ESS 4,481,501, 4,481,510, 4,481,523) all show `SUCCEEDED` in ESS. Their ESS logs download as **empty** ZIPs (`erpintegrations` `ESSJobExecutionDetailsRF`, file types ALL, LOG, OUT), and the setup-import process is **not found** under those numbers (HTTP 404; a scan of 4,481,480 to 4,481,540 found nothing).
- Reason, found in this part: the FSM import `ProcessId` is a **different number** from the ESS request ID (for example the status import here was ProcessId 100004741392995 but ESS request 4,481,888). Batch 2 did not keep its ProcessIds, so the full process log of the 3 zone-type imports cannot be opened by REST any more.
- So **no detailed ORA- cause could be read**, and the one extra import you approved (only for an error that shows our file is wrong) was **not made**.
- A new read-only export (22:50) still shows exactly 1 zone type (`US Zone Type`, mixed case with spaces, CreatedBy and LastUpdatedBy filled). Nothing from batch 2 was created.
- `manage-tax-zone-types/STATUS.md` stays `failed`; its notes give the cause and say "cannot do by CSV (as tested)". To go further a person must read the request log in Scheduled Processes on the screen, or create one zone type on the screen and export it.
- New rule 18 in `BATCH3_PLAN.md`: keep every import's ProcessId.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (main session) | Fresh test 1 | Re-test |
|---|---|---|---|
| 1 taxes (not live, regime `GAPFILL_AB_TR1`) | `GAPFILL_AB_P1_TX1`; `GAPFILL_AB_P1_TX4S` (simulation `S`, for statuses attempt 2) | `GAPFILL_AB_P1_TX2F` | `GAPFILL_AB_P1_TX3R` |
| 2 statuses | none (`GAPFILL_AB_P1_ST1`, `ST2`, `ST3` rejected, not created); subscription of `GAPFILL_AB_TR1` by test BU `ZZ_TEST_BU_1932` (for attempt 3) | - | - |
| 3 formulas (taxable basis, on TX1) | `GAPFILL_AB_P1_FM1` | `GAPFILL_AB_P1_FM2F` | - |

Batch 2's `GAPFILL_AB_TR1` regime row was re-sent **unchanged** as the parent in the 3 tax imports (the after-export shows it unchanged). No status, rate, rule or tax default was created. **One subscription was created with your approval:** test BU `ZZ_TEST_BU_1932` now subscribes to `GAPFILL_AB_TR1` (`GCO_ONLY`, from 2026/01/01). No tax of that regime is live (one is in simulation), so no transaction of that BU can change. It was not deleted (no-delete rule).

Evidence: `evidence/batch-03/<TASK_CODE>/`, `01_missing` to `05_fresh_test` for taxes and formulas, `01` to `04` for statuses (its 04 shows the rejection). Rendered text with no tokens, server addresses or user names.

## Problems and findings
1. **Tax statuses need a "real" tax.** The status import was rejected: `ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute` (row `GAPFILL_AB_TR1, GAPFILL_AB_P1_TX1, GAPFILL_AB_P1_ST1, -99`). A formula on the same tax imported fine 2 minutes later, so the tax exists. In the export, every tax that has a status is live (`Y`) or in simulation (`S`) and its regime is subscribed. Ours is neither, on purpose. **Follow-up (your choice "Use a simulation tax"):** a new tax `GAPFILL_AB_P1_TX4S` with `LiveForProcessingFlag=S` imported fine (read back PASS), but a status on it was rejected with the **same** error. So "not live" is ruled out; the likely cause is the regime having **no subscription**. **Second follow-up (your choice "Approve subscription"):** I subscribed the regime for the existing test business unit `ZZ_TEST_BU_1932` (it had no regime before). The first try needed the BU's internal id (`FirstPtyOrgId`); the second, with `FirstPtyEnterpriseId=1` copied from every existing usage row, worked, and the after-export shows exactly 3 rows added. The status on `GAPFILL_AB_P1_TX1` was **still** rejected with the same error. That was attempt 3, the limit, so Tax Statuses stays `failed`. The one difference left is the global configuration owner subscription row (`ORA_ZX_BU_GCO_TAX_SUB.csv`), which can only be built with internal IDs (`-99`, `SubscriptionOptionId`); a person can add it on the screen and retry once. This also **blocks Part 2's Tax Rates** (a rate needs a status); see the update note in `BATCH3_PLAN.md`.
2. **Taxes skill bug, found by the fresh tester:** the skill passed the tax's prefix `GAPFILL_AB_P1_` to `copy_parent_rows.py`, but the regime is `GAPFILL_AB_TR1`, so the script stopped. The tester worked around it; I added a separate placeholder `RPREFIX` and re-tested (PASS, no deviation). Lesson for Parts 2 and 3: with the new `P<n>` names, **a child record's prefix (`GAPFILL_AB_P2_`) differs from its parent's** (`GAPFILL_AB_` or `GAPFILL_AB_P1_`); always give the parent's own prefix to `copy_parent_rows.py`.
3. **No REST resource** for taxes, statuses or formulas (`taxes`, `taxesLOV`, `transactionTaxesLOV`, `taxStatusesLOV`, `taxFormulasLOV`: HTTP 404). `taxRatesLOV` answers (useful in Part 2). The after-export compare is the proof.
4. **FSM ProcessId is not the ESS request ID** (see Tax Zone Types). Every new skill says to write it down.
5. **Exports were stable this time:** 19 exports, 1 needed a second try (rates). Tax exports took 46 to 227 s, imports 29 to 82 s.
6. **Formulas:** the environment had no formula to copy, so the rows are written out in full (`TAXABLE_BASIS`, `LINE_AMOUNT`, all discount/charge flags `N`, owner `GCO`). Oracle filled the owner id `-99` itself.
7. Small run issue: my first evidence renderer printed whole process-log lines (literal `\r\n`); fixed by hand. New generic helper `common-features/manage-docseq-categories/scripts/text_png.py` (needs Pillow, run without `-I`).

## What Parts 2 and 3 can reuse
- **Test records:** regime `GAPFILL_AB_TR1` (batch 2), taxes `GAPFILL_AB_P1_TX1` / `TX2F` / `TX3R`, factor set `GAPFILL_AB_FS1` (batch 2). Use `GAPFILL_AB_P1_TX1` as the tax for jurisdictions and rules.
- **Skills as patterns:** `manage-taxes` (template row + parent rows), `manage-tax-formulas` (rows written in full when nothing can be copied).
- **Helpers:** batch 1 generic helpers (`manage-docseq-categories/scripts`, now with `text_png.py`), `manage-tax-regimes/scripts/template_row.py`, `manage-profile-options/scripts/copy_parent_rows.py` (give the **parent's** prefix).
- **Planning exports already checked** (read-only, all worked): rates, jurisdictions, condition sets, rules, party fiscal classifications, shorthand aliases, legal authorities. File lists are in `BATCH3_PLAN.md` section 1. Export again in the part itself (the planning copies were deleted with the work folder).
- **Part 2 warning:** rates are blocked; jurisdictions and rules may hit the same "valid value for the Tax attribute" check. Try once each; on that error, stop the task.
- **Timing:** about 4 to 6 minutes of Oracle waiting per tax task; fresh tests about 4 to 5 minutes each.

## Index and cleanup
- `python rebuild_index.py` in `gaps-filled`: 25 cards applied, **No problems**; all 19 modules: 23 tested of 935.
- The work folder `gaps-filled/_work_b3p1` (exports, payloads, import logs, fresh-test folders) is deleted after this report.
- All 3 sub-agents (2 fresh tests, 1 re-test) have finished. The sign-in listener exited after sign-in; no Python process or server started by this session is left, and nothing listens on port 8765.
- Nothing is committed or pushed. Parts 2 and 3 tasks were not touched (only planning exports).
