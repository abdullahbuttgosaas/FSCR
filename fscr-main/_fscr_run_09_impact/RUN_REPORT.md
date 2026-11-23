# FSCR Run 09: impact analysis of a change (read only)

Pod **ETIA-TEST** (26.10), 2026-11-04. Read only: **nothing was written, patched or deleted in Oracle.** The only Oracle records this run caused are 8 export-process records, created by FSCR's task-level export, which is a read route. No write was needed, so no stop was required.
Labels: **V** = verified (seen in Oracle or the repo in this run); **NV** = not verified.
Cases: (1) payment term **FSCRT_2P10N30F1**; (2) order-type lookup code **FSCRT_SO_TRAIL_DEALER_F01** (in ORA_DOO_ORDER_TYPES); (3) business unit **FSCRT_Brindle Harbor Marine Supply F01** (ID 300000394664009).
Not counted as findings, as instructed: the 184-BU count and FSCRT_CAMPING_F08.

## FSCR's dependency map: your belief is correct, with one correction
- **Only one map exists:** `knowledge/dependency-graphs/hcm-dependency-graph.json`. It has 86 nodes, all `hcm.*`, and 281 edges. **V**
- **None of this run's 3 tasks is in it.** It contains 0 mentions of AR_MANAGE_RECEIVABLES_PAYMENT_TERMS, FUN_MANAGE_BUSINESS_UNIT or DOO_MANAGE_ORCHESTRATION_LOOKUPS. **V**
- **Correction:** even for HR it is a **setup-order map** ("do task A before task B", used by `task-dependency-resolver`). It is not a record map, so it cannot answer "which records use this record". **V**
- **The three skills' rule files list only *upstream* needs**, meaning what the record itself needs before it can be created or changed:
  - Payment terms (`ora_dependency_readiness.md`): set, existing term, billing cycle, system options, Task Hook. **V**
  - Business units: advice text such as "assess Expenses, Projects… impacts" and "record … downstream functions … affected" (`manage-business-unit.md:59`, `manage-business-unit-set-assignment.md:56`). This is a checklist to think about, with no reader behind it. **V**
  - Order lookups (`manage-order-lookups/SKILL.md`, `core/.../lookups`): nothing about usage. **V**
- **No FSCR skill or script finds the *downstream* records** (what uses a given record). **V**

## Case 1: payment term FSCRT_2P10N30F1 (end date or terms change)

| What was checked | Result | Label |
|---|---|---|
| The term itself (FSCR export) | Set ENTERPRISE, 2026-11-03 to 2028-12-31, 1 line, 1 discount, 1 translation | V |
| Oracle's own "In use" flag on the term (FSCR export) | **N** (FSCRT_D25B75AF1 is also N) | V (what Oracle counts as "in use" was not checked: NV) |
| Customer profile classes (FSCR export, 5 classes, column StandardTermName) | 0 use it (they use ORA_HES, 001 PT, Ahsan PT or blank) | V |
| Transaction types (FSCR export, 25 rows, DefaultTermName) | 0 use it (5 types have some default term, none FSCRT) | V |
| Transaction sources (FSCR export, 6 rows) | 0 references | V |
| Receivables system options (FSCR export, 19 rows) | 0 references | V |
| Invoices (REST) | 3 invoices visible to this user; all use "30 Net" or "custom pt"; 0 use the FSCRT term | V (only the invoices visible to Configuration.TEST) |
| Invoices of the 4 FSCRT accounts and source FSCRT_TS1 (REST finder) | 0 invoices | V |
| Sales orders (REST) | 0 orders visible to this user in total | V (whether hidden orders exist: NV) |
| FSCRT customer accounts, sites and site uses (FSCR customer reader) | No payment-term field in the account, site or site-use data returned | V |
| Customer profiles of the 4 FSCRT accounts | **Could not check.** FSCR's reader returned only "CUSTOMER_SOAP_HTTP_500". My SOAP reader failed 3 times on DNS ("getaddrinfo failed"), so nothing was sent. Run 02 recorded "record … doesn't exist" (no profile). | NV in this run |
| Which BUs can pick the term (set ENTERPRISE) | 15 of 178 active BUs have ENTERPRISE for AR_PAYMENT_TERMS: 3 by an explicit assignment row, 12 by default set with no row. This includes both FSCRT BUs. | Data V; "these 15 can select it" is Oracle's set rule, NV on the pod |

**Ripple list (practice lead):**
- Ending or changing FSCRT_2P10N30F1 affects **no transaction, profile class, transaction type or source that this user can see** (V).
- The term stops being selectable for the BUs that use set ENTERPRISE, including both FSCRT BUs (NV: Oracle rule, not tested).
- **Unknown:** customer profiles (read failed this run), orders and invoices the user cannot see, and anything outside the 4 exported Receivables tasks.

## Case 2: lookup code FSCRT_SO_TRAIL_DEALER_F01 (order type)

| What was checked | Result | Label |
|---|---|---|
| The code itself (FSCR export + REST) | Enabled Y, end date 2027-10-31, meaning "FSCRT_Trail Dealer Replenishment F01" | V |
| Sales orders with this order type (REST, TransactionTypeCode) | 0 (and 0 orders visible in total) | V (visible orders only) |
| Every row of the 8 fresh FSCR exports (21 CSV files, 20,105 rows) | 0 references outside its own lookup row | V |
| Other OM users of an order type (orchestration process assignment, pricing segments and strategy rules, approval rules, transaction-type mapping) | **Not checked.** None of these was exported here, and I used no reader for them. | NV |
| Value sets or flexfields pointing at ORA_DOO_ORDER_TYPES | Not checked (no reader used) | NV |

**Ripple list:**
- Disabling or end-dating this order type affects **0 orders that this user can see** and **0 setup rows in the 8 exported tasks** (V).
- ORA_DOO_ORDER_TYPES is a standard (global) lookup, so a change applies to every BU (repo: standard-lookup route, V; pod behaviour NV).
- **Unknown:** OM orchestration, pricing and approval rules that may name the order type.

## Case 3: business unit FSCRT_Brindle Harbor Marine Supply F01

| Link | Found | Label |
|---|---|---|
| Ledger, legal entity | **None** (blank) | V |
| Location | LHR_WH (location set COMMON) | V |
| Manager | Yaqub, Younas | V |
| Default reference set | ENTERPRISE | V |
| Business functions (FUN_BU_USAGE, 1,075 rows) | **0** | V |
| Service-provider relationships (267 rows) | **0** | V |
| Explicit set assignments (FSCR export, 8,431 rows; REST setIdAssignmentsBusinessUnit) | **0**, so every reference group falls back to ENTERPRISE | Count V; fallback is Oracle's rule, NV |
| **Price lists** (REST, BusinessUnitId) | **1:** FSCRT_Brindle Harbor Dock Equipment EUR F01 (Approved) | V |
| **User data access** (REST dataSecurities) | **1:** Configuration.TEST, Pricing Administrator, active | V |
| Receivables system options (19 rows), transaction-type BU rows | 0 | V |
| Invoices / sales orders (REST) | 0 (3 invoices visible, all BU "BUU1"; 0 orders visible; 0 by BU or requesting BU) | V (visible only) |
| Payment terms | No direct link. Linked only through set ENTERPRISE (both FSCRT terms are in ENTERPRISE) | V for the data; visibility NV |
| Customers | No direct BU link in the account data read. Kestrel's site is in set ENTERPRISE, Pemberton's in CUSTOMER_RDS | V |
| Order types | No BU link (global standard lookup) | V (repo/route); NV on pod |
| Other modules (procurement, payables, projects, inventory, HCM assignments) | Not checked | NV |

**Ripple list:**
- Changing or inactivating this BU directly affects **1 price list** (FSCRT_Brindle Harbor Dock Equipment EUR F01) and **1 data-access grant** (Configuration.TEST, Pricing Administrator) (V).
- It has **no ledger, legal entity, business functions, service providers or explicit set assignments**, so nothing hangs off it there (V).
- Changing its default set (ENTERPRISE) changes which payment terms and customer sites it sees: both FSCRT terms and Kestrel's site are in ENTERPRISE (data V; Oracle effect NV).
- **Unknown:** modules not read (procurement, payables, projects, inventory, HCM).

## What FSCR did and what I wrote
- **FSCR (unmodified):**
  - task-level export of 8 tasks;
  - customer reader `customer_soap_read` (accounts OK; profiles HTTP 500);
  - the repo files read for the dependency question.
- **Me:**
  - choosing what to read;
  - all REST reads;
  - the reference scan across exports;
  - the set-visibility count;
  - the ripple lists.

**FSCR has no step for downstream impact.**

**Scripts:**
- **New (4):**
  - `impact_reads.sh`: REST GET list, 3 passes;
  - `impact_reads_pass2.sh` and `impact_reads_pass3.sh`: generated subsets of the same file;
  - `ref_scan.py`: scans every export cell for the 3 targets;
  - the inline analysis in `evidence/set_and_bu_facts.txt` was a one-off command, not a saved script.
- **Reused from Run 08, paths only:**
  - `rget.py`, `export_all.sh`, `fscr_cust_read2.py`, `soap_read.py`, `transcript_tokens.py`;
  - `diff_exports.py` and `fetch_export_result.py` were copied but not used.
- `bestart_compare.py` was **not reused**, because this run compares references, not expected vs actual.
- Run 08's saved exports were not reused, because fresh exports were taken.

## Problems (classified)
| # | Class | What | Outcome |
|---|---|---|---|
| 1 | Fusion API (input) | 3 REST filters rejected (HTTP 400): PaymentTerms/BusinessUnit not queryable on invoices and orders; the invoice finder needs a customer, source or date | Read all 3 visible invoices instead; checked orders by type, BU and total |
| 2 | Hidden error | FSCR profile reader: first "PROFILE_ACCOUNT_NUMBER_REQUIRED", then "CUSTOMER_SOAP_HTTP_500" | Reported; cause hidden by FSCR |
| 3 | Transport | My SOAP profile read: DNS "getaddrinfo failed" 3 times (nothing sent) | Stopped; profiles listed as not checked |

## Checks
- **Original repo and folders Run 01–08** (including `_fscr_run_07_inventory`, found at the start): hash-identical before and after. **V**
- **Sign-in:** none needed. FSCR's cached token was valid; port 8765 was never used. **V**
- **Processes:** no Python or curl process left; nothing listening on 8765. Your page was not running and was not started. **V**
- **No secrets:** no token printed or saved. Nothing named Corsair, Intel, AMD or NVIDIA was created or sent (the payloads hold only Run 02's read requests for FSCRT accounts). **V**

## Time and tokens
- **Time (no sign-in this run):** request at 15:00:00; work from 15:00:47 to the end of Oracle reads at 15:10:23; report finished at **15:11:51** (about 12 min from the request, no sign-in).
  - 8 FSCR exports: 15:05:31–15:06:49;
  - REST reads: 15:05:43–15:07:12, plus later passes to about 15:09.
- **Model calls and output tokens** (exact, from the session transcript, counted by message ID from the Run 09 request): **41 model calls; output 36,479 tokens; total 10,426,441 (input + output + cache), from the request at 15:00:00 through this measuring call at 15:11:51. Not included: the 2 calls after it (the wrap-up and the chat summary), which cannot measure themselves.**
