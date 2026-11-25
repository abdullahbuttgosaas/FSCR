task_code: OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_LOOKUPS
task_name: Manage Contract Clause Types
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 3
waiting_minutes: 2
fresh_claude_pass: yes (3 fresh rounds: F, R, R2; R2 found no wrong sentence)
route: FSM CSV (standard lookup package, type OKC_SUBJECT) + REST standardLookups read-back
depends_on: none (seeded extensible type OKC_SUBJECT)
test_records: code GAPFILL_AB_B1_CT1 on OKC_SUBJECT (ProcessId 100004744392840); fresh code GAPFILL_AB_B1_CT2F created (100004744393360); continuation fresh tests: codes GAPFILL_AB_B1_CT3F (100004744394163), CT4R (100004744393544), CT5R (100004743407899)
notes: Batch 01. Export is empty (scope OKC_SUBJECT); type row copied unchanged from REST (helper lookup_type_row.py). Own test PASS: 2 rows processed, 0 failed; REST: 1 code added, type and 16 codes unchanged. First fresh tester stopped by the org spend limit (records it loaded stay, listed in test_records; not re-imported). Continuation 2026-11-25: fresh round F PASS but found skill faults (no safe log reader: risk of printing a user name; wrong 'empty export' sentence); fixed (read_import_log.py, shell section) -> round R PASS but found the recovery path saved a log the reader cannot find and code blocks lacked the export line; fixed -> round R2 PASS, no wrong sentence. Suggestions NOT applied (would need another re-test): Save the export output to a file and print only a pass/fail line (the network error line holds the server address).
