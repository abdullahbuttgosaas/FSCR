# Batch 20 result: Common Features (AB), resource organizations, help duty, revoke data role, jurisdiction upload

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (ninth Common Features sitting, first batch). Test records only with the prefix `GAPFILL_AB_B20_`; no user accounts (CreateUserAccountFlag false, `example.invalid` emails). Work folder outside the repo.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 19:40 | 19:45 | 5 | Sign-in; read-only export of the jurisdiction upload (refused); REST names tried by GET; Oracle docs |
| 19:45 | 19:53 | 8 | Own tests by crm resourceUsers: 3 refused tries (nothing created), then manager RM1 (new org ORG1), member RM2, child org ORG2 under ORG1 (RM3); read back |
| 19:53 | 19:56 | 3 | Skills for members and hierarchies; fresh test (sub-agent) |
| 19:56 | 20:00 | 4 | Wording fixed (v0.1.1); R re-test (sub-agent); revoke and jurisdiction skills |
| 20:00 | 20:08 | 8 | Cards, evidence, reports |

## Results
| # | Task | Status | Working min | Waiting min | Proof / records (on the card) |
|---|---|---|---:|---:|---|
| 1 | Manage Resource Organization Members | **tested** | 22 | 4 | RM1 manager (made ORG1) + RM2 member; fresh RM4F/RM5F; R RM7R/RM8R |
| 2 | Manage Resource Organization Hierarchies | **tested** | 14 | 3 | RM3 made ORG2 under ORG1; fresh RM6F (ORG4F); R RM9R (ORG6R) |
| 3 | Assign Help Text Administration Duty | screen-only | 5 | 2 | export refused; SCIM Roles 200 but only manages user members (Oracle docs); fscm roles 404 |
| 4 | Revoke Data Role from Implementation Users | written (unsafe) | 8 | 2 | route: hcm userAccounts child userAccountRoles (delete); the task is a delete |
| 5 | Run Jurisdiction and Rates Upload Program | written (unsafe) | 8 | 2 | route: Import Tax Configuration Content by erpintegrations; changes shared US tax content |
| | **Total** | **2 tested, 1 screen-only, 2 written** | **57** | **13** | |

## Problems and findings
1. The audit's guess "screen-only" was wrong for both resource organization tasks: crm `resourceUsers` builds members and the hierarchy (no hierarchy resource exists).
2. A manager sent with no parent read back later with parent `GAPFILL_AB_B20_ORG1` (seen in the fresh and R tests; own records only). The skill tells the user to check it.
3. **Finding outside this sitting's 10 (not changed):** Manage Internal Resource Organizations is screen-only in `screen-only.csv`, but a manager POST to `resourceUsers` creates a new resource organization; re-judge it.

## What is left
See `MODULE_RESULT.md`.
