# Transaction Sources

Task: **Manage Transaction Sources**, code `AR_MANAGE_TRANSACTION_SOURCES` (Setup and Maintenance > offering
**Financials** > functional area **Customer Billing**). Status summary: built 2026-11-01 and tested offline (page
matrix, Oracle replaced by ETIA-TEST's real layout); **read-only check on ETIA-TEST 2026-11-01** (sets, template, data
file, Oracle's source list, grouping rules and `--plan` work); **Create PROVEN on ETIA-TEST 2026-11-02** through the
folder's own run (ZZ_TEST_TS_7731 Manual and ZZ_TEST_TS_7732 Imported with grouping rule DEFAULT, one import, both read
back "every value as sent", rerun skipped both; see "Observed in the live Create"). Not yet run through the upload sheet,
not yet seen on Oracle's screen. The page shows it under the **Receivables** side of the Order Management | Receivables switch.

Built from the spec `TRANSACTION_SOURCES_SPEC.md` in `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_spec\`
(Oracle knowledge from the FSCR skill `pillars/erp/financials/customer-billing/manage-transaction-sources`, read-only).
Code copied from `AutoInvoice Grouping Rules/` (isolation rule: no import across folders) and changed.

**Requests that reach Oracle use neutral ZZ_TEST_ names only** (user's rule, 2026-11-01): never Corsair, Intel, AMD or
NVIDIA, not even in a read-only check. The Corsair story stays in the local sample workbooks and offline tests.

What it is: a transaction source says where Receivables transactions come from and how they are numbered. Manual =
entered on screen; Imported = filled by AutoInvoice from another application (Order Management uses "Distributed Order
Orchestration" on ETIA-TEST), which is where a grouping rule applies.

## Input rules

REQUIRED (ask in one plain message if missing; never ask for codes or IDs):
- Name: not starting with `ORA_`, no space at the start or end. Capitals and spaces count. An existing **Name + Set
  Code** is skipped and never changed.
- Set Code: one of Oracle's reference data sets (exact code). **Never defaulted.**
- Item Description: Oracle needs it for a new source (FSCR "Core create information").
- From Date (YYYY-MM-DD). **Never defaulted** (FSCR: "Supply ... the active-from date").
- Last Number when Automatic Numbering is Yes: a whole number, 1 or more; the numbering starts there. **Never
  invented** (FSCR: "Do not invent a number; block the record").

OPTIONAL (FSCR's create defaults, shown on the preview as filled in):

| Request key | Sheet column | Default | Rule |
|---|---|---|---|
| source_type | Type | Manual (INV) | Manual / Imported (FOREIGN) |
| status | Status | Active (A) | Active / Inactive |
| auto_numbering | Automatic Numbering | Yes (Y) | Yes / No; with No, Last Number stays empty |
| invalid_lines | Invalid Lines | Reject Invoice (Reject) | Create Invoice / Reject Invoice |
| grouping_rule | Grouping Rule | none | Imported only; see Dependencies |

Never on the sheet (v1): default transaction type, credit transaction source, legal entity, document type, End Date,
the AutoInvoice "...Rule" options, flexfields; always empty. Update, end-dating and deleting are not supported.
No length limits are in FSCR's files (Name, Description); Oracle's import decides (a "too long" refusal asks).

## Dependencies (the root rule: Design principles)

- **Reference data set**: must be one of `setIdSetsLOV`'s codes (read before Create); else red with the codes.
- **Grouping rule** (Imported sources only):
  - a Name on this upload's **AutoInvoice Grouping Rules** tab: the page marks the source `grouping_rule_pending`
    (registry `depends_on`), the grouping rules module runs first (registry order), the source waits while that rule
    waits for a decision, and is **not sent** when the rule failed or the user skipped it. At Create the folder reads
    Oracle's grouping rules again; still missing -> not sent, nothing saved;
  - otherwise it must already be in Oracle: read from the grouping rules task's data file
    (`AR_MANAGE_AUTOINVOICE_GROUPING_RULES`, read-only, only when a source names one); else red with Oracle's names.
  - `GroupName` on create is outside FSCR's evidenced create fields, but **accepted and kept on ETIA-TEST
    2026-11-02** (ZZ_TEST_TS_7732 with DEFAULT: the data file after shows GroupName DEFAULT; no warning).
- Not in v1: transaction type (future Transaction Types module, same `depends_on` pattern; `transactionTypesLOV`
  exists), credit source (second import pass), legal entity, document type.
- Map: `fscr-main\_fscr_spec\DEPENDENCY_MAP.md`.

## Route status

- **Create: setup task process without a browser** (`setupTaskCSVImports/AR_MANAGE_TRANSACTION_SOURCES`, Basic auth):
  **PROVEN on ETIA-TEST 2026-11-02** (2 sources in one import, COMPLETED, about 1 minute for the import, 184 s for the
  whole run). If Oracle refuses the call: plain card "... no other way was tried".
- **Layout: the task's own empty template** (`setupTaskCSVTemplateExports`): **PROVEN read-only 2026-11-01**.
- **Data file** (`setupTaskCSVExports`): **PROVEN read-only**, but it lists **only some sources** (1 of 22 on
  ETIA-TEST before the Create), so it is not enough to find existing sources. Sources we create **are** listed, under
  AR_BATCH_SOURCE (2026-11-02), so the read-back compares every value from it.
- **Oracle's source list** (`transactionSourcesLOV`, GET, paged, no filter: no name is sent): **PROVEN read-only
  2026-11-01** (22 sources). Used for existing names and, when the data file doesn't list a new source, for the
  read-back (name, set and description only; the result says so).
- **Reference data sets** (`setIdSetsLOV`): PROVEN (37 sets).
- **Grouping rules data file** (read for rule names): PROVEN read-only (`--plan` found DEFAULT).
- **`--plan` on Oracle: PROVEN read-only 2026-11-01** (neutral requests, see Observed).
- **Read-back after a Create**: **PROVEN 2026-11-02** from the data file (every sent value); the source-list fallback
  (name, set, description only) was not needed and is tested offline only.

## How to do it

```
python "Transaction Sources/run.py" --check                  # read-only: sets, layout, data file, source list
python "Transaction Sources/run.py" --plan '<JSON list>'     # read-only: the page's preview check
python "Transaction Sources/run.py" --run-batch '<JSON list>'   # every source of an upload in one go
python "Transaction Sources/run.py"                          # the sources in request.json (ZZ_TEST_TS_7731, 7732)
```

Order: rules without Oracle (`ts_rules.py`), read-only reads (sets, template, data file, source list, grouping rules
when needed), then for Create: names read again (data file + source list), pending grouping rules read again, ONE file
for every new source built from the template (`ts_package.py`), sent once, polled every 10 s, Oracle's log saved in
`_work/`, then a fresh data file (and the source list for a source the data file doesn't show) compared. **Never
resubmitted**; the read-back decides.

## File layout (read from the pod on every run)

Only the two entity names are fixed in code (`ts_package.ENTITIES`): `ORA_AR_TXN_BATCH_SOURCE` (the create target; our
rows) and `AR_BATCH_SOURCE` (sent as its header line only; FSCR: "create persists through AR_BATCH_SOURCE"). Everything
else comes from the template (entity order, members in its zip order, metadata byte for byte, headers from each CSV's
first line, types by name). Audit and derived columns (DefaultInvTrxType, LegalEntityName) always empty; dates ISO.
**Real layout**: `manual-notes/pod_layout_etia_test/` (ETIA-TEST template 2026-11-01, header lines and metadata only);
the offline stub uses it. The earlier STAND-IN (`standin_layout_NOT_FROM_ORACLE/`, from FSCR's contract) is kept for
comparison only.

## Observed in the read-only check, 2026-11-01 (ETIA-TEST, ORACLE_ENV test; facts only)

- Template call COMPLETED; release 11.13.26.10.0, ProcessEnv etia-test; template = data file layout; metadata 9,305
  bytes.
- Entity order ORA_AR_TXN_BATCH_SOURCE, AR_BATCH_SOURCE; zip members in the same order. Headers: exactly FSCR's lists
  (111 and 109 columns; AR_BATCH_SOURCE lacks BatchSourceName and CmBatchSrcSetCode). **NodeSequence: ORA_ = 2,
  AR_ = 1** (FSCR's adapter pins 1 and 2); field lists the same as FSCR's, node paths the same.
- **Data file: 1 source** (AR_BATCH_SOURCE: Distributed Order Orchestration, COMMON, Imported, Invalid Lines Create,
  grouping rule DEFAULT, from 2009/04/28); ORA_AR_TXN_BATCH_SOURCE: 0 rows.
- **Oracle's source list: 22 sources**, all in Common Set (COMMON): Manual, Intercompany, Global Intercompany,
  Distributed Order Orchestration, CONTRACT INVOICES, CONTRACT INTERNAL INVOICES, Channel Revenue Management, Oracle
  DOO Integrated Subscriptions, Oracle Joint Ventures, PSFT Migration, and 12 of Oracle's own `ORA_` sources. Its
  fields: Name, SetName, Description, TransactionSourceId.
- 37 reference data sets.
- `--plan` with three neutral requests: "2 new, 0 already in Oracle, 1 with problems": ZZ_TEST_TS_7731 (Manual) new;
  ZZ_TEST_TS_7732 (Imported, grouping rule DEFAULT, found in Oracle's grouping rules) new; ZZ_TEST_TS_7733 (rule
  ZZ_TEST_NO_SUCH_RULE) red. Nothing was created or changed.
- Step times: `--check` 74 s (it reads the source list too), `--plan` with 3 requests 121 s.
- A first `--check` at 23:43 failed before reaching Oracle (this PC couldn't look up the pod's host name); the next try
  a few seconds later worked.

## Observed in the live Create, 2026-11-02 (ETIA-TEST, ORACLE_ENV test; neutral names only)

Run once through the folder's plain run (`--file request.json`, same flow as `--run-batch`), with a wrapper that only
kept `_work/`. Kept files: `_work/live_create_20261102/` (sent file, data files before / names / after, template,
grouping rules file, Oracle's ProcessLog and two reports, the run's output; never shared).

| Step | Time (+0500) | Seconds | Result |
|---|---|---|---|
| `--check` (first try) | 04:54:44 | 14 | failed before Oracle: the pod's host name couldn't be looked up (same blip as 2026-11-01) |
| `--check` | 04:55:22-04:56:38 | 76 | OK (37 sets, template COMPLETED, data file 1 source, source list 22) |
| `--plan` | 04:56:38-04:58:31 | 113 | "2 new, 0 already in Oracle, 0 with problems" |
| Create | 04:58:43-05:01:49 | 184 | "Created 2 of 2", both "every value as sent" |
| Source list read | 05:02:08-05:02:11 | 3 | 24 sources, both new ones (Common Set, description as sent) |
| Rerun | 05:02:21-05:03:33 | 71 | "Created 0 of 2 ..., 2 already there"; nothing sent, no import process |
| Saved sign-in check | after the rerun | 16 | expired (saved 2026-10-30): not seen on screen |

- Import process 100004734400090, Oracle request 4,429,165, COMPLETED. ProcessLog: TransactionBatchSource "A total of 2
  rows were processed. 0 rows of them failed"; CmTransactionBatchSource 0 rows; Total Objects Succeeded 2, Failed 0.
- Sent: both rows in ORA_AR_TXN_BATCH_SOURCE (AR_BATCH_SOURCE header only). After: both in the data file under
  **AR_BATCH_SOURCE** (now 3 rows with Distributed Order Orchestration, unchanged); ORA_ 0 rows.
- Compared from the data file: Name, SetCode, Description, Status, LastBatchNum, AutoTrxNumberingFlag, BatchSourceType,
  InvalidLinesRule, StartDate, GroupName. Oracle filled only the audit columns; everything we leave empty stayed empty
  (transaction type, credit source, legal entity, AutoInvoice "...Rule" options). The source list confirms only name,
  set name and description.
- **Grouping rule DEFAULT on ZZ_TEST_TS_7732: kept** (GroupName DEFAULT in the data file after).
- Nothing refused, so length limits and how the log names a failed row are still unknown.
- Guess, not proven: the data file seems to list only sources that aren't untouched seed data (Distributed Order
  Orchestration was changed by a user in 2025).

## Receivables sheet test (2026-11-02)

Ran together with the other three Receivables modules from one upload (workbook A in `Transaction Types/manual-notes/receivables_sheet_test/`) through the page's server code on ETIA-TEST: ZZ_TEST_TS_3114 (Imported, COMMON, grouping rule ZZ_TEST_AG_3112 from the same sheet) created after the rule, read back "every value as sent" (the page's depends_on proven live); rerun skipped, nothing sent. Details: root CLAUDE.md > The upload sheet > Receivables sheet test.

## Page interface

Upload sheet tab **Transaction Sources** (Name *, Set Code *, Item Description *, Type, From Date *, Status, Automatic
Numbering, Last Number, Invalid Lines, Grouping Rule), registry group "Transaction Sources", area Receivables, after
AutoInvoice Grouping Rules, with `depends_on` on it. `--plan` = `oracle_check`; `--run-batch` = `batch_run`;
`ask_on_refusal` on name, set_code, description, source_type, from_date, status, last_number, invalid_lines,
grouping_rule. The page refuses technical words in plain texts, and "Imported" contains one, so texts say "AutoInvoice
source" (the drop-down keeps Oracle's word Imported).

Offline tests: `python page/matrix/test_matrix.py` (generic 8 behaviours + 2 check cases, plus 14 cases running this
folder's real code through `page/matrix/stub_transaction_sources.py`, including a rule and a source in one upload).

## Open items

1. Name and Description length limits; how the log names a failed row (nothing refused yet).
2. Whether AutoInvoice can use an Imported source whose "...Rule" options are empty (Oracle accepted it; not used yet).
3. Not seen on Oracle's screen (Setup and Maintenance > Financials > Customer Billing > Manage Transaction Sources,
   search ZZ_TEST_TS): needs a valid saved sign-in.
4. Not yet run through the upload sheet (with a grouping rule on the same sheet).
5. The test sources can't be deleted (their numbering sequences stay).

## Sample requests

- "Create a manual transaction source ZZ_TEST_TS_7731 in COMMON from 2026-11-01, automatic numbering starting at 1."
- "New AutoInvoice transaction source ZZ_TEST_TS_7732 in COMMON using grouping rule DEFAULT."

## Related folders

- `AutoInvoice Grouping Rules/`: a source may name its rules (registry `depends_on`); its code was copied, no import.
- Future Transaction Types: a source will name a default transaction type (same pattern).

## Known gotchas

- 2026-11-01: the task's data file lists only some sources (1 of 22 on ETIA-TEST). Never decide "new" from it alone:
  use Oracle's source list too.
- 2026-11-01: ETIA-TEST's NodeSequence values are the reverse of FSCR's; never fix them in code.

## Material (test records in Oracle)

On ETIA-TEST since 2026-11-02 (can't be deleted):
- ZZ_TEST_TS_7731: Manual, COMMON, "ZZ test transaction source (manual)", Active, from 2026-11-01, numbering from 1,
  Reject.
- ZZ_TEST_TS_7732: Imported, COMMON, "ZZ test transaction source (autoinvoice)", Active, from 2026-11-01, numbering
  from 1, Reject, grouping rule DEFAULT.

## Time log

| Phase | Start | Finish | Minutes |
|---|---|---|---|
| Spec + offline build + read-only check | 2026-11-01 23:29:24 +0500 | 2026-11-01 23:55:24 +0500 | 26 (26 min 0 s) |
| First live Create (2 sources), read-back, rerun, docs, matrix | 2026-11-02 04:54:15 +0500 | 2026-11-02 05:07:32 +0500 | 13 (13 min 17 s) |
