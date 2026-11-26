# CHANGELOG - Manage Status Values (DOO_MANAGE_STATUS_VALUES)

## 2026-11-26 (sitting 1, batch 01)
- Skill written from the live export; own test: FSCRT_AK_GF_ST1: export 100004744432201, import 100004743455333 (1 row, 0 failed), after-export 100004744422896: 2 new rows (code + US translation), 0 existing changed.
- Fresh test F: FSCRT_AK_GF_STF: export 100004743456389, import 100004744431303, after-export 100004743455676: 2 new rows, 0 changed. PASS.
- Wording fixes after F (all skills): "Notes for every run" added (empty before/after folders, file names hold the environment name, --find code check, interim import status lines are harmless, code length tested at 15).
- Tester F: no one-line command to check the code is free (fixed: inspect_export.py --find).
- Tester F: file names hold the environment name (fixed: Notes for every run).
- Tester F: maximum code length unknown (fixed: stated as tested 15, longer not tested).
- Tester F: re-run into the same before/after folder breaks the glob (fixed: Notes).
- Tester R suggestion (not applied): mention the .txt log next to the ZIP.
- Re-test R after the fixes: FSCRT_AK_GF_STR: export 100004744432727, import 100004744431579, after-export 100004744431734: 2 new rows, 0 changed. PASS, no wrong sentence.
