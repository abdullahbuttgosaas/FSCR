task_code: ZX_MANAGE_TAX_GEOGRAPHIES
task_name: Manage Tax Geographies
module: Common Features
status: written
filled_by: AB
date: 2026-11-27
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 0
fresh_claude_pass: not run (unsafe to test)
route: no own object: view of the shared master geography; write route = Import Management GeographyInterface (see load-geography-interface-data); crm geographies get only (countries only, VERIFIED); taxGeographies 404; FSM CSV refused (flag N)
depends_on: HZ_LOAD_GEOGRAPHY_INTERFACE_DATA (same route)
test_records: none (not loaded)
notes: Batch 24 (sitting 11). unsafe to test: there is no new prefix record to make; the task changes how existing countries' geography types are used for tax, which every real legal entity, business unit, tax jurisdiction and address validation in that country reads, with no undo by CSV or REST. What would make it safe: a customer-owned environment, written approval, a country they do not trade in.
