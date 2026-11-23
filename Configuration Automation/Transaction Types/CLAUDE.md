# Transaction Types

Task: **Manage Transaction Types**, code `AR_MANAGE_TRANSACTION_TYPES` (Setup and Maintenance > offering **Financials** >
functional area **Customer Billing**). **Header only.** Status summary: built 2026-11-02 and tested offline (page
matrix, Oracle replaced by ETIA-TEST's real layout); **read-only check on ETIA-TEST 2026-11-02** (sets, template, data
file, Oracle's type list, payment terms and `--plan` work); **Create PROVEN on ETIA-TEST 2026-11-02** through the
folder's own run (ZZ_TEST_TT_6421, Invoice, no payment term: COMPLETED, read back "every value as sent", no account
rows made, rerun skipped; see "Observed in the live Create"). Not yet run through the upload sheet, not yet with a
payment term, not yet seen on Oracle's screen.
The page shows it under the **Receivables** side of the Order Management | Receivables switch.

Built from the spec `TRANSACTION_TYPES_SPEC.md` in `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_spec\`
(Oracle knowledge from the FSCR skill `pillars/erp/financials/customer-billing/manage-transaction-types`, read-only).
Code copied from `Transaction Sources/` (isolation rule: no import across folders) and changed.

**Requests that reach Oracle use neutral ZZ_TEST_ names only** (user's rule, 2026-11-01): never Corsair, Intel, AMD or
NVIDIA, not even in a read-only check. The Corsair story stays in the local sample workbooks and offline tests.

**No accounting fields** (user's rule, 2026-11-02): the reference account table `AR_REF_ACCT_TRX_TYPE` (business unit,
ledger, every account segment) and `AllocateTaxFreight` are never sent: account segments can create new account
combinations in the shared pod's ledger (FSCR: "may create a valid combination and is not read-only"). The import file
carries `AR_REF_ACCT_TRX_TYPE.csv` as its header line only.

What it is: a transaction type names a kind of Receivables transaction (Invoice, Debit Memo, ...) and how it behaves
(open receivable, post to GL, freight, tax, application, default payment term). Transaction sources and AutoInvoice
point at it.

## Input rules

**Nothing is defaulted** (FSCR: "Require explicit create values ... do not invent defaults"). REQUIRED (ask in one
plain message if missing; never ask for codes or IDs): Name (at most 20 characters, no outer spaces), Set Code, Class
(Invoice or Debit Memo), Status (Active / Inactive), From Date (YYYY-MM-DD), Open Receivable, Post to GL, Allow Freight,
Tax Calculation, Natural Application Only, Allow Overapplication (each Yes / No; Natural Application Only and Allow
Overapplication not both Yes), Creation Sign (Positive Sign only), Transaction Status (Open only), Printing Option
(Print / Do Not Print). An existing **Name + Set Code** is skipped and never changed.

OPTIONAL (empty = not sent): Item Description (at most 80 characters), To Date (not before From Date), Payment Term +
Payment Term Set (together).

Not offered in v1 (spec section 1 "Left out"): every accounting field, the other six classes (Credit Memo needs a
negative sign, FSCR verified only Positive; Deposit, Guarantee, Bills Receivable, Chargeback, Adjustment need more
setup), usage category / subclass (blocked by FSCR), credit memo and subsequent types, rule set, legal entity,
completion control and other optional flags, flexfields. Update, end-dating and deleting are not supported.

## Dependencies (the root rule: Design principles)

- **Reference data set**: must be one of `setIdSetsLOV`'s codes (read before Create); else red with the codes.
- **Payment term** (optional; name + set together, FSCR):
  - a Name on this upload's **Receivables Payment Terms** tab: the page marks the type `payment_term_pending` (registry
    `depends_on` on Name), the payment terms module runs first (registry order), the type waits while that term waits
    for a decision, and is **not sent** when the term failed or the user skipped it. At Create the folder reads Oracle's
    terms again; still missing in that set -> not sent, nothing saved;
  - otherwise it must already be in Oracle in that set: read from the Receivables payment terms task's data file
    (`AR_MANAGE_RECEIVABLES_PAYMENT_TERMS`, read-only, only when a type names a term); else red with the terms Oracle
    has in that set (and the set it has the name in, if another).
  - `depends_on` matches the term's Name only; Payment Term Set should be that row's Set Code.
- Used by: **Transaction Sources** (default transaction type, `TrxTypeName` + `InvTrxTypeSetCode`): **not wired yet**.
  Wiring it needs a column on the Transaction Sources tab, that folder's rules and file builder, and `depends_on` on this
  group; a group has ONE `depends_on` today (Transaction Sources already uses it for grouping rules), so
  `workbook.depends()` / `server.hold_dependents()` must accept a list (a shared-code addition). This group is placed
  before Transaction Sources in the registry so the run order is already right.
- Map: `fscr-main\_fscr_spec\DEPENDENCY_MAP.md`.

## Route status

- **Create: setup task process without a browser** (`setupTaskCSVImports/AR_MANAGE_TRANSACTION_TYPES`, Basic auth):
  **PROVEN on ETIA-TEST 2026-11-02** (1 type, COMPLETED, import under a minute, 130 s for the whole run). If Oracle
  refuses the call: plain card "... no other way was tried".
- **Layout: the task's own empty template** (`setupTaskCSVTemplateExports`): **PROVEN read-only 2026-11-02**.
- **Data file** (`setupTaskCSVExports`): **PROVEN read-only**; on ETIA-TEST it lists **all 21 types** (the same 21 as
  Oracle's type list), unlike Transaction Sources' data file.
- **Oracle's type list** (`transactionTypesLOV`, GET, paged, no filter: no name is sent): **PROVEN read-only
  2026-11-02** (21 types). Kept as a second source for existing names and as the read-back fallback (name, set,
  description only; the result says so), in case a new type isn't in the data file.
- **Reference data sets** (`setIdSetsLOV`): PROVEN (37 sets).
- **Receivables payment terms data file** (read for term names + sets): PROVEN read-only (`--plan` listed 12 terms in
  COMMON, including 30 Net and IMMEDIATE). Whether it lists every term is not proven.
- **`--plan` on Oracle: PROVEN read-only 2026-11-02** (neutral requests, see Observed).
- **Read-back after a Create**: **PROVEN 2026-11-02** from the data file (every sent value); the type-list fallback
  was not needed and is tested offline only.

## How to do it

```
python "Transaction Types/run.py" --check                  # read-only: sets, layout, data file, type list
python "Transaction Types/run.py" --plan '<JSON list>'     # read-only: the page's preview check
python "Transaction Types/run.py" --run-batch '<JSON list>'   # every type of an upload in one go
python "Transaction Types/run.py"                          # the types in request.json (ZZ_TEST_TT_6421)
```

Order: rules without Oracle (`tt_rules.py`), read-only reads (sets, template, data file, type list, payment terms when
needed), then for Create: names read again (data file + type list), pending payment terms read again, ONE file for
every new type built from the template (`tt_package.py`), sent once, polled every 10 s, Oracle's log saved in `_work/`,
then a fresh data file compared (the type list for a type the data file doesn't show). **Never resubmitted**; the
read-back decides.

## File layout (read from the pod on every run)

Only the two entity names are fixed in code (`tt_package.ENTITIES`): `AR_TRANSACTION_TYPE` (our rows) and
`AR_REF_ACCT_TRX_TYPE` (header line only). Everything else comes from the template (entity order, members in its zip
order, metadata byte for byte, headers from each CSV's first line, types by name). Audit columns always empty; dates
ISO. **Real layout**: `manual-notes/pod_layout_etia_test/` (ETIA-TEST template 2026-11-02, header lines and metadata
only); the offline stub uses it. The STAND-IN (`standin_layout_NOT_FROM_ORACLE/`, from FSCR's contract) is kept for
comparison only (its headers are identical).

## Observed in the read-only check, 2026-11-02 (ETIA-TEST, ORACLE_ENV test; facts only)

- Template call COMPLETED; release 11.13.26.10.0, ProcessEnv etia-test; metadata 5,723 bytes.
- Entity order AR_TRANSACTION_TYPE, AR_REF_ACCT_TRX_TYPE; zip members in the same order; **headers, NodeSequence (1, 2),
  node paths and field types exactly FSCR's** (87 and 24 columns).
- **Data file: 21 types, the same 21 as Oracle's type list** (all in COMMON): 12 Invoice, 9 Credit Memo, no Debit Memo;
  Invoice, Credit Memo, Intercompany, BUU1, JV, PA, PSFT types and 8 of Oracle's own `ORA_` types. 3 reference account
  rows (BUU1 Invoice and BUU1 Credit Memo for BU BUU1, Invoice for AMNA BU); the other 18 types have none.
- Values the pod's types use (facts, not offered unless verified): CreationSign **A, P and N** (FSCR verified only P);
  DefaultStatus OP everywhere; DefaultPrintingOption PRI, and N on the PSFT types; Status A or empty (seeded types);
  Natural Application Only and Allow Overapplication: one of them Yes on most types, both No on ORA_PA_Prepayment.
  Payment terms named: 30 Net (on the types Credit Memo and PA Invoice), IMMEDIATE (on PA Internal Invoice), all with
  DefaultTermSetCode COMMON.
- 37 reference data sets. Receivables payment terms data file: 12 names in COMMON (001 PT, 15NET, 30 Net, Ahsan PT,
  IMMEDIATE, Net15, ORA_HES, ZZFSCR N45 4203, ZZRPT 9721, custom pt, test, test2).
- `--plan` with three neutral requests: "2 new, 0 already in Oracle, 1 with problems": ZZ_TEST_TT_6421 (Invoice, no term)
  new; ZZ_TEST_TT_6422 (Debit Memo, term 30 Net in COMMON) new; ZZ_TEST_TT_6423 (term ZZ_TEST_NO_SUCH_TERM) red with
  the 12 terms as the fix. Nothing was created or changed.
- Step times: `--check` 65 s (05:30:42-05:31:47), `--plan` with 3 requests 81 s (05:32:19-05:33:40). No network blip.

## Observed in the live Create, 2026-11-02 (ETIA-TEST, ORACLE_ENV test; neutral name only)

Run once through the folder's plain run (`--file request.json`, the same flow as `--run-batch`), with a wrapper that only
kept `_work/`. Kept files: `_work/live_create_20261102/` (sent file, data files before / names / after, template,
Oracle's ProcessLog and two reports, the run's output; never shared).

| Step | Time (+0500) | Seconds | Result |
|---|---|---|---|
| `--plan` (request.json) | 05:39:42-05:40:43 | 61 | "1 new, 0 already in Oracle, 0 with problems" |
| Create | 05:40:55-05:43:06 | 130 | "Created 1 of 1", "every value as sent" |
| Type list read | 05:43:20 | a few | 22 types (was 21), ZZ_TEST_TT_6421 in Common Set, description as sent |
| Rerun | 05:43:31-05:44:23 | 51 | "Created 0 of 1 transaction types, 1 already there"; nothing sent, no import process |

- Import process 100004734402166, Oracle request 4,429,252, COMPLETED. ProcessLog: business object "Receivables
  Transaction Type Reference Account", detail object TransactionType "A total of 1 rows were processed. 0 rows of them
  failed"; "Receivables Transaction Type ... already processed"; Total Objects Succeeded 2, Failed 0. The import took
  under a minute (sent 05:42:13, after-read saved 05:43:06).
- Sent: one row in AR_TRANSACTION_TYPE; AR_REF_ACCT_TRX_TYPE header line only. After: the type in the data file under
  **AR_TRANSACTION_TYPE** (21 -> 22 rows); **AR_REF_ACCT_TRX_TYPE still 3 rows, none for the new type** (no accounts were
  made); every other type's rows identical before and after.
- Compared from the data file, all equal: Name, SetCode, Description, Type INV, Status A, StartDate (2026/11/01 = sent
  2026-11-01), PostToGl Y, AccountingAffectFlag Y, AllowFreightFlag Y, TaxCalculationFlag Y, NaturalApplicationOnlyFlag
  N, AllowOverapplicationFlag N, CreationSign P, DefaultStatus OP, DefaultPrintingOption PRI. Oracle filled only the audit
  columns; everything we leave empty stayed empty (no payment term, no end date, no accounts). The type list confirms
  only name, set name and description.
- So, answered: the route works for this task; Oracle takes a new type with **Post to GL Yes and no reference
  accounts**, and with **Natural Application Only and Allow Overapplication both No**; a new type shows in the data file.
- Nothing refused, so the length limits and how the log names a failed row are still unknown.
- Not seen on Oracle's screen: the saved browser sign-in had expired (checked earlier the same day; not renewed, the
  user does no manual steps). Where to look: Setup and Maintenance > Financials > Customer Billing > Manage Transaction
  Types, search Name ZZ_TEST_TT_6421 (Reference Data Set Common Set).

## Receivables sheet test (2026-11-02)

Ran together with the other three Receivables modules from one upload (workbook A in `Transaction Types/manual-notes/receivables_sheet_test/`) through the page's server code on ETIA-TEST: ZZ_TEST_TT_3113 (Invoice, payment term ZZ_TEST_PT_311 / COMMON from the same sheet) created after the term, read back "every value as sent" (first live type with a payment term; depends_on proven live); ZZ_TEST_TT_6421 on the same sheet skipped; rerun skipped, nothing sent. Since then (2026-11-02) its registry group has `"uses_browser": false`: a sheet with only Receivables modules is checked and created without the Oracle browser sign-in. Details: root CLAUDE.md > The upload sheet > Receivables sheet test.

## Page interface

Upload sheet tab **Transaction Types** (Name *, Set Code *, Item Description, Class *, Status *, From Date *, To Date,
Open Receivable *, Post to GL *, Allow Freight *, Tax Calculation *, Natural Application Only *, Allow Overapplication
*, Creation Sign *, Transaction Status *, Printing Option *, Payment Term, Payment Term Set), registry group
"Transaction Types", area Receivables, after AutoInvoice Grouping Rules and before Transaction Sources, with
`depends_on` on Receivables Payment Terms. `--plan` = `oracle_check`; `--run-batch` = `batch_run`; `ask_on_refusal` on
every column's key. Sheet guide: `sheet_fields.md`.

Offline tests: `python page/matrix/test_matrix.py` (generic 8 behaviours + 2 check cases, plus 14 cases running this
folder's real code through `page/matrix/stub_transaction_types.py`, including a payment term and a type in one upload).

## Open items (for the live Create)

1. ~~Route~~, ~~Post to GL without accounts~~, ~~both application flags No~~: answered by the live Create 2026-11-02.
   Still open: whether Oracle requires Open Receivable Yes with Post to GL Yes (not tried).
2. A type with a payment term (next live step: an existing term such as 30 Net in COMMON), then a sheet with a term
   and a type that names it.
3. Name 20 / Description 80 limits on this pod; how the log names a failed row.
4. Whether the payment terms data file lists every term.
5. Not seen on Oracle's screen (needs a valid saved sign-in).
6. A test type can't be deleted (no physical delete).

## Sample requests

- "Create an invoice transaction type ZZ_TEST_TT_6421 in COMMON from 2026-11-01: open receivable, post to GL, freight,
  tax calculation Yes; natural application and overapplication No; Positive Sign, Open, Print."
- "Same as a debit memo ZZ_TEST_TT_6422 with payment term 30 Net (COMMON)."

## Related folders

- `Receivables Payment Terms/`: a type may name its terms (registry `depends_on`); no code shared.
- `Transaction Sources/`: will name a type as its default transaction type (not wired yet; see Dependencies).

## Known gotchas

- 2026-11-02: the pod's types use creation signs A (any) and N (negative) besides P; FSCR verified only P, so v1 offers
  Positive Sign only and Invoice / Debit Memo only.

## Material (test records in Oracle)

On ETIA-TEST since 2026-11-02 (can't be deleted):
- ZZ_TEST_TT_6421: Invoice, COMMON, "ZZ test transaction type (invoice)", Active, from 2026-11-01; open receivable, post to GL, freight, tax calculation Yes; natural application and overapplication No; Positive Sign, Open, Print; no payment term; no accounts.

## Time log

| Phase | Start | Finish | Minutes |
|---|---|---|---|
| First live Create (1 type), read-back, rerun, docs | 2026-11-02 05:39:41 +0500 | 2026-11-02 05:45:16 +0500 | 5 (5 min 36 s) |
| Spec + offline build + read-only check | 2026-11-02 05:12:50 +0500 | 2026-11-02 05:38:07 +0500 | 25 (25 min 17 s) |
