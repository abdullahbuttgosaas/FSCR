task_code: PO_MANAGE_PURCHASING_VALUE_SETS
task_name: Manage Purchasing Value Sets
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 8
minutes_to_test: 9
waiting_minutes: 6
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: Purchasing module ID read live (ORA_PO_* lookup types)
test_records: FSCRT_MZ_GF_VS1 (own), FSCRT_MZ_GF_VSF (fresh), FSCRT_MZ_GF_VSR, FSCRT_MZ_GF_VS2R, FSCRT_MZ_GF_VS3R (retests); one value each
notes: own live test import 100004743402716, after-export 100004743405729; REST valueSets INDEP, max 20; final fresh retest (3R) passed on the final wording with no wrong sentence. retest_after_wording_fix: done
