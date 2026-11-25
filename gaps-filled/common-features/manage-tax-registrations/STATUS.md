task_code: ORA_ZX_MANAGE_TAX_REGISTRATIONS
task_name: Manage Tax Registrations
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 7
minutes_to_test: 7
waiting_minutes: 3
fresh_claude_pass: yes (re-test R after a wording fix)
route: REST taxRegistrations POST (third-party profile) through FSCR's REST client via the GoSaaS wrapper scripts/rest_call.py; the FSM CSV package holds first-party files only (out of scope)
depends_on: a test customer with a THIRD_PARTY party tax profile (manage-tax-exemptions Step 1); ZX_MANAGE_TAX_REGIMES (a test regime)
test_records: GAPFILL_AB_B9_TRG1 (refused ZX-885657, not created); GAPFILL_AB_B9_TRG2 (customer GAPFILL_AB_B4FIX_CUST1, regime GAPFILL_AB_TR3R); fresh GAPFILL_AB_B9_TRG3F (CUST2F); re-test GAPFILL_AB_B9_TRG4R on new test customer GAPFILL_AB_B9_CUST3R (+ its THIRD_PARTY profile)
notes: Batch 09. Try 1 on a GB test regime refused: number must start with GB (ZX-885657). US test regime: created. Fresh test: record created but the read-back filter 'q=A and B' returns 0 rows on this resource; fixed to ';' (also in the duplicate check), log check changed to grep HTTP; re-test PASS (it also made its own customer + profile). Suggestions not applied: point to Steps 1b/1c of manage-tax-exemptions; fields= on the profile GET.
