# FSCR Run 01: OM and Financials setup on ETIA-TEST

Start 2026-11-02 23:49:54 +05:00 · finish 2026-11-03 01:27:29 +05:00 · total 98 min, of which 47 min (23:56–00:43) was waiting for the Oracle sign-in. Active work: 51 min.
Environment: one pod (ETIA-TEST, release 11.13.26.10.0), one FSCR copy, 24 input records (two per sub-module). Area tags: **SCM** = Order Management; **ERP** = Financials.

---

## Part 1: Summary for practice leads (two-minute read)

**Result (updated 2026-11-03 07:05):** all 24 input records are now created in ETIA-TEST and read back, and both price lists are Approved. In the main run 22 of 24 were done; the 2 price lists (SCM) were blocked until you granted Pricing Administrator data access on the two FSCRT BUs, then created in a follow-up (see "Follow-up: price lists" below).

**How much FSCR did:**
- **FSCR end to end, but only with an earlier local patch, 2 records: payment terms (ERP).**
  - FSCR exported the current setup, previewed, built, validated, ran its approval gates, imported, re-exported and reconciled: "verified", 0 mismatches.
  - This ran on the repo's `payment_terms_fsm_package.py`, which is the copy patched locally on 2026-10-28 (15:59). The original script failed on this pod on 2026-10-28 with `payment_terms_object_order_mismatch`: it has a hard-coded object order, and ETIA-TEST declares a different one. That failure is recorded in `project/draft-impl-project-20261028/state/runs/20261028-payment-term-create-blocked.json`. **This run did not re-test the unpatched original.**
- **FSCR route and client, but my own request bodies, 8 records: lookup types, lookup codes and order types (SCM).**
  - FSCR supplied the endpoint, the REST client, the lookup-view discovery order and the approval rule. It gave no body fields. The fields, ModuleId and enabled-flag handling came from Oracle's describe, a read of an existing lookup, and my own knowledge (detail in section 3a).
- **Needed my own code, 12 records:**
  - **Business units (ERP org structure):** FSCR has the route and the rules but no file builder; I wrote one (60 lines).
  - **Customers, persons and address purposes (ERP), 10 records:** FSCR could not create them in this pod. Its only customer skill is FBDI-only and organization-only, and by its own result it is "live blocked". The pod's Data Loader has no FBDI objects at all. I wrote a SOAP client using Oracle's customer services. FSCR's own read adapter did the read-back verification.
- **Done in a follow-up, 2 records: price lists (SCM).** Blocked in the main run:
  - FSCR's FBDI route cannot run here: no FBDI loader objects in the pod, and Oracle's Excel template is not in the repo.
  - Oracle's Pricing REST rejected the new BUs. The signing-in user has no Pricing Administrator data access on them.
  - Granting data access is a security change I am not allowed to make. A security administrator must grant it; then the price lists can be created in minutes. After you granted it, both were created by REST in under a minute (my route; FSCR has no REST route for price lists).

**Where FSCR can be used on a client project today:**
- **With a patch:** Receivables payment terms (ERP). They need the local order-check patch of 2026-10-28; the unpatched original failed on this pod and was not re-tested in this run.
- **Route only, with your own request body:** lookups and order types (SCM). FSCR's REST route and client work, but someone has to supply the body fields and ModuleId.
- **With a small add-on:** business units (a CSV builder from the template).
- **Not yet:** price lists (FSCR's route is FBDI only; REST worked once data access was granted), customers and person customers.

**Biggest practical gaps found:**
1. FBDI routes assume FBDI objects are registered in the pod's Data Loader. ETIA-TEST has none.
2. Customers: no create path at all; persons not covered.
3. FSCR has no knowledge of BU data access for pricing.
4. Tooling problems on Windows/Git Bash: path rewriting, gzip error bodies, a crashing mapping script.
5. One FSCR export script silently wrote into an existing project file.
6. The Task Hook only accepts tasks from the project's generated Run Book, so a new task needs a new project and Run Book (FSCR created a new Oracle Run Book for this run).

**Time:** FSCR's FSM imports finished in about 1–2 minutes each, and REST lookups in seconds. I have no hand-entry baseline from this run, so I make no speed-up claim.

**Follow-up: price lists (2026-11-03 06:40–06:45 +05:00).** After you granted the data access:
- Sign-in: the token had expired. I ran FSCR's `fusion_login.py --token-cache auto` in the background. Your browser was still signed in to Oracle, so it completed with no password. The token was saved and the process exited. Port 8765 was free before the login (your page was not running).
- Pre-check (read-only): 0 price lists named FSCRT%.
- Create, one POST each, no retries: both returned HTTP 201.
  - FSCRT_Quillon Ridge Wholesale Tents USD F01: PriceListId 300000394622041 (USD, BU Quillon Ridge, Sale Price, Buy, Price, no end date).
  - FSCRT_Brindle Harbor Dock Equipment EUR F01: PriceListId 300000394623080 (EUR, BU Brindle Harbor, ends 2027-10-31; Line Type and Calculation Method left to Oracle defaults, which came back as Buy and Price).
- Access sets: each has ENTERPRISE (PriceListSetIds 300000394622042 and 300000394623081).
- Read-back: a separate GET compared every field sent, with 0 mismatches.
- Oracle stored both as **In progress** (IN_PROGRESS), even though I sent StatusCode APPROVED.

**Follow-up 2: approving the price lists (2026-11-03 06:59 +05:00).**
- FSCR route: none. `import-price-lists/SKILL.md` ("Approval-status decision") sets STATUS_CODE only inside the FBDI workbook before an import. It has no route for changing the status of an existing price list.
- Oracle route: the read-only `priceLists/describe` (`evidence/pricelists/describe.json`) shows StatusCode `updatable: true`, values from ORA_QP_APPROVAL_STATUSES, and item actions get/update/delete.
- Approach 1, used for both: `PATCH /fscmRestApi/resources/11.13.18.05/priceLists/{PriceListId}`, body `{"StatusCode":"APPROVED"}` (`payloads/pl_approve.json`), Content-Type application/json. No retry and no other approach were needed.

| Price list | PriceListId | Sent | Oracle response | Final status (read-back) | Error |
|---|---|---|---|---|---|
| FSCRT_Quillon Ridge Wholesale Tents USD F01 | 300000394622041 | 06:59:10 | HTTP 200, StatusCode APPROVED, Status "Approved" (`evidence/pricelists/pl1_approve_a1.json`) | **Approved** | none |
| FSCRT_Brindle Harbor Dock Equipment EUR F01 | 300000394623080 | 06:59:17 | HTTP 200, StatusCode APPROVED, Status "Approved" (`evidence/pricelists/pl2_approve_a1.json`) | **Approved** | none |

- Read-back (`evidence/pricelists/readback_after_approve.json`), compared with the earlier read-back: the only fields that changed are Status, StatusCode, LastUpdateDate and Oracle's version tag (ETag). Access sets are unchanged. EntityApprovalStatusCode is still null, so the approval-flow opt-in is not in use. No new records were created.
- Evidence: `evidence/pricelists/` (pre_check, pl1_create, pl2_create, readback). The request bodies are `payloads/pl1.json` and `payloads/pl2.json`.

**Limits:** one pod, one release, two records per module. The main run used one login (token valid 1 hour). Follow-up 1 needed a second login, which completed silently via browser single sign-on.

---

## Part 2: Full detail

### 1. Scorecard

| Module | Area | Records given | Created + verified | Partly | Not done | FSCR skill exists | Route used | Scripts I wrote (create path) | Minutes | Tool calls (approx.) | Retries | Approval / permission stops |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 Business Units | ERP | 2 | 2 (default set not REST-visible) | 0 | 0 | Partly (task guide + rules, no builder) | FSM CSV via FSCR export → my builder → FSCR Data Loader + Task Hook | `build_bu_package.py` | 12 | ~30 | 0 Oracle; 1 Task Hook refusal | G1, G2, G3 |
| 2 Price Lists (+ access sets) | SCM | 2 (+2 sets) | 2 (+2 sets), follow-up | 0 | 0 | Yes (FBDI guidance, no script) | Main run: FBDI impossible, REST rejected. Follow-up: REST POST via my `rest_diag.py` after data access grant | `rest_diag.py` | 4 + 2 | ~12 + 8 | 1 (main run) | G6; BLOCKER: BU data access, cleared by you |
| 3 Payment Terms | ERP | 2 | 2 | 0 | 0 | Yes, with own script (locally patched 2026-10-28) | FSM CSV, FSCR end to end on the patched script (original not re-tested) | none (driver only) | 7 | ~10 | 0 | G5, G1, Task Hook |
| 4 Lookup Types + Codes | SCM | 2 + 4 | 6 | 0 | 0 | Route only (endpoint + client, no body recipe) | REST via FSCR client, my request bodies | none (`fr.sh` sets an env var) | 2 (+3 discovery) | ~6 | 0 | G4 |
| 5 Order Types | SCM | 2 | 2 | 0 | 0 | Route only (endpoint + client, no body recipe) | REST via FSCR client, my request bodies | none | 1 | ~2 | 0 | G4 |
| 6 Organization Customers | ERP | 2 | 2 | 0 | 0 | Partly (FBDI, self-blocked) | Own SOAP | `customers_soap.py` | 18 (6–8 together) | ~45 (6–8) | party create resent 3×, account 1× (each failed with nothing created) | none raised by SOAP (G7 noted) |
| 7 Person Customers | ERP | 2 | 2 (prefix only in create response) | 0 | 0 | No | Own SOAP | `customers_soap.py` | in 6 | in 6 | person create resent 2× | G7 |
| 8 Address Purposes | ERP | 6 | 6 | 0 | 0 | No (persons); FBDI only (orgs) | Own SOAP (in account create) | `customers_soap.py` | in 6 | in 6 | 0 | G7 |

Setup before module 1 (sign-in, mapping skills, new FSCR project and Run Book): about 20 active minutes and ~60 tool calls.

### 2. Totals

- **Total time:** 98 min wall clock; 51 min active (47 min waiting for sign-in).
- **Total records:** 24 = BU 2, price lists 2 (access sets counted inside them), payment terms 2, lookup types 2, lookup codes 4, order types 2, organization customers 2, person customers 2, address purposes 6.
- **FSCR end to end on a locally patched script: 2** (payment terms). The create path ran only FSCR skills and scripts, plus my blueprint and wrappers. The script had been patched on 2026-10-28; the unpatched original was not re-tested.
- **FSCR route and client with my own request bodies: 8** (2 lookup types, 4 lookup codes, 2 order types). FSCR gave the endpoint, client, discovery order and gates. The body fields and ModuleId are mine (section 3a).
- *(The earlier figure, "10 created by FSCR alone", was wrong and is replaced by these two lines.)*
- **Needed something I wrote on the create path: 14.** 2 BUs (my CSV builder), 10 customer records (my SOAP client) and, in the follow-up, 2 price lists (my REST call).
- **Could not be done: 0.** (Main run: 2 price lists, blocked on BU data access.)

**Data objects created and verified (A):**

| Type | Created | Verified | Source of verification |
|---|---|---|---|
| Business units | 2 | 2 (name, active, location, manager; default set not exposed) | `finBusinessUnitsLOV`, `hcmBusinessUnitsLOV` |
| Price lists / access sets | 2 / 2 (follow-up) | 2 / 2, 0 mismatches | `priceLists` GET with `expand=accessSets` |
| Payment terms | 2 | 2 | FSCR `reconcile` on fresh export |
| Payment term lines | 3 | 3 | same |
| Payment term discounts | 1 | 1 | same |
| Payment term translations | 2 | 2 | same |
| Payment term set assignments (ENTERPRISE) | 2 | 2 | same |
| Lookup types | 2 | 2 | REST GET |
| Lookup codes | 4 | 4 (FREIGHT stored `EnabledFlag N`) | REST GET |
| Order types | 2 | 2 (WARRANTY_SWAP stored `N`) | REST GET; 58 existing codes unchanged |
| Organization customers (party + account) | 2 | 2 | FSCR SOAP read + hub REST |
| Person customers (party + account) | 2 | 2 (prefix echoed only) | same |
| Addresses (location + party site + account site each) | 4 + 4 + 4 | all | same |
| Address purposes (site uses) | 6 | 6 | FSCR SOAP read |
| Oracle Run Book (FSCR control record) | 1 | 1 | FSCR `runbook_rest.py summary`: 2 of 5 tasks completed (BU, payment terms) |

**Oracle jobs and requests:**

| What | IDs | Rows processed / failed |
|---|---|---|
| BU template export | process 100004733440567, ESS 4431275 | – |
| BU import | UCMFA04523794, data-load request 4431286, FSM ESS 4431288, process 100004733440699 | BusinessUnit 2 / 0 |
| PT template / baseline / verification exports | 100004734412291 / 100004733439686 / 100004733439700 | – |
| PT import | UCMFA04523803, request 4431298, FSM ESS 4431301, process 100004733440709 | 3 objects / 0 failed |
| REST creates, main run | 8 POSTs succeeded (2 types, 4 codes, 2 order types; 8 `*_post_response.json` files) + 3 price-list POSTs rejected (00:59 FSCR client by id, 01:00 `rest_diag.py` diagnostic re-send by id, 01:01 by BU name; all HTTP 400) | 8 created / 3 rejected, nothing created |
| REST creates, follow-up 1 | 2 price-list POSTs (HTTP 201; `evidence/pricelists/pl1_create.json`, `pl2_create.json`) | 2 created / 0 rejected |
| REST status changes, follow-up 2 | 2 price-list PATCHes StatusCode→APPROVED (HTTP 200; `pl1_approve_a1.json`, `pl2_approve_a1.json`) | 2 changed / 0 failed |
| SOAP creates | 20 calls: 12 succeeded (4 createLocation, 4 createOrganization/createPerson, 4 createCustomerAccount) and 8 faulted, each creating nothing. The faults were 7 party creates (Kestrel 3, Caspian 2, Linnea 2) and 1 account create (Kestrel, SetCode). | 12 / 8 faulted |
| Run Book | WorkerJourneyId 300000394648040 | 5 tasks |

**Count method:** REST and SOAP calls were counted from the evidence files (`evidence/*_post_response.json`, `evidence/pricelists/*`, `evidence/customers/*_state.json`) and from the printed result lines of each call in this session's tool output. The tool output was needed because `customers_soap.py` overwrites its request/response files on each attempt, so faulted SOAP calls leave no separate file. The earlier figures "10 POSTs" and "7 faulted" were miscounts.

### 3. Skills used, and skills that did not exist

**FSCR files actually used:**
- **Routing and project:**
  - `router/implementation-router/SKILL.md` (Run Book gate)
  - `core/project-mgmt/project-workspace-initializer` (`initialize_project_workspace.py`, `create_project_runbook.py`)
  - `core/runbook` (`runbook_rest.py create-runbook`, `summary`)
- **Auth:** `core/auth/fusion-oauth-authentication` (`fusion_login.py`, `fusion_auth.py`)
- **Export and validation:**
  - `shared/setup-export/task-level-export` (`export_setup_task_csv.py`, 4 exports)
  - `shared/validation/setup-data-validator` (context only)
- **Import:**
  - `core/data-loader` (`upload_and_initiate.py` preflight + approved upload, `get_data_load_info.py`)
  - `core/data-loader/task-hook` (`task_hook.py data-load / build / approve / verify`)
- **Business units:** `pillars/erp/financials/organization-structures/manage-business-unit.md` + `ora-resource/*` (fill rules, lookups, gates)
- **Payment terms:** `pillars/erp/financials/customer-billing/manage-receivables-payment-terms` (`SKILL.md`, `payment_terms_fsm_package.py` preview/build/validate/reconcile, rule registry)
- **Lookups and order types:**
  - `pillars/scm/order-management/orders/manage-order-lookups/SKILL.md`
  - `core/fusion-api/apps-common/lookups` (`standard-lookups.md`)
  - `core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`
- **Price lists:** `pillars/scm/order-management/pricing/import-price-lists/SKILL.md` (route checked, not runnable)
- **Customers:** `pillars/erp/financials/customers/manage-customer-uploads`
  - `customers_package.py preview`, offline only: `OFFLINE_PREVIEW_LIVE_BLOCKED`
  - `customer_soap_read.py`, used for read-back

**Did not exist in FSCR:**
- A skill for AR_MANAGE_CUSTOMERS / AR_CREATE_CUSTOMER.
- Any person-customer support.
- A "Manage Price Lists" task.
- A BU package builder.
- A working sequence resolver (`task_to_skill_mapping.py` crashes).
- The price-list test file `tests/golden-scenarios.md` that the skill cites.

### 3a. Where each part of the 8 lookup and order-type records came from

FSCR files used (paths in `fscr-work/`):
- `core/fusion-api/apps-common/lookups/SKILL.md`: the discovery order Common → Standard → Generic → Set-enabled, the rule to approve before create, and no automatic retry.
- `core/fusion-api/apps-common/lookups/references/standard-lookups.md`: endpoints (lines 16 and 18) and client usage (`--method POST --body-file`). It says to "put the exact supported JSON body in a temporary file" but gives no fields.
- `core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`: the client that sent every POST.
- `pillars/scm/order-management/orders/manage-order-lookups/SKILL.md`: lists ORA_DOO_ORDER_TYPES as user-extensible, says to route to apps-common, and adds Oracle doc links. It has no write recipe and no fields.

| Records | Endpoint | Lookup view | ModuleId | Payload fields | Enabled flag |
|---|---|---|---|---|---|
| 2 lookup types (FSCRT_OUTDOOR_ACTIVITY_F01, FSCRT_CARRIER_SERVICE_TIER_F01) | FSCR: `standard-lookups.md:16` `POST /standardLookups` | **Mine.** FSCR's discovery order applies to existing lookups. For a new type I chose Standard because the OM lookup ORA_DOO_ORDER_TYPES was found there (read-only probes: commonLookups count 0, standardLookups count 1). | **Discovery**: copied `61ECAF4AAB00E990E040449821C61C97` from the existing ORA_DOO_ORDER_TYPES. That it means "Order Management" is *inferred*, not verified against a module table. | **Oracle describe** (`evidence/standardLookups_describe.json`: LookupType, ModuleId, Meaning, CustomizationLevel mandatory; Description, RestAccessSecured optional). The mappings CustomizationLevel U = "User" and "Authenticated" = `AUTH` are **mine**, with AUTH seen on the existing lookup. "Default" means the field was omitted, and Oracle stored SECURE. | n/a |
| 4 lookup codes (HIKING, PADDLING, STANDARD, FREIGHT) | FSCR: `standard-lookups.md:18` `POST /standardLookups/{LookupType}/child/lookupCodes` | follows the type | n/a | **Oracle describe** (child lookupCodes: LookupCode, Meaning, EnabledFlag mandatory with default Y; Description, Tag, DisplaySequence optional). STANDARD "(auto)" sequence was omitted: **my decision**. | **Mine**: Yes/No sent as `Y`/`N`. FSCR says nothing on it. Read back: FREIGHT = N. |
| 2 order types (FSCRT_SO_TRAIL_DEALER_F01, FSCRT_SO_WARRANTY_SWAP_F01) | FSCR: same `standard-lookups.md:18` with LookupType ORA_DOO_ORDER_TYPES | **FSCR procedure** (apps-common discovery order), run by me with read-only GETs | n/a (existing type) | **Oracle describe**, same fields as above | **Mine**: WARRANTY_SWAP sent `N`, read back N |

**Which FSCR skill gave a write recipe:** only `core/fusion-api/apps-common/lookups` (via `standard-lookups.md`), and only a partial one: method, endpoint, client command and gates, with no body schema. The Order Management pillar skill gave none. These 8 records are therefore labelled "FSCR route and client, my own request bodies", not "FSCR end to end".

### 4. Everything I wrote (all in `_fscr_run_01/scripts`)

| File | Size | What it does | Why FSCR's was not enough | Reusable? |
|---|---|---|---|---|
| `build_bu_package.py` | 2.1 KB | Fills FUN_BUSINESS_UNIT.csv in the fresh FSM template per FSCR's `ora_bulk_intake.md` rules | FSCR states the rules but ships no builder | Yes; values are hard-coded and should be parameterised |
| `customers_soap.py` | ~9 KB | Creates location (+DFF), organization or person party with site and usage, and customer account with site in a set plus purposes, via Oracle TCA SOAP; saves IDs after each step; never auto-retries | FSCR has no working customer create path; persons not covered | Yes; field order taken from the pod's own XSDs |
| `verify_customers.py` | ~5 KB | Field-by-field read-back of customers using FSCR's `customer_soap_read` plus hub REST | FSCR has no customer reconcile that works for this route | Yes |
| `taskhook_lifecycle.py` | 2.3 KB | Pipes JSON through FSCR Task Hook preview → approve → verify | FSCR documents the 3 commands but has no driver | Yes |
| `rest_diag.py` | 2.6 KB | REST GET/POST with FSCR token that decodes gzip error bodies | FSCR REST client prints gzip error bodies unreadably | Yes |
| `fr.sh` | 0.3 KB | Runs FSCR REST client with `MSYS_NO_PATHCONV=1` | Git Bash rewrites `/fscmRestApi/...` arguments | Yes |
| `token_status.py`, `token_lifetime.py` | <1 KB | Read-only token-cache expiry check (no token printed) | FSCR has no status command | Yes |
| `xsd_dump.py`, `fscr_customer_read.py`, `verify_lookups.py`, `ledger_add.py` | small | Schema discovery, FSCR read wrapper, lookup compare, ledger | Support only | Partly |

Data I wrote: `payloads/*.json` (lookups, price lists, customers), the payment-term blueprint `request.json`, the task mapping `identified-task-mapping-run01.json`, and Task Hook rule-result files.

### 5. Every failure

| # | What | Why | Tried | Outcome |
|---|---|---|---|---|
| 1 | Saved sign-in expired | 1-hour token, no refresh token | Ran FSCR login in background (user instruction) | OK at 00:43 |
| 2 | FSCR REST client error "valid HTTPS authority" | Git Bash path rewriting | `MSYS_NO_PATHCONV=1` | OK |
| 3 | Task Hook: "Task context must be the project's generated task-context.json." | Task Hook only accepts the project's generated task list; old project had only payment terms; editing it was not allowed | New FSCR project + Run Book via FSCR initializer | OK |
| 4 | FSCR export appended to an existing project file | `export_setup_task_csv.py` writes token-usage rows | Restored byte-exact; moved all FSCR runs to a copy | OK (original repo 0 changed files) |
| 5 | `task_to_skill_mapping.py` crash | `ModuleNotFoundError: No module named 'task_context'` | Sequence set by hand | Worked around |
| 6 | Price list POST 400 | "Attribute set with value 300000394664006 for BusinessUnitId in PriceListHeaderVO failed" (27011) and "The value of the attribute BusinessUnit isn't valid." | (1) FSCR FBDI: no FBDI loader objects in pod, template not in repo; (2) REST by id; (3) REST by name | **Not done.** Cause: no Pricing Administrator data access for `Configuration.TEST` on the new BUs (`dataSecurities` shows such grants for other BUs used in price lists, e.g. TESTBU4). A security grant is needed. |
| 7 | Transient DNS `getaddrinfo failed` (3 times) | Local network | Retried after `nslookup`; no request had been sent | OK |
| 8 | SOAP party create faults | Boolean flags sent as Y; missing party usage; person names and tax ID must be on PersonProfile | Fixed each and re-sent after confirming nothing was created | OK |
| 9 | SOAP account create fault | "JBO-27008: Attribute SetCode … cannot be set." | Used SetId | OK |
| 10 | FSCR `customer_soap_read` location read failed once with `CUSTOMER_SOAP_CORE_CALL_FAILED` (cause hidden by design) | Unknown (transient) | Re-ran; succeeded | OK |

### 6. Dependencies (order used: BU → lookups → order types → payment terms → price lists → customers → purposes)

| Dependency | Told by FSCR | Worked out by me |
|---|---|---|
| Reference set ENTERPRISE exists (BU, PT, access set, address set) | Yes (BU and PT dependency files) | |
| BU duplicate check by name | Yes | |
| BU location and manager must exist and be resolved | Yes (`ora_reference_lookups.md` GETs) | Location found via `/hcmRestApi/.../locations` because FSCR's `locationsLovV2` returned 0 rows |
| BU must be usable by Pricing | No | Yes: needs user data access (blocked) |
| Lookup codes need their type; disabled codes check | User brief | Created type first, codes one by one; read back enabled flags |
| Order types are codes in `ORA_DOO_ORDER_TYPES` (standard lookup) | Partly (listed as user-extensible) | View found by FSCR's discovery order |
| PT template + baseline from same pod/release; split-term choices | Yes | Choices made by me (D9) |
| Payment term name ≤ 15 characters | Yes, in `ora-resource/ora_input_validation.md:69` ("Enforce Name 15"). The earlier report missed it. | Confirmed in Oracle's describe: `paymentTermsLOV` Name maxLength 15 (`evidence/pt_limit/paymentTermsLOV_describe.json`). This LOV lists both FSCRT receivables terms. |
| CUSTOMER_RDS usable as address set | User brief | Accepted by Oracle (SetId 300000334604945) |
| Customer chain: location → party (+usage) → party site → account → account site → site uses | Partly (FSCR names "configured references") | Yes; party usage requirement found from Oracle error |
| Customer class codes exist | No | `PUBLIC SECTOR COMPANIES`, `FEDERAL` found |
| DFF segments for extra customer fields | Conditional mention | Found in pod XSDs (account DFF, location DFF) |

### 7. Permissions, approvals and sign-ins

| Gate | Raised by | What it asked | How handled |
|---|---|---|---|
| Sign-in | FSCR auth (expired cache) | Interactive Oracle login | I stopped once and asked you; then you told me to run it; I ran `fusion_login.py` in the background; callback in ~30 s; process exited by itself |
| G1 | Core Data Loader | "Reply with an approval to upload and initiate this exact validated load." (BU, PT) | Treated your written approval as the standalone approval |
| G2 | Task Hook / Run Book guard | Task must be in the project's generated task context | Created new FSCR project + Run Book (no existing file edited) |
| G3 | core.runbook | Run Book creation (FSCR: automatic after init) | Ran; Oracle Run Book created |
| G4 | apps-common lookups | "obtain explicit approval before any create" | Covered by your approval; payloads saved in `payloads/` |
| G5 | Payment terms skill | Design confirmation bound to design SHA-256 `5ef54bef…` | Recorded confirmation in blueprint (FSCR's mechanism) |
| G6 | Price list skill | Confirm APPROVED status | Covered by your approval; moot (not created) |
| G7 | none (own SOAP route) | – | Logged; my route has no FSCR gates; I ran duplicate checks and never auto-retried |
| Security blocker | Oracle pricing | BU data access for the signed-in user | Not attempted (security change prohibited for me) |
| Tool permission prompts | none denied | – | – |

### 8. Tokens and cost

| When | Source | Context tokens used | Plan 5-hour window | Weekly |
|---|---|---|---|---|
| Start (23:51) | app usage tool `get_usage` | 100,881 / 1,000,000 | 13% | 18% |
| After modules 1, 3, 4, 5 (01:03) | same | 357,640 | 34% | 22% |
| After modules 6–8 (01:23) | same | 448,119 | 48% | 24% |
| Now, after follow-ups 1 and 2 (2026-11-03 ~07:05) | same | 166,294 | 6% (a new 5-hour window, resets 07:19 +05:00) | 25% |

- **Start reading:** the first reading (100,881) was taken at the start, before any run work. It is the session's baseline (system prompt, tools, your brief), not run work.
- **Main run:** context grew from 100,881 to 448,119, so **347,238 were added during the run**. That is context-window size, not billed tokens. The plan 5-hour window went from 13% to 48% (**+35 points**) and weekly from 18% to 24% (**+6 points**). Those are plan-window percentages, not billed tokens.
- **Follow-up work (price-list creates, approvals and this correction pass):** its own line. The session was automatically summarized after the main run, so the context dropped. The present 166,294 is the size of the summarized context plus the follow-ups, and cannot be subtracted from 448,119. *Not verified* as a follow-up-only amount. The 5-hour window shows 6% of a new window that started after the main run (plan-window percentage); weekly rose from 24% to 25% (**+1 point**). Both are *inferred* to be mostly this follow-up, because other use on the account in the same window would also count.
- None of these figures is a billed-token or dollar count; no per-request figure was visible to me.

Proxy measures:
- **Tool calls:** about 200 in total. This is my approximate count from the session; I did not tally it exactly.
- **Files written in `_fscr_run_01`:** 205 files, 4.3 MB, excluding the repo copy. This includes about 1.4 MB of Oracle describe/XSD evidence. The new FSCR project folder is 180 KB.
- **FSCR text read:** about 350 KB of skill and rule files.

FSCR's own token-usage log is in the new project (`fscr-work/project/fscrt-run01-om-setup/artifacts/shared/token-usage/current/token-usage-log.md`). FSCR writes chars/4 estimates there automatically.

### 9. Where FSCR's documentation or code was wrong, outdated or contradictory against the pod

1. **Price Lists FBDI route** assumes FBDI business objects are registered in the Data Loader.
   - ETIA-TEST: 353 objects, 0 with ObjectType FBDI, none for price list or customers.
   - The skill also needs `PriceListsImportBatchTemplate.xlsm`, which is not in the repo.
   - It cites `tests/golden-scenarios.md`, which does not exist.
2. **Pricing BU readiness:** nothing in FSCR. The pod requires Pricing Administrator data access on the BU.
3. **BU reference lookups** list a ledger/legal-entity check ("A Business Unit create … requires a primary ledger and default legal entity"). The BU was created without either.
   - The declared `locationsLovV2` GET returned 0 rows without its finder.
   - The Default Set cannot be read back by any REST resource I could reach.
4. **Manage Order Lookups** lists only existing OM lookup types. Creating a new user lookup type with module Order Management is not covered, though the generic apps-common route worked.
5. **Shared setup-data validator** says it validates, but it only resolves context ("Task-local guidance files: 0. Fallback to Oracle documentation references is required.").
6. **Task export script** writes into an existing project file (token-usage log). The data-loader skill says not to create or update token-usage logs. The two are inconsistent, and the side effect is silent.
7. **Windows:**
   - Git Bash path rewriting breaks REST/SOAP path arguments.
   - pywin32 is invisible under `python -I`.
   - The FSCR REST client prints gzip error bodies undecoded.
   - None of this is documented.
8. **`task_to_skill_mapping.py`** fails to import `task_context`.
9. **Customers skill:**
   - The packager requires PARTY_NUMBER for a brand-new party.
   - It is organization-only.
   - The Sales-Tax-Inside-City-Limits 1/0 vs Y/N conflict is flagged but unresolved; Oracle SOAP stored `1`.
10. **Payment terms:** the original `payment_terms_fsm_package.py` hard-codes the business-object order [TERM, TRANSLATION, DISCOUNT, LINE]. ETIA-TEST declares [LINE, TERM, TRANSLATION, DISCOUNT], so the original failed here on 2026-10-28 (`payment_terms_object_order_mismatch`). This run used the locally patched copy and did not re-test the original. (Correction: the 15-character name limit *is* in the skill's `ora_input_validation.md:69`; the earlier report said it was not.)

### 10. Capability matrix

| # | Capability | Exercised in | Result | Evidence | Limits |
|---|---|---|---|---|---|
| 1 | Create setup | BU (FSM), PT (FSM), lookups/order types (REST) | 2 records FSCR end to end only **with a patch** (PT, local patch 2026-10-28; original not re-tested); 8 by FSCR route + client with my bodies; 2 BUs with my builder | Request IDs 4431286, 4431298; HTTP 201s | No create for price lists or customers in this pod |
| 2 | Understand/read environment | Exports, LOV GETs, Data Loader registry, dataSecurities, SOAP reads | Good; FSCR export + reads worked | Export ZIPs, read-back JSON | Some reads hide causes (`CUSTOMER_SOAP_CORE_CALL_FAILED`); BU default set not readable |
| 3 | Change/maintain existing setup | Not exercised in this run (rule 1: no changes to existing records) | – | – | The PT skill claims update/end-date; not tested |
| 4 | Plan and advise (routing, modes) | Task mapping, router Run Book gate, skill selection | Mixed: routing data present for all modules; resolver script broken; FBDI routes not checked against pod readiness | Steps 2–3 files | Sequence set by hand |
| 5 | Verify (read-back, reconcile, preview, gates) | PT reconcile, Task Hook, Data Loader preflight, FSM logs | Strong for PT (reconcile 0 mismatches) and FSM logs; BU partial; lookups via REST | `reconcile-result.json`, FSM logs | Shared validator does nothing; no price-list read-back in skill |
| 6 | Breadth and robustness | Errors, retries, recovery | Gates fail closed correctly; no unsafe auto-retries | Task Hook refusal, preflight approval stops | Tooling breaks on Windows; an export script edits an existing file silently |
| – | **Not yet tested** | – | – | – | Changing existing setup; understanding and explaining the environment across areas; repeat runs; other areas (pillars and modules outside these 8) |

### 11. Honest assessment

**What FSCR did well:**
- Where a skill has its own script (Receivables payment terms), FSCR ran the whole chain on this pod: export, preview, confirmation, build, validation, approval gates, import, re-export, reconcile. It proved the result with a field-level reconcile. **But this only worked with a patch:** the repo's script is the copy patched locally on 2026-10-28, because the original failed on this pod's object order. This run did not re-test the unpatched original.
- Its Data Loader and Task Hook gates are strict and behaved predictably: they stopped on a missing approval and on an unregistered task.
- Its generic REST route and client for lookups worked first time, but it supplies no request-body fields. I built those from Oracle's describe and an existing lookup.
- Its customer SOAP reader was useful for verification even though its create path is blocked.

**What it could not do:**
- Price lists: blocked by pod readiness (no FBDI loader objects, missing template) and by BU data access, which FSCR does not mention.
- Customers and persons: no create route.
- Business units: the route works but needs a file builder.

**FSCR versus me:**
- By record: 2 of 24 were FSCR end to end, and only on a locally patched script. 8 used FSCR's route and client with my request bodies. 14 needed my code (12 in the main run, plus the 2 price lists in follow-up 1 after you granted BU data access). Follow-up 2 approved the 2 price lists with my REST PATCH.
- By effort: much of the work was making FSCR runnable here: a new project and Run Book, Windows workarounds, error decoding, schema discovery for customers.

**Time without FSCR:** I cannot ground a comparison; I did not time any manual entry. The observed numbers are below.

| Module | FSCR elapsed (prep to verified) | Oracle processing time |
|---|---|---|
| Payment terms | ~7 min | ~1 min import |
| BUs | ~12 min, of which ~5 min was resolving the task-context gate | ~1 min import |
| Lookups and order types | ~2 min after discovery | seconds |

---

### B. Where we can take advantage (per module)

| Module | Area | Today | What a consultant must do first |
|---|---|---|---|
| Payment terms | ERP | **With a patch** (local order-check patch of 2026-10-28; the original failed on this pod and was not re-tested) | Sign in (1-hour token); have the project's Run Book include the task; decide print lead days, tax/freight and discount basis (FSCR asks); keep names ≤ 15 characters |
| Lookup types / codes / order types | SCM | **Route only** (FSCR endpoint and client; you supply the body) | Take ModuleId from an existing OM lookup; on Windows set `MSYS_NO_PATHCONV=1` |
| Business units | ERP | **With a patch** (CSV builder) | Add a builder; accept that the default set cannot be read back by REST |
| Price lists | SCM | **Not yet with FSCR** | Done in this run by my REST call, after Pricing Administrator data access was granted on the BU; approved by REST PATCH of StatusCode (FSCR has no route for it). For FBDI, Oracle's template and FBDI loader registration are needed |
| Organization customers | ERP | **Not yet** | Use a SOAP/REST create tool (like `customers_soap.py`) |
| Person customers, address purposes | ERP | **Not yet** | Same |

### C. Where it has holes (what to build, size, basis of estimate)

| Gap | Missing | What to build | Size | Basis |
|---|---|---|---|---|
| Customers (org + person + purposes) | No create route; FBDI-only skill is self-blocked | SOAP create adapter with FSCR-style preview/approval/reconcile | **Medium** | My working script took ~18 min with live debugging; adding FSCR gates, tests and DFF mapping per pod adds more |
| Price lists | No REST route; FBDI depends on pod and template; no BU access check | REST create + access-set child + pre-check of user BU data access + read-back | **Small–medium** | REST contract is in the pod describe; payload already built |
| BU builder | No package builder | Template filler following existing rules | **Small** | 60-line script written in this run |
| Pod readiness preflight | FBDI objects, data access, template presence not checked before routing | Readiness check skill | **Small** | Each check is 1–2 GETs used in this run |
| Windows robustness | Path rewriting, gzip error bodies, pywin32 under `-I` | Client fixes + docs | **Small** | Fixes used here are a few lines each |
| Side effects on existing files | Export script appends to project log silently | Make it opt-in or report it | **Small** | Single code path |
| Sequence resolver | Script crashes | Fix import | **Small** | ImportError only |
| Shared validator | No checks performed | Real CSV/metadata checks | **Medium** | Needs per-object rules |

### D. Where we found time savings (observed only)

- **Payment terms:** FSCR did export → preview → build → import → reconcile in about 7 minutes for two terms, with an automatic field-level proof (0 mismatches). Manual comparison: not measurable from this run.
- **Lookups and order types:** about 2 minutes for 8 records, including read-back. Manual comparison: not measurable from this run.
- **Business units:** 12 minutes, about 5 of which were FSCR gate overhead (task-context/Run Book). Not a saving on its own.
- **Customers and price lists:** no FSCR time saving; FSCR could not create them.

### E. Changes on the pod outside the run's own records

| Change | Made by | When | Detail |
|---|---|---|---|
| FSCR Run Book "FSCRT Run01 OM Setup" (WorkerJourneyId 300000394648040) | **FSCR** (`core/runbook/runbook_rest.py create-runbook`, run by me in the main run) | 2026-11-03 00:51 +05:00 | An Oracle record that FSCR creates automatically after project initialization. The name uses "FSCRT " with a space because FSCR derives it from the project name. Oracle shows 2 of its 5 tasks completed. |
| Pricing Administrator data access for `Configuration.TEST` on FSCRT_Quillon Ridge Outfitters West F01 and FSCRT_Brindle Harbor Marine Supply F01 | **You** (not me) | 2026-11-03, before 06:40 +05:00 | Granted so the price lists could be created. I made no security change. Effect seen: the same POST that was rejected at 00:59–01:01 succeeded at 06:43. *Not verified* by a separate read of the grant. |

### Files

- **Run records:** `input_records.md`, `ledger.md`, `ledger.csv`, `mapping.csv`, `step2_task_skill_map.md`, `step3_dependencies_and_order.md`
- **Scripts and data:** `scripts/`, `payloads/`
- **Evidence:** `evidence/` (FSM logs, REST/SOAP responses, read-backs)
- **FSCR working copy:** `fscr-work/`, including the new project `fscr-work/project/fscrt-run01-om-setup` with its exports, Task Hook runs and payment-term artifacts.
- **Original repo:** `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`, unchanged (6,117 files hash-identical to start). Only the restored token-usage log has a new timestamp; its content is identical.
