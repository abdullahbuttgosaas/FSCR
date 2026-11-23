# FSCR Run 19: business unit workbook (read only)

Pod **ETIA-TEST**, 2026-11-09. Nothing was created, changed or deleted in Oracle. No change test was run.

## Answer

The workbook **`bu_change_impact_workbook_ETIA-TEST.xlsx`** is built. It covers 6 business units and has 11 sheets: README, 9 data sheets and an empty Changes sheet.
- Every data sheet starts with **BusinessUnitName** and **BusinessUnitId** and ends with **Source**, so rows can be matched across sheets.
- Most data comes from the Run 18 exports and REST reads. Only price lists were read again, to get all their columns.
- The saved sign-in still worked, so no sign-in listener or browser was started.

**Check result:** every sheet matches its source for every BU, and every BU ID matches. Set assignments also match a second source (REST) row for row.

There is one difference from Run 18: **service providers**. Run 18 counted a BU that serves itself twice, once as client and once as provider. The workbook lists each such row once, so ABD shows 4 rows, not 8. This is a counting fix, not missing data.

There is one gap: **business function names are not in the export**. The sheet shows the Oracle module ID only. FSCR says the ID-to-name list is seed data provided by the developers, and it is not in the repo.

## Step 1: The 6 business units

| Business unit | ID | Why picked |
|---|---|---|
| ABD | from REST (in the workbook) | Most kinds of links: ledger, legal entity, 19 functions, service providers, 68 set assignments, 21 price lists, user access |
| ABC Procurement BU | " | Also has all 7 kinds of links, including 3 price lists, on a different ledger (GoSaaS Labs Ledger) |
| GoSaaS | " | Most user access (25 grants); its ledger GoSaaS MFG US is shared with other BUs |
| AMNA BU | " | Has Receivables system options and a Receivables transaction-type row |
| AKBusiness Unit Domestic | " | Has Receivables system options, a default currency (USD) and the most service-provider rows (7) |
| ZZ_TEST_7669 | " | Contrast: active, but no ledger, legal entity, functions, set assignments, price lists or user access |

The README sheet lists the IDs.

## Step 2: Rows per sheet and BU

| Sheet (source) | ABD | ABC Proc. | GoSaaS | AMNA | AK Domestic | ZZ_TEST_7669 |
|---|---|---|---|---|---|---|
| BusinessUnits: 35 columns (FSM export FUN_MANAGE_BUSINESS_UNIT + REST finBusinessUnitsLOV) | 1 | 1 | 1 | 1 | 1 | 1 |
| BusinessFunctions (BU export, FUN_BU_USAGE; all enabled = Y) | 19 | 18 | 18 | 18 | 18 | **0** |
| LedgerAndLegalEntity (BU export + REST ledgersLOV, legalEntitiesLOV + GL export) | 1 | 1 | 1 | 1 | 1 | 1 (blank: none) |
| ServiceProviders (BU export, FUN_BU_SERVICE_PROVIDERS) | 4 | 4 | 4 | 4 | 7 | **0** |
| SetAssignments (BU export set file, checked against REST) | 68 | 68 | 67 | 68 | 68 | **0** |
| PriceLists (REST priceLists, read in Run 19) | 21 | 3 | **0** | **0** | **0** | **0** |
| UserAccess (REST dataSecurities) | 1 | 1 | 25 | 11 | 11 | **0** |
| ReceivablesOptions (FSM export AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS; 52 columns with values) | **0** | **0** | **0** | 1 | 1 | **0** |
| ReceivablesTxnTypeBU (FSM export AR_MANAGE_TRANSACTION_TYPES) | **0** | **0** | **0** | 1 | **0** | **0** |
| Changes | empty, as asked | | | | | |

UserAccess was readable, so no "not readable" note was needed. Bold 0 means the sheet has no rows for that BU.

## Step 3: Check

| Check | Result |
|---|---|
| Sheet count = source count, per BU (9 sheets × 6 BUs) | **All match** |
| BU ID column the same on every sheet | **Yes** (all 9 sheets) |
| Set assignments: FSM export vs REST setIdAssignmentsBusinessUnit | **Match** for all 6 BUs, same set code on every row |
| Price lists: Run 19 read vs Run 18 read | **Match** |
| Ledgers found in REST ledgersLOV | **Yes** for all 5 BUs that have one |
| Compared with Run 18 numbers (ABD: 19 functions, 68 set assignments, 21 price lists, 1 user grant) | **Match**, except service providers below |

**Mismatches (all from Run 18's counting, not from missing data):**

| Sheet / BU | Workbook | Run 18 | Why |
|---|---|---|---|
| ServiceProviders / ABD | 4 | 8 | 4 rows where ABD serves itself; Run 18 counted each twice |
| ServiceProviders / ABC Procurement BU | 4 | 8 | same (4 self rows) |
| ServiceProviders / GoSaaS | 4 | 8 | same (4 self rows) |
| ServiceProviders / AMNA BU | 4 | 8 | same (4 self rows) |
| ServiceProviders / AKBusiness Unit Domestic | 7 | 11 | 7 rows, 4 of them self rows |

Proof: `evidence/service_provider_self_rows.txt`.

**Empty sheets per BU:**
- **ZZ_TEST_7669:** empty everywhere except BusinessUnits, and its LedgerAndLegalEntity row is blank. This is expected for the contrast BU.
- **PriceLists:** empty for GoSaaS, AMNA BU and AKBusiness Unit Domestic.
- **ReceivablesOptions:** empty for ABD, ABC Procurement BU and GoSaaS.
- **ReceivablesTxnTypeBU:** has a row only for AMNA BU.

**Known limits:**
- Function names are missing (module IDs only).
- Run 18's data is about 1 hour old; price lists are fresh.
- The BusinessUnits sheet includes manager names from the export.

## Time and tool calls

| Item | Value |
|---|---|
| Start → finish of the work | 18:06:11 → 18:09:14 (+05:00), about 3 min (request received 18:05:57) |
| Sign-in | none needed (saved sign-in still valid) |
| New Oracle reads | 1 REST read (price lists, 55 rows), plus 1 sign-in check and 3 probes for business-function REST routes (all HTTP 404) |
| Tool calls | **12** from the Run 19 request to the counting step: 9 Bash, 2 Write, 1 plan update. Counted from this session's transcript (`scripts/count_tool_calls.py`, output in `evidence/tool_call_count.txt`). After that: 1 Edit of this report and 1 wrap-up call, so **14 in total**. |

## Cleanup
- No sign-in listener, browser pane or background job was started in this run.
- After the run, no Python or curl process was running and nothing was listening on port 8765. Your own page was not touched.
- `fscr-work19` is a copy of the FSCR repo made for this run; nothing in it was run. The original repo was not touched. No token was printed or saved.
