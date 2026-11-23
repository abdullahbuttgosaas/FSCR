task_code: ZX_MANAGE_TAX_CONDITION_SETS
task_name: Manage Tax Condition Sets
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 9
minutes_to_test: 6
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS
test_records: GAPFILL_AB_P2_CS1 (live, STATE = NY), GAPFILL_AB_P2_CS2F (fresh test, STATE = CA); both on factor set GAPFILL_AB_FS1, no rule uses them
notes: Batch 3 part 2. Rows written in full (header + condition + translation); the test factor set has only a GEOGRAPHY/BILL_FROM/STATE line, so the state is given by its name (2-letter code here) and Oracle resolves the geography ID itself; internal-ID columns left empty. No REST resource searched; export compare is the proof. Fresh test PASS (one export retry after a network drop, allowed by the skill); notes not applied.
