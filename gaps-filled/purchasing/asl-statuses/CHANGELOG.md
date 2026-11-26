# CHANGELOG: Manage Approved Supplier List Statuses

- 25/11/2026 batch 01: own live test, import 100004743402666, after-export 100004743405690. Skill written (VERIFIED/GUESS labels).
- Fresh test F: FSCRT_MZ_GF_ASF, import ProcessId 100004743404886, after-export 100004743402872: PASS; reported --match wording, length and description unclear, listener stop missing.
- Fresh test R: FSCRT_MZ_GF_ASR, import ProcessId 100004744391092, after-export 100004744393044: PASS; no wrong sentence.
- Fresh test 2R: FSCRT_MZ_GF_A2R, import ProcessId 100004743436222, after-export 100004744415960: PASS; noted COMMON prose slip S/log_summary.py.
- Fresh test 3R: FSCRT_MZ_GF_A3R, import ProcessId 100004743447599, after-export 100004744417655: PASS; no wrong sentence.
- Wording fixes after fresh tests (COMMON_STEPS and this skill): --match output described correctly; extra prefix keys from parallel testers are not a failure; console output and REST output go to logs (environment names in file names); import status lines explained; listener stop; `$S` scripts variable; ProcessIds not in time order; free-text rule; unchanged parent rows in step 2; log_summary.py prints only the ProcessId.
- Tester suggestions not applied (not errors): worked-example counts are from one run.
