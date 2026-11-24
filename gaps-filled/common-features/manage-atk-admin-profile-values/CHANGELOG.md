# CHANGELOG: manage-atk-admin-profile-values (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-24 (batch 4 part 1, AB with Claude)
- Read-only export: see `evidence/batch-04/ORA_ATK_ADMIN_PROFILE_OPTION_VALUES/02_found.png`.
- Live test: option `GAPFILL_AB_P1_APO1` + SITE value `GAPFILL_AB_P1_AV1`: 1 import (ProcessId 100004741419235), 5 rows, 0 failed. REST option + value PASS; export compare added 1 + 3 + 1, removed 0, changed 0: PASS.
- Fresh test (task name + SKILL.md only): PASS, `GAPFILL_AB_P1_APO2F` + `GAPFILL_AB_P1_AV2F`, ProcessId 100004741415574, about 3 minutes. Read back again by REST in the main session (option and value): PASS.
- Tester notes, **not applied** (tested wording stays on disk): **the full skill's log one-liner prints the 'Submitted By' user name: needs a filter (follow-up, needs a re-test of the full skill and its cards)**; environment name appears in FSCR output file names; Description/StartDateActive defaults; timings were faster (24 s / 39 s); REST shows more ATK options than the export (normal); spell out APPID in all compare expects.

## Test records created
- GAPFILL_AB_P1_APO1 + SITE value GAPFILL_AB_P1_AV1 (live); GAPFILL_AB_P1_APO2F + GAPFILL_AB_P1_AV2F (fresh test); values only on own new ATK options.
