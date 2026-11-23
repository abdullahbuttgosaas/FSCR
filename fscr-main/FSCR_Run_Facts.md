# FSCR run facts (Runs 01–05)

Read-only lookup, 2026-11-03. Sources: the five run folders under `E:\GoSaaS\Configuration Automation v2.1\fscr-main\`, and this session's transcript, `C:\Users\PC\.claude\projects\E--GoSaaS-fscr-main-fscr-main\fdb8d1e2-ed83-470f-bab1-2a37235221e5.jsonl`. No Oracle call was made and no server was started.

---

## 1. Exact tokens

**Source:** the session transcript holds the usage that the API returned for each response: input, output, cache read and cache write tokens. All five runs are in this one session, model `claude-opus-5-5`, with no subagents.
- Each response was counted once (deduplicated by message ID).
- Each response was assigned to a run by its timestamp.
- The run start and finish times come from each run's `run_times.txt`.

**What is not in the counts:**
- The session was automatically summarized twice. The transcript records no token usage for those summarizing calls, so they are not counted.
- The run reports themselves recorded only context size and plan-window percentages from `get_usage`. They hold no billed token counts.

### Table A: from each run's start to the next run's start

This span includes each run's follow-ups and closing summary. Run 05 runs to the start of this lookup.

| Run | Window (+05:00) | API calls | Input | Output | Cache read | Cache write | Total |
|---|---|---:|---:|---:|---:|---:|---:|
| 01 Create | 11-02 23:49:54 → 11-03 07:10:16 | 299 | 610 | 234,137 | 78,388,615 | 550,175 | 79,173,537 |
| 02 Understand | 07:10:16 → 07:49:05 | 93 | 188 | 95,316 | 28,256,036 | 193,303 | 28,544,843 |
| 03 Change | 07:49:05 → 08:50:44 | 137 | 282 | 137,699 | 70,842,034 | 239,386 | 71,219,401 |
| 04 Create 16 | 08:50:44 → 09:40:15 | 115 | 232 | 120,133 | 85,183,257 | 193,044 | 85,496,666 |
| 05 Breadth | 09:40:15 → 12:23:23 | 23 | 48 | 25,102 | 19,760,472 | 41,314 | 19,826,936 |
| **All five** | | **667** | **1,360** | **612,387** | **282,430,414** | **1,217,222** | **284,261,383** |

### Table B: recorded start to recorded finish only

| Run | Window (+05:00) | API calls | Input | Output | Cache read | Cache write | Total |
|---|---|---:|---:|---:|---:|---:|---:|
| 01 | 23:49:54 → 01:27:29 | 228 | 460 | 175,164 | 67,566,080 | 374,566 | 68,116,270 |
| 02 | 07:10:16 → 07:34:37 | 87 | 174 | 89,843 | 25,865,684 | 185,534 | 26,141,235 |
| 03 | 07:49:05 → 08:49:18 | 133 | 272 | 132,854 | 68,290,536 | 232,029 | 68,655,691 |
| 04 | 08:50:44 → 09:24:59 ¹ | 110 | 220 | 115,024 | 81,036,683 | 178,012 | 81,329,939 |
| 05 | 09:40:15 → 10:08:20 | 18 | 38 | 16,743 | 15,393,196 | 32,292 | 15,442,269 |
| **All five** | | **576** | **1,164** | **529,628** | **258,152,179** | **1,002,433** | **259,685,404** |

¹ Run 04's finish is recorded only to the minute ("09:24"), so its window ends at 09:24:59.

**Notes:**
- Total is the sum of the four columns.
- One API call came 5 seconds before Run 01's recorded start. It totalled 78,335 tokens (input 2, output 751, cache read 48,185, cache write 29,397) and is in neither table.
- Run 01's window includes 47 minutes of waiting for sign-in.
- Run 03's window includes the gap between its main run (to 08:05:43) and its follow-up (08:24).
- The Run 05 report gives "about 30 (approximate)" tool calls. The transcript shows 22 tool calls in Run 05's recorded window.

---

## 2. Run 01: skills used for the 24 records

Sources: `_fscr_run_01\RUN_REPORT.md` (sections 1–4), `ledger.csv` and `mapping.csv`.

Every create also used these FSCR skills: the router (`router/implementation-router`), the project initializer (`core/project-mgmt/project-workspace-initializer`), the Run Book (`core/runbook`) and sign-in (`core/auth/fusion-oauth-authentication`).

| Object | Records | FSCR skill used | FSCR route or my code |
|---|---:|---|---|
| Business units | 2 | `organization-structures/manage-business-unit.md` + `task-level-export` + `core/data-loader` + Task Hook | FSCR route (FSM CSV), but **my code** built the file: `build_bu_package.py` |
| Payment terms (Receivables) | 2 | `manage-receivables-payment-terms` (`payment_terms_fsm_package.py`) + export + Data Loader + Task Hook | **FSCR end to end, on a script patched locally on 2026-10-28** (the original failed on this pod) |
| Lookup types | 2 | `manage-order-lookups` → `core/fusion-api/apps-common/lookups` (`standard-lookups.md`) + `fusion_rest_client.py` | FSCR route and client; **request bodies mine** |
| Lookup codes | 4 | same | FSCR route and client; **request bodies mine** |
| Order types | 2 | same (`ORA_DOO_ORDER_TYPES`) | FSCR route and client; **request bodies mine** |
| Price lists (+2 access sets) | 2 | `import-price-lists` (checked; FBDI only, could not run) | **My code:** REST POST (`rest_diag.py`) in a follow-up, after you granted data access; approved later by my REST PATCH |
| Organization customers | 2 | `manage-customer-uploads` (preview gave `OFFLINE_PREVIEW_LIVE_BLOCKED`; its `customer_soap_read` was used only to read back) | **My code:** `customers_soap.py` (SOAP) |
| Person customers | 2 | none (FSCR has no person-customer skill) | **My code:** `customers_soap.py` |
| Address purposes | 6 | none separately (created inside the customer account call) | **My code:** `customers_soap.py` |
| **Total** | **24** | | |

**Split** (the Run 01 report's own totals):
- FSCR end to end on a patched script: 2.
- FSCR route and client with my request bodies: 8.
- Needed my code: 14.

Payment terms also created child rows, which are not counted in the 24: 3 lines, 1 discount, 2 translations and 2 set assignments.

### Workbook rows and skills

**Run 01 did not use the workbook.** Its ledger says (decision D2): "The user attached `Upload_sheet_FSCR_Run01.xlsx` but the task text says the records section is the whole input. Worked only from the pasted records." The brief itself said: "this is the whole input; there is no workbook to find".

**What the workbook holds**, read for this lookup only (`E:\downloads\downloads 2.0\downloads 2.1\Upload_sheet_FSCR_Run01.xlsx`):
- Each data sheet has 3 header rows: a title, the column names and the hints.
- The records start on row 4.
- Most areas have 2 data rows, not 3.

The data rows hold the same records as the pasted text; I checked the first columns. If they had been used, they would map to these skills:

| Workbook sheet | Data rows | Records | Skill (as used in Run 01) |
|---|---|---:|---|
| Business Units | 4–5 | 2 | manage-business-unit + my builder |
| Price Lists | 4–5 | 2 | import-price-lists (not runnable) → my REST |
| Price List Access Sets | 4–5 | 2 | same (sent inside the price-list POST) |
| Payment Terms | 4–5 | 2 | manage-receivables-payment-terms |
| Payment Term Lines | 4–6 | 3 | same |
| Payment Term Sets | 4–5 | 2 | same |
| Lookup Types | 4–5 | 2 | manage-order-lookups → apps-common lookups |
| Lookup Codes | 4–7 | 4 | same |
| Order Types | 4–5 | 2 | same |
| Organization Customers | 4–5 | 2 | my `customers_soap.py` |
| Person Customers | 4–5 | 2 | my `customers_soap.py` |
| Address Purposes | 4–9 | 6 | my `customers_soap.py` |

The workbook also has a "Read me" sheet and a "Lists" sheet (dropdown values), with no records.

---

## 3. Run 02 and Run 03

### 3a. Run 02: reading 8 areas

Source: `_fscr_run_02_understand\RUN_REPORT.md`, section 2 scorecard.

| # | Area | Read end to end by FSCR? | What was or was not possible |
|---|---|---|---|
| 1 | Business units | Partly | The FSCR export gave the setup values, including the Default Set. User data access needed my own read (`dataSecurities`). Reference-group set assignments for the FSCRT BUs returned 0 rows (reason unclear). |
| 2 | Price lists | **No** | FSCR has no read route: the task has no CSV export and the skill is import-only. I read the headers with my own REST calls. The lines came back as 0 rows for every list; whether they are real or hidden is unclear. |
| 3 | Payment terms | **Yes** | FSCR export + FSCR `reconcile`: verified, 0 mismatches. |
| 4 | Lookup types and codes | **Yes** | FSCR export + FSCR REST client. What ModuleId means is inferred. |
| 5 | Order types | **Yes** | FSCR export + FSCR REST client. |
| 6 | Organization customers | Partly | FSCR's SOAP reader returned the account, site, site uses, DFF and location. It could not read the customer profile: it reported only `CUSTOMER_SOAP_HTTP_500`. My own read showed that no profile exists. |
| 7 | Person customers | Partly | Account level only; FSCR has no person reader. The name prefix was not readable by any route tried. |
| 8 | Address purposes | **Yes** | Read inside FSCR's `getCustomerAccount`. |

The 4 read end to end are 3, 4, 5 and 8. The report's summary text says "three areas" because it counts lookups and order types as one.

### 3b. Run 03: the 6 changes

Source: `_fscr_run_03_change\RUN_REPORT.md`, section 2, and `payloads\`. A seventh item, C7, was a read-only check of delete routes; nothing was deleted.

| # | Record | From → to | Result |
|---|---|---|---|
| C1 | Payment term FSCRT_D25B75AF1 (ENTERPRISE) | End date blank → 2028-12-31 | **Worked.** FSCR route with two deviations: a run config with a blank Run Book ID, and the locally patched script. Import request 4432070; reconcile 0 mismatches. |
| C2 | Lookup codes | FSCRT_STANDARD enabled Y → N; FSCRT_FREIGHT enabled N → Y; FSCRT_HIKING meaning "FSCRT_Hiking" → "FSCRT_Hiking and trekking", description blank → "Day hikes and multi-day treks" | **Worked** (FSCR route and client, my request bodies) |
| C3 | Order types | FSCRT_SO_TRAIL_DEALER_F01: end date blank → 2027-10-31, description → "Stock refills for trail dealers, retired after October 2027". FSCRT_SO_WARRANTY_SWAP_F01: enabled N → Y | **Worked** (FSCR route and client, my request bodies) |
| C4 | Business unit FSCRT_Brindle Harbor Marine Supply F01 | Manager Yaqub, Younas → Smith, Aron | **Refused by FSCR.** Nothing was sent to Oracle. |
| C5 | Price list FSCRT_Brindle Harbor Dock Equipment EUR F01 | Description "Dock and mooring equipment prices for European marinas" → same + ", 2027 season"; end date 2027-10-31 → 2027-09-30 | **Worked** (my REST PATCH; FSCR has no route). It stayed Approved. |
| C6 | Customers | Kestrel account description "Buying cooperative for trail shops" → "Buying cooperative for trail and outdoor shops". Linnea shipping instructions "Leave with neighbour if absent" → "Leave with neighbour at No. 90 if absent" | **Worked** (my SOAP `updateCustomerAccount`; FSCR's only route is FBDI) |

**FSCR's exact rule that refused C4**, from `pillars/erp/financials/organization-structures/ora-resource/`:
- **`ora_input_validation.md`, line 28:** "Exact BU lookup returns one candidate but any comparable desired field differs from current saved-state evidence | Classify as `existing-different`; block creation and require an explicit update decision or a different BU name."
- **`ora_input_validation.md`, line 55, rule BU.IDEMPOTENCY:** "new->BU.READY;existing-identical->BU.NOOP;existing-different->BU.BLOCKED;ambiguous->BU.BLOCKED"
- **`ora_rule_registry.json`, line 218:** `"existing-different": "BU.BLOCKED"`
- **Task Hook response** (`evidence\gate\c4_preview.json`): "Preview is blocked until user corrections are supplied and all rules pass: ora_input_validation.md."

---

## 4. Code files I wrote

**Method:** the files listed are the ones that exist in each run's `scripts\` folder, so this is a count of files found. Each run report also lists its scripts in an "Everything I wrote" section.
- **Run 04 mismatch:** its report says "9 scripts", but 8 files exist in its `scripts\` folder.
- **Total:** 48 files in `scripts\` folders, with 39 distinct names. Run 03 re-used 6 files from earlier runs, Run 04 re-used 2, and Run 05 re-used 1, re-pointed to their own run.
- **Separate from the 48:** 1 config file and 4 copies of FSCR files in Run 04's `patches\` (listed at the end).

**Run 01 (14)**

| File | Purpose |
|---|---|
| build_bu_package.py | Fills the business-unit CSV in FSCR's template |
| customers_soap.py | Creates customers (location, party, account, site, purposes) by SOAP |
| verify_customers.py | Reads customers back field by field |
| taskhook_lifecycle.py | Runs FSCR Task Hook preview → approve → verify |
| rest_diag.py | REST GET/POST that decodes gzip error bodies |
| fr.sh | Runs FSCR's REST client with the Git Bash path fix |
| token_status.py | Checks token expiry without printing it |
| token_lifetime.py | Checks token lifetime without printing it |
| xsd_dump.py | Reads Oracle SOAP schemas |
| fscr_customer_read.py | Wrapper for FSCR's customer reader |
| verify_lookups.py | Compares lookups after create |
| ledger_add.py | Adds ledger rows |
| fix_ledgers_followup2.py | One-off correction of ledgers after follow-up 2 |
| fix_report_followup2.py | One-off correction of the report after follow-up 2 |

**Run 02 (7)**

| File | Purpose |
|---|---|
| rget.py | GET-only REST helper with paging |
| soap_read.py | Read-only SOAP helper that shows Oracle's fault text |
| fscr_cust_read2.py | Calls FSCR's customer reader and saves the output |
| fr2.sh | GET-only wrapper for FSCR's REST client |
| diff_exports.py | Local diff of two export ZIPs |
| analyze.py | Per-area facts and cross-area links |
| coverage_scan.py | Scans skill folders for read routes |

**Run 03 (15; 6 re-used: rget, soap_read, fscr_cust_read2, fr2.sh and diff_exports from Run 02, taskhook_lifecycle from Run 01)**

| File | Purpose |
|---|---|
| rmut.py | One whitelisted price-list PATCH |
| soap_update.py | Whitelisted customer-account SOAP update |
| build_bu_update.py | Business-unit update CSV |
| snapshot.sh | Whole-area before/after reads |
| diff_areas.py | Whole-area REST diff |
| diff_accounts.py | Field diff of customer-reader XML |
| fetch_export_result.py | Downloads an already-started export |
| update_report_followup.py | One-off report update |
| amend_report_part4.py | One-off: applies amendments A1–A7 to the report |
| + the 6 re-used files | as in Runs 01–02 |

**Run 04 (8; 2 re-used: diff_exports, fetch_export_result)**

| File | Purpose |
|---|---|
| adapter_run.py | Runs one FSCR adapter's offline steps unchanged |
| live_run.py | Runs FSCR's live chain one stage per call |
| survey16.py | Surveys the 16 adapter skills |
| build_task_mapping.py | Builds the task-mapping file (FSCR's resolver crashes) |
| inspect_candidate.py | Facts about a candidate ZIP for the rule results |
| export_all.sh | Template and data export per task |
| + the 2 re-used files | as in Run 03 |

**Run 05 (4; 1 re-used: export_all.sh from Run 04)**

| File | Purpose |
|---|---|
| sample40.py | Seeded sample of 40 skills |
| analyze40.py | Grades the 40 skills by fixed rules |
| compare_fields.py | Compares skill field names with template columns |
| export_all.sh | Template and data export per task |

**Not counted in the 48:**
- `_fscr_run_03_change\run-config-blank.properties`: a config file with a blank Run Book ID.
- Run 04 `patches\`:
  - patched copies of FSCR's `ap-payment-terms\fsm_task_adapter.py` and `remit-to\fsm_task_adapter.py`;
  - a patched copy of `receipt-classes\e2e-adapter.json`;
  - an unchanged copy of `remit-to\remit_identity.py`.
