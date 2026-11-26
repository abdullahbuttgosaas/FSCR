# Batch 22 result: Common Features (AB), resource organizations, implementation data role, tax box rules, Thomson Reuters

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (tenth Common Features sitting, first batch). Test records only with the prefix `GAPFILL_AB_B22_`; no user accounts (`CreateUserAccountFlag` false, `example.invalid` emails). Work folder outside the repo.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 22:42 | 22:50 | 8 | Read CONTEXT, CHANGELOG, MODULE_RESULT, audit, tracker; picked the 10 tasks |
| 22:50 | 22:51 | 1 | Sign-in (waiting, not task time) |
| 22:51 | 22:54 | 3 | 4 read-only exports in parallel (data roles, tax box rules, reporting types, trees) |
| 22:54 | 22:56 | 2 | Own test: resource organization ORG1 by REST |
| 22:55 | 22:57 | 2 | Builder impl_data_role.py; own import IDR1 and compare |
| 22:57 | 23:03 | 6 | Tax box codes read live; try 1 (result refused), export, try 2, compare PASS |
| 23:03 | 23:08 | 5 | Skills (3); fresh tests started; Thomson Reuters route re-read and 2 skills |
| 23:08 | 23:25 | 17 | Fresh tests, wording fixes, R/R2 re-tests (sub-agents, in parallel with batch 23) |

## Results
| # | Task | Status | Working min | Waiting min | Proof / records |
|---|---|---|---:|---:|---|
| 1 | Manage Internal Resource Organizations | **tested** | 10 | 2 | ORG1 (own), ORG2F (fresh), ORG3R, ORG4R (re-tests) |
| 2 | Create Data Role for Implementation Users | **tested** | 12 | 4 | IDR1 (100004743461592), IDR2F (100004743462761) |
| 3 | Manage Tax Box Allocation Rules | **tested** (was written-untested) | 18 | 8 | TB1 (100004743462568 + 100004744438453), TB2F refused, TB3R (100004744437528) |
| 4 | Manage Indirect Tax Automation with Thomson Reuters | written (unsafe) | 4 | 1 | taxPartnerRegistrations describe (create, get) |
| 5 | Manage Thomson Reuters Services | written (unsafe) | 3 | 1 | same route |
| | **Total** | **3 tested, 2 written** | **47** | **16** | |

## Problems and findings
1. **Internal resource organizations** are not screen-only: one manager POST to crm `resourceUsers` with a new `ResourceOrganizationName` creates the organization. Oracle put every new organization under an earlier own test organization (`GAPFILL_AB_B20_ORG1`) although no parent was sent.
2. **Create Data Role for Implementation Users** has no own CSV (flag N) but the same object loads through the Manage Data Role and Security Profiles package; new builder `create-data-role-for-implementation-users/scripts/impl_data_role.py` sets the implementation job role. The new role shows in SCIM Roles with category DATA.
3. **Tax box rules:** codes read live, no template needed: rule type `DET_TAX_BOX` (export scope), `PERIODIC`/`ANNUAL` (lookup `ZX_RULE_PERIODICITY`), result type `CODE`. A `CODE` result needs `AlphanumericResult` (= the box), else `ZX_REQUIRED_VALUE`; the header went in alone on try 1 and the result was added on try 2 under the unchanged own header (copy_parent_rows.py). The fresh test found that the rule order (`Priority`) must be unused among tax box rules on the same tax (`ZX_RULES_ORDER_EXISTS_GCO_OWN`, nothing created): step added, re-test PASS.
4. **Thomson Reuters** (both tasks) use the same `taxPartnerRegistrations` route as Avalara: needs the customer's partner account and credentials, applies to the whole environment, no update or delete. Written unsafe. Oracle's REST docs give no list of partner names.

## Tester notes not applied (suggestions only)
Resource organizations: heredoc for the body file; say the LE/BU pair comes from the Counter output. Data role: say whether the source must already use the job role; write the second export command out in full. Tax box: take FROM from the template; ignore the "Tax Rule Condition In progress" line; filter the Step 2 list by prefix.

## What is left
See `MODULE_RESULT.md`.
