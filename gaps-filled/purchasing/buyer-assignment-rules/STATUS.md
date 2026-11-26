task_code: ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES
task_name: Manage Buyer Assignment Rules
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 14
minutes_to_test: 10
waiting_minutes: 6
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP (a test rule set); an existing rule to copy BU, organization, supplier and buyer from
test_records: rules 9999 (FSCRT_MZ_GF_RS1, own), 9998 (FSCRT_MZ_GF_RSF, fresh), 10007 (FSCRT_MZ_GF_RS2R, retest R), 10008 (FSCRT_MZ_GF_RS3R, retest 2R); all with ExceedsLineAmount 999999999
notes: own live test import 100004744422117, after-export 100004743447698; final fresh retest (2R) passed with no factual error. retest_after_wording_fix: done. tested on 26/11/2026 after the tester confirmed the environment is for testing only. Safeguard: Oracle evaluates every rule in sequence order whatever its rule set (26D docs), so test rules use a sequence above all existing ones and ExceedsLineAmount 999999999. Earlier (25/11) marked unsafe to test.
