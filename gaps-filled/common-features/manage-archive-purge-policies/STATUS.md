task_code: ORA_MANAGE_FINANCIALS_BUSINESS_OBJECTS_ARCHIVE
task_name: Manage Archive and Purge Policies
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: not run (unsafe to test)
route: FSM CSV (ORA_ARCHIVE_AND_PURGE_POLICY + _DETAIL); read steps VERIFIED, ledger-level row GUESS
depends_on: a real ledger and balancing segment value
test_records: none created; try 1 detail row with test LE only refused JBO-27014 LedgerId / BalancingSegmentValue required (100004743458273); export after: 0 detail rows
notes: Batch 17 (sitting 7). unsafe to test: the policy file has one global row per business object (ORA_ACCOUNTING_DATA 99/98 years, a change hits every ledger); a detail row must name a real ledger and balancing segment value and sets when that ledger's accounting data may be purged; no test ledger exists and there is no delete by CSV. Next step: load-test only on an environment we own, with the finance owner's approval. Re-judged 2026-11-26 (sitting 8): still unsafe: a detail row needs a real ledger and balancing segment value (no test ledger can be made by this task), and the global row is shared; no delete by CSV, so no test-and-restore.
