task_code: GL_MANAGE_DAILY_RATES
task_name: Manage Daily Rates
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 7
minutes_to_test: 2
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV (GL_DAILY_CONVERSION_TYPE + ORA_GL_CONVERSION_RATE_RULE); rate values are an external data load (not in the package)
depends_on: none (new rate type + its rules in one package)
test_records: GAPFILL_AB_B6_DRT2 (live; rules EUR, GBP); GAPFILL_AB_B6_DRT3F (fresh test; rules CAD, EUR); GAPFILL_AB_B6_DRT1 created by try 1 but without rules
notes: Batch 06. The CSV package holds rate types and cross-rate rules only; Oracle's log marks Conversion Rate (the rate values) as Data Load Pending = external load, not tested. Try 1: rules with EnabledFlag=Y were dropped without an error (type DRT1 created, 0 rules). Working rules all have EnabledFlag=N; try 2 with N: compare PASS. Fresh test PASS.
