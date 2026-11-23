# Receivables sheet test (2026-11-02)

Three workbooks made from the page's own Receivables blank sheet. Every name starts `ZZ_TEST_` (names that touch Oracle
are neutral; records Oracle makes can't be deleted). Generator: the session's `make_sheet_test.py` (not kept here).

| File | What it is | Who runs it |
|---|---|---|
| `Receivables_sheet_test_A_run_by_Claude.xlsx` | one connected story: term `ZZ_TEST_PT_311` (net 30) -> type `ZZ_TEST_TT_3113` naming it; rule `ZZ_TEST_AG_3112` (Invoice, `L.INTERFACE_LINE_ATTRIBUTE1`) -> Imported source `ZZ_TEST_TS_3114` naming it; plus the existing type `ZZ_TEST_TT_6421` (skipped) | Claude, 2026-11-02 (results: `Transaction Types/CLAUDE.md` > Sheet test) |
| `Receivables_sheet_test_B_for_you.xlsx` | the same story with new names: `ZZ_TEST_PT_472`, `ZZ_TEST_AG_4721`, `ZZ_TEST_TT_4722`, `ZZ_TEST_TS_4723`, plus `ZZ_TEST_TT_6421` | the user, by hand; never uploaded by Claude |
| `Receivables_sheet_test_C_mistakes_check_only.xlsx` | 16 rows, one mistake each across the four tabs (name too long, lines add to 90, unknown set, no From Date, characteristic no rule uses, To before From, type name 21, Credit Memo, Post to GL empty, both application flags Yes, term nowhere, Last Number 0, rule on a Manual source, rule nowhere, no description, a number with numbering No) | check only: every row goes red and Create stays off |

Since 2026-11-02 the page no longer checks the Oracle browser sign-in for a sheet with only Receivables tabs (registry
`"uses_browser": false`); the page's start-up checklist still asks for it once when the page starts.

How to run B or C by hand: start the page with `start.cmd`, switch to **Receivables**, choose the workbook, read the
check, and press Create only for B (C must show 16 red rows and no Create).
