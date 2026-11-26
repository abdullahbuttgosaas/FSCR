task_code: ORA_JE_MANAGE_TAX_BOX_ALLOCATION_RULES
task_name: Manage Tax Box Allocation Rules
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 10
minutes_to_test: 8
waiting_minutes: 8
fresh_claude_pass: yes (fresh F failed on a skill gap: rule order already used, nothing created; rule-order step added; R PASS with no wrong sentence)
route: FSM CSV (task package = tax rules package): header ZX_TAX_RULE_SUPERTYPE with ServiceTypeCode DET_TAX_BOX, ReportingTypeCode, PeriodicityCode; translation; result ResultTypeCode CODE with AlphanumericResult = box; result detail ORA_TAX_RULE_RESULT_DETAILS
depends_on: ZX_MANAGE_TAX_REGIMES (own regime with GCO option row), ZX_MANAGE_TAXES (own tax), ZX_MANAGE_TAX_REPORTING_TYPES (own reporting type with a code), ZX_MANAGE_TAX_RULES (own template rule, factor set, condition set)
test_records: GAPFILL_AB_B22_TB1 (try 1 ProcessId 100004743462568: header and translation, result refused ZX_REQUIRED_VALUE AlphanumericResult; try 2 ProcessId 100004744438453: result and detail under the unchanged own header); fresh GAPFILL_AB_B22_TB2F refused ZX_RULES_ORDER_EXISTS_GCO_OWN (ProcessId 100004744437367, nothing created); R GAPFILL_AB_B22_TB3R priority 20 (ProcessId 100004744437528). All disabled, on own regime GAPFILL_AB_TR1 / tax GAPFILL_AB_P1_TX1, reporting type GAPFILL_AB_RT1, box GAPFILL_AB_C1, PERIODIC
notes: Batch 22 (sitting 10). Was written-untested (batch 21: no template rule, codes GUESS). Codes read live: rule type DET_TAX_BOX (export scope), periodicity PERIODIC/ANNUAL (lookup ZX_RULE_PERIODICITY), result type CODE (lookup ZX_RESULT_TYPES). Own test compare PASS (4 rows added, 0 changed). Fresh test found that the header Priority (rule order) must be unused among DET_TAX_BOX rules on the same regime and tax: step added (v0.2.1); R re-test PASS (4 added, 0 changed). Tester suggestions not applied: take FROM from the template, say the Tax Rule Condition In progress line can be ignored, filter the Step 2 list by prefix.
