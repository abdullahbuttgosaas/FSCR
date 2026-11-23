# Run 06 ledger: existing configuration + new requirements

Pod ETIA-TEST (release 26.10). Start 2026-11-03 22:00:27 +05:00. Labels: verified / not verified / unclear.

## Setup (22:00–)
- **Authority:** the user said "just complete the test and tell me the result idc how u do it". Decision D1: I drafted the requirements myself (`requirements.md`) and applied the same rules as earlier runs: FSCRT records only, no deletes, nothing pre-existing changed, every payload saved before it is sent.
- **Copies:** `fscr-work6` = copy of the original repo, plus the Run 04 FSCR project `fscrt-run04-create16` (its Run Book already lists AR_MANAGE_AUTOINVOICE_GROUPING_RULES, so FSCR's Task Hook accepts that task). Original repo and Runs 01–05 hashed at start (`orig_repo_hashes_start.md5`, `hashes_*.md5`).
- **Scripts:** Run 04 drivers (`live_run.py`, `adapter_run.py`, `inspect_candidate.py`, `diff_exports.py`, `fetch_export_result.py`, `export_all.sh`) and Run 03 readers (`rget.py`, `fr2.sh`) copied and re-pointed to Run 06 (paths only).
- **Usage at start** (`get_usage`): context 401,769; 5-hour 16%; weekly 46%. Context size, not billed tokens.
- **Sign-in:** token expired; port 8765 free (the user's page was not running). FSCR `fusion_login.py --token-cache auto` in the background. First attempt: browser step completed, then the token exchange failed: "[WinError 10060] A connection attempt failed…" (transport). Network checked (sign-in host and pod reachable); retried once.

## Routing (followed the router text; FSCR has no router script)
- R1, R2, R3, R4, R5 → task DOO_MANAGE_ORCHESTRATION_LOOKUPS (Manage Order Lookups, CSV Y) → `pillars/scm/order-management/orders/manage-order-lookups/SKILL.md` → `core/fusion-api/apps-common/lookups` (REST via FSCR `fusion_rest_client.py`).
- R6 → task AR_MANAGE_AUTOINVOICE_GROUPING_RULES (CSV Y) → `pillars/erp/financials/customer-billing/manage-autoinvoice-grouping-rules` (own `fsm_task_adapter.py`, FSM CSV via `core/data-loader` + Task Hook).

## Current setup read through FSCR (22:07–22:10)
- FSCR task-level export, template + data: DOO_MANAGE_ORCHESTRATION_LOOKUPS (processes 100004733458054, 100004734424696) and AR_MANAGE_AUTOINVOICE_GROUPING_RULES (100004733457644, 100004733459180). Log: `evidence/exports_before.log`.
- Found (verified, from the data exports): FSCRT_HIKING meaning "FSCRT_Hiking and trekking"; FSCRT_PADDLING description "Kayak and canoe gear"; no FSCRT_CLIMBING; FSCRT_SO_WARRANTY_SWAP_F01 enabled Y; no FSCRT_SO_CONSIGN_F06; grouping rule FSCRT_GRP1 exists (Invoice class), no FSCRT_GRP6.

## Gap analysis (what must change)
| Req | Current (export) | Needed | Action |
|---|---|---|---|
| R1 | no FSCRT_SO_CONSIGN_F06 | new enabled order type | CREATE lookup code in ORA_DOO_ORDER_TYPES (REST POST) |
| R2 | no FSCRT_CLIMBING | new code, seq 3, enabled | CREATE lookup code in FSCRT_OUTDOOR_ACTIVITY_F01 (REST POST) |
| R3 | "Kayak and canoe gear" | "Kayak, canoe and paddleboard gear" | CHANGE description (REST PATCH) |
| R4 | "FSCRT_Hiking and trekking" | same | NONE: already met |
| R5 | EnabledFlag Y | enabled | NONE: already met |
| R6 | no FSCRT_GRP6 | new rule like GRP1 | CREATE through FSCR adapter + Data Loader + Task Hook |
- Payloads saved before sending: `payloads/r1_consign.json`, `r2_climbing.json`, `r3_paddling.json`, `payloads/grp6/design.json` (GRP1's Run 04 design with the new name and description). Request bodies are mine (FSCR gives no fields); field names from the export columns.

## Apply (22:10–22:12)
- R1 POST ORA_DOO_ORDER_TYPES/child/lookupCodes → HTTP 201 (22:10:45); R2 POST FSCRT_OUTDOOR_ACTIVITY_F01/child/lookupCodes → HTTP 201 (22:10:47); R3 PATCH …/FSCRT_PADDLING → HTTP 200 (22:10:49). FSCR `fusion_rest_client.py`, my bodies. No retries.
- R6: adapter manifest ×2, normalize, build, validate rc 0 (candidate sha256 cf8809a2…); Data Loader preflight "passed validation. No data was uploaded." + approval request; approval = the user's instruction to complete the test (D2); Task Hook rule plan 4 files, my rule results all passed with evidence; hook OK; upload UCMFA04525787, request 4433652 (22:11:47).

## Verify (22:11–22:14)
- Import Succeeded 3/3, 0 failed (FSM log in `C:\Users\PC\.codex\data-loader-status-logs\requestid-4433652`). After-export 100004733459213; adapter reconcile PASS. Diff: +1 rule, +1 class row, 0 changed, 0 removed.
- Lookups after-export 100004733447631. Diff: +FSCRT_CLIMBING, +FSCRT_SO_CONSIGN_F06, FSCRT_PADDLING description changed, nothing else. Values match the payloads.

## End (22:14:43)
- Original repo and Runs 01–05 hash-identical. No Python process; port 8765 free.
- Tokens (transcript, request → finish): 23 calls; output 18,214; input 50; cache read 9,539,882; cache write 39,187; total 9,597,333.
- `get_usage` end: context 439,426; 5-hour 20%; weekly 46%.
