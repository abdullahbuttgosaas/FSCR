# FSCR Run 18: best setup for a change-impact test (read only)

Pod **ETIA-TEST**, 2026-11-09. Nothing was created, changed or deleted in Oracle. The 9 FSM exports each left one export-process record, which is how FSM export works (a read route). No sign-in was needed: FSCR's saved sign-in from Run 17 was still valid, so no listener and no browser were started.

## Answer

**Use business units.** A business unit is set up once, and many other setups in many modules point to it. FSCR exports it with its own FSM route, and the export works: 186 business units, plus their business functions, service providers and set assignments in the same file. In ETIA-TEST, other setup really points to business units:
- 92 BUs point to a ledger and a legal entity;
- 1,093 business-function rows (19 modules);
- 273 service-provider rows;
- 8,567 set-assignment rows;
- 55 price lists;
- 350 data-access grants;
- 19 Receivables system-option rows.

The best test example is BU **ABD**, which has 7 kinds of links. Reference data sets, currencies, ledgers and legal entities came close (9 of 10 each), but each lost a point (see step 4). FSCR still has no step that finds what points to a record, so Claude does the impact part.

## Step 1: Candidates (13)

| # | Candidate | Module | Task code | Where it came from |
|---|---|---|---|---|
| 1 | Receivables payment terms | Receivables | AR_MANAGE_RECEIVABLES_PAYMENT_TERMS | catalog + skill |
| 2 | Payables payment terms | Payables | AP_MANAGE_PAYMENT_TERMS | catalog + skill |
| 3 | Business units | Enterprise structure | FUN_MANAGE_BUSINESS_UNIT | catalog + skill |
| 4 | Reference data sets | Enterprise structure | FND_MANAGE_REFERENCE_DATA_SETS | catalog + skill |
| 5 | Legal entities | Legal structure | XLE_MANAGE_LEGAL_ENTITY | catalog + skill |
| 6 | Primary ledgers | General Ledger | GL_MANAGE_PRIMARY_LEDGERS | catalog + skill |
| 7 | Accounting calendars | General Ledger | GL_MANAGE_ACCOUNTING_CALENDARS | catalog + skill |
| 8 | Units of measure | Product management | INV_MANAGE_UNITS_OF_MEASURE | catalog + skill |
| 9 | Currencies | Common setup | FND_MANAGE_CURRENCIES | catalog + skill |
| 10 | Conversion rate types | General Ledger | GL_MANAGE_CONVERSION_RATE_TYPES | catalog only |
| 11 | Tax regimes | Tax | ZX_MANAGE_TAX_REGIMES | catalog only |
| 12 | Carriers | Shipping | WSH_MANAGE_CARRIERS | catalog + skill |
| 13 | Customer profile classes | Receivables | AR_MANAGE_RECEIVABLES_CUSTOMER_PROFILE_CLASSES | catalog only |

Catalog: `fscr-main/knowledge/setup-task-catalog/effective/setupTasksAll.json`. Inventory organizations and order types were left out, as asked.

## Step 2: Quick screen (FSCR files only)

The "Named in" column counts how many FSCR dependency files (`ora_dependency_readiness.md`) mention the candidate, and in how many areas. It is a rough sign of how much depends on it: some matches are just mentions. Full lists are in `evidence/quick_screen.json`.

| Candidate | Export route (catalog flags: export / CSV) | Skill file | Named in |
|---|---|---|---|
| AR payment terms | FSM CSV (Y/Y) | `pillars/erp/financials/customer-billing/manage-receivables-payment-terms/SKILL.md` | 4 files, 1 area |
| AP payment terms | FSM CSV (Y/Y) | `pillars/erp/financials/payables/manage-payment-terms/SKILL.md` | 4 files, 1 area |
| **Business units** | FSM CSV (Y/Y) | `pillars/erp/financials/organization-structures/manage-business-unit.md` (readiness: `.../organization-structures/ora-resource/ora_dependency_readiness.md`) | **35 files, 10 areas** |
| **Reference data sets** | FSM CSV (Y/Y) | `pillars/hcm/goal-management/goal-management-common/manage-reference-data-sets/SKILL.md` | **66 files, 14 areas** |
| Legal entities | FSM CSV (Y/Y) | `pillars/erp/financials/legal-structures/manage-legal-entity/SKILL.md` | 18 files, 6 areas |
| Primary ledgers | FSM CSV (Y/Y) | `pillars/erp/financials/general-ledger/manage-primary-ledgers/SKILL.md` | 28 files, 4 areas |
| Accounting calendars | FSM CSV (Y/Y) | `pillars/erp/financials/financial-reporting-structures/manage-accounting-calendars/SKILL.md` | 4 files, 3 areas |
| Units of measure | FSM CSV (Y/Y) | `pillars/scm/product-management/items/manage-units-of-measure/SKILL.md` | 11 files, 4 areas |
| **Currencies** | FSM CSV (Y/Y) | `pillars/hcm/goal-management/goal-management-common/manage-currencies/SKILL.md` | **40 files, 12 areas** |
| Conversion rate types | FSM CSV (Y/Y) | **no skill found** | 2 files, 1 area |
| Tax regimes | FSM CSV (Y/Y) | **no skill found** | 0 |
| Carriers | FSM CSV (Y/Y) | `pillars/scm/manufacturing-and-supply-chain-materials-management/carriers-and-transit-times/manage-carriers/SKILL.md` | 12 files, 4 areas (several are loose matches) |
| Customer profile classes | FSM CSV (Y/Y) | **no skill found** | 1 file, 1 area |

The top 3 by FSCR files are **reference data sets, currencies and business units**. FSCR's only dependency graph, `knowledge/dependency-graphs/hcm-dependency-graph.json`, covers HCM only.

## Step 3: Deep check on the top 3

### a) Real exports (FSCR task-level FSM CSV export)

| Subject | Sheet | Rows | Columns |
|---|---|---|---|
| Business units | `business_units_ETIA-TEST.xlsx` | 186 | 28: Name, DefaultSetCode, PrimaryLedgerName, OrganizationCode, LegalEntityName, InternalLocationCode, Status, ManagerListName, FinancialBUShortCode, DefaultCurrencyCode, Classification, ProfitCenterFlag, effective dates, audit and manager-name fields |
| Reference data sets | `reference_data_sets_ETIA-TEST.xlsx` | 37 (REST shows 39) | 8: SetCode, SetName, Description, audit fields |
| Currencies | `currencies_ETIA-TEST.xlsx` | **9 only** (REST shows 268) | 22: CurrencyCode, Name, EnabledFlag, StartDateActive, EndDateActive, Precision, and more |

The currency export seems to hold only added or changed currencies, so it does not give a full picture. This was not confirmed.

### b) Live links in ETIA-TEST (all VERIFIED IN ENVIRONMENT)

| Subject | What points to it | Count | Source |
|---|---|---|---|
| Business units | BUs with a primary ledger / a default legal entity | 92 / 92 of 186 | BU export |
| | Business functions turned on (FUN_BU_USAGE) | 1,093 rows, 19 modules | BU export |
| | Service-provider links (client or provider BU) | 273 rows | BU export |
| | Set assignments (which set each setup type uses) | 8,567 rows for 126 BUs | BU export; REST setIdAssignmentsBusinessUnit (8,580) |
| | Price lists | 55, across 21 BUs | REST priceLists |
| | User data-access grants by BU | 350 | REST dataSecurities |
| | Receivables system options | 19 BUs | AR system options export |
| | Receivables transaction-type BU rows | 3 | AR transaction types export |
| Reference data sets | Set-assignment rows / setup types that use sets | 8,580 / 81 | REST setIdAssignmentsBusinessUnit |
| | COMMON set alone | 5,980 rows, 89 BUs | same |
| | BUs whose default set is a set | 186 (COMMON 94, 001 CUSTOMER SITE 56, ENTERPRISE 15) | BU export |
| | AR payment terms / AR transaction types tied to a set | 18 / 25 | AR exports |
| | AP payment-term set links | 61 | AP export |
| Currencies | Ledger currency (primary / secondary rows) | 65 / 65 (USD in 120 cells) | GL export; REST ledgersLOV (48 of 68 are USD) |
| | Ledger relationships with a target currency | 17 | GL export |
| | Price lists by currency | 55 (USD 30, PKR 14, AFN 7) | REST priceLists |
| | BUs with a default currency | 19 | BU export |

### c) What Oracle's documentation says depends on them

| Subject | Dependency | Tag | Link |
|---|---|---|---|
| Business units | A BU is tied to a primary ledger and a default legal entity, and turns on business functions | FROM ORACLE DOCUMENTATION | [Define Business Units, Assign Business Function, Ledger and Legal Entity](https://docs.oracle.com/en/cloud/saas/sales/oacts/Chunk176647350.html) |
| | The legal entity can be inferred from the BU that processes a transaction | FROM ORACLE DOCUMENTATION | [Model Legal Entities (24b)](https://docs.oracle.com/en/cloud/saas/financials/24b/faigl/model-legal-entities.html) |
| | A BU's default reference data set is used for all setup types unless overridden | FROM ORACLE DOCUMENTATION | [Reference data sharing (Fusion HCM)](https://docs.oracle.com/cd/E25178_01/fusionapps.1111/e20378/F587343AN17CA3.htm) |
| | Receivables transaction types, sources and payment terms are found through the BU's set | FROM ORACLE DOCUMENTATION | [Reference Data Sets in Receivables (25a)](https://docs.oracle.com/en/cloud/saas/financials/25a/fairp/reference-data-sets-in-receivables.html) |
| | Enterprise structure model (BU, legal entity, ledger) | FROM ORACLE DOCUMENTATION | [Enterprise Structures Business Process Model (25a)](https://docs.oracle.com/en/cloud/saas/financials/25a/faigl/enterprise-structures-business-process-model.html) |
| Reference data sets | Sharing methods: one set, common set, or many sets (Payables terms) | FROM ORACLE DOCUMENTATION | [Reference Data Sets and Sharing Methods (24c)](https://docs.oracle.com/en/cloud/saas/human-resources/24c/faucf/reference-data-sets-and-sharing-methods.html) |
| | Payment terms carry a set (AP_TERMS_ST.SET_ID) | FROM ORACLE DOCUMENTATION | [AP_TERMS_ST (25b)](https://docs.oracle.com/en/cloud/saas/financials/25b/oedmf/aptermsst-11042.html) |
| Currencies | A ledger currency with an end date blocks use; Oracle says to remove the end date | FROM ORACLE DOCUMENTATION | [Desupported currency codes (25d)](https://docs.oracle.com/en/cloud/saas/applications-common/25d/facia/what-do-i-do-if-a-currency-code-i-am-still-using-in-my-existing.html) |
| | Price lists stop working if their currency is disabled | GUESS (no Oracle page found) | — |

Older Oracle pages for "What reference data objects can be shared across business units?" now redirect to a landing page, so the 81 setup types read live from ETIA-TEST are used instead.

## Step 4: Scores

Scoring for 3 and 4: **2** = checked and works in this run; **1** = a route exists or data exists, but it was not run, is partial, or has few links; **0** = none or not checked. Checks 3 and 4 reuse Runs 09 and 17 where noted.

| Candidate | 1 Setup, not transactions | 2 Many depend on it | 3 Export works | 4 Live links | 5 One-sentence | **Total** |
|---|---|---|---|---|---|---|
| **Business units** | 2 | 2 | 2 | 2 | 2 | **10** |
| Reference data sets | 2 | 2 | 2 | 2 | 1 (hard to explain) | 9 |
| Currencies | 2 | 2 | 1 (export holds 9 of 268) | 2 | 2 | 9 |
| Primary ledgers | 2 | 2 | 2 | 2 (92 BUs) | 1 | 9 |
| Legal entities | 2 | 2 | 1 (not run) | 2 (92 BUs, REST) | 2 | 9 |
| AR payment terms | 2 | 1 | 2 | 1 (Run 09: 0 uses of the test term) | 2 | 8 |
| AP payment terms | 2 | 1 | 2 | 1 (61 set links only) | 2 | 8 |
| Carriers | 2 | 1 | 2 (Run 17) | 1 (Run 17: 20 org-service rows) | 2 | 8 |
| Customer profile classes | 2 | 1 | 2 (Run 09) | 1 | 2 | 8 |
| Accounting calendars | 2 | 1 | 1 | 1 | 2 | 7 |
| Units of measure | 2 | 2 | 1 | 0 | 2 | 7 |
| Conversion rate types | 2 | 1 | 1 | 0 | 1 | 5 |
| Tax regimes | 2 | 0 | 1 | 0 | 1 | 4 |

### Winner: business units

| Item | Detail |
|---|---|
| Export route | FSCR `shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code FUN_MANAGE_BUSINESS_UNIT --data`. One zip holds 4 files: FUN_BUSINESS_UNIT, FUN_BU_USAGE, FUN_BU_SERVICE_PROVIDERS, and the set assignments (LE_1214416713655.csv). |
| Sheet columns | The 28 columns above. The key ones are Name, Status, DefaultSetCode, PrimaryLedgerName, LegalEntityName, DefaultCurrencyCode and OrganizationCode. |
| Value to change | **BU "ABD": Status A → I (inactive).** ABD has the most kinds of links: ledger DSSLedger US, legal entity DSSVision America, 19 business functions, 8 service-provider links, 68 set assignments (all to set 001 CUSTOMER SITE), 21 price lists and 1 data-access grant. Making it inactive touches all of them. |
| Second option | Change ABD's DefaultSetCode. This only affects setup types without their own assignment; ABD has 68 of its own, so the effect is smaller. |

**What we expect to be affected if ABD becomes inactive:**

| Affected setup or module | Tag |
|---|---|
| 21 price lists (Pricing / Order Management) | VERIFIED IN ENVIRONMENT (links); the effect is a GUESS |
| 68 set assignments: AR payment terms, AP payment terms, AR transaction types, collectors, lockbox, memo lines and others | VERIFIED IN ENVIRONMENT (links); FROM ORACLE DOCUMENTATION (sets via BU) |
| 19 business functions (for example payables, receivables, procurement, order fulfilment) | VERIFIED IN ENVIRONMENT (links); FROM ORACLE DOCUMENTATION |
| 8 service-provider relationships with other BUs | VERIFIED IN ENVIRONMENT |
| Ledger DSSLedger US and legal entity DSSVision America (the links, not the records) | VERIFIED IN ENVIRONMENT; FROM ORACLE DOCUMENTATION |
| 1 user data-access grant | VERIFIED IN ENVIRONMENT |
| Advice to check Expenses, Projects, Time and Labor and Requisitioning | FROM FSCR (`manage-business-unit.md:59`) |
| Customer sites, suppliers, receivables and payables setup not read in this run | GUESS |

**What FSCR does and what Claude does**
- **FSCR by itself:** the export (one call gives the BU plus 3 kinds of links), the BU guidance with its "assess impacts" checklist, the REST client and sign-in.
- **Claude:** choose what to read; read the other setups (price lists, data access, AR, AP, GL); match names and codes across files; count links per BU; add Oracle's documented links; tag each line; write the impact list. FSCR has no step that finds what points to a record.

**One sentence for the presentation:** "A business unit is a part of the company that does its own buying and selling. If we switch one off, its price lists, payment terms, user access and links to other business units are all affected, and the tool shows us exactly which ones."

## Time and tool calls

| Item | Value |
|---|---|
| Start → finish of the work | 17:49:33 → 18:00:51 (+05:00), about 11 min |
| Sign-in | none needed (saved sign-in still valid) |
| FSM exports | 9 run, 9 returned data (17:51–17:59) |
| REST reads | 8, all HTTP 200 |
| Tool calls | **29** from the Run 18 request to the counting step: 19 Bash, 3 Write, 3 WebSearch, 3 WebFetch, 1 plan update. Counted from this session's transcript (`scripts/count_tool_calls.py`, output in `evidence/tool_call_count.txt`). After that: 1 Edit of this report and 1 wrap-up call, so **31 in total**. |

## Cleanup
- No sign-in listener or browser pane was started in this run.
- Exports and REST reads ran in the foreground or as finished background jobs. After the run, no Python or curl process was running and nothing was listening on port 8765.
- The original repo was not touched: the run used a copy, `fscr-work18`. No token was printed or saved.
