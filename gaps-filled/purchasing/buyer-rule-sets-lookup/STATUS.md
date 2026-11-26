task_code: ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP
task_name: Manage Buyer Assignment Rule Sets Lookup
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 9
minutes_to_test: 8
waiting_minutes: 6
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: parent lookup type PO_BUYER_ASSIGN_RULE_SETS (seeded, sent unchanged)
test_records: FSCRT_MZ_GF_RS1 (own), FSCRT_MZ_GF_RSF (fresh), FSCRT_MZ_GF_RS2R, FSCRT_MZ_GF_RS3R (retests)
notes: own live test try 1 import 100004743404860 (parent missing, 0 processed); try 2 import 100004743404898; after-export 100004743404936; final fresh retest (3R) passed on the final wording with no wrong sentence. retest_after_wording_fix: done
