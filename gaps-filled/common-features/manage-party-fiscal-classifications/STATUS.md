task_code: ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS
task_name: Manage Party Fiscal Classifications
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 5
minutes_to_test: 8
waiting_minutes: 9
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P3_PFC1 (live), GAPFILL_AB_P3_PFC2F (fresh test); USER_DEFINED types reusing the class category of the first seeded type; no regime association, no codes
notes: Batch 3 part 3. Template row from an existing party fiscal classification type; reusing its TCA class category was accepted (3 types now share it). No REST searched; export compare is the proof. Fresh test PASS, no deviation; notes not applied. Oracle waiting shared with the other two Part 3 tasks (run in parallel).
