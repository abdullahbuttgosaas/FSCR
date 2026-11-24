task_code: FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES
task_name: Manage Applications Core Attachment Entities
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 6
minutes_to_test: 3
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P1_AE2 (live); GAPFILL_AB_P1_AE3F (fresh test); entities on FND_LOOKUP_TYPES / LOOKUP_TYPE, no category link. GAPFILL_AB_P1_AE1 was refused, not created
notes: Batch 4 part 1. Row written in full (scoped export empty); ModuleId live from YES_NO. Try 1 refused (JBO-27014 DataObjectCode required); fixed by comparing with 22 working entities (DataObjectCode = upper-case entity name). Export compare is the proof (no REST). Fresh test PASS; tester notes not applied.
