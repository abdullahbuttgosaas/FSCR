# FSCR Test 4 (Run 02): can FSCR read and explain an existing Oracle environment?

Pod ETIA-TEST (release 11.13.26.10.0), read-only. Start 2026-11-03 07:10:16 +05:00 · finish 2026-11-03 07:34:37 +05:00 · total 24 min.
**Limits:** one pod, one release, two FSCRT records per module plus 2–3 pre-existing records per area, one user (Configuration.TEST). Area tags: **ERP** = Financials, **SCM** = Order Management.
**Labels used:** *verified* (checked against Oracle data read in this run), *not verified*, *unclear*.

---

## 1. One-page summary for practice leads

**What FSCR can read, explain and compare here**
- **Three areas read end to end through FSCR's own route,** the setup-task CSV export: business units, payment terms, and lookups including order types. One export per task gives the full configuration, including pre-existing records.
  - This export also shows the **business unit Default Set** (ENTERPRISE for both FSCRT BUs). Run 01 had reported it as unreadable.
- **One real comparison:** for payment terms only, FSCR's offline `reconcile` checked the Run 01 request against a fresh export: "verified", 0 mismatches, 0 external calls.
- **Customer accounts,** including sites and address purposes (bill-to, ship-to), through FSCR's read-only SOAP reader. It returns raw XML and explains nothing.

**What FSCR cannot do**
- **Price lists:** no read route at all. The catalog's only price-list task is "Import Price Lists", which has no export, and the skill is import-only.
- **Person details beyond the account:** no reader. The name prefix (Mr./Ms.) could not be read by any route I tried.
- **Explain anything:** no plain-words output, no linking across areas (price list → BU → set → user access), and no gap finding.
- **Answer a "what is set up?" question:** the router is text only (no script) and has no read intent. FSCR's AGENTS.md rules read-only calls outside a workflow as "not permissible as exploratory shortcuts".
- **Compare two states in general:** FSCR's compare skill uploads both files to Oracle and starts a compare process there, which is a write. I ran it as a dry run only and wrote a local diff instead.
- **Show why a read failed:** FSCR's customer reader hides Oracle's error text, reporting only `CUSTOMER_SOAP_HTTP_500`.

**What I found that FSCR did not**
- **The 4 FSCRT customer accounts have no customer profile.** Oracle says "The record for Account ID … doesn't exist." So they have no profile class, credit settings, collector or payment terms. All 4 pre-existing accounts read have a DEFAULT profile. *(verified)* Run 01 did not catch this.
- **The FSCRT BUs have no primary ledger, no legal entity and no business functions,** although FSCR's own BU guidance says to align a BU to a primary ledger. The pattern is common here: 94 of 183 BUs have no ledger. *(verified)*
- **All 55 price lists return 0 items through REST,** including pre-existing ones. Whether they are really empty or the items are hidden from this user is *unclear*.
- **Everything else matches Run 01's input** for the 24 records. One FSCRT order type, FSCRT_SO_WARRANTY_SWAP_F01, is disabled as requested. *(verified)*

**What I had to write:** 7 small scripts (about 26 KB in total), listed in section 4: a GET-only REST helper, a get/find-only SOAP helper, a wrapper for FSCR's reader, a local export diff, an evidence analyser, a static coverage scan, and wrappers.

**Honest split (definition: who produced the data used for the answer):**
- **By FSCR:** about 45% of the answers' raw data, mainly the 3 exports, the customer-account reads and the payment-term reconcile.
- **By my own calls and code:** about 55%. That covers price lists, data access, persons, profiles, set-ID resolution, every explanation, every cross-area link and every gap finding.
- This split is my estimate from the evidence list in section 2; it is not measured.

---

## 2. Scorecard per area

| # | Area | Tag | FSCR read end to end? | FSCR route used | My own reads | What could not be read (reason) | Answer quality |
|---|---|---|---|---|---|---|---|
| 1 | Business units | ERP | **Partly**: yes for setup values (export); no for user data access | task-level export FUN_MANAGE_BUSINESS_UNIT (process 100004734412462); FSCR-declared GETs finBusinessUnitsLOV, setIdAssignmentsBusinessUnit, ledgersLOV, legalEntitiesLOV | hcmBusinessUnitsLOV, dataSecurities | Reference-group set assignments for FSCRT BUs: 0 rows in setIdAssignmentsBusinessUnit (123 of 183 BUs have rows); the reason is *unclear* | verified |
| 2 | Price lists | SCM | **No** | none (CUSTOM_IMPORT_PRICE_LISTS has CSV export N; the skill is FBDI import only) | priceLists (+accessSets), items child for all 55 | Price-list lines: 0 rows for every list; real or hidden is *unclear* | headers verified; items unclear |
| 3 | Payment terms | ERP | **Yes** | export AR_MANAGE_RECEIVABLES_PAYMENT_TERMS (100004733440719) + FSCR `reconcile` (offline) | paymentTermsLOV | – | verified |
| 4 | Lookup types and codes | SCM | **Yes** (for OM-module lookups) | export DOO_MANAGE_ORCHESTRATION_LOOKUPS (100004733440757) includes both FSCRT types and their 4 codes; FSCR REST client GET (`fr2.sh`) | standardLookups | Which application "ModuleId 61ECAF4A…" denotes is *inferred* (it is the ID that ORA_DOO_ORDER_TYPES also uses) | verified |
| 5 | Order types | SCM | **Yes** | same export + FSCR REST client GET | ORA_DOO_ORDER_TYPES codes | – | verified |
| 6 | Organization customers | ERP | **Partly**: account, site, site uses, account DFF, location yes; customer profile no | manage-customer-uploads `customer_soap_read` (getCustomerAccount, getLocation, getActiveCustomerProfile) | hubOrganizations (DUNS, taxpayer ID, party site), own getActiveCustomerProfile (to see the fault) | FSCRT profiles: none exist (Oracle "record … doesn't exist"); FSCR hides that text | verified |
| 7 | Person customers | ERP | **Partly**: account level only; FSCR has no person-party read | same FSCR reader (account) | hubPersons, contacts, own findPersonProfile | Name prefix: hubPersons has no such field; findPersonProfile failed on DNS 3 times; contacts returns 0 rows for these parties | names, tax ID and accounts verified; prefix **not verified** |
| 8 | Address purposes | ERP | **Yes** (inside getCustomerAccount) | FSCR reader | – | – | verified |

### Each area in plain words (FSCRT records, then pre-existing)

**1. Business units (ERP)**
- **FSCRT_Quillon Ridge Outfitters West F01:** active, Default Set ENTERPRISE, manager Smith, Aron, no location (the input said none).
- **FSCRT_Brindle Harbor Marine Supply F01:** active, Default Set ENTERPRISE, location LHR_WH (Lahore Warehouse, set COMMON), manager Yaqub, Younas.
- Neither FSCRT BU has a primary ledger, a legal entity or any business function.
- User Configuration.TEST holds Pricing Administrator data access on both. You granted it on 2026-11-03, and the rows were created 01:40–01:41 UTC.
- **Pre-existing:**
  - **0012:** set ASCEND_001, ledger GoSaaS MFG US, legal entity Go Venue 02, 1 business function.
  - **01PRC Exam BU:** set COMMON, ledger GoSaaS Labs Ledger, legal entity GoSaaS Inc., 6 functions.
  - **TESTBU4:** set CUSTOMER_RDS, no ledger, no legal entity, no functions. Like the FSCRT BUs.

**2. Price lists (SCM)**
- **FSCRT_Quillon Ridge Wholesale Tents USD F01 (300000394622041):** segment price list for the Quillon BU in USD, from 2026-11-03 with no end, charge "Sale Price", line type Buy, calculation Price, access set ENTERPRISE, **Approved**, 0 lines.
- **FSCRT_Brindle Harbor Dock Equipment EUR F01 (300000394623080):** the same for the Brindle BU in EUR, ending 2027-10-31, **Approved**, 0 lines.
- **Pre-existing:**
  - **Collector Retail USD D01** (Emberlight BU, ENTERPRISE, Approved).
  - **TESTPRICELIST4** (TESTBU4, AFN, no charge definition, Approved).
  - **zz_test_pl_8034_all** (BU ABD): **In progress with no access set**, the only list in the pod in that state.

**3. Payment terms (ERP)**
- **FSCRT_2P10N30F1:** set ENTERPRISE, 2026-11-03 to 2028-12-31, one line of 100% due in 30 days, with a 2% discount if paid within 10 days.
- **FSCRT_D25B75AF1:** set ENTERPRISE, from 2026-11-02 with no end, two lines (25% due in 15 days, 75% due in 60 days), print lead days 1, first-installment option ALLOCATE (tax and freight spread over the installments).
- **Pre-existing:**
  - **30 Net:** COMMON set, 100% due in 30 days.
  - **ORA_HES:** COMMON set, 15 days.
  - **ABC:** set 001 CUSTOMER SITE, 1 day.
- The pod holds 17 terms in total.

**4. Lookup types and codes (SCM)**
- **FSCRT_OUTDOOR_ACTIVITY_F01:** user-level, in the same module as the OM lookups, REST access SECURE (Oracle's default).
  - FSCRT_HIKING: sequence 1, enabled.
  - FSCRT_PADDLING: sequence 2, enabled, description "Kayak and canoe gear", tag "water".
- **FSCRT_CARRIER_SERVICE_TIER_F01:** REST access AUTH.
  - FSCRT_STANDARD: enabled, no sequence.
  - FSCRT_FREIGHT: **disabled**.
- **Pre-existing in the same module:** ORA_DOO_LINE_TYPES (Oracle-owned, codes Buy and Projects), plus TEST LINE TYPES and TEST LINE TYPES 1 (user-level, 1 code each).

**5. Order types (SCM)**
- The lookup ORA_DOO_ORDER_TYPES ("Type of Sales Order") has 60 codes: the 58 that existed before Run 01, all unchanged, plus 2 FSCRT codes.
  - FSCRT_SO_TRAIL_DEALER_F01: enabled.
  - FSCRT_SO_WARRANTY_SWAP_F01: **disabled**.
- **Pre-existing:**
  - **teest:** enabled, but its start and end dates are both 2026-10-20, so it is effectively expired.
  - **Subscription:** enabled.
  - **AMNA_STANDARD_ORDERS:** enabled.

**6. Organization customers (ERP)**
- **FSCRT_Kestrel (account 22050):** class Public Sector Companies, type R, 2026-11-02 to 2028-12-31. One site in set ENTERPRISE, key account, trading partner 5502101, EDI code KBT-EDI-01. Primary bill-to and ship-to. Account notes, shipping instructions and agreement are filled in. The location's extra fields (mineral status, supplier site 4201, contact email and others) are filled in. DUNS 204118306, taxpayer ID 84-2210764.
- **FSCRT_Pemberton (account 22051):** the same pattern, with its site in **CUSTOMER_RDS**.
- **No customer profile on either.**
- **Pre-existing:**
  - **1002 OM_Test_Customer:** site in SET0001, bill-to only, DEFAULT profile with credit checking on and Default Collector.
  - **20008 Apex Wireless:** SET0001, bill-to and ship-to, DEFAULT profile.

**7. Person customers (ERP)**
- **FSCRT_Caspian Reed Thornbury Jr. (account 22052):** taxpayer ID 58-4410237, set ENTERPRISE, bill-to, no end date (4712-12-31).
- **FSCRT_Linnea Voskuijlen (account 22053):** taxpayer ID 63-7702158, class FEDERAL, ship-to, ends 2027-12-31.
- No profile on either, and the prefix is not readable.
- **Pre-existing:** ZZ_TEST_2536 Q Person Jr (account 21264) and ZZ_TEST_9231 Q Tester Jr. (account 21040, site in CUSTOMER_RDS). Both have profiles and both bill-to and ship-to.

**8. Address purposes (ERP)**
- All 6 FSCRT purposes exist, are active and primary, and start on the requested dates: Kestrel bill/ship 2026-11-02, Pemberton bill/ship 2026-11-03, Caspian bill-to, Linnea ship-to.

### B. Across areas: how the records connect

| Link | What Oracle shows | Verified? | Link described in FSCR files? |
|---|---|---|---|
| Price list → BU | Each FSCRT price list's BusinessUnit is its FSCRT BU | verified | **No.** FSCR's pricing files never mention the BU |
| BU → default set | Both FSCRT BUs → ENTERPRISE (export) | verified | Yes (`organization-structures/manage-business-unit-set-assignment.md` and 11 other files) |
| Price list → access set | Both → ENTERPRISE, the same set as the BU's default | verified | Yes (`import-price-lists/SKILL.md`) |
| Price list ↔ user data access | Configuration.TEST holds Pricing Administrator on both FSCRT BUs (`dataSecurities`). Run 01 showed price-list creation fails without it | verified | **No.** Worked out by me |
| Customer → address set | Kestrel, Caspian and Linnea sites → ENTERPRISE (ID 300000000003463); Pemberton → CUSTOMER_RDS (300000334604945) | verified (IDs resolved through setIdAssignmentsBusinessUnit) | Yes (`manage-customer-uploads/assets/customer-contract.json`) |
| Customer → profile → payment terms | **No profile, so no payment terms**, for all 4 FSCRT accounts | verified (absence) | Profile: yes (6 files). Customer → payment term: **no** |
| Order type → lookup | FSCRT codes are codes of ORA_DOO_ORDER_TYPES | verified | Yes (`manage-order-lookups/SKILL.md`) |
| Lookup types → module | Same ModuleId as ORA_DOO_ORDER_TYPES | verified; meaning *inferred* | Partly (ORA_CJM rules say not to hard-code ModuleId) |
| Payment terms → set | Both → ENTERPRISE | verified | Yes (`e2e-adapter.json` and 10 other files) |
| Price list → customer (pricing strategy) | No link exists; none was requested | not verified (not read) | FSCR mentions strategies, not a route |

FSCR supplied none of these joins at run time; every join was done by `analyze.py` or by me.

### C. Missing, inconsistent or incomplete

| # | Finding | Who produced it | Evidence | Quality |
|---|---|---|---|---|
| C1 | FSCRT customer accounts (4) have **no customer profile**, so no payment terms, credit or collector. Run 01's SOAP create made none, and Oracle didn't add one by default | me (FSCR's reader returned only `CUSTOMER_SOAP_HTTP_500`) | `evidence/A6/soap/prof_resp_*.xml` | verified |
| C2 | FSCRT BUs have no primary ledger, legal entity or business functions; FSCR's guidance says to align a BU to a primary ledger (`manage-business-unit.md:56`) | me, from FSCR's export | BU export; `area_facts.json` A1 | verified |
| C3 | Price lists have no lines. Expected for FSCRT ("header only" in the input), but every list in the pod shows 0 through REST | me | `evidence/A2/items_all_summary.json` | FSCRT verified; pod-wide *unclear* |
| C4 | Disabled records: FSCRT_FREIGHT, FSCRT_SO_WARRANTY_SWAP_F01 (both requested); pre-existing ZZ_TEST_7981 is disabled and `teest` has an end date | me, from FSCR's export and REST | `area_facts.json` A4/A5 | verified |
| C5 | Pre-existing zz_test_pl_8034_all is In progress with no access set | me | `priceLists_all.json` | verified |
| C6 | FSCRT payment terms match the Run 01 request exactly | **FSCR** (`reconcile`: verified, 0 mismatches) | `evidence/D/fscr_pt_reconcile_fresh.json` | verified |
| C7 | FSCRT customers, persons, sites, purposes, DFFs and locations show 0 differences from the Run 01 request payloads | me (`analyze.py`) | `area_facts.json` C_customer_diffs | verified |
| C8 | Person prefix (Mr./Ms.) not readable, so input match unknown | me | `evidence/A7/*` | not verified |
| C9 | FSCRT BUs have 0 rows in setIdAssignmentsBusinessUnit (no per-reference-group set rows), while 123 of 183 BUs have rows | me | `evidence/A1/setIdAssignmentsBusinessUnit.json` | verified (count); impact *unclear* |

### D. Compare two states
- **FSCR's general compare** (`shared/baseline-assessment/setup-compare/task-level-compare/compare_setup_task_zips.py`) uploads both ZIPs to Oracle and submits a compare process. The dry run shows: create file blob → upload file blob (×2) → create upload COMPARE_REQUEST. That is a write, so it was **stopped** (`evidence/D/fscr_compare_dryrun.log`).
- **What I used:** FSCR's payment-term `reconcile` (offline) plus my own local CSV diff (`diff_exports.py`).

| Baseline | Fresh export | Result |
|---|---|---|
| PT data export before Run 01 (100004733439686) | 100004733440719 | +2 terms (FSCRT_2P10N30F1, FSCRT_D25B75AF1), +3 lines, +1 discount, +2 translations; **0 changed or removed** |
| PT data export after Run 01 (100004733439700) | 100004733440719 | **no difference** |
| Run 01 PT candidate ZIP | 100004733440719 | FSCR `reconcile`: verified, 0 mismatches |
| Run 01 BU candidate ZIP (no BU data export exists from Run 01) | 100004734412462 | FSCRT rows match; only Oracle-filled fields added (OrganizationCode, effective dates) |
| Run 01 REST read of ORA_DOO_ORDER_TYPES (58 codes) | REST now (60) | +2 FSCRT codes; 58 unchanged |

---

## E. Routing and modes (8 plain questions)

**How FSCR routes:** `router/implementation-router/SKILL.md` → `router/project-objective-classifier/SKILL.md`. Both are text only (no script), written for "implementation objectives", with no read or explain intent. The classifier resolves an offering from the catalog and sets it to *pending* and asks the user when a task belongs to more than one offering. Below is what that text yields when followed literally; it is *not verified* because there is nothing to execute.

| Plain question | Offerings containing the task | Router outcome | Task skill it reaches | Right skill for reading? | Mode |
|---|---|---|---|---|---|
| What is set up for BU FSCRT_Quillon…? | 24 | offering pending, asks | `erp.financials.organization-structures` (manage-business-unit.md) | Partly: guidance and reference GETs; the working read is `shared.setup-export.task-level-export` | assisted (area) / hybrid (export) |
| …for price list FSCRT_Quillon…? | 1 (DOO_ORCHESTRATION) | resolves | `scm.order-management.pricing.import-price-lists` | **No** (FBDI import only) | hybrid |
| …for payment term FSCRT_2P10N30F1? | 6 | pending, asks | `erp.financials.customer-billing.manage-receivables-payment-terms` | Yes (export + reconcile) | assisted |
| …for lookup FSCRT_OUTDOOR_ACTIVITY_F01? | n/a (no OM user-lookup task); FND_MANAGE_STANDARD_LOOKUPS is in 10 offerings, with skills only in HCM | ambiguous | `core.fusion-api.apps-common.lookups` (via manage-order-lookups) | Yes | hybrid |
| …for order type FSCRT_SO_TRAIL_DEALER_F01? | 2 | pending, asks | `scm.order-management.orders.manage-order-lookups` → apps-common lookups | Yes | assisted → hybrid |
| …for customer FSCRT_Kestrel…? | AR_MANAGE_CUSTOMERS: 3, no skill | pending; falls to ORA_AR_MANAGE_CUSTOMER_UPLOADS | `erp.financials.customers.manage-customer-uploads` | Partly (SOAP reader, raw) | assisted |
| …for person customer FSCRT_Caspian…? | same | same | same skill (organization-only contract) | Partly (account only) | assisted |
| …for Kestrel's address purposes? | same | same | same | Yes (inside account read) | assisted |

**How the modes differ for a read-only question** (definitions from `governance/skill-design-standards.md`):
- **Advisory:** guidance only; the person reads Oracle themselves. No live read.
- **Assisted:** generates artifacts for human review. In practice, export ZIPs or XML a person must interpret.
- **Automated:** "performs approved actions directly". None of the 8 area skills is automated, so FSCR offers no automated read for these areas.
- **Hybrid:** automated analysis plus human approval. The export and lookups skills; the only modes that actually call Oracle here.

For a read, all four modes end with a human interpreting raw output; none produces an explanation.

## F. Coverage

| Area | Tag | FSCR read? | Route | Not readable (reason) |
|---|---|---|---|---|
| Business units | ERP | partly | export + LOV GETs | user data access (no FSCR route) |
| Price lists | SCM | no | – | everything via FSCR (no export task, import-only skill) |
| Payment terms | ERP | yes | export + reconcile | – |
| Lookups | SCM | yes | export (OM module) + REST | – |
| Order types | SCM | yes | export + REST | – |
| Org customers | ERP | partly | SOAP reader | profile fault text hidden; party DUNS and tax ID need my hub REST read |
| Person customers | ERP | partly | SOAP reader (account) | person party, prefix |
| Address purposes | ERP | yes | SOAP reader | – |

**10 further tasks (static check only, not run; *not verified* live):**
- All 10 have a FSCR skill and catalog flag CSV export Y, so FSCR's generic task-level export would be the read route.
- None has its own read script, and none explains or compares.

| Task | Area | Skill mode | CSV export (catalog) | Own scripts | Declared REST reads |
|---|---|---|---|---|---|
| INV_MANAGE_INVENTORY_ORGANIZATIONS | SCM Inventory | assisted | Y | 0 | 0 |
| ORA_ADVANCED_INVENTORY_PARAMETERS | SCM Inventory | assisted | Y | 0 | 1 |
| PO_MANAGE_PROCUREMENT_AGENTS | SCM Procurement | assisted | Y | 0 | 0 |
| POZ_CONFIGURE_SUPPLIER_REGISTRATION | SCM Procurement | assisted | Y | 0 | 2 |
| EGP_MANAGE_DEFAULT_CATALOGS | SCM Product Mgmt | assisted | Y | 0 | 1 |
| EGI_MANAGE_CATALOG_MAPPINGS | SCM Product Mgmt | assisted | Y | 0 | 0 |
| ORA_SHIP_CONFIRM_RULES | SCM Shipping | assisted | Y | 0 | 0 |
| ORA_PICK_WAVE_RELEASE_RULES | SCM Shipping | assisted | Y | 0 | 0 |
| PER_MANAGE_DEPARTMENT | HCM | assisted | Y | 0 | 1 |
| ORA_MANAGE_COLLECTIVE_AGGREMENTS | HCM | assisted | Y | 0 | 0 |

---

## 3. Skills used, and skills that did not exist
**Used:**
- `shared/setup-export/task-level-export` (`export_setup_task_csv.py`, 3 exports)
- `pillars/erp/financials/customer-billing/manage-receivables-payment-terms` (`payment_terms_fsm_package.py reconcile`)
- `pillars/erp/financials/customers/manage-customer-uploads` (`customer_soap_read.py`)
- `core/fusion-api/rest-api-client` (`fusion_rest_client.py`, GET)
- `core/auth/fusion-oauth-authentication` (cached token, no login needed)
- `shared/baseline-assessment/setup-compare/task-level-compare` (dry run only)
- Read, not run: router, classifier, organization-structures, import-price-lists, manage-order-lookups, apps-common lookups, governance standards, catalogs.

**Did not exist:**
- A "read or explain environment" skill or router intent.
- A price-list reader or a Manage Price Lists task.
- A person-party reader.
- A customer-profile reader that shows Oracle's error.
- A cross-area link or dependency view at run time. `shared/validation/cross-pillar-dependency-validator`, `configuration-completeness-validator` and `shared/baseline-assessment/environment-comparison` / `configuration-drift-analyzer` exist as 2 KB guidance stubs with 0 scripts.
- An offline general compare.

## 4. Everything I wrote (`_fscr_run_02_understand/scripts`)
| File | Size | Why |
|---|---|---|
| `rget.py` | 2.9 KB | GET-only REST with paging and gzip decoding; refuses any other method |
| `soap_read.py` | 2.1 KB | get/find-only SOAP; needed to see Oracle's fault text that FSCR hides |
| `fscr_cust_read2.py` | 1.5 KB | Calls FSCR's `customer_soap_read.read` from the run 02 copy and saves the output |
| `fr2.sh` | 0.5 KB | FSCR REST client wrapper, GET only, with the Git Bash path fix |
| `diff_exports.py` | 2.7 KB | Local diff of export ZIPs (FSCR's compare is a write) |
| `analyze.py` | 11.6 KB | Per-area facts, cross-area joins, comparison with the Run 01 request |
| `coverage_scan.py` | 4.6 KB | Static scan of 18 skill folders for read routes |

## 5. Failures
| What | Exact text | Handling |
|---|---|---|
| DNS (5 bursts, 07:13–07:30) | `[Errno 11001]` / `[Errno 11002] getaddrinfo failed` | Nothing was sent. Retried at most twice; findPersonProfile stopped after 3 attempts |
| FSCR profile read | `CUSTOMER_SOAP_HTTP_500` | Own read gave `JBO-FND:::FND_CMN_RCRD_MSNG … The record for Account ID 300000394607181 doesn't exist.` (same for 22051–22053) |
| CRM contacts with a field list | `URL request parameter fields with value … is not valid.` (27519) | Re-read without a field list: 0 rows |
| setupTaskCSVExports by ProcessId | `Failed to build ViewCriteria … Unable to create criteria item from node: "ProcessId".` (29140) | Export process IDs taken from FSCR's own log instead |
| REST profile resources | HTTP 404 for receivablesCustomerAccountProfiles, customerProfiles, receivablesCustomerProfiles | none exists; used SOAP |
| My mistakes | Export batch log folder missing (first launch never ran); POSIX `--output-dir` wrote to `E:\e\…`; 2 parsing bugs in `analyze.py` | ZIPs moved into run 02 and the empty `E:\e` folder removed (only my 3 files were in it); bugs fixed |

## 6. Permissions, approvals and sign-ins
- **Sign-in:** none needed. The cached token was valid all run (1,947 s at start).
- **Port 8765:** not used.
- **FSCR gates hit:** none. Exports need no approval in FSCR.
- **Write stop:** FSCR task-level compare (dry run only).
- **FSCR rule tension:** AGENTS.md says read-only requests "must also be selected by the active workflow" and are "not permissible as exploratory shortcuts". This test's own reads were authorised by you, which is outside FSCR's workflow.
- **Tool permission prompts:** none denied.

## 7. Stats and token proxy
- **Oracle export processes (writes of export records only):** 100004733440719, 100004734412462, 100004733440757.
- **REST GETs:** about 110 (approximate), including 59 price-list item reads.
- **SOAP reads:** 43 attempts, 25 with an Oracle response. 18 went through FSCR's reader (8 account reads, 4 location reads, 6 profile reads, 4 of which returned HTTP 500), and 7 profile reads through my `soap_read.py`. The other 18 failed on DNS before sending: 12 `findPersonProfile` (4 parties × 3 attempts) and 6 profile reads.
- **Tool calls:** about 90 in this test (my approximate count, not tallied exactly).
- **Files written:** 160 files, 9.1 MB (8.1 MB of it evidence), excluding the 86 MB FSCR copy.
- **FSCR files read:** about 40 skill, rule and catalog files.

| When | Source | Context size | 5-hour plan window | Weekly |
|---|---|---|---|---|
| Start 07:10 | app `get_usage` | 210,862 | 10% (that window reset at 07:20) | 26% |
| End 07:34 | app `get_usage` | 396,367 | 11% (a new window) | 28% |

Context size is the running size of this session's window, **not billed tokens**. The start figure already included all earlier work in this session (Run 01 and its follow-ups). Context added during Test 4 is about **185,505 (396,367 − 210,862)**. The weekly window rose by **2 points**, which may include other use on the account. The 5-hour figures span a reset and can't be subtracted.

**Verification at the end:**
- **Oracle:** no price list or order type was updated after 07:10. Every FSCRT price list, lookup, organization, person and data-access row has a LastUpdateDate before the run started (`evidence/final/`).
- **Only Oracle records this test created:** the 3 export processes 100004733440719, 100004734412462 and 100004733440757.
- **Local files:** Run 01's 6,384 files and the original repo are hash-identical to their start states. The run 02 FSCR copy is identical to Run 01's copy (`diff -rq`).
- **Processes:** no Python process is left running and nothing listens on port 8765. I started no server. Your page was not running, and I didn't start it.

## 8. Where FSCR's documentation was wrong or contradicted the pod
1. **Business units:**
   - `ora_reference_lookups.md` says a BU create requires a primary ledger and legal entity. The pod holds BUs without either, including both FSCRT ones.
   - The Default Set *is* readable, through FSCR's export; Run 01's conclusion was too narrow.
2. **Customer reader:** `customer_soap_read` hides Oracle's message by design, so "the account has no profile" is indistinguishable from a server error.
3. **Customer uploads skill:** written for organizations only, yet its reader works for person accounts too. There is no person-party read.
4. **Router:** documents only implementation objectives; "what is set up?" has no route. AGENTS.md effectively forbids exploratory reads.
5. **Validators and comparison skills:** `cross-pillar-dependency-validator`, `configuration-completeness-validator`, `environment-comparison` and `configuration-drift-analyzer` are 2 KB stubs with no scripts.
6. **Task-level compare:** its name suggests a local compare, but it needs uploads to Oracle.

## 9. Capability matrix
| Capability | Area | Tested | Result | Evidence | Limits |
|---|---|---|---|---|---|
| Create | all | not exercised | – | – | read-only test |
| Understand environment | BU, PT, lookups, order types (export); customers (SOAP) | yes | 3 areas end to end, 3 partly, price lists none; FSCR does no explaining or linking | exports, SOAP XML, `area_facts.json` | profile errors hidden; prefix unreadable; price lists unreadable via FSCR |
| Change | all | not exercised | – | – | – |
| Plan and advise (routing, modes) | 8 questions | yes (static) | 4 of 8 reach a suitable skill, 3 partly, 1 wrong (price lists); 6 of 8 would stop for an offering choice, 1 is ambiguous, 1 resolves; no read intent | section E | no executable router |
| Verify | PT | yes | FSCR reconcile verified, 0 mismatches | `fscr_pt_reconcile_fresh.json` | PT only |
| Breadth | 10 tasks in 5 other areas | static | all have a generic export route (CSV Y); none has its own reader | `evidence/F/coverage_scan.json` | not run live |

## 10. Honest assessment
**What FSCR did well:**
- The generic setup export is a solid reader for any task with CSV export support. It read three of the eight areas completely, including the BU default set.
- Payment-term reconcile is a real, offline, field-level comparison.

**Where it falls short for "understand the environment":**
- It has no reader for price lists or person parties.
- It doesn't explain, link areas or flag gaps.
- Its compare needs writes.
- Its router has no read intent.
- Its customer reader hides the one fact that mattered most: that FSCRT accounts have no profile.

**FSCR versus me:** see the split in section 1.
- FSCR contributed the bulk data for 5 areas and one verified comparison.
- Every explanation, every link (B), all findings in C except C6, the price-list and person reads, and the general state comparison (D) were mine.

**Time:** no hand-done baseline was measured, so no speed claim is made.
