# Transaction Sources: sheet columns, request keys and Oracle's columns

Tab "Transaction Sources" in `page/sheet_definition.json` (2026-11-01), one row per source -> `ORA_AR_TXN_BATCH_SOURCE`
(the create target; Oracle then shows it in `AR_BATCH_SOURCE`). Every rule is checked by `run.py --plan`
(`ts_rules.py`); the page only reads types and required columns. Examples follow the local Corsair story (sample
workbook only; requests that reach Oracle use ZZ_TEST_ names).

| Column | Key | Oracle column | Rule / default | Corsair example |
|---|---|---|---|---|
| Name * | name | Name | not starting ORA_, no outer spaces; existing Name + Set Code = skipped | CORSAIR OEM ORDERS |
| Set Code * | set_code | SetCode | one of Oracle's reference data sets; never defaulted | COMMON |
| Item Description * | description | Description | required by Oracle for a new source | Imported OEM order lines from Order Management for Intel, AMD and NVIDIA |
| Type | source_type | BatchSourceType | Manual = INV, Imported = FOREIGN; empty = Manual | Imported |
| From Date * | from_date | StartDate | YYYY-MM-DD; never filled in for you | 2026-11-01 |
| Status | status | Status | Active = A, Inactive = I; empty = Active | (empty) |
| Automatic Numbering | auto_numbering | AutoTrxNumberingFlag | Yes / No; empty = Yes | Yes |
| Last Number | last_number | LastBatchNum | with Yes: required, whole, 1 or more (the numbering starts there); with No: empty | 100000 |
| Invalid Lines | invalid_lines | InvalidLinesRule | Create Invoice / Reject Invoice; empty = Reject Invoice | (empty) |
| Grouping Rule | grouping_rule | GroupName | Imported only; a Name on the AutoInvoice Grouping Rules tab (created first, the source waits) or a rule already in Oracle | CORSAIR OEM BY ORDER REFERENCE |
| (none) | | transaction type, credit source, legal entity, document type, EndDate, AutoInvoice "...Rule" options, flexfields | always empty | |
| (none) | | audit and derived columns (DefaultInvTrxType, LegalEntityName) | always empty | |

Local workbooks in `manual-notes/`: `Receivables_Corsair_sample.xlsx` (payment terms, grouping rules and sources of the
Corsair story; the two Imported sources name grouping rules on the same sheet) and `Transaction_Sources_TEST_bad.xlsx`
(one mistake per row: ORA_ name, no description, no From Date, Last Number 0, numbering No with a number, grouping rule
on a Manual source, a rule nowhere, an unknown set).
