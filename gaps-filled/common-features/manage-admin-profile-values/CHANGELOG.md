# CHANGELOG: manage-admin-profile-values (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 2 part 1, filled by AB with Claude)
- Wrote this card over `manage-profile-options`. New helper `../manage-profile-options/scripts/copy_parent_rows.py`.
- Live test on own option `GAPFILL_AB_PO1`: import attempt 1 (value row only) said "0 rows were processed" and created nothing (the package is hierarchical); attempt 2 with the parent option row copied unchanged: 2 rows, 0 failed; REST read-back of siteProfileOptionValues PASS.

## Fresh test 1, 2026-11-23 19:55-19:58: PASS
- Set `GAPFILL_AB_V3F` on `GAPFILL_AB_PO3` (made by the main session for this test); 1 import; REST PASS; no help.
- Notes applied as wording after it: which FSCR copy; the full skill's module-id step is not needed; unzip + inspect commands and how to check SITE EnabledFlag; `StatusCode: (unknown)` and `Total Objects Processed: 1` are normal.

## Re-test after the wording fix, 2026-11-23 20:03-20:05: PASS
- Set `GAPFILL_AB_V2R` on `GAPFILL_AB_PO2F`; 1 import; REST PASS. Main session read all 3 values back afterwards: PASS.
- Note NOT applied: the builder prints "FND_APP_PROFILE_OPTION.csv: 0 new rows" before the parent copy; that is expected.

## Test records created (site values on GAPFILL_ test options only; no code reads them)
| When | Who | Value |
|---|---|---|
| live test | main session | `GAPFILL_AB_V1` on `GAPFILL_AB_PO1` |
| fresh test 1 | sub-agent | `GAPFILL_AB_V3F` on `GAPFILL_AB_PO3` |
| re-test | sub-agent | `GAPFILL_AB_V2R` on `GAPFILL_AB_PO2F` |
