task_code: ORA_ATK_MANAGE_HELP_CONTENT
task_name: Manage Help Content
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 14
waiting_minutes: 12
fresh_claude_pass: no (screen-only: no working create step to test)
route: none: no FSM CSV package that creates this record, no REST create route; set on the page only
depends_on: none
test_records: GAPFILL_AB_B13_HT1 to HT7 (100004743427290, 100004743428359, 100004743426241, 100004743429152, 100004743428368, 100004743426250, 100004743426259): all refused; after-export shows no new topic or title; retry 2026-11-26: round trip of the existing URL topic (100004744404970, PASS, no change); GAPFILL_AB_B13_HT8 (100004744404985), HT9 (100004743427714), HT10 (100004743429241): all refused; after-export topics 5, titles 10
notes: Verification run 2026-11-26 (read only): 1) CSV: export 2026-11-26: flag Y, 3 files; package holds the help topic files (ATK_KR_TOPIC 5 rows, ORA_ATK_KR_TITLE 10, ORA_ATK_KR_GRAPHICS 0), BUT a new topic cannot be created: 10 create imports refused in batch 13 (PrimaryHierarchyIds rejected on insert; the page makes the hierarchy id); round trip of an existing topic passes with no change. 2) REST: atkhelpcentertopics GET 200, describe: get only (VERIFIED today); 6 other help names 404 (earlier). 3) Oracle docs (3 endpoint lists read: Common Features, Financials, part of Sales; plus page searches): Common Features endpoint list: the Help Center topic resource is read only. DECISION: screen-only (no CSV package that can create the record and no REST create route). Nothing was created.
