task_code: ORA_MANAGE_INDIRECT_TAX_AUTOMATION_WITH_THOMSON_REUTERS
task_name: Manage Indirect Tax Automation with Thomson Reuters
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run (unsafe to test)
route: REST fscm taxPartnerRegistrations (create, get only; VERIFIED describe 2026-11-26); no FSM CSV (task export refused, flag N); thomsonReutersServices, oneSourceIndirectTaxes, taxPartners 404
depends_on: a Thomson Reuters ONESOURCE account of the customer (endpoint, user, password)
test_records: none (not loaded)
notes: Batch 22 (sitting 10). unsafe to test: same route and same reasons as Manage Indirect Tax Automation with Avalara (written, batch 19): a registration needs the customer's real partner account (endpoint, user, password we do not have and must not type), applies to the whole environment so other people's tax calculation would go to the partner, and the resource has no update or delete, so it cannot be put back. Oracle REST docs 26D/25D read: no list of partner names, no partner in the example. What would make it safe: an environment the customer owns, with their Thomson Reuters sandbox account and approval; a person types the password.
