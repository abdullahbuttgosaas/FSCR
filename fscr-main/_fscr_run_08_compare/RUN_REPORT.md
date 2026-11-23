# FSCR Run 08: best start vs current deployment (automated comparison)

Pod **ETIA-TEST** (26.10). Request received 2026-11-04 14:07:27 +05:00; pod work finished 14:31:03; checks and report until about 14:40.
Run folder `_fscr_run_08_compare`, repo copy `fscr-work8`, FSCR project `fscr-work8/project/draft_impl_project_20261104` (created from `_template`, as AGENTS.md requires; the name was not changed because no question was to be asked).
Labels: **verified** (computed or read back from Oracle in this run), **not verified**, **unclear**.

## Result

**Shown with a live example: verified.** A best-start definition of 20 FSCRT_ records (147 fields) was compared automatically with the pod. Each record got a status of match / different / missing / extra.

| Stage | match | different | missing | extra | What it shows |
|---|---:|---:|---:|---:|---|
| Baseline | 20 | 0 | 0 | 0 | Pod equals best start |
| After the drift change | 19 | **1** | 0 | 0 | Only FSCRT_PADDLING flagged; field Description |
| After changing it back | 20 | 0 | 0 | 0 | Clean again |
| After adding FSCRT_CAMPING_F08 | 20 | 0 | 0 | **1** | New record reported as "extra" |

The "missing" status was never triggered on the pod, because nothing in the best start was absent and no deletes were allowed. The code path exists but was **not verified live**.

### Per-record results (MD5 fingerprint, first 8 characters)

| # | Area | Record | Fields | Expected MD5 | Baseline | After drift | After revert | After extra |
|---|---|---|---:|---|---|---|---|---|
| 1 | business_unit | FSCRT_Brindle Harbor Marine Supply F01 | 4 | 4fe3588e | match 4fe3588e | match 4fe3588e | match 4fe3588e | match 4fe3588e |
| 2 | business_unit | FSCRT_Quillon Ridge Outfitters West F01 | 4 | beee78ee | match beee78ee | match beee78ee | match beee78ee | match beee78ee |
| 3 | grouping_rule | FSCRT_GRP1 | 4 | 42def27b | match 42def27b | match 42def27b | match 42def27b | match 42def27b |
| 4 | grouping_rule | FSCRT_GRP6 | 4 | 6d6778f2 | match 6d6778f2 | match 6d6778f2 | match 6d6778f2 | match 6d6778f2 |
| 5 | lookup_code | FSCRT_CARRIER_SERVICE_TIER_F01/FSCRT_FREIGHT | 5 | 3101ed21 | match 3101ed21 | match 3101ed21 | match 3101ed21 | match 3101ed21 |
| 6 | lookup_code | FSCRT_CARRIER_SERVICE_TIER_F01/FSCRT_STANDARD | 5 | 5cefdbe8 | match 5cefdbe8 | match 5cefdbe8 | match 5cefdbe8 | match 5cefdbe8 |
| 7 | lookup_code | FSCRT_OUTDOOR_ACTIVITY_F01/FSCRT_CAMPING_F08 | 6 | – | – | – | – | **extra** 9e36ec5e |
| 8 | lookup_code | FSCRT_OUTDOOR_ACTIVITY_F01/FSCRT_CLIMBING | 6 | 1b4a848c | match 1b4a848c | match 1b4a848c | match 1b4a848c | match 1b4a848c |
| 9 | lookup_code | FSCRT_OUTDOOR_ACTIVITY_F01/FSCRT_HIKING | 6 | 80982c4c | match 80982c4c | match 80982c4c | match 80982c4c | match 80982c4c |
| 10 | lookup_code | FSCRT_OUTDOOR_ACTIVITY_F01/FSCRT_PADDLING | 6 | 61a5da51 | match 61a5da51 | **different** e362c851 | match 61a5da51 | match 61a5da51 |
| 11 | lookup_type | FSCRT_CARRIER_SERVICE_TIER_F01 | 5 | 3738ddc3 | match 3738ddc3 | match 3738ddc3 | match 3738ddc3 | match 3738ddc3 |
| 12 | lookup_type | FSCRT_OUTDOOR_ACTIVITY_F01 | 4 | 39c6569a | match 39c6569a | match 39c6569a | match 39c6569a | match 39c6569a |
| 13 | order_type | FSCRT_SO_CONSIGN_F06 | 4 | e5db8a55 | match e5db8a55 | match e5db8a55 | match e5db8a55 | match e5db8a55 |
| 14 | order_type | FSCRT_SO_TRAIL_DEALER_F01 | 4 | 8e69d74b | match 8e69d74b | match 8e69d74b | match 8e69d74b | match 8e69d74b |
| 15 | order_type | FSCRT_SO_WARRANTY_SWAP_F01 | 4 | 6264c077 | match 6264c077 | match 6264c077 | match 6264c077 | match 6264c077 |
| 16 | org_customer | FSCRT_Kestrel Basin Trading Cooperative F01 | 25 | 0ca9b6af | match 0ca9b6af | match 0ca9b6af | match 0ca9b6af | match 0ca9b6af |
| 17 | org_customer | FSCRT_Pemberton Cove Boatworks F01 | 25 | 559f6fc3 | match 559f6fc3 | match 559f6fc3 | match 559f6fc3 | match 559f6fc3 |
| 18 | payment_term | FSCRT_2P10N30F1 | 6 | 6ce8d299 | match 6ce8d299 | match 6ce8d299 | match 6ce8d299 | match 6ce8d299 |
| 19 | payment_term | FSCRT_D25B75AF1 | 6 | a45630ed | match a45630ed | match a45630ed | match a45630ed | match a45630ed |
| 20 | price_list | FSCRT_Brindle Harbor Dock Equipment EUR F01 | 9 | 44ca60f6 | match 44ca60f6 | match 44ca60f6 | match 44ca60f6 | match 44ca60f6 |
| 21 | price_list | FSCRT_Quillon Ridge Wholesale Tents USD F01 | 11 | 73419890 | match 73419890 | match 73419890 | match 73419890 | match 73419890 |

Every status above was computed by `bestart_compare.py`: **verified**. Full MD5s and field lists are in `results/<stage>.json`. The expected definition is in `expected/best_start.json`; the normalized actual state is in `actual/<stage>/normalized.json`.
Drift detail (`results/drift.md`): FSCRT_PADDLING `Description: 'Kayak, canoe and paddleboard gear' -> 'Kayak, canoe and paddleboard gear (FSCRT drift test)'`.

### Second opinion: FSCR's own compare (ZIP vs ZIP)
- **Area:** Manage Order Lookups (DOO_MANAGE_ORCHESTRATION_LOOKUPS), baseline export 100004734424708 vs drift export 100004733457672. Compare process **163220195**, COMPLETED.
- **FSCR report:** Application Standard Lookup: 0 mismatch, 6 match. Application Standard Lookup Code: **1 mismatch**, 69 match (`evidence/fscr_compare/compare_163220195_standard_report.md`).
- **Same record:** FSCR's report gives counts only. The record is named only in Oracle's nested `ORA_FND_APP_STANDARD_LOOKUP_CODE_Discrepancy.xml` inside the report ZIP, which FSCR downloads but does not parse; Claude extracted it (`evidence/fscr_compare/detail/`). It names `FSCRT_OUTDOOR_ACTIVITY_F01,FSCRT_PADDLING`, Source 1 "Kayak, canoe and paddleboard gear" and Source 2 "… (FSCRT drift test)". **The two methods agree: verified.**
- **Coverage:** FSCR's compare covered all 76 OM lookup rows in that area, including non-FSCRT rows. The fingerprint compare covers only the best-start records plus FSCRT_ extras in all 7 areas.
- **Side effects:** FSCR's compare writes to Oracle: 2 file blobs, 2 upload processes (100004733459559, 100004733457741) and the compare process. It also appended a line to the project's token-usage log.

## Steps and decisions (safest reading taken where the brief was unclear)

1. **Expected state (step 1).**
   - `Best Start.xlsx` (`E:\GoSaaS\positive cases\`) was **not used.** It is a customer upload template (Organization Customers, Person Customers, Address Purposes) and contains 0 FSCRT rows, so it does not hold the same records.
   - The best start was built by script from the saved request payloads and input records:
     - Run 01 `input_records.md` and `payloads/*`;
     - the later deliberate changes of Run 03 (C1, C2, C3, C5, C6; C4 was refused, so the Brindle manager stays Yaqub, Younas);
     - Run 06 (R1–R3, GRP6).
   - **Reading taken:** "records of Run 01 and Run 06" was read as the latest *intended* state. Without the Run 03 changes, 6 records would show as "different" from changes that were approved on purpose.
   - **GRP1** comes from Run 04. It was included because Run 06's GRP6 was defined "like GRP1".
   - Person customers were left out, because the step 1 list names organization customers only.
2. **Fingerprint rule.**
   - The MD5 covers the fields the best start defines for each record. The actual side is hashed over exactly the same field list, after the same `norm()`:
     - trim; None → "";
     - true/false → Y/N;
     - any date → YYYY-MM-DD;
     - "2.0" → "2";
     - child rows (payment-term lines and discounts, rule classes, access sets, site uses) are sorted and joined into one field.
   - A value the best start leaves as "default" is not compared. This applies to RestAccessSecured on FSCRT_OUTDOOR_ACTIVITY_F01, the Brindle line type and calculation method, and DisplaySequence on the "(auto)" codes.
   - **Extra** means an FSCRT_ record found on the pod in a compared area that the best start does not define.
3. **Actual state (step 2).**
   - **FSCR task-level export (data):** payment terms, OM lookups (lookup types, codes and order types), grouping rules and business units. 4 export processes per stage, 16 in total.
   - **Price lists:** `rget.py` (Claude's GET reader; FSCR has no read route).
   - **Organization customers:**
     - party, DUNS, taxpayer ID and address: `rget.py` hubOrganizations;
     - account, site, site uses and account DFF: FSCR's own `customer_soap_read`.
4. **Drift (step 4).**
   - **Change:** one PATCH on FSCRT_PADDLING Description through FSCR's REST client, the same route Run 06 R3 used. HTTP 200 at 14:23:53. Reverted with HTTP 200 at 14:25:57. The response bodies confirm both values.
   - **Approval:** the brief itself was taken as the approval for these exact writes (one change, its revert and one extra record), since no questions were to be asked. Payloads were saved before sending (`payloads/`).
5. **Extra (step 5).**
   - FSCRT_CAMPING_F08 was POSTed into FSCRT_OUTDOOR_ACTIVITY_F01 at 14:29:33 (HTTP 201) and was flagged as **extra**.
   - **It stays on the pod** (no deletes allowed). It is the only new record this run left behind.

## Proof nothing else changed (verified)
Whole-area offline diff of the FSCR exports, baseline vs final, using `diff_exports.py` (audit columns ignored):
- **Payment terms:** 17/20/2/17 rows (terms/lines/discounts/translations); 0 added, 0 removed, 0 changed.
- **OM lookups:**
  - 6 types unchanged;
  - codes 70 → 71: +1 (FSCRT_CAMPING_F08), 0 removed, 0 changed. FSCRT_PADDLING is back to its baseline value.
- **Grouping rules:** 13 rules, 23 request rows, 17 type rows; 0 changes.
- **Business units:**
  - 184 BUs, 267 service-provider rows, 1,075 usages and 8,431 set rows; 0 changes;
  - 184 is one more than Run 03's 183; that BU was already there at this run's baseline, so not this run's (cause **unclear**).
- **Price lists:** the FSCRT LastUpdateDate values are identical in the baseline and final reads.

## Failures (classified)
| # | When | Class | What | Outcome |
|---|---|---|---|---|
| 1 | 14:17 | transport/environment | Sign-in token exchange "[WinError 10060]" after the browser step (same as Run 06) | Network checked; retried once, OK |
| 2 | 14:19 | artifact persistence (my script) | `export_all.sh` quoting wrote the baseline ZIPs into a folder literally named `exports$L$t` | ZIPs moved to `exports/baseline/<TASK>/`, script fixed; contents unaffected |
| 3 | 14:23 | input validation (my script) | 2 PATCH attempts failed **before sending** (body-file path errors in `frw.sh`) | Nothing sent; script rewritten |
| 4 | 14:25 | transport/environment | Lookups drift export: process 100004733457672 started, then the result poll failed | Result fetched for the same process ID with Run 03's `fetch_export_result.py`, no second export (FSCR has no resume option) |
| 5 | 14:26 | transport/environment | FSCR compare: first POST (file blob) failed with a connect timeout "[WinError 10060]" | Connect failure, so the request did not reach Oracle; retried once, OK (compare 163220195) |

## Time per step (from `run_times.txt`; minutes)
| Step | Window (+05:00) | Minutes |
|---|---|---:|
| Read the context file and prior runs; set up the folder, copy and hashes | 14:07:27–14:16:29 | 9.0 |
| **Sign-in waiting** (attempt 1 failed at token exchange 14:16:29–14:17:26; retry 14:17:49–14:17:51) | 14:16:29–14:17:51 | **1.4** |
| Baseline read (4 FSCR exports in parallel + price list/customer reads) | 14:19:15–14:20:47 | 1.5 |
| Expected-state build + compare script + baseline compare (script partly written during sign-in) | 14:17:51–14:22:30 | about 4.7 (includes 14:17:51–14:19:15 export setup) |
| Drift: change, re-read all areas, compare | 14:23:01–14:25:40 | 2.7 |
| Revert, re-read, compare | 14:25:55–14:27:25 | 1.5 |
| FSCR compare (failed attempt + retry; overlapped with the revert) | 14:25:58–14:28:45 | 2.8 |
| Extra record: create, re-read, compare | 14:29:09–14:30:43 | 1.6 |
| Checks (side-effect diff, processes, hashes), tokens, report | 14:31:03–about 14:40 | about 9 |
| **Whole run** | 14:07:27–about 14:40 | about 33, of which 1.4 sign-in |

Each of the 4 full read-and-compare cycles took about 1.5 minutes, almost all of it Oracle export time.

## Tokens (exact, from the session transcript)
Method as in earlier runs: each response was counted once by message ID, from the user's request (14:07:27) to the last recorded call. Automatic summarizing calls are not recorded. `scripts/transcript_tokens.py`.
**73 API calls (14:07:31–14:38:01): output 59,663; input 146; cache read 11,298,294; cache write 168,556; total 11,526,659.** The calls made after 14:38:01 to finish this report are not included (not recorded at the time of writing). FSCR's own project token-usage log (`fscr-work8/project/draft_impl_project_20261104/artifacts/shared/token-usage/current/token-usage-log.md`) holds FSCR's "chars/4 estimate" rows, which are estimates and not billed tokens; one exact session row was appended.

## What FSCR did vs what Claude wrote
| Piece | FSCR | Claude |
|---|---|---|
| Sign-in | `fusion_login.py` | Ran it; retry decision |
| Read 4 areas | Task-level export (16 processes) | Ran it (`export_all.sh`) |
| Read price lists | Nothing (no read route) | `rget.py` (Run 03) |
| Read org customers | `customer_soap_read` (account, site, uses, DFF) | Account list and address via `rget.py`; wrapper `fscr_cust_read2.py` |
| Best-start definition | Nothing | `bestart_compare.py expected` from Run 01/03/04/06 payloads |
| Normalize, fingerprint, per-record status | Nothing (FSCR's compare is per area, counts only, through Oracle) | `bestart_compare.py` |
| Second-opinion compare | `compare_setup_task_zips.py` (ran unmodified) | Picked the ZIPs; extracted the record-level detail from the nested XML |
| Drift change, revert, extra record | REST client `fusion_rest_client.py` | Request bodies; whitelist wrapper `frw.sh` |
| Recover the lost export poll | Export engine `download_result` | `fetch_export_result.py` (Run 03) |
| Side-effect proof | Exports | `diff_exports.py` (Run 02/06) |

**No FSCR file was patched.**

## Scripts (in `scripts/`)
**New in Run 08 (4):**
- `bestart_compare.py`: expected build, normalize, MD5 fingerprint, compare (273 lines);
- `read_nonexport.sh`: price list and customer reads, adapted from Run 03 `snapshot.sh`;
- `frw.sh`: whitelist wrapper for the only 3 writes;
- `transcript_tokens.py`.

**Reused, re-pointed to Run 08 (paths only):** `rget.py`, `fr2.sh` (copied, not used), `fscr_cust_read2.py`, `soap_read.py` (copied, not used), `rmut.py` (copied, not used), `diff_exports.py`, `fetch_export_result.py`.

**Changed:** `export_all.sh` (from Run 06: data only, output to the project's `exports/<label>/`, label argument).

## What the comparison cannot see (not compared, so no match is claimed)
- **Price list lines:** no reader. REST returns 0 lines for every list (Run 02 C3, **unclear**), and FSCR has no export.
- **Person customers, including the name prefix (Mr./Ms.):** no reader returns the prefix (Run 02). Person records were not in this best start.
- **Customer profile** (payment terms, credit, collector): the FSCRT accounts have none (Run 02 C1). FSCR's reader returns only HTTP 500, so it could not be compared.
- **Other customer fields not compared:** location DFF (mineral status, URL, e-mail, authorizer, supplier site ID), Sales Tax Inside City Limits and the account address set name. The FSCR reader's account response carries no LocationId, so its `location` read was not reachable from it.
- **Other areas outside this compare:**
  - BU set assignments and Pricing data access;
  - Run 04 Finance records (FSCRT_CAL1, FSCRT_AP_N45, FSCRT_TT1, FSCRT_TS1);
  - person accounts 22052/22053;
  - address purposes of persons.
- **Run 01 decisions** not in the input (for example payment-term PrintingLeadDays 1, ALLOCATE): not part of the best start, so not compared.
- **"Extra" scope:** only FSCRT_ records in the 7 compared areas. Non-FSCRT records are out of scope by design.

## Checks at the end
- **Original repo:** identical to its start-of-run hash (6,120 files). Runs 01–06 folders are also identical.
  - **Observation:** at the start, the original repo had 3 `__pycache__/*.pyc` files that were not in Run 06's start list. They were not created by this run, which never ran Python from the original (cause **unclear**).
- **Processes:** no Python or curl process left; nothing listening on port 8765. The user's page was not running at the start, and it was not started.
- **No secrets:** no token was printed or stored. The login logs are kept, but the authorize URL contains no token; the cache stays in FSCR's location outside the repo.
- **Oracle records this run left:**
  - FSCRT_CAMPING_F08;
  - FSCRT_PADDLING (value unchanged, LastUpdateDate updated twice);
  - 16 export processes, the compare process 163220195 and its 2 uploads and 2 file blobs.
