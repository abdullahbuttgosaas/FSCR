---
skill_id: "gosaas.gap-fills.common-features.manage-data-access-for-users"
name: "Manage Data Access for Users: grant a user a role for one business unit, ledger, data access set or other context (GoSaaS gap fill, written, not load-tested)"
description: "Read and add user data access (user + role + security context value) through FSCR's setup-task CSV export/import (ORA_FUN_ALL_USER_DATA_ACCESS) or the REST resource dataSecurities. Read steps VERIFIED; the grant is GUESS because it is a security change for a real user. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10, 2026-11-25. Read-only export and REST reads seen live; nothing created. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS"
task_name: "Manage Data Access for Users"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "written (unsafe to test on a shared environment)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
side_effects:
  - "Read steps: none (the export holds user names: keep it outside any repo)."
  - "Grant step: gives one user one role for one context value (for example a business unit). The user then sees and changes that data."
---

# Manage Data Access for Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.
> **Status: written, not load-tested.** Why: every row gives a **real user** access to real company data (a business unit, ledger, data access set, reference data set, legal entity, inventory or cost organization...). The only user we could use is our own sign-in user, and granting ourselves more access is a security change on a shared environment that the security owner did not approve. Load-test only on an environment you own, with written approval.

## What it is and when to use
Many Fusion roles are "data roles by context": a user has the role, plus a data assignment that says **for which** business unit (or ledger, set, organization...). This task lists and adds those assignments. Related gap skills: `manage-bu-data-access-for-users` (context Business unit) and `manage-set-data-access-for-users` (context Reference data set) use the same resource.

## Placeholders
```text
FSCR    = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
W       = <GAPS>/common-features/scripts/rest_call.py                (REST; runs FSCR's client unchanged, shows Oracle's error text)
RUN     = a NEW empty work folder OUTSIDE FSCR and outside any git repo (exports hold user names)
USER    = the user who gets access (read at run time; never print other people's user names)
ROLE    = the role's common name (RoleCommonName / RoleNameCr), e.g. a job role code
CTX     = the security context: one of the values in Step 2 (VERIFIED list)
VALUE   = the context value: the business unit name, ledger name, set name, ...
```

## Step 1. Safe run and sign-in
- FSCR scripts with full path and `python -B`; REST through `<W>` (`cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" <endpoint> [options] --no-open-browser --output x.json > x.log 2>&1`). Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`, paths as `E:/...`. Join `q=` conditions with `;`.
- **Never print user names** other than your own test user: always pass `fields=` without `UserName`, `Userrf`, `CreatedBy`, `LastUpdatedBy` when you show rows; count in code.
- Sign-in: FSCR `core/auth/fusion-oauth-authentication`; a person completes the browser page.

## Step 2. Read (VERIFIED)
- REST: `... /fscmRestApi/resources/11.13.18.05/dataSecurities --query limit=500 --query onlyData=true --query fields=SecurityContext,ActiveFlag` (VERIFIED: 500+ rows). Contexts seen (VERIFIED): `Business unit`, `Inventory organization`, `Data access set`, `Reference data set`, `Legal entity`, `Cost organization`, `Manufacturing plant`, `Ledger`, `Project organization classification`. The resource has `get`, `create`, `upsert` (VERIFIED by `/describe`); its fields: `UserName, RoleNameCr, RoleCommonName, SecurityContext, SecurityContextValue, SecurityContextValue2, SecurityContextValue3, ActiveFlag` (+ `UserRoleDataAssignmentId` and audit columns).
- CSV: read-only export of task `ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS` (FSCR `export_setup_task_csv.py --task-code ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS --data --output-dir "<RUN>/export_before"`, about 1 minute, VERIFIED): `ORA_FUN_ALL_USER_DATA_ACCESS.csv` (516 rows; columns `RoleName, UserName, BuName, Name, BookTypeCode, SetName, OrganizationCode, CostOrgName, AccesssetName, ..., LegalEntityName, ActiveFlag, ...`: one value column per context), `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` (72 rows: which role uses which context), `ORA_FUN_DATA_PROVISIONING_RULES.csv` and `ORA_FUN_DATA_PROVISIONING_RULE_DETAIL.csv` (automatic provisioning rules; leave alone).
- Which context a role needs: look up ROLE in `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` (`RoleName`, `SecurityContext`).

## Prerequisites (for a grant)
1. USER exists and already has ROLE (a data assignment does not grant the role itself; GUESS from Oracle's docs).
2. ROLE uses CTX (Step 2 mapping file).
3. VALUE exists (for example `finBusinessUnitsLOV` by `BusinessUnitName` for a business unit, VERIFIED read; `ledgersLOV` by `Name` for a ledger, VERIFIED read).
4. No row yet for USER + ROLE + CTX + VALUE: `dataSecurities` with `q=UserName='<USER>';RoleNameCr='<ROLE>';SecurityContextValue='<VALUE>'` → `count 0` (GUESS for the exact filter).

## Step 3. Grant (GUESS, not run)
REST (preferred, one row):
```json
{"UserName":"<USER>","RoleNameCr":"<ROLE>","SecurityContext":"<CTX>","SecurityContextValue":"<VALUE>","ActiveFlag":true}
```
`... /fscmRestApi/resources/11.13.18.05/dataSecurities --method POST --body-file "<RUN>/post.json" --header "Content-Type=application/vnd.oracle.adf.resourceitem+json"` → want `HTTP 201`. Never send `Upsert-Mode` (it can change an existing grant). CSV alternative: one new row in `ORA_FUN_ALL_USER_DATA_ACCESS.csv` with `RoleName`, `UserName`, the one value column of CTX, `ActiveFlag=Y`, built with `<H>/build_fsm_package.py` and imported with FSCR `import_setup_task_csv.py` (task name "Manage Data Access for Users"); keep the ProcessId.

## Step 4. Read back (GUESS for a new row)
Step 4 of Prerequisites again → `count 1`, `ActiveFlag true`; or a second export compared with `<H>/compare_fsm_exports.py` (key `RoleName,UserName,<value column>`).

## Rules and limits
1. Only on an environment you own, or with written approval of its security owner. Never grant access to another person's user.
2. Never deactivate, change or delete an existing grant; never change provisioning rules.
3. Exports and full REST rows hold user names: keep them in RUN, never in a repo, report or image.

## Worked example
None: not load-tested (see Status). VERIFIED reads only: the export above (4 files) and `dataSecurities` reads and describe.
