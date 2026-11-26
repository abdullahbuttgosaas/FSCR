task_code: FND_MANAGE_APPLCORE_DESCRIPTIVE_FLEXFIELDS
task_name: Manage Applications Core Descriptive Flexfields
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 8
waiting_minutes: 4
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (FND_APP_DESCRIPTIVE_FLEXFIELD package): new disabled context + one segment, parent row unchanged; builder scripts/dff_context_package.py
depends_on: none
test_records: FND_ATTACHED_DOCUMENTS: GAPFILL_AB_B16_CTX1 + SEG1 (100004744435230); fresh CTX2F + SEG2F (100004744434847); re-test CTX3R + SEG3R (100004744433960)
notes: Batch 16 (sitting 7). New DISABLED context with one text segment on the attachments flexfield; no deploy needed or run (DEPLOYED before and after). Own test PASS (contexts and segments +1 each, nothing else changed). Fresh test PASS, wording fixed, re-test PASS. Builder and check_dff_rows.py reused by the LE configurator and note DFF cards.
