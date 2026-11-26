task_code: ORA_GL_MANAGE_APPLCORE_MESSAGES
task_name: Manage Messages for General Ledger
module: Common Features
status: failed
filled_by: AB
date: 2026-11-27
minutes_to_write: 3
minutes_to_test: 1
waiting_minutes: 0
fresh_claude_pass: not run (failed: job path unknown)
route: pipe-delimited MESSAGES file + scheduled process Upload Comma-Separated Values File for Import Process (file type MESSAGES), from Oracle docs; same route as manage-messages
depends_on: the job package and definition name of the upload process (not published); GL ApplicationId (read live)
test_records: none (nothing loaded)
notes: Batch 24 (sitting 11). Same object and blocker as Manage Messages (failed, batch 23): FSM CSV refused (flag N); REST messages get only (POST refused 2026-11-25); the upload process job package and definition are not in Oracle's docs, valueSets has no upload action, scheduler REST returns empty job names. Next step: AB reads the job name once on Scheduled Processes (or MOS 2174930.1); then skill Steps 3 to 5 with a prefix GL message.
