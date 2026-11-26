task_code: OKC_SPECIFY_PROCUREMENT_CONTRACT_MGMT_BUSINESS_FUNC_PROP
task_name: Specify Supplier Contract Management Business Function Properties
module: Procurement
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 6
minutes_to_test: 6
waiting_minutes: 4
fresh_claude_pass: yes (GAPFILL_AB_B15_BU2F, ProcessId 100004743464382, compare PASS, no wrong sentence)
route: FSM CSV (OKC_BU_IMPL_OPTIONS) for an own prefix business unit; unit id read live by REST finBusinessUnitsLOV; build_csv_package.py / compare_exports.py
depends_on: an own prefix business unit with the Procurement business function (configure-procurement-business-function Prerequisite 2)
test_records: own GAPFILL_AB_B15_BU1: try 1 100004744437661 refused OKC_BUSET_MIGINVALID_DATA (related customer accounts); try 2 100004743463605 refused OKC_BUSET_GLOBALBUEXISTS; try 3 100004743465019 refused JBO-27014 DefaultCurrencyCode required (LedgerYn Y, unit has no ledger); try 4 100004743463626 created. Fresh GAPFILL_AB_B15_BU2F (100004743464382)
notes: Batch 07 (sitting 4). Re-opened from written (unsafe): the safe way is an own prefix business unit. Failure protocol: each try had a written diagnosis and changed one thing (full template settings; GlobalBusUnitYn N; LedgerYn N); refused tries created nothing (export after try 3: still 1 row). Read back by AB 01:25: OKC_BU_IMPL_OPTIONS 1 -> 3 (only BU1 and BU2F added). Suggestions NOT applied: Prerequisite 2 pointer says 'skip to Step 1' of the other skill (should say go back to Prerequisite 3); advise an own prefix unit as TPL. Where it shows: Specify Supplier Contract Management Business Function Properties page, business unit GAPFILL_AB_B15_BU1.
