task_code: GL_SELECT_AGGREGATION_OPTIONS_FOR_ACCOUNT_HIERARCHIES
task_name: Publish Account Hierarchies
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 0
waiting_minutes: 3
fresh_claude_pass: not run (unsafe to test)
route: FSM CSV export works but is the trees package (5 files, no publish or aggregation column); publish = scheduled process (erpintegrations submitESSJobRequest, job path not published); REST accountHierarchies, publishAccountHierarchies, treeVersions, accountHierarchyPublications 404
depends_on: FND_MANAGE_TREES_AND_TREE_VERSIONS (tree with an active version); a chart of accounts with a balances cube
test_records: none (not loaded)
notes: Batch 23 (sitting 10). unsafe to test: publishing writes the hierarchy into the shared GL balances cubes of every chart of accounts that uses the tree's value set, and there is no unpublish by CSV or REST, so it cannot be put back; a new prefix tree does not help because the cube is shared. Own trees GAPFILL_AB_B7_AH1/AH2F exist on GL_ACCT_FLEX. Creating trees through this package is already covered by manage-trees-and-tree-versions (tested). What would make it safe: an environment with its own test chart of accounts and ledger, with written approval.
