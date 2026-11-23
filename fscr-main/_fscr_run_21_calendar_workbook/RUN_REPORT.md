# FSCR Run 21: accounting calendar workbook (read only)

Pod **ETIA-TEST**, 2026-11-09. Nothing was created, changed or deleted in Oracle. No change test was run.

## Answer

The workbook **`calendar_chain_workbook_ETIA-TEST.xlsx`** is built. It shows the current setup of the chain: calendar → ledgers → business units → Receivables (and Payables and Procurement). It covers calendar **GoSaaS MFG** plus two contrast calendars:
- **N24Ledger:** few ledgers, but it reaches Receivables.
- **GS Account:** many business units, but no Receivables options.

It has 10 sheets: README, Calendars, Periods, **PeriodStatus**, Ledgers, BusinessUnits, ReceivablesOptions, ReceivablesTxnTypes, OtherModules and Changes. Every data sheet starts with the join keys (CalendarName, then LedgerName and LedgerId, then BusinessUnitName and BusinessUnitId) and has a Source column.

**The check matches Run 20 with no mismatches:** 13 ledgers, 37 business units, Receivables options for BUU1 and AMNA BU, and 3 Receivables transaction-type rows.

**What was added since Run 20:**
- **Period status per ledger and application** (new REST read). Dec-26 is "Never opened" for Receivables in all 13 GoSaaS MFG ledgers.
- **Payables and Procurement options** for these business units (4 new exports).

**Copies:** a frozen BASELINE copy (read-only file, MD5 recorded) and an identical EDIT copy.

## Rows per sheet

| Sheet | GoSaaS MFG | N24Ledger | GS Account | Source |
|---|---|---|---|---|
| Calendars | 1 | 1 | 1 | FSM export GL_MANAGE_ACCOUNTING_CALENDARS (Run 20), GL_PERIOD_SET |
| Periods | 52 (includes Dec-26: 2026/12/01–2026/12/31) | 26 | 13 | same export, GL_PERIOD_DEF |
| PeriodStatus | 3,380 | 390 | 585 | REST accountingPeriodStatusLOV (Run 21), one read per ledger, 25 ledgers |
| Ledgers | 13 | 3 | 9 | FSM export GL_MANAGE_PRIMARY_LEDGERS (Run 18) + REST ledgersLOV (IDs, chart of accounts ID) |
| BusinessUnits | 37 | 3 | 28 | FSM export FUN_MANAGE_BUSINESS_UNIT (Run 18) + REST finBusinessUnitsLOV (IDs) |
| ReceivablesOptions | 2 (BUU1, AMNA BU) | 3 | **0** | FSM export AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS (Run 18) |
| ReceivablesTxnTypes | 3 | **0** | **0** | FSM export AR_MANAGE_TRANSACTION_TYPES (Run 18) |
| OtherModules (one row per BU, setup and field) | 604 | 369 | 532 | FSM exports, Run 21 (see below) |
| Changes | empty, as asked | | | — |

**OtherModules** covers 4 setups:
- Payables and Procurement common options: 7 BUs;
- Payables invoice options: 7 BUs;
- Payables payment options: 7 BUs;
- Procurement business-function options: 12 BUs.

The Procurement file names the BU in a column called "ShortCode"; all 13 of its values match BU names exactly. Nothing in OtherModules is a guess, and no source was "not readable".

**About the period sheets:**
- **Periods** shows the calendar as defined. Status is not part of the calendar, because each ledger and each application has its own status, so it is in **PeriodStatus**.
- Application IDs 101, 200 and 222 are General Ledger, Payables and Receivables. **10037 and 10455** are in the data, but their names were not read.
- Status meanings come from Oracle's standard codes: O Open, C Closed, F Future entry, N Never opened.

## Check against Run 20

| Check | Workbook | Expected | OK |
|---|---|---|---|
| Ledgers on GoSaaS MFG | 13 (same names as Run 20) | 13 | ✓ |
| Business units on those ledgers | 37 | 37 | ✓ |
| BUs with Receivables options | BUU1, AMNA BU | BUU1, AMNA BU | ✓ |
| Receivables transaction-type rows | 3 | 3 | ✓ |
| GoSaaS MFG periods | 52 | 52 | ✓ |
| Dec-26 period present | 2026/12/01–2026/12/31 | yes | ✓ |
| Dec-26 Receivables status rows (one per ledger) | 13, all "Never opened" | 13 | ✓ |
| Ledger IDs and BU IDs filled | all filled | all | ✓ |

**Mismatches: none.**

**Empty sheets:**
- **ReceivablesOptions / GS Account:** expected; this is the contrast calendar with no Receivables options.
- **ReceivablesTxnTypes:** empty for N24Ledger and GS Account.
- **Changes:** empty by design.

**Status across all GoSaaS MFG ledgers:**
- **General Ledger:** 46 Open, 1 Future entry, the rest Never opened.
- **Payables:** 32 Open, 1 Future entry, the rest Never opened.
- **Receivables:** 4 Open, 2 Future entry, the rest Never opened.

## Copies

| File | MD5 |
|---|---|
| calendar_chain_workbook_ETIA-TEST.xlsx | c2bf561cec4267d6e8964e215bd2dd3a |
| calendar_chain_workbook_ETIA-TEST_BASELINE.xlsx (set to read-only) | c2bf561cec4267d6e8964e215bd2dd3a (in `evidence/baseline_md5.txt`) |
| calendar_chain_workbook_ETIA-TEST_EDIT.xlsx | c2bf561cec4267d6e8964e215bd2dd3a |

## Time and tool calls

| Item | Value |
|---|---|
| Start → finish of the work | 18:54:36 → 19:00:28 (+05:00), about 6 min (request received 18:54:10) |
| Sign-in | none needed (the 18:39 sign-in was still valid) |
| New Oracle reads | 4 FSM exports (Payables ×3, Procurement ×1; all worked); 25 REST reads of period status (all HTTP 200, plus 25 earlier attempts whose saving failed on a file-name bug); 1 sign-in check; 5 route probes (2 worked, 3 HTTP 404) |
| Tool calls | **19** from the Run 21 request to the counting step: 12 Bash, 4 Edit, 2 Write, 1 plan update. Counted from this session's transcript (`scripts/count_tool_calls.py`, output in `evidence/tool_call_count.txt`). After that: 2 Edits of this report and 1 wrap-up call, so **22 in total**. |

## Cleanup
- No sign-in listener, browser pane or long-running process was started. The one background job (the exports) finished by itself.
- After the run, no Python or curl process was running and nothing was listening on port 8765. Your own page was not touched.
- The baseline MD5 was checked again at the end: OK.
- `fscr-work21` is a copy of the FSCR repo, used for the exports; the original was not touched. No token was printed or saved.
