---
skill_id: "gosaas.gap-fills.common-features.manage-set-data-access-for-users"
name: "Manage Reference Data Set Data Access for Users: grant a user a role for one reference data set (GoSaaS gap fill, written, not load-tested)"
description: "Read and add reference data set data access for a user through FSCR's REST client (resource dataSecurities, SecurityContext 'Reference data set'). Read steps VERIFIED; the grant is GUESS because it is a security change for a real user. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10, 2026-11-25. REST reads seen live; nothing created. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FUN_MANAGE_REFERENCE_DATA_SET_DATA_ACCESS_FOR_USERS"
task_name: "Manage Reference Data Set Data Access for Users"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "written (unsafe to test on a shared environment)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
  - "gosaas common-features/manage-data-access-for-users (same resource, full rules)"
side_effects:
  - "Grant step: gives one user one role for one reference data set. The user then sees and changes that reference data set's data."
---

# Manage Reference Data Set Data Access for Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill or guide for this task and no FSM CSV route for its own task code (read-only export refused, VERIFIED 2026-11-25). The same data is reachable through the REST resource `dataSecurities` (VERIFIED: `get`, `create`, `upsert`) and through the CSV package of the sister task `ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS` (file `ORA_FUN_ALL_USER_DATA_ACCESS.csv`, column `SetName`, VERIFIED).
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.
> **Status: written, not load-tested.** Why: a grant gives a **real user** access to a real reference data set. The only user we could use is our own sign-in user, and granting ourselves more access is a security change on a shared environment that its security owner did not approve. Load-test only on an environment you own, with written approval.

## What it is and when to use
Roles such as roles that maintain set-enabled reference data (for example payment terms or transaction types) work "by reference data set": the user has the role, and a data assignment says for which reference data set. This task lists and adds those assignments for the security context `Reference data set`. Read the gap skill `manage-data-access-for-users` first: it holds the full rules (placeholders, sign-in, never printing user names, CSV alternative).

## Placeholders
```text
FSCR, GAPS, W, RUN, USER, ROLE = as in manage-data-access-for-users
VALUE = the reference data set name
```

## Step 1. Read (VERIFIED)
`cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/dataSecurities --query "q=SecurityContext='Reference data set'" --query onlyData=true --query fields=RoleNameCr,SecurityContextValue,ActiveFlag --no-open-browser --output ctx.json > ctx.log 2>&1`
VERIFIED: rows with SecurityContext `Reference data set` exist (VERIFIED: 24 rows with this filter). Keep `UserName` out of `fields` when you show rows; filter on it in `q=` only for your own test user.
Check VALUE exists: the set name must appear in the read-only export of the reference data set task, or as `SetName` in `ORA_FUN_ALL_USER_DATA_ACCESS.csv` (VERIFIED column); a REST set list was not checked (GUESS).

## Step 2. Prerequisites (for a grant)
1. USER already has ROLE; ROLE uses context `Reference data set` (`ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` of the sister task's export, VERIFIED file).
2. No row yet: `q=UserName='<USER>';RoleNameCr='<ROLE>';SecurityContext='Reference data set';SecurityContextValue='<VALUE>'` → `count 0` (GUESS for the exact filter).

## Step 3. Grant (GUESS, not run)
```json
{"UserName":"<USER>","RoleNameCr":"<ROLE>","SecurityContext":"Reference data set","SecurityContextValue":"<VALUE>","ActiveFlag":true}
```
POST to `/fscmRestApi/resources/11.13.18.05/dataSecurities` with `--header "Content-Type=application/vnd.oracle.adf.resourceitem+json"` → want `HTTP 201`. Never send `Upsert-Mode`. Read back with Step 2's filter → `count 1`.

## Rules and limits
1. Only on an environment you own, or with written approval of its security owner. Never grant access to another person's user.
2. Never deactivate, change or delete an existing grant.
3. Full rows hold user names: keep them in RUN only.

## Worked example
None: not load-tested (see Status). VERIFIED reads only.
