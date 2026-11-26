# CHANGELOG - Manage Task Types (DOO_MANAGE_TASK_TYPES)

## 2026-11-26 (sitting 1, batch 01)
- Skill written from the live export; own test: FSCRT_AK_GF_TT1: export 100004744422798, import 100004743456286 (1 row, 0 failed), after-export 100004743455410: 6 new rows (type, translation, 2 services, 2 service translations), 0 existing changed.
- Fresh test F: FSCRT_AK_GF_TTF: export 100004744422955, import 100004743456490, after-export 100004743455721: 6 new rows, 0 changed. PASS.
- Wording fixes after F (all skills): "Notes for every run" added (empty before/after folders, file names hold the environment name, --find code check, interim import status lines are harmless, code length tested at 15).
- Tester F: no command to check the code / list OperationCodes (fixed: --find and --csv commands; VERIFIED list of 8 codes).
- Tester F: OrchestrationActivityDefinitionSetupVO with 0 rows could look like a problem (fixed: said normal).
- Tester F: file names hold the environment name (fixed).
- Tester R notes (not applied): 4-char suffix and the Create+Inbound requirement remain untested (labelled GUESS).
- Re-test R after the fixes: FSCRT_AK_GF_TTR: export 100004744433050, import 100004744433146, after-export 100004744431692: 6 new rows, 0 changed. PASS, no wrong sentence.
