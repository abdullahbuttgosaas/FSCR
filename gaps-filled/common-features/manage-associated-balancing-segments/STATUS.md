task_code: XLE_MANAGE_ASSOCIATED_BALANCING_SEGMENTS
task_name: Manage Associated Balancing Segments
module: Common Features
status: written
filled_by: AB
date: 2026-11-27
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 0
fresh_claude_pass: not run (unsafe to test)
route: rapid implementation workbook Create Chart of Accounts, Ledger, Legal Entities, and Business Units in Spreadsheet (legal entity sheet with balancing segment values), two uploads (Oracle docs); FSM CSV = legal entity package, no balancing segment column (VERIFIED); REST legalEntitiesLOV get only, legalEntityBalancingSegmentValues 404
depends_on: a ledger with the legal entity assigned (primary ledger configuration)
test_records: none (not loaded)
notes: Batch 24 (sitting 11). unsafe to test: the only file route builds or changes a whole ledger setup (chart, calendar, ledger, legal entities), none of which can be deleted; a link on a real ledger changes how its journals balance; a prefix legal entity alone is not enough because the link needs a ledger, and a new ledger is permanent and shared. What would make it safe: a new test-only environment with written approval.
