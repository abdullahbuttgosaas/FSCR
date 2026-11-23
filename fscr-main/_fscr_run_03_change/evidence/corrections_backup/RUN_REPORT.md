# FSCR Test 4b (Run 03): can FSCR change and maintain existing setup?

Pod ETIA-TEST (release 11.13.26.10.0). Main run 2026-11-03 07:49:05–08:05:43 +05:00 (17 min). Follow-up for C1/C4 after your Task Hook permission: 08:24–08:31 (7 min). **Total 24 min.**
**Limits:** one pod, one release, two FSCRT records per module (one or two changed per area), one user (Configuration.TEST). **ERP** = Financials, **SCM** = Order Management.

---

## 1. One page for practice leads

**What FSCR could change here:** lookups and order types (SCM), through its documented REST route and its own client.
- **C2:** disabled one lookup code, enabled another, and changed a third code's meaning and description.
- **C3:** end-dated one order type and changed its description, and enabled another.
- **Verified:** whole-area diffs show only the requested fields changed.
- **Caveat:** FSCR supplied the endpoint, client and approval rule. The request bodies were mine (as found in Run 01).

**Payment terms (C1, ERP): changed end to end through FSCR, after you allowed the Task Hook step.**
- FSCR's script really supports `end-date`, despite the manifest marker listing only "create, update".
- It produced a correct, minimal candidate: only EndDateActive changes, 86 fields preserved, no rows touched.
- The route ran: preview → design confirmation → build/validate → Data Loader preflight → Task Hook (rule plan, my evaluated rule results, preview → approve → verify) → approved upload → import (request 4432070: 3 objects, 0 failed) → fresh export → FSCR `reconcile` verified, 0 mismatches.
- Whole-area diff: only that end date changed.

**Business unit (C4, ERP): blocked by FSCR's own rule, not by me.**
- The BU rule registry has **no update path**. Its idempotency node sends an existing BU that differs from the request to BLOCKED ("require an explicit update decision or a different BU name"). The only success outcome is a *new* BU.
- The Task Hook refused: "Preview is blocked until user corrections are supplied and all rules pass: ora_input_validation.md."
- FSCR allows this only with an explicit user waiver of that validation, which you have not given. Nothing reached Oracle.

**History of the Task Hook gate:** in the main run, the session's permission system blocked my writing of the Task Hook rule results ("Security Weaken") before anything reached Oracle. You then allowed it, add-only, in Run 01's project folder (see section 6).

**Detail from the main run, kept for the record:**
- **C1 payment term end-date:** FSCR's script really supports `end-date`, despite the manifest marker listing only "create, update". It produced a correct, minimal candidate: only EndDateActive changes, 86 fields preserved, no rows touched. The candidate passed FSCR validation and the Data Loader preflight.
- **C4 BU manager:** FSCR states update rules but has no builder, so I wrote one. The candidate passed the Data Loader preflight.
- **Why neither finished:** the next mandatory FSCR step is the Task Hook. There the agent writes `rule-results.json`, stating which of FSCR's rule files passed. This session's permission system **blocked** my write of that file ("Security Weaken"). Its concern: an agent grading its own safety checks. I did not work around it. Neither change reached Oracle.
- **Practice-lead takeaway:** FSCR's governance relies on the AI agent attesting rule compliance itself. That step is exactly what a cautious control layer blocks.

**What FSCR cannot change:**
- **Price lists (C5, SCM):** no route; the only skill is an FBDI import that can't run here. I changed it with my own REST PATCH. Oracle let me edit the **Approved** list directly, and it stayed Approved.
- **Customers (C6, ERP):** the only route is FBDI, which is blocked in this pod. I changed both with my own SOAP `updateCustomerAccount`.

**Delete check (C7, read only):**
- FSCR documents REST **DELETE** for lookup types and lookup codes, which covers order types.
- It has none for business units, price lists, customers or payment terms; payment terms explicitly refuse hard delete.
- Nothing was deleted.

**What I wrote:** 7 new small scripts (about 15 KB) plus 6 reused helpers from Runs 01 and 02. Two whitelisted write helpers (price list, customers), a BU update builder, snapshot and diff tools, and an export-result fetcher. Section 4 lists them.

**Result: 5 of 6 changes made and verified (C1, C2, C3, C5, C6). C4 not done (FSCR rule: no BU update path). No change outside the named records** (verified by whole-area before/after diffs, after the main run and again at the end).

---

## 2. Scorecard per change

| # | Change | Area | FSCR route | Own call | Final status | Side effects | Oracle IDs |
|---|---|---|---|---|---|---|---|
| C1 | FSCRT_D25B75AF1 end date 2028-12-31 | ERP | **Yes, end to end**: PT skill end-date → preview/build/validate → Data Loader → Task Hook → upload → reconcile | rule results written by me (Task Hook design) | **Changed and verified** (follow-up) | none (16 other terms identical; Run Book unchanged) | request 4432070, ESS 4432071, FSM 100004733447103; export 100004734412650 |
| C2 | FSCRT_STANDARD off, FSCRT_FREIGHT on, FSCRT_HIKING meaning + description | SCM | Yes: apps-common lookups, FSCR client PATCH | body only | **Changed and verified** | none | 3 × HTTP 200 |
| C3 | FSCRT_SO_TRAIL_DEALER_F01 end 2027-10-31 + description; FSCRT_SO_WARRANTY_SWAP_F01 on | SCM | Yes: manage-order-lookups → apps-common, FSCR client PATCH | body only | **Changed and verified** | none (58 other codes identical) | 2 × HTTP 200 |
| C4 | Brindle BU manager → Smith, Aron | ERP | **No update path**: registry BU.IDEMPOTENCY existing-different → BLOCKED; builder mine | `build_bu_update.py` | **Not done**: Task Hook refused preview (FSCR rule) | none (nothing sent) | exports 100004734412594, 100004734402958 |
| C5 | Brindle price list description + end 2027-09-30 | SCM | **None** | `rmut.py` PATCH | **Changed and verified**; edited while Approved, stayed Approved | none (54 other lists identical) | PATCH HTTP 200 on 300000394623080 |
| C6 | Kestrel Account Description; Linnea Shipping Instructions | ERP | **None runnable** (FBDI blocked) | `soap_update.py` | **Changed and verified** | none | 2 × updateCustomerAccount HTTP 200 |
| C7 | Delete/end-date route check | ERP+SCM | read only | – | done | – | – |

### Details per change

**C1 payment term (ERP)**
- **Before:** EndDateActive blank.
- **What FSCR did:**
  - Request: `{"action":"end-date","header":{"Name":"FSCRT_D25B75AF1","SetCode":"ENTERPRISE","EndDateActive":"2028-12-31"}}`.
  - Preview, designSha256 06089bee…: EndDateActive '' → 2028-12-31. FSCR also canonicalized the StartDateActive format (2026/11/02 → 2026-11-02, same date) and preserved 86 fields.
  - Candidate sha256 b2425e01…: 1 header, 2 lines, 1 translation. Validate: importEligible true, 0 errors.
  - Data Loader preflight: "passed validation. No data was uploaded."
- **Main run:** stopped at the Task Hook rule results (permission denied); export 100004733440780 identical to before.
- **Follow-up:**
  - Ran in Run 01's project; Task Hook `data-load` gave the rule plan; I evaluated all 6 rule files (all passed, with node evidence).
  - Preview → approve → verify, then approved upload: request 4432070, status Succeeded, 3 objects, 0 failed. FSM log: "A total of 1 rows were processed. 0 rows of them failed".
  - Fresh export 100004734412650: only EndDateActive '' → 2028/12/31. FSCR reconcile: verified, 0 mismatches.
- **Status:** changed and verified.

**C2 lookups (SCM)**
- STANDARD EnabledFlag Y→N.
- FREIGHT N→Y.
- HIKING Meaning "FSCRT_Hiking" → "FSCRT_Hiking and trekking"; Description null → "Day hikes and multi-day treks".
- Verified by REST read and by FSCR export 100004733440794.

**C3 order types (SCM)**
- TRAIL_DEALER: EndDateActive null → 2027-10-31; Description changed.
- WARRANTY_SWAP: EnabledFlag N→Y.
- Verified by REST (all 60 codes) and by export.

**C4 BU (ERP)**
- **Before:** manager Yaqub, Younas; Status A; location LHR_WH; set ENTERPRISE.
- **Package:** only the manager columns differ; Active kept at A.
- **After:** BU export and LOV unchanged.
- **Not verified:** whether Fusion's BU CSV import would replace the manager or add a second one.
- **Follow-up:** the rule evaluation gives BU.IDEMPOTENCY = existing-different → BU.BLOCKED. Recorded as `blocked`, not overridden; no user waiver was given. The Task Hook refused the preview. Not done; the manager is unchanged in the final snapshot.

**C5 price list (SCM)**
- **Before:** Approved; ends 2027-10-31.
- **Request:** PATCH `{"PriceListDescription":"…, 2027 season","EndDate":"2027-09-30T23:59:59+00:00"}`, HTTP 200.
- **After:** Approved, new description, ends 2027-09-30.
- **Approval status:** Oracle **did not** require moving the list back from Approved, so no status change was made.

**C6 customers (ERP)**
- Kestrel AccountName "Buying cooperative for trail shops" → "Buying cooperative for trail and outdoor shops".
- Linnea DFF shippingInstrustions "Leave with neighbour if absent" → "Leave with neighbour at No. 90 if absent". The other two DFF segments were sent unchanged and are verified unchanged.
- Verified with FSCR's customer reader by full XML diff (156 and 119 fields).

---

## 3. Skills used and skills that did not exist

**Used:**
- `pillars/erp/financials/customer-billing/manage-receivables-payment-terms` (`payment_terms_fsm_package.py` validate/preview/build)
- `core/data-loader` (`upload_and_initiate.py` preflight, approved upload with `--run-config`; `get_data_load_info.py`)
- `core/data-loader/task-hook` (`task_hook.py data-load`, `build-data-load-preview`, `approve-data-load-preview`, `verify-approved-data-load-archive`)
- `core/fusion-api/apps-common/lookups` + `core/fusion-api/rest-api-client` (`fusion_rest_client.py` PATCH)
- `pillars/scm/order-management/orders/manage-order-lookups` (routing and category rules)
- `pillars/erp/financials/organization-structures` (BU update rules, declared GET `publicWorkers`)
- `shared/setup-export/task-level-export` (8 exports)
- `shared/setup-export/fsm-csv-export` engine (`download_result`)
- `shared/baseline-assessment/setup-compare/task-level-compare` (once)
- `pillars/erp/financials/customers/manage-customer-uploads` (`customer_soap_read` for read-back)
- `core/runbook` (`runbook_rest.py summary`, read)
- `core/auth` (login)

**Did not exist or could not run:**
- Price-list update.
- Customer update outside FBDI.
- BU package builder.
- A BU **update** path in the rule registry (create-only).
- A way to resume an export by process ID.
- An offline general compare (FSCR's compare uploads to Oracle).
- Any compare for price lists or customers.

## 4. Everything I wrote (`_fscr_run_03_change/scripts`)

| File | Size | Why |
|---|---|---|
| `rmut.py` | 2.1 KB | Single whitelisted PATCH (Brindle price list only); FSCR has no price-list update |
| `soap_update.py` | 3.4 KB | Whitelisted `updateCustomerAccount` (Kestrel, Linnea only); FSCR's customer route is FBDI-only |
| `build_bu_update.py` | 2.3 KB | BU update CSV from the fresh template (FSCR rule BU.NO_FULL_DATA_EXPORT); FSCR has no builder |
| `snapshot.sh` | 1.8 KB | Whole-area before/after reads |
| `diff_areas.py` | 2.7 KB | Whole-area REST diff incl. audit-only changes |
| `diff_accounts.py` | 1.4 KB | Field-level diff of FSCR customer-reader XML |
| `fetch_export_result.py` | 1.2 KB | Download an already-started export through FSCR's engine (avoids a second export) |
| `update_report_followup.py`, `run-config-blank.properties` | 8 KB / 0.1 KB | One-off report update; Data Loader run config with blank runID (passed via `--run-config`, so Run 01's env.properties stayed unedited) |
| *Reused from Run 02, re-pointed:* `rget.py`, `soap_read.py`, `fscr_cust_read2.py`, `diff_exports.py`, `fr2.sh` | – | Reads and diffs |
| *Reused from Run 01:* `taskhook_lifecycle.py` | – | Task Hook driver (not reached) |

## 5. Failures

| What | Exact text | Handling |
|---|---|---|
| Task Hook rule results (C1, C4) | Permission classifier: "Permission for this action was denied … Reason: [Security Weaken]" | Not worked around. C1 and C4 not done |
| C1 preflight | "Project root is not available: \e\GoSaaS\…" | My POSIX path; one retry with a Windows path: OK |
| C1 validate | "the following arguments are required: --package" | My CLI misuse; corrected |
| C2 first attempt | "[Errno 2] No such file or directory: '…payloads$f.json'" | My shell quoting; nothing sent; one retry: OK |
| C4 build | "can't open file 'E:\\e\\GoSaaS\\…build_bu_update.py'" | My path; nothing built; one retry: OK |
| Follow-up reconcile | "A readable ZIP file is required: …$(basename …)" | My shell quoting; re-run once: verified |
| Follow-up C4 Task Hook | "Preview is blocked until user corrections are supplied and all rules pass: ora_input_validation.md." | FSCR rule (no BU update path); stopped |
| After lookups export | "Failed calling …SetupTaskCSVExportProcess/100004733440794 … [Errno 11002] getaddrinfo failed" | Process had started in Oracle; file fetched with FSCR's `download_result` |

## 6. Permissions and sign-ins

| Gate | Raised by | Handling |
|---|---|---|
| Sign-in | FSCR auth (token expired at start) | Ran `fusion_login.py --token-cache auto` in the background after checking port 8765 was free. Your browser was still signed in, so no password was needed. Process exited |
| G-C1a design confirmation | PT skill ("ask the customer to reply exactly confirm") | Your approval recorded as the confirmation (blueprint carries design SHA) |
| G-C1b, G-C4 Data Loader approval | "Reply with an approval to upload and initiate this exact validated load." | Not used: the Task Hook step before it was blocked |
| **G-TH Task Hook rule results** | FSCR Task Hook: `data-load` returns `ready` with "checks have not yet run"; the caller must execute the rule plan and supply `ruleResults` before preview | **Main run:** the session's permission classifier denied the write ("Security Weaken"); **the gate stopped before anything reached Oracle**. **Follow-up:** you allowed add-only files in `_fscr_run_01/fscr-work/project/fscrt-run01-om-setup`. C1: 6 rule files evaluated, all passed. C4: `blocked` |
| Task Hook approve-data-load-preview | FSCR ("Only after explicit user approval") | C1: your C1 approval |
| Data Loader standalone approval (C1) | "Reply with an approval to upload and initiate this exact validated load." | Your C1 approval: approved upload (request 4432070) |
| G-C2, G-C3 | apps-common lookups "obtain explicit approval before any create, update, or delete" | Covered by your approval |
| C5, C6 | none (own calls) | Whitelisted helpers; no Oracle prompt |
| Run Book | Data Loader sends `runID` when configured, and Fusion then updates the Run Book's task status | `runID` blanked in my copy (D2). Run Book verified unchanged (2 of 5 complete) |

## 7. Stats and token proxy

**Oracle requests and records created:**
- 8 setup exports: PT 100004733446385, 100004733440767, 100004733440780; BU 100004734412594, 100004734402958, 100004733447091; lookups 100004733446425, 100004733440794.
- 1 FSCR compare: file blobs 100004733439804 and 100004733440796; uploads 100004733446477 and 100004733440805; compare 162140984.
- Writes: 5 REST PATCHes through FSCR's client (C2, C3), 1 own REST PATCH (C5), 2 own SOAP updates (C6), and **1 FSCR Data Loader import (C1)**: UCMFA04524480, request 4432070, ESS 4432071, FSM 100004733447103.
- Follow-up export: 100004734412650 (PT after C1).
- Reads: about 20 REST GETs (approximate) and 12 SOAP reads through FSCR's customer reader.

**Proxy measures:**
- Tool calls: about 75 (my approximate count).
- Files written: 106 files, 2.6 MB, excluding the 86 MB FSCR copy.
- FSCR files read: about 30.

| When | Source | Context size | 5-hour plan window | Weekly |
|---|---|---|---|---|
| Start 07:49 | app `get_usage` | 404,257 | 12% | 28% |
| End of main run 08:04 | app `get_usage` | 514,007 | 27% | 31% |
| End of follow-up 08:30 | app `get_usage` | 579,051 | 37% | 33% |

- Context added: **109,750** in the main run plus **65,044** in the follow-up (174,794 in total). That is context-window size, **not billed tokens**. The start figure already included Runs 01 and 02.
- The 5-hour window rose 15 points (same window, no reset) and weekly 3 points. These are plan-window percentages and may include other use on the account.

## 8. Where FSCR's docs were wrong or silent

1. **PT manifest vs text:** the marker says `fscr-supported-operations: create, update`. The text and the script support `end-date` too; the script works.
2. **BU:**
   - No builder for updates.
   - The rule `BU.NO_FULL_DATA_EXPORT` forbids using a full BU export as source, while Run 02 showed the export is the only route that reads the Default Set.
   - The docs are silent on whether a manager change via CSV replaces or adds a manager.
3. **Price lists:**
   - Silent on editing an existing list.
   - Silent that Oracle allows editing an Approved list directly. Only FBDI status setting is described.
4. **Customers:** update exists only as FBDI. Silent on the pod readiness that blocks it (Run 01).
5. **Data Loader `runID`:** the docs say it makes Fusion update Run Book task status. That is a side effect on a record outside the setup being changed, and it is not surfaced to the user as a change.
6. **Export script:** has no resume-by-process-ID option. A lost poll means either a second export or own code.
7. **Compare:** "task-level compare" requires uploads and an Oracle compare process. Silent that this creates Oracle records.
8. **Task Hook:** depends on the agent writing its own rule-pass attestations (`rule-results.json`); FSCR does not compute them itself. Run 01 skipped the `data-load` plan step that the Task Hook skill requires. The follow-up ran it.
9. **BU skill:** the text and intake mention "Create or update intent", but the executable rule registry only reaches READY for a **new** BU. An update is BLOCKED unless the user waives the validation. This contradiction is not called out in the skill.
10. **Data Loader:** deletes its single-use preflight and Task Hook envelopes after upload, and writes status logs to `C:\Users\PC\.codex\data-loader-status-logs\` outside the repo. Neither is stated where the files are requested.

## 9. Capability matrix

| Capability | Area | Tested | Result | Evidence | Limits |
|---|---|---|---|---|---|
| Create | – | not exercised (Run 01) | – | – | – |
| Understand | – | Run 02 | – | – | – |
| **Change** | Lookups, order types (SCM) | yes | FSCR route works; 5 changes verified | `evidence/C2`, `C3`, export diff | bodies supplied by me |
| **Change** | Payment terms (ERP) | yes | **Works end to end** once the Task Hook rule results may be written: minimal end-date import, 0 failed, reconcile verified | `evidence/C1`, `evidence/gate` | Task Hook relies on agent-written rule results |
| **Change** | Business unit (ERP) | yes | **No update path** in FSCR's BU rule registry; Task Hook refused | `evidence/gate/c4_preview.json` | create-only unless the user waives |
| **Change** | Price lists (SCM), customers (ERP) | yes | no FSCR route; own calls worked | `evidence/C5`, `C6` | all own |
| **Verify** | All areas | yes | FSCR export diff + FSCR compare (PT, 0 mismatches) + FSCR `reconcile` after C1 (verified) + FSCR customer reader; whole-area diffs mine | `evidence/diff_*`, `evidence/compare` | FSCR compare writes to Oracle; none for price lists or customers |
| Plan and advise | – | not exercised here | – | – | – |
| Breadth | 6 areas | yes | 3 of 6 changed through FSCR routes (C1, C2, C3); 1 blocked by FSCR rule (C4); 2 none (C5, C6) | this report | one pod |
| Delete (C7) | 5 object types | static | DELETE documented for lookup types and codes only | ledger C7 table | not executed |

## 10. Honest assessment

**FSCR versus my work:**
- **Changed through FSCR:** C2 and C3 (5 field changes). FSCR gave the route, client, approval rule and an export to verify. I wrote the request bodies.
- **C1 changed through FSCR end to end** (follow-up): the payment-term route is FSCR's strongest. It is minimal, preserves the baseline, validates itself and reconciles after import. My part was the request, the rule evaluation the Task Hook requires the agent to write, and a run-config with blank runID to keep the Run Book unchanged.
- **C4 is not possible through FSCR as written:** the BU rule registry is create-only. FSCR stops an update unless the user explicitly waives the validation.
- **No FSCR involvement:** C5 and C6 (own calls); FSCR's reader was used only to verify C6.
- **Verification:** whole-area diffs, account XML diffs and the export-result fetch are mine. FSCR's compare ran once and correctly reported no difference (C1 never imported).

**Nothing outside the named records changed.**
- Verified by before/after diffs: 17 payment terms, 183 BUs, 6 lookup types and 68 codes, 60 order types, 55 price lists, 4 FSCRT accounts, 212 site rows, and the FSCRT parties. Re-checked after the follow-up (final snapshot at 08:29 and PT export diff).
- The FSCR Run Book is unchanged.
- The new Oracle records are the 9 export processes, the compare's blobs, uploads and process, and the C1 import (request 4432070).
- **Run 01 files:** only the 10 new files listed in the ledger were added; every pre-existing Run 01 file is hash-identical.

**Time:** no hand-done baseline, so no speed claim.
