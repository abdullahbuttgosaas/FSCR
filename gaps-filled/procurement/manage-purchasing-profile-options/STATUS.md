task_code: PO_MANAGE_PURCHASING_PROFILE_OPTIONS
task_name: Manage Purchasing Profile Options
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: yes (3 fresh rounds: F, R, R2; R2 found no wrong sentence)
route: FSM CSV (profile package, application 201) + REST profileOptions read-back
depends_on: none
test_records: GAPFILL_AB_B2_PO1 (3 levels + SITE value Y; ProcessId 100004743407091); continuation fresh tests: GAPFILL_AB_B2_PO2F (100004743406790), PO3R (100004744394653), PO4R (100004744396141; connection dropped, log recovered by ProcessId)
notes: Batch 02. A new Purchasing option outside the export's fixed scope list was accepted (5 rows, 0 failed); REST profileOptions read-back PASS (profileValues did not find it). Changing seeded purchasing options is not tested (shared settings; test-and-restore possible later). First fresh tester stopped by the org spend limit (records it loaded stay, listed in test_records; not re-imported). Continuation 2026-11-25: fresh round F PASS but found skill faults (no safe log reader: risk of printing a user name; wrong 'empty export' sentence); fixed (read_import_log.py, shell section) -> round R PASS but found the recovery path saved a log the reader cannot find and code blocks lacked the export line; fixed -> round R2 PASS, no wrong sentence. Suggestions NOT applied (would need another re-test): mkdir the import folder before the recovery fetch; StatusCode '(no result yet)' is normal too.
