# CHANGELOG: manage-tax-formulas (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 3 part 1, AB with Claude)
- Read-only export: 19 files, 0 formulas (81 s).
- Live test: `GAPFILL_AB_P1_FM1` (taxable basis, line amount) on test tax `GAPFILL_AB_P1_TX1`; 1 import (ProcessId 100004741397811, 29 s): TaxFormula 1 row, 0 failed. Export after + compare: added 1 + 1, removed 0, changed 0: PASS.
- Fresh test (task name + SKILL.md only): PASS, `GAPFILL_AB_P1_FM2F`, ProcessId 100004741400006, about 5 minutes, no deviation.
- Tester notes, **not applied** (so the tested wording stays on disk): say that "Total Objects Processed: 9" for one row is normal; say that "StatusCode: (unknown)" from the FSCR scripts is harmless; add a file-count command after the unzip; the worked example's "0 formulas" will not match a repeat run.

## Test records created
- `GAPFILL_AB_P1_FM1`, `GAPFILL_AB_P1_FM2F` (regime `GAPFILL_AB_TR1`, tax `GAPFILL_AB_P1_TX1`).
