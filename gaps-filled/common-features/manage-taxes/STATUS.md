task_code: ZX_MANAGE_TAXES
task_name: Manage Taxes
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 8
minutes_to_test: 9
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAX_REGIMES
test_records: GAPFILL_AB_P1_TX1 (live), GAPFILL_AB_P1_TX2F (fresh test), GAPFILL_AB_P1_TX3R (re-test), all not live; GAPFILL_AB_P1_TX4S (simulation S, made for the statuses attempt 2, read back PASS); regime GAPFILL_AB_TR1 (no subscription)
notes: Batch 3 part 1. Template row from an existing GCO tax that is not live, plus the parent regime rows copied unchanged (copy_parent_rows.py). No REST resource (taxes, taxesLOV 404); export compare is the proof. Fresh test passed only by changing the parent-copy prefix (skill bug); wording fixed (RPREFIX), re-test PASS with no deviation.
