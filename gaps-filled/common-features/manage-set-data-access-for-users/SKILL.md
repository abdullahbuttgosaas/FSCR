---
skill_id: "gosaas.gap-fills.common-features.manage-set-data-access-for-users"
name: "Manage Reference Data Set Data Access for Users: grant a user a role for one reference data set (GoSaaS gap fill)"
description: "Adds and reads a reference data set data assignment (user + role + set) through the REST resource dataSecurities, context 'Reference data set', run with FSCR's REST client. Tested on a test user that nobody signs in with. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10 (written) and batch 11 (tested), 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FUN_MANAGE_REFERENCE_DATA_SET_DATA_ACCESS_FOR_USERS"
task_name: "Manage Reference Data Set Data Access for Users"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
status: "tested (batch 11)"
depends_on:
  - "gap skill manage-data-access-for-users (same resource, full rules)"
  - "gap skill create-implementation-users (test user, Step 5 role)"
side_effects:
  - "Adds one data assignment: USER can use ROLE for reference data set VALUE."
---

# Manage Reference Data Set Data Access for Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** No FSCR skill or guide; no FSM CSV route for this task code (read-only export refused, VERIFIED). The data lives in the REST resource `dataSecurities` (VERIFIED: get, create, upsert), context `Reference data set`.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
Some roles (for example Order Administrator, Cost Accountant, Product Data Steward, Customer Service Representative) are granted "by reference data set": the user has the role, and a data assignment says for which set. This task adds those assignments. **Read the gap skill `manage-data-access-for-users` first**: it holds the placeholders, call pattern, sign-in, the rules about user names, and Steps 1 to 4. This skill only fixes CTX and the value check.

## Placeholders
```text
FSCR, GAPS, W, RUN, USER, ROLE, ROLE_CODE = as in manage-data-access-for-users
CTX   = Reference data set   (exactly)
VALUE = the reference data set NAME (SetName), not its code
```

## Steps
1. **Sign-in and read**: Steps 1 and 2 of `manage-data-access-for-users`. Pick ROLE among rows with `SecurityContext` `Reference data set` (VERIFIED: Order Administrator = `ORA_DOO_ORDER_ADMINISTRATOR_JOB`, Cost Accountant, Product Data Steward, Customer Service Representative, Order Promising Manager, Supplier Administrator, Application Implementation Consultant).
2. **USER has ROLE**: its Prerequisite 1 (for a test: your own test user from `create-implementation-users`, role added with its Step 5). Without the role the POST is refused (`LOV_RoleNameCr ... no matching row`, VERIFIED in the sister skill).
3. **VALUE exists**: `/fscmRestApi/resources/11.13.18.05/setIdSetsLOV --query "q=SetName='<VALUE>'" --query onlyData=true --query fields=SetName,SetCode` → `count 1` (VERIFIED).
4. **No row yet**: its Prerequisite 4, filtered on `Userrf` (never `UserName`, which always returns 0, VERIFIED).
5. **Grant**: POST to `/fscmRestApi/resources/11.13.18.05/dataSecurities` with `--header "Content-Type=application/vnd.oracle.adf.resourceitem+json"` and
   ```json
   {"UserName":"<USER>","RoleNameCr":"<ROLE>","SecurityContext":"Reference data set","SecurityContextValue":"<VALUE>","ActiveFlag":true}
   ```
   Want `rc=0` and an answer with `UserRoleDataAssignmentId`, `RoleCommonName` = ROLE_CODE, your VALUE, `ActiveFlag true` (VERIFIED). `RoleNameCr` takes the display name, not the code. No `Upsert-Mode`. Dropped connection: do not POST again; wait 2 minutes and read back.
6. **Read back**: its Step 4 (by `Userrf`, or by `UserRoleDataAssignmentId`) → your row, active (VERIFIED).

## Rules and limits
1. For tests use only your own test user, which nobody signs in with. A grant to a real user gives that person the set's reference data: only on the environment owner's written request.
2. Never deactivate, change or delete an existing grant.
3. Full rows hold user names: keep them in RUN only.

## Worked example (2026-11-25, batch 11)
| Step | Values | Result |
|---|---|---|
| role | Order Administrator on test user `GAPFILL_AB_B11_U1` (create-implementation-users Step 5) | SCIM read shows `ORA_DOO_ORDER_ADMINISTRATOR_JOB` |
| grant | `Reference data set` = `Common Set` | created (HTTP 201), read back by `Userrf`, active |
| fresh test | see CHANGELOG.md | |
