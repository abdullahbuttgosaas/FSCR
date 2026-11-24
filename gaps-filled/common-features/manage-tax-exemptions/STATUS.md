task_code: ORA_ZX_MANAGE_TAX_EXEMPTIONS
task_name: Manage Tax Exemptions
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 12
minutes_to_test: 9
waiting_minutes: 7
fresh_claude_pass: yes
route: FSM CSV (prerequisite customer and third-party tax profile by REST)
depends_on: Step 1: a test customer (CRM REST accounts POST, Type ZCA_CUSTOMER) with a THIRD_PARTY party tax profile (REST partyTaxProfiles POST); ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES (test rate on a not live tax)
test_records: customer GAPFILL_AB_B4FIX_CUST1 + its THIRD_PARTY tax profile + exemption GAPFILL_AB_B4FIX_EXM1 (live); customer GAPFILL_AB_B4FIX_CUST2F + profile + exemption GAPFILL_AB_B4FIX_EXM2F (fresh test); 10 % discounts on the not live test tax GAPFILL_AB_P1_TX1
notes: Batch 4 part 3 failed (JBO-27014 PartyTaxProfileId required: exemptions need a customer third-party profile). Batch 4 fix: customer and profile made by REST through FSCR's client (GET first, POST only if missing); exemption imported first try; export compare + REST read-back PASS. Fresh test PASS (import connection dropped after start; not re-imported; record proved by export and REST). Tester notes not applied.
