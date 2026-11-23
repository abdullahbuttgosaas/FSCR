task_code: XLE_MANAGE_LEGAL_AUTHORITIES
task_name: Manage Legal Authorities
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 7
minutes_to_test: 7
waiting_minutes: 9
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P3_LA1 (live), GAPFILL_AB_P3_LA2F (fresh test); organization parties with legal authority usage, address copied from the template (test street), legislative category, tax authority profile; nothing points to them
notes: Batch 3 part 3. Template rows from an existing legal authority over 7 files, every internal id column cleared; Oracle kept the given PartyNumber and PartySiteNumber. No REST searched; export compare is the proof. Fresh test PASS (one export retry after a drop, allowed by the skill); notes not applied. Oracle waiting shared with the other two Part 3 tasks (run in parallel).
