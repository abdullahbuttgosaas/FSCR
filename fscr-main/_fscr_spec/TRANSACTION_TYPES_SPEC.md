# Transaction Types module: spec (header only)

Written 2026-11-02, before the offline build; section 9 is filled in after the read-only check on ETIA-TEST, section 12
after the first live Create (one type, the same day). Layout follows `TRANSACTION_SOURCES_SPEC.md`.

- Configuration project: `E:\GoSaaS\Configuration Automation v2.1\Configuration Automation`
- FSCR repo (read-only): `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`
- Plan: `fscr-main\RECEIVABLES_MODULES_PLAN.md` (build order 3 of the Receivables extension: "v1 header only").

Short names: **SKILL** = `fscr-main/pillars/erp/financials/customer-billing/manage-transaction-types/SKILL.md`;
**RES/** = its `ora-resource/` folder; **ADP** = its `scripts/fsm_task_adapter.py`; **E2E** = its `e2e-adapter.json`.
Labels: **[F]** stated in FSCR files, **[P]** our project, **[J]** my judgment, **[?]** to confirm live.

**Hard rules** (user, 2026-11-01 / 2026-11-02): nothing named Corsair, Intel, AMD or NVIDIA is ever sent to Oracle, not
even in a read-only check; anything that touches Oracle uses neutral `ZZ_TEST_` names. **Header only: every accounting
and GL account field is left out** of this version (section 1, "Left out").

---

## 1. The Oracle object

**Task:** Manage Transaction Types, code `AR_MANAGE_TRANSACTION_TYPES`, Financials > Customer Billing (functional area
code `ORA_FIN_CUST_BILL`) [F, SKILL frontmatter]. CSV export/import supported, import mode FSM [F]. Adapter evidence
release **11.13.26.10.0** [F, E2E `package.evidenceRelease`].

What it is [J]: a transaction type names a kind of Receivables transaction (invoice, debit memo, credit memo, ...) and
how it behaves: whether it creates an open receivable, posts to the general ledger, allows freight, calculates tax,
how it is applied, and which payment term it starts with. Transaction sources and AutoInvoice point at it.

**Entities** [F, E2E `package.entities`; SKILL "Source-Backed Task Behavior"]:

| Role | Entity / CSV | Key | Use in this module |
|---|---|---|---|
| Transaction type (parent) | `AR_TRANSACTION_TYPE` | SetCode + Name ("never identify a transaction type by Name alone") | the rows we send |
| Reference accounts (child, per business unit) | `AR_REF_ACCT_TRX_TYPE` | AR_TRANSACTION_TYPE.SetCode + AR_TRANSACTION_TYPE.Name + BuName | **never sent in v1**: header line only (it holds only accounting: BU, ledger and account segments) |

FSCR's adapter lists 87 / 24 columns; node paths `/TransactionTypeVO/TransactionTypeVORow` and
`.../ReferenceAccount/ReferenceAccountVORow`, NodeSequence 1 / 2 [F]. We read all of this from the pod (section 3).

**Fields of `AR_TRANSACTION_TYPE`** (FSCR create contract, RES/ora_input_validation.md "Parent create contract"; types
E2E `types`; values E2E `valueContracts`):

| Field | Sheet column | Type [F] | Required [F] | Max [F] | Allowed values | v1 |
|---|---|---|---|---|---|---|
| Name | Name | string | yes | **20** characters | text; with the set it is the key | sheet, **asked** |
| SetCode | Set Code | string | yes | n/a | an exact reference data set code | sheet, **asked** (live list) |
| Description | Item Description | string | no | **80** characters | text | sheet, optional |
| Type | Class | string | yes | n/a | [F] ADJ Adjustment, BR Bills Receivable, CB Chargeback, CM Credit Memo, DEP Deposit, DM Debit Memo, GUAR Guarantee, INV Invoice. **v1 offers Invoice and Debit Memo only** [J]: the only verified creation sign is Positive (a credit memo needs a negative sign), and BR / DEP / GUAR / CB / ADJ need related types, drawee or bills-receivable setup that v1 doesn't have | sheet, **asked** |
| Status | Status | string | yes | n/a | [F] A, D, I (labels not given). v1: Active (A), Inactive (I) [J]; D is not offered (meaning not evidenced) | sheet, **asked** |
| StartDate | From Date | date | yes | n/a | ISO date | sheet, **asked** |
| EndDate | To Date | date | no | n/a | ISO date, not before StartDate [F] | sheet, optional |
| AccountingAffectFlag | Open Receivable | Y/N | yes | n/a | Yes / No | sheet, **asked** |
| PostToGl | Post to GL | Y/N | yes | n/a | Yes / No | sheet, **asked** (a flag, not an account; see "Left out") |
| AllowFreightFlag | Allow Freight | Y/N | yes | n/a | Yes / No | sheet, **asked** |
| TaxCalculationFlag | Tax Calculation | Y/N | yes | n/a | Yes / No | sheet, **asked** |
| NaturalApplicationOnlyFlag | Natural Application Only | Y/N | yes | n/a | Yes / No; **not Yes together with Allow Overapplication** [F] | sheet, **asked** |
| AllowOverapplicationFlag | Allow Overapplication | Y/N | yes | n/a | Yes / No | sheet, **asked** |
| CreationSign | Creation Sign | string | yes | n/a | **only `P` / "Positive Sign" is verified** [F, RES/ora_reference_lookups.md "Verified safe value subset"]; every other value is blocked | sheet, **asked** (one choice) |
| DefaultStatus | Transaction Status | string | yes | n/a | **only `OP` / "Open" is verified** [F]; every other value is blocked | sheet, **asked** (one choice) |
| DefaultPrintingOption | Printing Option | string | yes | n/a | [F] N, NOT, PRI (labels not given). v1: Print (PRI), Do Not Print (NOT) [J]; N is not offered | sheet, **asked** |
| DefaultTermName + DefaultTermSetCode | Payment Term + Payment Term Set | string | no | n/a | **supplied together** [F]; an existing Receivables payment term in that set | sheet, optional (section 5) |

**Ask; never default** [F: "Require explicit create values for SetCode, Name, PostToGl, AccountingAffectFlag, Status,
Type, DefaultPrintingOption, DefaultStatus, AllowFreightFlag, AllowOverapplicationFlag, CreationSign, StartDate,
TaxCalculationFlag, and NaturalApplicationOnlyFlag; do not invent defaults for these fields"; RES/ora_defaulting_rules.md
"No other business default is authorized"]: all 14 of those. **No defaults are applied** (unlike Transaction Sources):
an empty required cell is red. Optional fields left empty are omitted (sent empty) [F].

**Left out of v1, and why:**

| Fields | Why left out |
|---|---|
| **Every accounting / GL account field**: the whole `AR_REF_ACCT_TRX_TYPE` child (BuName, LedgerName, SourceRefTable, Rec / Rev / Tax / Freight / Unearned / Unbilled / Clearing / DepositOffset / DistSet / Drc / BrUnpaid / BrRemit / BrFactor Segments) and `AllocateTaxFreight` | **User's hard rule for this version.** FSCR: "The authoritative FSM path may create a valid combination and is not read-only" (RES/ora_dependency_readiness.md `account_combination`): sending account segments can create new GL account combinations in the shared pod's ledger, which can't be removed. Without reference accounts the type has none; AutoAccounting decides the accounts at transaction time [J] |
| AdjPostToGlFlag, AllowFutureAcctDateFlag | accounting behaviour flags; optional; kept out with the accounting fields [J] |
| UsageCategoryCode, TrxSubclassCode | **blocked** in FSCR until the pod's codes are verified (RESOLVER-USAGE-CATEGORY / -TRANSACTION-SUBCLASS) |
| CreditMemoTypeName + set, SubsequentTrxTypeName + set | related transaction types (a type naming another type; would need this module to depend on itself, second pass) [J]: later |
| RuleSetName (application rule set), LegalEntityIdentifier | optional references to objects no module creates; later with read-only lists [J] |
| ControlCompletion, SignedFlag, DraweeIssuedFlag, ExcludeFromLateCharges, MagneticFormatCode, DocumentType | optional; not needed for an Invoice / Debit Memo header; MagneticFormatCode and DocumentType "must not be inferred" [F] |
| Attribute*, GlobalAttribute* (flexfields) | need their exact context [F]; none on the pod's sheet |
| LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin | audit: always empty [F] |

Update (Description, Status, EndDate are FSCR's only update fields) and delete (no physical delete [F]) are not
supported: an existing Set Code + Name is skipped and never changed.

## 2. Checks before Create (all in `--plan`)

| Check | Rule | Reads from |
|---|---|---|
| Name present, text, no outer spaces, at most 20 characters (count shown, never cut) | red | rule [F] |
| Set Code | one of Oracle's reference data sets (exact code) | `setIdSetsLOV` (REST GET, proven) |
| Already in Oracle | exact Name + Set Code -> **skipped** | the data file and, if it is incomplete, a read-only list (section 9) |
| Capitals-only match in the same set | yellow note, sent as new | same |
| Same Name + Set twice in the sheet | red on the later row | sheet |
| Item Description | at most 80 characters (count shown) | rule [F] |
| Class | Invoice / Debit Memo (codes INV / DM also taken); the other six classes red "not offered yet" | rule [F + J] |
| Status | Active / Inactive | rule |
| From Date / To Date | required / optional, YYYY-MM-DD, To not before From | rule [F] |
| The six Yes/No flags | each required, Yes or No | rule [F] |
| Natural Application Only + Allow Overapplication | not both Yes | rule [F] |
| Creation Sign | Positive Sign (or P) only | rule [F] |
| Transaction Status | Open (or OP) only | rule [F] |
| Printing Option | Print / Do Not Print (PRI / NOT) | rule [F + J] |
| Payment Term + Payment Term Set | both or neither; the set must be a reference data set | rule [F] + `setIdSetsLOV` |
| Payment term exists | on this sheet's Receivables Payment Terms tab -> created first (section 5); else must be in Oracle (Name + set); else red with the terms Oracle has in that set | Receivables payment terms data file (`AR_MANAGE_RECEIVABLES_PAYMENT_TERMS`, read-only, only when a type names a term) |
| Pod layout | both entities present, task right, COMPLETED, release = data file's, pod = .env host | template + data file |

## 3. File layout

Read from the pod's own template on every run (`setupTaskCSVTemplateExports`; fallback the data file), exactly as the
Transaction Sources module: entity order from the metadata, members in the template's zip order, metadata byte for
byte, headers from each CSV's first line, types by name, quoting and line ends as the template's. Only the two entity
names are fixed in code. FSCR pins 87 / 24 columns and the header order [F]; we don't. The import file carries rows
only in `AR_TRANSACTION_TYPE`; `AR_REF_ACCT_TRX_TYPE.csv` is its header line only. Dates ISO; audit columns empty.

## 4. Create route and read-back

Route: the setup task process without a browser (`setupTaskCSVImports/AR_MANAGE_TRANSACTION_TYPES`, Basic auth), proven
for Business Units, Receivables Payment Terms, AutoInvoice Grouping Rules and Transaction Sources [P]. **UNTESTED for
this task until 2026-11-02; PROVEN on ETIA-TEST 2026-11-02** (section 12).
Run (`--run-batch`): the same checks; names read again just before sending (a type made meanwhile is skipped); a type
whose payment term was on the sheet is checked once more against Oracle's terms (it must exist by now, else the type is
not sent); ONE file for all new types; sent once; polled every 10 s; never resubmitted; Oracle's log saved in `_work/`.

Read-back (fresh data file): each sent type must appear once under SetCode + Name in `AR_TRANSACTION_TYPE`; every sent
non-audit value is compared, dates as dates (FSCR: a persisted `YYYY/MM/DD` equals the sent `YYYY-MM-DD`, "DISC-MTT-
STARTDATE-CANON"); other types' rows identical before and after (a change is a note, the pod is shared); no
`AR_REF_ACCT_TRX_TYPE` row for the new type (we sent none). If the data file doesn't list a new type (as happened with
Transaction Sources), the read-only list confirms name, set and description only, and the result says so.
Results: created and checked / skipped / refused with Oracle's reason (pause-and-ask) / saved but not as sent / may
have been saved.

## 5. Dependencies and links

| Need | Mandatory | On the sheet? | Read from Oracle before Create | When missing |
|---|---|---|---|---|
| Reference data set (`SetCode`) | **yes** | no module creates sets | `setIdSetsLOV` | red with Oracle's set codes |
| Receivables payment term (`DefaultTermName` + `DefaultTermSetCode`) | no | **yes**: the Receivables Payment Terms tab | the Receivables payment terms data file (Name + SetCode of `AR_PAYMENT_TERM`) | on the sheet (same name): the type waits (registry `depends_on`); the payment terms group runs first (registry order); if that term failed or the user skipped it, the type is **not sent** and says why; at Create the term is read again from Oracle (missing -> not sent). Not on the sheet and not in Oracle in that set: red with the term names Oracle has in that set |
| Payment term's set | with a term | the term's own Set Code on its tab | `setIdSetsLOV` | red (must be a set) |
| Related transaction types (credit memo type, subsequent type) | no | this module (self-reference) | data file / list | **not in v1** |
| Application rule set, legal entity | no | no | no read-only list proven | **not in v1** |
| Business unit + ledger, account combinations (child rows) | n/a in v1 | no | n/a | **left out** (hard rule, section 1) |

Note on the payment term match [J]: the page's `depends_on` matches one column (the term's Name). The sheet's Payment
Term Set should be the set of that term's row on the Receivables Payment Terms tab; if it isn't, the term won't be
found in that set at Create and the type is not sent (said in its result).

**Used by:** Transaction Sources (`TrxTypeName` + `InvTrxTypeSetCode`, the default transaction type) [F]; AutoInvoice
and Order Management to Receivables (a transaction type per order type) [J]; Receivables System Options [F, plan].

**Wiring Transaction Sources' default transaction type later** (left out of that module in v1): add a column "Default
Transaction Type" (+ its set, or the source's own set) on the Transaction Sources tab with keys `trx_type` /
`trx_type_set`; in that folder's rules + file builder fill `TrxTypeName` / `InvTrxTypeSetCode`; existence: this
module's data file or list; and a `depends_on` on the "Transaction Types" group (column "Default Transaction Type",
match "Name", key `trx_type_pending`). **One shared-code addition is needed:** a registry group has ONE `depends_on`
today (Transaction Sources already uses it for grouping rules), so `workbook.depends()` and `server.hold_dependents()`
must accept a list of dependencies (additive: a single object keeps working). Registry order already allows it: this
group is placed **before** Transaction Sources (after AutoInvoice Grouping Rules), so types run before sources.

Works on an empty pod (only a reference data set is needed; COMMON exists everywhere [J]; a payment term only when one
is named) and on a populated pod (existing Name + Set skipped).

## 6. Sheet design (Receivables side only)

One tab **Transaction Types**, section "Transaction Types (Manage Transaction Types)". No defaults: every required
column must be filled.

| Column | Key | Type | Req. | Hint |
|---|---|---|---|---|
| Name | name | text, keep_spaces | * | At most 20 characters. An existing name in the same set is skipped |
| Set Code | set_code | pick (live sets), check folder | * | Never filled in for you |
| Item Description | description | text | | At most 80 characters |
| Class | trx_class | pick Invoice / Debit Memo | * | The other classes are not offered yet |
| Status | status | pick Active / Inactive | * | |
| From Date | from_date | date, start | * | |
| To Date | to_date | date, end | | |
| Open Receivable | open_receivable | yes-no | * | |
| Post to GL | post_to_gl | yes-no | * | Accounts are not set here (not offered yet) |
| Allow Freight | allow_freight | yes-no | * | |
| Tax Calculation | tax_calculation | yes-no | * | |
| Natural Application Only | natural_application | yes-no | * | Not Yes together with Allow Overapplication |
| Allow Overapplication | allow_overapplication | yes-no | * | |
| Creation Sign | creation_sign | pick Positive Sign | * | Only Positive Sign is offered |
| Transaction Status | transaction_status | pick Open | * | Only Open is offered |
| Printing Option | printing_option | pick Print / Do Not Print | * | |
| Payment Term | payment_term | text, check folder, dropdown_warn | | A term on the Receivables Payment Terms tab, or one Oracle has |
| Payment Term Set | payment_term_set | pick (live sets), check folder | | Required with Payment Term |

Registry: group "Transaction Types", area Receivables, **after AutoInvoice Grouping Rules and before Transaction
Sources**, `batch_run`, `oracle_check`, `plan_skips_red_fields`, `ask_on_refusal`, and `depends_on` {group "Receivables
Payment Terms", column "Payment Term", match_column "Name", key "payment_term_pending", request_key "payment_term"}.

## 7. Test plan

Offline: the 8 generic behaviours, the 2 check cases, and the real folder through `stub_transaction_types.py`: happy
path, payment term already in Oracle, payment term on the sheet (pending, then checked at Create; missing then -> not
sent), payment term missing everywhere (red), term without set (red), every required field missing (red, never
defaulted), Name 21 / Description 81 characters (red with counts), Natural Application + Overapplication both Yes,
Credit Memo class (red), sign / status other than the verified value (red), To before From, existing / capitals / twice,
refused value at Create -> pause and ask, an incomplete data file (a type only in the list), layout stops, route
refused, check can't run, a sheet preview through the page with the dependency note, and the page's dependency run:
a payment term and a type in one upload; the term failing -> the type not sent.

Live (later, separate request, after the user says go): one Invoice type `ZZ_TEST_TT_<4 digits>` in COMMON without a
payment term; read back; rerun skipped. A type with a payment term only after that.

## 8. Sample record (local sample workbook only, never sent to Oracle)

The Corsair story (one workbook): Corsair's OEM sales to Intel, AMD and NVIDIA are billed from Order Management through
AutoInvoice: payment term **CRSR NET 45** (Receivables Payment Terms; that module's names are at most 15 characters)
-> grouping rule **CORSAIR OEM BY ORDER REFERENCE** -> transaction type **CORSAIR OEM INVOICE** with that term ->
transaction source **CORSAIR OEM ORDERS**. The workbook `Transaction Types/manual-notes/Receivables_Corsair_sample.xlsx`
holds the whole story: 3 terms, 2 grouping rules, 4 types (3 name a term on the same sheet), 3 sources.

| Name | Set | Description | Class | Status | From | Open Rec. | Post GL | Freight | Tax | Natural | Overapp. | Sign | Trx Status | Printing | Payment Term (set) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CORSAIR OEM INVOICE | COMMON | OEM invoices to Intel, AMD and NVIDIA from Order Management | Invoice | Active | 2026-11-01 | Yes | Yes | Yes | Yes | No | No | Positive Sign | Open | Print | CRSR NET 45 (COMMON), a row on the payment terms tab |
| CRSR EARLY PAY INV | COMMON | OEM invoices for early-pay accounts (2% 10, net 30) | Invoice | Active | 2026-11-01 | Yes | Yes | Yes | Yes | No | No | Positive Sign | Open | Print | CRSR 2/10 N30 (COMMON) |
| CORSAIR GPU COOLING | COMMON | Large GPU cooling orders billed half at 30, half at 60 days | Invoice | Active | 2026-11-01 | Yes | Yes | Yes | Yes | No | No | Positive Sign | Open | Print | CRSR 50/50 N60 (COMMON) |
| CORSAIR OEM DEBIT | COMMON | OEM debit memos for freight and price corrections | Debit Memo | Active | 2026-11-01 | Yes | Yes | Yes | Yes | No | No | Positive Sign | Open | Do Not Print | (none) |

(The source's default transaction type is not wired yet: section 5.)

## 9. Read-only check on ETIA-TEST (2026-11-02; neutral ZZ_TEST_ requests only; nothing created)

| Topic | FSCR says | The pod did |
|---|---|---|
| Layout | AR_TRANSACTION_TYPE (1), AR_REF_ACCT_TRX_TYPE (2); 87 / 24 headers pinned | **exactly FSCR's**: entity order, NodeSequence 1 / 2, node paths, 87 / 24 headers in the same order, field types; release 11.13.26.10.0. Saved as the test fixture `pod_layout_etia_test/` |
| Template call | not used (Core Data Loader) | `setupTaskCSVTemplateExports` accepted, COMPLETED |
| Existing types | fresh same-task export; `transactionTypesLOV` only "discovery evidence" | **the data file lists all 21 types; `transactionTypesLOV` lists the same 21** (all COMMON: 12 Invoice, 9 Credit Memo, no Debit Memo). Unlike Transaction Sources, the data file is complete here; the module still reads both [P] |
| Reference accounts | child per BU | 3 rows on the pod (BUU1 Invoice / Credit Memo for BU BUU1, Invoice for AMNA BU); 18 of 21 types have none |
| CreationSign / DefaultStatus | only P / OP verified | the pod's types use CreationSign **A, P and N**; DefaultStatus OP on all. v1 still offers P only [J] |
| DefaultPrintingOption | N, NOT, PRI (no labels) | PRI on most; N on the PSFT types |
| Natural / overapplication | not both Y | one of them Y on most types; both N on ORA_PA_Prepayment |
| Payment term reference | name + set, FSM resolver | the Receivables payment terms data file lists 12 terms in COMMON (30 Net, IMMEDIATE, ...); existing types use 30 Net and IMMEDIATE |
| Preview | n/a | ZZ_TEST_TT_6421 (Invoice, no term) new; ZZ_TEST_TT_6422 (Debit Memo, 30 Net / COMMON) new; ZZ_TEST_TT_6423 (term ZZ_TEST_NO_SUCH_TERM) red with Oracle's 12 terms as the fix |
| Times | n/a | `--check` 65 s, `--plan` (3 requests) 81 s; no network blip |

No design change was needed after the check (the data file is complete, and the type list stays as a cross-check and
read-back fallback). Details: the folder's CLAUDE.md > Observed in the read-only check.

## 10. What FSCR gave and what we still had to do

| FSCR gave | Evidence |
|---|---|
| Task code, two entities, keys, 87 / 24 headers, types, node paths | E2E `package.entities` |
| The 14 required create fields, "do not invent defaults" | SKILL, RES/ora_input_validation.md, RES/ora_defaulting_rules.md |
| Name 20, Description 80 characters, never truncated | E2E `fieldConstraints`, RES/ora_input_validation.md (SRC-E2E-MTT-FIELD-LENGTH-20260909) |
| Fixed domains (class, status, printing, completion), Y/N flags, the natural / overapplication rule, EndDate >= StartDate | RES/ora_input_validation.md, E2E `valueContracts` |
| Only `P` and `OP` verified for CreationSign / DefaultStatus | RES/ora_reference_lookups.md |
| Payment term needs name + set together | RES/ora_dependency_readiness.md `payment_term` |
| Account segments may create GL combinations | RES/ora_dependency_readiness.md `account_combination` |
| Persisted `YYYY/MM/DD` = sent `YYYY-MM-DD` for StartDate / EndDate | RES/ora_design_enforcement.md |

| Gaps | Evidence |
|---|---|
| No labels for Status (A/D/I) or DefaultPrintingOption (N/NOT/PRI) | E2E `valueContracts` (label = code) |
| `transactionTypesLOV` is "discovery evidence" only, no proven Name + SetCode preflight | RES/ora_reference_lookups.md |
| Whether the data file lists every type (Transaction Sources' did not) | not stated; on ETIA-TEST it does (section 9) |
| No tests in the skill | folder listing |
| Header order and NodeSequence pinned | ADP, E2E |

## 11. Open questions and risks

1. ~~Route~~: accepted (section 12).
2. ~~Does Oracle accept a type with Post to GL Yes and no reference accounts?~~ Yes (section 12). (FSCR's evidence created types; whether
   with accounts is not stated.) Does Oracle require Open Receivable Yes when Post to GL is Yes? [?]
3. The meaning of Status D and Printing Option N [?] (N is used by the pod's PSFT types).
4. ~~Does the data file list every type?~~ Yes on ETIA-TEST (21 = 21, section 9).
6. Does the Receivables payment terms data file list every term? Not proven (12 in COMMON seen).
7. ~~Both Natural Application Only and Allow Overapplication No~~: accepted (section 12).
8. Length limits and how the log names a failed row: not seen (nothing refused yet). A type with a payment term: not
   run live yet.
5. A test type can't be deleted [F: no physical delete]; it can be made Inactive / end-dated only by an update this
   module doesn't do.

## 12. What the pod actually did (live Create, ETIA-TEST, 2026-11-02; neutral ZZ_TEST_ name only)

One type, `ZZ_TEST_TT_6421` (Invoice, COMMON, no payment term), through the folder's own run, once, with a wrapper that
only kept `_work/` (kept in `Transaction Types/_work/live_create_20261102/`).

| Step | Start | End | Seconds | Result |
|---|---|---|---|---|
| `--plan` | 05:39:42 | 05:40:43 | 61 | 1 new, 0 problems |
| Create (whole run) | 05:40:55 | 05:43:06 | 130 | "Created 1 of 1", "every value as sent" |
| Type list read | 05:43:20 | | a few | 22 types (was 21), the new one with its set and description |
| Rerun | 05:43:31 | 05:44:23 | 51 | "1 already there"; nothing sent |

- **Route accepted.** Import process 100004734402166, Oracle request 4,429,252, COMPLETED; ProcessLog: TransactionType
  "A total of 1 rows were processed. 0 rows of them failed"; Total Objects Succeeded 2, Failed 0.
- **Where it shows**: the next data file under `AR_TRANSACTION_TYPE` (21 -> 22); Oracle's type list (21 -> 22).
- **No accounts made**: `AR_REF_ACCT_TRX_TYPE` still the same 3 rows, none for the new type; other types unchanged.
- **Read-back**: every sent value equal (dates as dates: persisted 2026/11/01 = sent 2026-11-01); Oracle filled only
  the audit columns; empty fields stayed empty.
- **Answered**: Post to GL Yes with no reference accounts is accepted; Natural Application Only and Allow
  Overapplication both No is accepted.
- **Refused**: nothing. Length limits and failed-row naming: not seen. Not seen on Oracle's screen (saved sign-in
  expired). Not yet with a payment term or through the upload sheet.

## Time log

| Phase | Start | Finish | Minutes |
|---|---|---|---|
| First live Create (1 type), read-back, rerun, docs | 2026-11-02 05:39:41 +0500 | 2026-11-02 05:45:16 +0500 | 5 (5 min 36 s) |
| Spec + offline build + read-only check | 2026-11-02 05:12:50 +0500 | 2026-11-02 05:38:07 +0500 | 25 (25 min 17 s) |
