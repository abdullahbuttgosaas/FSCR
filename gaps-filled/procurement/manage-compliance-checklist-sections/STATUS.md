task_code: ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS
task_name: Manage Compliance Checklist Sections
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 6
waiting_minutes: 4
fresh_claude_pass: yes (no wrong sentence)
route: FSM CSV (ORA_POQ_CHECKLIST_SECTION + translation + section questions)
depends_on: a procurement BU; for an active section an active checklist question
test_records: GAPFILL_AB_B3_CS1 draft (100004744391888); GAPFILL_AB_B3_CS2 active without question refused POQ_AREA_QUES_REQD_ERROR (100004744391901, not created); GAPFILL_AB_B3_CS3 active with question CQ2 (100004744391914); fresh GAPFILL_AB_B3_CS4F draft (100004744395994)
notes: Batch 03. Usage code ORA_CHECKLIST; owner set by Oracle (DefaultQualOwnerFlag=Y, owner columns empty); BU Vision BU. Own + fresh export compare PASS. Suggestions NOT applied: 'started with 0 rows' is out of date (counts grow, already said); add a name-free check before the build.
