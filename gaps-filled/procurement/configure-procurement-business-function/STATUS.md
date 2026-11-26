task_code: PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION
task_name: Configure Procurement Business Function
module: Procurement
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 8
minutes_to_test: 7
waiting_minutes: 6
fresh_claude_pass: yes (round F on GAPFILL_AB_B15_BU2F PASS, one wrong sentence 'Step 3 lists them' fixed to Step 1; re-test R on GAPFILL_AB_B15_BU5R PASS, no wrong sentence)
route: FSM CSV: prerequisite Assign Business Unit Business Function (FUN_BU_USAGE, ModuleId 110) + PO_SYSTEM_PARAMETER row for an own prefix business unit; build_csv_package.py / compare_exports.py
depends_on: an own prefix business unit (common-features test-business-unit); FUN_ASSIGN_BUSINESS_UNIT_BUSINESS_FUNCTION (Procurement function 110 on that unit); an existing inventory organization code (value only)
test_records: own unit GAPFILL_AB_B15_BU1: function 110 (ProcessId 100004744439440); config try 1 refused JBO-27014 InventoryOrganizationId (100004744439507, nothing created); config row (100004743463568). Fresh: GAPFILL_AB_B15_BU2F function (100004743465127) + config (100004744437693). Re-test: GAPFILL_AB_B15_BU5R function (100004743464296) + config (100004743463880)
notes: Batch 07 (sitting 4). Re-opened from written (unsafe): the safe way is an own prefix business unit nobody uses (units made in Common Features batch 15). PO_SYSTEM_PARAMETER 14 -> 17 (only the 3 own units added; document types 84, negotiation terms 2 unchanged; read back by AB 01:21). ModuleId 110 = Procurement: VERIFIED as the function every configured procurement unit has, name GUESS (pairs 120 -> 110 in service providers). Settings copied from a working row except unit, inventory org, currency, audit columns. Suggestions NOT applied: say 6 document types per configured real unit; command for 'unit not in list'; note PON_CONTRACTS_TRANSLATION compare needs no --key; print only key columns when inspecting a ZIP. Where it shows: Configure Procurement Business Function page, business unit GAPFILL_AB_B15_BU1.
