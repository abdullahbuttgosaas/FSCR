task_code: PJB_MANAGE_BILLING_EXTENSIONS
task_name: Manage Billing Extensions
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes
route: FSM CSV (PJB_BILLING_EXTENSIONS, row written in full); export read-back (REST billingExtensions 404)
depends_on: none (lookup PJB_BILL_EXT_CALL_PROCESS read live)
test_records: GAPFILL_AB_B10_BX1 (refused PJB_BILL_EXT_PROC_INVALID, 100004743405841, not created); GAPFILL_AB_B10_BX2 (100004743406265); fresh GAPFILL_AB_B10_BX3F (100004744392322)
notes: Batch 10. Empty export (0 rows): row written in full. CallingProcess takes the lookup code I/R, not the meaning (try 1 refused). Procedure name is not checked when saving. New definitions are not assigned to any method, so they change nothing. Fresh test PASS (Revenue).
