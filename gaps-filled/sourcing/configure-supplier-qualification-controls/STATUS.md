task_code: ORA_POQ_CONFIGURE_SUPPLIER_QUALIFICATION_CONTROLS
task_name: Configure Supplier Qualification Controls
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-28
minutes_to_write: 6
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes (fresh F PASS; no wrong sentence)
route: FSM CSV (ORA_SUPPLIER_QUALIFICATION_OPTIONS, one global row) as test-and-restore
depends_on: none
test_records: no new record (one global row). Own test: SendRFENotifEvalTeamFlag Y -> N (100004744440678), restored Y (100004744440698), restored export = first export; fresh F: Y -> N (100004744441931), restored Y (100004744442345), restored export = first export
notes: Sourcing batch 04 (sitting 2). The task has one row (key ORA_POQ_QUALIFICATION_OPTION) and no create, so a new prefix record is impossible; test-and-restore on the lowest-impact column (notifications only), old value read by export first, both packages built before the change, value live about 2 minutes, restore proved by a compare with the first export (changed 0). Eligibility codes were never changed. Suggestions NOT applied: mkdir RUN in Step 1; a way to check the sign-in age; mention the builder's 'Y' -> 'N' line; print times around Step 3.
