task_code: ORA_ATK_MANAGE_HELP_CONTENT
task_name: Manage Help Content
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 14
waiting_minutes: 12
fresh_claude_pass: no (screen-only: no working create step to test)
route: FSM CSV export (ATK_KR_TOPIC, ORA_ATK_KR_TITLE, ORA_ATK_KR_GRAPHICS) read only; import of a new custom topic refused
depends_on: none
test_records: GAPFILL_AB_B13_HT1 to HT7 (100004743427290, 100004743428359, 100004743426241, 100004743429152, 100004743428368, 100004743426250, 100004743426259): all refused; after-export shows no new topic or title; retry 2026-11-26: round trip of the existing URL topic (100004744404970, PASS, no change); GAPFILL_AB_B13_HT8 (100004744404985), HT9 (100004743427714), HT10 (100004743429241): all refused; after-export topics 5, titles 10
notes: CSV exists but cannot create a new topic: PrimaryHierarchyIds is rejected on insert; the Manage Help Content page creates the hierarchy ID. Proven 2026-11-25/26 (batch 13): 10 create tries refused whatever hierarchy value was sent; round trip of an existing topic passes with no change; no help REST resource (6 names, HTTP 404). Read by the CSV export works (skill manage-help-content). Was failed in batch 13; changed to screen-only 2026-11-26 at AB's request (the cause is proven, not a fault of the skill).
