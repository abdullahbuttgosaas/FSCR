task_code: ORA_MANAGE_ONBOARDING_FOR_AVALARA
task_name: Manage Indirect Tax Automation with Avalara
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 7
minutes_to_test: 3
waiting_minutes: 3
fresh_claude_pass: not run (unsafe to test)
route: REST fscm taxPartnerRegistrations (create only, describe VERIFIED 2026-11-26); no FSM CSV (export refused, task flag N)
depends_on: the customer's Avalara account for the environment
test_records: none (read-only checks: export refused, describe, GET HTTP 500 = GET not supported)
notes: Batch 19 (sitting 8). Not screen-only: a REST route exists (taxPartnerRegistrations, create). unsafe to test: it needs a real Avalara account (endpoint, user, password we do not have and must not type), it registers the tax partner for the whole environment so other people's transactions would go to it, and the resource has no delete or update, so it cannot be put back. Next step: run only on an environment the customer owns, with their Avalara sandbox account and approval; a person types the password. Finding for a later sitting (not changed here): ORA_MANAGE_INDIRECT_TAX_AUTOMATION_WITH_THOMSON_REUTERS is screen-only in screen-only.csv, but the same resource may serve Thomson Reuters; re-judge it.
