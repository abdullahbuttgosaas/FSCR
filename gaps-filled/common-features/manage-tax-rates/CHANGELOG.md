# CHANGELOG: manage-tax-rates (GoSaaS gap fill, not official FSCR)

## 0.0.1, 2026-11-24 (batch 3 part 2, AB with Claude): FAILED (blocked)
- Read-only export `ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES` (109 s, 32 files): 4 tax statuses and 5 percentage rates, none on a `GAPFILL_` tax.
- No import: a rate needs a tax status, and `ZX_MANAGE_TAX_STATUSES` failed in batch 3 part 1 (status refused on every test tax). The batch 3 plan says to skip the task and mark it failed "blocked by ZX_MANAGE_TAX_STATUSES".
- SKILL.md records what is known (files, columns) and how to finish once a test status exists. No fresh test (nothing works yet).

## Test records created
None.

## 0.2.0, 2026-11-24 (batch taxfix, AB with Claude): TESTED
- Real cause of the block: the status could not be made because the test regime had no global configuration owner option row (see manage-tax-statuses and manage-tax-regimes Step 7). With that row and status `GAPFILL_AB_TF_ST1`, the rate path opened.
- Live test: `GAPFILL_AB_TF_RT1`, 5 %, from 2026/01/01, GCO, no jurisdiction, not default, no account row; template = the GCO percentage rate with no jurisdiction; parent status rows re-sent unchanged. 1 import (ProcessId 100004741411939, 61 s): rate 1 row and status 1 row, 0 failed. Export compare PASS (rates 5 to 6, status unchanged).
- SKILL.md rewritten as a full recipe (template choice, parent copy with SPREFIX, read back).
- Fresh test (15:12-15:18): PASS. `GAPFILL_AB_TF_RT2F`, 7 %, on status `GAPFILL_AB_TF_ST2F` of tax `GAPFILL_AB_TF_TX2` (regime `GAPFILL_AB_TR2F`, GCO row only). ProcessId 100004741413676, compare PASS. Notes NOT applied (keep tested wording): the builder lists 31 CSVs (the XML is not counted); say that the template match needs the EffectiveFrom too when a code repeats.

## Test records created (batch taxfix)
`GAPFILL_AB_TF_RT1` (live), `GAPFILL_AB_TF_RT2F` (fresh test). Not live (their taxes are not live).
