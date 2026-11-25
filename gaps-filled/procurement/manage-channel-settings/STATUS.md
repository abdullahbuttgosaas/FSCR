task_code: ORA_MANAGE_CHANNEL_SETTINGS
task_name: Manage Channel Settings
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 7
waiting_minutes: 5
fresh_claude_pass: yes (test-and-restore; no wrong sentence)
route: FSM CSV (ORA_CJM_SETTING parent unchanged + ORA_CJM_SETTING_VALUE)
depends_on: the value row must exist
test_records: no new record (test-and-restore of EnabledFlag). Own: CLAIM_OWNER_CODE/BU2 Y->N 100004744393512 (no log found, mid export proved it), N->Y 100004744394843. Fresh: CUST_CHANNEL_CALENDAR/BUU1 Y->N 100004744395141, N->Y 100004744395154
notes: Batch 02. Value row needs its parent setting row in the same ZIP (--copy-row unchanged). build_csv_package.py --edit-row got a two-column key (Col=v&Col2=v2) because one ValueCode can sit under several settings. Own and fresh test-and-restore PASS (final compare with the first export: changed 0). Suggestions NOT applied: warn that compare_exports exits 1 on the expected mid FAIL.
