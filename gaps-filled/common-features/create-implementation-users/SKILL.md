---
skill_id: "gosaas.gap-fills.common-features.create-implementation-users"
name: "Create Implementation Users: create a test user with FSCR's own implementation-users scripts (GoSaaS gap fill)"
description: "Creates one Fusion user account (no roles, or roles you choose) through SCIM /hcmRestApi/scim/Users with FSCR's core skill core/getting-started/implementation-users, run unchanged, and reads it back by SCIM and userAccounts. Optional step: give your own test user a job role. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 09 (written) and batch 11 (tested), 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_CREATE_IMPLEMENTATION_USERS"
task_name: "Create Implementation Users"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
status: "tested (batch 11)"
depends_on:
  - "core.getting-started.implementation-users (FSCR scripts, run unchanged)"
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
side_effects:
  - "Creates one user account. With the default FSCR plan it also gets 3 setup job roles; this skill removes them from the plan so a test user gets NO role unless you add one in Step 5."
---

# Create Implementation Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a skill for this work, `core/getting-started/implementation-users`, but its catalog does not map it to the task code `FND_CREATE_IMPLEMENTATION_USERS`, so the tracker counted the task as "neither". No FSM CSV route (read-only export refused, VERIFIED).
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
An implementation user is an account that does setup. Use this skill to create one user with FSCR's scripts, or (for tests) a **test user with no roles** that nobody signs in with. Other gap skills (`manage-data-access-for-users`, `manage-bu-data-access-for-users`, `manage-set-data-access-for-users`, `manage-search-profile-options`) use such a test user as their prerequisite.

## Placeholders
```text
FSCR     = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only, never edit.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
W        = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's fusion_rest_client.py unchanged; shows Oracle's error text)
RUN      = a NEW empty work folder OUTSIDE FSCR and outside any git repo
USERNAME = the new user name, upper case, starting with your test prefix, e.g. <PREFIX>U1
EMAIL    = a mail address nobody reads for a test user (for example <username>@example.com, a reserved domain); a real person's own address for a real user. Never a colleague's.
USERGUID = the new user's SCIM id (32 characters), read live in Step 4
```

## Step 1. Safe run and sign-in
- Git Bash on Windows: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; paths as `E:/...`; run FSCR scripts from `<FSCR>` with `python -B`.
- Steps 2 to 5 run from `<FSCR>` (relative `core/...` paths). REST reads (Step 6) run from RUN: `cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" <endpoint> [--scim-only] [--query k=v ...] --no-open-browser --output x.json > x.log 2>&1`. On failure the last line of `x.log` is Oracle's own message.
- Sign-in: FSCR `core/auth/fusion-oauth-authentication` (`python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`, in the background; a person completes the browser page; never type credentials). The signed-in user needs user-management rights; without them SCIM answers 401/403.
- Never print tokens, the server address, or user names other than your own test user. JSON answers hold the server address in `links` / `meta.location`: do not copy them into reports.

## Prerequisites
1. **USERNAME is free** (Step 3 preflight shows `existingUser.found false`). If it exists, pick another name; never change an existing user.

## Step 2. Plan (offline)
```bash
cd "<FSCR>"; python -B core/getting-started/implementation-users/scripts/prepare_implementation_user_plan.py \
  --username "<USERNAME>" --email "<EMAIL>" --last-name "<USERNAME>" --project-id "<any short id>" \
  --execution-mode execute --output "<RUN>/plan.json"
```
The plan lists 3 setup job roles (Application Implementation Consultant, IT Security Manager, Application Diagnostic Administrator) (VERIFIED). **For a test user, empty them** (a small edit of the JSON in RUN, not of FSCR):
```bash
python -c "import json,sys;p=sys.argv[1];d=json.load(open(p));d['baseJobRoles']=[];d['abstractRoles']=[];d['finalRoleAssignments']=[];json.dump(d,open(p,'w'),indent=2)" "<RUN>/plan.json"
```
For a real implementation user keep the 3 roles (and the approval rule in Rules 1).

## Step 3. Read-only preflight
Still in `<FSCR>`:
```bash
python -B core/getting-started/implementation-users/scripts/execute_implementation_user_plan.py --plan "<RUN>/plan.json" \
  --live-preflight --token-cache auto --no-include-roles-in-user-body --skip-role-assignments --audit-output "<RUN>/preflight.json"
```
Want `Result: live_preflight_completed` and in `preflight.json` `"existingUser": {"found": false}` (VERIFIED). `Result: stopped_existing_user_found` = the name is taken: choose another.

## Step 4. Create
Still in `<FSCR>`, the Step 3 command with `--execute --confirm-create-user` in place of `--live-preflight`, keeping `--no-include-roles-in-user-body --skip-role-assignments`, and `--audit-output "<RUN>/execute.json"`. Want `Result: completed` (VERIFIED, about 10 s); the `create_user_account` step has `status success` and its `response.id` is **USERGUID**: `python -c "import json,sys;print([s['response']['id'] for s in json.load(open(sys.argv[1]))['steps'] if s['name']=='create_user_account'][0])" "<RUN>/execute.json"`. Passwords never go in a plan, body or log; Fusion mails EMAIL a password set-up link (for a test user nobody reads it, so nobody can sign in).
**Dropped connection after the POST:** do not run Step 4 again; wait 2 minutes and do Step 6.

## Step 5 (optional). Give your own test user a job role
Only for your own new test user (another skill needs it, for example a data access grant needs the role first). Copy the plan, put the roles in it, and run the executor on the existing user:
```bash
python -c "import json,sys;d=json.load(open(sys.argv[1]));d['baseJobRoles']=[{'displayName':'<ROLE NAME>','roleCode':'<ROLE_CODE>'}];d['finalRoleAssignments']=['<ROLE NAME>'];json.dump(d,open(sys.argv[2],'w'),indent=2)" "<RUN>/plan.json" "<RUN>/plan_roles.json"
python -B core/getting-started/implementation-users/scripts/execute_implementation_user_plan.py --plan "<RUN>/plan_roles.json" \
  --execute --confirm-create-user --assign-roles-to-existing --token-cache auto --audit-output "<RUN>/roles.json"
```
- `ROLE_CODE` is the role's `ORA_..._JOB` code (for example `ORA_GL_GENERAL_ACCOUNTANT_JOB` for General Accountant). Several roles = several entries.
- **Known false alarm (VERIFIED):** each `assign_role_via_scim_roles` step shows `status error` ("REST client failed") although the role **was** added: Oracle answers the SCIM PATCH with an empty body and FSCR's client cannot read it as JSON. Do not repeat the step; prove it with Step 6 (`roles` list).
- `--assign-roles-to-existing` works on any existing user: use it **only** on your own test user.

## Step 6. Read back
```bash
cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" /hcmRestApi/scim/Users --scim-only \
  --query 'filter=userName eq "<USERNAME>"' --query attributes=id,userName,active --no-open-browser --output u.json > u.log 2>&1
timeout 120 python -B "<W>" "<FSCR>" /hcmRestApi/scim/Users/<USERGUID> --scim-only --no-open-browser --output u1.json > u1.log 2>&1
timeout 120 python -B "<W>" "<FSCR>" /hcmRestApi/resources/11.13.18.05/userAccounts \
  --query "q=Username='<USERNAME>'" --query onlyData=true --query fields=Username,SuspendedFlag,PersonId --no-open-browser --output ua.json > ua.log 2>&1
```
- `u.json`: 1 item in `Resources` (the list has no `totalResults`; count the array), `active true`, `id` = USERGUID (VERIFIED). (`attributes=roles` in a filtered list gives HTTP 400 "Attribute roles is not a valid attribute", VERIFIED: read roles from the single user, `u1.json`.)
- `u1.json`: `roles` lists the role codes (`value`); a no-role user has **no `roles` key at all** (VERIFIED, with 3 roles after Step 5).
- `ua.json`: `count 1`, `SuspendedFlag false`, `PersonId null` (no HR person, VERIFIED).

## Rules and limits
1. A real implementation user (with the 3 setup roles) is a security change: only with the environment owner's written approval. A **test user with no roles**, or with roles only for your own tests, named with your prefix and a mailbox nobody reads, is a new record nobody uses.
2. Never update, suspend, or change roles of an existing user other than your own test user.
3. FSCR lists the processes "Retrieve Latest LDAP Changes" and "Import Users and Roles into Application Security"; they were not needed for the steps above (VERIFIED) and affect every user: do not start them.
4. Never print or save other people's user names, tokens or the server address.

## Worked example (2026-11-25, batch 11)
| Step | Record | Result |
|---|---|---|
| preflight | `GAPFILL_AB_B11_U1` | not found (OK) |
| create (no roles) | `GAPFILL_AB_B11_U1` | `completed`; SCIM read: active, no roles; userAccounts: not suspended, no person |
| Step 5 | 3 roles (General Accountant, Buyer, Order Administrator) on `GAPFILL_AB_B11_U1` | 3 PATCH steps "error" (empty body), SCIM read shows the 3 roles |
| fresh test | see CHANGELOG.md | |
