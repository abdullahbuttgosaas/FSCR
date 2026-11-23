# FSCR evaluation: full context (everything found, Runs 01–06)

**Purpose of this document:** a complete, self-contained record of everything discovered while evaluating Oracle's FSCR repository on a test pod, written so another Claude conversation can use it as background knowledge. Every number here comes from the run reports, ledgers, evidence files or the session transcript. Labels used: **verified** (checked against Oracle data or the repo), **not verified**, **unclear**, **inferred**.

Compiled 2026-11-04 from:
- `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01` … `_fscr_run_06_requirements`, each with `RUN_REPORT.md`, `ledger.md`/`ledger.csv` and `evidence/`;
- `FSCR_Run_Facts.md`, `FSCR_Creation_Tokens.md` and `FSCR_Creation_Tokens_calls.csv` in the same folder;
- the session transcript.

---

## 0. Quick facts

| Item | Value |
|---|---|
| What FSCR is | Oracle's **Fusion Setup and Configuration Skills Registry**: a repository of AI "skills" (Markdown manifests, rule files, catalogs and some Python scripts) for implementing Oracle Fusion Cloud setup |
| Who ran it | Claude Code (model Claude Opus 5.5), executing every step from a shell. FSCR has no runner of its own. |
| Who asked | Abdullah Butt (GoSaaS), for a business presentation to Oracle practice leads |
| Pod | **ETIA-TEST**, Oracle Fusion release **11.13.26.10.0** (26.10), one user: `Configuration.TEST` |
| Dates | 2026-11-02 23:49 to 2026-11-03 22:14 (+05:00) |
| Test record prefix | Every record created is named `FSCRT_…` (FSCR Test) |
| Original FSCR repo | `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`. Never changed; hash-checked before and after every run. Each run used its own copy (`fscr-work`, `fscr-work2` … `fscr-work6`). |
| Runs | 01 Create (OM + Financials) · 02 Understand (read only) · 03 Change · 04 the 16 Finance create-script skills · 05 Breadth sample of 40 skills (read only) · 06 Existing setup + new requirements |
| Oracle creation methods actually executed | FSM / Data Loader CSV, REST, SOAP. **FBDI and HDL were never executed.** |

---

## 1. How FSCR is built (as observed)

### 1.1 Layers
- **`router/`**: `implementation-router/SKILL.md` and `project-objective-classifier/SKILL.md`. **Text only, no script.** Written for implementation objectives; there is no "read/explain the environment" intent. When a task belongs to more than one offering, the classifier marks the offering *pending* and asks the user.
- **`pillars/`** (`erp`, `scm`, `hcm`, `cx`, `common`): per-task skills. Many have an `ora-resource/` folder of rule files (input validation, defaulting, dependency readiness, reference lookups, bulk intake) plus a rule registry JSON.
- **`core/`**: technical services:
  - `core/auth/fusion-oauth-authentication` (`fusion_login.py`, PKCE browser login on port 8765; token lasts 1 hour; no refresh token);
  - `core/data-loader` (`upload_and_initiate.py`, `get_data_load_info.py`) and its **Task Hook** (`task_hook.py`);
  - `core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`;
  - `core/fusion-api/apps-common/lookups` (`references/standard-lookups.md`);
  - `core/runbook` (`runbook_rest.py`);
  - `core/project-mgmt/project-workspace-initializer`.
- **`shared/`**: cross-pillar methods:
  - `shared/setup-export/task-level-export` (`export_setup_task_csv.py`), the most useful single tool;
  - `shared/baseline-assessment/setup-compare/task-level-compare` (`compare_setup_task_zips.py`);
  - `shared/validation/setup-data-validator` (only resolves context, validates nothing);
  - several 2 KB stubs with no scripts: `cross-pillar-dependency-validator`, `configuration-completeness-validator`, `environment-comparison`, `configuration-drift-analyzer`.
- **`knowledge/`**: catalogs, e.g. `knowledge/setup-task-catalog/effective/setupTasksAll.json`, and `knowledge/product-guidance/`.
- **`governance/`**, **`schemas/`**, **`project/`** (workspace template `project/_template`).

### 1.2 The FSM task-adapter chain (the "16 create-script skills")
Each of 16 ERP Financials skills ships `fsm_task_adapter.py` (about 1,800 lines) plus `e2e-adapter.json`. Steps:
1. manifest, normalize, build, validate (offline);
2. Data Loader preflight, which says "passed validation. No data was uploaded." and then asks for approval;
3. the Task Hook;
4. UCM upload, data-load request and FSM import;
5. a fresh export, then the adapter's `reconcile`.

### 1.3 The Task Hook (important governance finding)
- It only accepts tasks listed in the project's **generated Run Book** (`task-context.json`). A new task set therefore needs a **new FSCR project**, and initializing a project creates an **Oracle Run Book record** in the pod.
- It returns a rule plan ("checks have not yet run"). **The AI agent must evaluate FSCR's rule files and write `rule-results.json` itself.** FSCR checks only the file's structure (one result per planned rule file, allowed status, shape). It does **not** re-run the rules. **The approval gate is self-attested by the AI.**
- In Run 03 the session's own permission classifier blocked Claude's first rule-results write ("Security Weaken"), because an agent was grading its own safety checks. The user then allowed add-only writes.

### 1.4 Repository size (recounted in the original repo; verified)

| Statistic | Value | Correct meaning |
|---|---:|---|
| Skill manifest files | 1,126 | 1,124 `SKILL.md` + 2 `skill.md`, guides included (not all files in the repo) |
| Leaf skills | 934 | Folder rule: no other skill folder beneath it. Says nothing about whether it performs a task. |
| Parent skills | 192 | Contain other skill folders; usually offering or area overviews (not "reference material") |
| Catalog tasks | 2,616 | `setupTasksAll.json`, 2,616 distinct task codes |
| Tasks with a skill | 701 | Distinct catalog task codes named in skill manifests (848 if any task `.md` under `pillars/` is counted; 848 taken from an earlier file, not re-checked) |
| CSV export/import tasks | 2,076 | `CSVExportImportSupportedFlag = Y` (covers export and import together); 2,121 have `ExportImportSupportedFlag = Y` (not re-checked) |
| Skill files by layer | | 1,009 `pillars/`, 82 `shared/`, 33 `core/`, 3 `router/` |

Leaf skills by area: HCM 359 · SCM 202 · CX 166 · ERP 84 · Shared 81 · Core 31 · Common 8 · Router 3 = 934.
All skill files: HCM 457 · SCM 243 · CX 196 · ERP 103 · Shared 82 · Core 33 · Common 9 · Router 3 = 1,126.
Only HCM, SCM, CX, ERP and Common are Oracle areas; Shared, Core and Router are FSCR's own layers. The pillars also hold 162 other task `.md` files with a task code (CX 72, SCM 59, HCM 21, Common 6, ERP 4), not in either count.
**ERP has the fewest pillar skills (84), but all 16 skills with their own create scripts are ERP Financials.**

---

## 2. Run 01: Create (Order Management + Financials)

**When:** 2026-11-02 23:49:54 to 2026-11-03 01:27:29. 98 min wall clock, of which 47 min was waiting for Oracle sign-in, so **51 min active**. Follow-ups for price lists on 2026-11-03 at 06:40–06:45 (create) and 06:59 (approve).
**Input:** 24 records pasted by the user, two per sub-module. The attached workbook `Upload_sheet_FSCR_Run01.xlsx` was **not used** (decision D2: the brief said the pasted records were the whole input). Its data rows hold the same records.

### 2.1 Result: all 24 created and read back

| Object | Area | Records | Method | Who did what |
|---|---|---:|---|---|
| Receivables payment terms (FSCRT_2P10N30F1, FSCRT_D25B75AF1) | ERP | 2 | FSM / Data Loader CSV (UCMFA04523803, request 4431298; 3 objects, 0 failed) | **FSCR end to end**, but on `payment_terms_fsm_package.py` **patched locally on 2026-10-28**. The original failed on this pod with `payment_terms_object_order_mismatch` (hard-coded order [TERM, TRANSLATION, DISCOUNT, LINE]; the pod declares [LINE, TERM, TRANSLATION, DISCOUNT]). The original was not re-tested. Reconcile: verified, 0 mismatches. |
| Lookup types (FSCRT_OUTDOOR_ACTIVITY_F01, FSCRT_CARRIER_SERVICE_TIER_F01) | SCM | 2 | REST POST `/standardLookups` | FSCR route and client; **request bodies Claude's** |
| Lookup codes (HIKING, PADDLING, STANDARD, FREIGHT) | SCM | 4 | REST POST `…/child/lookupCodes` | same |
| Order types (FSCRT_SO_TRAIL_DEALER_F01, FSCRT_SO_WARRANTY_SWAP_F01) in ORA_DOO_ORDER_TYPES | SCM | 2 | REST POST | same |
| Business units (FSCRT_Quillon Ridge Outfitters West F01, FSCRT_Brindle Harbor Marine Supply F01) | ERP | 2 | FSM / Data Loader CSV (UCMFA04523794, request 4431286; 2/0) | FSCR export, Data Loader and Task Hook; **file builder Claude's** (`build_bu_package.py`, ~60 lines), because FSCR ships no builder |
| Price lists (+2 access sets): FSCRT_Quillon Ridge Wholesale Tents USD F01 (300000394622041), FSCRT_Brindle Harbor Dock Equipment EUR F01 (300000394623080) | SCM | 2 | REST POST (follow-up), then REST PATCH StatusCode → APPROVED | **Claude's code** (`rest_diag.py`). FSCR supplied only the sign-in token. |
| Organization customers (FSCRT_Kestrel acct 22050, FSCRT_Pemberton acct 22051) | ERP | 2 | SOAP (createLocation → createOrganization → createCustomerAccount) | **Claude's code** (`customers_soap.py`); FSCR's `customer_soap_read` did the read-back |
| Person customers (FSCRT_Caspian Reed Thornbury Jr. 22052, FSCRT_Linnea Voskuijlen 22053) | ERP | 2 | SOAP (createPerson) | **Claude's code**; FSCR has **nothing** for person customers |
| Address purposes (bill-to/ship-to site uses) | ERP | 6 | SOAP, inside the account create | **Claude's code** |

**The correct split (verified against the ledger): 2 + 8 + 14.**
- 2 used FSCR end to end on a patched script.
- 8 used FSCR's route and client with Claude's request bodies.
- 14 needed Claude's code: 2 BUs, 2 price lists and 10 customer records.

A proposed "10 + 11 + 3" split was wrong. By area, 10 are Order Management (lookups, order types, price lists) and 14 are Financials.

Payment terms also created child rows that are not counted in the 24: 3 lines, 1 discount, 2 translations, 2 set assignments.

### 2.2 FSCR guidance for the 14 records that needed code
- **Business units:** FSCR had the route ("export template → validate → core.data-loader import") and 11 rule files plus a registry. Only the file builder was missing.
- **Price lists:** `import-price-lists/SKILL.md` is **FBDI only**, using Oracle's `PriceListsImportBatchTemplate.xlsm`, which is not in the repo.
  - The pod's Data Loader has **353 objects, 0 FBDI**.
  - No price-list REST route exists anywhere in FSCR (search for `/priceLists`: 0 files).
  - The skill cites `tests/golden-scenarios.md`, which does not exist.
- **Organization customers:** `manage-customer-uploads` has an FBDI packager (`customers_package.py`), which returned `OFFLINE_PREVIEW_LIVE_BLOCKED`, `live_ready: false`.
  - The skill is organization-only.
  - It has a read-only SOAP reader.
  - No SOAP create exists in FSCR (createOrganization, createPerson, createCustomerAccount, createLocation: 0 files).
- **Person customers and their 2 purposes:** no FSCR guidance at all.

### 2.3 Where the 8 lookup/order-type request bodies came from
- FSCR gave the endpoint (`standard-lookups.md` lines 16 and 18), the client usage, the discovery order (Common → Standard → Generic → Set-enabled), "approve before create" and "no automatic retry". It gave **no body fields**.
- Fields came from Oracle's `describe` and from reading an existing lookup.
- ModuleId `61ECAF4AAB00E990E040449821C61C97` was copied from ORA_DOO_ORDER_TYPES. That it means "Order Management" is *inferred*.
- Claude chose the Standard lookup view, CustomizationLevel U and AUTH, and Y/N enabled flags.

### 2.4 Price lists in detail
- **Main run:** 3 POSTs were rejected with HTTP 400: "Attribute set with value … for BusinessUnitId in PriceListHeaderVO failed" (27011) and "The value of the attribute BusinessUnit isn't valid."
  - **Cause:** the user Configuration.TEST had no **Pricing Administrator data access** on the new BUs. FSCR says nothing about this.
  - The grant is a security change, so Claude did not make it.
- **The user granted the access**, and both POSTs then returned HTTP 201.
  - Oracle stored them as **IN_PROGRESS** even though StatusCode APPROVED was sent.
  - A `PATCH {"StatusCode":"APPROVED"}` then gave HTTP 200, and the lists are Approved.
  - FSCR has no route to change the status of an existing price list.

### 2.5 Failures in Run 01
| # | Failure | Cause | Outcome |
|---|---|---|---|
| 1 | Sign-in expired | 1-hour token | FSCR login in background; OK |
| 2 | FSCR REST client "valid HTTPS authority" error | Git Bash rewrites `/fscmRestApi/...` paths | `MSYS_NO_PATHCONV=1` (`fr.sh`) |
| 3 | Task Hook: "Task context must be the project's generated task-context.json." | Task not in the project's Run Book | New FSCR project + Run Book "FSCRT Run01 OM Setup" (WorkerJourneyId 300000394648040) |
| 4 | FSCR export silently appended a row to an existing project file (token-usage log) | `export_setup_task_csv.py` side effect | Restored; all FSCR runs moved to a copy |
| 5 | `task_to_skill_mapping.py` crash | `ModuleNotFoundError: No module named 'task_context'` | Sequence set by hand |
| 6 | Price-list POST 400 | No BU data access | Fixed by the user's grant |
| 7 | DNS `getaddrinfo failed` ×3 | Local network | Retried; nothing had been sent |
| 8 | SOAP party create faults | Boolean flags sent as Y; missing party usage; person names and tax ID belong on PersonProfile | Fixed and re-sent after confirming nothing was created |
| 9 | SOAP account fault "JBO-27008: Attribute SetCode … cannot be set." | Must use SetId | Fixed |
| 10 | FSCR `customer_soap_read` failed once: `CUSTOMER_SOAP_CORE_CALL_FAILED` (cause hidden by design) | Transient | Re-ran OK |

SOAP totals: 20 calls; 12 succeeded and 8 faulted, each fault creating nothing.

### 2.6 Where FSCR's docs were wrong against the pod (Run 01)
1. FBDI routes assume FBDI objects are registered in Data Loader; ETIA-TEST has none.
2. Nothing about Pricing BU data access.
3. BU reference lookups say a BU needs a primary ledger and legal entity; it was created without either. The declared `locationsLovV2` GET returned 0 rows without its finder.
4. Manage Order Lookups covers only existing OM lookup types; creating a new user lookup type isn't covered, though the generic route worked.
5. The shared setup-data validator only resolves context ("Task-local guidance files: 0").
6. The export script writes into an existing project file, contradicting the data-loader skill.
7. Windows problems: Git Bash path rewriting, pywin32 invisible under `python -I`, and gzip error bodies printed undecoded.
8. `task_to_skill_mapping.py` import error.
9. Customers skill: the packager requires PARTY_NUMBER for a new party; organization-only; Sales-Tax-Inside-City-Limits 1/0 vs Y/N conflict unresolved.
10. Payment terms: the hard-coded object order (patched 2026-10-28). The 15-character name limit *is* documented (`ora_input_validation.md:69`).

### 2.7 Changes on the pod outside the records
- The FSCR Run Book "FSCRT Run01 OM Setup", created automatically by FSCR; 2 of 5 tasks completed.
- The Pricing data-access grant, made by the user.

---

## 3. Run 02: Understand an existing environment (read only)

**When:** 2026-11-03 07:10:16 to 07:34:37 (**24 min**). No sign-in was needed. Nothing was created except 3 Oracle export process records.

### 3.1 What FSCR could read (8 areas)
| Area | Read end to end by FSCR? | Route / what was missing |
|---|---|---|
| Business units | Partly | FSCR export FUN_MANAGE_BUSINESS_UNIT (100004734412462) gave everything, including the **Default Set** (ENTERPRISE), which Run 01 had wrongly called unreadable. User data access needed Claude's read (`dataSecurities`). Set assignments for FSCRT BUs: 0 rows (reason unclear). |
| Price lists | **No** | No FSCR read route (task CUSTOM_IMPORT_PRICE_LISTS has CSV export N; the skill is import only). Claude's REST read the headers. **All 55 price lists return 0 lines through REST**; real or hidden is *unclear*. |
| Payment terms | **Yes** | Export (100004733440719) + FSCR offline `reconcile`: verified, 0 mismatches |
| Lookup types and codes | **Yes** | Export DOO_MANAGE_ORCHESTRATION_LOOKUPS (100004733440757) + FSCR REST client |
| Order types | **Yes** | same |
| Organization customers | Partly | FSCR SOAP reader: account, site, site uses, DFF, location. Profile read returned only `CUSTOMER_SOAP_HTTP_500`. |
| Person customers | Partly | Account level only; no person-party reader. Name prefix unreadable by any route. |
| Address purposes | **Yes** | Inside FSCR's getCustomerAccount |

4 areas were read end to end (payment terms, lookups, order types, address purposes); the report says "three" because it counts lookups and order types as one.

### 3.2 Findings Claude made that FSCR did not
- **C1:** the 4 FSCRT customer accounts have **no customer profile**, so no payment terms, credit or collector. Oracle: "The record for Account ID … doesn't exist." FSCR's reader hid this as HTTP 500. *(verified)*
- **C2:** FSCRT BUs have no primary ledger, legal entity or business functions; 94 of 183 BUs in the pod have no ledger. *(verified)*
- **C3:** every price list in the pod shows 0 lines via REST. *(unclear)*
- **C5:** pre-existing zz_test_pl_8034_all is In progress with no access set.
- **C7:** all Run 01 customer records show 0 differences from the request payloads.
- **C9:** FSCRT BUs have 0 set-assignment rows, while 123 of 183 BUs have rows (impact *unclear*).

### 3.3 Comparison and explanation
- **FSCR's general compare uploads both ZIPs to Oracle** and starts a compare process, which is a write. It was run as a dry run only, and Claude wrote a local diff (`diff_exports.py`).
- FSCR provides **no explanations, no cross-area links** (price list → BU → set → user access) and **no gap finding**. All of that was Claude's (`analyze.py`).
- Routing 8 plain "what is set up?" questions by following the router text:
  - 4 reach a suitable skill, 3 partly, and 1 is wrong (price lists → an import-only skill);
  - 6 of 8 would stop to ask for an offering.
- AGENTS.md says read-only calls outside a workflow are "not permissible as exploratory shortcuts", so FSCR's own rules discourage exploratory reads.
- **Execution modes:** none of the 8 area skills is "automated"; only export and lookups (hybrid) actually call Oracle.

### 3.4 Data-source split (Claude's estimate, not measured)
About 45% of the raw data came from FSCR (3 exports, customer reads, the reconcile) and about 55% from Claude's own calls and code.

### 3.5 Breadth check (static, not live)
10 further tasks (inventory, procurement, product management, shipping, HCM) all have a skill and CSV export Y, but none has its own read script.

### 3.6 Scripts Claude wrote (7, about 26 KB)
`rget.py` (GET-only REST), `soap_read.py` (get/find-only SOAP, shows Oracle fault text), `fscr_cust_read2.py`, `fr2.sh`, `diff_exports.py`, `analyze.py`, `coverage_scan.py`.

---

## 4. Run 03: Change existing setup

**When:**
- main run 07:49:05–08:05:43 (17 min);
- follow-up 08:24–08:31 (7 min), after the user allowed the Task Hook writes;
- second compare and amendments 08:45–08:49 (about 4 min).

**Active about 24–28 min; 60 min first start to last finish.**

### 4.1 The 6 changes: 5 done and verified, 1 refused by FSCR
| # | Change | Route | Result |
|---|---|---|---|
| C1 | Payment term FSCRT_D25B75AF1 end date blank → 2028-12-31 | FSCR route with **two deviations**: a run config with a blank Run Book ID (so the Run Book wasn't updated), and the patched payment-terms script. Task Hook rule results AI-attested. | **Done.** Request 4432070, 3 objects, 0 failed; FSCR reconcile verified. FSCR produced a minimal candidate: only EndDateActive changed, 86 fields preserved. FSCR's script supports `end-date` even though the manifest marker lists only "create, update". |
| C2 | FSCRT_STANDARD enabled Y→N; FSCRT_FREIGHT N→Y; FSCRT_HIKING meaning → "FSCRT_Hiking and trekking", description → "Day hikes and multi-day treks" | FSCR REST client PATCH, Claude's bodies | **Done** (3 × HTTP 200) |
| C3 | FSCRT_SO_TRAIL_DEALER_F01 end 2027-10-31 + new description; FSCRT_SO_WARRANTY_SWAP_F01 enabled N→Y | same | **Done** (2 × HTTP 200) |
| C4 | Brindle BU manager Yaqub, Younas → Smith, Aron | FSCR BU rules; Claude's builder `build_bu_update.py` | **Refused by FSCR.** The BU rule registry is **create-only**. `ora_input_validation.md` line 28 classifies an existing BU that differs as `existing-different` and blocks it. Rule BU.IDEMPOTENCY (line 55): "new->BU.READY;existing-identical->BU.NOOP;existing-different->BU.BLOCKED". Task Hook: "Preview is blocked until user corrections are supplied and all rules pass: ora_input_validation.md." Nothing was sent. Whether a CSV import would replace or add a manager is unknown. |
| C5 | Brindle price list description + ", 2027 season", end 2027-10-31 → 2027-09-30 | **Claude's REST PATCH** (`rmut.py`); FSCR has no route | **Done.** Oracle allowed editing an **Approved** list directly, and it stayed Approved. |
| C6 | Kestrel account description; Linnea shipping instructions (DFF) | **Claude's SOAP** `updateCustomerAccount` (`soap_update.py`); FSCR's only route is FBDI | **Done.** All 3 DFF segments were sent to avoid blanking the others; the risk itself was not tested. |
| C7 | Delete-route check (read only) | – | FSCR documents REST DELETE only for lookup types and codes. None for BUs, price lists, customers or payment terms (payment terms explicitly refuse hard delete). Nothing deleted. |

**Verified: no change outside the named records.** Whole-area before/after diffs covered 17 payment terms, 183 BUs, 6 lookup types and 68 codes, 60 order types, 55 price lists, 4 accounts and 212 site rows. The Run Book was unchanged.

### 4.2 FSCR compare
- **First run** (162140984) used identical data, so it proved nothing.
- **Second run** (162143105), on payment terms before vs after C1: **detected the one real change correctly with no false differences** (Receivables Payment Terms: 1 mismatch, 16 match).
- **Gap:** FSCR's report shows **counts only**. The record and field detail sits in Oracle's nested `AR_PAYMENT_TERM_Discrepancy.xml` inside the report ZIP, which FSCR downloads but does not parse; Claude extracted it.
- The compare also writes Oracle records (file blobs, uploads, a compare process) and appends to the token-usage log.

### 4.3 Run 03 amendments (corrections the user required)
- **A1:** the Task Hook gate is AI self-attested. Claude's first draft marked as `passed` some rule files only judged not applicable; the permission system caught it, not FSCR.
- **A2:** C1 had two deviations (blank Run Book ID config; patched script).
- **A3:** the first compare proved nothing; the second one detected the change.
- **A4:** Data Loader status logs are written **outside the repo** at `C:\Users\PC\.codex\data-loader-status-logs\requestid-<id>\`.
- **A5:** risk of a partial DFF update.
- **A6:** unknown C4 behaviour.
- **A7:** the capability row was restated.

### 4.4 Other doc problems found
- The Data Loader `runID` makes Fusion update Run Book task status: a side effect on a record outside the setup being changed.
- No export resume-by-process-ID.
- The rule `BU.NO_FULL_DATA_EXPORT` forbids using the full BU export as a source, yet that export is the only way to read the Default Set.
- The BU skill text mentions "create or update intent" but the registry only reaches READY for a new BU.
- The Data Loader deletes its single-use preflight and envelope files after upload.

### 4.5 Scripts Claude wrote
7 new (about 15 KB): `rmut.py`, `soap_update.py`, `build_bu_update.py`, `snapshot.sh`, `diff_areas.py`, `diff_accounts.py` and `fetch_export_result.py`, plus one-off report updaters. 6 helpers were reused from Runs 01–02.

---

## 5. Run 04: the 16 Finance skills that ship their own create script

**When:** 08:50:44 to about 09:24 (**about 33 min**). All 16 are ERP Financials.
**Definitions:**
- **Works unmodified:** FSCR's own route ran end to end with no patch, and the record was read back.
- **With a patch:** a patched copy of an FSCR file was needed.
- **Blocked:** stopped before import by an FSCR guard or for lack of a safe target.
- **Failed:** stopped by an error that couldn't be passed without skipping a safety check.

### 5.1 Scorecard
| # | Skill | Built for | Result | Evidence |
|---|---|---|---|---|
| S1 | Receivables Payment Terms | 26.10 | **With a patch** (Run 01's order-check patch, medium) | Run 01 request 4431298 |
| S2 | Payables Calendars | 26.10 | **Works unmodified** | request 4432126, 2/2; FSCRT_CAL1 + 12 periods; reconcile PASS |
| S3 | Payables Payment Terms | 26.10 | **With a patch** (1 line, reconcile only): export dates YYYY/MM/DD were compared as text with ISO dates, giving a false FAIL | request 4432147, 3/3; FSCRT_AP_N45 |
| S4 | Bank Charges | 26.10 | **Blocked** | exports only |
| S5 | Common Options | 26.10 | Blocked: no safe target | exports only |
| S6 | Invoice Options | **27.01** | Blocked: no safe target | exports only |
| S7 | Payment Options | **26.04** | Blocked: no safe target | exports only |
| S8 | AutoInvoice Grouping Rules | 26.10 | **Works unmodified** | request 4432170, 3/3; FSCRT_GRP1; reconcile PASS |
| S9 | Remit-to Addresses | 26.10 | **Blocked** | exports only |
| S10 | Receipt Classes and Methods | **26.07** | **Failed:** "Build template node sequence for AR_RECEIPT_CLASS is '2', expected canonical value '1'." After a patch: "Relationship 3 violates package dependency order: AR_RECEIPT_METHOD must precede AR_CC_ERROR_MAPPINGS." | exports only |
| S11 | Conversion Rates and Policies | **27.01** | **Blocked** | exports only |
| S12 | Transaction Types | 26.10 | **Works unmodified** after an input fix. The first import 4432190 was rejected by Oracle: "JBO-27014: Attribute CreationSign … is required." FSCR's rules don't require CreationSign. | request 4432197, 2/2; FSCRT_TT1 |
| S13 | AutoAccounting Rules | **27.01** | Blocked: no safe target | exports only |
| S14 | Transaction Sources | 26.10 | **Works unmodified** after 3 input corrections the adapter demanded (create entity isn't AR_BATCH_SOURCE; no create contract for the transaction-type link; LastBatchNum ≥ 1 with automatic numbering) | request 4432203, 2/2; FSCRT_TS1 |
| S15 | Receipt Sources | **26.07** | Blocked: no safe target; depends on S10 | exports only |
| S16 | Receivables System Options | 26.10 | Blocked: no safe target | exports only |

**Totals: 4 unmodified, 2 with a patch, 1 failed, 3 blocked by FSCR's own guards, 6 blocked for lack of a safe target = 16.**
The presentation counts **10 creation skills** (4 + 2 + 1 + 3; the 6 with no safe target weren't attempted). **5 records were created in Run 04** (S2, S3, S8, S12, S14); S1's records came from Run 01.

The 6 "no safe target" skills each need a **business unit with a ledger and business functions**. All 18 AP_SYSTEM_PARAMETER rows carry SOBName. The FSCRT BUs have no ledger, and existing BUs were off limits.

### 5.2 The 3 blocked tasks explained
All three stopped **inside FSCR's adapter, offline, before anything reached Oracle**. Oracle only ran exports, so there was no Oracle error in any of the three.

**Bank Charges (S4):** missing FSCR capability, plus Claude's safe-target decision.
- `e2e-adapter.json` line 126: `"readiness": "blocked"`, with the blocker "ORA_AP_BANK_CHARGE has no configured local row-index fields". 6 of its 8 capabilities are blocked.
- Normalize: "Operation b1 targetKey must contain exactly []." The adapter allows no identifying fields, so no create can be described. (A design with no identifying fields was not tried.)
- A bank charge has no name, so it can't be FSCRT-named, and any create would affect existing legal entities or banks.
- A custom builder plus FSCR's Data Loader is plausible but was not tested.

**Remit-to Addresses (S9):** two FSCR defects, then an unfinished safety gate.
1. "Base URL must be the credential-free HTTPS root of the selected environment." The adapter (around line 1773) requires the first host label to equal `etia-test`. This pod's host is `fa-etia-test-saasfaprod1…`, so it can never pass. **Code defect**, and only this adapter of the 16 has the check. Patched (1 line) in a copy.
2. "targetKey must contain exactly […'OrigSystemReference'…]". The adapter requires it as a key, but `ora_defaulting_rules.md` line 15 says the value is service-derived and must not be invented. **FSCR contradicts itself.**
3. "Operation r1 creates conditionally blocked key field AR_REMIT_TO_LOCATION.SetCode: Target access policy and optional supported public preflight are not yet reviewed." Declared under `conditionallyBlockedFields` (around line 218), status "partial". This is an **intentional but unfinished gate**, and it was not bypassed.

**Conversion Rates (S11):** an intentional gate that **can't be satisfied as built** (observed limitation, not proven impossible).
- "Operation x1 creates conditionally blocked key field EXM_EXCHANGE_RATE_OPTION.BuName: Require fresh complete exact destination reference evidence bound to the candidate…". Descriptor line 233, status "requires_preflight".
- The evidence must be bound to the candidate file's SHA-256, but the gate is checked at normalize, before the build creates that file.
- The adapter was built for 27.01 while the pod runs 26.10; no error points to this.

### 5.3 Patches (copies in `_fscr_run_04_create16\patches\`; FSCR files untouched)
- **S3:** `ap-payment-terms/fsm_task_adapter.py` line 1475; the reconcile accepts `/` → `-` dates.
- **S9:** `remit-to/fsm_task_adapter.py` line 1773; the host check accepts a host *containing* the environment name.
- **S10:** `receipt-classes/e2e-adapter.json`; 4 nodeSequence values. It still failed afterwards.

### 5.4 Wrong or overstated in FSCR (Run 04)
1. The "full create set / e2e ready" labels overstate readiness: only 4 of 15 run created a record unpatched, and three adapters block their own create keys.
2. 6 of 16 adapters were built on other releases (26.04, 26.07, 27.01); Receipt Classes failed on this drift.
3. **Export object order varies between exports** of the same task, yet adapters pin node sequences. The S12 first reconcile failed on this; a second export passed.
4. The AP reconcile date-format bug.
5. The Remit-to host check and OrigSystemReference contradiction.
6. CreationSign is required by Oracle but not by FSCR.
7. The Transaction Sources create entity and contract gaps.
8. The "test files" are a specification catalog with **no runner** (0 executable variants among 93).
9. **The discount basis "F" contradicts itself:** `payment_terms_fsm_package.py:81` says "Lines and tax, excluding freight", while `e2e-adapter.json:808` says "Freight". All 17 pod terms store I, so this was **not verified** on the pod.
10. The Data Loader writes logs outside the repo.

### 5.5 Other Run 04 facts
- A new Oracle Run Book "FSCRT Run04 Create16" (300000394655024) was created with 15 tasks, 5 completed.
- 36 export processes; 6 import requests (4432126, 4432147, 4432170, 4432190 failed with 0 created, 4432197, 4432203).
- Every whole-area diff showed only FSCRT additions.
- The creation order was worked out by Claude, because FSCR's sequence resolver crashes.
- Claude wrote every design file, since FSCR has no request-to-design step that runs.
- Observed: **about 4–7 min per working skill**, mostly Oracle import and export time.

---

## 6. Run 05: Breadth (40 random skills, read only)

**When:** 09:40:15 to 10:08:20 (**28 min**). Seeded sample (`sample40.py`, seed 20261103) of 40 of 1,123 skill files, excluding 32 already tested. Strata: ERP 10, SCM 10, HCM 12, CX 4, Shared/core 4. No cherry-picking.

**Grades:**
| Grade | Meaning | Count |
|---|---|---:|
| 0 | Route only, or no route | 28 |
| 1 | Route + field list | 7 |
| 2 | Complete recipe | **0** |
| 3 | Own runnable script | 5 |

The 5 grade-3 skills are REST helpers, a workbook builder, a security script and the UCM client. **None is a setup-import skill with an adapter.**

**Findings:**
- **Exports work everywhere:** all 20 sampled CSV-capable tasks exported from the pod (40 export processes; one data download failed on DNS).
- **Field names rarely match the pod's template columns:** median coverage is **0%**. Only 4 of 20 exceed 5%: FA value sets 20%, Contact lookups 56%, and two at 8%. Some skills list names that aren't columns; asset categories lists 17, e.g. `BookName`.
- **Routing:** 8 of 8 sample questions reach the right skill by exact task code, and 4 of 8 first need an offering choice. The router answers **which skill, not what to set up.**
- **HCM:**
  - Routes across HCM task files: FSM 190, REST 75, **HDL 22**, ESS 1. **FSCR ships no HDL builder.**
  - `hcm-dependency-graph.json` (86 nodes, 281 edges) contains only 2 of the 8 sampled HCM task codes, both with 0 edges, so it is **not usable** to order them.
- **Execution modes in the sample:** assisted 31, hybrid 9, none automated or advisory. The repo uses about 9 type labels.
- `import-items` has no Data Loader mode or CSV flag.
- Many area skills route to REST with no body recipe.

**Size of the gap:** a working adapter is about 1,800 lines per task, and none of the 40 sampled tasks has one. Adapters appear to be generated (`fscr-deliverable-builder`), so the effort is "medium" per task. HCM HDL tasks are medium–large.

**Conclusion:** for about 900 skills outside the 16 adapters, a consultant still builds each import file from the template by hand. This agrees with an earlier route audit, which found a real write recipe in only 2 of 10 REST skills.

---

## 7. Run 06: Existing configuration + new requirements (end-to-end scenario test)

**Why:** to support the presentation line "Existing configuration + new requirements — YES".
**When:** 2026-11-03 22:00:27 to 22:14:43 (**14 min**; about 6 were sign-in, including one `[WinError 10060]` transport retry; **about 8 min of work**).
**Requirements:** 6, drafted by Claude (`requirements.md`) on the user's instruction to "just complete the test".

| Req | Requirement | Current setup (read via FSCR export) | Action | Result |
|---|---|---|---|---|
| R1 | New order type "Dealer Consignment F06" (FSCRT_SO_CONSIGN_F06) | Missing | REST POST via FSCR client, Claude's body | HTTP 201, verified |
| R2 | Outdoor activity FSCRT_CLIMBING, sequence 3 | Missing | REST POST | HTTP 201, verified |
| R3 | Paddling description "Kayak, canoe and paddleboard gear" | "Kayak and canoe gear" | REST PATCH | HTTP 200, verified |
| R4 | Hiking named "FSCRT_Hiking and trekking" | Already so | None | Correctly left alone |
| R5 | Warranty swap order type enabled | Already enabled | None | Correctly left alone |
| R6 | Grouping rule FSCRT_GRP6 like FSCRT_GRP1 | Missing | FSCR's own adapter + Data Loader + Task Hook, **all unmodified** (Run 04 project) | Request 4433652, 3 loaded, 0 failed; reconcile PASS |

- **Proof nothing else changed:** fresh FSCR exports before and after.
  - Lookups: +2 codes, 1 changed, 0 removed.
  - Grouping rules: +1 rule, +1 class row, 0 changed, 0 removed.
- **Who did what:**
  - **FSCR:** read the setup (exports), sent R1–R3 (REST client) and ran R6 (adapter chain + reconcile).
  - **Claude:** wrote the requirements, did the **gap analysis** (FSCR has no gap-analysis tool), wrote the request bodies and the AI-attested Task Hook rule results, ran everything, and did the whole-area diff.
  - **No new code, no FSCR patch.**
- **Tokens:** 23 API calls; output 18,214; total 9,597,333.
- **Limits:** 6 small requirements written by Claude, not a business user, in two areas where FSCR has a working route (OM lookups, Receivables grouping rules). Price lists, customers and BU updates would still need Claude's code or are blocked, as earlier runs showed.

---

## 8. Tokens and time (exact, from the session transcript)

**Method:**
- The transcript records API usage per response (input, output, cache read, cache write).
- Each response was counted once by message ID and assigned to a run by timestamp.
- **`get_usage` "context size" figures in the run reports are NOT billed tokens.**
- Automatic summarizing calls are not recorded, so they are not counted.

### 8.1 Per run, recorded start to finish (Table B)
| Run | Window (+05:00) | Calls | Output | Cache read | Total |
|---|---|---:|---:|---:|---:|
| 01 | 23:49:54 → 01:27:29 | 228 | 175,164 | 67,566,080 | 68,116,270 |
| 02 | 07:10:16 → 07:34:37 | 87 | 89,843 | 25,865,684 | 26,141,235 |
| 03 | 07:49:05 → 08:49:18 | 133 | 132,854 | 68,290,536 | 68,655,691 |
| 04 | 08:50:44 → 09:24:59 | 110 | 115,024 | 81,036,683 | 81,329,939 |
| 05 | 09:40:15 → 10:08:20 | 18 | 16,743 | 15,393,196 | 15,442,269 |
| 06 | 22:00 → 22:14:43 | 23 | 18,214 | 9,539,882 | 9,597,333 |

Runs 01–05 start-to-next-start (including follow-ups) total 284,261,383; start-to-finish total 259,685,404 (both exclude Run 06).

### 8.2 Creation-only tokens (Run 01 + Run 04; `FSCR_Creation_Tokens.md`)
Rule: each call was labelled by what its own commands did. Shared work (sign-in, project init, shared scripts, reading FSCR files, reports) sits on separate lines and is not spread across objects.

| Group | Output | Total | Calls |
|---|---:|---:|---:|
| A. Through FSCR, no code written | 37,125 | 26,720,317 | 46 |
| B. Needed Claude's script, code or patch | 80,255 | 45,979,869 | 117 |
| C. Tried, nothing created (S4, S9, S10, S11) | 11,111 | 8,432,181 | 11 |
| **Creation total** | **128,491** | **81,132,367** | **174** |
| Separate (non-object) lines | 228,310 | 84,183,476 | 241 |

Creation output by run: Run 01 83,768 · Run 04 44,723.
One correction was made: 3 calls first labelled S11 were a discount-basis side question and were moved to a separate line.

### 8.3 Figures used in the presentation (output tokens)
| Run | Time | Output tokens | Basis |
|---|---|---:|---|
| 01 Create | 51 min active | 83,768 | creation work only |
| 02 Understand | 24 min | 89,843 | whole run |
| 03 Change | 24 min (about 28 with the final compare; 60 elapsed) | 132,854 | whole run |
| 04 Creation skills | 33 min | 44,723 | creation work only |
| **Total Runs 01–04** | **132 min** | **351,188** | |
| 06 Requirements | 14 min (about 8 of work) | 18,214 | whole run |

Rounded: about 350k total, about 130k creation (128,491), about 222k read and change (222,697 = Runs 02 + 03).

**No speed claims:** no manual (hand-entry) baseline was ever timed, so no "X times faster" statement is supported.

---

## 9. Code Claude wrote (48 files in `scripts/` folders, 39 distinct names)
- **Run 01 (14):** `build_bu_package.py`, `customers_soap.py`, `verify_customers.py`, `taskhook_lifecycle.py`, `rest_diag.py`, `fr.sh`, `token_status.py`, `token_lifetime.py`, `xsd_dump.py`, `fscr_customer_read.py`, `verify_lookups.py`, `ledger_add.py`, plus 2 one-off fixers.
- **Run 02 (7):** `rget.py`, `soap_read.py`, `fscr_cust_read2.py`, `fr2.sh`, `diff_exports.py`, `analyze.py`, `coverage_scan.py`.
- **Run 03 (15, 6 reused):** `rmut.py`, `soap_update.py`, `build_bu_update.py`, `snapshot.sh`, `diff_areas.py`, `diff_accounts.py`, `fetch_export_result.py`, plus one-off report scripts and reused helpers.
- **Run 04 (8, 2 reused):** `adapter_run.py` (runs FSCR adapter steps unchanged), `live_run.py` (runs FSCR's live chain one stage per call), `survey16.py`, `build_task_mapping.py`, `inspect_candidate.py`, `export_all.sh`, plus reused helpers.
- **Run 05 (4, 1 reused):** `sample40.py`, `analyze40.py`, `compare_fields.py`, `export_all.sh`.
- **Run 06:** none new; Run 04 and Run 03 scripts were copied and re-pointed (paths only).
- **Not counted:** `run-config-blank.properties` and the 4 files in Run 04 `patches/`.

---

## 10. Capability summary (all runs)

| Capability | Verdict | Evidence |
|---|---|---|
| **Create** in a new or empty area | Works where a skill ships its own adapter and the adapter matches the release: 5 Finance records via FSCR's chain (4 unmodified, 1 small patch). Lookups and order types work via FSCR's REST route with request bodies supplied. Price lists, customers and persons have no working FSCR route on this pod. | Runs 01, 04 |
| **Understand / read** existing setup | Strong for any CSV-capable task (the export reads the full configuration, 20/20 sampled tasks exported). Weak elsewhere: no price-list or person reader, the customer reader hides errors, no explanation or cross-area linking. | Runs 02, 05 |
| **Change** existing setup | Lookups and order types via the REST route; payment terms via the FSCR chain (patched script). BU updates blocked by FSCR's create-only rules. Price lists and customers need own code. | Run 03 |
| **Existing setup + new requirements** | Tested end to end: read → compare → apply only gaps → prove nothing else changed. Gap analysis is Claude's job, not FSCR's. | Run 06 |
| **Verify** | Strong: adapter reconcile on fresh exports; the compare detects real differences but reports counts only and writes to Oracle. | Runs 01, 03, 04, 06 |
| **Plan / route** | Router is text only. It reaches the right skill by task code but often asks for an offering choice. The sequence resolver crashes. The HCM dependency graph is not usable. | Runs 02, 05 |
| **Safety** | Gates fail closed and nothing unsafe reached Oracle, but the Task Hook relies on AI-attested rule results, and some gates are unfinished or defective. | Runs 03, 04 |

### 10.1 Where we can take advantage
- The 16 Finance create-script skills: FSCR's workflow handles export, build, validation, import and verification, with Claude Code running it.
- Full-setup exports of any supported task in one step, for reviewing an existing environment.
- Safety gates that stop unsafe or unclear creates before Oracle.
- Ready REST routes and a client for lookups: only the request body is needed.

### 10.2 Gaps we can fill
- Field mappings and file builders for the many skills that give only a route (median 0% template-field coverage).
- REST/SOAP adapters for price lists and customers (including persons).
- An HDL builder for HCM.
- A pod-readiness preflight: FBDI object registration, BU data access, ledgered BU, template presence.
- Release-matching checks for adapters.
- Non-AI-attested rule checking in the Task Hook.
- Field-level output for the compare, and an offline compare.
- Error transparency in the customer reader.
- Windows robustness: path rewriting, gzip error bodies.
- A fix for the sequence resolver.
- Gap analysis between requirements and current setup.

### 10.3 Where we can save time (qualitative; no measured baseline)
- Creating setup where a skill has its own create script: one guided flow takes minutes instead of manual file preparation.
- Reviewing setup: one export per task gives the full configuration instead of checking screens.
- Checking results: re-export and reconcile prove what changed.
- Standard REST routes: only the request body has to be prepared.

---

## 11. The presentation summary (final agreed wording, with Run 06 added)

> **Conclusion:** FSCR combined with Claude Code helps create, review, compare and modify Oracle Fusion configuration.
> - **Run 01, Create:** 24 records created. 2 used locally patched FSCR workflows, 8 used FSCR routes with Claude-written request bodies, and 14 required additional code.
> - **Run 02, Understand:** reviewed the existing setup using FSCR and Claude-written read scripts. Read only.
> - **Run 03, Change:** 5 of 6 requested changes succeeded using FSCR and Claude-written update scripts.
> - **Run 04, Finance creation:** 10 Finance creation skills counted; 5 records created. 4 worked as is, 2 needed patches, 1 failed and 3 were blocked before Oracle.
> - **Run 06, New requirements on existing setup:** read the current setup, found 4 of 6 new requirements missing, applied only those 4, and confirmed nothing else changed.
>
> **Tokens (output, Runs 01–04):** about 350k (351,188); creation about 130k (128,491); read and change about 222k (222,697). Run 06: about 18k (18,214).
> **Time:** about 132 active minutes across Runs 01–04; Run 06 took 14 minutes.
>
> **Scenarios:**
> - **New environment: YES.** It can help create setup records. Testing used an already configured pod.
> - **Existing configuration: YES.** We reviewed, compared and changed selected setup.
> - **Existing configuration + new requirements: YES.** Runs 02–03 support this workflow, and Run 06 tested it end to end.
>
> **Bottom line:** Claude Code ran every step. FSCR provides setup routes, rules and import workflows; Claude Code supplies request bodies, read and update scripts, builders, REST/SOAP code and patches.

---

## 12. Standing rules used throughout (for any future FSCR work)
- ETIA-TEST only, and only `FSCRT_` test records; no deletes; nothing pre-existing changed. Read-only runs allow no create, update, delete, import or approval.
- Never print or save tokens or secrets. The OAuth token cache stays outside the repo.
- Sign-in: `python core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto` in the background. It uses port 8765, which the user's own page also uses; check the page isn't running first. The token lasts 1 hour.
- Never use the user's portal code (`E:\GoSaaS\Configuration Automation v2.1\Configuration Automation`).
- Never change the original repo or earlier run folders; work in a copy, in a new run folder.
- Label findings verified / not verified / unclear; write "not recorded" rather than estimating; no "X times faster" claims.
- At the end, stop every process started and leave only the user's page running (never start it).
- Per the repo's AGENTS.md: implementation requests go through `router/implementation-router/SKILL.md`; exports belong under `project/{id}/exports/`; approval comes before mutating calls; failures are classified and diagnostics persisted.
