task_code: ORA_ZX_MANAGE_TAX_FORMULAS
task_name: Manage Tax Formulas
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAXES
test_records: GAPFILL_AB_P1_FM1 (live), GAPFILL_AB_P1_FM2F (fresh test); both taxable-basis formulas on test tax GAPFILL_AB_P1_TX1, regime GAPFILL_AB_TR1
notes: Batch 3 part 1. Rows written in full (no formula existed to copy); taxable basis, line amount, GCO owner; no tax or rule points to the formulas. No REST resource (taxFormulasLOV 404); export compare is the proof. Fresh test passed first time with no deviation.
