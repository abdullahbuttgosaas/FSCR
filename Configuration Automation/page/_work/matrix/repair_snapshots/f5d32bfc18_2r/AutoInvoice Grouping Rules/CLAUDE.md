# AutoInvoice Grouping Rules

Task: **Manage AutoInvoice Grouping Rules**, code `AR_MANAGE_AUTOINVOICE_GROUPING_RULES` (Setup and Maintenance >
offering **Financials** > functional area **Customer Billing**). Status summary: built 2026-11-01; **read-only live
check on ETIA-TEST 2026-11-01** (template call, data file and `--plan` work; real layout saved); **Create PROVEN on
ETIA-TEST 2026-11-01** through the folder's command (`--run-batch`, no browser): `ZZ_TEST_AG_5317` created, read back
"every value as sent", the other 8 rules unchanged, a rerun skipped it. Not yet run through the page's upload sheet;
not yet seen on Oracle's screen (the saved browser sign-in had expired). Offline matrix runs on ETIA-TEST's real layout
(Oracle replaced). The page shows it under the **Receivables** side of the Order Management | Receivables switch.

Built from the spec `AUTOINVOICE_GROUPING_RULES_SPEC.md` in `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_spec\`
(Oracle knowledge from the FSCR skill `pillars/erp/financials/customer-billing/manage-autoinvoice-grouping-rules`,
read-only). Code copied from `Receivables Payment Terms/` (isolation rule: no import across folders) and changed.

What it is: AutoInvoice turns imported billing lines into Receivables transactions; a grouping rule says which lines
may share one invoice, debit memo or credit memo. Oracle always groups by its mandatory attributes; the rule adds
optional characteristics per transaction class (e.g. one invoice per order reference).

## Input rules

REQUIRED (ask in one plain message if missing; never ask for codes or IDs):
- Name: 1-40 characters, not starting with `ORA_` (Oracle's own rules), no space at the start or end. Capitals and
  spaces count. An existing **Name** (exact) is skipped and never changed.
- From Date (YYYY-MM-DD). **Never defaulted**: FSCR says the start date must be explicit (no import default; the
  screen's prefill is not one), so the usual "empty = Oracle's today minus one day" does NOT apply here.
- Per class row: Transaction Class, one of **Invoice**, **Debit Memo**, **Credit Memo** (codes I / D / C accepted).
  **Never defaulted.**

OPTIONAL:

| Request key | Sheet column | Default | Rule |
|---|---|---|---|
| description | Item Description | none | max 80 |
| to_date | To Date | none | folder: on or after From Date (FSCR allows equal); the sheet's shared date rule is stricter: after the From Date and after Oracle's today |
| classes[] | Grouping Rule Classes rows | none (a rule with no class rows gets a yellow note) | each class once; the same class repeated only with different Characteristics |
| classes[].characteristic | Characteristic | none (the class only) | exact name, as Oracle writes it; must already be used by a grouping rule in Oracle (see Dependencies) |

Never on the sheet (v1): Line Ordering Rule, flexfields (AttributeCategory, Attribute1-15), Consolidated Billing flag;
always empty. Update, end-dating and deleting are not supported (Oracle has no hard delete).

## Dependencies (the root rule: Design principles)

- Transaction class codes: seeded (C, D, I), nothing to read.
- **Characteristic**: Oracle has no list to read (FSCR `ora_reference_lookups.md:16`), and a name Oracle doesn't know
  makes it drop that characteristic and **save the rule without it** (a rerun skips the rule, so it can't be fixed by
  the module). So the check accepts only names a grouping rule in Oracle already uses (from the task's data file);
  any other name is **red** with Oracle's names as the fix. **Kept strict by the user's decision, 2026-11-01**, after
  the live check showed ETIA-TEST's rules use only `L.INTERFACE_LINE_ATTRIBUTE1-7`; don't accept other `L.<column>`
  names unless the user says so or a full list of Oracle's characteristics can be read.
- Line ordering rule: left out of v1 (no lookup, no FSCR contract for that task's file).
- Used by: Transaction Sources (Imported sources name a grouping rule) and Receivables System Options
  (`GroupingRuleName`). The registry keeps this group before any future Transaction Sources group.
- Map: `fscr-main\_fscr_spec\DEPENDENCY_MAP.md`.

## Route status

- **Create: setup task process without a browser** (`setupTaskCSVImports/AR_MANAGE_AUTOINVOICE_GROUPING_RULES`, Basic
  auth): **PROVEN 2026-11-01** (ETIA-TEST, `ZZ_TEST_AG_5317`; import process 100004733437943, ESS request 4,428,576,
  COMPLETED in about 21 s; whole run 124 s). Offline: PASS (matrix 2026-11-01). If Oracle refuses the call: "Oracle refused the setup task process for
  AutoInvoice grouping rules ... no other way was tried" (SETUP_NEEDED, or NO_PERMISSION on 401/403). No browser
  fallback.
- **Layout: the task's own empty template** (`setupTaskCSVTemplateExports`), fallback the data file's layout:
  **PROVEN read-only 2026-11-01** (ETIA-TEST, COMPLETED in about 35 s; template = data file's layout, metadata 5,615
  bytes both).
- **Data file** (`setupTaskCSVExports`, existing names and characteristics): **PROVEN read-only 2026-11-01** (about 40 s).
- **`--plan` on Oracle: PROVEN read-only 2026-11-01** (request.json: 1 with problems, see Observed below).
- **Read-back: a fresh data file, field by field**: **PROVEN 2026-11-01** ("every value as sent"; checked again by hand
  from the after-file).
- **Rerun skips**: **PROVEN 2026-11-01** ("Created 0 of 1 ..., 1 already there", no import sent).
- Page interface (`--spec`, `--options classes.transaction_class`, `--run`) and the upload sheet's Create: offline only.

## How to do it

```
python "AutoInvoice Grouping Rules/run.py" --check                  # read-only: layout, existing rules, characteristics
python "AutoInvoice Grouping Rules/run.py" --plan '<JSON list>'     # read-only: the page's preview check
python "AutoInvoice Grouping Rules/run.py" --run-batch '<JSON list>'   # every rule of an upload in one go
python "AutoInvoice Grouping Rules/run.py"                          # the rules in request.json
```

Order: rules without Oracle (`agr_rules.py`), then read-only reads (the template, the data file "before"), then for
Create: names read again from a fresh data file (a rule made meanwhile is skipped), ONE file for every new rule built
from the template (`agr_package.py`), sent once, polled every 10 s (30-minute limit), Oracle's log and reports saved in
`_work/`, then a fresh data file compared field by field (other rules unchanged). **Never resubmitted** after a
timeout or unknown result; the read-back decides.

Results per rule: created and checked ("every value as sent") / skipped (already there) / refused with Oracle's reason
("Nothing was saved in Oracle", INVALID_REQUEST, saved "no", a structured problem for pause-and-ask) / "saved in
Oracle, but not as sent" (VERIFY_FAILED, saved "yes"; e.g. Oracle dropped a characteristic) / "may have been saved".

## File layout (read from the pod on every run)

Only the three entity names are fixed in code (`agr_package.ENTITIES`): `AR_AI_GROUPING_RULE` (rule, key Name),
`ORA_AR_AI_GRP_TXN_TYPE` (class, + Class11, link `AR_AI_GROUPING_RULE.Name`), `ORA_AR_AI_GRP_TXN_REQUEST`
(characteristic, + FromColumnName, links `AR_AI_GROUPING_RULE.Name`, `ORA_AR_AI_GRP_TXN_TYPE.Class11`). Everything
else comes from the template: entity order (metadata rows), members in the template's order, metadata byte for byte,
each CSV's header = its first line, field types from the metadata by name, extra columns only as parent links,
quoting and line ending as the template's. FSCR's adapter pins the header and node order; this module does not.
Stops (plain, nothing built): wrong task, status not COMPLETED, an entity / member / needed column missing, an unknown
column, the template's release differing from the data file's, the template's ProcessEnv not in ORACLE_HOST.
Dates YYYY-MM-DD in the file; audit columns always empty.
**Real layout** (ETIA-TEST template of 2026-11-01, header lines and metadata only, test fixture):
`manual-notes/pod_layout_etia_test/`; the offline stub uses it. The earlier **STAND-IN** (`standin_layout_NOT_FROM_ORACLE/`,
built from FSCR's contract, NOT from Oracle) is kept only for comparison: same CSV headers, field types, node paths
and node sequences as the pod, but a different entity order, a different field order inside the metadata lists, and
an invented BatchName. None of these matter, because the module reads them from the pod.

## Observed in the read-only live check, 2026-11-01 (ETIA-TEST, ORACLE_ENV test; facts only)

- Template call and data file both COMPLETED; release 11.13.26.10.0, ProcessEnv etia-test.
- **Entity order in the metadata: ORA_AR_AI_GRP_TXN_TYPE, ORA_AR_AI_GRP_TXN_REQUEST, AR_AI_GROUPING_RULE** (not FSCR's
  node order). The zip's member order is different again: AR_AI_GROUPING_RULE.csv, ORA_AR_AI_GRP_TXN_TYPE.csv,
  ORA_AR_AI_GRP_TXN_REQUEST.csv, metadata. The metadata names the entities a second time later (another section, other
  order); the module reads only the first section.
- CSV headers: exactly FSCR's adapter lists; every value quoted, `\n` line ends. Dates in the data file are
  `1952/01/01` (slash).
- 8 rules: DEFAULT (no class rows at all), GLOBAL_INTERCOMPANY, PN GROUPING RULE, PROJECTS GROUPING RULE, and four of
  Oracle's own `ORA_` rules (ORA_PSCR, ORA_Consolidated Invoice with ConsBillingUseFlag Y, two ORA_Lease Accounting).
  So a rule without classes exists (open item 4 answered), and capitals are mixed in Oracle's own names.
- **Characteristic names are written `L.<interface column>`**: in use only `L.INTERFACE_LINE_ATTRIBUTE1` ...
  `L.INTERFACE_LINE_ATTRIBUTE7` (open item 3 answered). The sample's `PURCHASE_ORDER` is therefore red on this pod.
- Line ordering rules named by existing rules: PROJECTS LINE ORDER, ORA_Lease Accounting, ORA_Consolidated Invoice,
  ORA_Lease Accounting Revenue Equipment (a possible "already used" check if that column is added later).
- `--plan` with request.json: "0 new, 0 already in Oracle, 1 with problems": the PURCHASE_ORDER red with the seven
  names above as the fix. Nothing was created or changed.

## Observed in the live Create, 2026-11-01 (ETIA-TEST, ORACLE_ENV test; facts only)

Request (`request.json`): `ZZ_TEST_AG_5317`, description "ZZ test grouping rule: invoices by line attribute 1", From
Date 2026-11-01 (explicit), no To Date, one class Invoice with characteristic `L.INTERFACE_LINE_ATTRIBUTE1`.

| Step | Command | Time | Result |
|---|---|---|---|
| Check | `--check` | 55 s (23:15:03-23:15:58) | layout from the template, 8 rules, 7 characteristics; nothing changed |
| Preview | `--plan request.json` | 49 s | "1 new, 0 already in Oracle, 0 with problems" |
| Create + read-back | `--run-batch request.json` | 124 s (23:17:05-23:19:11) | "Created ... with 1 transaction class and 1 characteristic, and checked it in Oracle: every value as sent." |
| Rerun | `--run-batch request.json` | 63 s | "Created 0 of 1 AutoInvoice grouping rules, 1 already there."; no import sent |

Create's parts: data file "before" about 25 s, template about 25 s, names again about 25 s, the import process
COMPLETED at the second poll (about 21 s), data file "after" about 25 s.
- The import accepted ISO dates (`2026-11-01`); the data file then shows `2026/11/01`.
- The file sent: the template's zip order (RULE, TYPE, REQUEST csv, then the metadata copied byte for byte), every
  value quoted, audit columns empty: 1 rule row, 1 class row (`I`), 1 characteristic row.
- Oracle's ProcessLog (a success) names no rule and no row, only counts: "Business object: AutoInvoice Grouping Rule.
  Status: Completed successfully ... Detail Object: TransactionRequestGroupingRule ... A total of 1 rows were processed.
  0 rows of them failed"; "AutoInvoice Grouping Rule Optional Attributes" and "AutoInvoice Grouping Rule Transaction
  Class": "This object was already processed ...". Total Objects Processed 3, Failed 0. How a FAILED row is named:
  not observed.
- After-file: `ZZ_TEST_AG_5317` = 1 rule row (StartDate 2026/11/01, description as sent, CreatedBy Configuration.TEST),
  1 class row I, 1 characteristic row I / L.INTERFACE_LINE_ATTRIBUTE1. The other 8 rules: all 8 rule rows, 12 class
  rows and 20 characteristic rows identical before and after.
- Nothing refused. No retry was needed.
- Screen check: `page/look.py` stopped at once ("The saved Oracle sign-in has expired"); renewing it needs the user to
  sign in, so the record was not looked at on screen.

## Receivables sheet test (2026-11-02)

Ran together with the other three Receivables modules from one upload (workbook A in `Transaction Types/manual-notes/receivables_sheet_test/`) through the page's server code on ETIA-TEST: ZZ_TEST_AG_3112 (Invoice, L.INTERFACE_LINE_ATTRIBUTE1) created, read back "every value as sent"; the source ZZ_TEST_TS_3114 named it and ran after it; rerun skipped, nothing sent. Details: root CLAUDE.md > The upload sheet > Receivables sheet test.

## Page interface

Upload sheet tabs **AutoInvoice Grouping Rules** (Name *, Item Description, From Date *, To Date) and **Grouping
Rule Classes** (Grouping Rule Name *, Transaction Class *, Characteristic), joined by Grouping Rule Name exactly
(registry group "AutoInvoice Grouping Rules", area Receivables). `--plan` is the group's `oracle_check` and
`answer_check`; `--run-batch` the `batch_run`; `ask_on_refusal` on name, description, from_date, to_date,
transaction_class, characteristic. Yellow notes (no class rows) go into the preview's summary line.

Offline tests: `python page/matrix/test_matrix.py` (generic 8 behaviours + 2 check cases with the stub folder, plus
13 cases running this folder's real code through `page/matrix/stub_grouping.py`).

## Open items (for the live test)

1. ~~Route proof~~: accepted 2026-11-01 (`ZZ_TEST_AG_5317`).
2. ~~The real layout~~: saved 2026-11-01 (`manual-notes/pod_layout_etia_test/`).
3. ~~Characteristic names~~: `L.<column>`; ETIA-TEST uses only `L.INTERFACE_LINE_ATTRIBUTE1-7`. Decided 2026-11-01
   (user): keep the strict check. The Corsair samples now use `L.INTERFACE_LINE_ATTRIBUTE1`. What that attribute holds
   for Corsair's lines depends on the source's line transaction flexfield (not in FSCR's files): to confirm.
4. ~~Must a rule have a class?~~ No: Oracle's DEFAULT rule has none.
5. How the log names a failed row (a success names none); name case rule.
7. The upload sheet's Create through the page, and a look at the rule on Oracle's screen (needs a fresh sign-in).
6. The live test record can't be deleted afterwards (stays on the shared pod; can be end-dated later by hand).

## Discovery steps (live)

`--check` (read-only) -> record layout and characteristics here -> `--plan` with the live-test rule `ZZ_TEST_AG_5317`
(request.json: Invoice by `L.INTERFACE_LINE_ATTRIBUTE1`; neutral ZZ_TEST_ names only, never the demo names) -> Create through the
page -> read-back "every value as sent" -> the same sheet again: skipped. Mark routes PROVEN only after that.

## Sample requests

- "Create a grouping rule ZZ_TEST_AG_5317 from 2026-11-01: invoices grouped by line attribute 1
  (L.INTERFACE_LINE_ATTRIBUTE1)."
- "New AutoInvoice grouping rule ZZ_TEST_AG_6402 for credit memos, standard attributes only."
- Requests that reach Oracle use neutral ZZ_TEST_ names only (user's rule, 2026-11-01). The Corsair story (Corsair,
  Intel, AMD, NVIDIA) stays in the local sample workbooks and the offline tests.

## Related folders

- `Receivables Payment Terms/`: the code this folder was copied from; no dependency.
- Future Transaction Sources: will depend on this folder's rules (registry `depends_on`).

## Known gotchas

- 2026-11-01: ETIA-TEST's metadata order (TYPE, REQUEST, RULE) differs from FSCR's node order and from the zip's
  member order. Never fix either order in code.
- 2026-11-01: characteristic names carry an `L.` prefix (`L.INTERFACE_LINE_ATTRIBUTE1`); a bare column name is not
  what Oracle stores.

## Material (test records in Oracle)

- `ZZ_TEST_AG_5317` (ETIA-TEST, created 2026-11-01 by this folder): Invoice by L.INTERFACE_LINE_ATTRIBUTE1, from
  2026-11-01. No hard delete exists; it stays (it can be end-dated later).

## Time log

| Phase | Start | Finish | Minutes |
|---|---|---|---|
| Spec + offline build | 2026-11-01 22:27:25 +0500 | 2026-11-01 22:45:59 +0500 | 19 (18 min 34 s) |
| Read-only live check + tests on the real layout | 2026-11-01 22:54:42 +0500 | 2026-11-01 23:06:38 +0500 | 12 (11 min 56 s) |
| First live Create (ZZ_TEST_AG_5317) | 2026-11-01 23:14:38 +0500 | 2026-11-01 23:25:33 +0500 | 11 (10 min 55 s) |
