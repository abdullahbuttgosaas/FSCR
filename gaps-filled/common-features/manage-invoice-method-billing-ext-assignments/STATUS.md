task_code: PJB_MANAGE_INVOICE_METHOD_BILLING_EXTENSION_ASSIGNMENTS
task_name: Manage Invoice Methods: Billing Extension Assignments
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 7
minutes_to_test: 9
waiting_minutes: 4
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (ORA_PJB_BILLING_METHOD + _TRANSLATION + ORA_PJB_BILLING_ASSIGNMENTS, rows written in full: a NEW extension-based invoice method with its assignment); export compare read-back (no REST resource found)
depends_on: PJB_MANAGE_BILLING_EXTENSIONS (a test extension with CallingProcess I: GAPFILL_AB_B10_BX2)
test_records: GAPFILL_AB_B12_IM1 (refused: ProcessingOrder must be blank; 100004744403991; connection dropped, log fetched by ProcessId; not created); GAPFILL_AB_B12_IM2 (100004744404076); fresh GAPFILL_AB_B12_IM3F (100004744396826); re-test GAPFILL_AB_B12_IM4R (100004743426123)
notes: Batch 12. Safe way: a NEW prefix method (nothing uses it) instead of an assignment on an existing method. Export had 0 methods before. Try 1 refused 'You must leave the Processing Order attribute blank'; try 2 PASS (3 files, 1 added each). Oracle sets MethodCfgType EXTENSION_BASED and TransactionCode BILLING_EVENT; AsmFlag shows empty. Fresh test PASS; wording fixed (drop sign = no process log; AsmFlag note; extension check one-liner; row count history); re-test PASS.
