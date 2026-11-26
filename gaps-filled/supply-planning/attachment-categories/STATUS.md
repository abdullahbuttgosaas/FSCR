task_code: ORA_DOS_MANAGE_SUPPLY_ORCHESTRATION_ATTACHMENT_CATEGORIES
task_name: Manage Supply Orchestration Attachment Categories
module: Supply Planning
status: tested
filled_by: IR
date: 24/11/2026
minutes_to_write: 22
minutes_to_test: 10
waiting_minutes: 11
fresh_claude_pass: yes (final retest ACR5 passed with no errors; ACF, ACR, ACR3, ACR4 passed; ACR2 failed on a reused display name, which led to the unique-name rule)
route: FSM CSV (task-level export, new-rows-only package, task-level import) plus one REST GET for the ModuleId
depends_on: none
test_records: FSCRT_IR_GF_AC1, FSCRT_IR_GF_ACF, FSCRT_IR_GF_ACR, FSCRT_IR_GF_ACR3, FSCRT_IR_GF_ACR4, FSCRT_IR_GF_ACR5 (ACR2 not created)
notes: Display name must be unique (Oracle FND_CORE_RCRD_VAL). Code at most 21 characters. Import ProcessIds in CHANGELOG.md. Helper scripts in ../scripts. Minutes are approximate (writing shared with the profile-options skill).
