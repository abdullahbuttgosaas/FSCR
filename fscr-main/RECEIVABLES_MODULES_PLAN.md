# Receivables modules plan (Step 0 of the Receivables extension)

Read-only, offline. No Oracle calls were made (no REST, no export, no import, no browser). Nothing in the FSCR clone
or in the Setup Assistant project was changed. This file is the only file created.

**Legend.** **[F]** = stated in the FSCR files (path given). **[P]** = stated in my project's files.
**[J]** = my judgment (not stated anywhere; based on the facts next to it).

All FSCR paths below are relative to `fscr-main\fscr-main\pillars\erp\financials\`. Each skill folder has the same
file set [F]: `SKILL.md` (task metadata, `fscr-supported-operations`, `fscr-create-fields` / `fscr-update-fields`
markers), `e2e-adapter.json` (`package.entities`: headers, keys, required, create/update fields, value contracts,
blocked fields; `generation.readiness`/`blockers`; `package.evidenceRelease`; `deletionPolicy`),
`ora-resource\ora_rule_registry.json` (compiled rules), `ora-resource\ora_dependency_readiness.md` (prerequisites),
`ora_input_validation.md`, `ora_defaulting_rules.md`, `ora_reference_lookups.md`, `ora_design_enforcement.md`,
`ora_error_handling.md`, and `scripts\fsm_task_adapter.py` (plus extra scripts where listed).
"Files that list fields and rules" in the tables below = that set.

---

## 1. The 16 skills with the full create set

Definition used [F, earlier verification `verify_counts.py`]: the skill has its own script(s), the
`<!-- fscr-supported-operations: ... -->` create/update marker, an `e2e-adapter.json`, and an
`ora-resource\ora_rule_registry.json`. The saved scan
(`C:\Users\PC\AppData\Local\Temp\claude\E--GoSaaS-fscr-main-fscr-main\d71fd8b3-...\scratchpad\verify.json`, 2026-10-28/29)
was re-run today with the same script against the current clone: **same 16 paths** (1,126 SKILL.md scanned).
(A 17th skill, `expenses/manage-auto-submission-and-matching-options`, has the marker but no e2e adapter, so it is out.)

| # | Skill folder | Section [J, from functional area] |
|---|---|---|
| 1 | `customer-billing/manage-receivables-payment-terms` | Receivables (already built in my project) |
| 2 | `customer-billing/manage-autoinvoice-grouping-rules` | Receivables |
| 3 | `customer-billing/manage-transaction-sources` | Receivables |
| 4 | `customer-billing/manage-transaction-types` | Receivables |
| 5 | `customer-billing/manage-remit-to-addresses` | Receivables |
| 6 | `customer-billing/manage-autoaccounting-rules` | Receivables |
| 7 | `customer-payments/manage-receipt-classes-and-methods` | Receivables |
| 8 | `customer-payments/manage-receipt-sources` | Receivables |
| 9 | `receivables/manage-receivables-system-options` | Receivables (options task) |
| 10 | `payables/manage-payment-terms` | Payables |
| 11 | `payables/manage-payables-calendars` | Payables |
| 12 | `payables/manage-bank-charges` | Payables |
| 13 | `payables/manage-invoice-options` | Payables (options task) |
| 14 | `payables/manage-payment-options` | Payables (options task) |
| 15 | `payables/manage-common-options-for-payables-and-procurement` | general Financials options (Payables and Procurement) |
| 16 | `expenses/manage-conversion-rates-and-policies` | Expenses (options task per BU) |

---

## 2. Per-skill facts

Release: FSCR adapter `package.evidenceRelease` [F] vs the shared test pod ETIA-TEST, whose template showed release
**11.13.26.10.0** on 2026-10-30 [P, `Receivables Payment Terms/CLAUDE.md:156`].

Order pinning [F]: **all 16** adapters stop when a template's header order differs from `e2e-adapter.json`
(`scripts/fsm_task_adapter.py`: "header order differs from e2e-adapter.json") and fix each entity's `nodeSequence`
(Transaction Sources: "accepts only the two complete NodeSequence profiles observed ... arbitrary entity sequence
changes still fail"). So every one **pins the CSV header order and the entity order**.

Tests [F]: only Conversion Rates and Policies has test material (`e2e-test-catalog.json`,
`references/create-test-lifecycle.md`). The other 15 have **no tests**.

Readiness [F, `e2e-adapter.json` `generation.readiness` / `generation.blockers`]: 15 say `ready` with no blockers;
**Bank Charges says `blocked`** ("ORA_AP_BANK_CHARGE has no configured local row-index fields." and the same for
the line entity; its capabilities determinism / packageBuild / prerequisiteChecks / promptNormalization /
reconciliation / semanticValidation are `blocked`). Field-level blockers (status `blocked` / `partial` /
`requires_preflight` in `conditionallyBlockedFields`) are listed per task.

"Creates" vs "options": [F] keys and entity shape from `e2e-adapter.json`; the reading "one settings record per
business unit" is [J] from the key being only the business unit.

### Receivables

| Task (code) | Creates | Entities (create fields) [F] | Release [F] vs 26.10 | Readiness / blockers [F] |
|---|---|---|---|---|
| Manage Receivables Payment Terms (`AR_MANAGE_RECEIVABLES_PAYMENT_TERMS`) | new terms | `AR_PAYMENT_TERM` (16) header, `AR_PAYMENT_TERM_LINE` (9), `AR_PAYMENT_TERM_TRANSLATION` (6), `AR_PAYMENT_TERM_DISCOUNT` (10) | 11.13.26.10.0 = match | ready, none |
| Manage AutoInvoice Grouping Rules (`AR_MANAGE_AUTOINVOICE_GROUPING_RULES`) | new rules | `AR_AI_GROUPING_RULE` (5, key Name), `ORA_AR_AI_GRP_TXN_TYPE` (2, + Class11), `ORA_AR_AI_GRP_TXN_REQUEST` (3, + FromColumnName) | 11.13.26.10.0 = match | ready, none; AttributeCategory (DFF) `partial` |
| Manage Transaction Sources (`AR_MANAGE_TRANSACTION_SOURCES`) | new sources | `ORA_AR_TXN_BATCH_SOURCE` (9 create fields, key Name + SetCode, 111 columns); `AR_BATCH_SOURCE` (109 columns, 0 create fields: read-back only, "create persists through AR_BATCH_SOURCE") | 11.13.26.10.0 = match | ready, none; update supported for Description only |
| Manage Transaction Types (`AR_MANAGE_TRANSACTION_TYPES`) | new types | `AR_TRANSACTION_TYPE` (80, key SetCode + Name, 87 columns), `AR_REF_ACCT_TRX_TYPE` (19, + BuName) | 11.13.26.10.0 = match | ready; **blocked fields**: UsageCategoryCode, TrxSubclassCode, AllocateTaxFreight, Rec/Rev/TaxSegments ("The authoritative FSM path may create a valid combination and is not read-only") |
| Manage Remit-to Addresses (`AR_MANAGE_REMIT_TO_ADDRESSES`) | new addresses + receipt-from criteria | `AR_REMIT_TO_LOCATION` (14, key SetCode + TerritoryCode + Address1 + OrigSystemReference + PostalCode + State + City), `AR_REMIT_TO_ADDRESS` (13, + Country, State, PostalCodeLow/High) | 11.13.26.10.0 = match | ready; `partial`: SetCode/SetName ("Target access policy ... not yet reviewed"), Country, State, flexfields |
| Manage AutoAccounting Rules (`AR_MANAGE_AUTOACCOUNTING_RULES`) | rule per BU + account type (settings-like) | `AR_AUTO_ACCOUNTING` (18, key BuName + Type), `ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT` (22, + Segment, SegmentNum) | **11.13.27.01.0 ≠ 26.10** | ready, none |
| Manage Receipt Classes and Methods (`AR_MANAGE_RECEIPT_CLASSES_AND_METHODS`) | new classes / methods | `AR_RECEIPT_CLASS` (46, key Name), `AR_RECEIPT_METHOD` (55), `AR_RECEIPT_METHOD_ACCOUNT` (73, + BuName, BankAccountName, CurrencyCode, StartDate), `AR_CC_ERROR_MAPPINGS` (9) | **11.13.26.07.0 ≠ 26.10** (older) | ready, none |
| Manage Receipt Sources (`AR_MANAGE_RECEIPT_SOURCES`) | new sources | `AR_RECEIPT_SOURCE` (11, key BUName + Name) | **11.13.26.07.0 ≠ 26.10** (older) | ready; `partial`: BankAccountName (no public bank-method compatibility resolver), DFF |
| Manage Receivables System Options (`AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS`) | **options**: one `AR_SYSTEM_OPTIONS` row per BU ("`ORG_ID` owns one system-options row per BU") | `AR_SYSTEM_OPTIONS` (39 create fields of 202 columns, key BUName) | 11.13.26.10.0 = match | ready; `blocked` fields: BUName, CC/BA ReceiptMethodName ("runtime blocks on access denial or non-unique exact match") |

### Payables, Expenses, general options

| Task (code) | Creates | Entities [F] | Release [F] | Readiness [F] |
|---|---|---|---|---|
| Manage Payment Terms (`AP_MANAGE_PAYMENT_TERMS`) | new terms | `AP_TERM_HEADER` (55), `AP_TERM_LINE` (37), `AP_TERM_SUBSCRIPTION` (2), `AP_TERM_HEADER_TRANSLATION` (5) | 11.13.26.10.0 match | ready |
| Manage Payables Calendars (`AP_MANAGE_PAYABLES_CALENDARS`) | new calendars + periods | `AP_OTHER_PERIOD_TYPE` (25), `AP_OTHER_PERIOD_PERIOD` (29) | 11.13.26.10.0 match | ready |
| Manage Bank Charges (`ORA_AP_MANAGE_BANK_CHARGES`) | new charge groups | `ORA_AP_BANK_CHARGE` (44), `ORA_AP_BANK_CHARGE_LINE` (50), no key fields | 11.13.26.10.0 match | **blocked** (see above); CurrencyCode `blocked` |
| Manage Invoice Options (`AP_MANAGE_INVOICE_OPTIONS`) | **options** per BU (`AP_SYSTEM_PARAMETER`, key BuName) | 1 entity, 119 create fields | **11.13.27.01.0** | ready; Term names `blocked` until a resolver receipt |
| Manage Payment Options (`AP_MANAGE_PAYMENT_OPTIONS`) | **options** per BU (same `AP_SYSTEM_PARAMETER`) | 1 entity, 6 create fields | **11.13.26.04.0** | ready |
| Manage Common Options for Payables and Procurement (`AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT`) | **options** per BU (`AP_FINANCIAL_SYS_PARAM`, key BuName + EnterpriseId) | 1 entity, 74 create fields | 11.13.26.10.0 match | ready; account segments `partial`; ships `account_combination_create.py` |
| Manage Conversion Rates and Policies (`EXM_MANAGE_CONVERSION_RATES_AND_POLICIES`) | **options** per BU + currency tolerances | `EXM_EXCHANGE_RATE_OPTION` (6, key BuName), `EXM_EXCH_RATE_TOLERANCE` (6) | **11.13.27.01.0** | ready; BU, rate type, currency `requires_preflight`; **has tests** |

---

## 3. Prerequisites (what must exist in Oracle first) — Receivables

Quoted from each skill's `ora-resource/ora_dependency_readiness.md` [F]. Line numbers are of that file.

- **Receivables Payment Terms** — reference data set: "PT.DEP.SET | Reference data set | Yes | Every create, update,
  end-date ..." (l.26). Conditional: billing cycle ("Balance-forward behavior is requested"), Receivables System
  Options ("PartialDiscountFlag is enabled"). Nothing else required.
- **AutoInvoice Grouping Rules** — nothing mandatory beyond seeded data. "Transaction class | Yes | Each class child
  row | Lookup | GROUPING_TRX_TYPE system seed" (seeded). Conditional: "If LineOrderingRuleName is supplied, its exact
  name must exist in RA_LINE_ORDERING_RULES in the target pod" (dependency order table; row ordering_rule_name at l.18); group-by column "verify its exact
  FromColumnName and target-pod availability".
- **Transaction Sources** — "transaction_source_set | Reference data set | Yes | Every source" (l.20). Conditional:
  legal entity, "Standard transaction type | Resolve InvTrxTypeSetCode first, then TrxTypeName in that set",
  "AutoInvoice grouping rule | Resolve GroupName for an Imported source when supplied", Revenue Management document
  type, credit transaction source ("second import pass").
- **Transaction Types** — "reference_set | Reference data set | Yes | Every parent create" (l.19). Conditional: legal
  entity, application rule set, "payment_term | Default payment term | ... Supply both DefaultTermName and
  DefaultTermSetCode", related transaction types, "reference_account_context | Business unit and ledger | ... A
  reference-account child row is emitted", account combinations (`Blocked`, l.26).
- **Remit-to Addresses** — "remit_set | Existing authorized reference data set | Yes" (l.16); "remit_postal | Shared
  postal location and country validation | Yes"; "criteria_country | Receipt-from country | Yes | Criteria create"
  (l.18).
- **AutoAccounting Rules** — "Receivables-enabled business unit | Every operation" (l.9); "AutoAccounting account
  type | Every operation | One seeded supported Type code"; "Chart of accounts and segment structure | Every
  operation". "The skill never creates business units, ledgers, charts of accounts, value sets, or DFF deployments."
- **Receipt Classes and Methods** — receipt class for every child; conditional "RCM.DEP.BANK | Remittance bank
  account | Conditional | A receipt method is assigned remittance accounts" (l.21), "RCM.DEP.AUTOMATIC | Automatic
  receipt prerequisites" (payment channel, payment system/profile), "RCM.DEP.ACCOUNTING | Valid accounting
  combinations".
- **Receipt Sources** — "RS.DEP.BU | Receivables business unit | Yes | Every operation" (l.20). Conditional:
  receipt method and class ("Method/class is supplied or lockbox is intended"), bank account ("BankAccountName is
  supplied") plus "Bank existence alone does not prove the receipt source combination is valid".
- **Receivables System Options** — "business_unit | Business unit | Yes | Always" (l.19), "ledger | Ledger and chart
  of accounts | Yes | Always" (l.20); conditional item validation org, AutoCash / automatch / grouping / application
  rule sets, receipt methods, reference sets, transaction sources, transaction types, receivables activities,
  remittance bank accounts, accounting flexfield prompt, account combinations.

Non-Receivables, in short [F]: Payables Payment Terms — conditional Payables calendar and set code; Payables
Calendars — none beyond its own parent/child; Bank Charges — conditional legal entity, currency, bank, branch;
Invoice Options — BU (+EnterpriseId) and **three existing payment terms** (TermName, PrepaymentTermName,
EmployeeTermName); Payment Options — BU and the Invoice Options contract; Common Options — BU, ledger, account
combinations, conditional bill-to location, rate type, VAT country; Conversion Rates — BU, conversion rate type,
currency.

---

## 4. Comparison with my built Receivables Payment Terms module

My module's approach [P, `Receivables Payment Terms/CLAUDE.md`, `run.py`, `rpt_package.py`, `rpt_rules.py`,
spec `_fscr_spec/RECEIVABLES_PAYMENT_TERMS_SPEC.md`]:
(a) the file layout read from the pod's own template on every run (entity order from `ASM_SETUP_CSV_METADATA.xml`,
members in the template's order, headers from each CSV's first line, metadata copied byte for byte; only entity names
fixed in code); (b) setup task process without a browser (`setupTaskCSVImports`, Basic auth) — accepted live on
ETIA-TEST 2026-10-30 (`ZZRPT 9721`) per the folder's own observations, while the root index row still says UNTESTED;
(c) read-back by a fresh data file, field by field; (d) sheet tabs joined by name exactly; (e) rules without Oracle
in `rpt_rules.py`; (f) dates YYYY-MM-DD in the file; audit columns empty.

**Key difference with FSCR [F + P]:** FSCR pins header order and node sequence; my module reads them from the pod.
My CLAUDE.md records that FSCR's fixed order failed on ETIA-TEST for payment terms (LINE before TERM). So for every new
module: **take only field names, keys, required/create rules and value lists from FSCR, never the column or entity
order** [J].

| Task | Reuse layout-from-template / setup import / fresh-export read-back / tabs by name? [J] | Shape [F] | Fields that are lists from other Oracle data [F] | What is new [J unless marked] |
|---|---|---|---|---|
| AutoInvoice Grouping Rules | Yes, all four | header + 2 child tables (class, then group-by under class: 3 levels) | LineOrderingRuleName (existing ordering rule), FromColumnName (grouping characteristic), Class11 (seeded C/D/I) | three-level join (rule → class → column); no public list for ordering rules ("no public preflight GET established" [F]) — read them from the data file or leave to Oracle's import check |
| Transaction Sources | Yes | one created table + one read-back table (`AR_BATCH_SOURCE`) | SetCode, TrxTypeName + InvTrxTypeSetCode, GroupName, DocumentTypeCode, credit source + set, LegalEntityIdentifier | wide file (111 columns); create goes in one entity, read-back in another [F]; Manual vs Imported branches (`BatchSourceType=INV` / `FOREIGN`) [F]; LastBatchNum rule [F]; self-reference needs a second pass [F] |
| Transaction Types | Yes, but v1 header only | header + child per BU (`AR_REF_ACCT_TRX_TYPE`) | SetCode, payment term (name+set), rule set, related types, legal entity, BuName/LedgerName, account segments | 80 create fields; leave out every `blocked` field (usage category, subclass, segments, AllocateTaxFreight); no child accounting rows in v1 |
| Remit-to Addresses | Yes | location (header) + criteria child | SetCode, Country, State (geography), flexfield context | 7-part key including postal fields (`remit_identity.py` [F]); postal validation; criteria coverage choices |
| Receipt Sources | Yes | single flat table | BUName, receipt method/class, bank account | the BU list (`finBusinessUnitsLOV`, PROVEN in Price Lists [P]); FSCR release 26.07 so its rules need a check against the 26.10 template |
| Receipt Classes and Methods | Yes | class → method → bank account rows + card-error mappings (4 tables) | BuName, BankAccountName, CurrencyCode, accounting combinations, payment system/channel | bank accounts on the pod; accounting segments; release 26.07 |
| AutoAccounting Rules | Layout yes; but it is settings-like | header + segment child | BuName, Type (seeded), segment constants (value sets) | built on 27.01; one rule per BU and type |
| Receivables System Options | Layout yes; it updates one row per BU | single wide table (202 columns) | BU, ledger, many rule/method/source/type/activity/account names | options task: an update of a shared row, not a new record |

---

## 5. Safety on the shared test pod

Deletion [F, `e2e-adapter.json` `deletionPolicy`]: **no skill has a physical delete**. Disposition `unsupported` or
`unresolved` for all 16. What a test record leaves behind, and whether it can be retired:

| Task | Leaves behind [F/J] | End-date / inactivate? [F] | Flag [J] |
|---|---|---|---|
| Receivables Payment Terms | a term in its set (`ZZRPT 9721` already stays [P]) | FSCR: create, update and **end-date** supported; my module does not end-date yet | safe (new named record) |
| AutoInvoice Grouping Rules | a named rule + its class rows | **EndDate** is in `fscr-update-fields` | safe; only used when a transaction source names it |
| Transaction Sources | a source in the set (+ its numbering) | update proven for **Description only**; Status/EndDate exist, but "Never describe Status or EndDate retirement as delete" and no retirement evidence → **left as is** | safe if a new set-scoped name; cannot be cleaned through the proven route |
| Transaction Types | a type in the set | **Status / EndDate** in `fscr-update-fields` | **caution**: segment fields "may create a valid combination" (a new GL account combination on the pod's ledger, not removable) — leave them out |
| Remit-to Addresses | a location (shared postal location) + criteria | criteria **Status A/I** update supported; location deletion unsupported | **affects other users**: a criteria row with a country (or default coverage) can change which remit-to address other users' invoices get. Test only with a narrow, unused country/state/postal range |
| Receipt Sources | a source under a BU | **end-date** supported | safe (BU-scoped, new name) |
| Receipt Classes and Methods | class, method, bank-account rows | **end-date** of a method observed (process 207556) | caution: bank-account/remittance rows touch the pod's bank setup |
| AutoAccounting Rules | the rule for a BU + account type | none | **BU-wide setting**: changes accounting for every transaction in that BU; cannot be cleaned |
| Receivables System Options | changes the one row per BU | reverse-update only ("do not infer it from reverse-update cleanup") | **BU-wide setting**, affects every Receivables user of that BU |
| Invoice / Payment / Common Options, Conversion Rates | changes the one row per BU | "It does not support delete or end-date operations" (Invoice, Payment Options) | **BU-wide settings**; Common Options can also create account combinations (`account_combination_create.py`) |
| Payables Payment Terms, Payables Calendars | new named records | Payment Terms: EndDateActive update; Calendars: "does not support delete or end-date" | safe-ish; calendars stay |
| Bank Charges | charge group | none | adapter blocked |

---

## 6. Where to look in Oracle

[F] Every skill states the Setup and Maintenance task by name and functional area (`SKILL.md` `task_name`,
`functional_area`, offering Financials). **No FSCR file states the page or navigation where a person sees the created
record** (searched all `.md` files of the 16 for Setup and Maintenance / Navigator / page / UI path) → "not stated".
Fields to compare [F] = the entity keys and the `fscr-create-fields` of `SKILL.md` / `createFields` of
`e2e-adapter.json`; FSCR's own verification is a fresh export reconciled field by field
(`reconciliationPolicy.requestedRows = exact`, baseline rows unchanged).

| Task | Setup and Maintenance task [F] | Page to see the record | Fields to compare [F] |
|---|---|---|---|
| Receivables Payment Terms | Financials > Customer Billing > Manage Receivables Payment Terms | not stated in FSCR; my project uses "search for {name} (set {set})" on that task [P, `run.py:41`] | Name, SetCode, header defaults, line SequenceNum / RelativeAmount / due dates, discounts, translation Description |
| AutoInvoice Grouping Rules | Financials > Customer Billing > Manage AutoInvoice Grouping Rules | not stated | Name, Description, StartDate, EndDate, LineOrderingRuleName; Class11; FromColumnName |
| Transaction Sources | Financials > Customer Billing > Manage Transaction Sources | not stated | Name, SetCode, Description, BatchSourceType, StartDate, AutoTrxNumberingFlag, LastBatchNum, InvalidLinesRule, Status |
| Transaction Types | Financials > Customer Billing > Manage Transaction Types | not stated | SetCode, Name, Type, Status, StartDate, required flags (PostToGl, AccountingAffectFlag, CreationSign ...) |
| Remit-to Addresses | Financials > Customer Billing > Manage Remit-to Addresses | not stated | location key (SetCode, TerritoryCode, Address1, PostalCode, State, City); criteria Country, State, PostalCodeLow/High, Status |
| AutoAccounting Rules | Financials > Customer Billing > Manage AutoAccounting Rules | not stated | BuName, Type, Segment, SegmentNum, source/constant |
| Receipt Classes and Methods | Financials > Customer Payments > Manage Receipt Classes and Methods | not stated | class Name, method Name, bank account BuName / BankAccountName / CurrencyCode / StartDate |
| Receipt Sources | Financials > Customer Payments > Manage Receipt Sources | not stated | BUName, Name, Type1, AutoBatchNumbering, StartDateActive |
| Receivables System Options | Financials > Receivables > Manage Receivables System Options | not stated | BUName + the changed option fields |
| Payables / Expenses tasks | their task names above, functional areas Payables / Expenses | not stated | their entity keys + create fields |

---

## 7. Effort and build order (Receivables)

Effort is my judgment [J] from section 4: **small** = one or two tables, few create fields, no other-data lists that
need new lookups; **medium** = a wide table or a new list source or a second-pass/branch rule; **large** = many
tables or fields, bank/accounting data, or blocked fields to fence off.

| Order | Task | Section | Prerequisites (must exist) [F] | Release vs 26.10 [F] | Safety [J] | Effort [J] |
|---|---|---|---|---|---|---|
| done | Receivables Payment Terms | Receivables | reference data set | match | safe, end-datable (not yet in module) | built |
| 1 | AutoInvoice Grouping Rules | Receivables | none (seeded classes); optional ordering rule | match | safe, end-datable | **small** |
| 2 | Transaction Sources | Receivables | reference data set; optional type, grouping rule | match | safe, but stays (no proven retirement) | **medium** |
| 3 | Transaction Types (header only) | Receivables | reference data set; optional payment term, rule set | match | caution: no segment fields | **large** (v1 header only: medium) |
| 4 | Receipt Sources | Receivables | Receivables business unit; optional method, bank | 26.07 (older) | safe, end-datable | **medium** |
| 5 | Receipt Classes and Methods | Receivables | receipt class; bank accounts, accounting, payment setup for automatic | 26.07 (older) | caution: bank rows | **large** |
| 6 | Remit-to Addresses | Receivables | reference data set, postal location, country | match | **affects other users** (coverage) | **medium-large** |
| skip | AutoAccounting Rules | Receivables | BU, account type, chart of accounts | **27.01** | **BU-wide, no cleanup** | — |
| skip | Receivables System Options | Receivables | BU, ledger, many | match | **BU-wide setting** | — |

Reasons for the order [J]:
1. **AutoInvoice Grouping Rules first**: smallest, no required prerequisite, release matches, can be end-dated, and
   Transaction Sources (Imported) can name it — dependencies first. Proves a three-level child join with the existing
   approach.
2. **Transaction Sources** next: needs only a reference data set (my module already reads `setIdSetsLOV`); its optional
   references (grouping rule, transaction type) can point at what exists on the pod or what step 1 made.
3. **Transaction Types** third, header only: it depends on Payment Terms (done) and is referenced by Transaction Sources
   and System Options; large field set, so v1 leaves out the blocked and accounting fields. (Built after Sources
   because Sources can use the pod's existing types; safest-first.)
4. **Receipt Sources** before Receipt Classes: a single flat table and end-datable; a manual source does not need a
   receipt method. Check FSCR's 26.07 rules against the 26.10 template's real columns first.
5. **Receipt Classes and Methods**: four tables and bank/accounting references; only after the simpler ones work.
6. **Remit-to Addresses** last: medium effort but its receipt-from criteria can change behaviour for other users of
   the shared pod; build it with a test range nobody uses and confirm the test design with the pod's other users.

Skip for now:
- **AutoAccounting Rules** — built on release 27.01 (pod is 26.10) [F] and is a BU-wide accounting setting with no
  cleanup [F/J].
- **Receivables System Options** — options task: changes the single row per BU that every Receivables user of that BU
  relies on; deletion has no contract; several resolver fields `blocked` [F].
- Outside Receivables (for later, not this extension): **Bank Charges** is self-declared `blocked` [F]; **Invoice
  Options** and **Conversion Rates and Policies** are built on 27.01 [F]; **Invoice / Payment / Common Options** and
  **Conversion Rates** are BU-wide settings [J]; **Payment Options** built on 26.04 [F]. Payables Payment Terms already
  exists in my project (browser route) [P]. Payables Calendars (26.10, simple parent/child) is the one clean Payables
  candidate [J].

Rules to carry into every new module [J]: read layout from the pod's template (never FSCR's pinned order); send only
FSCR `createFields`, never `blocked` / `partial` fields in v1; leave who-columns empty; dates as the pod's loader
accepts (my RPT finding: YYYY-MM-DD); test names `ZZ_TEST_...`, recorded under "Material" because nothing can be
deleted.

---

## 8. Time log

| Phase | Start | End |
|---|---|---|
| Step 0: classify 16 skills and write this plan (read-only, offline) | 2026-11-01 22:00:50 +0500 | 2026-11-01 22:06:50 +0500 |
