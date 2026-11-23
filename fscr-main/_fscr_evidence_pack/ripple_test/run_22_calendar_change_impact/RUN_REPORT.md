# FSCR Run 22: calendar change-impact test (analysis only)

## Plain summary
1. **The change:** in a copy of the workbook (not in Oracle), we moved the last day of December 2026 in the "GoSaaS MFG" calendar from 31 Dec to 24 Dec. A calendar is the list of months the company books money into.
2. **Ledgers:** 13 ledgers (sets of books) use this calendar, so all 13 would get a December that ends on 24 Dec.
3. **Business units:** 37 business units (parts of the company) keep their books in those 13 ledgers.
4. **Receivables:** 2 of them, BUU1 and AMNA BU, have Receivables (customer billing) set up. Their December billing month would also end on 24 Dec, even though nobody touched Receivables.
5. **Payables and Procurement:** 3 business units have Payables (supplier bills) set up and 4 have Procurement (buying) set up; their December would move the same way.
6. **The catch:** 25–30 Dec would belong to no month at all, and Oracle checks for such gaps when a calendar is saved. So Oracle would refuse this edit unless the next period is changed too.
7. **Example 1 (illustrative):** a customer invoice in BUU1 dated 28 Dec 2026 would no longer fall in December; it would have no month to be booked in. BUU1 really does bill customers: it has 3 invoices, from March 2025.
8. **Example 2 (real setup):** AMNA BU's Receivables setup points to ledger "EBS-Testing-AI". That ledger uses GoSaaS MFG, so AMNA BU's December would shrink without any edit to AMNA BU.
9. **Today:** no real invoices or receipts are dated 25–31 Dec 2026, so no existing document is hit.
10. **Control:** the second calendar, "GS Account", has no December 2026 (its last month is July 2022), so that change could not be made. Its 28 business units have no Receivables setup at all.

**Nothing was applied to Oracle.**
- **Baseline:** the BASELINE file's MD5 was checked at the start and at the end (unchanged).
- **Live vs baseline:** live ETIA-TEST still equals the baseline.
- **Sign-in:** not needed; the saved sign-in was still valid.

## Step 1: Changes made in the copy

| Change | Sheet | Rows changed | Column | Old → new |
|---|---|---|---|---|
| 1 (main) | Periods | 1 (GoSaaS MFG / Dec-26) | EndDate | 2026/12/31 → 2026/12/24 |
| 1 (main) | PeriodStatus | 65 (13 ledgers × 5 applications, Dec-26) | EndDate | 2026-12-31 → 2026-12-24 |
| 2 (control) | Periods | **0: not made** | EndDate | GS Account has no Dec-26. Workbook and live both show 13 periods, Jul21 to 13_Jul22 (2022/07/25). |

All 67 entries (66 changes plus the "not made" note) are logged in the **Changes** sheet. The result is `calendar_chain_workbook_ETIA-TEST_EDITED.xlsx`.

## Step 2: Detection

| Compare | Result |
|---|---|
| EDITED vs BASELINE | **66 cells differ:** Periods EndDate 1, PeriodStatus EndDate 65. Changes has 67 new log rows, and ImpactMap and WhoDidWhat are new sheets. No other cell differs. Full list: `evidence/diff_cells.csv`. |
| Live periods (REST accountingPeriodsLOV, 3 calendars) vs BASELINE | 91 = 91 periods, **0 differences** |
| Live period status (REST accountingPeriodStatusLOV, 25 ledgers) vs BASELINE | 4,355 = 4,355 rows, **0 differences** |

**Live ETIA-TEST still equals the baseline.**

## Step 3: Impact, level by level (Change 1)

| Level | Module | What | Link | Count | Tag | Source |
|---|---|---|---|---|---|---|
| 0 | General Ledger | Dec-26 EndDate 2026/12/31 → 2026/12/24 | edited cell | 1 | VERIFIED IN ENVIRONMENT | EDITED workbook |
| 1 | General Ledger | Adjacent period 13_Dec-26 (adjusting, 2026/12/31) | next period | 1 | VERIFIED IN ENVIRONMENT | workbook Periods |
| 1 | General Ledger | 25–30 Dec 2026 belong to no period | calendar continuity | 6 days | VERIFIED IN ENVIRONMENT | workbook Periods |
| 1 | General Ledger | Calendar save checks for gaps, so this edit fails | Oracle validation | — | FROM ORACLE DOCUMENTATION | [How Accounting Calendars Are Validated (25d)](https://docs.oracle.com/en/cloud/saas/applications-common/25d/facia/how-accounting-calendars-are-validated.html) |
| 1 | General Ledger | FSCR stops when continuity breaks; the adjacent period becomes "affected" | FSCR rule | — | FROM FSCR | `manage-accounting-calendars/SKILL.md:179-229` |
| 1 | General Ledger | Ledgers using GoSaaS MFG | ledger PeriodSetName | 13 | VERIFIED IN ENVIRONMENT | workbook Ledgers |
| 2 | General Ledger | Dec-26 GL status per ledger | status row | 13 (all Never opened) | VERIFIED IN ENVIRONMENT | REST accountingPeriodStatusLOV |
| 2 | Receivables | Dec-26 Receivables status per ledger | status row | 13 (all Never opened) | VERIFIED IN ENVIRONMENT | same |
| 2 | Payables | Dec-26 Payables status per ledger | status row | 13 (all Never opened) | VERIFIED IN ENVIRONMENT | same |
| 2 | Other | Dec-26 status for applications 10037 and 10455 (names not read) | status row | 13 + 13 (all Never opened) | VERIFIED IN ENVIRONMENT | same |
| 2 | Enterprise structure | Business units on those ledgers | BU primary ledger | 37 | VERIFIED IN ENVIRONMENT | workbook BusinessUnits |
| 3 | Receivables | System options: BUU1, AMNA BU | options row per BU | 2 | VERIFIED IN ENVIRONMENT | workbook ReceivablesOptions |
| 3 | Receivables | Transaction-type BU rows | BU row | 3 | VERIFIED IN ENVIRONMENT | workbook ReceivablesTxnTypes |
| 3 | Receivables | Receivables Dec-26 follows the GL dates | subledger follows GL | 2 BUs | FROM ORACLE DOCUMENTATION | [Accounting periods (24d)](https://docs.oracle.com/en/cloud/saas/financials/24d/faofc/what-happens-to-accounting-periods-during-reconciliation.html) |
| 3 | Payables and Procurement | Common options: AmnaNBU, Splendid BU, Zaid BU | options row per BU | 3 | VERIFIED IN ENVIRONMENT | workbook OtherModules |
| 3 | Payables | Invoice and payment options: the same 3 BUs | options row per BU | 3 | VERIFIED IN ENVIRONMENT | workbook OtherModules |
| 3 | Procurement | Options: GoSaaS, Splendid BU, Vision BU, Zaid BU | options row per BU | 4 | VERIFIED IN ENVIRONMENT | workbook OtherModules |
| 3 | Costing | Cost books on these ledgers (not read) | cost book uses ledger calendar | — | FROM FSCR | `cost-organization-relationships/ora-resource/ora_dependency_readiness.md:28-29` |
| 3 | Several modules | FSCR "assess impacts" checklist: Expenses, Projects, Time and Labor, Requisitioning | FSCR guide | — | FROM FSCR | `organization-structures/manage-business-unit.md:59` |
| 4 | Receivables | Invoices dated 25–31 Dec 2026 | date in period | **0** (3 visible, all BUU1, March 2025) | VERIFIED IN ENVIRONMENT | REST receivablesInvoices |
| 4 | Receivables | Receipts dated 25–31 Dec 2026 | date in period | **0** | VERIFIED IN ENVIRONMENT | REST standardReceipts |
| 4 | Payables | Invoices dated 25–31 Dec 2026 (invoice or accounting date) | date in period | **0** (71 visible in total) | VERIFIED IN ENVIRONMENT | REST invoices |
| 4 | Receivables | A future invoice dated 25–30 Dec would have no period | gap | — | GUESS | reasoning from the gap |

**The three checks you asked for:**
- **Adjusting period 13_Dec-26:** it stays dated 2026/12/31. With Dec-26 ending on 2026/12/24, 25–30 Dec are in no period and 31 Dec is only in the adjusting period, so the change conflicts with it. Making it valid would need 13_Dec-26, or a new period, to cover 25–30 Dec. FSCR calls that adjacent period "affected". The calendar also has no 2027 periods after 13_Dec-26.
- **Would Oracle allow it?**
  - **Status lock: not triggered.** Dec-26 is "Never opened" in all 13 ledgers for all 5 applications (65 of 65 rows), and Oracle and FSCR only lock periods that are open or future-entry.
  - **Calendar check: fails.** The gap breaks Oracle's calendar check on save, and FSCR's continuity rule.
  - **Verdict:** blocked as written.
- **Documents dated 25–31 Dec 2026:** none in Receivables (invoices or receipts) and none in Payables. No existing document would move.

**Change 2 (control, GS Account):**
- **The change:** Dec-26 does not exist, so nothing is changed.
- **Reach, for contrast:**
  - 9 ledgers and 28 business units;
  - **0 Receivables options and 0 transaction-type rows**;
  - Payables options: 1 BU (PRCSYEDA_BZNS);
  - Procurement options: 8 BUs.
- **What this shows:** even with a matching period, Receivables would not be reached through this calendar.

## Step 4: Examples

| Change | Example | Type |
|---|---|---|
| 1 | A customer invoice in **BUU1** dated 28 Dec 2026 would no longer fall in Dec-26: 25–30 Dec belong to no period, so it could not be booked until the calendar is fixed. (BUU1 is a real billing BU with 3 invoices from March 2025.) | ILLUSTRATIVE (real BU; no such invoice exists) |
| 1 | **AMNA BU**'s Receivables options name ledger **EBS-Testing-AI**, which uses GoSaaS MFG. AMNA BU's Receivables December (Never opened today) would end on 24 Dec without anyone editing AMNA BU. | Real rows |
| 2 | GS Account's last period is **13_Jul22 (25 Jul 2022)**; there is no Dec-26 to move, so the edit changes nothing. | Real rows |
| 2 | Even if GS Account had a Dec-26, **none of its 28 BUs has Receivables options**. Only Payables (PRCSYEDA_BZNS) and Procurement (8 BUs) would be reached. | ILLUSTRATIVE (real counts, hypothetical period) |

## Step 5: Impact map

The **ImpactMap** sheet (also in `impact_map.csv`) has 35 rows, with the columns Change, Level, Module, ObjectType, ObjectName, ReachedFrom, LinkType, Count, Tag and Source.

| | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 |
|---|---|---|---|---|---|
| Change 1 map rows | 1 | 5 | 6 | 8 | 4 |
| Change 1 key counts | 1 cell | 13 ledgers, 1 adjacent period, 6-day gap | 37 BUs; 65 status rows | 2 AR options, 3 AR txn-type rows, 3 Payables BUs, 4 Procurement BUs | 0 documents |
| Change 2 map rows | 1 (not made) | 1 | 1 | 8 | — |
| Change 2 key counts | 0 cells | 9 ledgers | 28 BUs | 0 AR, 1 Payables BU, 8 Procurement BUs | — |

The **WhoDidWhat** sheet has 15 steps:
- **FSCR (5):** the calendar edit rules, the continuity and adjacent-period rule, the ledger-to-calendar link, the BU "assess impacts" checklist, and the exports.
- **Claude (10):** copy and edit, detection, live reads, the join across levels, the document search, the Oracle documentation, the examples and the report.

FSCR has no step that runs the impact walk itself.

## Time and tool calls

| Item | Value |
|---|---|
| Start → finish | 19:13:22 → 19:18:32 (+05:00), about 5 min (request received 19:12:59) |
| Sign-in | none needed |
| Oracle reads (all GET) | 3 live period reads; 25 period-status reads; 8 document searches (3 Receivables reads rejected date filters with HTTP 400, so all 3 visible invoices were read and filtered locally); 1 sign-in check. **No writes.** |
| Tool calls | **14** from the Run 22 request to the counting step: 9 Bash, 2 Write, 1 Read, 1 WebSearch, 1 plan update. Counted from this session's transcript (`scripts/count_tool_calls.py`, output in `evidence/tool_call_count.txt`). After that: 2 Edits of this report and 1 wrap-up call, so **17 in total**. |

## Cleanup
- No sign-in listener, browser pane or background job was started.
- After the run, no Python or curl process was running and nothing was listening on port 8765. Your own page was not touched.
- The BASELINE MD5 was checked at the start and at the end: OK (`evidence/baseline_check.txt`, `evidence/baseline_check_end.txt`).
- `fscr-work22` is a copy of the FSCR repo, used to read the calendar skill; the original was not touched. No token was printed or saved.
