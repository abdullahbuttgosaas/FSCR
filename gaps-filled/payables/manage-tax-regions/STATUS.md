task_code: AP_MANAGE_TAX_REGIONS
task_name: Manage Tax Regions
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes (fresh F passed first try, no errors)
route: FSM setup CSV import, AP_INCOME_TAX_REGION.csv; REST read-back payablesIncomeTaxRegions (q on state)
depends_on: -
test_records: FSCRT_AK_1; FSCRT_AK_F
notes: RegionShortName max 10 characters, so the 12-character GF prefix cannot be the key; names follow the pack rule FSCRT_AK_ and the long names carry FSCRT_AK_GF_
