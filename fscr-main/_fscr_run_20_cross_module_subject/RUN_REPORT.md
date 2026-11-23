# FSCR Run 20: a setup whose change reaches another module (read only)

Pod **ETIA-TEST**, 2026-11-09. Nothing was created, changed or deleted in Oracle. The FSM exports each left one export-process record, which is how FSM export works (a read route).

## Answer

**Use the accounting calendar (General Ledger) and its link to Receivables.** Receivables never names the calendar. It names a ledger, and the ledger uses the calendar, so a calendar change reaches Receivables without anyone in Receivables touching anything.

In ETIA-TEST this is real for **8 calendars that reach all 19 Receivables system-option rows**. The widest one is **GoSaaS MFG**:
- 13 ledgers use it;
- 37 business units point to those ledgers;
- 2 of those BUs (BUU1 and AMNA BU) have Receivables system options;
- 3 Receivables transaction-type rows belong to those BUs.

FSCR exports the calendar (24 calendars, 454 periods), and every step was traced in live data.

The runner-up is the **"Corporate" conversion rate type**. It reaches more Receivables rows (17 BUs), but Receivables names it directly, so the link is less hidden.

**Sign-in note:** the saved sign-in expired at about 18:23, during the first exports. I started one clean listener; the sign-in finished at 18:39, and the exports were run again.

## Step 1 and 2: Candidates and screen

A = different modules. B = indirect (not a parent and child). C = real link in ETIA-TEST.

| # | Chain: change X in B → through Y → Z in A | Idea from | A | B | C | Result |
|---|---|---|---|---|---|---|
| 1 | **Accounting calendar (GL) → ledger → Receivables system options and Receivables periods (AR)** | FSCR cost-organization readiness file (ledger → calendar); Oracle docs; live data | ✓ | ✓ AR never names the calendar | ✓ 8 calendars, 19 AR rows | **Kept** |
| 2 | Conversion rate type "Corporate" (GL) → Receivables system option "cross-currency rate type" → cross-currency receipts and Lockbox (AR) | Run 18 AR export; Oracle docs; FSCR Payables and Expenses readiness files | ✓ | ✓ (a reference, not a child; one hop) | ✓ 17 AR rows | **Kept** |
| 3 | Segment value 2640 (GL value set) → account combination → Receivables system options tax account (AR) | Run 18 AR export; FSCR AutoAccounting readiness file; Oracle docs | ✓ | ✓ | ✓ 13 AR rows | **Kept** |
| 4 | Currency (Common) → ledger currency (GL) → Receivables options of BUs on those ledgers (AR) | Run 18 GL export | ✓ | ✓ | ✓ 48 USD ledgers | Kept (4th) |
| 5 | Payables payment terms → supplier sites and purchase orders (Procurement) | FSCR Payables skill; Oracle docs | ✓ | ✓ | **✗ not read** (supplier data not checked) | Rejected: C |
| 6 | Set assignment for AR_PAYMENT_TERMS (Common) → terms a BU sees → customer profile classes (AR) | Run 18 | ✓ | **✗** set assignments are BU children | ✓ | Rejected: B |
| 7 | Business unit → price lists | Runs 18–19 | ✓ | **✗** parent and child | ✓ | Rejected: B, excluded |
| 8 | Order type → process assignment rule | Run 17 | ✓ | ✓ | ✓ | Rejected: excluded |
| 9 | Legal entity → balancing segment values in the ledger (GL) | GL export (38 rows) | ✓ | **✗** detail rows of the legal entity | ✓ | Rejected: B |
| 10 | Tax regime (Tax) → Receivables system-option tax fields (AR) | AR export | ✓ | ✓ | **✗** all tax fields empty in 19 rows | Rejected: C |
| 11 | Customer profile class → payment term (both in AR) | Run 09 | **✗** same module | — | — | Rejected: A |
| 12 | AR transaction type → default payment term (both in AR) | AR export | **✗** same module | — | — | Rejected: A |
| 13 | Carriers (Shipping) → carrier services per organization | Run 17 | ✓ | **✗** child rows; inventory organizations excluded | ✓ | Rejected: B, excluded |

## Step 3: Deep check on the top 3

### a) Exports (FSCR task-level FSM CSV export)

| Subject | Sheet | Rows and columns |
|---|---|---|
| Accounting calendars | `accounting_calendars_ETIA-TEST.xlsx` | GL_PERIOD_SET: 24 rows, 31 columns. GL_PERIOD_DEF: 454 rows, 64 columns. |
| Conversion rate types | `conversion_rate_types_ETIA-TEST.xlsx` | GL_DAILY_CONVERSION_TYPE: 12 rows, 32 columns. ORA_GL_CONVERSION_RATE_RULE: 10 rows, 9 columns. |
| Chart-of-accounts values | `coa_value_set_values_ETIA-TEST.xlsx` | ORA_FND_APP_FLEX_VALUE_SET_VALUE: 1,117 rows, 28 columns. FND_APP_FLEX_VALUE_SET: 102 rows, 28 columns. Plus 4 small files. |

The middle and A rows come from the Run 18 exports: GL_MANAGE_PRIMARY_LEDGERS, FUN_MANAGE_BUSINESS_UNIT, AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS and AR_MANAGE_TRANSACTION_TYPES.

### b) and c) The chains, step by step

**Chain 1: calendar GoSaaS MFG**

| Step | Rows | Tag | Source or link |
|---|---|---|---|
| B: calendar GoSaaS MFG (12 periods and 1 adjusting period a year; 52 periods; starts 2023-01-01) | 1 calendar | VERIFIED IN ENVIRONMENT | calendar export |
| Y: ledgers whose PeriodSetName = GoSaaS MFG (for example GoSaaS MFG US, EBS-Testing-AI) | 13 | VERIFIED IN ENVIRONMENT | GL ledger export |
| A ledger is built on one accounting calendar | — | FROM FSCR | `pillars/scm/.../cost-accounting/cost-organization-relationships/ora-resource/ora_dependency_readiness.md:28-29` |
| A secondary ledger must share the primary ledger's calendar | — | FROM ORACLE DOCUMENTATION | [Oracle Fusion GL guide (11.1)](https://docs.oracle.com/cd/E15586_01/fusionapps.1111/e20375/F350915AN25358.htm) |
| Y2: business units on those ledgers | 37 | VERIFIED IN ENVIRONMENT | BU export |
| A: Receivables system options whose LedgerName uses this calendar (BUU1, AMNA BU) | 2 | VERIFIED IN ENVIRONMENT | AR system options export |
| A: Receivables transaction-type BU rows for those BUs | 3 | VERIFIED IN ENVIRONMENT | AR transaction types export |
| Receivables periods follow the GL periods (a closed GL period blocks reopening the AR period) | — | FROM ORACLE DOCUMENTATION | [What happens to accounting periods during reconciliation (24d)](https://docs.oracle.com/en/cloud/saas/financials/24d/faofc/what-happens-to-accounting-periods-during-reconciliation.html) |
| All 8 linked calendars together | 19 AR option rows | VERIFIED IN ENVIRONMENT | `evidence/winner_detail.txt` |

**Chain 2: conversion rate type Corporate**

| Step | Rows | Tag | Source or link |
|---|---|---|---|
| B: rate type Corporate (seeded; EnforceInverseRateFlag Y; last changed 2026-11-04) | 1 | VERIFIED IN ENVIRONMENT | rate type export |
| Y and A: Receivables system options with CrossCurrencyRateType = Corporate | 17 of 19 BUs | VERIFIED IN ENVIRONMENT | AR export |
| Also in GL: ledger translation rate type | 2 secondary ledgers | VERIFIED IN ENVIRONMENT | GL export |
| Receivables uses this rate type for cross-currency receipts and Lockbox | — | FROM ORACLE DOCUMENTATION | [How Cross-Currency Receipts Are Processed (24b)](https://docs.oracle.com/en/cloud/saas/financials/24b/faofc/how-cross-currency-receipts-are-processed.html) |
| Payables, Procurement and Expenses use rate types | — | FROM FSCR | `payables/manage-common-options-for-payables-and-procurement/ora-resource/ora_dependency_readiness.md:22`; `expenses/manage-conversion-rates-and-policies/ora-resource/ora_dependency_readiness.md:15` |

**Chain 3: segment value 2640**

| Step | Rows | Tag | Source or link |
|---|---|---|---|
| B: value 2640, enabled, in 7 account value sets (one per ledger family, for example N24Account N24Ledger) | 7 | VERIFIED IN ENVIRONMENT | value set export |
| Y: account combinations that contain it | not read | GUESS (combinations not exported) | — |
| A: Receivables system options whose tax account uses 2640 | 13 | VERIFIED IN ENVIRONMENT | AR export |
| Disabling a value reaches existing combinations only through a separate process | — | FROM ORACLE DOCUMENTATION | [How Cross-Validation Rule Violations Are Managed (25b)](https://docs.oracle.com/en/cloud/saas/financials/25b/faigl/how-cross-validation-rule-violations-are-managed.html) |
| Receivables AutoAccounting uses value-set values | — | FROM FSCR | `customer-billing/manage-autoaccounting-rules/ora-resource/ora_dependency_readiness.md:13` |

## Step 4: Scores

Score 1: export works. Score 2: can be said in two sentences. Score 3: every step supported.

| Candidate | A | B | C | 1 Export | 2 Two sentences | 3 Every step supported | **Total** |
|---|---|---|---|---|---|---|---|
| **1 Calendar → ledger → Receivables** | ✓ | ✓ (2 hops, never named in AR) | ✓ | 2 | 2 | 2 (live for every step, FSCR file, Oracle docs) | **6** |
| 2 Rate type → Receivables options | ✓ | ✓ (1 hop, named directly) | ✓ | 2 | 2 | 2 | 6 (tie; loses on "quiet") |
| 3 Segment value → Receivables tax account | ✓ | ✓ | ✓ | 2 | 1 | 1 (combination step not read) | 4 |
| 4 Currency → ledger → Receivables | ✓ | ✓ | ✓ | 1 (export holds 9 of 268) | 2 | 1 | 4 |
| 5–13 | rejected (see the screen) | | | | | | — |

**The tie-break:** chain 1 wins because it fits your shape exactly. Receivables does not name the calendar anywhere; it relies on it only through the ledger.

### Winner: accounting calendar GoSaaS MFG

| Item | Detail |
|---|---|
| Two sentences | "The accounting calendar is set up once in General Ledger and decides where each month starts and ends. Receivables never mentions the calendar, but it uses a ledger that does, so if we move a month-end in the calendar, Receivables month-ends move too, for every business unit on those ledgers." |
| Export route | FSCR `export_setup_task_csv.py --task-code GL_MANAGE_ACCOUNTING_CALENDARS --data` |
| Sheet columns | **GL_PERIOD_SET** (calendars): UserPeriodSetName, PeriodSetName, Description, AdjPeriodsNum, NonAdjPeriodsNum, CalendarStartDate, CalendarTypeCode, LatestYearStartDate and others (31 in all). **GL_PERIOD_DEF** (periods): PeriodSetName, PeriodName, PeriodNum, PeriodYear, StartDate, EndDate, YearStartDate, QuarterNum, AdjustmentPeriodFlag and others (64 in all). |
| Value to change | **Calendar GoSaaS MFG, period Dec-26: EndDate 2026/12/31 → for example 2026/12/24.** It is a future period. This calendar has the widest reach: 13 ledgers, 37 BUs, 2 Receivables option rows and 3 Receivables transaction-type rows. A month-end move changes the Dec-26 period in every one of those ledgers and in each subledger that uses them. |
| Compare against | The ledger export (PeriodSetName), the BU export (PrimaryLedgerName), the AR system options export (LedgerName) and the AR transaction types export (BuName) |

**What we expect to be affected in Receivables (module A):**

| Item | Tag |
|---|---|
| Receivables system options of BUU1 and AMNA BU (their ledgers use GoSaaS MFG) | VERIFIED IN ENVIRONMENT (link) |
| Receivables Dec-26 accounting period for those BUs (opening, closing, GL dates) | FROM ORACLE DOCUMENTATION |
| 3 Receivables transaction-type BU rows of BUU1 and AMNA BU | VERIFIED IN ENVIRONMENT (link); the effect is a GUESS |
| Payables and Procurement periods for the 37 BUs on these ledgers | GUESS (not read) |
| Costing cost books on these ledgers | FROM FSCR (not read; that area is owned by another team) |

**What FSCR does and what Claude does**
- **FSCR by itself:** the exports (calendar, ledgers, BUs, Receivables options), the sign-in, and readiness files that name the ledger-to-calendar link.
- **Claude:**
  - think of the chain;
  - join calendar → ledger → BU → Receivables across 4 exports;
  - count the reach per calendar;
  - find Oracle's documentation;
  - tag each step;
  - pick the value.

  FSCR has no step that follows a link across modules.

## Time and tool calls

| Item | Value |
|---|---|
| Start → finish of the work | 18:22:11 → 18:44:22 (+05:00), about 22 min (request received 18:21:33) |
| Of which lost to the expired sign-in | 18:23 → 18:39: first exports timed out (5 minutes each), then the sign-in finished at 18:39:40 |
| FSM exports | 3 tried at 18:23 (all timed out on sign-in), 3 again at 18:39–18:42 (all worked) |
| Tool calls | **31** from the Run 20 request to the counting step: 18 Bash, 4 WebSearch, 2 Write, 2 plan updates, 1 wrap-up (the sign-in question), 4 browser-pane calls. Counted from this session's transcript (`scripts/count_tool_calls.py`, output in `evidence/tool_call_count.txt`). After that: 1 Edit of this report and 1 wrap-up call, so **33 in total**. |

## Cleanup
- **Sign-in listener:** one was started (port 8765). It closed by itself after the sign-in at 18:39. The three export retries at 18:23 also waited on 8765 and timed out by themselves.
- **Browser pane:** opened for the sign-in (Oracle's page was refused), then closed.
- **Processes:** after the run, no Python or curl process was running and nothing was listening on 8765. Your own page was not touched.
- **Repo and secrets:** `fscr-work20` is a copy of the FSCR repo; the original was not touched. No token was printed or saved. The sign-in link in `evidence/signin.raw` holds no secret.
