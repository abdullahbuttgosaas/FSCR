---
skill_id: "gosaas.gap-fills.common-features.import-worker-users"
name: "Import Worker Users: workers with user accounts (GoSaaS gap fill, written, not load-tested)"
description: "How to load workers together with their user accounts (HCM Data Loader Worker.dat with user details, or the REST resources workers and userAccounts), with the rules for a shared environment. Read checks VERIFIED; loads GUESS: they create people and sign-in accounts. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10, 2026-11-25. Written from REST describes and Oracle's docs; nothing created. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "HRC_IMPORT_WORKER_USERS"
task_name: "Import Worker Users"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "written (unsafe to test on a shared environment)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
  - "gosaas common-features/create-implementation-users (FSCR's SCIM user skill, same safety rules)"
side_effects:
  - "A load creates person records (HR data) and user accounts; Fusion may send password mails and auto-provision roles by its role provisioning rules."
---

# Import Worker Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill or guide for this task and no FSM CSV route (read-only export refused, VERIFIED 2026-11-25). Users of workers are reachable by REST `/hcmRestApi/resources/11.13.18.05/userAccounts` (VERIFIED: `get`, `create`, `upsert`; fields `Username, SuspendedFlag, PersonId, PersonNumber, CredentialsEmailSentFlag, GUID`; child `userAccountRoles`).
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.
> **Status: written, not load-tested.** Why: a worker load creates HR person records **and** sign-in accounts on the shared environment. Fusion's automatic role provisioning may then give those accounts roles (security change), and HR data of test people would show in headcount and HR reports that other people use. Load-test only on an environment you own, with written approval of its HR and security owners.

## What it is and when to use
Oracle's task "Import Worker Users" loads people (workers) with their user details, so that each new worker gets a Fusion account. Oracle's own route for bulk loads is **HCM Data Loader** (`Worker.dat` with `Worker`, `PersonName`, `WorkRelationship`, `WorkTerms`, `Assignment` and `PersonUserInformation` lines) (GUESS, from Oracle's HCM Data Loader docs; not run). One person at a time: REST `workers` (HCM) to create the person, then the user account (GUESS).

## Placeholders
```text
FSCR, W, RUN = as in the gap skill manage-data-access-for-users
PERSON = test person number / name starting with your test prefix
USERNAME = test user name starting with your test prefix
EMAIL  = a mailbox the person controls; never a colleague's address
```

## Step 1. Read (VERIFIED for the resource, GUESS for the filter)
`cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" /hcmRestApi/resources/11.13.18.05/userAccounts --query "q=Username='<USERNAME>'" --query onlyData=true --query fields=Username,SuspendedFlag,PersonNumber --no-open-browser --output ua.json > ua.log 2>&1`
→ `count 0` before a load. Never list user accounts without a filter on your own test name: the rows are other people's user names.

## Step 2. Load (GUESS, not run)
1. **HCM Data Loader (bulk):** build `Worker.dat` (business object Worker) with one test worker and a `PersonUserInformation` line (`UserName=<USERNAME>`), zip it, upload and run "Import and Load Data" (HCM Data Loader). Keep the content ID and request ID. Not covered by FSCR's clients in this pack.
2. **REST (one worker):** POST the person to `/hcmRestApi/resources/11.13.18.05/workers` (legal employer, business unit, hire date, name), then check `userAccounts` for the person's `PersonId`; Fusion creates the account by its user-creation rules, or POST to `userAccounts` with `PersonId` and `Username`.
3. Approval in writing before either load (environment, PERSON, USERNAME, EMAIL, legal employer).

## Step 3. Read back (GUESS)
Step 1 again → `count 1`, `SuspendedFlag false`, `PersonNumber` = your test worker.

## Rules and limits
1. Only on an environment you own, with written approval. Never change, terminate or suspend an existing worker or user.
2. Never use a real person's name or e-mail address for a test worker.
3. Keep every response with person or user data in RUN only.

## Worked example
None: not load-tested (see Status). VERIFIED only: no FSM CSV route; `userAccounts` resource and its actions.
