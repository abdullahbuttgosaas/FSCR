task_code: HRW_ESTABLISH_ENTERPRISE_STRUCTURES
task_name: Establish Enterprise Structures
module: Common Features
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 6
minutes_to_test: 5
waiting_minutes: 6
fresh_claude_pass: yes
route: FSM CSV of the task (16 files); one new HRW_ENTERPRISE_CONFIG row (Name, EnterpriseId, Description), the other 15 files header only: creates a new enterprise configuration draft that is never loaded
depends_on: none (EnterpriseId read from the export)
test_records: GAPFILL_AB_B25_EC1 (ProcessId 100004743463498); fresh GAPFILL_AB_B25_EC2F (ProcessId 100004744439054). Drafts only, never loaded: no business unit, legal entity, division or location created
notes: Batch 25 (sitting 11). Own test: 1 row, 0 failed; read back: new row found, only HRW_ENTERPRISE_CONFIG.csv changed (5 -> 6 drafts), other 15 files same row counts. Fresh test PASS (6 -> 7 drafts, only that file changed), no wrong sentence. Rule: never press Load Configuration on a test draft. Tester suggestions not applied: print the ProcessId in Step 3; say the log has more Completed lines plus an In progress header line (holds the environment name, do not print); draft count in Step 1 is a snapshot; say whether row counts include the header; z.close() in the zip line; put the EnterpriseId note above the printf.
