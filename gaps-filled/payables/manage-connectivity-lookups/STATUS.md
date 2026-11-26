task_code: IBY_MANAGE_LOOKUPS:_EXTERNAL_CONNECTIVITY
task_name: Manage Payment System Connectivity Lookups
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes (fresh F passed first try, no errors)
route: FSM setup CSV import, FUN_APP_GENERIC_LOOKUP.csv; REST genericLookups (type) + standardLookups (read-back)
depends_on: an extensible IBY lookup type (e.g. IBY_SEC_CRED_TYPES, read live)
test_records: FSCRT_AK_GF_SCT1; FSCRT_AK_GF_SCT1F
notes: same package and export scope as Manage Disbursement Lookups (all IBY module codes)
