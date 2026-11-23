# Create demo: `FSCR_Demo_Sheet_1_Run_Now.xlsx` on ETIA-TEST

**Pod:** ETIA-TEST, release 11.13.26.10.0.
**Request:** received 2026-11-04 21:30:16 +05:00. The report was written at about 21:55.
**Input:** a copy of the sheet is at `input/FSCR_Demo_Sheet_1_Run_Now.xlsx`. Only its data rows were used.
**Repo copy:** `fscr-work-demo` is a copy of the original repo. It also holds a copy of the Run 01 FSCR project `fscrt-run01-om-setup`, taken from Run 03's copy, because that project's Run Book already contains the payment-terms and order-lookups tasks.

## 1. Result

| # | Kind | Name | Route | Group | Read back |
|---|---|---|---|---|---|
| 1 | Lookup type | FSCRT_DEMO_ROUTE_TIER_F11 | REST POST `/standardLookups`, FSCR `fusion_rest_client.py` | FSCR plus Claude | **verified** |
| 2 | Lookup code | FSCRT_EXPRESS (in FSCRT_DEMO_ROUTE_TIER_F11) | REST POST `…/standardLookups/FSCRT_DEMO_ROUTE_TIER_F11/child/lookupCodes`, FSCR client | FSCR plus Claude | **verified** |
| 3 | Order type | FSCRT_SO_DEMO1_F11 (in ORA_DOO_ORDER_TYPES) | REST POST `…/standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes`, FSCR client | FSCR plus Claude | **verified** |
| 4 | Payment term | FSCRT_N20D1 | FSM CSV: FSCR payment-terms skill, then Data Loader, Task Hook, import and reconcile | FSCR plus Claude | **verified** |
| 5 | Payment term line | FSCRT_N20D1, line 1: 100 % due in 20 days | same import | FSCR plus Claude | **verified** |
| 6 | Payment term set | FSCRT_N20D1 → ENTERPRISE | same import (SetCode is part of the term's key) | FSCR plus Claude | **verified** |

**Counts:**
- **6 records created and read back:** FSCR alone 0, Claude alone 0, FSCR plus Claude 6. (verified)
- **Skipped as already existing:** 0. Every sheet name was absent before the run. (verified by GETs and the payment-term export)
- **Failed:** 0. (verified)

**Not in the sheet but created with the term:** one US translation row for FSCRT_N20D1, with name and description equal to the term's. FSCR's package builds it, and every term in the pod has one (17 terms and 17 translations before this run). Without it, Oracle doesn't load a term. (verified in the before/after export)

### Why each record is "FSCR plus Claude" and none is "FSCR alone"
- **Rows 1–3:** FSCR supplied the route (`standard-lookups.md`) and the REST client that sent the call. **The JSON request bodies were written by me** from the sheet's values, because FSCR gives no body fields. The POST went through a wrapper I wrote, `scripts/fr_post.sh`. It sends only to the 3 approved endpoints and refuses the 4 brand names.
- **Rows 4–6:** FSCR's own skill script, Data Loader, Task Hook and reconcile did all the Oracle work, with no change to any FSCR file in this run. What I wrote:
  - the skill's design input (`request.json`), built from the sheet's values;
  - the Task Hook rule results (`rule-results.json`). These are AI-attested: FSCR checks only their shape;
  - `final-data.json`;
  - a run config with a blank Run Book ID, so Oracle's Run Book is not updated;
  - the driver `taskhook_lifecycle.py`, reused from Run 03.

  Also, the repo's `payment_terms_fsm_package.py` is the copy patched locally on 2026-10-28 (md5 `1508355745c2…`), not Oracle's original. It is in the original repo as delivered to these runs, and this run did not change it.

### Values read back from Oracle (verified)
- **Lookup type:**
  - LookupType FSCRT_DEMO_ROUTE_TIER_F11, Meaning "FSCRT_Demo Route Tier F11", Description "FSCRT demo lookup type 1";
  - CustomizationLevel U, which is a User type;
  - RestAccessSecured SECURE, which is the sheet's "empty = Secure";
  - ModuleId 61ECAF4AAB00E990E040449821C61C97.
- **Module:** the sheet says "Order Management". Oracle's REST returns the module ID but not its name. In this pod, this module ID has 15 lookup types: all 11 seeded ones are DOO / ORA_DOO (Order Management) types, and the other 4 are test types (2 FSCRT, 2 "TEST LINE TYPES") (`evidence/pre/module_61ECAF_types.json`). The name match is therefore **verified from Oracle data, not by a returned module name**.
- **Lookup code:** FSCRT_EXPRESS, Meaning "FSCRT_Express", Description "FSCRT demo lookup code 1". It is enabled Y, with display sequence 1, no start or end date and no tag. It is the only code in the type.
- **Order type:** FSCRT_SO_DEMO1_F11, Meaning "FSCRT_Demo One Order Type F11", Description "FSCRT demo order type 1". It is enabled Y, with no end date and no tag.
  - **Display sequence 9:** the sheet's "empty = highest existing + 1". The highest of the 61 existing order types was 8.
  - **Start 2026-11-04:** the sheet's "empty = today".
- **Payment term:** checked by FSCR `reconcile` against a fresh export (100004733467561): status **verified**, 0 mismatches, 0 errors.
  - Before/after export diff: term rows 17 → 18, lines 20 → 21, translations 17 → 18, discounts 2 → 2. Nothing was removed or changed.
  - The added rows are: Name FSCRT_N20D1, SetCode ENTERPRISE, Description "FSCRT demo payment term 1", StartDateActive 2026/11/04; line 1, RelativeAmount 100, DueDays 20, SetCode ENTERPRISE; US translation.
- **FSCR-disclosed defaults on the term:**
  - BaseAmount 100;
  - discount basis I (invoice amount);
  - credit check N;
  - first installment INCLUDE;
  - prepayment N;
  - partial discount N.

## 2. Nothing else changed (verified)
- **Order types:** 61 before and 62 after. The only addition is FSCRT_SO_DEMO1_F11; 0 were removed and 0 changed (code, sequence and meaning compared).
- **Payment terms:** the before/after export diff in section 1 shows additions only.
- **The new lookup type** holds exactly 1 code.
- **FSCR Run Book** "FSCRT Run01 OM Setup" (300000394648040): 5 tasks, 2 completed and 3 not started. This matches the Run 01 report ("2 of 5 tasks completed"). Checked by the status counts only, using FSCR `runbook_rest.py summary` (read).

## 3. Other writes to Oracle (all part of FSCR's create route, none extra)
| Record | Why | Status |
|---|---|---|
| Export processes 100004733467548 (template), 100004733457871 (data before), 100004733467561 (data after) | FSCR's payment-term route needs a template and a baseline export, and the read-back uses a fresh export | verified (IDs in the logs) |
| UCM file UCMFA04527888 and data-load request 4436026 (FSM process 100004734447407) | the payment-term import itself | Succeeded, 3 loaded, 0 failed (verified) |
| 3 REST POSTs (HTTP 201) | rows 1–3 | verified |

No update, delete, rename, approval or Run Book update was sent. No name containing Corsair, Intel, AMD or NVIDIA was created or sent; the POST wrapper checked each body before sending (verified). "AMD" appears only as a currency code in the sheet's own Lists tab, which was not used.

**Outside the repo:** FSCR's Data Loader wrote its status log to `C:\Users\PC\.codex\data-loader-status-logs\requestid-4436026\`. A copy is in `evidence/pt/`.

## 4. Time

| Part | Window (+05:00) | Time |
|---|---|---|
| Request to start of the final report | 21:30:16 → about 21:55 | about 25 min. The final summary message adds about 1 min, which is not measured here. |
| Sign-in waiting (not counted below) | 21:38:21 → 21:38:24 | 3 s; no password was needed |
| Shared setup: hashes, repo copy, scripts | 21:30:29 → 21:37:58 | 7 min 29 s (hashing alone: 6 min 05 s) |
| Problem: Git Bash path rewriting looked like a DNS failure | 21:38:30 → 21:44:51 | about 6 min 21 s |
| Existence and module checks | 21:44:51 → 21:46:30 | about 1 min 39 s |
| Lookup type + lookup code (POSTs only) | 21:46:53 → 21:47:44 | 51 s |
| Order type (POST only; its sequence was read at 21:46:30) | 21:47:45 → 21:47:46 | 2 s |
| Payment term + line + set (exports, preview, build, validate, preflight, Task Hook, import, reconcile) | 21:47:59 → 21:52:59 | 5 min 00 s, of which the Oracle import took 1 min 18 s |
| Read-back of the REST records | 21:52:59 → 21:53:32 | 33 s |
| End hashes, Run Book check, token count | 21:53:32 → 21:54:33 | about 1 min |

The per-kind times cover only that kind's own steps. Shared setup, sign-in and the existence checks are listed separately.

## 5. Model calls and tokens (from the session transcript)

**Method:** each response is counted once by message ID, from the request at 21:30:16 to the last call I can measure (21:54:32).

| Item | Value |
|---|---:|
| Model calls | 59 |
| Output tokens | **40,047** |
| Input (uncached) | 120 |
| Cache read | 11,135,964 |
| Cache write | 94,523 |
| Total | 11,270,654 |

**Not included:**
- the calls after 21:54:32: writing this report, the final summary, and the cleanup check;
- summarizing calls with no recorded usage.

## 6. Problems met (none affected Oracle)
1. **Lookups looked like DNS failures but weren't.** 17 read attempts returned `getaddrinfo failed`. The cause was Git Bash rewriting the `/fscmRestApi/...` path argument, the known Run 01 issue F1. Fixed with `MSYS_NO_PATHCONV=1`. Nothing was sent while it failed. (verified)
2. **One real local DNS failure** (nslookup at 21:38:51, router 192.168.100.1). It resolved 10 s later.
3. **Malformed read queries:** 3 queries without quotes returned HTTP 400. The payment-term list doesn't accept a `Name` filter, so existence was taken from FSCR's data export instead.
4. **First lookup-type POST attempt** failed locally on a POSIX file path before sending. It was retried with a Windows path and returned HTTP 201 once. (verified: one type exists)
5. **My first read-back check** compared the number 1 with the text "1" and reported "not verified". Compared as text, all values match.

## 7. What remains on the pod
- **From this run:** lookup type FSCRT_DEMO_ROUTE_TIER_F11 with code FSCRT_EXPRESS; order type FSCRT_SO_DEMO1_F11; payment term FSCRT_N20D1 (ENTERPRISE) with 1 line and 1 US translation.
- **Also from this run:** 3 export process records, the UCM file and the data-load request listed in section 3.
- **Not deleted:** nothing was deleted, as instructed.

## 8. Repo and folder integrity (verified)
- **Hashes:** MD5 hashes of the original repo `fscr-main` and the folders `_fscr_run_01` to `_fscr_run_09_impact` were taken at the start (`hashes/start__*.md5`) and checked at the end (`hashes/summary.txt`).
- **Result:** all 10 are identical, with 0 failed files and 0 new files.

## 9. Processes
- **Started by this run:** FSCR sign-in (exited after login), 2 background hash jobs (exited) and short Python commands. All have ended.
- **Port 8765:** free.
- **Your page:** it was not running, and I didn't start it.
- **Other processes:** a `node.exe` process (PID 1748) was running. This run did not start it, so it was left alone.

## Files
- `payloads/`: the 3 REST bodies, plus the payment-term design input before and after confirmation.
- `scripts/`: `fr_post.sh` (new) and the reused `rget.py`, `fr2.sh`, `taskhook_lifecycle.py` and `diff_exports.py`.
- `evidence/`:
  - `pre` (existence checks);
  - `create` (POST responses);
  - `pt` (preview, build, validate, preflight, Task Hook plan and results, upload, status, FSM log, reconcile);
  - `readback`;
  - `runbook_summary_after.txt`.
- `hashes/`, `run_times.txt`, `login_demo.log` (state and challenge values redacted; no token in it).
