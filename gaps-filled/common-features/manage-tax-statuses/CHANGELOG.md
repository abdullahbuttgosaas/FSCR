# CHANGELOG: manage-tax-statuses (GoSaaS gap fill, not official FSCR)

## 0.0.1, 2026-11-23 (batch 3 part 1, AB with Claude): FAILED
- Read-only exports: 33 files, 4 existing statuses (all on live or simulation taxes of subscribed regimes).
- Import attempt 1 (`GAPFILL_AB_P1_ST1` on test tax `GAPFILL_AB_P1_TX1`, ProcessId 100004741392995): `ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute`. Nothing created.
- A tax formula on the same tax imported fine (batch 3 part 1), so the tax exists; the cause is most likely that the tax is not live/simulated or the regime has no subscription. Fixing that changes real setup: stopped and left for AB's decision.
- Attempt 2, approved by AB ("Use a simulation tax"): a new tax `GAPFILL_AB_P1_TX4S` with `LiveForProcessingFlag=S` imported fine (ProcessId 100004741400397; after-export compare PASS). Status `GAPFILL_AB_P1_ST2` on it (ProcessId 100004741402182): the same `ZX_INVALID_VALUE ... Tax attribute`. Nothing created. "Not live" is ruled out; the remaining cause is most likely the regime with no subscription. Stopped: a subscription was not approved.
- Attempt 3, approved by AB ("Approve subscription"): the test regime `GAPFILL_AB_TR1` was subscribed by the existing test business unit `ZZ_TEST_BU_1932` (usage + `GCO_ONLY` subscription + detail; first try rejected `FirstPtyOrgId` required, second try with `FirstPtyEnterpriseId=1` worked, ProcessId 100004741401398; after-export shows exactly these 3 rows added). Status `GAPFILL_AB_P1_ST3` on `GAPFILL_AB_P1_TX1` (ProcessId 100004741398375): the same `ZX_INVALID_VALUE ... Tax attribute`. Nothing created. Stopped at the 3-attempt limit; the remaining idea (a GCO subscription row) needs internal IDs.
- No fresh test: a fresh tester cannot pass a recipe that does not work.

## Test records created
None. `GAPFILL_AB_P1_ST1`, `GAPFILL_AB_P1_ST2` and `GAPFILL_AB_P1_ST3` were tried once each and do not exist. Made for the attempts: simulation tax `GAPFILL_AB_P1_TX4S`, and a subscription of `GAPFILL_AB_TR1` by business unit `ZZ_TEST_BU_1932` (see `manage-tax-regimes/CHANGELOG.md`). The simulation tax made for attempt 2, `GAPFILL_AB_P1_TX4S`, exists (listed under `manage-taxes`).

## 0.2.0, 2026-11-24 (batch taxfix, AB with Claude): TESTED
- Diagnosis (read-only): old process log of try 3 read again by ProcessId: row `GAPFILL_AB_TR1, GAPFILL_AB_P1_TX1, GAPFILL_AB_P1_ST3, -99`, `ZX_INVALID_VALUE ... Tax attribute`. Field-by-field compare of a working GCO tax/status/regime with ours: the tax rows differ only in option flags; the regime lacks the `ORA_ZX_BU_GCO_TAX_SUB.csv` row that every regime with tax content has.
- Prerequisite done by CSV: manage-tax-regimes Step 7 on `GAPFILL_AB_TR1` (ProcessId 100004742409055), compare PASS.
- Live test: `GAPFILL_AB_TF_ST1` on `GAPFILL_AB_P1_TX1` (not live), template = the GCO status, 1 import (ProcessId 100004741413261, 61 s), compare PASS (4 to 5).
- SKILL.md rewritten as a full recipe with a prerequisite check (taxes export: the tax and the regime's GCO row).
- Fresh test 1 (15:05-15:12): PASS. `GAPFILL_AB_TF_ST2F` on new tax `GAPFILL_AB_TF_TX2` of `GAPFILL_AB_TR2F`, a regime with the GCO row and **no** business-unit subscription (so the GCO row alone is enough). ProcessId 100004741414186. Wording fixed after it: file count (32 or 33), where the template's tax comes from, the totals line and up to 90 s.
- Re-test (15:18-15:24): PASS. `GAPFILL_AB_TF_ST3R` on `GAPFILL_AB_P1_TX2F` (ProcessId 100004741415225), compare PASS (6 to 7). No wording change after it.

## Test records created (batch taxfix)
Statuses `GAPFILL_AB_TF_ST1` (live), `GAPFILL_AB_TF_ST2F` (fresh test), `GAPFILL_AB_TF_ST3R` (re-test); tax `GAPFILL_AB_TF_TX2` on `GAPFILL_AB_TR2F` (made by the main session for the fresh tests, ProcessId 100004741413437, not live).
