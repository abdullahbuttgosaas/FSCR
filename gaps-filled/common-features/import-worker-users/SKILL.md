---
skill_id: "gosaas.gap-fills.common-features.import-worker-users"
name: "Import Worker Users: create a worker and check its user account by REST hcm workers and userAccounts (GoSaaS gap fill)"
description: "Creates one worker (person, work relationship, assignment) through the REST resource workers; Fusion then makes the worker's user account by its user-creation rules. Reads the account and its roles back from userAccounts. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10 (written 2026-11-25), tested batch 21 2026-11-26 (own test, fresh test). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "HRC_IMPORT_WORKER_USERS"
task_name: "Import Worker Users"
dataloader_import_mode: "REST"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
  - "a legal employer and a business unit (read live)"
side_effects:
  - "Each POST creates a person (HR record, a new person number) and Fusion creates a user account for it (VERIFIED 2026-11-26: account made, no roles). Role provisioning rules of another environment may add roles: always check Step 4. No delete by REST."
---

# Import Worker Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV route (read-only export refused, VERIFIED 2026-11-25). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.
> Safe test (rule of 2026-11-26): ONE new worker with your test prefix, an `example.invalid` email and no roles is a new record nobody uses. Stop and report if Step 4 shows any role.

## What it is and when to use
Oracle's task "Import Worker Users" loads workers so each gets a Fusion user account. Bulk route: HCM Data Loader `Worker.dat` (GUESS, not run). One worker at a time: REST `workers` (hcm, VERIFIED create), then Fusion makes the account by its user-creation rules; `userAccounts` (hcm, VERIFIED get, create, upsert; child `userAccountRoles`) shows it.

## Placeholders
```text
FSCR = the FSCR root folder (holds core\ and core\auth\fusionEnv.properties). Read only.
W    = <GAPS>/common-features/scripts/rest_call.py   (never prints the server)
RUN  = a NEW empty work folder OUTSIDE FSCR and outside any git repo
H    = /hcmRestApi/resources/11.13.18.05
NAME = the test last name, starting with your test prefix (e.g. GAPFILL_AB_B21_WU1)
EMAIL = NAME in lower case with "_" as ".", then @example.invalid (e.g. gapfill.ab.b21.wu1@example.invalid)
TODAY = the hire date, YYYY-MM-DD
LE, BU = a legal employer and a business unit that existing workers or CRM resources use (2026-11-26: "GS Legal Entity" / "GoSaaS")
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. Never print tokens, the server address or user names.

## Step 1. Check the name is new (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <H>/publicWorkers --query "q=LastName='<NAME>'" --query onlyData=true --query fields=PersonId,PersonNumber,LastName --no-open-browser --output pre.json > pre.log 2>&1
```
`pre.json` must have 0 items. Tip: pass absolute paths to `--body-file` and `--output` in every step (VERIFIED with Windows paths such as `E:/run/pre.json`).

## Step 2. Create the worker ONCE (VERIFIED)
`wu.json`:
```json
{"names":[{"LegislationCode":"US","FirstName":"GAPFILL","LastName":"<NAME>"}],
 "emails":[{"EmailType":"W1","EmailAddress":"<EMAIL>","PrimaryFlag":true}],
 "workRelationships":[{"LegalEmployerName":"<LE>","WorkerType":"E","StartDate":"<TODAY>","assignments":[{"BusinessUnitName":"<BU>","ActionCode":"HIRE"}]}]}
```
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <H>/workers --method POST --body-file wu.json --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" --no-open-browser --output wu_out.json > wu.log 2>&1
python -I -c "import json; d=json.load(open('wu_out.json',encoding='utf-8')); print(d['PersonId'], d['PersonNumber'])"
```
Never print the whole answer: it holds links with the server address. If the connection drops, run Step 1 again before any new POST. `LegislationCode` is the legal employer's country (GUESS for other countries).

## Step 3. Read back the worker (VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <H>/publicWorkers --query "q=LastName='<NAME>'" --query onlyData=true --query fields=PersonId,PersonNumber,LastName --no-open-browser --output post.json > post.log 2>&1
```
Expect 1 row with your NAME and the new PersonNumber (keep `pre.json` as the before state).

## Step 4. Read the user account and its roles (VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <H>/userAccounts --query "q=PersonId=<PersonId>" --query onlyData=true --query expand=userAccountRoles --no-open-browser --output ua.json > ua.log 2>&1
python -I -c "import json; it=json.load(open('ua.json',encoding='utf-8'))['items']; print(len(it), [(i.get('SuspendedFlag'), [r.get('RoleCode') for r in i.get('userAccountRoles',[])]) for i in it])"
```
Expect 1 account, `SuspendedFlag` false, roles `[]` (VERIFIED 2026-11-26). Never print `Username`. If roles appear, stop and report them: the environment's role provisioning rules gave them.

## Rules and limits
1. One test worker per test, with your prefix and an `example.invalid` email. Never a real person's name or address.
2. Never change, terminate or suspend an existing worker or user; never add roles.
3. No delete by REST: test workers stay. Keep all answers in RUN (they hold person data).

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused, task flag `CSVExportImportSupportedFlag N` |
| Own test | worker `GAPFILL_AB_B21_WU1` created (PersonNumber 103); user account made by Fusion, not suspended, 0 roles |
| Fresh test | see STATUS.md (`fresh_claude_pass`) |
