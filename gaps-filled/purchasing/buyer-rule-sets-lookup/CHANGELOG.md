# CHANGELOG: Manage Buyer Assignment Rule Sets Lookup

- 25/11/2026 batch 02: own live test, try 1 import 100004743404860 (parent missing, 0 processed); try 2 import 100004743404898; after-export 100004743404936. Skill written (VERIFIED/GUESS labels).
- Fresh test F: FSCRT_MZ_GF_RSF, import ProcessId 100004744391104, after-export 100004744392127: PASS; reported Meaning/Description conflict, partial REST check, $R not set.
- Fresh test 2R: FSCRT_MZ_GF_RS2R, import ProcessId 100004743435992, after-export 100004744415983: PASS; reported step 2 "ONLY your new rows" vs unchanged parents.
- Fresh test 3R: FSCRT_MZ_GF_RS3R, import ProcessId 100004743448053, after-export 100004744422074: PASS; no wrong sentence.
- Wording fixes after fresh tests (COMMON_STEPS and this skill): --match output described correctly; extra prefix keys from parallel testers are not a failure; console output and REST output go to logs (environment names in file names); import status lines explained; listener stop; `$S` scripts variable; ProcessIds not in time order; free-text rule; unchanged parent rows in step 2; log_summary.py prints only the ProcessId.
- Tester suggestions not applied (not errors): heredocs need <RUN> typed in; separate REST log names.
