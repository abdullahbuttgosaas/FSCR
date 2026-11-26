task_code: PO_MANAGE_HAZARD_CLASSES
task_name: Manage Hazard Classes
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 6
minutes_to_test: 9
waiting_minutes: 6
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: none
test_records: FSCRT_MZ_GF_HC1 (own), FSCRT_MZ_GF_HCF (fresh), FSCRT_MZ_GF_HCR, FSCRT_MZ_GF_HC2R, FSCRT_MZ_GF_HC3R (retests)
notes: own live test import 100004743405677, after-export 100004743404738; final fresh retest (3R) passed on the final wording with no wrong sentence. retest_after_wording_fix: done
