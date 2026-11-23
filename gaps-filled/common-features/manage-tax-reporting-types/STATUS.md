task_code: ZX_MANAGE_TAX_REPORTING_TYPES
task_name: Manage Tax Reporting Types
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAX_REGIMES
test_records: GAPFILL_AB_RT1 (code GAPFILL_AB_C1); GAPFILL_AB_RT2F (code GAPFILL_AB_C2F); both on regime GAPFILL_AB_TR1
notes: Batch 2 part 3. New regime-level TEXT reporting type + 1 code + translations on a test regime; no usage, no association. No REST resource; export compare is the read-back. Live import 1 failed (ZX_MIN_LENGTH_VALUE, MinLength needed), import 2 passed. Fresh test PASS; no wording change after it.
