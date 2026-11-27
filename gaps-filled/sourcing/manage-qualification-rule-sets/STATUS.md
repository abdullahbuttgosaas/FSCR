task_code: ORA_POQ_MANAGE_SUPPLIER_REG_RULE_SETS
task_name: Manage Supplier Qualification Rule Sets
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-28
minutes_to_write: 7
minutes_to_test: 6
waiting_minutes: 4
fresh_claude_pass: yes (fresh F PASS; no wrong sentence)
route: FSM CSV (rule set package: ORA_POQ_RULE_SETS, _TRANS_RULE_SETS, _RULE_SET_BU_ASSIGNMENTS, _RULE_SET_BU_EVENT_RULES, _RULES, _RULE_AREA_QUESTIONS); no REST resource (3 names HTTP 404)
depends_on: a procurement business unit (own test unit GAPFILL_AB_B15_BU1/BU2F); ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS (own test area); status codes from standard lookup POQ_RULE_SET_STATUS (read live)
test_records: try 1 refused (100004744441515, status DRAFT invalid, nothing created, proved by export); GAPFILL_AB_S3_RS1 on own unit BU1, area QA1 (100004743464733, own test, try 2); GAPFILL_AB_S3_RS2F on own unit BU2F, area QA2F (100004743464790, fresh F (v1.0.0))
notes: Sourcing batch 03 (sitting 2). New INACTIVE rule set with one always-display area rule at registration, translation row US and one BU assignment; event rules (owners, responders = people) left out. Try 1 used RuleSetStatus DRAFT: FND_CMN_INVALID_ATTRB_API_SERV (valid ACTIVE, INACTIVE). Try 2 PASS: export 3 -> 4 rule sets, 6 -> 7 rules and area rows, nothing removed or changed. Skill v1.0.0 corrected before the fresh test: status lookup read from standardLookups (commonLookups returns nothing). Fresh round F PASS with no wrong sentence. Suggestions NOT applied (each would need a re-test): say counts vary; echo rc after export/import; print "build skipped" when the && check fails; say where to record test rule sets.
