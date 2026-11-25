task_code: ORA_FND_GUIDED_LEARNING_ENABLED
task_name: Configure Guided Learning
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 2
waiting_minutes: 1
fresh_claude_pass: yes (re-test R after a wording fix)
route: REST profileOptions/FND_GUIDED_LEARNING_ENABLED/child/siteProfileOptionValues/SITE PATCH; REST read-back; test-and-restore. No CSV (FSCR: CSVExportImportSupportedFlag N)
depends_on: skill enable-click-to-dial (steps)
test_records: SITE Y->N->Y own (about 25 s); fresh F Y->N->Y (4 s); re-test R Y->N->Y (3 s)
notes: Batch 13. Neither-level task: no CSV package; the option was found by REST search (only option named Guided Learning; link to the task is a GUESS from name and description). Fresh test PASS; wrong sentence fixed (lookup is FND_SANDBOX_YESNO_TYPE, not YES_NO); re-test PASS.
