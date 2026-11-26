task_code: FND_MANAGE_APPLCORE_MESSAGES
task_name: Manage Applications Core Messages
module: Common Features
status: failed
filled_by: AB
date: 2026-11-26
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run (no load possible yet)
route: same file route as Manage Messages: MESSAGES file + scheduled process Upload Comma-Separated Values File for Import Process; REST messages read only; FSM CSV task export refused (flag N)
depends_on: FND_MANAGE_MESSAGES (same object and route); the job package and definition name of the scheduled process
test_records: none (nothing loaded)
notes: Batch 23 (sitting 10). FAILED, proven cause: same as Manage Messages (the scheduled process job path is not published, valueSets has no upload action, the scheduler REST API hides job names); nothing loaded. Next step: as Manage Messages; once that test passes, run this skill with ModuleKey of an Applications Core application (FND).
