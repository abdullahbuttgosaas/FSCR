# CHANGELOG: Manage Purchasing Descriptive Flexfields

- 25/11/2026 (sitting 1, batch 02): skill written, not tested (unsafe to test, see STATUS.md). Read-only export only:
  13 CSVs, all 0 rows. No test records.
- 26/11/2026: placeholder `S` changed to `$S` (common wording fix).
- 26/11/2026: environment confirmed test-only by the tester; skill rewritten from a live test. Own test: try 1 import 100004743436790 (refused: multirow N, display type LIST_OF_VALUES), try 2 100004744417669 (refused: translatable N), try 3 100004744422130 (3 rows, 0 failed); after-export 100004743454753.
- Fresh test F: FSCRT_MZ_GF_CTXF, import ProcessId 100004744417700, after-export 100004743454861: PASS; reported that DEPLOYED status cannot show pending edits.
- Fresh test R: FSCRT_MZ_GF_CTXR, import ProcessId 100004744417737, after-export 100004744417758: PASS; found that each import moves DeploymentDate: the import deploys the flexfield (skill said it did not).
- Fresh test 2R: FSCRT_MZ_GF_CTX2R, import ProcessId 100004743447867, after-export 100004744422238: PASS; no factual error.
- Wording fixes after the fresh tests: see the findings above (each fixed before the next retest).
- Tester suggestions not applied (not errors): ShortPrompt cut mid-code; note that DeploymentDate may already be today from earlier tests; check the REST parent against the export parent before importing.
