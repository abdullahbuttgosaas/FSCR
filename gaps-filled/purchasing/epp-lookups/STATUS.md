task_code: ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_LOOKUPS
task_name: Manage External Purchase Prices Lookups
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 7
minutes_to_test: 9
waiting_minutes: 6
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: module ID read live (ORA_SCH_EPP% lookup types)
test_records: FSCRT_MZ_GF_LK1 (own), FSCRT_MZ_GF_LKF (fresh), FSCRT_MZ_GF_LKR, FSCRT_MZ_GF_LK2R, FSCRT_MZ_GF_LK3R (retests); code FSCRT_MZ_GF_A in each
notes: own live test import 100004742441892, after-export 100004743404730; final fresh retest (3R) passed on the final wording with no wrong sentence. retest_after_wording_fix: done
