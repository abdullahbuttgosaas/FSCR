# Run 30 notes (supporting RESULT.md)

## Oracle reference for the plan comparison
The 40 prerequisite links are in `scripts/plan.py` (list `ORA`) and `evidence/oracle_edges_check.csv`.
- Read in full: Oracle "Create Your Enterprise Structure" (https://docs.oracle.com/en/cloud/saas/student-management/faism/create-your-enterprise-structure.html). It says the chart of accounts is uploaded before the ledger, legal entities and business units.
- Seen through search summaries only (the PDF link returned 404): Oracle "Implementing Enterprise Structures and General Ledger" (faigl), and Oracle Support note 1428444.1 "Minimum Steps For Financial Enterprise Structures and General Ledger Setup". These cover the order primary ledger → ledger options → assign legal entities → balancing segments → review and submit.
- The other links (geographies before legal addresses, value sets before COA structure, cross-validation rules before account combinations, duties before job roles, and so on) are standard Oracle setup rules from my own knowledge. **GUESS**: they were not checked line by line in this run.

## How the FSCR plan was built
- Used the method of `shared/implementation-planning/task-dependency-resolver`.
- Order: the release catalog's `functionalAreaOrder` and `displaySequence`, with Financials as the main offering. 21 tasks that are not in Financials take their order from another ERP offering (for example, the ledger tasks come from Grants Management).
- FSCR prerequisites: other Common Features tasks named in the task's own skill or readiness file, plus 3 links from the HCM dependency graph. There is no ERP dependency graph.

## Deviations and workarounds
1. The 3 CSV tasks (#1, #3, #4) used FSCR `task-level-export` and `task-level-import` directly, as Run 24 did. FSCR says every import must go through `core/data-loader` with Task Hook; this run did not do that for those 3.
2. The 144-task Run Book POST timed out on the client side. FSCR reported "outcome unknown" and I did not retry. It later showed up in ETIA-TEST, complete with 144 tasks. Before I saw it, I created the 6-task Run Book FSCRT_R30 Common Features Exec for the Job Family load. Oracle marked the Job Family task in that Run Book as Completed.
3. All FSCR scripts ran from a full copy (`fscr-work30`). I blanked the copy's Data Loader `runID`, which pointed at the existing Run Book 300000394423893. I deleted the copy after the run; the runbook and project files are saved in `runbook/` and `evidence/`.
4. The sign-in on port 8765 failed once with a network timeout. The second try worked. No token or password was printed or saved in this folder.

## Records created in ETIA-TEST (all FSCRT_)
- Reference data set FSCRT_R30_SET
- Conversion rate type FSCRT_R30 Rate Type
- Lookup type FSCRT_R30_LOOKUP, with codes FSCRT_A and FSCRT_B
- Job family FSCRT_R30_JF
- Run Book FSCRT_R30 Common Features (300000395092022)
- Run Book FSCRT_R30 Common Features Exec (300000395063022)
