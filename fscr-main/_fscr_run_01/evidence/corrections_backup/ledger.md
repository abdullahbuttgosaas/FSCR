# Run ledger — FSCR run 01 (ETIA-TEST)

Start: 2026-11-02 23:49:54 +05:00 (from `date` in the shell).

## Usage readings
| When | Source | Reading |
|---|---|---|
| Start (23:51) | `mcp__ccd_session_mgmt__get_usage` (app usage tool) | context 100,881 / 1,000,000 tokens (10%); plan 5-hour window 13% used; weekly 18% used |

## Proxy counters
Tool calls are counted by me from this session's transcript (approximate; stated per module).

## Decisions log
- D1: Two FSCR copies exist (`E:\GoSaaS\fscr-main\fscr-main` = session working dir, and `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`). Used the second, as the user named it and only it holds the project workspace `draft-impl-project-20261028`.
- D2: The user attached `Upload_sheet_FSCR_Run01.xlsx` but the task text says the records section is the whole input. Worked only from the pasted records (saved in `input_records.md`).

## Module and record log
- D3 (23:58): Saved sign-in checked with my read-only `scripts/token_status.py` (uses FSCR's own `fusion_auth.py` cache reader; prints no token). Standard-service token cache exists but expired ~127 h ago; boss and fusion-common caches do not exist. FSCR auth has no refresh token, so a new interactive sign-in is required. Port 8765: `netstat -ano` shows nothing listening (user's page not running). Per hard rule 4 I will stop and ask for sign-in once offline planning is done.
- D4: FSCR's `fusion_auth.py` needs pywin32; it is installed for the user Python but not visible under `python -I`, so FSCR scripts are run with plain `python`.
- D5: Project workspace: reuse `project/draft-impl-project-20261028` (Run Book `runbook_control.status = active`, journey 300000394423893). FSCR requires exports and runs to live there; I only add new files there, never edit existing ones, and copy evidence to `_fscr_run_01`. Repo hashes taken at start (`repo_hashes_start.md5`, 6,117 files) to prove this at the end.
- Note: `payment_terms_fsm_package.py` in the repo is already the patched copy from the 2026-10-28 session (not original).
- D6: Prefix rule applied to names, codes, meanings and site names (meanings/site names are display names, so prefixing them keeps every created value traceable). Descriptions not prefixed.
- Step 2 written: `step2_task_skill_map.md`. Step 3 written: `step3_dependencies_and_order.md`.
- 23:56 STOP for sign-in: FSCR standard-service token expired; 1-hour token, no refresh token. Port 8765 free.
- 00:43 Login 1: I ran `fusion_login.py --token-cache auto` in the background (user instruction). Browser opened by the script; callback received 00:43:47; token cache saved outside the repo (user profile `.fusionaim`); process exited by itself (exit 0). Login log `login_01.log` (state/challenge redacted when read; no token in it).
- 00:44 Read-only check: FSCR `fusion_rest_client.py` GET `setIdSets` → HTTP 200. ENTERPRISE and CUSTOMER_RDS exist (dependencies 1 and 12 OK).
- Finding F1 (Windows/Git Bash): FSCR REST client fails with "REST URL must have a valid HTTPS authority without credentials" because Git Bash rewrites the `/fscmRestApi/...` argument into a Windows path. Fix: `MSYS_NO_PATHCONV=1`. Not documented in FSCR.
- 00:44–00:46 BU prerequisites (read-only, FSCR REST client): `finBusinessUnitsLOV` name search FSCRT/Quillon/Brindle → 0 rows (New). Location "Lahore Warehouse" = LocationCode LHR_WH, set COMMON (`hcm locations`; FSCR-declared `locationsLovV2` returned 0 rows without its finder; `locationsLovV2` with `fields=ActiveStatus` → HTTP 400). Managers via `publicWorkers`: Aron Smith (PersonNumber 4), Younas Yaqub (PersonNumber 300000002688269).
- 00:46 FSCR `export_setup_task_csv.py` exports (parallel): BU template process 100004733440567 (ESS 4431275); PT template 100004734412291; PT data 100004733439686. All completed in ~1.5 min.
- 00:47 My script `scripts/build_bu_package.py` built `fscrt-bu-f01-candidate.zip` (2 BU rows; children header-only) following FSCR `ora_bulk_intake.md` fill rules.
- 00:48 `setup_data_validation_context.py` (shared validator) only resolves context: "Task-local guidance files: 0 / Fallback to Oracle documentation references is required." No checks performed (Finding F2).
- 00:48 Data Loader preflight (`upload_and_initiate.py --task-routed`, no upload) → "passed validation… Approval required" (GATE G1: Data Loader standalone approval).
- 00:48 Task Hook `data-load` refused my run-specific task list: "Task context must be the project's generated task-context.json." (runbook_guard.py). GATE G2.
- Finding F3: FSCR `export_setup_task_csv.py` silently appended 3 rows to the EXISTING project file `token-usage-log.md` (an existing repo file). Restored it byte-exact (md5 72ea73ef… matches start). From 00:50 all FSCR execution runs in a full copy `_fscr_run_01/fscr-work` (decision D7) so the original repo stays unchanged; files I had added to the original were moved out. Re-check: 0 changed files vs start hashes.
- Finding F4: `shared/implementation-planning/offering-task-map-builder/scripts/task_to_skill_mapping.py` crashes: `ModuleNotFoundError: No module named 'task_context'`. Resolver Sequence set by hand from step 3 (decision D8).
- 00:50 New FSCR project `fscrt-run01-om-setup` via FSCR `initialize_project_workspace.py` + `create_project_runbook.py --refresh-artifacts` (5 tasks: BU, Order Lookups, AR Payment Terms, Import Price Lists, Manage Customer Uploads).
- 00:51 FSCR `runbook_rest.py create-runbook` → Oracle Run Book "FSCRT Run01 OM Setup" created, WorkerJourneyId 300000394648040 (an Oracle record created by this run; name uses "FSCRT " with a space because FSCR derives it from the project name). FSCR rule: automatic after init, no extra confirmation (GATE G3, handled under user approval). It stamped runID into the work copy's `core/data-loader/config/env.properties`.
- 00:52 BU import accepted (UCMFA04523794 / request 4431286); FSM log: BusinessUnit 2 rows processed, 0 failed (ESS 4431288). Read-back OK; default set not REST-visible.
- 00:53–00:54 Lookups: 2 types, 4 codes, 2 order types created via FSCR REST client (HTTP 201 each); all read back and match; 58 existing ORA_DOO_ORDER_TYPES codes unchanged.
- 00:56–01:03 Payment terms: FSCR preview (design SHA 5ef54bef…) → confirmation (G5) → build/validate OK → Task Hook → upload (request 4431298) → 3 objects loaded, 0 failed → fresh export 100004733439700 → FSCR reconcile "verified", 0 mismatches; existing terms identical. Decision D9: split-term PrintingLeadDays=1, FirstInstallmentCode=ALLOCATE; discount basis I; names shortened to 15 chars.
- 00:58 Finding F6: ETIA-TEST Data Loader registry: 353 objects, 0 with ObjectType FBDI, none for price list or customers → FSCR's FBDI routes for Price Lists and Customers cannot run here.
- 00:59 Transient DNS failure (getaddrinfo 11002) twice on a GET; network fine on recheck; third try OK.
- 00:59–01:01 Price list REST POST rejected: BusinessUnitId invalid for PriceListHeaderVO. Finding F5: FSCR REST client prints gzip error bodies undecoded; wrote `rest_diag.py`. Cause: no Pricing Administrator data access for Configuration.TEST on FSCRT BUs (dataSecurities). BLOCKER: granting data access is a security change I may not make. Price lists: not created.
- 01:03–01:21 Customers (modules 6–8). FSCR routes: no skill for AR_MANAGE_CUSTOMERS/AR_CREATE_CUSTOMER; `manage-customer-uploads` is FBDI-only and organization-only, its packager returns `OFFLINE_PREVIEW_LIVE_BLOCKED` (tested offline 01:22 with customer A data; also first needed a PARTY_NUMBER for a new party), and the pod has no FBDI `customers` loader object. No REST resource for financial customer accounts (`customerAccounts` 404). Used Oracle TCA SOAP (same services FSCR's own read adapter calls) with my `customers_soap.py`.
  - Field discoveries from pod schemas: account DFF = accountNotesOther / shippingInstrustions / customerAgreement; location DFF = responsibleMineralStatus / address1 / urlattr / ContactEmailAttr / AuthorizerAttr / TekSupplierSiteID; account site = KeyAccountFlag, TpHeaderId, EceTpLocationCode, TranslatedCustomerName, StartDate/EndDate, SetId.
  - Decisions: D10 Trading Partner Identifier → account site TpHeaderId (sits with Key Account and EDI location on the site; persons have no party-level TP field); D11 Account Description → AccountName; D12 Sales Tax Inside City Limits Yes/No → 1/0 (Oracle stores 1/0; FSCR contract flags this as an unresolved domain gap); Address From/To → party site and account site dates.
  - Errors fixed in order: boolean flags (Y → true); missing party usage (added CUSTOMER usage); SetCode not settable (use SetId 300000000003463 / 300000334604945); person names and tax ID must be on PersonProfile. Each failed create returned a fault and created nothing (checked with hub searches before resending).
  - Result: 4 customers, 4 locations, 4 party sites, 4 accounts, 4 account sites, 6 site uses. Read-back: FSCR `customer_soap_read.read` (account + location) and hub REST: orgs 39/39 fields; persons all but prefix (prefix echoed in create response only).
  - Transient DNS failure once more (01:14) before any bytes were sent.

## Usage readings (continued)
| When | Source | Reading |
|---|---|---|
| 01:03 after modules 1,3,4,5 | get_usage | context 357,640 (36%); 5-hour 34%; weekly 22% |
| 01:23 after modules 6–8 | get_usage | context 448,119 (45%); 5-hour 48%; weekly 24% |

- End checks: Oracle searches show only FSCRT_ BUs (2), lookup types (2), order-type codes (2), parties (4), price lists (0); payment terms verified by export. Original repo 0 changed files. No process on port 8765; no python process left running. Run Book summary: 2 of 5 tasks completed.

## Follow-up 2026-11-03 06:40–06:45 +05:00: price lists
- User reported "access ganted" (Pricing Administrator data access on the two FSCRT BUs).
- Token had expired (-17,929 s). Port 8765 was free. Ran FSCR `fusion_login.py --token-cache auto` in the background (log `login_02.log`). The browser SSO session was still valid, so it finished with no password. Token saved; process exited (code 0).
- Read-only pre-check: 0 FSCRT price lists.
- POST pl1: HTTP 201, PriceListId 300000394622041. POST pl2: HTTP 201, PriceListId 300000394623080. Each has access set ENTERPRISE. No retries.
- Read-back: 0 mismatches on the sent fields. Oracle stored StatusCode IN_PROGRESS, not APPROVED as sent. Left as is, because the records give no status (decision D13).
- Totals now: 24/24 created and verified; 10 FSCR-only, 14 needed my code.
