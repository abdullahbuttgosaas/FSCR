# CHANGELOG: Manage Change Order Templates

- 25/11/2026 batch 02: own live test, import 100004744391044, after-export 100004743404958. Skill written (VERIFIED/GUESS labels).
- Fresh test F: FSCRT_MZ_GF_COF, import ProcessId 100004744392093, after-export 100004744393058: PASS; reported --rows sample concern, source template choice, ProcessId order.
- Fresh test 2R: FSCRT_MZ_GF_CO2R, import ProcessId 100004743436232, after-export 100004743448005: PASS; no wrong sentence.
- Fresh test 3R: FSCRT_MZ_GF_CO3R, import ProcessId 100004744422018, after-export 100004744422033: PASS; no wrong sentence.
- Wording fixes after fresh tests (COMMON_STEPS and this skill): --match output described correctly; extra prefix keys from parallel testers are not a failure; console output and REST output go to logs (environment names in file names); import status lines explained; listener stop; `$S` scripts variable; ProcessIds not in time order; free-text rule; unchanged parent rows in step 2; log_summary.py prints only the ProcessId.
- Tester suggestions not applied (not errors): worked-example counts are from one run; heredoc placeholders typed by hand.
