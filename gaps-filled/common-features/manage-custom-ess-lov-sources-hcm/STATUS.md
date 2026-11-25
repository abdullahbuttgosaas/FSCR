task_code: ORA_ATK_CUSTOM_ESS_HCM
task_name: Manage Enterprise Scheduler Job Definitions and Job Sets for Human Capital Management and Related Applications
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 1
minutes_to_test: 3
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV (same package as ORA_ATK_CUSTOM_ESS_FSCM: ATK_ESSMETA_USER_JOB_LOV_SOURCE); export compare read-back
depends_on: skill manage-custom-ess-lov-sources-fscm (steps)
test_records: GAPFILL_AB_B12_LOV3 (100004743427054); fresh GAPFILL_AB_B12_LOV6F (100004744404522)
notes: Batch 12. Same file and rows as the FSCM task. Own test PASS (100 -> 101). Fresh test PASS.
