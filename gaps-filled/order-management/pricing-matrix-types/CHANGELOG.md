# CHANGELOG - Manage Pricing Matrix Types (ORA_QP_MANAGE_PRICING_MATRIX_TYPES)

## 2026-11-26 (sitting 1, batch 01)
- Skill written from the live export; own test: FSCRT_AK_GF_MT1: export 100004743456213, import 100004744422848 (1 row, 0 failed), after-export 100004744431234: 1 new row, 0 existing changed; REST GET shows class resolved from the name.
- Fresh test F: FSCRT_AK_GF_MTF: export 100004743455531, import 100004744422999, after-export 100004744431361: 1 new row, 0 changed; REST OK. PASS.
- Wording fixes after F (all skills): "Notes for every run" added (empty before/after folders, file names hold the environment name, --find code check, interim import status lines are harmless, code length tested at 15).
- Tester F: class choice rule (fixed).
- Tester F: export holds only part of the types (fixed: explained).
- Tester R suggestion (not applied): call the 4/18 counts examples, they grow with test records.
- Re-test R after the fixes: FSCRT_AK_GF_MTR: export 100004744433067, import 100004744431526, after-export 100004743455857: 1 new row, 0 changed; REST OK. PASS, no wrong sentence.
