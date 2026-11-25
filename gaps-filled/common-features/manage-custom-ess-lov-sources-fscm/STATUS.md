task_code: ORA_ATK_CUSTOM_ESS_FSCM
task_name: Manage Enterprise Scheduler Job Definitions and Job Sets for Financial, Supply Chain Management, and Related Applications
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 4
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV (ATK_ESSMETA_USER_JOB_LOV_SOURCE: a NEW job-parameter list-of-values source); export compare read-back. Job definitions and job sets are not in the package (task page only)
depends_on: none (an existing row's view object as data source)
test_records: GAPFILL_AB_B12_LOV1 (100004743427019); fresh GAPFILL_AB_B12_LOV4F (100004743426141)
notes: Batch 12. The task's CSV package holds only LOV sources (98 seeded-derived rows before). New source on an existing view object: PASS first try (98 -> 99). Fresh test PASS.
