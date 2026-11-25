task_code: OKC_MANAGE_CONTRACT_LINE_TYPES
task_name: Manage Contract Line Types
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes (3 fresh rounds: F, R, R2; R2 found no wrong sentence)
route: FSM CSV (OKC_LINE_TYPE)
depends_on: an existing line type source (SourceCode from the export)
test_records: GAPFILL_AB_B1_LT1 (refused OKC_SETUP_INVALID_LINE_SOURCE, not created; ProcessId 100004744392804); GAPFILL_AB_B1_LT2 (100004744392822); fresh GAPFILL_AB_B1_LT3F created (100004744393348); continuation fresh tests: GAPFILL_AB_B1_LT4F (100004744394186), LT5R (100004744394829), LT6R (100004743407814)
notes: Batch 01. Try 1 with a made-up SourceCode refused; try 2 on USER_FREE_FORM_BUY: PASS (compare added 1, removed 0, changed 0). First fresh tester stopped by the org spend limit (records it loaded stay, listed in test_records; not re-imported). Continuation 2026-11-25: fresh round F PASS but found skill faults (no safe log reader: risk of printing a user name; wrong 'empty export' sentence); fixed (read_import_log.py, shell section) -> round R PASS but found the recovery path saved a log the reader cannot find and code blocks lacked the export line; fixed -> round R2 PASS, no wrong sentence. Suggestions NOT applied (would need another re-test): Check for a ZIP before the unzip line (a failed export gives an IndexError); save export output to a file.
