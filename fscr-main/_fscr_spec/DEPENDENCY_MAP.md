# Dependency map (modules of the Receivables plan and the existing ones they touch)

Written 2026-11-01. Rule (root `CLAUDE.md` > Design principles): a need that is a row in the sheet is created first and
the dependent item isn't sent if it failed or was skipped; otherwise it must already exist in Oracle and the check
reads Oracle before Create; otherwise a red problem with the fix.

Sources: each FSCR skill's `ora-resource/ora_dependency_readiness.md` [F]; our project [P]; my judgment [J].
"to confirm" = not proven yet.

| Module (status) | Needs (mandatory **bold**) | Already built module that can supply it | Used by | Notes |
|---|---|---|---|---|
| Business Units (built, OM side) | location, default set [P] | n/a | Receipt Sources, Receivables System Options, Remit-to (via set), Price Lists | Price Lists already `depends_on` Business Units [P] |
| Receivables Payment Terms (built, live-tested 2026-10-30) | **reference data set** [F]; billing cycle, Receivables System Options only for options v1 leaves out | none (sets are read from Oracle, `setIdSetsLOV`) [P] | Transaction Types (DefaultTermName + set; sheet `depends_on`, built 2026-11-02) [F]; customer profiles (to confirm) | no hard sheet dependency |
| **AutoInvoice Grouping Rules (built offline 2026-11-01)** | none mandatory; class codes seeded [F]; a characteristic must already be used by a rule in Oracle (read from the task's data file before Create; no public list exists [F]), else red; line ordering rule left out of v1 | none | Transaction Sources (GroupName, Imported sources) [F]; Receivables System Options (GroupingRuleName, required there) [F] | works on an empty pod |
| Transaction Sources (built 2026-11-01; **Create PROVEN on ETIA-TEST 2026-11-02**) | **reference data set** (read from `setIdSetsLOV`) [F]; grouping rule for an Imported source: a row on the sheet (registry `depends_on`, the source waits and is not sent if the rule failed or was skipped) or already in Oracle (read from the grouping rules data file), else red; transaction type, legal entity, document type, credit source (second pass) [F]: not in v1 | Grouping Rules (sheet `depends_on`, built); Transaction Types when built | Receivables System Options (late-charge / BR sources) [F] | GroupName on create: accepted and kept (live, ZZ_TEST_TS_7732 with DEFAULT) |
| **Transaction Types (built 2026-11-02, header only; Create PROVEN on ETIA-TEST 2026-11-02, without a payment term)** | **reference data set** (`setIdSetsLOV`) [F]; payment term (name + set together) [F]: a row on the Receivables Payment Terms tab (registry `depends_on` on Name; the type waits and is not sent if the term failed or was skipped) or already in Oracle (read from the Receivables payment terms data file), else red; not in v1: rule set, legal entity, related types (credit memo / subsequent), BU + ledger + account segments (left out: they can create GL account combinations) [F] | Receivables Payment Terms (sheet `depends_on`, built) | Transaction Sources (TrxTypeName + InvTrxTypeSetCode: not wired yet; needs `depends_on` as a list, a shared-code addition) [F]; Receivables System Options [F] | v1 header only; only Invoice and Debit Memo; CreationSign P and DefaultStatus OP only [F] |
| Receipt Sources (plan 4, to build) | **Receivables business unit** [F]; receipt method + class, bank account (conditional) [F] | Business Units (sheet, OM side: cross-area dependency, to confirm); Receipt Classes and Methods when built | Receivables System Options? (to confirm) | FSCR release 26.07 |
| Receipt Classes and Methods (plan 5, to build) | **receipt class** for every child [F]; bank account, BU, accounting, payment system (conditional) [F] | Business Units (BU) | Receipt Sources (lockbox / method) [F]; Receivables System Options (BA/CC receipt methods) [F] | bank setup is pod-shared |
| Remit-to Addresses (plan 6, to build) | **reference data set**, **postal location**, **receipt-from country** [F] | none | customers' invoices (coverage) [J] | affects other users of the pod |
| AutoAccounting Rules (skipped: 27.01) | **Receivables BU**, **account type**, **chart of accounts** [F] | Business Units | transaction accounting [J] | BU-wide |
| Receivables System Options (skipped: BU-wide) | **BU**, **ledger** [F]; grouping rule, rule sets, receipt methods, sources, types, activities, accounts [F] | almost every Receivables module | Payment Terms' partial-discount option [F] | build last, if ever |
| Line Ordering Rules (no module) | to confirm | n/a | Grouping Rules (LineOrderingRuleName, optional) [F] | needed before Grouping Rules can offer that column |

Cross-area links to raise [J]:
- Receipt Sources and Receipt Classes need a business unit; Business Units lives on the Order Management side. With
  one workbook for all areas, the `depends_on` link should work across areas (to confirm in the page code: today
  `depends_on` is used only inside Order Management).
- Customers (OM side) will later need Receivables payment terms, grouping rules and profiles on their accounts (to
  confirm).
