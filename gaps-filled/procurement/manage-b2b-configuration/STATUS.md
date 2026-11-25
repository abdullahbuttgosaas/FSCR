task_code: ORA_CMK_MANAGE_B2B_CONFIG
task_name: Manage B2B Configuration
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 5
waiting_minutes: 3
fresh_claude_pass: yes (no wrong sentence)
route: REST b2bServiceProviders + b2bTradingPartners (POST, GET by id)
depends_on: none (own test service provider)
test_records: GAPFILL_AB_B4_TP1 refused HTTP 400 (no ServiceProviderId, not created); service provider GAPFILL_AB_B4_SP1 + trading partner GAPFILL_AB_B4_TP2; fresh: service provider GAPFILL_AB_B4_SP2F + trading partner GAPFILL_AB_B4_TP3F, READBACK PASS
notes: Batch 04. No FSM CSV (catalog N); REST route. A partner needs a ServiceProviderId; the skill creates its own test provider so no real network is touched. Read back by id: PASS. Suggestions NOT applied: say shell variables are fine inside one call; wrap REST calls in a timeout.
