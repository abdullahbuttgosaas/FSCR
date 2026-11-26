task_code: FND_MANAGE_MESSAGES
task_name: Manage Messages
module: Common Features
status: failed
filled_by: AB
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: not run (no load possible yet)
route: file route (Oracle docs, VERIFIED by reading): pipe-delimited MESSAGES file in the content repository + scheduled process Upload Comma-Separated Values File for Import Process (file type MESSAGES); REST messages read only; FSM CSV task export refused (flag N)
depends_on: the job package and definition name of the scheduled process (read once on the Scheduled Processes page); ApplicationId of the owning application (read live)
test_records: none (nothing loaded)
notes: Batch 23 (sitting 10). FAILED, proven cause: the scheduled process cannot be started by script because its job package and job definition name are not in Oracle's published docs (3 doc searches 2026-11-26), the REST resource the docs point to (valueSets) has no upload action (describe: get, create, update, delete, upsert), and the scheduler REST API returns empty job fields for requests; nothing was loaded. Next step: AB opens Scheduled Processes > Schedule New Process > Upload Comma-Separated Values File for Import Process once and notes the job package and definition (or reads MOS note 2174930.1); then run the skill Steps 3 to 5 with a GAPFILL_AB_ message (erpintegrations uploadFileToUcm + submitESSJobRequest).
