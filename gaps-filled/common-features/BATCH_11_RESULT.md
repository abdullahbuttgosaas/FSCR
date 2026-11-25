# Batch 11 result: Common Features (AB), test user, data access for users, search profile option

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (fourth Common Features sitting). One test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file was edited. Work folder outside the repo. Record names `GAPFILL_AB_B11_<name>`. No existing record was edited or deleted.

**Why these 5:** this sitting's prompt narrowed the "unsafe" rule: creating a NEW prefix record that nobody uses is not unsafe, even for users or security ("a new user with no roles" is named as an example). All 5 tasks were cards with status written (unsafe to test); each was re-judged and now has a safe way: a new test user `GAPFILL_AB_B11_U1` (no password set, mailbox `@example.com`, nobody signs in), grants and a USER-level profile value on that user only.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 21:16 | 21:16 | 0.5 | Sign-in (browser page completed). Waiting |
| 21:16 | 21:17 | 1 | Test user plan (roles emptied), preflight, create |
| 21:18 | 21:20 | 2 | Data access tries 1-2 refused; 3 roles added to own test user; 3 grants created and read back |
| 21:21 | 21:23 | 2 | Search option levels read; USER value tries 1 (refused) and 2 (created); read back |
| 21:23 | 21:26 | 3 | 5 skills rewritten as tested skills |
| 21:26 | 21:30 | 4 | Fresh tests: users F (then wording fix), then users R + 4 data/search tests in parallel; own read-back |
| 21:30 | 21:40 | 10 | Cards, evidence, tracker, report |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records |
|---|---|---|---:|---:|---|---|
| 1 | Create Implementation Users (`FND_CREATE_IMPLEMENTATION_USERS`) | tested | 6 + 4 | 1 | PASS, re-test R PASS | `GAPFILL_AB_B11_U1`; fresh `U2F`; re-test `U3R` (all no roles at creation) |
| 2 | Manage Data Access for Users (`ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS`) | tested (try 3) | 5 + 3 | 1 | PASS | `U1` + General Accountant + data access set `GAPFILL_AB_B5_DAS2`; fresh `U2F` + `GAPFILL_AB_B5_DAS3F` |
| 3 | Manage Business Unit Data Access for Users | tested | 3 + 2 | 1 | PASS | `U1` + Buyer + an existing BU; fresh `U2F` + Buyer + BU GoSaaS |
| 4 | Manage Reference Data Set Data Access for Users | tested | 2 + 2 | 1 | PASS | `U1` + Order Administrator + Common Set; fresh `U2F` + Enterprise Set |
| 5 | Manage Search Profile Options (`ZCA_MANAGE_SEARCH_PROFILE_OPTIONS`) | tested (try 2, USER level) | 5 + 2 | 1 | PASS | USER value `REAL-TIME_SEARCH` for `U1`; fresh for `U2F`; SITE `KEYWORD_SEARCH` unchanged |
| | **Total** | **5 tested** | **34** | **5** | 5 of 5 (+1 re-test) | |

No FSM import was used (all REST), so there are no ProcessIds in this batch.

## Problems and findings
1. **FSCR's implementation-users executor reports a false error:** each `assign_role_via_scim_roles` step shows "REST client failed" although the role is added. Oracle answers the SCIM PATCH with an empty body and FSCR's client cannot parse it as JSON. The single-user SCIM GET (`roles`) is the proof. Worth telling Oracle.
2. **The FSCR plan always lists 3 setup roles** (Application Implementation Consultant, IT Security Manager, Application Diagnostic Administrator); the skill empties them in the plan copy for a test user.
3. **dataSecurities:** the user must already have the role (`LOV_RoleNameCr ... no matching row` otherwise); `RoleNameCr` takes the display name (the code alone is refused); **`q=UserName='x'` returns 0 rows even when rows exist: filter on `Userrf`**.
4. **USER-level profile values:** `LevelValue` is the user's GUID (= SCIM id), not the user name (`LOV_UserName` refused). `profileOptionLevels` tells which levels are open: `ZCA_SEARCH_DEFAULT_OPTION` has USER; `HZ_ENABLE_MULTIPLE_BU_CRM` is SITE only, so Common CRM BU Profile Options stays written-unsafe.
5. A transient DNS failure (`getaddrinfo failed`) hit some reads; re-running them worked; no POST was affected.
6. Also proven **screen-only** this batch (do not count): Manage Languages, Manage Territories, Manage Time Zones (REST `languagesLOV`, `territoriesLOV`, `timezonesLOV` are get-only; plain resources 404; no FSM CSV).

## Re-judged written cards that stay written (reasons updated in the cards / my_gaps)
- Common CRM BU Profile Options: option is SITE only (USER level disabled, VERIFIED); a SITE flip changes multiple-BU behaviour for every CRM user.
- Intercompany Exceptions, LE Tax Profiles, LRU Tax Profiles, Configuration Owner Tax Options: a safe way exists (a NEW test legal entity with its own LRU and profiles), but it is a long chain (legal entity package): next sitting.
- Import Worker Users, Partner Organizations: a NEW test worker (then a resource from it, then a partner owned by that resource) is the safe way; long chain: next sitting.
- Map Reports to Work Areas, Country Default Controls: see batch 12.

## What is left
Batch 12 continues at once (sitting limit 10).
