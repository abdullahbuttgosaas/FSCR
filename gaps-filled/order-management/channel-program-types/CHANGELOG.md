# CHANGELOG - Manage Channel Program Types (ORA_CJM_MANAGE_PROGRAM_TYPES)

## 2026-11-26 (sitting 1, batch 01)
- Skill written from the live export; own test: FSCRT_AK_GF_PT1: export 100004744431194, import 100004744432477 (1 row, 0 failed), after-export 100004744432496: 3 new rows (type + 2 qualifiers), 0 existing changed; REST GET returned it (DRAFT).
- Fresh test F: FSCRT_AK_GF_PTF: export 100004744432577, import 100004743455628, after-export 100004744431370: 3 new rows, 0 changed; REST OK. PASS.
- Wording fixes after F (all skills): "Notes for every run" added (empty before/after folders, file names hold the environment name, --find code check, interim import status lines are harmless, code length tested at 15).
- Tester F: model-row choice and currency carry-over (fixed).
- Tester F: prefix uniqueness (fixed: pick an unused one; rule untested).
- Tester F: script had literal <RUN> (fixed: run folder as argument).
- Tester F: log wording incomplete (fixed: full sentence + qualifier object).
- Tester R suggestion (not applied): move the code-free note after the Export section.
- Re-test R after the fixes: FSCRT_AK_GF_PTR: export 100004744431388, import 100004743455842, after-export 100004743456531: 3 new rows, 0 changed; REST OK. PASS, no wrong sentence.
