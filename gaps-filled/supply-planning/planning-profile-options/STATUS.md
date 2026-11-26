task_code: ORA_MSC_MANAGE_PLANNING_PROFILE_OPTIONS
task_name: Manage Planning Profile Options
module: Supply Planning
status: tested
filled_by: IR
date: 24/11/2026
minutes_to_write: 18
minutes_to_test: 9
waiting_minutes: 9
fresh_claude_pass: yes (POF, POR, POR2, POR3, POR4 all passed; final retest POR4 after the last wording fix)
route: FSM CSV (task-level export, new-rows-only package, task-level import)
depends_on: none
test_records: FSCRT_IR_GF_PO1, FSCRT_IR_GF_POF, FSCRT_IR_GF_POR, FSCRT_IR_GF_POR2, FSCRT_IR_GF_POR3, FSCRT_IR_GF_POR4
notes: Creates a new custom profile option (definition, 3 levels, site value); never touches predefined options. Import ProcessIds in CHANGELOG.md. Helper scripts in ../scripts. Minutes are approximate (writing shared with the attachment-categories skill).
