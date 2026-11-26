task_code: IBY_MANAGE_LOOKUPS:_DISBURSEMENTS
task_name: Manage Disbursement Lookups
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes (fresh F passed; wording error fixed; retest R passed with no errors)
route: FSM setup CSV import, FUN_APP_GENERIC_LOOKUP.csv; REST genericLookups (type) + standardLookups (read-back)
depends_on: an extensible IBY lookup type (e.g. IBY_BANK_CHARGE_BEARER, read live)
test_records: FSCRT_AK_GF_BCB1; FSCRT_AK_GF_BCB1F; FSCRT_AK_GF_BCB1R
notes: shares package and export scope (IBY module codes) with Manage Payment System Connectivity Lookups
