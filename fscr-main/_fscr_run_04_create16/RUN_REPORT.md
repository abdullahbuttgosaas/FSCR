# FSCR Test 1 (Run 04): do the 16 "full create set" skills really work on ETIA-TEST?

Pod ETIA-TEST, release 11.13.26.10.0. Start 2026-11-03 08:50:44 +05:00 · finish 09:24 +05:00 · **total about 33 min**. Per-skill times in the ledger are approximate: some were logged ahead of the real clock.
**Limits:** one pod, one release, one test record per skill, one user (Configuration.TEST). The "ready" labels quoted below are the FSCR authors' own. All 16 skills are **ERP Financials**.
**Definitions used:**
- **works unmodified:** FSCR's own create route ran end to end with no code or descriptor patch, and the record was read back from Oracle.
- **works with a patch:** the same, but a patched *copy* of an FSCR file was needed (in `patches/`).
- **blocked:** stopped before import by FSCR's own guard or by the lack of a safe target.
- **failed:** stopped by an error that I could not get past without skipping a safety check.

---

## 1. One page for practice leads

| Result | Count | Skills |
|---|---:|---|
| **Works unmodified** (ran end to end, read back) | **4** | Payables Calendars, AutoInvoice Grouping Rules, Transaction Types¹, Transaction Sources² |
| **Works with a patch** | **2** | Receivables Payment Terms (Run 01: order-check patch, medium), Payables Payment Terms (1-line reconcile date fix, small) |
| **Failed** | **1** | Receipt Classes and Methods (26.07 adapter vs 26.10 template order) |
| **Blocked by FSCR's own guard** | **3** | Bank Charges (adapter declares itself blocked; no nameable target), Remit-to Addresses (conditional blocker, after a URL patch), Conversion Rates (conditional blocker) |
| **Blocked: missing safe target** | **6** | Common Options, Invoice Options, Payment Options, AutoAccounting, Receivables System Options, Receipt Sources (each needs a BU with a ledger; the FSCRT BUs have none, and existing BUs are off limits) |

Total: 4 + 2 + 1 + 3 + 6 = **16**.

¹ The first import failed in Oracle: "JBO-27014: Attribute CreationSign … is required." FSCR's rules don't require CreationSign; adding it as input (no patch) succeeded.
² Needed three input corrections that the adapter itself demanded; no patch.

**What it takes to use them:**
- **A Run Book that lists the tasks.** FSCR's Task Hook only accepts tasks in the project's generated Run Book, so every new task set needs a new FSCR project, which creates an Oracle Run Book. This run created "FSCRT Run04 Create16" (300000394655024).
- **An AI agent that evaluates and writes the Task Hook rule results.** FSCR checks their format, not their truth (self-attested; see Run 03 A1).
- **A business unit with a ledger and business functions** for 6 of the 16 skills: Payables options, AutoAccounting, Receivables system options, Receipt sources. A fresh or test pod without such a BU cannot test them safely.
- **Tolerance for release drift.** 6 of 16 adapters were built on another release (26.04, 26.07, 27.01). One failed on that drift here (Receipt Classes). Exports also vary their object order between runs, which broke one reconcile.
- **Knowing which entity to create.** For Transaction Sources the create entity is not the one in the task's main CSV.

---

## 2. Scorecard per skill (all ERP)

| # | Skill | Task code | Built | Pod | Status | Oracle evidence |
|---|---|---|---|---|---|---|
| S1 | Receivables Payment Terms | AR_MANAGE_RECEIVABLES_PAYMENT_TERMS | 26.10 | 26.10 | **Works with a patch** (Run 01; order-check patch of 28 Oct, medium) | Run 01 request 4431298; reconcile verified |
| S2 | Payables Calendars | AP_MANAGE_PAYABLES_CALENDARS | 26.10 | 26.10 | **Works unmodified** | request 4432126, 2/2 objects; reconcile PASS; +1 calendar, +12 periods |
| S3 | Payables Payment Terms | AP_MANAGE_PAYMENT_TERMS | 26.10 | 26.10 | **Works with a patch** (small: 1 line, reconcile only) | request 4432147, 3/3; unpatched reconcile FAIL 1/17 (date format); patched PASS 0/17 |
| S4 | Bank Charges | ORA_AP_MANAGE_BANK_CHARGES | 26.10 | 26.10 | **Blocked** (FSCR adapter `generation.readiness: blocked`; no FSCRT-nameable safe target) | exports only |
| S5 | Common Options | AP_MANAGE_COMMON_OPTIONS_… | 26.10 | 26.10 | **Blocked** (missing safe target) | exports only |
| S6 | Invoice Options | AP_MANAGE_INVOICE_OPTIONS | **27.01** | 26.10 | **Blocked** (missing safe target) | exports only |
| S7 | Payment Options | AP_MANAGE_PAYMENT_OPTIONS | **26.04** | 26.10 | **Blocked** (missing safe target) | exports only |
| S8 | AutoInvoice Grouping Rules | AR_MANAGE_AUTOINVOICE_GROUPING_RULES | 26.10 | 26.10 | **Works unmodified** | request 4432170, 3/3; reconcile PASS |
| S9 | Remit-to Addresses | AR_MANAGE_REMIT_TO_ADDRESSES | 26.10 | 26.10 | **Blocked** (FSCR conditional blocker, after a 1-line patch) | exports only |
| S10 | Receipt Classes and Methods | AR_MANAGE_RECEIPT_CLASSES_AND_METHODS | **26.07** | 26.10 | **Failed** (release drift + FSCR dependency-order rule) | exports only |
| S11 | Conversion Rates and Policies | EXM_MANAGE_CONVERSION_RATES_AND_POLICIES | **27.01** | 26.10 | **Blocked** (FSCR conditional blocker, circular evidence) | exports only |
| S12 | Transaction Types | AR_MANAGE_TRANSACTION_TYPES | 26.10 | 26.10 | **Works unmodified** (after input correction; FSCR gap) | request 4432190 failed (JBO-27014); 4432197 2/2; reconcile PASS |
| S13 | AutoAccounting Rules | AR_MANAGE_AUTOACCOUNTING_RULES | **27.01** | 26.10 | **Blocked** (missing safe target) | exports only |
| S14 | Transaction Sources | AR_MANAGE_TRANSACTION_SOURCES | 26.10 | 26.10 | **Works unmodified** (3 adapter-demanded input corrections) | request 4432203, 2/2; reconcile PASS |
| S15 | Receipt Sources | AR_MANAGE_RECEIPT_SOURCES | **26.07** | 26.10 | **Blocked** (missing safe target; depends on S10) | exports only (template download needed a refetch, not used) |
| S16 | Receivables System Options | AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS | 26.10 | 26.10 | **Blocked** (missing safe target) | exports only |

**Totals:** works unmodified **4**, works with a patch **2**, failed **1**, blocked **9**.

## 3. Every patch and failure

**Patches** (all copies in `patches/`; FSCR files untouched):

| Skill | File | Change | Lines | Size | Why |
|---|---|---|---:|---|---|
| S3 | `patches/ap-payment-terms/fsm_task_adapter.py` | reconcile value check also accepts `persisted.replace("/", "-") == requested` | 1 (line 1475) | small | FSCR's export returns YYYY/MM/DD; the reconcile compared it as text with the requested YYYY-MM-DD, giving a false FAIL (REQ-004) |
| S9 | `patches/remit-to/fsm_task_adapter.py` (+ unchanged `remit_identity.py`) | base-URL check accepts a host *containing* the environment name | 1 (line 1773) | small | the check required the first host label to equal `etia-test`; this pod's host is `fa-etia-test-saasfaprod1…`, so it can never pass |
| S10 | `patches/receipt-classes/e2e-adapter.json` | 4 `nodeSequence` values set to the pod template's order | 4 values | small | the 26.07 descriptor pins an order this pod's template doesn't use; the next FSCR check then failed (below) |

Size basis: number of lines or values changed, and whether the change sits in the create path (none did) or only in a check.

**Failures and stops (exact text):**
- **S2:** my design put keys inside `values`: "Operation cal1 cannot change key/audit fields" (my input; one retry).
- **S3:** export download "Failed calling …SetupTaskCSVExportProcessResult…", recovered with FSCR's own `download_result`. Unpatched reconcile: FAIL, mismatchCount 1 of 17.
- **S4:** "Operation b1 targetKey must contain exactly []." The adapter blockers say both entities have "no configured local row-index fields".
- **S9:**
  - "Base URL must be the credential-free HTTPS root of the selected environment."
  - Then "targetKey must contain exactly […'OrigSystemReference'…]".
  - Then "Operation r1 creates conditionally blocked key field AR_REMIT_TO_LOCATION.SetCode: Target access policy and optional supported public preflight are not yet reviewed."
- **S10:**
  - "Build template node sequence for AR_RECEIPT_CLASS is '2', expected canonical value '1'."
  - After the patch: "Relationship 3 violates package dependency order: AR_RECEIPT_METHOD must precede AR_CC_ERROR_MAPPINGS."
- **S11:** "Operation x1 creates conditionally blocked key field EXM_EXCHANGE_RATE_OPTION.BuName: Require fresh complete exact destination reference evidence bound to the candidate…"
- **S12:**
  - Oracle import 4432190: "JBO-27014: Attribute CreationSign in TransactionTypeEO__DefCustomizer__ is required."
  - That attempt's reconcile: "Metadata node sequence for AR_TRANSACTION_TYPE is '2', expected '1' from e2e-adapter.json." The second export passed, so export object order varies between runs.
- **S14:**
  - "cannot target 'AR_BATCH_SOURCE' for create … not an implementor target"
  - "no source-backed create contract for fields: ['InvTrxTypeSetCode', 'TrxTypeName']"
  - "requires LastBatchNum to be at least 1 when automatic numbering is Y"
- **Not bypassed:** the S9 and S11 conditional blockers and the S10 dependency-order rule are FSCR safety checks. Removing them was the only next step, and your rules forbid it.

## 4. Dependencies and creation order

**Order used** (worked out; FSCR's `task_to_skill_mapping.py` crashes, Run 01 F4):
1. Payables Calendars
2. Payables Payment Terms
3. Bank Charges
4. Common Options
5. Invoice Options
6. Payment Options
7. Conversion Rates
8. AutoInvoice Grouping Rules
9. Remit-to
10. Receipt Classes and Methods
11. Transaction Types
12. AutoAccounting
13. Transaction Sources
14. Receipt Sources
15. Receivables System Options

| Dependency | FSCR-stated (file) | Worked out |
|---|---|---|
| AP payment term → calendar, reference set | yes (`manage-payment-terms/ora_dependency_readiness.md`) | – |
| Invoice Options → one active exact BU, three term names | yes (`manage-invoice-options` dependency file) | the BU must also have a ledger: all 18 AP_SYSTEM_PARAMETER rows carry SOBName |
| Payment Options → Invoice Options AP_SYSTEM_PARAMETER contract | yes | same ledger requirement |
| Common Options → BU | partly | ledger: 18/18 AP_FINANCIAL_SYS_PARAM rows carry SOBName |
| Receivables System Options → BU and ledger | yes ("Resolve one business unit and one ledger") | – |
| AutoAccounting → BU, chart of accounts | BU yes | ledger chart of accounts: segment rows (395) |
| Transaction Sources → set, legal entity, transaction type, grouping rule | yes | the transaction-type link cannot be supplied on create (adapter refusal) |
| Transaction Types → set, legal entity, rule set, payment term, BU+ledger for accounting rows | yes | CreationSign required by Oracle (not FSCR) |
| Receipt Sources → Receivables BU, receipt class/method, bank account | yes | blocked because S10 failed and FSCRT BUs have no Receivables function |
| Receipt Classes/Methods → remittance bank account (optional) | yes | – |
| Conversion Rates → BU, conversion rate type, currency | yes | – |
| Remit-to → reference set, postal destination, receipt-from criteria | yes | receipt-from criteria would change remit-to selection for existing customers (not created) |
| Bank Charges → legal entity, currency, banks/branches | yes | no nameable identity; any create affects existing legal entities or banks |
| All → task in the project's Run Book | yes (Task Hook) | required a new FSCR project and Run Book |

## 5. Permissions and approvals

| Gate | Raised by | What I did |
|---|---|---|
| Run Book creation | FSCR initializer + `runbook_rest.py create-runbook` (automatic after init) | Created a **new** Oracle Run Book "FSCRT Run04 Create16" (300000394655024, 15 tasks). FSCR stamped runID into the run 04 copy only |
| Run Book task status | Data Loader `runID` (standard FSCR behavior) | Not changed from FSCR's default. The new Run Book shows 5 of 15 completed (the 5 imports). Only the Run Book this run created was updated |
| Design confirmation | each adapter / skill | your written approval of the test records |
| Data Loader standalone approval ("Reply with an approval to upload and initiate this exact validated load.") | core.data-loader, 6 times | covered by your approval; each exact candidate preflighted first |
| Task Hook rule results | Task Hook (`data-load` → "checks have not yet run") | for each of 6 imports, ran the rule plan and evaluated every planned rule file against evidence. Statuses: passed, or not_applicable where the node's condition was false. Never passed by default. New files only, in the new project. **No permission stop occurred this run** |
| Task Hook approve | Task Hook | covered by your approval |
| FSCR conditional blockers / safety rules | S9, S10, S11 adapters | **not bypassed**; skills marked blocked or failed |
| Sign-in | – | token valid all run; no login |

## 6. Stats and token proxy

- **Oracle export processes:** 30 initial (template + data × 15), plus 6 after-exports (100004733440885, 100004733440909, 100004734412743, 100004733446782, 100004733440989, 100004733441000). Full list in `evidence/exports/export_all.log` and the ledger.
- **Imports:** 6 requests: 4432126, 4432147, 4432170, 4432190 (failed, 0 created), 4432197, 4432203.
- **Tool calls:** about 110 (approximate).
- **Files:** 4 patches, 9 scripts (adapter driver, live driver, survey, mapping builder, inspector, export wrapper, diff and fetch copies).

| When | Source | Context size | 5-hour window | Weekly |
|---|---|---|---|---|
| Start 08:50 | `get_usage` | 643,704 | 45% | 34% |
| After the first skills, 09:11 | `get_usage` | 779,954 | 70% | 38% |
| End 09:24 | `get_usage` | 820,050 | 79% | 39% |

Context added: about 176,346. That is context-window size, **not billed tokens**. Plan windows are percentages and may include other use on the account.

## 7. Where FSCR's docs or code were wrong

1. **"Full create set / e2e ready":** of 15 skills run here, only 4 created a record without any patch. Bank Charges' own adapter declares itself blocked, and two more adapters block their own create keys (Remit-to SetCode, Conversion Rates BuName).
2. **Release pinning:** 6 of 16 adapters were built on another release. Receipt Classes failed on this pod's template order, and its dependency rule also rejects that order.
3. **Export order varies** between exports of the same task, yet two adapters (S10 build, S12 reconcile) pin node sequences.
4. **Date format:** the AP payment-terms reconcile compares export dates (YYYY/MM/DD) as text with ISO dates, giving a false FAIL.
5. **Remit-to:** the hostname check assumes `<env>.…`; and an OrigSystemReference contradiction (required key vs "do not … require an invented value"), which FSCR's own coverage file marks Blocked.
6. **Transaction Types:** CreationSign is not required by FSCR but is required by Oracle.
7. **Transaction Sources:** the create entity is not AR_BATCH_SOURCE, and a dependency FSCR lists (standard transaction type) has no create contract.
8. **Tests:** the "test files" are a specification catalog with no runner (0 executable variants among 93).
9. **Discount basis F:** the repo contradicts itself (`payment_terms_fsm_package.py:81` "Lines and tax, excluding freight" vs `e2e-adapter.json:808` "Freight").
10. **Data Loader** writes status logs outside the repo (`C:\Users\PC\.codex\data-loader-status-logs\`), as in Run 03.

## 8. Discount basis check: NOT VERIFIED on the pod

- The contradiction is confirmed in the repo (section 7, item 9).
- The pod's 17 receivables terms all store CalcDiscountOnLinesFlag **I**, so none uses F.
- The discount-basis lookup type was not reachable through `standardLookups` (searches %DISC%, AR%/RA%).
- Oracle's meaning of F could not be read from this pod.

## 9. Capability matrix

| Capability | Area | Tested | Result | Evidence | Limits |
|---|---|---|---|---|---|
| **Create** | 16 ERP Financials skills | yes (15 live + S1 from Run 01) | 4 unmodified, 2 with a small or medium patch, 1 failed, 9 blocked (3 by FSCR's own guards, 6 for lack of a safe BU) | ledger, `evidence/skills/*` | one record per skill; one pod |
| Understand | – | Run 02 | – | – | – |
| Change | – | Run 03 | – | – | – |
| Plan and advise | dependency order | partly | FSCR states most dependencies; its sequence resolver crashes; order worked out | section 4 | – |
| **Verify** | 6 imports | yes | adapter reconcile PASS on 4 unmodified; 1 false FAIL (date format; patched), 1 reconcile error from varying export order; whole-area diffs (mine) showed only additions | `evidence/skills/*/diff.json`, reconcile reports | FSCR reconcile is per adapter; quality varies |
| **Breadth** | 16 skills, 5 functional areas (Payables, Customer Billing, Customer Payments, Expenses, Receivables) | yes | usable as is: calendars, grouping rules, transaction types and sources; not usable here: anything per-BU without a ledgered safe BU | this report | ERP Financials only |

## 10. Honest assessment

- **Where FSCR helps:** when an adapter is current and the object is set-based or global, the route is solid. It gives a template-preserving build, its own validation, the Data Loader and Task Hook gates, and an offline reconcile. Calendars, grouping rules, transaction types and transaction sources each went from request to verified Oracle record in a few minutes.
- **Where it has holes:**
  - The "e2e ready" labels overstate readiness. Three adapters block their own create.
  - One fails on release drift, and one needed a patch to verify its own import.
  - Oracle rejected one package that FSCR validated (CreationSign).
  - 6 of 16 skills cannot be tested without a business unit that has a ledger and business functions.
- **FSCR versus me:**
  - **FSCR:** the build, validation and reconcile logic, plus the gates.
  - **Me:**
    - every design file (FSCR has no request-to-design step that runs)
    - the creation order and the Task Hook rule evaluation
    - 3 patches, the drivers, the whole-area diffs, and the safe-target analysis
- **Time:** no hand-done baseline was measured, so no speed claim. Observed: about 4–7 minutes per working skill, most of it Oracle import and export time.

---

## Records created in Oracle by this run (all FSCRT-named, plus FSCR process records)

| Record | Type | Skill |
|---|---|---|
| FSCRT_CAL1 + 12 periods (Jan-27..Dec-27) | Payables calendar (GENERAL) | S2 |
| FSCRT_AP_N45 (+ line, ENTERPRISE subscription, US translation) | Payables payment term | S3 |
| FSCRT_GRP1 (+ class I) | AutoInvoice grouping rule | S8 |
| FSCRT_TT1 | Receivables transaction type (ENTERPRISE) | S12 |
| FSCRT_TS1 | Receivables transaction source (ENTERPRISE) | S14 |
| FSCRT Run04 Create16 (300000394655024) | FSCR Run Book (15 tasks, 5 completed) | setup |
| 36 export processes, 6 data-load requests (UCM files, ESS jobs, FSM processes) | Oracle process records | all |

**Nothing outside FSCRT names was created or changed:**
- Each import's whole-area diff showed only the FSCRT additions, with 0 changed and 0 removed rows.
- The failed import 4432190 created nothing (24 → 24 types).
- The blocked and failed skills imported nothing.
- **Local:** Runs 01, 02 and 03 and the original repo are hash-identical to their start states. No process is left running and nothing is listening on port 8765.
