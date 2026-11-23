# Transaction Sources module: spec

Written 2026-11-01, together with the offline build and a read-only check on ETIA-TEST (one request). No Create was
run. Layout follows `AUTOINVOICE_GROUPING_RULES_SPEC.md`.

- Configuration project: `E:\GoSaaS\Configuration Automation v2.1\Configuration Automation`
- FSCR repo (read-only): `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`
- Plan: `fscr-main\RECEIVABLES_MODULES_PLAN.md` (build order 2 of the Receivables extension).

Short names: **SKILL** = `fscr-main/pillars/erp/financials/customer-billing/manage-transaction-sources/SKILL.md`;
**RES/** = its `ora-resource/` folder; **ADP** = its `scripts/fsm_task_adapter.py`; **E2E** = its `e2e-adapter.json`.
Labels: **[F]** stated in FSCR files, **[P]** our project, **[J]** my judgment, **[?]** to confirm live.

**Hard rule** (user, 2026-11-01): nothing named Corsair, Intel, AMD or NVIDIA is ever sent to Oracle, not even in a
read-only check. Anything that touches Oracle uses neutral `ZZ_TEST_` names. The Corsair rows below are for the local
sample workbook only.

---

## 1. The Oracle object

**Task:** Manage Transaction Sources, code `AR_MANAGE_TRANSACTION_SOURCES`, Financials > Customer Billing [F, SKILL
frontmatter]. CSV export/import supported, import mode FSM [F]. Adapter evidence release **11.13.26.10.0** [F, E2E
`package.evidenceRelease`].

What it is [J]: a transaction source names where Receivables transactions come from and how they are numbered. A
**Manual** source is used when people enter invoices on screen; an **Imported** source is used by AutoInvoice for lines
coming from another application (for example Order Management), and that is where a grouping rule applies.

**Entities** [F, E2E `package.entities`; SKILL "relationship-partition ownership matrix"]:

| Role | Entity / CSV | Key | Use in this module |
|---|---|---|---|
| Source (create target) | `ORA_AR_TXN_BATCH_SOURCE` | Name + SetCode | the rows we send |
| Source (persisted view) | `AR_BATCH_SOURCE` | Name + SetCode | never sent; read back: "an ORA_AR_TXN_BATCH_SOURCE create persists through AR_BATCH_SOURCE under the same Name and SetCode key" [F, E2E `semanticModel.extension.evidence`] |

One flat table (no child rows). `ORA_AR_TXN_BATCH_SOURCE` has 111 columns, `AR_BATCH_SOURCE` 109 [F].

**Fields** (FSCR `fscr-create-fields`: AutoTrxNumberingFlag, BatchSourceType, Description, InvalidLinesRule,
LastBatchNum, Name, SetCode, StartDate, Status [F, RES/ora_input_validation.md:4]) and v1:

| Field | Type [F] | Required | Max | Allowed values [F] | Create default [F] | v1 |
|---|---|---|---|---|---|---|
| Name | string | yes | not stated in FSCR | must not start `ORA_` (RES/ora_design_enforcement.md) | none | sheet, required |
| SetCode | string | yes | n/a | an exact reference data set code | **never defaulted** | sheet, required |
| Description | string | yes (create) | not stated | n/a | none | sheet, **required** |
| BatchSourceType | string | yes | n/a | `INV` = Manual, `FOREIGN` = Imported | `INV` | sheet, default Manual (shown as filled in) |
| StartDate | date | yes | n/a | ISO date | none ("Supply ... the active-from date") | sheet, **required, never defaulted** |
| Status | string | no | n/a | `A` Active, `I` Inactive | `A` | sheet, default Active |
| AutoTrxNumberingFlag | string | no | n/a | `Y`, `N` | `Y` | sheet, default Yes |
| LastBatchNum | long | when numbering Y | n/a | whole number >= 1; "the new sequence uses it directly as its start" | **never invented** (RES/ora_defaulting_rules.md "Do not invent a number; block the record") | sheet, required with numbering Yes |
| InvalidLinesRule | string | no | n/a | `Create` = Create Invoice, `Reject` = Reject Invoice | `Reject` | sheet, default Reject Invoice |
| GroupName | string | no | n/a | an existing grouping rule name; "GroupName is supplied for an Imported source: Verify during FSM validation" (RES/ora_input_validation.md) | none | sheet, Imported only, **outside FSCR's evidenced create fields: unproven** [J] |
| TrxTypeName + InvTrxTypeSetCode, BatchSourceName + CmBatchSrcSetCode, LegalEntityIdentifier, DocumentTypeCode | string | no | n/a | portable references | none | **not in v1** (section 5) |
| EndDate, the 30 AutoInvoice "...Rule" options, flags, DFF/GDF | various | no | n/a | not in FSCR's create contract | none | always empty |
| LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin, DefaultInvTrxType, LegalEntityName | n/a | n/a | n/a | audit / derived | n/a | always empty [F, "Exclude ... from normal create input"] |

**Ask; never default** [F + J]: Name, Set Code, Description, From Date, and Last Number when automatic numbering is on.
**Defaults applied and shown on the preview** [F, RES/ora_defaulting_rules.md]: Type Manual, Status Active, Automatic
Numbering Yes, Invalid Lines Reject Invoice.

**Other rules** [F]: Manual sources must not carry Imported-only fields (except InvalidLinesRule); update is evidenced
for Description only; no physical delete ("block deletion until an exact source-backed mechanism"); a credit
transaction source needs a second import pass (not in v1).

## 2. Checks before Create (all in `--plan`)

| Check | Rule | Reads from |
|---|---|---|
| Name present, text, no outer spaces, not `ORA_` | red | rule |
| Set Code | one of Oracle's reference data sets (exact code) | `setIdSetsLOV` (REST GET, proven in Receivables Payment Terms) |
| Already in Oracle | exact Name + Set Code in the data file (either entity) -> **skipped** | data file |
| Capitals-only match in the same set | yellow, sent as new | data file |
| Same Name + Set twice in the sheet | red on the later row | sheet |
| Description | required | rule |
| Type | Manual / Imported (or INV / FOREIGN) | rule [F] |
| From Date | required, YYYY-MM-DD | rule |
| Status | Active / Inactive | rule [F] |
| Automatic Numbering / Last Number | with Yes: Last Number whole and >= 1, required; with No: Last Number must be empty | rule [F] |
| Invalid Lines | Create Invoice / Reject Invoice | rule [F] |
| Grouping Rule on a Manual source | red: "only for Imported sources" | rule [F, Imported-only fields on Manual] |
| Grouping Rule exists | on this sheet's AutoInvoice Grouping Rules tab -> waits for it (section 5); else must be in Oracle's grouping rules data file; else red with the names Oracle has | grouping rules data file (`AR_MANAGE_AUTOINVOICE_GROUPING_RULES`, read-only, only when a source names a rule) |
| Pod layout | both entities present, task right, COMPLETED, release = data file's, pod = .env host | template + data file |

## 3. File layout

Read from the pod's own template on every run (`setupTaskCSVTemplateExports`; fallback the data file), exactly as the
grouping rules module: entity order from the metadata, members in the template's zip order, metadata byte for byte,
headers from each CSV's first line, types by name, quoting and line ends as the template's. Only the two entity names
are fixed in code. FSCR's adapter accepts "only the two complete NodeSequence profiles observed" and pins the header
order [F]; we don't. The import file carries rows only in `ORA_AR_TXN_BATCH_SOURCE`; `AR_BATCH_SOURCE.csv` is sent as
its header line only. Dates ISO; audit and derived columns empty. The real ETIA-TEST layout (read-only check) is saved
as the test fixture; see section 9.

## 4. Create route and read-back

Route: the setup task process without a browser (`setupTaskCSVImports/AR_MANAGE_TRANSACTION_SOURCES`, Basic auth),
proven for Business Units, Receivables Payment Terms and AutoInvoice Grouping Rules [P]. **PROVEN for this task on ETIA-TEST 2026-11-02** (section 12).
Run (`--run-batch`): the same checks; names read again just before sending (a source made meanwhile is skipped); a
source whose grouping rule was on the sheet is checked once more against Oracle's grouping rules (it must exist by
now); ONE file for all new sources; sent once; polled every 10 s; never resubmitted; Oracle's log saved in `_work/`.

Read-back (fresh data file): each sent source must appear once under Name + SetCode in `ORA_AR_TXN_BATCH_SOURCE` or
`AR_BATCH_SOURCE` (FSCR: create persists through `AR_BATCH_SOURCE`); every sent non-audit value is compared (dates as
dates, numbers as numbers); every other source's rows identical before and after (a change is a note, the pod is
shared). Results: created and checked / skipped / refused with Oracle's reason (pause-and-ask) / saved but not as
sent / may have been saved.

## 5. Dependencies and links

| Need | Mandatory | On the sheet? | Read from Oracle before Create | When missing |
|---|---|---|---|---|
| Reference data set | **yes** | no module creates sets | `setIdSetsLOV` | red with Oracle's set codes |
| AutoInvoice grouping rule (`GroupName`) | only for an Imported source that names one | **yes**: the AutoInvoice Grouping Rules tab | the grouping rules data file | on the sheet: the source waits (registry `depends_on`); the rule group runs first (registry order); if that rule failed or the user skipped it, the source is **not sent** and says why. Not on the sheet and not in Oracle: red with the rule names Oracle has |
| Transaction type (`TrxTypeName` + set) | no | future Transaction Types module | `transactionTypesLOV` (REST, FSCR documented) | **not in v1**; to add with the Transaction Types module (plan order 3) using the same `depends_on` pattern |
| Credit transaction source (`BatchSourceName` + set) | no | this module itself (self-reference, second import pass [F]) | `transactionSourcesLOV` / data file | not in v1 |
| Legal entity, document type | no | no | `legalEntitiesLOV` / import only | not in v1 |
| Accounting fields | none on this task [F: no account segments in the create contract] | n/a | n/a | n/a |

Used by: Receivables System Options (late-charge and BR sources) [F]; AutoInvoice imports and the Order Management
to Receivables flow use an Imported source [J]; Transaction Types does **not** depend on sources (the other way round:
a source names a type).

Works on an empty pod (only a reference data set is needed; COMMON exists everywhere [J]) and on a populated pod
(existing Name + Set skipped).

## 6. Sheet design (Receivables side only)

One tab **Transaction Sources**, section "Transaction Sources (Manage Transaction Sources)":

| Column | Key | Type | Req. | Default | Hint |
|---|---|---|---|---|---|
| Name | name | text, keep_spaces | * | | Not starting with ORA_. An existing name in the same set is skipped |
| Set Code | set_code | pick (live sets), check folder | * | | Never filled in for you |
| Item Description | description | text | * | | Required by Oracle |
| Type | source_type | pick Manual / Imported | | Manual | Imported = AutoInvoice |
| From Date | from_date | date, start | * | | Never filled in for you |
| Status | status | pick Active / Inactive | | Active | |
| Automatic Numbering | auto_numbering | yes-no | | Yes | |
| Last Number | last_number | number | | | Required with automatic numbering: whole number, 1 or more; the numbering starts there |
| Invalid Lines | invalid_lines | pick Create Invoice / Reject Invoice | | Reject Invoice | |
| Grouping Rule | grouping_rule | text, check folder | | | Imported only. A rule on the AutoInvoice Grouping Rules tab, or one already in Oracle |

Registry: group "Transaction Sources", area Receivables, after AutoInvoice Grouping Rules, `batch_run`, `oracle_check`,
`plan_skips_red_fields`, `ask_on_refusal`, and `depends_on` {group "AutoInvoice Grouping Rules", column "Grouping
Rule", match_column "Name", key "grouping_rule_pending", request_key "grouping_rule"}.

## 7. Test plan

Offline: the 8 generic behaviours, the 2 check cases, and the real folder through `stub_transaction_sources.py`:
happy path (Manual), Imported with a rule already in Oracle, Imported with a rule that is on the sheet (pending, then
checked at Create), rule missing everywhere (red), rule on a Manual source (red), required fields, numbering rules,
existing / capitals / twice, refused value at Create -> pause and ask, template order changes, layout stops, route
refused, check can't run, a sheet preview through the page with the dependency note, layout units. Then the page's
dependency run: a grouping rule and a source in one upload; the rule failing -> the source not sent.

Live (later, separate request, after the user says go): one Manual source `ZZ_TEST_TS_<4 digits>` in COMMON, numbering
Yes, Last Number 1; read back; rerun skipped. An Imported source with a grouping rule only after that.

## 8. Sample record (local sample workbook only, never sent to Oracle)

| Name | Set | Description | Type | From | Numbering | Last Number | Invalid Lines | Grouping Rule |
|---|---|---|---|---|---|---|---|---|
| CORSAIR OEM ORDERS | COMMON | Imported OEM order lines from Order Management for Intel, AMD and NVIDIA | Imported | 2026-11-01 | Yes | 100000 | Reject Invoice | CORSAIR OEM BY ORDER REFERENCE (a row on the grouping rules tab) |
| CORSAIR MANUAL INVOICES | COMMON | Manual invoices for OEM price adjustments and samples | Manual | 2026-11-01 | Yes | 500000 | Reject Invoice | (none) |

## 9. Read-only check on ETIA-TEST (2026-11-01; neutral ZZ_TEST_ requests only; nothing created)

| Topic | FSCR says | The pod did |
|---|---|---|
| Layout | node order ORA_ (1), AR_ (2); header order pinned | entity order ORA_AR_TXN_BATCH_SOURCE, AR_BATCH_SOURCE; **NodeSequence ORA_ = 2, AR_ = 1**; headers exactly FSCR's lists (111 / 109) |
| Template call | not used (Core Data Loader) | `setupTaskCSVTemplateExports` accepted, COMPLETED |
| Existing sources | fresh same-task export | **the data file lists 1 source** (Distributed Order Orchestration, Imported, rule DEFAULT); **Oracle's `transactionSourcesLOV` lists 22** (all Common Set). The module uses both [P] |
| Grouping rule reference | "Verify during FSM validation" | the grouping rules data file names DEFAULT; `--plan` found it; a missing name is red before Create |
| Preview | n/a | ZZ_TEST_TS_7731 (Manual) new; ZZ_TEST_TS_7732 (Imported, DEFAULT) new; ZZ_TEST_TS_7733 (rule ZZ_TEST_NO_SUCH_RULE) red |

**Design change after the check [J]:** the data file is not a complete list, so the existence check reads Oracle's
source list too, and the read-back falls back to it (name, set and description only, said in the result) when a new
source doesn't show in the data file. Details: the folder's CLAUDE.md > Observed in the read-only check.

## 10. What FSCR gave and what we still had to do

| FSCR gave | Evidence |
|---|---|
| Task code, two entities, keys, 111/109 headers, types, node paths | E2E `package.entities` |
| The 9 create fields, 4 defaults, value codes and labels | RES/ora_input_validation.md, RES/ora_defaulting_rules.md, E2E `valueContracts` |
| LastBatchNum >= 1, never invented; the sequence starts at it | RES/ora_input_validation.md (SRC-CS-EO-NUMBERING-2610) |
| Create persists through AR_BATCH_SOURCE | E2E extension evidence |
| Reference lookups: legal entity, transaction type, credit source (REST LOVs) | RES/ora_reference_lookups.md |

| Gaps | Evidence |
|---|---|
| No length limits (Name, Description) | E2E `fieldConstraints` empty |
| GroupName on create is not in the evidenced create fields; Imported-only AutoInvoice options are unevidenced | RES/ora_input_validation.md |
| No tests in the skill | folder listing |
| Header order and NodeSequence pinned | ADP, E2E |

## 11. Open questions and risks

1. ~~Route~~: answered 2026-11-02 (section 12): accepted.
2. ~~Imported source with GroupName~~: answered 2026-11-02: accepted and kept. Still unknown: whether Oracle fills the
   AutoInvoice "...Rule" options later or whether AutoInvoice needs them (the data file shows them empty for our source,
   filled for Distributed Order Orchestration).
3. Name and Description length limits [?]: not seen (no refusal yet).
4. ~~Where a create shows~~: answered 2026-11-02: in the data file under `AR_BATCH_SOURCE`, and in Oracle's source list.
5. The test sources can't be deleted; their numbering sequences stay too (ZZ_TEST_TS_7731 and ZZ_TEST_TS_7732 on
   ETIA-TEST).
6. How Oracle's log names a failed row for this task: not seen (nothing refused yet).
7. Not seen on Oracle's screen yet (saved browser sign-in expired 2026-11-02; steps in section 12).

## 12. What the pod actually did (live Create, ETIA-TEST, 2026-11-02; neutral ZZ_TEST_ names only)

Command: the folder's own plain run (`run.py --file request.json`, the same flow as `--run-batch`), run once, with a
wrapper that only kept `_work/` (no code change). Kept for inspection: `Transaction Sources/_work/live_create_20261102/`
(sent file, before / names / after data files, template, grouping rules file, Oracle's ProcessLog and both reports,
the run's output).

| Step | Start | End | Seconds | Result |
|---|---|---|---|---|
| `--check` (first try) | 04:54:44 | 04:54:58 | 14 | failed before Oracle: this PC couldn't look up the pod's host name (the DNS blip again) |
| `--check` | 04:55:22 | 04:56:38 | 76 | OK: 37 sets, template COMPLETED, data file 1 source, source list 22 |
| `--plan` (request.json) | 04:56:38 | 04:58:31 | 113 | "2 new, 0 already in Oracle, 0 with problems" |
| Create (whole run) | 04:58:43 | 05:01:49 | 184 | "Created 2 of 2", both "every value as sent" |
| Oracle's source list read | 05:02:08 | 05:02:11 | 3 | 24 sources, both new ones there |
| Rerun of the same request | 05:02:21 | 05:03:33 | 71 | "Created 0 of 2, 2 already there"; nothing sent |
| Saved sign-in check | after the rerun | | 16 | expired (saved 2026-10-30): not seen on screen |

What happened:
- **Route accepted.** Import process 100004734400090, Oracle request 4,429,165, status COMPLETED. ProcessLog: "Detail
  Object: TransactionBatchSource ... A total of 2 rows were processed. 0 rows of them failed"; CmTransactionBatchSource
  0 rows; "Receivables Transaction Batch Source ... already processed"; Total Objects Succeeded 2, Failed 0. The import
  itself took about 1 minute (sent 05:00:52, after-read saved 05:01:49).
- **Sent**: both rows in `ORA_AR_TXN_BATCH_SOURCE` only (AR_BATCH_SOURCE header line only), ISO dates, audit empty.
- **Where they show**: the next data file lists them under **`AR_BATCH_SOURCE`** (FSCR was right), now 3 rows
  (Distributed Order Orchestration, ZZ_TEST_TS_7731, ZZ_TEST_TS_7732); `ORA_AR_TXN_BATCH_SOURCE` 0 rows. Oracle's source
  list (`transactionSourcesLOV`) lists both (Common Set, description as sent): 22 -> 24.
- **Read-back**: from the data file, every sent value compared: Name, SetCode, Description, Status A, LastBatchNum 1,
  AutoTrxNumberingFlag Y, BatchSourceType INV / FOREIGN, InvalidLinesRule Reject, StartDate 2026/11/01 (slash form in
  the file), GroupName (7732). The source list can only confirm Name, set name and Description. Not comparable: the
  values we leave empty stay empty (no transaction type, credit source, legal entity, AutoInvoice "...Rule" options);
  Oracle filled only the audit columns. Distributed Order Orchestration unchanged.
- **Grouping rule DEFAULT on the Imported source: KEPT.** Sent `GroupName` DEFAULT; the data file after shows
  ZZ_TEST_TS_7732 with `GroupName` DEFAULT; no warning in the log.
- **Why the data file listed only 1 of 22 before** (guess, not proven): it seems to hold only sources not delivered as
  seed data or later changed (Distributed Order Orchestration was updated by a user in 2025); new sources are listed.
  The module keeps reading Oracle's source list for existing names.
- **Refused**: nothing. Length limits and how a failed row is named: not seen.

Where to see them in Oracle (not seen on screen; written from the task name and FSCR, the saved sign-in had expired):
Setup and Maintenance > offering **Financials** > functional area **Customer Billing** > task **Manage Transaction
Sources** > search Name `ZZ_TEST_TS` (Reference Data Set: Common Set) > open each one.

## Time log

| Phase | Start | Finish | Minutes |
|---|---|---|---|
| Spec + offline build + read-only check | 2026-11-01 23:29:24 +0500 | 2026-11-01 23:55:24 +0500 | 26 (26 min 0 s) |
| First live Create (2 sources), read-back, rerun, docs, matrix | 2026-11-02 04:54:15 +0500 | 2026-11-02 05:07:32 +0500 | 13 (13 min 17 s) |
