# CHANGELOG: manage-tax-jurisdictions (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-24 (batch 3 part 2, AB with Claude)
- Read-only export of `ZX_MANAGE_TAX_JURISDICTIONS`: 5 files, **0 jurisdictions**, although the taxes package (`ORA_ZX_TRAN_TAX_JURISDICTION.csv`) shows 5 existing ones. So the read-back uses the taxes export.
- Live test on test tax `GAPFILL_AB_P1_TX1` (zone type STATE, not live), rows written in full:
  - Attempt 1 (ProcessId 100004741401696): `GeographyName=New York`, `GeographyType=STATE`: "Completed with warnings", 0 rows, `Geography 'null' has to be imported prior to import of this Tax Jurisdiction BO`. Nothing created.
  - Attempt 2 (ProcessId 100004741398527): + `GeographyCode=NY`: same, `Geography 'NY' ...`. Nothing created.
  - Attempt 3 (ProcessId 100004741403415): style copied from the existing jurisdictions (no GeographyCode, `GeographyName=NY`, `GeographyElement1=United States`, `GeographyElement2=NY`, `PrecedenceLevel=300`): 1 row, 0 failed, 61 s.
- Taxes export after + compare: added `GAPFILL_AB_P2_JR1` + translation, removed 0, changed 0 (tax, regime, subscriptions unchanged): PASS. The test tax was **not** refused here (unlike statuses and rules).
- Fresh test 1 (01:01:49 to 01:08:09): `GAPFILL_AB_P2_JR2F`, state `CA`. Import 1 (ProcessId 100004742404179) refused: `This precedence level already exists. Create unique precedence levels for tax jurisdictions that apply to the same tax.` (the skill hard-coded 300, already used by JR1). The tester retried with 310 (own guess; ProcessId 100004741401859): 1 row, 0 failed; compare PASS. Counted as a skill bug.
- Wording fix: new placeholder PREC, Step 3.4 (precedence unique per tax: 300 if the tax has none, else highest + 10, with the Oracle message); Step 3.3 says to take a state another jurisdiction already uses; placeholder GEO renamed STATE.
- Re-test (01:09:00 to 01:13:59): `GAPFILL_AB_P2_JR3R`, state `GA`, precedence 320, 1 import (ProcessId 100004742403980): 1 row, 0 failed; taxes compare PASS (7 to 8). Verdict PASS, no deviation.
- Re-test notes, **not applied** (tested wording stays on disk): no tie-break when several states qualify; "write it in your log" names no file; the import counts 3 objects but shows one detail line; worked-example counts will differ.

## Test records created
- `GAPFILL_AB_P2_JR1` (NY, 300), `GAPFILL_AB_P2_JR2F` (CA, 310), `GAPFILL_AB_P2_JR3R` (GA, 320), all on test tax `GAPFILL_AB_P1_TX1` of regime `GAPFILL_AB_TR1` (not live).
