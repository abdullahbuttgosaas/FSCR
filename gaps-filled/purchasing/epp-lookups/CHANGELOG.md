# CHANGELOG: Manage External Purchase Prices Lookups

- 25/11/2026 batch 01: own live test, import 100004742441892, after-export 100004743404730. Skill written (VERIFIED/GUESS labels).
- Fresh test F: FSCRT_MZ_GF_LKF, import ProcessId 100004743405762, after-export 100004743404925: PASS; reported prerequisite 2 output overwrite, Meaning wording, import status lines.
- Fresh test R: FSCRT_MZ_GF_LKR, import ProcessId 100004744392107, after-export 100004744391139: PASS; reported free-text conflict with COMMON_STEPS, REST redirect, bare S.
- Fresh test 2R: FSCRT_MZ_GF_LK2R, import ProcessId 100004744415939, after-export 100004744415972: PASS; noted COMMON prose slip S/log_summary.py.
- Fresh test 3R: FSCRT_MZ_GF_LK3R, import ProcessId 100004744417642, after-export 100004743448077: PASS; no wrong sentence.
- Wording fixes after fresh tests (COMMON_STEPS and this skill): --match output described correctly; extra prefix keys from parallel testers are not a failure; console output and REST output go to logs (environment names in file names); import status lines explained; listener stop; `$S` scripts variable; ProcessIds not in time order; free-text rule; unchanged parent rows in step 2; log_summary.py prints only the ProcessId.
- Tester suggestions not applied (not errors): prerequisite 1 limit=3 could be raised; separate REST log names.
