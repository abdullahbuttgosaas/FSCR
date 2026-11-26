# Batch 18 result: Common Features (AB), screen-only checks: WebLogic communication services, PaaS identity sync, read-only masking

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (eighth Common Features sitting, first batch). Read only on Oracle: task exports and REST GET / describe; nothing was created. Work folder outside the repo. Proof for every screen-only task is on its own `STATUS.md` card (new rule).

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 19:13 | 19:15 | 2 | Tracker rebuilt from the cards; 5 written cards re-judged (new unsafe rule) |
| 19:14 | 19:17 | 3 | Version-level REST catalogs read: incomplete (hcm lacks userAccounts), so NOT used as proof; stopped |
| 19:15 | 19:16 | 1 | Read-only exports (all refused, task flag N) |
| 19:17 | 19:20 | 3 | Oracle docs searched (PaaS role sync, masking); REST names tried by GET |
| 19:30 | 19:45 | 15 | Cards, evidence, reports |

## Results
| # | Task | Status | Working min | Waiting min | Proof (on the card) |
|---|---|---|---:|---:|---|
| 1 | Deploy WebLogic Communication Services | screen-only | 4 | 2 | export refused (flag N); crm communicationServices 404 (multiChannelAdapterToolbars exists but is CTI toolbars) |
| 2 | Integrate WebLogic Communication Services with Telephony Network | screen-only | 4 | 2 | export refused; crm telephonyNetworks, telephonyIntegrations 404 |
| 3 | Migrate Enterprise Roles and Assignments to PaaS Identity Store | screen-only | 4 | 2 | export refused; fscm roleSynchronizations, hcm roles 404; Oracle docs: task flow page |
| 4 | Manage User Identity Synchronization to PaaS Identity Store | screen-only | 4 | 2 | export refused; fscm userIdentitySynchronizations 404; report + process |
| 5 | Manage Read-Only Schema Column Masking for Users | screen-only | 4 | 2 | export refused; fscm readOnlySchemaMasking, columnMasks 404; no route in Oracle docs |
| | **Total** | **5 screen-only** | **20** | **10** | |

## Problems and findings
1. The version-level REST `describe` (metadataMode=minimal) does not list every resource (hcm: 145 names, no userAccounts), so a missing name there proves nothing. Proof uses direct GETs instead.
2. Re-judged written cards: Import Worker Users and Partner Organizations now have a SAFE WAY (a new user with no roles is not unsafe; crm resourceUsers allows create): tracker `written-untested`, to test next sitting. Map Reports to Work Areas, CRM BU Profile Options and Archive and Purge stay unsafe (reasons on the cards).
3. Read-only exports were also run for 4 tasks that were then left for a later sitting (Assign Help Text Administration Duty, Revoke Data Role from Implementation Users, Resource Organization Hierarchies, Run Geography Loader): all refused (flag N). Their status was not changed; each may have a REST route (SCIM roles, userAccounts, crm resources, scheduled processes) to check first.

## What is left
See `MODULE_RESULT.md`.
