# Batch 21 result: Common Features (AB), worker users, partners, geography loader, project rules, tax box rules

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (ninth Common Features sitting, second batch). Test records only with the prefix `GAPFILL_AB_B21_`.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 19:54 | 19:56 | 2 | Partner create with own owner resource: refused twice, nothing created |
| 19:56 | 19:58 | 2 | Own test worker WU1 (hcm workers); user account read back: no roles |
| 19:58 | 20:01 | 3 | Worker skill v0.2.0, fresh test, wording fix v0.2.1, R re-test (sub-agents) |
| 19:59 | 20:02 | 3 | REST names tried by GET; tax box export read; Oracle docs (tax box allocation) |
| 20:01 | 20:08 | 7 | Skills (geography, project rules, tax box), cards, evidence, reports |

## Results
| # | Task | Status | Working min | Waiting min | Proof / records (on the card) |
|---|---|---|---:|---:|---|
| 1 | Import Worker Users | **tested** | 14 | 3 | WU1 (PersonNumber 103), fresh WU2F (104), R WU3R (108); each 1 user account, 0 roles |
| 2 | Manage Partner Organizations | **failed** | 12 | 2 | `ResourceId` not an attribute; `OwnerPartyNumber` of own resource refused; GET 0 rows |
| 3 | Run Geography Loader | written (unsafe) | 6 | 2 | route: crm importActivities; master geography is shared, no delete |
| 4 | Manage User-Defined Rules for Project Management | written (unsafe) | 6 | 2 | FSM CSV BPM rule set (0 rows); an upload replaces a workflow's rule set |
| 5 | Manage Tax Box Allocation Rules | written (safe way found, not tested yet) | 10 | 3 | tax rules package has ReportingTypeCode / PeriodicityCode; no tax box rule to copy; codes GUESS |
| | **Total** | **1 tested, 1 failed, 3 written** | **48** | **12** | |

## Problems and findings
1. Partner owner: Oracle refuses a CRM resource with no user account as owner (message names `ResourceId`). Next try: an owner resource with a user account, with approval.
2. A new worker gets a user account from Fusion's rules, with no roles on this environment (VERIFIED 3 times).
3. Tax box rule: safe way exists (disabled rule on own regime with an own tax box reporting type), but a template rule is needed first.

## What is left
See `MODULE_RESULT.md`.
