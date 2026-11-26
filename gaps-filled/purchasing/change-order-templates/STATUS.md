task_code: PO_MANAGE_CHANGE_ORDER_TEMPLATES
task_name: Manage Change Order Templates
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 8
minutes_to_test: 8
waiting_minutes: 6
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: an existing template with attribute rows (read only, copied)
test_records: FSCRT_MZ_GF_CO1 (own), FSCRT_MZ_GF_COF (fresh), FSCRT_MZ_GF_CO2R, FSCRT_MZ_GF_CO3R (retests); 132 attribute rows each
notes: own live test import 100004744391044, after-export 100004743404958; final fresh retest (3R) passed on the final wording with no wrong sentence. retest_after_wording_fix: done
