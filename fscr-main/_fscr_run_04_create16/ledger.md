# Run 04 ledger: FSCR's 16 "full create set" skills on ETIA-TEST

Start 2026-11-03 08:50:44 +05:00. All times are local (+05:00). If context runs out, resume from this file.

## Setup (08:50–08:55)
- **Checks:** Run 01, Run 02 and the original repo verified unchanged against their recorded hashes. Run 03 hashed at start (`run03_hashes_start.md5`, 6,318 files).
- **Working copy:** `fscr-work4` = a copy of the original repo `fscr-main/fscr-main` (includes the locally patched PT script; not used here), plus the Run 01 project `fscrt-run01-om-setup`.
- **Usage at start** (`get_usage`): context 643,704 (64%); 5-hour 45%; weekly 34%. Context size, not billed tokens.
- **Token:** valid (3,267 s). Port 8765 free.

## Decisions
- **D1: new FSCR project `fscrt-run04-create16` ("FSCRT Run04 Create16"), created with FSCR's initializer, plan generator and `runbook_rest.py create-runbook`.**
  - **Why:** FSCR's Task Hook only accepts tasks in the project's generated Run Book. Run 01's Run Book has 5 other tasks, and editing that existing Oracle record is not allowed. A new project creates a **new Oracle Run Book** (allowed: a new record with an FSCRT name).
  - **Oracle Run Book:** WorkerJourneyId **300000394655024**, 15 tasks, created 08:54:54.
  - FSCR stamped runID=300000394655024 into `fscr-work4/core/data-loader/config/env.properties` (inside the new folder).
  - Imports will update this new Run Book's task status. That is standard FSCR behavior on a record this run created, so no deviation.
- **D2: creation order (worked out; FSCR's resolver is broken, Run 01 F4):**
  1. Payables Calendars
  2. Payables Payment Terms
  3. Bank Charges
  4. Common Options
  5. Invoice Options
  6. Payment Options
  7. Conversion Rates and Policies
  8. AutoInvoice Grouping Rules
  9. Remit-to Addresses
  10. Receipt Classes and Methods
  11. Transaction Types
  12. AutoAccounting Rules
  13. Transaction Sources
  14. Receipt Sources
  15. Receivables System Options

  Skill 1 of the 16 (Receivables Payment Terms) is counted from Run 01 and not repeated.
- **D3: exports.** A template and a data export per skill (30 export processes) through FSCR's task-level export, with output in `evidence/exports/<TASK>/`, outside the project, so no token-log append.

## Skill log

### S2 Payables Calendars (AP_MANAGE_PAYABLES_CALENDARS), built 26.10 = pod, 08:55–09:00: WORKS UNMODIFIED (verified)
- **Route:** the skill's own `fsm_task_adapter.py` + `e2e-adapter.json` (unchanged): manifest ×2, normalize, build, validate → `core.data-loader` preflight → Task Hook data-load plan, then my rule results → preview/approve/verify → approved upload → status → fresh export → adapter `reconcile`.
- **Record:** calendar FSCRT_CAL1, GENERAL, monthly MMM from 2027-01-01, generatePeriods → 12 periods Jan-27..Dec-27.
- **Errors:** my first design put key fields inside `values`: "Operation cal1 cannot change key/audit fields: ['CalendarName', 'CalendarType']" (my input error; retried once with the keys only in targetKey).
- **Rule checks** (3 resources, each evaluated; evidence in `runs/cal/rule-results.json`): CALENDAR.VALIDATE_INPUT valid; ENFORCE_DESIGN ready; EXECUTION_GATE approved_preview.
- **Gates:**
  - Data Loader preflight: "Reply with an approval to upload and initiate this exact validated load." Covered by your approval.
  - Task Hook approve: covered by your approval.
- **Oracle:** exports 100004733446510 (template) and 100004733446521 (data); UCM UCMFA04524519, request **4432126**, ESS 4432128, FSM 100004733447138: Succeeded, 2 objects, 0 failed. After-export 100004733440885.
- **Read-back:** adapter reconcile **PASS**. Diff baseline → after: +1 calendar (FSCRT_CAL1), +12 periods, 0 changed, 0 removed.
- **Patches:** none. Retries: 1 (my design input). Tool calls: about 8.

### S3 Payables Payment Terms (AP_MANAGE_PAYMENT_TERMS), built 26.10 = pod, 09:00–09:07: WORKS WITH A PATCH (small: 1 line, reconcile only; verified)
- **Route:** adapter (unchanged) offline steps PASS → FSCR `resolve_reference_prerequisites.py` (declared read-only SetCode check: PASS, satisfied 1) → Data Loader preflight → Task Hook (6 rule files: 5 passed, `ora_defaulting_rules.md` not_applicable because EnabledFlag, Type and StartDateActive were supplied) → upload → status → export → reconcile.
- **Record:** FSCRT_AP_N45 (net 45, 100% in 45 days, STD, start 2026-11-03, set ENTERPRISE, US translation).
- **Oracle:** exports 100004733447113 (template) and 100004733440852 (data); UCM UCMFA04524532, request **4432147**, ESS 4432148, FSM 100004733447158: Succeeded, 3 objects, 0 failed. After-export 100004733440909.
- **Errors:**
  - FSCR's export poll could not download the completed export ("Failed calling …SetupTaskCSVExportProcessResult…"). Fetched the existing process file with FSCR's own engine (`fetch_export_result.py`); no second export.
  - Unpatched reconcile: **status FAIL, mismatchCount 1 of 17**. REQ-004 "Persist AP_TERM_HEADER.StartDateActive=2026-11-03" with persisted "2026/11/03". This is a false mismatch: the export returns YYYY/MM/DD and the comparison is plain text.
- **Patch** (`patches/ap-payment-terms/fsm_task_adapter.py`, `patch.diff`): line 1475, the value comparison also accepts `persisted.replace("/", "-") == requested`. 1 line; size **small** (one comparison in the verification step; create path untouched). Patched reconcile: **PASS, 0 of 17**.
- **Read-back:** diff baseline → after: +1 header, +1 line, +1 subscription, +1 translation; 0 changed, 0 removed.
- **Retries:** 0 on Oracle. Tool calls: about 12.

### S4 Bank Charges (ORA_AP_MANAGE_BANK_CHARGES), built 26.10 = pod, 09:05–09:08: BLOCKED (FSCR adapter blocked; no safe FSCRT target)
- **FSCR's own adapter declares itself blocked:** `generation.readiness: blocked`, with blockers "ORA_AP_BANK_CHARGE has no configured local row-index fields." and the same for ORA_AP_BANK_CHARGE_LINE. 6 of 8 capabilities are `blocked` (determinism, packageBuild, prerequisiteChecks, promptNormalization, reconciliation, semanticValidation).
- **Approach 1, adapter as written** (offline; exports 100004733447147 template and 100004733448016 data, 0 existing charges): manifest COMPLETED; **normalize FAIL: "Operation b1 targetKey must contain exactly []."** The adapter cannot express any create.
- **Approach 2, `prepare_charge_group_create.py`** (offline source preparation, a second FSCR script): **not sent to Oracle.**
  - A bank charge has no name or code. Its identity is legal entity + currency + settlement priority + bank/branch options, so it cannot carry an FSCRT_ prefix.
  - Any create would apply charges to existing legal entities, banks or payments ("All banks"), which changes behavior for existing records. **Blocked: missing safe target** (worked out).
- **Oracle:** 2 exports only. Nothing imported.

### S8 AutoInvoice Grouping Rules (AR_MANAGE_AUTOINVOICE_GROUPING_RULES), built 26.10 = pod, 09:08–09:12: WORKS UNMODIFIED (verified)
- **Route:** adapter (unchanged) PASS → DL preflight → Task Hook (4 rule files, all passed with evidence) → upload → status → export → reconcile.
- **Record:** grouping rule FSCRT_GRP1 (start 2026-11-03), transaction class I.
- **Oracle:** UCM UCMFA04524545, request **4432170**, ESS 4432172, FSM 100004733446737: Succeeded, 3 objects, 0 failed. After-export 100004734412743.
- **Read-back:** reconcile **PASS**. Diff: +1 rule, +1 class row; 0 changed, 0 removed.
- **Patches:** none. Errors: none. Tool calls: about 5.

### S9 Remit-to Addresses (AR_MANAGE_REMIT_TO_ADDRESSES), built 26.10 = pod, 09:12–09:17: BLOCKED (FSCR's own conditional blocker, after a patch)
- **Design:** one remit-to location in set ENTERPRISE (FSCRT_1 Remit Way, Boston MA 02110 US, short description FSCRT_RMT1) and **no receipt-from criteria** (decision: criteria for a country or state would change remit-to selection for existing customers).
- **Approach 1, unmodified adapter:** manifest FAIL "Base URL must be the credential-free HTTPS root of the selected environment."
  - Line 1773 requires the first host label to equal the environment name (`etia-test`). This pod's host is `fa-etia-test-saasfaprod1.fa.ocs.oraclecloud.com`, so the check can never pass here.
  - Only this one of the 16 adapters has the check.
- **Patch 1** (`patches/remit-to/fsm_task_adapter.py`, `patch.diff`): line 1773 accepts a host *containing* the environment name. 1 line, small. The helper `remit_identity.py` was copied unchanged next to it (imported by the adapter).
- **After patch 1:** manifest COMPLETED ×2; normalize FAIL "Operation r1 targetKey must contain exactly ['SetCode', 'TerritoryCode', 'Address1', 'OrigSystemReference', 'PostalCode', 'State', 'City']".
  - **FSCR contradiction:** `ora_defaulting_rules.md:15` says OrigSystemReference is service-derived on create: "Do not synthesize a customer ID or require an invented value". The adapter requires it as a key; SKILL.md:359 requires it non-empty; `references/release-scope-and-coverage.md` marks its identity handling **Blocked**.
- **Approach 2,** blank OrigSystemReference (per the defaulting rule): normalize FAIL "**Operation r1 creates conditionally blocked key field AR_REMIT_TO_LOCATION.SetCode: Target access policy and optional supported public preflight are not yet reviewed.**"
- **Approach 3** would mean removing FSCR's conditional blocker. **Not done:** that skips an FSCR safety check, which your rules forbid.
- **Oracle:** exports only. Nothing imported.

### S10 Receipt Classes and Methods (AR_MANAGE_RECEIPT_CLASSES_AND_METHODS), **built 26.07 ≠ pod 26.10**, 09:17–09:21: FAILED (release drift meets an FSCR safety rule)
- **Design:** manual receipt class FSCRT_RC1 (no confirm, clear or remit) + receipt method FSCRT_RM1 (start 2026-11-03, payment type NONE). No remittance bank account, which would need an existing BU's bank account.
- **Approach 1, unmodified:** manifest FAIL "**Build template node sequence for AR_RECEIPT_CLASS is '2', expected canonical value '1'.**"
  - The 26.07-built descriptor pins node sequences CLASS 1, METHOD 2, ACCOUNT 3, CC_ERROR 4.
  - This pod's template (100004733447126) declares CC_ERROR_MAPPINGS 1, CLASS 2, METHOD 3, ACCOUNT 4.
- **Approach 2, patched descriptor copy** (`patches/receipt-classes/e2e-adapter.json`, `patch.diff`): 4 nodeSequence values set to the pod's (lines 227, 1005, 1884, 2120); adapter code unchanged. Size: small (4 values).
  - Result: manifest FAIL "**Relationship 3 violates package dependency order: AR_RECEIPT_METHOD must precede AR_CC_ERROR_MAPPINGS.**"
  - The pod's own template orders a child (credit-card error mappings, child of the receipt method) before its parent, which FSCR's parent-first dependency rule rejects.
- **Approach 3** would mean disabling FSCR's dependency-order check. **Not done:** it is an FSCR safety check (import order), which your rules forbid.
- **Oracle:** exports 100004733447126 (template) and 100004733439934 (data). Nothing imported.

### Usage after the first batch of skills (09:11, `get_usage`)
- Context 779,954 (78%); 5-hour 70%; weekly 38%. Context size, not billed tokens.

### S5 Common Options, S6 Invoice Options, S7 Payment Options, S13 AutoAccounting, S15 Receipt Sources, S16 Receivables System Options: BLOCKED (missing safe target), 09:11–09:13
- **S5, S6, S7:** every existing row is ledger-scoped. Data exports AP_FINANCIAL_SYS_PARAM (S5) and AP_SYSTEM_PARAMETER (S6, S7) each hold **18 rows, all 18 with SOBName (ledger)**. These are one row per Payables BU and ledger.
  - The only BUs I may touch, FSCRT_Quillon and FSCRT_Brindle, have **no ledger, no legal entity and no business functions** (Run 02 verified).
  - Every other BU is an existing record whose options must not be changed. Blocked; not attempted in Oracle.
  - FSCR-stated: Invoice Options needs one active exact BU (`ora_dependency_readiness.md`); Payment Options delegates to the Invoice Options AP_SYSTEM_PARAMETER contract. Ledger dependency: worked out from the export (18/18).
- **S16 Receivables System Options:** FSCR-stated "Business unit and ledger: Resolve one business unit and one ledger". The export AR_SYSTEM_OPTIONS has 19 rows, all with LedgerName. FSCRT BUs have no ledger. Blocked.
- **S13 AutoAccounting** (built 27.01 ≠ pod): per BU (AR_AUTO_ACCOUNTING 83 rows, BuName), with account segments from the BU's ledger chart of accounts (ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT, 395 rows). FSCRT BUs have no ledger or chart of accounts. Existing BUs' rules must not be changed (one rule per BU and account type). Blocked.
- **S15 Receipt Sources** (built 26.07 ≠ pod): FSCR-stated "Receivables business unit: Resolve one exact BUName" and a receipt class/method. FSCRT BUs have no Receivables function or ledger, and S10 could not create a receipt class/method. Blocked.
- None of these six was imported. Their exports are the only Oracle activity.

### S12 Transaction Types (AR_MANAGE_TRANSACTION_TYPES), built 26.10 = pod, ~09:13–09:20: WORKS UNMODIFIED after a design correction (FSCR gap; verified)
- **Approach 1** (adapter unchanged, 5 rule files: 4 passed, defaulting not_applicable): FSCRT_TT1, set ENTERPRISE, INV, start 2026-11-03, PostToGl N, no accounting child.
  - Offline PASS; DL and Task Hook OK. Import request **4432190** (UCMFA04524554, ESS 4432191): **Failed, 2 objects, 0 loaded**.
  - Oracle: "**JBO-27014: Attribute CreationSign in TransactionTypeEO__DefCustomizer__ is required.**" Nothing created (after-export 100004733446782: 24 → 24 types).
  - That attempt's reconcile also errored: "Metadata node sequence for AR_TRANSACTION_TYPE is '2', expected '1' from e2e-adapter.json." The export object order varies between exports.
- **FSCR gap:** the adapter and rules accepted an invoice type without CreationSign, which Oracle requires.
- **Approach 2,** design correction with no code patch: CreationSign P (used by 7 of 15 existing INV types). New candidate, new Task Hook files (`runs/ttype2`), DL approval.
  - Import request **4432197** (UCMFA04524562): **Succeeded, 2/2, 0 failed**. After-export 100004733440989: reconcile **PASS**.
  - Diff: +1 type (FSCRT_TT1), 0 changed.
- **Patches:** none. Tool calls: about 9.

### S14 Transaction Sources (AR_MANAGE_TRANSACTION_SOURCES), built 26.10 = pod, ~09:15–09:22: WORKS UNMODIFIED (verified; 3 input corrections from the adapter)
- **Adapter feedback before success** (my input, no code patch):
  1. "Operation s1 cannot target 'AR_BATCH_SOURCE' for create; … classifies it as a package dependency or reconciliation target, not an implementor target." Used ORA_AR_TXN_BATCH_SOURCE instead.
  2. "Operation s1 has no source-backed create contract for fields: ['InvTrxTypeSetCode', 'TrxTypeName']." So a standard transaction type cannot be linked on create, although `ora_dependency_readiness.md` lists that dependency. Dropped it.
  3. "Operation s1 requires LastBatchNum to be at least 1 when automatic numbering is Y for MTS create." Set to 1.
- **Record:** manual source FSCRT_TS1, set ENTERPRISE, start 2026-11-03, auto numbering. FSCR default InvalidLinesRule=Reject applied.
- **Rule files:** 6 (5 passed, reference lookups not_applicable).
- **Oracle:** UCMFA04524565, request **4432203**: Succeeded 2/2, 0 failed. After-export 100004733441000: reconcile **PASS**.
  - Diff: AR_BATCH_SOURCE +1 (FSCRT_TS1), 0 changed. The created row is exported under AR_BATCH_SOURCE, not under the create entity.
- **Patches:** none. Tool calls: about 8.

### S11 Conversion Rates and Policies (EXM_MANAGE_CONVERSION_RATES_AND_POLICIES), **built 27.01 ≠ pod 26.10**, ~09:22–09:25: BLOCKED (FSCR's own conditional blocker)
- **Design:** one EXM_EXCHANGE_RATE_OPTION row for FSCRT_Quillon Ridge Outfitters West F01 (a BU this run may touch; the export has no ledger column): Corporate rate type, warning 5, error 10.
- **Unmodified adapter:** manifest COMPLETED ×2; normalize FAIL "**Operation x1 creates conditionally blocked key field EXM_EXCHANGE_RATE_OPTION.BuName: Require fresh complete exact destination reference evidence bound to the candidate; Oracle error wording is not a prerequisite.**"
- **The skill's `validate_references.py`** is a library ("checks supplied provenance; it cannot establish that a GET occurred") that wants evidence bound to the **candidate SHA-256**. The adapter blocks at normalize, before any candidate exists. The design is circular unless the blocker is removed, which would skip an FSCR safety check. Not done. Nothing imported.

### Repo test files (task 4)
- **Among the 16 skills,** only Conversion Rates has test files: `e2e-test-catalog.json` (24 cases, 93 variants) and `references/create-test-lifecycle.md`.
  - The catalog is a **specification, not executable**: 0 variants carry a command; each lists automation blockers ("Requires agent-assisted execution through the Implementation Router…"). No script in the repo reads the catalog. **0 tests run.**
- **The other 4 skills with test or fixture files** are outside the 16 (Risk `activate-algorithms` fixture; HCM content-library test-batch runner and schemas; HCM wiki test prompts; HCM performance-template fixtures). They were not run: the HCM runner loads data into Oracle (outside the FSCRT scope) and the rest are data or prompts, not tests.

### Discount basis F (task 5): NOT VERIFIED on the pod
- **Contradiction confirmed in the repo:** `payment_terms_fsm_package.py:81` gives "F": "Lines and tax, excluding freight", while `manage-receivables-payment-terms/e2e-adapter.json:808` gives label "Freight".
- **Pod data cannot settle it:** all 17 stored receivables terms use CalcDiscountOnLinesFlag I (Run 03 export). The discount-basis lookup type was not found through `standardLookups` (searches %DISC% and AR%/RA%).

## End, 09:24 (total about 33 min)
- **Run Book "FSCRT Run04 Create16"** (300000394655024): 15 tasks, 5 completed (FSCR's Data Loader runID updates on this run's own Run Book).
- **Checks:** Runs 01, 02 and 03 and the original repo are hash-identical. No Python process, nothing on port 8765, no stray `E:\e` folder, no token text in the outputs.
- **Usage at end** (`get_usage`): context 820,050 (82%); 5-hour 79%; weekly 39%. Context size, not billed tokens.
- **Totals:** 4 works unmodified (S2, S8, S12, S14), 2 works with a patch (S1 from Run 01, S3), 1 failed (S10), 9 blocked (S4, S9, S11 by FSCR guards; S5, S6, S7, S13, S15, S16 missing safe target).
- **Note:** the per-skill start and end times above are approximate. Several were logged ahead of the real clock; the real span of the whole run is 08:50:44–09:24.
