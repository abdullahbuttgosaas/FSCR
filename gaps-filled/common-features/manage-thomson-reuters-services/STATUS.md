task_code: ORA_MANAGE_THOMSON_REUTERS_SERVICES
task_name: Manage Thomson Reuters Services
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run (unsafe to test)
route: REST fscm taxPartnerRegistrations (create, get only; VERIFIED describe 2026-11-26); no FSM CSV (task export refused, flag N); thomsonReutersServices 404
depends_on: a Thomson Reuters ONESOURCE account of the customer (endpoint, user, password)
test_records: none (not loaded)
notes: Batch 22 (sitting 10). unsafe to test: the services connection is the tax partner registration (taxPartnerRegistrations): it needs the customer's real Thomson Reuters account (credentials an agent must not type), applies to the whole environment, and has no update or delete, so it cannot be put back. Same judgement as Avalara onboarding (batch 19). What would make it safe: an owned environment with the customer's sandbox account and approval.
