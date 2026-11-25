task_code: ORA_CMK_MANAGE_COLLAB_MESG_CONFIG
task_name: Manage Collaboration Messaging Configuration
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 7
waiting_minutes: 5
fresh_claude_pass: yes (test-and-restore; re-test R after one wording fix)
route: FSM CSV (ORA_CMK_COLLAB_MSG_PARAM one row, --edit-row)
depends_on: none
test_records: no new record (test-and-restore of one parameter). Own: AutoRepTimePeriod 50->51 100004744393468, ->50 100004744394251. Fresh F: EssOutRepInterval 140->141 100004743407969, ->140 100004744391850. Re-test R: AutoRepTimePeriod 50->52 100004744396452, ->50 100004744393644; final compare PASS
notes: Batch 02. One shared parameter row; tested only as test-and-restore. Fresh F PASS but found one wrong sentence (PARAM_DATA maximums cannot be matched to a field: no parameter name) -> fixed, plus re-run-folder hints in Steps 4/6 -> re-test R: PASS. Re-test R found no wrong sentence. Suggestions NOT applied: re-run folder for the before export; check for 'Failed calling' before the unzip line.
