# CHANGELOG: manage-tax-exceptions (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-24 (batch 4 part 3, AB with Claude)
- Read-only export: see `evidence/batch-04/ZX_MANAGE_TAX_EXCEPTIONS/02_found.png`.
- Live test: `GAPFILL_AB_P3_EXC1`: 1 import (ProcessId 100004741425074), TaxException 1 row, 0 failed. Export compare (0 -> 1) PASS.
- Fresh test (task name + SKILL.md only): PASS, `GAPFILL_AB_P3_EXC2F`, ProcessId 100004742415631, about 5 minutes, 1 import. Checked again in the main session: the added row matches.
- Tester notes, **not applied** (tested wording stays on disk): no rule to choose among several test rates and codes; no live check that the tax is not live; the file is no longer empty; Step 1 exports can run in parallel; the rate listing does not print the owner column.

## Test records created
- GAPFILL_AB_P3_EXC1 (live, on GAPFILL_AB_TF_RT1 / GAPFILL_AB_P2_PCC1); GAPFILL_AB_P3_EXC2F (fresh test, on GAPFILL_AB_TF_RT2F / GAPFILL_AB_P2_PCC2F); 10 % discounts on not live test taxes.
