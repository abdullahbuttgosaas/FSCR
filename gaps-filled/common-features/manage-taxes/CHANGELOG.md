# CHANGELOG: manage-taxes (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 3 part 1, AB with Claude)
- Read-only export: 23 files, 9 taxes, 15 regimes (93 s).
- Live test: `GAPFILL_AB_P1_TX1` under test regime `GAPFILL_AB_TR1`, copied from a GCO tax that is not live; parent regime and its translation copied unchanged. 1 import (ProcessId 100004741395551, 78 s): TransactionTax 1 row, TaxRegime 1 row, 0 failed. Export after + compare: added 1 + 1, regime and subscription files unchanged: PASS.
- Fresh test 1: `GAPFILL_AB_P1_TX2F`, read-back PASS, **but** the tester had to change `--prefix` for `copy_parent_rows.py` (the skill passed the tax's PREFIX `GAPFILL_AB_P1_`, the regime starts with `GAPFILL_AB_`, so the script stopped). Counted as a skill bug.
- Wording fix: new placeholder RPREFIX (the regime's own test prefix) for the two parent copies; the regime list now prints start dates; TEMPLATE = the first listed GCO tax that is not live.
- Re-test: `GAPFILL_AB_P1_TX3R`, PASS, no deviation (ProcessId 100004741401025, about 4 minutes).
- Re-test notes, **not applied** (tested wording stays on disk): RPREFIX could be read as `GAPFILL_` or `GAPFILL_AB_` (both work); the translation row holds 6 columns, not all listed ones (empty ones are skipped); warn that the new tax inherits the template's country and geography; say that "StatusCode: (unknown)" is harmless; the import can take 40 to 80 s.
- Found while testing children: a tax formula on the new tax imports fine; a tax status is rejected (see `manage-tax-statuses`).

- 23:28, approved by AB for the statuses retry: `GAPFILL_AB_P1_TX4S` with `LiveForProcessingFlag=S` (simulation), same recipe; 1 import (ProcessId 100004741400397): 1 row, 0 failed; after-export compare PASS. Oracle accepted `S` without a default status or rate. SKILL.md not changed (it still makes taxes not live; its limit 5 still says "live or simulation", which attempt 2 narrowed to "subscribed regime": left as is to keep the tested wording).

## Test records created
- `GAPFILL_AB_P1_TX1`, `GAPFILL_AB_P1_TX2F`, `GAPFILL_AB_P1_TX3R` (regime `GAPFILL_AB_TR1`, not live).
- `GAPFILL_AB_P1_TX4S` (regime `GAPFILL_AB_TR1`, simulation `S`; the regime has no subscription, so no real transaction can use it).
