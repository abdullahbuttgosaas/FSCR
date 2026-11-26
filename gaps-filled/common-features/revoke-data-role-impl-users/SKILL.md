---
skill_id: "gosaas.gap-fills.common-features.revoke-data-role-impl-users"
name: "Revoke Data Role from Implementation Users: remove a role from a user by REST hcm userAccounts/userAccountRoles (GoSaaS gap fill, written, unsafe to test)"
description: "Removes a data role from an implementation user through the REST child resource userAccounts/{id}/child/userAccountRoles (delete). Not run: the task is a delete, which the test rules forbid. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 20, 2026-11-26. Resource describe VERIFIED; delete not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_REVOKE_DATA_ROLE_FROM_IMPLEMENTATION_USERS"
task_name: "Revoke Data Role from Implementation Users"
dataloader_import_mode: "REST"
type: "delete"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "FND_CREATE_DATA_ROLE_FOR_IMPLEMENTATION_USERS (the data role was given before)"
side_effects:
  - "Step 3 (not run) removes a role from a user: the user loses access at once. It cannot be undone by this skill (a new grant is a separate task)."
---

# Revoke Data Role from Implementation Users (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: the task export is refused (task flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-26). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.
> **Status: written, unsafe to test.** The task's only action is a **delete** (remove a role grant). The test rules forbid deleting any record, even an own one.

## What it is and when to use
An implementation user got a data role (for example a role for one business unit) during setup; when the setup ends, the role is removed. REST: `hcm userAccounts` (VERIFIED: get, create, upsert) has the child `userAccountRoles` (VERIFIED by describe: create, delete, get). Removing the child row revokes the role. SCIM `/hcmRestApi/scim/Roles` PATCH can also remove members from a role (Oracle docs; GUESS here).

## Why it is unsafe to test here
1. It is a delete. Our rules allow only new records.
2. On another person's user it removes their access (security change).
What would make it safe: the person's written approval to delete, on an own test user (for example the GAPFILL worker user of Import Worker Users) that first gets an own test role.

## Placeholders
```text
FSCR, W, RUN = as in import-worker-users
H     = /hcmRestApi/resources/11.13.18.05
PID   = the PersonId of the user (never list users without a filter)
ROLE  = the RoleCode of the data role to remove
```

## Step 1. Read the user's roles (read only, VERIFIED for the resource)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <H>/userAccounts --query "q=PersonId=<PID>" --query onlyData=true --query expand=userAccountRoles --no-open-browser --output ua.json > ua.log 2>&1
```
Find the row with `RoleCode` = ROLE. Its self link (in `ua.json`, never print it) is the child item to remove. Never print `Username`.

## Step 2. Approval
The person names the user, the role and says to delete it, in writing.

## Step 3. Remove the role ONCE (GUESS, not run)
`DELETE <H>/userAccounts/<GUID>/child/userAccountRoles/<UserRoleId>` with FSCR's REST client (`--method DELETE`).

## Step 4. Read back (GUESS)
Step 1 again: ROLE is gone; the other roles are unchanged.

## Rules and limits
1. Never run Step 3 without the person's written approval naming the user and the role.
2. Never remove a role from your own sign-in user (you may lock yourself out).

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused, flag N |
| REST | `userAccounts` child `userAccountRoles` describe: create, delete, get (VERIFIED) |
| Delete | not run (unsafe: delete) |
