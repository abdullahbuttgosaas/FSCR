task_code: ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES
task_name: Manage Tax Rates and Tax Recovery Rates
module: Common Features
status: failed
filled_by: AB
date: 2026-11-24
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: no
route: FSM CSV
depends_on: ZX_MANAGE_TAX_STATUSES
test_records: none (no import made)
notes: Batch 3 part 2. Blocked by ZX_MANAGE_TAX_STATUSES: a rate needs a tax status and no status could be created on a test tax (batch 3 part 1). Read-only export checked (32 files, 4 statuses, 5 percentage rates, none on a GAPFILL_ tax). No import tried; a rate on a real status would change real setup.
