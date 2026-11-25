---
skill_id: "gosaas.gap-fills.common-features.create-implementation-users"
name: "Create Implementation Users: route to FSCR's own implementation-users skill (GoSaaS gap fill, written, not load-tested)"
description: "Points the setup task Create Implementation Users to FSCR's existing core skill core/getting-started/implementation-users (SCIM /hcmRestApi/scim/Users and /Roles), with the safety rules for a shared environment. Not load-tested: it creates a sign-in account with security roles. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 09, 2026-11-25. Written from FSCR's own skill and REST describes; nothing created. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_CREATE_IMPLEMENTATION_USERS"
task_name: "Create Implementation Users"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "written (unsafe to test on a shared environment)"
depends_on:
  - "core.getting-started.implementation-users (FSCR, does the work)"
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
side_effects:
  - "Execute mode creates one Fusion user account and grants it three job roles (Application Implementation Consultant, IT Security Manager, Application Diagnostic Administrator)."
---

# Create Implementation Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** Finding: FSCR **does** have a skill for this work, `core/getting-started/implementation-users`, but FSCR's catalog does not map it to the setup task code `FND_CREATE_IMPLEMENTATION_USERS`, so the module tracker counts the task as "neither" (no skill, no route). The task has no FSM CSV route (read-only export refused, VERIFIED 2026-11-25).
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.
> **Status: written, not load-tested.** Why: running it creates a real sign-in account with IT Security Manager and setup roles on the shared environment. That is a security change other people did not ask for. Load-test only on an environment you own, with written approval from the security owner. In our sitting even FSCR's read-only preflight was not run (our tool permissions stopped account-related calls), so every live step below is GUESS.

## What it is and when to use
An implementation user is the first account that does setup in a new environment. Use FSCR's skill; this card only adds the task-code link and the shared-environment rules.

## Placeholders
```text
FSCR     = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
RUN      = a NEW empty work folder OUTSIDE FSCR and outside any git repo (plans and logs go here, not in FSCR's project\ folder)
USERNAME = the new user name, starting with your test prefix, e.g. GAPFILL_<INITIALS>_IMPL1
EMAIL    = a mailbox the person controls (Fusion sends the password set-up mail there). Never a colleague's address.
```

## Steps (from FSCR's skill; GUESS for live behaviour)
1. Sign in as in FSCR `core/auth/fusion-oauth-authentication`. The signing-in user needs rights to manage users and roles (for example IT Security Manager); without them SCIM answers 401/403.
2. Plan (offline, writes only a file):
   `cd "<FSCR>"; python -B core/getting-started/implementation-users/scripts/prepare_implementation_user_plan.py --username "<USERNAME>" --email "<EMAIL>" --project-id "<id>" --execution-mode execute --output "<RUN>/plan.json"`
3. Read-only preflight (checks the user does not exist and resolves the three `ORA_` roles by SCIM `name`):
   `python -B core/getting-started/implementation-users/scripts/execute_implementation_user_plan.py --plan "<RUN>/plan.json" --live-preflight`
   Stop if the user exists or a role cannot be resolved.
4. **Approval** in writing (environment, USERNAME, EMAIL, the three roles). Then execute: same command with `--execute --confirm-create-user`. The executor never overwrites an existing user. Passwords never go in a plan, body or log.
5. Read back: SCIM `GET /hcmRestApi/scim/Users?filter=userName eq "<USERNAME>"` (through FSCR's client with `--scim-only`) shows the user active, and `GET /hcmRestApi/scim/Roles?filter=name eq "<ORA_ROLE_CODE>"` membership lists it. Alternative read: `GET /hcmRestApi/resources/11.13.18.05/userAccounts?q=Username='<USERNAME>'&fields=Username,SuspendedFlag` (the resource exists and also allows create and upsert, VERIFIED by `/describe`; child `userAccountRoles`).
6. FSCR lists "Retrieve Latest LDAP Changes" and "Import Users and Roles into Application Security" as scheduled processes to run before; on a shared environment do not start them yourself (they affect every user). GUESS

## Rules and limits
1. Only on an environment you own, or with written approval of its security owner.
2. Never update, suspend or change roles of an existing user (do not use `--assign-roles-to-existing` on a shared environment).
3. Never print or save user names other than your own test user name, tokens or the server address.

## Worked example
None: not load-tested (see Status). Verified only: no FSM CSV route; `userAccounts` resource has `get`, `create`, `upsert`.
