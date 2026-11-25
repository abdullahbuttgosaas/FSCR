---
skill_id: "gosaas.gap-fills.common-features.manage-data-access-for-users"
name: "Manage Data Access for Users: grant a user a role for one data access set, ledger, business unit or other context (GoSaaS gap fill)"
description: "Reads and adds user data access (user + role + security context value) through the REST resource dataSecurities, run with FSCR's REST client; read-only CSV export of ORA_FUN_ALL_USER_DATA_ACCESS for reference. Tested on a test user that nobody signs in with. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10 (written) and batch 11 (tested), 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS"
task_name: "Manage Data Access for Users"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
status: "tested (batch 11)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
  - "gap skill create-implementation-users (test user, Step 5 role)"
  - "shared.setup-export.task-level-export (read only, optional)"
side_effects:
  - "Adds one data assignment: USER can use ROLE for VALUE. On a real user that user then sees and changes that data."
---

# Manage Data Access for Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
Many Fusion job roles are "data roles by context": the user has the role, and a **data assignment** says for which data access set, ledger, business unit, reference data set, inventory organization... This task lists and adds those assignments. Related gap skills, same resource: `manage-bu-data-access-for-users` (context `Business unit`) and `manage-set-data-access-for-users` (context `Reference data set`).

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
W     = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's fusion_rest_client.py unchanged; shows Oracle's error text)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (reads and exports hold user names)
USER  = the user who gets access. For a test: your own test user (prefix name, no sign-in), see Prerequisite 1
ROLE  = the role's display name (RoleNameCr), e.g. General Accountant; ROLE_CODE = its code (RoleCommonName), e.g. ORA_GL_GENERAL_ACCOUNTANT_JOB
CTX   = the security context, exactly as Oracle writes it (Step 2 list), e.g. Data access set
VALUE = the context value: the data access set / ledger / business unit / set name
```
Call pattern (all steps): `cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" <endpoint> [--method POST --body-file f.json --header "Content-Type=application/vnd.oracle.adf.resourceitem+json"] [--query k=v ...] --no-open-browser --output x.json > x.log 2>&1; echo rc=$?`. On `rc=1` the last line of `x.log` is Oracle's own message. Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`, paths as `E:/...`. `R=/fscmRestApi/resources/11.13.18.05/dataSecurities` below.

## Step 1. Safe run and sign-in
- Sign in as in FSCR `core/auth/fusion-oauth-authentication` (a person completes the browser page; never type credentials). On HTTP 401/403 or a hang, sign in again.
- **Never print user names** other than your own test user: in reads always pass `fields=` **without** `UserName` and `Userrf`, except when the filter is your own test user. Never print tokens or the server address (JSON answers hold it in `links`).

## Step 2. Read (VERIFIED)
`<R> --query limit=500 --query onlyData=true --query fields=RoleNameCr,RoleCommonName,SecurityContext,SecurityContextValue,ActiveFlag` (VERIFIED, 500 rows per page). Contexts seen: `Business unit`, `Inventory organization`, `Data access set`, `Reference data set`, `Legal entity`, `Cost organization`, `Manufacturing plant`, `Ledger`, `Project organization classification`. Which roles use CTX: the `(SecurityContext, RoleNameCr, RoleCommonName)` combinations in this read (VERIFIED: General Accountant uses `Data access set`; Buyer uses `Business unit`, `Inventory organization` and `Ledger`; Order Administrator uses `Reference data set`), or the file `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` of the read-only export (Step 7).

## Prerequisites (numbered; do them in order)
1. **USER exists and already has ROLE.** Oracle checks this: a POST for a user without the role is refused with `Applying List binding LOV_RoleNameCr with given set of values leads to no matching row` (VERIFIED, nothing created). For a test, create your own test user with the gap skill `create-implementation-users` (Steps 2 to 4, no roles) and give it ROLE with its Step 5; prove the role with its Step 6 (`roles` holds ROLE_CODE). Never add a role to another person's user.
2. **ROLE uses CTX** (Step 2).
3. **VALUE exists.** Business unit: `/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV --query "q=BusinessUnitName='<VALUE>'" --query onlyData=true --query fields=BusinessUnitName` → `count 1` (VERIFIED). Reference data set: `setIdSetsLOV` with `q=SetName='<VALUE>'`, fields `SetName,SetCode` → `count 1` (VERIFIED). Ledger: `ledgersLOV` with `q=Name='<VALUE>'` (VERIFIED read). Data access set: no REST list by name (`dataAccessSetsLOV` returned 0 rows for an existing set, VERIFIED): use a set you made with the gap skill `manage-data-access-sets` or one seen in Step 2.
4. **No row yet** for USER + ROLE + VALUE: `<R> --query "q=Userrf='<USER>'" --query onlyData=true --query fields=RoleCommonName,SecurityContext,SecurityContextValue,ActiveFlag,UserRoleDataAssignmentId` and look for ROLE_CODE + VALUE in the items. **Filter on `Userrf`, never on `UserName`:** `q=UserName='<USER>'` returns `count 0` even when the user has rows (VERIFIED), so a duplicate check with it always looks clean.

## Step 3. Grant (VERIFIED)
`<RUN>/post.json`:
```json
{"UserName":"<USER>","RoleNameCr":"<ROLE>","SecurityContext":"<CTX>","SecurityContextValue":"<VALUE>","ActiveFlag":true}
```
POST to `<R>` → want `rc=0`; the answer shows `UserRoleDataAssignmentId`, `RoleCommonName` = ROLE_CODE, your CTX and VALUE, `ActiveFlag true` (VERIFIED, about 3 s).
- `RoleNameCr` takes the **display name**. Sending only `RoleCommonName` (the code) is refused: `The value of the attribute Role isn't valid` (VERIFIED, nothing created).
- Never send an `Upsert-Mode` header (it can change an existing grant).
- **Dropped connection or time-out after the POST:** do not POST again; wait 2 minutes and do Step 4.

## Step 4. Read back (VERIFIED)
Prerequisite 4's read again → your row is there, `ActiveFlag true`. By id: `<R>/<UserRoleDataAssignmentId> --query onlyData=true --query fields=RoleCommonName,SecurityContext,SecurityContextValue,ActiveFlag,Userrf` (VERIFIED).

## Step 5. Other contexts
Same steps; only CTX and VALUE change. Contexts with two or three values (e.g. some cost or project contexts) also fill `SecurityContextValue2` / `SecurityContextValue3` (GUESS: not tried).

## Step 6. Rules and limits
1. A grant to a real user gives that person access to real company data: only on the environment owner's written request. For tests use only your own test user, which nobody signs in with.
2. Never deactivate, change or delete an existing grant; never change the automatic provisioning rules (`ORA_FUN_DATA_PROVISIONING_RULES*.csv`).
3. Full REST rows and exports hold user names: keep them in RUN only, never in a repo, report or image.

## Step 7. CSV export (read only, optional, VERIFIED)
`cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS --data --token-cache auto --no-open-browser --output-dir "<RUN>/export"` (about 1 minute): `ORA_FUN_ALL_USER_DATA_ACCESS.csv` (one value column per context: `BuName`, `SetName`, `AccesssetName`, `LegalEntityName`, ...), `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` (role → context), the two provisioning-rule files. A CSV grant (one new row, imported with FSCR `import_setup_task_csv.py`) is GUESS: not run; REST was used instead.

## Worked example (2026-11-25, batch 11)
| Step | Values | Result |
|---|---|---|
| POST without the role on the user | test user `GAPFILL_AB_B11_U1`, General Accountant | refused, LOV_RoleNameCr no matching row; nothing created |
| POST with the code only | `RoleCommonName` | refused, "attribute Role isn't valid" |
| role added | General Accountant on `GAPFILL_AB_B11_U1` (create-implementation-users Step 5) | SCIM read shows it |
| grant | `Data access set` = `GAPFILL_AB_B5_DAS2` (own test set) | created, read back by `Userrf` and by id, active |
| fresh test | see CHANGELOG.md | |
