task_code: ZX_MANAGE_TAX_JURISDICTIONS
task_name: Manage Tax Jurisdictions
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 12
minutes_to_test: 11
waiting_minutes: 7
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAXES
test_records: GAPFILL_AB_P2_JR1 (live, NY, precedence 300), GAPFILL_AB_P2_JR2F (fresh test, CA, 310), GAPFILL_AB_P2_JR3R (re-test, GA, 320); all on test tax GAPFILL_AB_P1_TX1 (not live), regime GAPFILL_AB_TR1
notes: Batch 3 part 2. Rows written in full; geography by name in the style of existing jurisdictions (US state as 2-letter code, no GeographyCode). The jurisdictions export lists no jurisdictions, so the read-back is a taxes export compare (ORA_ZX_TRAN_TAX_JURISDICTION). Live test needed 3 attempts (geography style). Fresh test passed only by guessing a unique precedence level (skill bug); wording fixed (precedence unique per tax), re-test PASS with no deviation.
