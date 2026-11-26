# CHANGELOG: Manage Purchasing Value Sets

- 25/11/2026 batch 01: own live test, import 100004743402716, after-export 100004743405729; REST valueSets INDEP, max 20. Skill written (VERIFIED/GUESS labels).
- Fresh test F: FSCRT_MZ_GF_VSF, import ProcessId 100004742441987, after-export 100004744391020: PASS; reported "export may be empty" wording and values-CSV key note.
- Fresh test R: FSCRT_MZ_GF_VSR, import ProcessId 100004743406225, after-export 100004743406278: PASS; reported missing REST commands, free-text conflict.
- Fresh test 2R: FSCRT_MZ_GF_VS2R, import ProcessId 100004743435976, after-export 100004743436267: PASS; noted COMMON prose slip S/log_summary.py.
- Fresh test 3R: FSCRT_MZ_GF_VS3R, import ProcessId 100004743436599, after-export 100004743447620: PASS; no wrong sentence.
- Wording fixes after fresh tests (COMMON_STEPS and this skill): --match output described correctly; extra prefix keys from parallel testers are not a failure; console output and REST output go to logs (environment names in file names); import status lines explained; listener stop; `$S` scripts variable; ProcessIds not in time order; free-text rule; unchanged parent rows in step 2; log_summary.py prints only the ProcessId.
- Tester suggestions not applied (not errors): grep -c "row:" for the --match check; worked-example counts are from one run.
