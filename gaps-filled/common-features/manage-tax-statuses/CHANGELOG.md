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
