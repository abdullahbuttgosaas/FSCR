task_code: ORA_PO_COMPLIANCE_CHECKLIST_TEMPLATES
task_name: Manage Compliance Checklist Templates
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 10
waiting_minutes: 7
fresh_claude_pass: yes (no wrong sentence)
route: FSM CSV (ORA_POQ_CHECKLIST_TEMPLATE + template sections)
depends_on: an active checklist section (ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS)
test_records: GAPFILL_AB_B3_CT1 failed JBO-56012 (100004744396548); CT2 (100004744396561) and CT4 (100004744393701) log success but invisible (usage ORA_CHECKLIST; left in Oracle, not visible in export or REST); CT3 failed JBO-56012 (100004744396574); GAPFILL_AB_B3_CT5 with section CS3 (100004744396588); fresh GAPFILL_AB_B3_CT6F (100004744393751)
notes: Batch 03. Two traps found: template usage must be CHECKLIST (ORA_CHECKLIST gives a 'successful' but invisible template) and the section row needs ObjectVersionNumber1=1 (else SQLException JBO-26048). REST supplierQualificationModels shows only qualification models: the export is the read-back. Own + fresh compare PASS. Suggestions NOT applied: 'started with 0 rows' out of date; add a name-free check.
