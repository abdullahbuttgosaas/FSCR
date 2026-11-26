# CHANGELOG - Manage Aging Periods

## 2026-11-25 (sitting 1, batch 01)
- Own test: FSCRT_AK_GF_AGE1 with 3 lines (CURRENT -30..0, PAST 1..60, PAST 61..999999999).
  Import ProcessId 100004744404007: Aging Period Header 1 row processed, 0 failed; Aging Period Line
  "already processed ... listed under the header". Export compare: header 3 -> 4, lines 10 -> 13, removed/changed 0.
  REST probes payablesAgingPeriods / agingPeriods: 404.
- Fresh test F: FSCRT_AK_GF_AGE1F, ProcessId 100004744396714, PASS (header 4 -> 5, lines 13 -> 16, RESULT OK).
  No errors reported; no wording change, so no retest needed.
- Own read-back: final export shows AGE1 and AGE1F with 3 lines each; first vs final export: header +2,
  lines +6, removed/changed 0.
- Tester suggestions not applied: move the name check into the Export section; say "showing 0 of N rows"
  means the name is free; say "status (unknown)" is also normal for the export; find the real PeriodName
  length; point at "Total Objects Failed: 0".
