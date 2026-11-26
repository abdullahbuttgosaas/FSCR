task_code: AP_MANAGE_PAYABLES_LOOKUPS
task_name: Manage Payables Lookups
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 7
waiting_minutes: 5
fresh_claude_pass: yes (fresh F passed first try, no errors)
route: FSM setup CSV import, FUN_APP_GENERIC_LOOKUP.csv (code row only; US translation automatic); REST genericLookups for the type
depends_on: an extensible Payables lookup type (e.g. PAY GROUP, read live by REST genericLookups)
test_records: FSCRT_AK_GF_PG1; FSCRT_AK_GF_PG1F
notes: needs ChangeSinceLastRefresh=N and no translation row for a new code (found in own tries 1-3)
