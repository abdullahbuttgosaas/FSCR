# Receivables Payment Terms module: spec (prompt 1 of 3)

Written 2026-10-30. Read-only and offline: no Oracle calls were made, nothing was built and
nothing else was changed.

- Configuration project used: `E:\GoSaaS\Configuration Automation v2.1\Configuration Automation`
  (the user said on 2026-10-30 to use this folder; it is the path first named as the original).
- FSCR repo used: `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`.

Short names used below: **SKILL** = `fscr-main/pillars/erp/financials/customer-billing/manage-receivables-payment-terms/SKILL.md`;
**RES/** = that skill's `ora-resource/` folder; **PKG** = its `scripts/payment_terms_fsm_package.py`;
**ADP** = its `scripts/fsm_task_adapter.py`; **E2E** = its `e2e-adapter.json`; **PROJ/** =
`fscr-main/project/draft-impl-project-20261028/`. Our files are named from the configuration root.

"AR" below means Oracle Receivables. Our existing **Payment Terms** folder is the Payables one
(`AP_MANAGE_PAYMENT_TERMS`, `Payment Terms/CLAUDE.md:3-4`). The new module is separate and doesn't touch it.

---

## 1. The Oracle object

**Task:** Manage Receivables Payment Terms, code `AR_MANAGE_RECEIVABLES_PAYMENT_TERMS`. In the catalog
it is `"AvailableFlag": "Y"`, `"ExportImportSupportedFlag": "Y"`, `"CSVExportImportSupportedFlag": "Y"`
(`knowledge/setup-task-catalog/effective/setupTasksAll.json`). It sits under Financials > Customer
Billing (SKILL:7-10). Its catalog row is `AR_DEFINE_CUSTOMER_BILLING_CONFIGURATIONAR_MANAGE_RECEIVABLES_PAYMENT_TERMS`
(`knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json:9453`).

**Entities.** One payment term is one parent package: the header plus its children. Each entity is
one CSV in the task ZIP (SKILL:269-274; E2E `package.entities`):

| Role | Entity / CSV | Key | Parent link |
|---|---|---|---|
| Header | `AR_PAYMENT_TERM` | Name + SetCode | n/a |
| Installment | `AR_PAYMENT_TERM_LINE` | parent + SequenceNum | `AR_PAYMENT_TERM.Name`, `AR_PAYMENT_TERM.SetCode` |
| Translation | `AR_PAYMENT_TERM_TRANSLATION` | parent + Language | `AR_PAYMENT_TERM.Name`, `AR_PAYMENT_TERM.SetCode` |
| Discount | `AR_PAYMENT_TERM_DISCOUNT` | parent + line SequenceNum + DiscountPercent | the two above + `AR_PAYMENT_TERM_LINE.SequenceNum` |

**Fields FSCR creates.** This is the `fscr-create-fields` list (SKILL:98). The `Attribute1-15` and
`AttributeCategory` flexfield columns exist on header, line and discount, but FSCR blocks them until
the pod's context is proven (RES/ora_input_validation.md:25).

| Entity | Field | Type (pod metadata) | Required | Create default (FSCR) | Allowed values / rule |
|---|---|---|---|---|---|
| Header | Name | string | yes | none | max **15** characters |
| Header | SetCode | string | yes | **never defaulted** | one exact current reference data set |
| Header | Description | string | no | none | max 240; also written to the base translation row |
| Header | StartDateActive | date | yes | none | ISO date |
| Header | EndDateActive | date | no | none | strictly after the start date |
| Header | BaseAmount | decimal | yes | `100` | positive; the ratio denominator, not money |
| Header | PrintingLeadDays | decimal | 2+ lines: yes | **never defaulted** | 2+ lines: positive whole number; 1 line: 0 or more |
| Header | FirstInstallmentCode | string | yes (entity) | `INCLUDE`, only for 1 line | `ALLOCATE`, `INCLUDE` |
| Header | CalcDiscountOnLinesFlag | string | yes (entity) | `I`, only when no discounts | `F`, `I`, `L`, `T` |
| Header | DiscountBasisDateType | string | yes (entity) | `APPLICATION_DATE` | `APPLICATION_DATE`, `DEPOSIT_DATE`, `RECEIPT_DATE` |
| Header | CreditCheckFlag | string | yes (entity) | `N` | Y/N |
| Header | InUse | string | yes (entity) | `N` | Y/N |
| Header | PartialDiscountFlag | string | yes (entity) | `N` | Y/N; Y needs the system option proven |
| Header | PrepaymentFlag | string | yes (entity) | `N` | Y/N |
| Header | DueCutoffDay | decimal | no | none | 1-31 |
| Header | CycleName | string | no | **never defaulted** | an exact balance-forward billing cycle; not with 2+ lines |
| Line | SequenceNum | long | yes | none | whole, positive, unique in the term |
| Line | RelativeAmount | decimal | yes | none | positive; all lines add up to BaseAmount |
| Line | DueDays / DueDate / DueDayOfMonth (+ DueMonthsForward) | decimal / date / decimal | exactly one method | none | Day of Month needs Months Forward; Months Forward only with Day of Month |
| Translation | Language, SourceLang | string | yes | **never defaulted** | max 4; base row has Language = SourceLang |
| Translation | Name, Description | string | yes | copied from header | 15 / 240 |
| Discount | SequenceNum | long | yes | none | must equal the line's SequenceNum |
| Discount | DiscountPercent | decimal | yes | none | 0-100; unique on its line; at most 3 per line |
| Discount | DiscountDays / DiscountDate / DiscountDayOfMonth (+ DiscountMonthsForward) | decimal / date / decimal | exactly one method | none | same pairing rule as lines |
| all | LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin | n/a | n/a | always blank | service-owned |

Evidence, quoted:
- Name limit: PKG:108 `"Name": 15,` and RES/ora_input_validation.md:69 "Enforce Name 15, Description 240,
  Language/SourceLang 4, header lookup/flag lengths, flexfield context 30, and flexfield segment 150 characters".
- Allowed codes: PKG:71-75 `"CalcDiscountOnLinesFlag": {"F", "I", "L", "T"}`,
  `"DiscountBasisDateType": {"APPLICATION_DATE", "DEPOSIT_DATE", "RECEIPT_DATE"}`, `"FirstInstallmentCode": {"ALLOCATE", "INCLUDE"}`.
- Defaults: RES/ora_defaulting_rules.md:20-27, e.g. line 25 "Discount basis | Invoice Amount (`I`) | Create has no
  discount rows" and line 26 "Include tax and freight in the first installment (`INCLUDE`) | Create has exactly one payment line".
- Entity-required header fields: RES/ora_error_handling.md:65 "JBO-27014: Attribute CalcDiscountOnLinesFlag in
  PaymentTermEO is required" and :66 "JBO-27014: Attribute FirstInstallmentCode in PaymentTermEO is required".
- Numbers and dates: RES/ora_input_validation.md:62-66, e.g. :63 "Require the sum of line RelativeAmount values to equal
  header BaseAmount; do not assume a fixed denominator" and :66 "require EndDateActive, when supplied, to be later
  than—not equal to—StartDateActive".
- Discounts: RES/ora_input_validation.md:71 "require unique DiscountPercent per payment line, and allow no more than
  three discounts per line".
- Balance forward: RES/ora_input_validation.md:42 "Balance-forward billing cycles and split installments are incompatible".
- Audit columns: SKILL:310-312 "`LastUpdateDate`, `LastUpdatedBy`, `CreationDate`, `CreatedBy`, and `LastUpdateLogin`
  are service-owned. Keep them only as read-only baseline evidence and emit them blank".
- Dates must be ISO in the import: SKILL:436-440 "Fusion current exports can contain slash-separated dates such as
  `2026/10/01`; ... the Payment Terms CSV loader rejects them when copied unchanged". RES/ora_error_handling.md:31
  names "JBO-25009 or JBO-25027". **This differs from our Payables folder, which writes `YYYY/MM/DD`**
  (`Payment Terms/CLAUDE.md:193`).

**Ask the user; never default** (SKILL:127-131, 185-198; RES/ora_defaulting_rules.md:28-30, 9):
- Reference data set (no defaulting to COMMON, ENTERPRISE or the first one; SKILL:524).
- Print Lead Days and the tax/freight choice for a term with 2 or more installments (SKILL:185-189 "require a
  positive whole-number Print Lead Days value and ask whether tax and freight should be allocated across all
  installments or included in the first installment").
- Discount basis when any discount is given (SKILL:194-196).
- Base language for a new term (SKILL:179-183 "When target evidence contains zero or multiple possible languages and
  the customer did not specify one, ask"). With exactly one language in the pod, that language is used and shown.
- Billing cycle, partial-payment discount, flexfields: only when asked for, and only with pod evidence (RES/ora_input_validation.md:22-25).

**Other rules.** Hard delete is not supported (SKILL:255). Name and SetCode can't be changed by an
update (SKILL:133-138). The import isn't one transaction, so after a failure every term must be
re-read (SKILL:411-415).

## 2. Duplicate and reference checks (before Create, all in the preview)

| Check | Rule | Reads from |
|---|---|---|
| Name already exists | exact Name + exact SetCode exists -> **skipped**, nothing changed (RES/ora_reference_lookups.md:65 "Exact SetCode plus exact Name; no normalized or fuzzy identity") | fresh **data export** of the task, `AR_PAYMENT_TERM.csv` |
| Same name, other capitals or spaces | yellow note, sent as a new term (as Payables does); Oracle's own rule here is **not proven** (see 9) | same export |
| Same name twice in the sheet (same set) | red on the later row (SKILL:528) | the sheet |
| Name length | 1-15 characters, no outer spaces | rule |
| Reference data set | must be one of Oracle's sets (exact code). The pod's payment terms use only `COMMON` (all 11 rows of `PROJ/exports/.../...100004731498215.zip`); FSCR accepts "a valid empty set that has no Payment Terms rows" (SKILL:397-398) | live list `setIdSetsLOV` (REST, already proven: root `CLAUDE.md:970-971`) |
| Base language | exactly one language in the export's translation rows -> use it and say so; zero or several -> red: "Choose the language" | data export `AR_PAYMENT_TERM_TRANSLATION.csv` (pod: only `US`/`US`) |
| Dates | From Date required (empty = Oracle's today minus one day, sent as that date); To Date strictly after From Date | rule + `page/oracle_today.py` |
| Installment amounts add up | sum of Relative Amount = Base Amount (Base Amount empty = 100, so the lines read as percentages adding to 100) | rule (RES/ora_input_validation.md:63) |
| "Amount Due" | AR has no amount-due lines; Relative Amount is a share of Base Amount, never money (SKILL:206-208). Payables' "last amount line is 0" rule does not apply | n/a |
| Split term | 2+ installments: Print Lead Days (whole, above 0) and Tax and Freight both required | rule |
| Due method | exactly one of Days / Fixed Date / Day of Month per installment; Day of Month needs Months Ahead | rule |
| Discounts | at most 3 per installment, each 0-100, no percent twice on one installment, one date method; Discount Basis required | rule |
| Billing cycle / partial discount | not offered in v1 (see 5); a Yes would need extra exports | n/a |
| Pod layout | the template has the four Payment Terms entities, task `AR_MANAGE_RECEIVABLES_PAYMENT_TERMS`, status COMPLETED (section 3) | template export metadata |

All checks run in the folder's `--plan` (the page's `oracle_check`), so the rules live in one place
(root `CLAUDE.md:444-446`). The checks report every value problem first, then the business choices
(RES/ora_input_validation.md:59).

## 3. File layout

**What the pod's files look like** (saved ETIA-TEST evidence in `PROJ/exports/financials/customer-billing/manage-receivables-payment-terms/`):

| ZIP | Process | Rows (TERM / LINE / TRANSLATION / DISCOUNT) |
|---|---|---|
| `ETIA-TEST_setup_task_csv_template_export_..._100004619543924.zip` | template export | 0 / 0 / 0 / 0 |
| `ETIA-TEST_setup_task_csv_export_..._100004619522844.zip` | data export before | 10 / 10 / 10 / 1 |
| `zzfscr-n45-4203-candidate.zip` | FSCR's import file | 1 / 2 / 1 / 0 |
| `ETIA-TEST_setup_task_csv_export_..._100004731498215.zip` | data export after | 11 / 12 / 11 / 1 |

All four have the same 5 members (`AR_PAYMENT_TERM.csv`, `AR_PAYMENT_TERM_LINE.csv`,
`AR_PAYMENT_TERM_TRANSLATION.csv`, `AR_PAYMENT_TERM_DISCOUNT.csv`, `ASM_SETUP_CSV_METADATA.xml`). The
metadata is 7,279 bytes, `ObjectShortName` AR_MANAGE_RECEIVABLES_PAYMENT_TERMS, `ObjectType` TASK,
`ProcessType` EXPORT, `ProcessStatus` COMPLETED, `ProcessEnv` etia-test, `ProcessRelease` 11.13.26.10.0.

**Entity order in the pod's metadata** (all four files the same):

| Position | BusinessObjectShortName | NodeSequence | XmlNodePath |
|---|---|---|---|
| 1 | AR_PAYMENT_TERM_LINE | 3 | /PaymentTermVO/PaymentTermVORow/PaymentTermLine/PaymentTermLineVORow |
| 2 | AR_PAYMENT_TERM | 1 | /PaymentTermVO/PaymentTermVORow |
| 3 | AR_PAYMENT_TERM_TRANSLATION | 1 | /PaymentTermVO/PaymentTermVORow/PaymentTermTranslation/PaymentTermTranslationVORow |
| 4 | AR_PAYMENT_TERM_DISCOUNT | 4 | /PaymentTermVO/PaymentTermVORow/PaymentTermLine/PaymentTermLineVORow/PaymentTermLineDiscount/PaymentTermLineDiscountVORow |

**CSV headers** (pod files; `Attribute1-15` left out here):
- TERM: Name, SetCode, LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin, CreditCheckFlag,
  DueCutoffDay, PrintingLeadDays, StartDateActive, EndDateActive, AttributeCategory, BaseAmount,
  CalcDiscountOnLinesFlag, DiscountBasisDateType, FirstInstallmentCode, InUse, PartialDiscountFlag, Description,
  PrepaymentFlag, CycleName
- LINE: AR_PAYMENT_TERM.Name, AR_PAYMENT_TERM.SetCode, SequenceNum, (5 audit), RelativeAmount, DueDays, DueDate,
  DueDayOfMonth, DueMonthsForward, AttributeCategory, SetCode
- TRANSLATION: AR_PAYMENT_TERM.Name, AR_PAYMENT_TERM.SetCode, Description, Name, Language, SourceLang, (5 audit)
- DISCOUNT: AR_PAYMENT_TERM.Name, AR_PAYMENT_TERM.SetCode, AR_PAYMENT_TERM_LINE.SequenceNum, SequenceNum,
  DiscountPercent, (5 audit), DiscountDays, DiscountDate, DiscountDayOfMonth, DiscountMonthsForward, AttributeCategory, SetCode

Two layout facts from the evidence:
- **The CSV column order is not the metadata order.** TERM's `XmlAttributeList` starts with `LastUpdateDate` and has
  `Name` near the end, but the CSV starts `Name,SetCode`. So headers must come from each CSV's first line, and field
  types from the metadata, matched by name.
- The child parent-link columns (`AR_PAYMENT_TERM.Name` etc.) are in the CSV but not in `XmlAttributeList`
  (PKG:49-64 adds them as `RELATIONSHIP_FIELDS`).

**What FSCR hardcodes:**
- PKG:26-30: the four CSV member names. PKG:31-36: the entity names. PKG:43-48: the four `XmlNodePath` values.
  PKG:49-64: the relationship columns. PKG:71-127: codes, defaults and string limits.
- The original PKG had a fixed entity order, and it **rejected ETIA-TEST's real files**:
  PROJ/state/runs/20261028-payment-term-create-blocked.json:11 "the helper's hardcoded PAYMENT_TERM_OBJECT_ORDER
  [AR_PAYMENT_TERM, AR_PAYMENT_TERM_TRANSLATION, AR_PAYMENT_TERM_DISCOUNT, AR_PAYMENT_TERM_LINE] differs from
  ETIA-TEST's ASM_SETUP_CSV_METADATA.xml declaration order [AR_PAYMENT_TERM_LINE, AR_PAYMENT_TERM, ...]". It was
  patched locally by our earlier session (verified.json:10 "fixed PAYMENT_TERM_OBJECT_ORDER replaced by
  template/baseline order equality"; PKG:456-458 now says "Declaration order varies by pod").
- ADP:244-247 still pins headers: "`{entity['member']} header order differs from e2e-adapter.json.`" E2E holds every
  header list and `"evidenceRelease": "11.13.26.10.0"` (E2E:2052).

**Our module reads the layout from the pod at run time** (the improvement):
1. **Where the template comes from:** in `--plan` and `--run-batch`, before anything is built, the folder asks
   Oracle for the task's own template with the setup task template export (`setupTaskCSVTemplateExports`, the
   resource FSCR's engine uses, `shared/setup-export/fsm-csv-export/scripts/fsm_csv_export_engine.py:22`; process
   and result names at :71 and :83). This is **not proven in our project yet**. If Oracle refuses it, the fallback
   is the task's data export, which `--plan` reads anyway for the duplicate check. The evidence shows the
   template and data export have identical members, headers and metadata, so its header lines and metadata are
   used with the rows dropped. Each run fetches fresh files. There is no saved copy like Business Units'
   `bu_import_template.json`, so a pod update is picked up automatically.
2. Read `ASM_SETUP_CSV_METADATA.xml`. For each `MigrationProcessBusinessObjectCSVMetadataVORow`, read its name,
   `XmlAttributeList`, `XmlAttributeTypeList`, `XmlNodePath` and `NodeSequence`, **in the order the pod lists them**.
3. For each entity, the CSV is the member `<BusinessObjectShortName>.csv` and the headers are its first line, as is.
   Every metadata attribute must be a header. Extra headers are allowed only if they are parent-link columns
   (`<ENTITY>.<Field>`).
4. Roles are assigned by entity name, the one thing we keep fixed: the header, line, translation and discount
   entities named in section 1. If the pod lacks one of them, or the task code or status is wrong, the preview
   stops with: "Oracle's file layout for Receivables payment terms isn't what this module knows. Nothing was
   created." No guessing.
5. The import ZIP is the template's members **in the template's own member order**, with the metadata copied
   byte for byte. Each CSV is the template's header line plus our rows. A column we don't fill stays empty, audit
   columns are always empty, dates are ISO `YYYY-MM-DD` (metadata type `date`), and the CSV format follows the
   template's own quoting and line endings.
6. The template's `ProcessEnv` must equal the pod in `.env`'s ORACLE_HOST label, and its release must equal the
   data export's release. If not, the preview stops and nothing is built.

## 4. Create route

**Recommendation: the setup task process without a browser, as Business Units does.** That means
`setupTaskCSVImports/AR_MANAGE_RECEIVABLES_PAYMENT_TERMS` with Basic auth, the same call as `Business Units/bu_batch.py:449-472`.

Why:
- The task supports CSV export/import (section 1).
- It is the route proven in our project for another task: `Business Units/CLAUDE.md:21-23` says "sent as a Setup task
  process (`setupTaskCSVImports`, the same file, no browser) ... (PROVEN: ZZ_TEST_BU_3138_*)".
- No Playwright, so no lost clicks (root `CLAUDE.md:617-649`) and no sign-in window during a run.
- FSCR's own proof went through a different path: Core Data Loader, a UCM upload and a Run Book (verified.json
  external ids `ucm_content_id`, `data_load_request_id`, `fsm_import_request_id`). That path needs FSCR's OAuth client
  and Run Book setup (claims report, PROJ/artifacts/shared/reporting/fscr-claims-verification-20261029.md, row 20).
  We don't take it.
- No REST resource for AR payment terms was proven anywhere in the evidence. FSCR forbids a direct REST write
  (SKILL:545).
- **Fallback if Oracle refuses `setupTaskCSVImports` for this task:** the task's own Import from CSV File screen
  through Playwright, as Payables Payment Terms does. Use the task-level import only (SKILL:377 "an offering-level or
  functional-area-level import page will reject this task-scoped archive").

How it runs (`--run-batch '<list>'`, all terms of the upload in one call):
1. The same checks as `--plan`. Just before sending, the names are read again from a fresh data export, so a term
   made meanwhile is never sent.
2. Build one ZIP for all new terms (section 3).
3. `POST setupTaskCSVImports/<task>/child/SetupTaskCSVImportProcess` with `{"TaskCode", "FileContent": base64,
   "SourceTargetDiffOkFlag": true}` (root `CLAUDE.md:961-963`), which returns the ProcessId.
4. Poll `SetupTaskCSVImportProcessResult/{id}` every 10 s, waiting until it reaches COMPLETED, COMPLETED_WARNINGS or
   COMPLETED_ERRORS, with a time limit and a plain timeout message. **Never resubmit** after a timeout or an unknown
   result (SKILL:548): the read-back decides.
5. Errors: download the ProcessLog, ProcessResultsReport and ProcessResultsSummaryReport enclosures into the
   folder's `_work/`. Then parse the "Row Identifier ... Status: Error ... Message Text" blocks, like
   `bu_batch.log_failures()`. Map Oracle's ids to plain words with FSCR's message table (RES/ora_error_handling.md:53-67,
   e.g. `AR_SU_TOT_RELAMOUNT_EQ_BASE_AM`, `AR_SU_INVALID_PRINT_LEAD_DAYS`, `AR_SU_UNIQUE_PAY_TERMS`,
   `AR_SU_DISCOUNT_PERCENT_RANGE`, JBO-27014, JBO-27040). An unlisted id is quoted as Oracle's reason. How AR's log
   names a failed row is **not proven**: Payables' log names the term, Business Units' log uses internal keys
   (bu_batch.py:493-497). So which term failed is decided by the read-back, never guessed.
6. **Read-back:** a fresh data export, compared field by field. This is planned; nothing here has been proven yet:
   - Every sent term: exactly one header with that Name + SetCode. Every sent line, translation and discount is
     matched by its key. Every non-audit column is compared by value: dates as dates (the export writes `2026/10/28`,
     we sent `2026-10-28`) and numbers as numbers.
   - An extra translation language that Oracle added itself is a note, not a failure (SKILL:382). An extra line or
     discount is a mismatch.
   - Every term not sent: all its rows are identical before and after (Payables' rule, `Payment Terms/CLAUDE.md:89-97`).
   - Result per term: "Created and checked: every value as sent" / skipped (already there) / "Oracle refused X:
     <reason>. Nothing was saved in Oracle." (INVALID_REQUEST, saved "no", with a structured problem for
     pause-and-ask) / "Saved but not as sent: <differences>" (VERIFY_FAILED, saved "yes").

**Reuse** (copied into the new folder where it comes from another folder, per the isolation rules in root `CLAUDE.md:92-107`):
- `common/oracle.py`: `check_environment`, `init_work_dir` / `cleanup_work_dir`, `process_urls`, `poll_result`,
  `call` / `try_call`, `rest_items` (set list), `export_task`. All of these are used unchanged.
- `common/page.py`: the whole page contract (`--spec` / `--options` / `--run`, plain-word check, step lines).
- From Business Units (copied): the `send()` / `unpack()` / `log_failures()` pattern, the double name read before
  sending, and `--plan` / `--run-batch` command shapes.
- From Payables Payment Terms (copied): the result shapes (`results` per term, `skipped`, `found`, `summary`,
  `fix`, `oracle`), `refusal_problems()` for pause-and-ask, the exact-name and yellow capitals note, and the
  "Oracle's today minus one day" date handling.
- From the page (as is): `batch_run`, `oracle_check`, `ask_on_refusal`, `plan_skips_red_fields`, child tabs joined
  by name (`"link": {"column", "exact": true}`), the failed-only sheet, the run summary and the repair.

**New:**
- The template-driven package writer (section 3) and the template export call.
- AR rules: 15-character name, Base Amount, Print Lead Days, tax and freight, discount basis, 3 discounts per line,
  and ISO dates.
- Set and language evidence.
- The AR log parser and the field-by-field reconcile.
- The folder itself: `Receivables Payment Terms/` with `run.py`, `CLAUDE.md`, `sheet_fields.md`, `request.json` and
  `manual-notes/`. The page finds `run.py` (`page/server.py:128-132`). It also needs its Configuration index row,
  which the page reads (`page/server.py:113-125`).

## 5. Sheet design

Two new tabs. Their names differ from Payables' "Payment Terms" / "Payment Term Lines" and stay under 31
characters. Same layout as every tab: section row, label row (yellow `*` required), hint row, data from row 4.
Long drop-downs go on the hidden **Lists** tab through `values_live` (`page/workbook.py:27`, :155-159).
Registry group **"Receivables Payment Terms"**, record word "receivables payment term", folder "Receivables
Payment Terms", `batch_run: "--run-batch"`, `oracle_check: "--plan"`, `plan_skips_red_fields: true`,
`ask_on_refusal`, `max_records` 100.

**Tab "Receivables Payment Terms"** (one row per term). Section "Receivables Payment Terms (Manage Receivables Payment Terms)":

| Column | Key | Type | Req. | Default | Hint |
|---|---|---|---|---|---|
| Name | name | text, keep_spaces | * | n/a | Text, max 15. Capitals and spaces count. An existing name in the same set is skipped |
| Set Code | set_code | pick, values_live `set_code`, check folder | * | n/a | Dropdown of Oracle's reference data sets (code) |
| Item Description | description | text | | n/a | Text, max 240 |
| From Date | from_date | date, role start | | today-1, send_default | YYYY-MM-DD; empty = today |
| To Date | to_date | date, role end, pair From Date | | n/a | YYYY-MM-DD, after the From Date; empty = none |
| Base Amount | base_amount | number | | 100 | What the installment amounts add up to; empty = 100 (then they are percentages) |
| Print Lead Days | print_lead_days | number | | n/a | Whole number above 0; required with 2 or more installments |
| Tax and Freight | tax_freight | pick: "Include in the first installment", "Allocate across all installments", check folder | | first installment (1 installment only) | Required with 2 or more installments |
| Discount Basis | discount_basis | pick: 4 labels (see 9), check folder | | Invoice amount (no discounts only) | Required when any installment has a discount |
| Discount Date Basis | discount_date_basis | pick: "Application date", "Receipt date", "Deposit date" | | Application date | Dropdown |
| Cutoff Day | cutoff_day | number | | n/a | Whole number 1-31 |
| Credit Check | credit_check | yes-no | | No | Yes / No |
| Prepayment | prepayment | yes-no | | No | Yes / No |

The following are left out of v1 and are always set to the create default with a note in the preview: Allow
Discount on Partial Payments (needs the Receivables system option proven), Billing Cycle (needs the cycle list),
In Use (N), flexfields and extra languages. A request for them is not possible from the sheet.

**Tab "Receivables Term Lines"** (one row per installment, in order; joined by Payment Term Name **exactly**,
`"link": {"column": "Payment Term Name", "exact": true}`). It is styled like Payables' lines tab, with discounts as
column sections:

| Section | Columns |
|---|---|
| Installment | Payment Term Name *, Sequence (digits; empty = row order 1, 2, 3), Relative Amount *, Days, Fixed Date, Day of Month, Months Ahead |
| First Discount | First Discount (%), First Discount Days, First Discount Fixed Date, First Discount Day of Month, First Discount Months Ahead |
| Second Discount | the same five |
| Third Discount | the same five |

The folder turns each filled discount section into one discount row with SequenceNum = the installment's
Sequence. The base translation row is built by the folder (header Name and Description, the pod's one
language), so there is no translations tab.

**Check messages** (plain words; red on the sheet row; `fix` shown as the suggestion):
- "Name is longer than 15 characters (Oracle's limit for Receivables payment terms). Shorten it."
- "A Receivables payment term 'X' already exists in set COMMON. It will be skipped; nothing is changed." (yellow)
- "Oracle has 'x' in set COMMON, which differs only in capitals or spaces. This one will be a new term." (yellow)
- "'X' is listed twice for set COMMON."
- "Set Code 'Y' isn't one of Oracle's reference data sets." plus suggestions from the list
- "The installments add up to 90, but Base Amount is 100. They must add up to exactly 100."
- "Installment 2: give one due date: Days, Fixed Date or Day of Month."
- "Installment 2: Day of Month needs Months Ahead (0 = same month)."
- "This term has 2 installments, so Print Lead Days is needed (a whole number above 0)."
- "This term has 2 installments: choose Tax and Freight (first installment, or across all installments)."
- "A discount is given, so choose the Discount Basis."
- "Installment 1: 2% is given twice. Each discount on an installment needs its own percent."
- "Installment 1: a discount must be between 0 and 100 percent."
- "To Date must be after the From Date."
- "This installment names payment term 'Z', which isn't on the Receivables Payment Terms tab."
- "Oracle's language for payment term names couldn't be decided (it has none or several). Nothing will be created."
- Pause-and-ask fields: name, description, set_code, from_date, to_date, base_amount, print_lead_days, tax_freight,
  discount_basis, and the line keys (relative_amount, days, fixed_date, day_of_month, months_ahead, discount*_*).

## 6. Portal changes

**Look and behaviour.** A two-option switch, **Order Management | Receivables**, in the header next to the
environment chip. It is drawn with the existing tokens (`.chip` / `.btn` look, `--accent` for the chosen one,
`aria-pressed`, keyboard focus) in both themes and at 390 px. It decides only:
- which module cards the Upload stage lists (Receivables: one card "Receivables Payment Terms", monogram RT,
  "Terms, installments, discounts");
- which blank template "Get the blank template" downloads (the chosen area's tabs plus Read me and Lists).

It does **not** filter an uploaded sheet. Check, Create and Done keep handling every module found in the file,
exactly as today, so a mixed sheet still works and no existing flow changes. The progress rail, routes (`#/`,
`#/sheet/<id>`, `#/job/<id>`, `#/summary/<id>`), runs, questions and summaries are untouched. Switching while a run
is open changes nothing in that run.

**State.** The choice is remembered with the existing `store` helper (localStorage `sa-area` inside try/catch,
`page/static/app.js:24-27`); default **Order Management**. With storage blocked, the page still works on the default.

**Where modules sit.** An optional registry key `"area": "Receivables"` goes on the new group only. A group without
it counts as Order Management, so no existing group is edited. Payables "Payment Terms" stays where it is today
(see 9).

**Files touched (additive only):**
- `page/static/index.html`: the switch markup.
- `page/static/app.js`: the switch, the `MODS` / `WHAT_MOD` entries for the new module, and filtering the Upload stage's
  cards; existing entries unchanged.
- `page/static/style.css`: at most one rule, reusing tokens.
- `page/server.py`: `/api/sheet/template` takes an optional `?area=`. Without it the result is byte-for-byte today's
  template.
- `page/workbook.py`: `make_template(lists, area=None)` and the `area` key; None = today's behaviour.
- `page/sheet_definition.json`: two tabs and one Read me line. `page/sheet_registry.json`: one group, last.
- `page/matrix/test_matrix.py`: one `MODULES` entry.
- Root `CLAUDE.md`: index row, Layout, a "Receivables Payment Terms module" section.
- The new folder `Receivables Payment Terms/`.

**Must NOT change:**
- `Customers/` and `_frozen/` (frozen; root `CLAUDE.md:575-591`).
- `Payment Terms/`, `Business Units/`, `Order Types/`, `Lookup types/` and `Price Lists/`.
- Any existing helper in `common/` (additive only).
- Existing tabs, columns and registry groups.
- The module order of existing groups.
- The page look (the approved mockup, root `CLAUDE.md:658-693`).

**Regression check, every time `page/` changes:**
- `python page/regression_customers.py` must PASS. Its part (c) already allows added empty tabs.
- `python page/matrix/test_matrix.py` must still give 48/48 and 12/12 for the six existing modules.
- A byte compare of `/api/sheet/template` without `area` before and after.
- The redesign screenshot check (`page/_work/redesign/shoot.py`) for both themes.

## 7. Test plan

**Offline matrix** (`page/matrix/test_matrix.py`; no Oracle, no Claude):
- Add the module to `MODULES`, with `child` "Receivables Term Lines", `rows` "installments", field `print_lead_days`
  and `base` = one 2-line term. The 8 behaviours give 56/56, and "check can't run" plus "check fails once" give 14/14.
- Folder unit checks that read the **saved ETIA-TEST files** as fixtures, copied into the folder's `manual-notes/`
  only as small header/metadata text, not zips:
  1. Pod order (LINE, TERM, TRANSLATION, DISCOUNT) builds a ZIP whose metadata equals the template byte for byte
     and whose members are in the template's order.
  2. The same with the metadata rows shuffled, and reversed: the ZIP still follows the given template.
  3. A template missing the DISCOUNT entity gives a plain stop; nothing is built.
  4. An extra unknown column in a pod CSV is kept and left empty.
  5. CSV column order different from `XmlAttributeList` gives values in the right columns.
  6. A slash date from the export is compared equal to the ISO date sent; the import file has only ISO dates.
  7. Rebuild FSCR's `ZZFSCR N45 4203` request from the template. Our rows must equal the non-audit values of
     `zzfscr-n45-4203-candidate.zip`, the one file Oracle accepted (verified.json `"loaded": 3, "failed": 0`).
  8. A reconcile of that candidate against the after-export (`...100004731498215.zip`) must be "every value as
     sent", with the other 10 terms unchanged.
  9. Rule cases, each red with its message: name of 16 characters, sum 99, 2 lines without Print Lead Days, 2 lines
     without Tax and Freight, a discount without a basis, 4 discounts on one line, the same percent twice, Day of
     Month without Months Ahead, To Date = From Date, an unknown set, an existing exact name (skipped), and a
     capitals-only name (yellow).
- Run `regression_customers.py` and the full matrix after every `page/` change.

**One live test on ETIA-TEST** (test pod, `ORACLE_ENV` test; after the user says go in prompt 2/3):
- Name **`ZZ_TEST_AR_4821`** (exactly 15 characters), set COMMON, language US (the pod's only one), From Date =
  Oracle's today minus one day.
- 2 installments 60 / 40 at 30 / 60 days, Print Lead Days 1, Tax and Freight "Include in the first installment".
  One discount on installment 1: 2% at 10 days, so Discount Basis is required; choose Invoice amount.
- This covers header, two lines, the translation and a discount. FSCR's live term had no discount.
- First a read-only `--plan`, which also proves the template export call. Then Create through the page.
- **Read-back proof:** `--run-batch` reports "every value as sent" from a fresh data export. Then, by hand from
  that export:
  - exactly 1 header, 2 lines, 1 translation and 1 discount row for `ZZ_TEST_AR_4821` / COMMON, each field equal;
  - every other term's rows identical to the before-export (11 terms, the 12 lines and the 1 discount on 2026-10-28);
  - optionally, Manage Receivables Payment Terms shows the term on screen.
- Then the same sheet again: the term is skipped and nothing is changed.

**What could go wrong:**
- Oracle refuses `setupTaskCSVImports` or the template export for this task; then use the fallback in section 4 and
  record it.
- The import's log names rows differently from what the parser expects; the read-back still decides.
- The `F` / `T` discount basis labels differ on screen (see 9).
- Oracle's name uniqueness is case-insensitive or not per set (see 9). The test name is new, so it can't clash.
- Oracle's date flips during the run (handled: the From Date is sent as shown).
- The import ends COMPLETED_ERRORS with a partial save. Never resubmit; the read-back decides.
- The test term can't be deleted afterwards (SKILL:255 hard delete unsupported). It stays as test material, like
  ZZFSCR N45 4203.

## 8. Savings and gaps (for the presentation)

| What the FSCR repo gave us for step 1 (learning how Oracle does it) | Evidence |
|---|---|
| The task code and that it supports CSV export/import | `setupTasksAll.json`: AvailableFlag, ExportImportSupportedFlag, CSVExportImportSupportedFlag all `Y` |
| The four entities, their CSV names, keys, parent links and field types | E2E `package.entities`; PKG:26-64 |
| Which header fields Oracle requires even for a simple term, with the error Oracle gives | RES/ora_error_handling.md:65-67 (JBO-27014 on CalcDiscountOnLinesFlag, FirstInstallmentCode, InUse, PartialDiscountFlag) |
| The safe create defaults and what must never be defaulted | RES/ora_defaulting_rules.md:20-30 |
| The allowed codes for discount basis, date basis and tax/freight | PKG:71-75 |
| Field limits: Name 15, Description 240, Language 4 | PKG:106-127; RES/ora_input_validation.md:69 |
| The schedule and discount rules (sum = Base Amount, one due method, 3 discounts per line, unique percent) | RES/ora_input_validation.md:62-66, :71 |
| Oracle's AR message ids with what each means | RES/ora_error_handling.md:53-64 |
| That imports need ISO dates although exports give slash dates | SKILL:436-440; RES/ora_error_handling.md:31 |
| That audit columns must be blank in an import | SKILL:310-313 |
| A field-by-field reconcile method (per parent, per child key, audit ignored, extra languages a note) | PKG:2389-2511 |
| The template export resource name | fsm_csv_export_engine.py:22 |
| One real create on our pod, read back with 0 mismatches | PROJ/state/runs/20261028-payment-term-create-verified.json ("loaded": 3, "failed": 0, "reconcile" verified) |
| Saved pod files that show the real layout | PROJ/exports/.../ (4 ZIPs, section 3) |

| What we still had to do or verify ourselves | Evidence |
|---|---|
| FSCR's original fixed entity order rejected the pod's real files; a local patch was needed before the live test | blocked.json:11; verified.json:10 |
| FSCR's import went through Core Data Loader, UCM and a Run Book, not our route. Our route for this task is unproven | verified.json `external_ids`; section 4 |
| The template export call has not been used in our project | section 3 step 1 |
| Discount basis labels disagree inside FSCR: PKG says `F` = "Lines and tax, excluding freight", E2E says `F` = "Freight" (and `T` = "Tax") | PKG:80-85; E2E:808, :823 |
| The adapter fails on any header-order difference | ADP:244-247 |
| FSCR's data-load status script crashed on the Windows console; not documented | verified.json `diagnostic_note`; claims report row 19b |
| The adapter generator named in E2E is not in the repo | claims report row 18 |
| The skill has no tests (1 of 16 FSM create skills has any) | claims report row C(iii) |
| The adapter evidence is pinned to release 11.13.26.10.0 | E2E:2052 |
| Which reference sets are valid for AR terms (pod uses only COMMON) and whether names are unique per set and case | not stated in FSCR; section 9 |
| The sheet, preview, pause-and-ask, result cards, read-back report and the page switch | all ours (sections 5-6) |

| Where our module improves on FSCR (planned, to be proven in prompts 2-3) | Basis |
|---|---|
| Entity order, members and headers are read from the pod's own template on every run, not fixed in code or JSON | section 3 vs PKG:26-48, ADP:244-247, blocked.json:11 |
| No OAuth client, Run Book or Core Data Loader: the same Basic-auth setup task process as Business Units | Business Units/CLAUDE.md:21-23; claims report row 20 |
| Business users fill an Excel sheet with drop-downs and see every problem before Create, instead of answering chat questions | root CLAUDE.md > The upload sheet |
| A refused value asks the user (suggestions, typed value, skip) and only that term is retried | root CLAUDE.md:498-509, :539-566 |
| One result card per term, a failed-only sheet and a run summary with time and cost | root CLAUDE.md:361-398 |
| A rerun never makes a term twice (exact name + set read again just before sending) | section 4 step 1 |

## 9. Open questions and risks

Blocking the build (answer before or during prompt 2):
1. **Route proof.** Does `setupTaskCSVImports` accept `AR_MANAGE_RECEIVABLES_PAYMENT_TERMS` with our Basic auth? It is
   proven for Business Units only. If it is refused, the fallback is Playwright on the task's own import screen.
   The first live step must answer this.
2. **Discount basis labels.** FSCR contradicts itself on `F` and `T` (section 8). The sheet's drop-down labels must
   come from Oracle's own screen, read once (a read-only look). Until then, the build can offer only "Invoice
   amount" (`I`) and "Lines only" (`L`), whose labels agree.

Not blocking, but needing a decision or a check:
3. **Name uniqueness.** FSCR matches Name + SetCode exactly. Whether Oracle's `AR_SU_UNIQUE_PAY_TERMS` ignores
   capitals or the set is not in the files. The preview warns in yellow; the live test can't prove it.
4. **Reference sets.** The pod's terms use only COMMON. Whether any of the 37 sets can hold an AR payment term is not
   proven; an unsuitable set would be refused at import (the read-back catches it).
5. **Language.** The pod has only US. A pod with several languages makes the preview ask; the sheet has no language
   column in v1.
6. **Payables vs Receivables naming.** The existing module card "Payment Terms" is Payables. Should it be renamed
   "Payables Payment Terms" or moved under a Financials area? This spec changes nothing there (frozen-style rule).
7. **Switch scope.** This spec makes the switch choose the Upload cards and the blank template only, not filter
   uploads. Confirm that this is what you want.
8. **Out of v1:** update, end-date, balance-forward cycles, partial-payment discounts, flexfields and extra
   translations. Each needs extra pod evidence (FSCR's own conditions, RES/ora_input_validation.md:22-25).
9. **Governance difference.** FSCR requires its Core Data Loader for every import (SKILL:258, :487-488). Our module
   deliberately uses our own proven route instead. Say so in the presentation.
10. **Root layout.** The root `CLAUDE.md:275-279` allows only listed items at the root. This `_fscr_spec/` folder was
    asked for by the user; move or remove it before sharing the project.
11. **Test leftovers.** Terms can't be hard-deleted (SKILL:255). `ZZ_TEST_AR_4821` will stay in ETIA-TEST.
