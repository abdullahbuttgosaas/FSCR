# Run 23: pick the gaps to fill

Pod ETIA-TEST. Read-only: GET calls only. Nothing created, changed or deleted in Oracle or in FSCR files.
Date 2026-11-15. Run folder created 15:44, files finished 15:49. The counting work began a few minutes before the folder existed, so the exact start time was not recorded.

**Tags:** VERIFIED = seen in files or the pod · FROM FSCR = FSCR file and line · FROM ORACLE DOCS = link · GUESS = my judgment.

## 1. Tasks per area

| Area | Total | With skill or guide | of which: skill names no CSV/REST route | Route only (no skill, CSV flag Y) | No skill, no route | **No standard route (total)** |
|---|---:|---:|---:|---:|---:|---:|
| ERP | 730 | 79 | 3 | 539 | 112 | **115** |
| SCM | 518 | 249 | 14 | 222 | 47 | **61** |
| HCM | 337 | 289 | 9 | 14 | 34 | **43** |
| CX | 490 | 218 | 11 | 209 | 63 | **74** |
| Other | 541 | 13 | 6 | 389 | 139 | **145** |
| **Total** | **2,616** | **848** | **43** | **1,373** | **395** | **438** |

VERIFIED. Recomputed by `scripts/count.py` from `_fscr_run_07_inventory/out/tasks.csv`. That file was built from the FSCR catalog `knowledge/setup-task-catalog/effective/setupTasksAll.json`. The same table is in `area_counts.csv`.

**How each number was counted**
- **Area:** the pillar of the task's skill. If there is no skill, the pillar of the catalog offerings that contain the task (Run 07 rule). Other = Common 7 + Multiple 233 + Unmapped 81 + No offering 220.
- **With skill or guide:** Skill column is not "none".
- **Skill names no CSV/REST route:** the skill declares neither FSM_CSV nor REST. Its routes are only HDL, ESS, FBDI, manual or none.
- **Route only:** no skill, and the catalog CSV flag is Y.
- **No skill, no route:** no skill, and the CSV flag is N or UNKNOWN.
- **No standard route** = the two "no route" columns added together.

**438 vs 395 (explained, VERIFIED)**
- **395** is Run 07's "No skill, no FSCR route". It counts tasks without a skill only.
- **438** = 395 + 43 skill tasks whose skill names no CSV or REST route. This is the only definition I tried that gives exactly 438.
- 2,616 − 438 = 2,178, which is 83.3%. That matches the "83% have a route" figure.
- No earlier report in `_fscr_run_01` to `_fscr_run_22` states 438. It must have come from a session, not from a saved file. GUESS.
- All other numbers match Run 07: 848, 1,373 and 395, and areas 730 / 518 / 337 / 490.

**Small caveats (GUESS)**
- "Route only" uses the catalog CSV flag. It does not prove that each import works.
- A REST route for tasks without a skill was not scanned.

## 2. ERP and SCM gaps by module

There are 654 ERP gap tasks and 283 SCM gap tasks: tasks with no skill, or a skill with no CSV/REST route. VERIFIED.
- Full list: `gaps_erp_scm.csv`.
- Counts per module: `gaps_by_module.csv`. "Module" is the functional area named in the catalog file `offering-functional-area-task-catalog.json`.

| ERP module | Gaps (no-route ones) | SCM module | Gaps (no-route ones) |
|---|---|---|---|
| General Ledger | 26 (5) | Inventory Management | 32 (0) |
| Expenses | 30 (4) | Orders | 29 (8) |
| Collections | 17 (0) | Shipping | 18 (1) |
| Receivables | 15 (0) | Cost Accounting | 15 (2) |
| Customer Payments | 13 (2) | Approval Management | 13 (13) |
| Fixed Assets | 13 (1) | Purchasing Foundation | 9 (1) |
| Customer Billing | 10 (2) | Supplier Qualification | 11 (1) |
| Intercompany | 11 (1) | Sourcing | 7 (2) |
| Financial Reporting Center | 16 (15) | Maintenance Management | 11 (1) |
| Projects (12 project areas) | 165 (24) | Receiving | 4 (0) |

The largest ERP groups are Public Sector and Joint Venture setups, for example Agency Profile with 43. No Payables (AP_) task falls in the ERP gaps. The AP_ tasks I saw are tagged "Multiple", because they appear in both ERP and SCM offerings, so they count under Other. VERIFIED for the rows I checked.

## 3. The 6 candidates

All 6 have no skill and CSV flag Y (VERIFIED). None is an inventory item or order type.

The route for all 6 is Oracle's FSM setup-task CSV import:
1. Get the template.
2. Fill in only the new FSCRT_ rows.
3. Zip the files.
4. POST `setupTaskCSVImports`.
5. Poll the result.

Sources for this route:
- FROM ORACLE DOCS: [Create a setup task CSV import](https://docs.oracle.com/en/cloud/saas/applications-common/25b/farca/op-fscmrestapi-resources-11.13.18.05-setuptaskcsvimports-post.html) and [Setup Task CSV Template Exports](https://docs.oracle.com/en/cloud/saas/applications-common/26a/farca/api-setup-task-csv-template-exports.html).
- FROM FSCR: `shared/setup-import/fsm-csv-import/SKILL.md:80` has the generic call, but no task fields.

The REST resources found for these tasks allow GET only (VERIFIED from their describe output). They can be used to read back results, not to create.

| # | Area | Task | Plain meaning | Claude would build | Main risk | Difficulty |
|---|---|---|---|---|---|---|
| C1 | ERP | Manage Journal Categories | Labels for journals ("Accrual") | one small CSV; read back with journalCategoriesLOV | categories can't be deleted, so test rows stay (GUESS) | **easy**: one file, few fields |
| C2 | ERP | Manage Standard Memo Lines | Ready-made non-stock invoice lines ("Consulting fee") | CSV with reference set, revenue account, tax; read back with memoLinesLOV | account and reference set must match (GUESS) | **medium**: links to GL accounts and sets |
| C3 | ERP | Manage Statement Cycles | How often customers get statements | header file plus dates file per business unit | business-unit link; no REST read (GUESS) | **medium**: two linked files |
| C4 | SCM | Manage Hazard Classes | Safety groups for dangerous goods | one small CSV | name clash would update a row (GUESS) | **easy**: one file, no links |
| C5 | SCM | Manage Shipping Cost Types | Kinds of shipping charge ("Freight") | one CSV; read back with shippingCostTypesLOV | currency and code values must match (GUESS) | **easy**: one file |
| C6 | SCM | Manage Qualification Areas | Topics for checking a supplier ("Safety") | area, questions and outcomes files; read back with supplierQualificationAreas | needs existing questions; status step (GUESS) | **medium**: several linked files |

Full fields for each candidate (why it is a gap, route and evidence, build, risks, check result) are in `candidates.csv`.

**Risks shared by all 6 (GUESS unless tagged)**
- The import is keyed by name. Always use the FSCRT_ prefix and check first that the name is unused.
- Never import a full exported package. It could rewrite existing rows.
- A revision mismatch stops the import unless SourceTargetDiffOkFlag is Y (FROM ORACLE DOCS).
- Without deletes, test rows stay in the pod.

## 4. Read-only check in ETIA-TEST (VERIFIED)

Script: `scripts/probe.py`. It sends GET only. Results are in `evidence/probe_results*.json` and the per-call JSON files.

- `setupTaskCSVImports`, `setupTaskCSVExports` and `setupTaskCSVTemplateExports` all return 200.
- For each of the 6 tasks (and the spare, Cost Elements), `setupTaskCSVImports/{TaskCode}` returns ImportSupportedFlag = true, and `setupTaskCSVExports/{TaskCode}` returns ExportSupportedFlag = true.
- Data read checks:
  - journalCategoriesLOV: 200, and no FSCRT_ rows.
  - memoLinesLOV: 200.
  - shippingCostTypesLOV: 200, 0 rows visible.
  - supplierQualificationAreas: 200, 0 rows visible.
- These return 404, so read-back for those tasks needs a CSV export: statementCyclesLOV, hazardClasses, hazardClassesLOV, costElements, collectorsLOV, standardMemoLinesLOV, shippingCostTypes.
- Setup pages in the browser UI were not opened. Reachability was checked through REST only.

**Spare candidate:** Manage Cost Elements (SCM, CST_MANAGE_COST_ELEMENTS). Import and export are supported (VERIFIED). Medium (GUESS).

## 5. Sign-in and clean-up
- **Sign-in:** the FSCR login script (Run 08 copy) on port 8765. It finished on its own and the listener exited. The token was not printed. `login_23.log` has the state and challenge values redacted.
- **After the run:** port 8765 is free and no process started by this run is still running. VERIFIED with netstat.
