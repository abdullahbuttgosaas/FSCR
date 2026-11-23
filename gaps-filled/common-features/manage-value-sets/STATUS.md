task_code: FND_MANAGE_APPLCORE_VALUE_SETS
task_name: Manage Applications Core Value Sets
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 3
minutes_to_test: 3
waiting_minutes: 11
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_VS_T1; GAPFILL_A; GAPFILL_B; GAPFILL_VSF1_FRESH1; GAPFILL_F1A; GAPFILL_F1B; GAPFILL_AB_RT_VS; GAPFILL_AB_RT_V1; GAPFILL_AB_RT_V2
notes: Batch 1 part 3. Card over FSCR value-sets skill; REST cannot create a value set, so FSM CSV creates and REST reads back. Waiting includes about 8.5 min of a REST call hung on an expired token. Only independent character sets tested. Re-tested 2026-11-24 after the wording fix: PASS.
