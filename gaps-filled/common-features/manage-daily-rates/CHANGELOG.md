# CHANGELOG: manage-daily-rates (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 06, AB with Claude)
- Read-only export: Read-only export GL_MANAGE_DAILY_RATES: 3 files (GL_DAILY_CONVERSION_TYPE 16 types, ORA_GL_CONVERSION_RATE_RULE 10 rows) + metadata. No rate values in the package.
- Live (AB): try 1 GAPFILL_AB_B6_DRT1 ProcessId 100004743401986: type created, 2 rules dropped (compare FAIL on rules). Try 2 GAPFILL_AB_B6_DRT2 ProcessId 100004742421461: compare types +1, rules +2, removed 0, changed 0: PASS.
- Fresh test PASS: GAPFILL_AB_B6_DRT3F (pivot USD, rules CAD and EUR), ProcessId 100004743401997, compare PASS. Read back by AB from the tester's after-export: type + 2 rules present.
- Tester notes not applied (suggestions): counts grow with each run; a one-liner to list cross-rate types; 'StatusCode: (unknown)' is normal; currencies 'used as pivot or in a rule row'; repeat --row per contra currency.

## Test records created
- GAPFILL_AB_B6_DRT2 (live; rules EUR, GBP); GAPFILL_AB_B6_DRT3F (fresh test; rules CAD, EUR); GAPFILL_AB_B6_DRT1 created by try 1 but without rules
