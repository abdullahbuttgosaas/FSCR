# AutoInvoice Grouping Rules module: spec

Written 2026-11-01, together with the offline build (Part B of the same request). No Oracle calls were made for this
spec or the build. Layout follows `RECEIVABLES_PAYMENT_TERMS_SPEC.md`.

- Configuration project: `E:\GoSaaS\Configuration Automation v2.1\Configuration Automation`
- FSCR repo (read-only): `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`
- Plan: `fscr-main\RECEIVABLES_MODULES_PLAN.md` (this module is build order 1 of the Receivables extension).

Short names: **SKILL** = `fscr-main/pillars/erp/financials/customer-billing/manage-autoinvoice-grouping-rules/SKILL.md`;
**RES/** = that skill's `ora-resource/` folder; **ADP** = its `scripts/fsm_task_adapter.py`; **E2E** = its
`e2e-adapter.json`. Our files are named from the configuration root.

Labels: **[F]** stated in FSCR files, **[P]** stated in our project, **[J]** my judgment, **[?]** to confirm in the
live test.

---

## 1. The Oracle object

**Task:** Manage AutoInvoice Grouping Rules, code `AR_MANAGE_AUTOINVOICE_GROUPING_RULES`, Financials > Customer
Billing [F, SKILL:100-113]. Catalog: AvailableFlag Y, ExportImportSupportedFlag Y, CSVExportImportSupportedFlag Y
[F, `knowledge/setup-task-catalog/effective/setupTasksAll.json`]. Adapter evidence release **11.13.26.10.0** [F,
E2E:1205], the same release as ETIA-TEST's Receivables payment terms template on 2026-10-30 [P].

What it is (in business words) [J]: AutoInvoice turns imported billing lines (for example from Order Management)
into Receivables transactions. A grouping rule says which lines may go on the same invoice, debit memo or credit
memo. Oracle always groups by its mandatory attributes; a rule adds optional characteristics per transaction class
(for example: one invoice per order reference).

**Entities** (one rule = one root plus children) [F, SKILL:172, :182; E2E `package.entities`]:

| Role | Entity / CSV | Key | Parent link | Node path (E2E) |
|---|---|---|---|---|
| Rule (root) | `AR_AI_GROUPING_RULE` | Name | n/a | /TransactionRequestGroupingRuleVO/TransactionRequestGroupingRuleVORow |
| Transaction class | `ORA_AR_AI_GRP_TXN_TYPE` | parent + Class11 | `AR_AI_GROUPING_RULE.Name` | .../TransactionRequestGroupingTransactionTypeVORow |
| Optional characteristic | `ORA_AR_AI_GRP_TXN_REQUEST` | parent + class + FromColumnName | `AR_AI_GROUPING_RULE.Name`, `ORA_AR_AI_GRP_TXN_TYPE.Class11` | .../TransactionRequestGroupByVORow |

Three levels: rule > class > characteristic. The import root is `AR_AI_GROUPING_RULE` [F, SKILL:172].

**Fields FSCR creates** (`fscr-create-fields`, SKILL:95) and how v1 treats each:

| Entity | Field | Type [F] | Required | Max [F] | Allowed values / rule [F] | v1 |
|---|---|---|---|---|---|---|
| Rule | Name | string | yes | **40** | unique; must not start `ORA_` (reserved) | sheet, required |
| Rule | StartDate | date | yes | n/a | explicit; "the UI's date prefill does not establish an FSM import default" (SKILL:183) | sheet, **required, never defaulted** |
| Rule | Description | string | no | **80** | n/a | sheet, optional |
| Rule | EndDate | date | no | n/a | **on or after** StartDate (equal allowed, unlike payment terms) | sheet, optional |
| Rule | LineOrderingRuleName | string | no | n/a | exact name of an existing line ordering rule; resolved inside the import, no public lookup (RES/ora_reference_lookups.md:15) | **not in v1** (section 6) |
| Class | Class11 | string | yes per row | **1** | `C` Credit Memo, `D` Debit Memo, `I` Invoice; label or code, trimmed, case-insensitive; no class twice in one rule (RES/ora_input_validation.md:26) | sheet, required per row |
| Characteristic | FromColumnName | string | yes per row | n/a | exact name of an available grouping column; no characteristic twice in one class; resolved inside the import, no public lookup (RES/ora_reference_lookups.md:16) | sheet, optional per row |
| all | AttributeCategory, Attribute1-15 (DFF) | string | no | 30 / 150 | deployed context unverified: blocked until proven (RES/ora_design_enforcement.md:21) | always empty |
| Rule | ConsBillingUseFlag | string | no | 1 | accepted codes unverified (RES/ora_design_enforcement.md:22) | always empty |
| all | CreatedBy, LastUpdatedBy | string | n/a | n/a | audit (E2E `auditFields`) | always empty |

**Defaults** [F, RES/ora_defaulting_rules.md:8]: "No FSM import default is established for this task." So:

**Ask the user; never default** [F + J]:
- Name.
- From Date (StartDate). The project's usual "empty = Oracle's today minus one day" is NOT applied here because FSCR
  says the start date must be explicit (RES/ora_input_validation.md:14 "Ask for an explicit start date").
- Transaction Class on each class row (RES/ora_defaulting_rules.md:15 "No default; choose one of C, D or I").
- Characteristic on a characteristic row (RES/ora_defaulting_rules.md:16 "No default").

**Other rules** [F]:
- Rename is not supported; the key is Name (SKILL:189 "The import hook matches roots through AltKey_Name").
- No physical delete; end-date retirement is not verified (SKILL:176; E2E `deletionPolicy.disposition` "unresolved").
  EndDate is an update field (RES/ora_input_validation.md:4), but v1 only creates.
- Consolidated billing: with the opt-in on, `ConsBillingUseFlag` Y refuses non-Invoice classes
  (`AR_CONS_BILL_TRAN_CLS_NOT_ALOW`) and some grouping columns are refused when the flag is off
  (`AR_CONS_BILL_GROUP_NOT_ALLOW_U`) (RES/ora_input_validation.md:45). v1 never sends the flag.
- Whether a rule must have at least one class is **not stated** [?]. v1 allows a rule with no class rows and says so
  in yellow on the preview.

## 2. Checks before Create (all in the preview)

All run in the folder's `--plan` (the page's `oracle_check`), so the rules live in one place.

| Check | Rule | Reads from |
|---|---|---|
| Name present, text, no outer spaces | red | rule |
| Name length | at most 40 characters | rule [F] |
| Name prefix | must not start `ORA_` (any capitals: Oracle reserves it; [J] case-insensitive to be safe) | rule [F] |
| Name already in Oracle | exact Name exists -> **skipped**, nothing changed | fresh data file, `AR_AI_GROUPING_RULE.csv` |
| Same name, other capitals or spaces | yellow note, sent as a new rule (Oracle's own case rule not proven) [?] | same |
| Same name twice in the sheet | red on the later row | sheet |
| Description | at most 80 characters | rule [F] |
| From Date | required, YYYY-MM-DD | rule |
| To Date | YYYY-MM-DD, on or after From Date (folder, [F]); the page's shared date rule for every module is stricter: after the From Date and after Oracle's today [P]. Left as is (shared code) | rule [F] |
| Class row | Transaction Class required: Invoice / Debit Memo / Credit Memo (or I / D / C) | rule [F] |
| Class twice | the same class twice in one rule without a characteristic, or the same class + characteristic twice -> red (`AR_SU_DEFGR_DUPCLASS` / `AR_SU_DEFGR_DUPCOL`) | rule [F] |
| Characteristic | text; exact name; a name no rule in Oracle uses yet -> **red** with Oracle's names as the fix (dependency rule; an unknown name would make Oracle save the rule without it) | data file (characteristics on existing rules) |
| Class row names an unknown rule | red on that row (the page's join, as payment terms) | sheet |
| No class rows | yellow note | rule [J] |
| Pod layout | template has the three entities, task code right, status COMPLETED, release = data file's, pod = .env host | template + data file metadata |

Problems are reported all at once; the check never writes to Oracle.

## 3. File layout

**There is no exported file for this task yet** (no FSCR project export, no pod evidence) [F: none under
`fscr-main/project/`]. So:

- The module reads the layout **from the pod's own template on every run**, exactly as Receivables Payment Terms:
  `setupTaskCSVTemplateExports/AR_MANAGE_AUTOINVOICE_GROUPING_RULES` (fallback: the data file's layout). Entity order =
  the order of `MigrationProcessBusinessObjectCSVMetadataVORow` in `ASM_SETUP_CSV_METADATA.xml`; members in the
  template's own zip order; metadata copied byte for byte; each CSV header = its own first line; field types from the
  metadata by name; extra columns only as parent links `<ENTITY>.<Field>`; quoting and line end as the template's.
- Only the three entity names are fixed in code (`agr_package.ENTITIES`).
- FSCR's adapter pins the header order and the node sequences (ADP: "header order differs from e2e-adapter.json").
  **We do not copy that order.**
- A **STAND-IN** layout for offline tests only: `AutoInvoice Grouping Rules/manual-notes/standin_layout_NOT_FROM_ORACLE/`
  (three CSV header lines and a metadata file), built from E2E `package.entities` (headers, types, node paths, node
  sequences). It is marked "STAND-IN, not from Oracle" in a README and in an XML comment. The module never reads it;
  only the offline stub does. **The real layout is confirmed only in the live test.**
- Dates are written `YYYY-MM-DD` (ADP validates dates with `date.fromisoformat`; our RPT finding: Oracle's AR loader
  refused slash dates). Read-back compares dates as dates (`2026/11/01` = `2026-11-01`).
- Audit columns (CreatedBy, LastUpdatedBy here; the five usual names are blanked too) always empty.

## 4. Create route and read-back

**Route: the setup task process without a browser**, as Business Units and Receivables Payment Terms:
`POST setupTaskCSVImports/AR_MANAGE_AUTOINVOICE_GROUPING_RULES/child/SetupTaskCSVImportProcess` with `{"TaskCode",
"FileContent": base64, "SourceTargetDiffOkFlag": true}`, Basic auth. **UNTESTED for this task.** Proven for
`FUN_MANAGE_BUSINESS_UNIT` and, on 2026-10-30, for `AR_MANAGE_RECEIVABLES_PAYMENT_TERMS` (term `ZZRPT 9721`) [P].
If Oracle refuses the call: plain card "Oracle refused the setup task process for AutoInvoice grouping rules ... no
other way was tried" (SETUP_NEEDED, or NO_PERMISSION on 401/403). No browser fallback in v1.

Run (`--run-batch`, all rules of the upload in one call):
1. Same checks as `--plan`; just before sending, the names are read again from a fresh data file (a rule made
   meanwhile is skipped, never sent twice).
2. One zip for all new rules, built from the template (section 3).
3. Send once; poll every 10 s (30-minute limit); save ProcessLog / ProcessResultsReport / ProcessResultsSummaryReport
   in `_work/`. **Never resubmitted** after a timeout or an unknown result.
4. Log reading: "Row Identifier ... Status: Error ... Message Text" blocks; Oracle's ids into plain words
   (`AR_SU_DEFGR_DUPCLASS`, `AR_SU_DEFGR_DUPCOL`, `AR_CONS_BILL_*`, JBO-27014 required, JBO-27040 too long,
   JBO-25009/25027 date, LOV no matching row). A block is tied to a rule only when it quotes the rule's exact name
   (how this task's log names rows is not proven) [?].

**Read-back** (a fresh data file, compared field by field):
- Each sent rule: exactly one root row with that Name; every sent class matched by Class11; every sent
  characteristic matched by (Class11, FromColumnName); every non-audit column compared (dates as dates, numbers as
  numbers). An extra class or characteristic Oracle shows that we didn't send = a mismatch [J]; FSCR's reconciliation
  policy says "requestedRows: exact" [F, E2E `reconciliationPolicy`].
- Every rule not sent: identical before and after (FSCR: "baselineRows: fail-on-change-or-removal"; we report a
  change as a note, as RPT does, because other users share the pod).
- Results per rule: "Created ... and checked: every value as sent" / skipped / "Oracle refused ...: <reason>. Nothing
  was saved in Oracle." (INVALID_REQUEST, saved "no", a structured problem for pause-and-ask) / "saved, but not as
  sent" (VERIFY_FAILED, saved "yes") / "may have been saved" (saved "maybe").
- Where to see it: Setup and Maintenance > Financials > Customer Billing > Manage AutoInvoice Grouping Rules, search
  for the name. (The page path is our wording; FSCR doesn't state the page [F: not stated].)

## 5. Dependencies and links

The dependency rule (root `CLAUDE.md` > Design principles): a need that is a row in the sheet is created first and the
dependent item isn't sent if it failed or was skipped; otherwise it must already exist in Oracle and the check reads
Oracle before Create; otherwise a red problem with the fix.

**What this module needs:**

| Need | Mandatory | From the sheet? | Read from Oracle before Create? | When missing |
|---|---|---|---|---|
| Transaction class codes C / D / I | yes per class row | no (seeded) [F] | not needed: fixed seed, "environmentVerificationRequired": false [F, E2E] | red on the row with the three choices |
| Grouping characteristic (FromColumnName) | per characteristic row | no (seeded, 87 base rows + 7 with the consolidated-billing opt-in) [F, RES/ora_reference_lookups.md:23] | **only partly**: no public lookup exists [F]; the check reads the names existing rules use from the data file. A name not seen there is **red** (dependency rule step 3): FSCR says a missing name "removes affected child row", so Oracle would save the rule without it and a rerun skips the rule [F, RES/ora_reference_lookups.md:16]. A refusal at Create (e.g. consolidated billing only) asks the user (suggestions = names seen on the pod) | red before Create; question after a refusal |
| Line ordering rule | only if named | could be, if a Line Ordering Rules module existed (none planned yet) | **not possible yet**: no public lookup [F]; the line ordering rules task's own export has no FSCR contract, so we can't read it safely [J] | **left out of v1**; the column is not on the sheet |
| DFF context, consolidated-billing opt-in | only if used | no | not proven how | left out of v1 (always empty) |

So the module has **no hard dependency**: it works on an empty pod and on a pod with data (existing names skipped).

**Which later modules use it:**

| Later module | How it uses a grouping rule | Link rule for the build |
|---|---|---|
| Transaction Sources (plan order 2) | an Imported source (`BatchSourceType` FOREIGN) may name `GroupName` [F, transaction sources dependency file "autoinvoice_grouping_rule ... GroupName is supplied and BatchSourceType is FOREIGN"] | registry `depends_on` from Transaction Sources' Grouping Rule column to this tab's Name: a rule on the sheet runs first; a source whose rule failed or was skipped by the user is not sent; a rule not on the sheet must be in this module's data file (read before Create); else red |
| Receivables System Options (skipped for now) | `GroupingRuleName` is a required field there [F, its adapter `requiredFields`] | the same `depends_on` pattern when that module is built |
| Customer (account) profiles | the AutoInvoice grouping rule can also be set on a customer profile [J, Oracle functional knowledge; not in FSCR files] | to confirm; not planned |

The page's run order is the registry order, and this group is placed before any future Transaction Sources group.

## 6. Sheet design

Two new tabs, on the **Receivables** side of the page switch only (registry `"area": "Receivables"`).

**Tab "AutoInvoice Grouping Rules"** (one row per rule). Section "AutoInvoice Grouping Rules (Manage AutoInvoice
Grouping Rules)":

| Column | Key | Type | Req. | Hint |
|---|---|---|---|---|
| Name | name | text, keep_spaces | * | Text, max 40, not starting ORA_. An existing name is skipped |
| Item Description | description | text | | Text, max 80 |
| From Date | from_date | date, role start | * | YYYY-MM-DD; never filled in for you |
| To Date | to_date | date, role end, pair From Date | | YYYY-MM-DD, on or after the From Date; empty = none |

**Tab "Grouping Rule Classes"** (one row per class, or per class + characteristic). Joined by Grouping Rule Name
**exactly** (`"link": {"column": "Grouping Rule Name", "exact": true}`). Three levels in one flat tab [J]: rows with
the same class under one rule make one class; each filled Characteristic adds one characteristic under it.

| Column | Key | Type | Req. | Hint |
|---|---|---|---|---|
| Grouping Rule Name | (join only) | text | * | The rule's Name, written exactly |
| Transaction Class | transaction_class | pick: Invoice, Debit Memo, Credit Memo, check folder | * | Dropdown |
| Characteristic | characteristic | text | | Oracle's grouping characteristic name, as Oracle writes it; empty = the class only |

Registry group "AutoInvoice Grouping Rules", record word "autoinvoice grouping rule", folder "AutoInvoice Grouping
Rules", `batch_run: "--run-batch"`, `oracle_check: "--plan"`, `plan_skips_red_fields: true`, `ask_on_refusal`
(name, description, from_date, to_date, transaction_class, characteristic), `max_records` 100, area Receivables.

Messages (plain; red unless marked):
- "Name is longer than 40 characters (Oracle's limit for grouping rules). Shorten it."
- "Name can't start with ORA_: Oracle keeps those names for its own rules."
- "An AutoInvoice grouping rule 'X' already exists in Oracle. It will be skipped; nothing is changed." (yellow)
- "Oracle has 'x', which differs only in capitals or spaces. This one will be a new rule." (yellow)
- "'X' is listed twice."
- "Item Description can be at most 80 characters; it has N."
- "From Date is missing. Grouping rules need an explicit start date; it is never filled in for you."
- "To Date can't be before the From Date."
- "Class row 2: Transaction Class is missing." / "... 'Sales' isn't one of: Invoice, Debit Memo, Credit Memo."
- "Class row 3: Invoice is listed twice for this rule." / "... characteristic X is listed twice under Invoice."
- "Class row 1: no grouping rule in Oracle uses characteristic 'X', so it can't be confirmed before Create (Oracle has
  no list of them to read)." Fix: "Use one Oracle already uses: ... If Oracle doesn't know a name, it saves the rule
  without it."
- "This rule has no transaction class rows; Oracle's mandatory grouping attributes still apply." (yellow, [?])

## 7. Portal changes

Additive only; same pattern as Receivables Payment Terms:
- `page/sheet_definition.json`: the two tabs, Read me lines for the Receivables area.
- `page/sheet_registry.json`: one group, last, with `"area": "Receivables"`.
- `page/static/app.js`: the module card (`MODS` "AutoInvoice Grouping Rules": mono "AG", "Rules, classes,
  characteristics"), `WHAT_MOD`, `MOD_ORDER`.
- `page/matrix/test_matrix.py` + `page/matrix/stub_grouping.py`.
- Root `CLAUDE.md`: index row, Layout, a module section.
- **Must not change:** the Order Management blank sheet (byte-identical, all sheet XML compared), every finished
  module's folder, `common/`, `_frozen/`, existing tabs/columns/groups.

## 8. Test plan

Offline (`page/matrix/test_matrix.py`):
- The module in the generic 8 behaviours (stub folder) and the 2 "check can't run / fails once" cases.
- The real folder with Oracle replaced by the STAND-IN layout (`stub_grouping.py`): happy path (Corsair rule, 3
  classes, 1 characteristic) created and read back as sent, rerun skipped; name over 40; ORA_ prefix; From Date
  missing; To Date before From Date; class missing / unknown / twice; characteristic twice; unknown characteristic
  red; refused characteristic at Create -> pause and ask; template entity order reversed and shuffled -> file
  follows it; template missing an entity -> plain stop; route refused -> plain card; check can't run; preview of a
  Corsair sheet through the page.

Live (separate prompt, after the user says go; not done here):
1. `--check` (read-only): proves the template call and the data file for this task; record the real layout, entity
   order, headers, release, and the characteristic names existing rules use.
2. `--plan` with the neutral live-test rule `ZZ_TEST_AG_5317`; then Create; read-back "every value as sent"; the same sheet
   again: skipped.
3. Replace the STAND-IN with the real headers/metadata as a test fixture (as RPT's `pod_layout_etia_test/`).

What could go wrong [J]: the import refuses this task; the characteristic name format differs from what the sheet
expects (label vs column name); Oracle requires at least one class; the log names rows by internal ids; the rule
can't be deleted afterwards (stays on the shared pod; it can be end-dated later).

## 9. Corsair example record

Story [J]: Corsair sells memory, cooling and power components to OEM customers Intel, AMD and NVIDIA. Their orders
come from Order Management into Receivables through AutoInvoice. Corsair's finance team wants one invoice per order
reference, so each OEM can match an invoice to its own order, and keeps credit and debit memos on the standard
attributes.

| Tab | Row |
|---|---|
| AutoInvoice Grouping Rules | Name `CORSAIR OEM BY ORDER REFERENCE`; Item Description `One invoice per OEM order reference for Intel, AMD and NVIDIA`; From Date `2026-11-01` |
| Grouping Rule Classes | `CORSAIR OEM BY ORDER REFERENCE` / Invoice / `L.INTERFACE_LINE_ATTRIBUTE1` |
| Grouping Rule Classes | `CORSAIR OEM BY ORDER REFERENCE` / Debit Memo / (empty) |
| Grouping Rule Classes | `CORSAIR OEM BY ORDER REFERENCE` / Credit Memo / (empty) |

Changed 2026-11-01 after the read-only live check: the first version grouped by `PURCHASE_ORDER` (my guess); ETIA-TEST
writes characteristics as `L.<column>` and its rules use only `L.INTERFACE_LINE_ATTRIBUTE1-7`, and the user decided to
keep the strict check, so the sample uses `L.INTERFACE_LINE_ATTRIBUTE1` [P]. What that attribute holds for Corsair's
lines depends on the source's line transaction flexfield (not in FSCR's files) [?].

A second sample rule for returns: `CORSAIR RMA CREDITS BY ORDER REFERENCE`, Credit Memo / `L.INTERFACE_LINE_ATTRIBUTE1`.

For the live test the record is named per the project's test-record rule (root `CLAUDE.md` > Adding a new
configuration folder: ZZ_TEST_<4 digits>): `ZZ_TEST_AG_5317`, with no demo name in it. **Nothing named Corsair, Intel,
AMD or NVIDIA is ever sent to Oracle, not even in a read-only check** (user's rule, 2026-11-01); the Corsair rows above
are for the local sample workbooks only. The test record can't be deleted afterwards.

## 10. What FSCR gave and what we still had to do

| FSCR gave | Evidence |
|---|---|
| Task code, CSV support, release 26.10 | setupTasksAll.json; E2E:1205 |
| Three entities, keys, parent links, node paths, headers and types | E2E `package.entities` |
| Name 40, Description 80, ORA_ reserved, StartDate explicit, EndDate >= StartDate | SKILL:174, :183-184; RES/ora_input_validation.md:23-25 |
| Class codes and labels, no duplicates | E2E `valueContracts.Class11`; RES/ora_input_validation.md:26-27 |
| That there are no create defaults | RES/ora_defaulting_rules.md:8 |
| That line ordering and characteristic names resolve only inside the import | RES/ora_reference_lookups.md:3, :15-16 |
| Duplicate message ids | RES/ora_error_handling.md:11-12 |

| Gaps we found | Evidence |
|---|---|
| No pod export for this task: layout unknown until the live test | no files under `fscr-main/project/` |
| SKILL links a test catalog `e2e-test-catalog.json` and E2E names a validator `tests/test_fsm_task_adapter.py`; neither file exists | SKILL:178; E2E `semanticModel.extension.validatorCommand`; folder listing |
| The 87 characteristic names are not listed | RES/ora_reference_lookups.md:23 |
| Whether a rule needs at least one class | not stated |
| How this task's log names a failed row | not stated |
| FSCR pins header and node order | ADP |

## 11. Open questions and risks

1. Route: does `setupTaskCSVImports` accept this task? (The template call and data file were accepted read-only on
   2026-11-01; the import is still untested.)
2. Characteristic names: answered 2026-11-01, `L.<column>`; ETIA-TEST's rules use only `L.INTERFACE_LINE_ATTRIBUTE1-7`.
   **Decided by the user 2026-11-01: keep the strict check** (only names an Oracle rule already uses pass).
3. Must a rule have a class? Answered: no, Oracle's DEFAULT rule has none.
4. Name uniqueness and case rule [?].
5. Line Ordering Rule: add it once a Line Ordering Rules module (or a proven read of that task's export) exists.
6. The live test record stays on the shared pod (no delete).

## 12. Live test on ETIA-TEST, 2026-11-01 (what the pod did versus FSCR)

One rule created: `ZZ_TEST_AG_5317` (neutral name; From Date 2026-11-01; Invoice by `L.INTERFACE_LINE_ATTRIBUTE1`),
through the folder's `--run-batch` (no browser). Read back "every value as sent"; the other 8 rules unchanged; a rerun
skipped it. Details and step times: `AutoInvoice Grouping Rules/CLAUDE.md` > Observed in the live Create.

| Topic | FSCR says | The pod did |
|---|---|---|
| Import route | Core Data Loader + Run Book (SKILL Core Data Loader handoff) | `setupTaskCSVImports` with Basic auth accepted the task; COMPLETED in about 21 s |
| Entity order | adapter pins node order RULE (1), TYPE (2), REQUEST (3) and header order (ADP) | metadata order TYPE, REQUEST, RULE; zip order RULE, TYPE, REQUEST; the metadata lists the entities again later in another order. Headers equal FSCR's lists |
| Characteristic names | exact FromColumnName, names not listed; 87 seeded | stored as `L.<interface column>`; ETIA-TEST's rules use only `L.INTERFACE_LINE_ATTRIBUTE1-7`; ATTRIBUTE1 accepted |
| A rule needs a class? | not stated | no: Oracle's DEFAULT rule has none |
| Dates | ISO in the adapter | ISO accepted on import; the data file writes `2026/11/01` |
| Audit columns | CreatedBy, LastUpdatedBy | the same; filled by Oracle (Configuration.TEST) |
| Process log | "Report the affected root row" on failure | a success names no rule or row, only counts per business object ("AutoInvoice Grouping Rule", "... Optional Attributes", "... Transaction Class"); a failure was not observed |
| Delete | none | none tried; the test rule stays |

Still unproven: the upload sheet's Create through the page; a refusal and how its log names the row; the rule on
Oracle's screen (the saved browser sign-in had expired).

## Time log

| Phase | Start | Finish | Minutes |
|---|---|---|---|
| Spec + offline build (this request) | 2026-11-01 22:27:25 +0500 | 2026-11-01 22:45:59 +0500 | 19 (18 min 34 s) |
| Read-only live check + tests on the real layout | 2026-11-01 22:54:42 +0500 | 2026-11-01 23:06:38 +0500 | 12 (11 min 56 s) |
| Keep strict: samples switched to a pod characteristic | 2026-11-01 23:08:12 +0500 | 2026-11-01 23:11:38 +0500 | 3 (3 min 26 s) |
| First live Create (ZZ_TEST_AG_5317) | 2026-11-01 23:14:38 +0500 | 2026-11-01 23:25:33 +0500 | 11 (10 min 55 s) |
