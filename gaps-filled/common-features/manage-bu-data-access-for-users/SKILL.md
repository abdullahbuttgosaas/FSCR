---
skill_id: "gosaas.gap-fills.common-features.manage-bu-data-access-for-users"
name: "Manage Business Unit Data Access for Users: grant a user a role for one business unit (GoSaaS gap fill)"
description: "Adds and reads a business unit data assignment (user + role + business unit) through the REST resource dataSecurities, context 'Business unit', run with FSCR's REST client. Tested on a test user that nobody signs in with. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10 (written) and batch 11 (tested), 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FUN_MANAGE_BUSINESS_UNIT_DATA_ACCESS_FOR_USERS"
task_name: "Manage Business Unit Data Access for Users"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
status: "tested (batch 11)"
depends_on:
  - "gap skill manage-data-access-for-users (same resource, full rules)"
  - "gap skill create-implementation-users (test user, Step 5 role)"
side_effects:
  - "Adds one data assignment: USER can use ROLE for business unit VALUE."
---

# Manage Business Unit Data Access for Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** No FSCR skill or guide; no FSM CSV route for this task code (read-only export refused, VERIFIED). The data lives in the REST resource `dataSecurities` (VERIFIED: get, create, upsert), context `Business unit`.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
Roles such as Buyer, Accounts Payable Manager or Order Manager work "by business unit": the user has the role, and a data assignment says for which business unit. This task adds those assignments. **Read the gap skill `manage-data-access-for-users` first** (in the same folder level as this skill): it holds the placeholders, call pattern, sign-in, the rules about user names, and Steps 1 to 4. This skill only fixes CTX and the value check.

## Placeholders
```text
FSCR, GAPS, W, RUN, USER, ROLE, ROLE_CODE = as in manage-data-access-for-users
CTX   = Business unit   (exactly, with the space and lower-case u)
VALUE = the business unit name
```

## Steps
1. **Sign-in and read**: Steps 1 and 2 of `manage-data-access-for-users`. Pick ROLE among rows with `SecurityContext` `Business unit` (VERIFIED: e.g. Buyer = `ORA_PO_BUYER_JOB`, Order Manager, Pricing Administrator, Procurement Manager).
2. **USER has ROLE**: its Prerequisite 1 (for a test: your own test user from `create-implementation-users`, role added with its Step 5). Without the role the POST is refused (`LOV_RoleNameCr ... no matching row`, VERIFIED in the sister skill).
3. **VALUE exists**: `/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV --query "q=BusinessUnitName='<VALUE>'" --query onlyData=true --query fields=BusinessUnitName` → `count 1` (VERIFIED). The name is exact and case-sensitive.
4. **No row yet**: its Prerequisite 4, filtered on `Userrf` (never `UserName`, which always returns 0, VERIFIED).
5. **Grant**: POST to `/fscmRestApi/resources/11.13.18.05/dataSecurities` with `--header "Content-Type=application/vnd.oracle.adf.resourceitem+json"` and
   ```json
   {"UserName":"<USER>","RoleNameCr":"<ROLE>","SecurityContext":"Business unit","SecurityContextValue":"<VALUE>","ActiveFlag":true}
   ```
   Want `rc=0` and an answer with `UserRoleDataAssignmentId`, `RoleCommonName` = ROLE_CODE, your VALUE, `ActiveFlag true` (VERIFIED). `RoleNameCr` takes the display name, not the code. No `Upsert-Mode`. Dropped connection: do not POST again; wait 2 minutes and read back.
6. **Read back**: its Step 4 (by `Userrf`, or by `UserRoleDataAssignmentId`) → your row, active (VERIFIED).

## Rules and limits
1. For tests use only your own test user, which nobody signs in with. A grant to a real user gives that person the business unit's data: only on the environment owner's written request.
2. Never deactivate, change or delete an existing grant.
3. Full rows hold user names: keep them in RUN only.

## Worked example (2026-11-25, batch 11)
| Step | Values | Result |
|---|---|---|
| role | Buyer on test user `GAPFILL_AB_B11_U1` (create-implementation-users Step 5) | SCIM read shows `ORA_PO_BUYER_JOB` |
| grant | `Business unit` = an existing business unit | created (HTTP 201), read back by `Userrf`, active |
| fresh test | see CHANGELOG.md | |
