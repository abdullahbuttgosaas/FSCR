task_code: FND_MANAGE_APPLCORE_STANDARD_LOOKUPS
task_name: Manage Applications Core Standard Lookups
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 11
minutes_to_test: 2
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_SL_T1; GAPFILL_A; GAPFILL_B; GAPFILL_SLF1_TYPE; GAPFILL_F1_ONE; GAPFILL_F1_TWO; GAPFILL_AB_RT_SL; GAPFILL_AB_RT_SL_A; GAPFILL_AB_RT_SL_B
notes: Batch 1 part 1. Full skill + 4 scripts (standard lookup package); created by FSM CSV import, read back by REST (FSCR generic lookups skill). Minutes to write include about 1 min waiting for an answer. Re-tested 2026-11-24 after the wording fix: PASS.
