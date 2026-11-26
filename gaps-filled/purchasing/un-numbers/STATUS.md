task_code: PO_MANAGE_UN_NUMBERS
task_name: Manage UN Numbers
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 6
minutes_to_test: 10
waiting_minutes: 7
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: PO_MANAGE_HAZARD_CLASSES (optional link to a test hazard class)
test_records: FSCRT_MZ_GF_UN1 (own), FSCRT_MZ_GF_UNF+HUF (fresh), FSCRT_MZ_GF_UNR+HUR, FSCRT_MZ_GF_UN2R+HU2R, FSCRT_MZ_GF_UN3R+HU3R (retests)
notes: own live test import 100004742441905, after-export 100004742441914; final fresh retest (3R) passed on the final wording with no wrong sentence. retest_after_wording_fix: done
