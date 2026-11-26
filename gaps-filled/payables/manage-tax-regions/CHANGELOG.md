# CHANGELOG - Manage Tax Regions

## 2026-11-25 (sitting 1, batch 02)
- Export (ProcessId 100004743425936): AP_INCOME_TAX_REGION.csv 56 rows (US states/territories, short names 2
  characters; methods FEDERAL 43, INDIVIDUAL 12, SUM 1).
- Own test:
  - try 1 FSCRT_AK_GF_TR1, ProcessId 100004743425947: refused, JBO-27040 "Value ... for field RegionShortName
    exceeds the maximum length allowed".
  - A 5-character name without the FSCRT_ start was considered and NOT used: it breaks the pack rule that every
    record starts with FSCRT_ + initials (the action was also blocked).
  - try 2 FSCRT_AK_1 (10 characters, pack rule kept; long name "FSCRT_AK_GF_ test income tax region 1"),
    ProcessId 100004743427182: 1 row processed, 0 failed; compare 56 -> 57, removed/changed 0; REST 1 item.
- REST payablesIncomeTaxRegions: attribute names lower case (`state`, `regionName`); `IncomeTaxRegion` in q
  gives HTTP 400.
- Fresh test F: FSCRT_AK_F, ProcessId 100004743425983, PASS first try (57 -> 58, REST 1 item). No errors.
- Own read-back: REST lists FSCRT_AK_1 and FSCRT_AK_F.
- No retest R needed (no errors, no wording change). A retest name would be FSCRT_AK_R (10 characters).
- Tester suggestions not applied: list export columns in real order; say the before count may include
  earlier test rows; say the console line shows the REST item; the 10-character limit is now confirmed live
  for 10 and refused for 15 (11-14 untested).
