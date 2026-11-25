task_code: PJB_MANAGE_REVENUE_METHOD_BILLING_EXTENSION_ASSIGNMENTS
task_name: Manage Revenue Methods: Billing Extension Assignments
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV (same 3 files as the invoice-method task, BillMethodFlag R: a NEW revenue method with its assignment); export compare read-back
depends_on: PJB_MANAGE_BILLING_EXTENSIONS (a test extension with CallingProcess R: GAPFILL_AB_B10_BX3F); skill manage-invoice-method-billing-ext-assignments (steps)
test_records: GAPFILL_AB_B12_RM1 (100004744396782); fresh GAPFILL_AB_B12_RM2F (100004743428028)
notes: Batch 12. Pointer skill to the invoice-method skill with R values. Try 1 PASS (first after-export lost to a network drop, re-run into a new folder). Fresh test PASS.
