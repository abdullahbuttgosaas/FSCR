# CHANGELOG: Manage UN Numbers

- 25/11/2026 batch 01: own live test, import 100004742441905, after-export 100004742441914. Skill written (VERIFIED/GUESS labels).
- Fresh test F: FSCRT_MZ_GF_UNF, import ProcessId 100004743405788, after-export 100004742424000: PASS; reported --match wording, separate run folder for the prerequisite, extra prefix keys.
- Fresh test R: FSCRT_MZ_GF_UNR, import ProcessId 100004744392231, after-export 100004744392255: records created and read back; the tester stopped on an API spend limit before reporting (results checked from its files).
- Fresh test 2R: FSCRT_MZ_GF_UN2R, import ProcessId 100004743436417, after-export 100004743447583: PASS; noted <RUN> sub-folder wording.
- Fresh test 3R: FSCRT_MZ_GF_UN3R, import ProcessId 100004743436725, after-export 100004743436736: PASS; no wrong sentence.
- Wording fixes after fresh tests (COMMON_STEPS and this skill): --match output described correctly; extra prefix keys from parallel testers are not a failure; console output and REST output go to logs (environment names in file names); import status lines explained; listener stop; `$S` scripts variable; ProcessIds not in time order; free-text rule; unchanged parent rows in step 2; log_summary.py prints only the ProcessId.
- Tester suggestions not applied (not errors): Read back could repeat the note about other testers' prefix keys.
