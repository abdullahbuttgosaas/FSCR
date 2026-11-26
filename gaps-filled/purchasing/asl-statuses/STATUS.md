task_code: PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES
task_name: Manage Approved Supplier List Statuses
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 5
minutes_to_test: 8
waiting_minutes: 5
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: none
test_records: FSCRT_MZ_GF_AS1 (own), FSCRT_MZ_GF_ASF (fresh), FSCRT_MZ_GF_ASR, FSCRT_MZ_GF_A2R, FSCRT_MZ_GF_A3R (retests)
notes: own live test import 100004743402666, after-export 100004743405690; final fresh retest (3R) passed on the final wording with no wrong sentence. retest_after_wording_fix: done
