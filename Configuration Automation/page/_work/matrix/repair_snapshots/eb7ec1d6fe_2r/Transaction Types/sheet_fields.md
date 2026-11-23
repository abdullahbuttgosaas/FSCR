# Transaction Types: sheet columns, request keys and Oracle's columns

Tab "Transaction Types" in `page/sheet_definition.json` (2026-11-02), one row per type -> `AR_TRANSACTION_TYPE`.
**Header only**: `AR_REF_ACCT_TRX_TYPE` (reference accounts per business unit) is never filled. Every rule is checked
by `run.py --plan` (`tt_rules.py`); the page only reads types and required columns. Examples follow the local Corsair
story (sample workbook only; requests that reach Oracle use ZZ_TEST_ names).

**Nothing is filled in for you.** FSCR: "Require explicit create values ... do not invent defaults". Every column with *
must be filled; an empty one is red.

| Column | Key | Oracle column | Rule | Corsair example |
|---|---|---|---|---|
| Name * | name | Name | at most 20 characters, no outer spaces; existing Name + Set Code = skipped | CORSAIR OEM INVOICE |
| Set Code * | set_code | SetCode | one of Oracle's reference data sets | COMMON |
| Item Description | description | Description | at most 80 characters | OEM invoices to Intel, AMD and NVIDIA from Order Management |
| Class * | trx_class | Type | Invoice = INV, Debit Memo = DM (the other six classes are not offered yet) | Invoice |
| Status * | status | Status | Active = A, Inactive = I | Active |
| From Date * | from_date | StartDate | YYYY-MM-DD | 2026-11-01 |
| To Date | to_date | EndDate | YYYY-MM-DD, not before From Date | (empty) |
| Open Receivable * | open_receivable | AccountingAffectFlag | Yes / No | Yes |
| Post to GL * | post_to_gl | PostToGl | Yes / No (a flag only; no accounts are set) | Yes |
| Allow Freight * | allow_freight | AllowFreightFlag | Yes / No | Yes |
| Tax Calculation * | tax_calculation | TaxCalculationFlag | Yes / No | Yes |
| Natural Application Only * | natural_application | NaturalApplicationOnlyFlag | Yes / No; not Yes together with Allow Overapplication | No |
| Allow Overapplication * | allow_overapplication | AllowOverapplicationFlag | Yes / No | No |
| Creation Sign * | creation_sign | CreationSign | Positive Sign = P (the only verified value) | Positive Sign |
| Transaction Status * | transaction_status | DefaultStatus | Open = OP (the only verified value) | Open |
| Printing Option * | printing_option | DefaultPrintingOption | Print = PRI, Do Not Print = NOT | Print |
| Payment Term | payment_term | DefaultTermName | a Receivables payment term: a Name on the Receivables Payment Terms tab (created first; the type waits) or one already in Oracle in the Payment Term Set | CRSR NET 45 |
| Payment Term Set | payment_term_set | DefaultTermSetCode | required with Payment Term; a reference data set | COMMON |

**Not offered yet, and why** (always empty in v1):

| Oracle fields | Why |
|---|---|
| Every accounting field: the whole reference account table (business unit, ledger, receivable / revenue / tax / freight / unearned / unbilled / clearing / deposit offset / distribution set / bills receivable account segments) and AllocateTaxFreight | user's rule for this version: sending account segments can create new account combinations in the shared pod's general ledger, which can't be removed (FSCR: "may create a valid combination and is not read-only") |
| AdjPostToGlFlag, AllowFutureAcctDateFlag | accounting flags, kept out with the accounts |
| UsageCategoryCode, TrxSubclassCode | blocked by FSCR until the pod's codes are verified |
| Credit memo type, subsequent type | a type naming another type; later |
| Application rule set, legal entity | no module or proven read-only list yet |
| Completion control, signed, drawee issued, exclude from late charges, magnetic format, document type, flexfields | optional; not needed for an Invoice / Debit Memo header |
| Audit columns | always empty |

Local workbooks in `manual-notes/`: `Receivables_Corsair_sample.xlsx` (the whole Receivables story in one workbook:
3 payment terms, 2 grouping rules, 4 transaction types (three name a payment term on the same sheet) and 3 transaction
sources; the sources' default transaction type is not wired yet) and `Transaction_Types_TEST_bad.xlsx` (one mistake
per row: name 22 characters, description 85, Credit Memo, Post to GL empty, natural application + overapplication both
Yes, Negative Sign, To before From, term without set, a term nowhere, an unknown set, transaction status Closed, a
space at the end of the name).
