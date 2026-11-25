task_code: ORA_PO_MANAGE_SPECIAL_HANDLING_TYPES
task_name: Manage Special Handling Types
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 3
waiting_minutes: 3
fresh_claude_pass: yes (3 fresh rounds: F, R, R2; R2 found no wrong sentence)
route: FSM CSV (ORA_PO_SPECIAL_HANDLING + translation)
depends_on: none
test_records: GAPFILL_AB_B1_SH1 (ProcessId 100004743406576); fresh GAPFILL_AB_B1_SH2F NOT created (tester stopped after its export); continuation fresh tests: GAPFILL_AB_B1_SH3F (100004744394175), SH4R (100004744394477; connection dropped, log recovered by ProcessId), SH5R (100004744393577)
notes: Batch 01. Own live test PASS (export compare: added 1 type + 1 translation, removed 0, changed 0). First fresh tester stopped by the org spend limit (records it loaded stay, listed in test_records; not re-imported). Continuation 2026-11-25: fresh round F PASS but found skill faults (no safe log reader: risk of printing a user name; wrong 'empty export' sentence); fixed (read_import_log.py, shell section) -> round R PASS but found the recovery path saved a log the reader cannot find and code blocks lacked the export line; fixed -> round R2 PASS, no wrong sentence. Suggestions NOT applied (would need another re-test): Step 1: warn not to print audit columns when looking at the export.
