task_code: GL_MANAGE_DATA_ACCESS_SETS
task_name: Manage Data Access Sets
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 8
minutes_to_test: 4
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV (GL_ACCESS_SET_DEF + ORA_GL_ACCESS_SET_ASSIGNMENT_DEF); ledger values by REST ledgersLOV + chartOfAccountsLOV
depends_on: an existing ledger (read by REST)
test_records: GAPFILL_AB_B5_DAS2 (live, ledger 28Ledger US); GAPFILL_AB_B5_DAS3F (fresh test, ledger MG Primary ledger); not given to any user. GAPFILL_AB_B5_DAS1 was refused, not created
notes: Batch 05. Try 1 refused GL_INVALID_LEDGER (no StructureInstanceCode; export check 0 GAPFILL sets); try 2 with the COA instance code read live by REST chartOfAccountsLOV: 2 objects succeeded, compare PASS. Fresh test PASS first time. Sets are assigned to no user (Manage Data Access for Users not touched).
