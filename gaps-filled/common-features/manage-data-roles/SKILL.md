---
skill_id: "gosaas.gap-fills.common-features.manage-data-roles"
name: "Manage Data Role and Security Profiles: create one HCM data role as a copy of an existing one by FSM CSV (GoSaaS gap fill)"
description: "Creates ONE new HCM data role (PER_HCM_DATA_ROLE + its security profile rows ORA_PER_HCM_DATA_ROLE_PROFILE) by copying an existing data role's job role and security profiles under a new name, through the task's FSM CSV package. The new role is assigned to nobody. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 16, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES"
task_name: "Manage Data Role and Security Profiles"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Step 3 creates a new data role: a security role that inherits the source's job role and grants the data its security profiles give (for example View All People). Nobody has it until a security administrator assigns it. There is no delete by CSV."
---

# Manage Data Role and Security Profiles (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
An HCM data role = a job role + one security profile per secured HCM object (person, organization, position, payroll, ...). The task's package (VERIFIED, 2 files):
- `PER_HCM_DATA_ROLE.csv`: one row per data role (`DataRoleName`, `GroupingKey`, `DataRoleDisplayName`, `AppRoleName`, `InheritedJobRoleCommonName`, `DelegationAllowedFlag`, `DataRoleIdResolverName`, id columns)
- `ORA_PER_HCM_DATA_ROLE_PROFILE.csv`: one row per data role and secured object (`PER_HCM_DATA_ROLE.DataRoleName`, `DataRoleName`, `HrSecuringObject`, `GroupingKey` = `<role>,<object>`, `StartDate`, `SecurityProfileName`, id columns)
Use it to create a data role. The safe way, used here, is a **copy**: a working data role's job role and security profiles under a new name (a round trip), so every value is one Oracle already accepts. Change the profiles afterwards only for an approved real role.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
CP    = <GAPS>/common-features/manage-data-roles/scripts/copy_data_role.py   (offline package builder)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
PREFIX= your test prefix, e.g. GAPFILL_XX_
SRC   = the data role to copy (from Step 1's list; prefer one that is itself a test role)
DR    = new data role name = PREFIX + short name, at most 30 characters (e.g. GAPFILL_XX_DR1)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; with a valid cached sign-in it returns at once). About one hour. Steps 1 and 3 use the cached sign-in: if one fails with HTTP 401/403 or hangs, sign in again and repeat that step (an import only after checking with an export that it did not run). Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name). The ZIP's `ASM_SETUP_CSV_METADATA.xml` holds the environment name and a user name: never print it.

## Prerequisites
None besides the source role (Step 1 lists them). The builder refuses a `<DR>` that already exists.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys; d=sys.argv[1]; n={}; [n.__setitem__(r['DataRoleName'],n.get(r['DataRoleName'],0)+1) for r in csv.DictReader(open(d+'/ORA_PER_HCM_DATA_ROLE_PROFILE.csv',encoding='utf-8-sig'))]; [print(r['DataRoleName'],'| job',r['InheritedJobRoleCommonName'],'| profiles',n.get(r['DataRoleName'],0)) for r in csv.DictReader(open(d+'/PER_HCM_DATA_ROLE.csv',encoding='utf-8-sig'))]" "<RUN>/exp1/unz"
```
2 CSVs + metadata; the last line lists every data role with its job role and number of profiles. Pick `<SRC>`: a role with job role other than `Predefined` and at least one profile. Prefer a role made for testing (its name says TEST, or it starts with your team's prefix); the copy gets the same data access, so avoid copying a role with wide profiles when a narrower one will do. The counts change from run to run as roles are added. No ZIP: run again into a NEW folder, up to 3 tries, and use that folder in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<CP>" --export-dir exp1/unz --source <SRC> --new <DR> --prefix <PREFIX> --out-dir pay --zip-name dr.zip
```
The builder refuses a `<DR>` that does not start with `<PREFIX>`, is longer than 30 characters or already exists. Success: `PER_HCM_DATA_ROLE.csv: 1 new row (<DR>, job role ...)`, `ORA_PER_HCM_DATA_ROLE_PROFILE.csv: N new rows (securing objects: ...)` and `wrote pay\dr.zip`. The builder copies the source's job role, delegation flag and profiles, sets the names, `GroupingKey` and `DataRoleIdResolverName` to `<DR>`, and empties every id column (Oracle makes new ids).

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES --task-name "Manage Data Role and Security Profiles" --zip-file "<RUN>/pay/dr.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be an absolute path. Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed` (the log counts the role only), `HCM Data Role Security Profile` and `HCM Data Role` both `Completed successfully`. Print only these grep lines (the log holds the environment name and user). If the grep finds no `*_process_log.txt`, read the last lines of `imp.log` for the error (the import did not finish); check with Step 4's export before any new try. Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again (Step 1's first two lines with `exp1` replaced by `exp2` everywhere), then compare, expecting exactly your role and its profile rows:
```bash
cd "<RUN>"; mapfile -t X < <(python -I -c "import csv,zipfile,io,sys; z=zipfile.ZipFile(sys.argv[1]); [print('--expect\nORA_PER_HCM_DATA_ROLE_PROFILE.csv='+r['DataRoleName']+','+r['HrSecuringObject']) for r in csv.DictReader(io.TextIOWrapper(z.open('ORA_PER_HCM_DATA_ROLE_PROFILE.csv'),encoding='utf-8'))]" pay/dr.zip | tr -d '\r')
python -I "<CMP>" exp1/unz exp2/unz --key "PER_HCM_DATA_ROLE.csv=DataRoleName" --key "ORA_PER_HCM_DATA_ROLE_PROFILE.csv=DataRoleName,HrSecuringObject" --expect "PER_HCM_DATA_ROLE.csv=<DR>" "${X[@]}"
```
`RESULT: PASS` = one data role and its profile rows added, nothing removed or changed. (The export shows `GeneratedDataRoleId` empty for the new role, as for most existing roles: VERIFIED.)

## Rules and limits
1. New data roles only: never send a row of an existing role (a re-import updates it). There is no delete by CSV.
2. Never assign the test role to a user. Copy a test role, or a role with harmless profiles, when you can.
3. Changing the job role or profiles of the copy was not tested (GUESS: the security profile names must exist and match the job role's secured objects).
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Export | 13 data roles, 127 profile rows (your counts will differ) |
| Import | `GAPFILL_AB_B16_DR1` copied from `HCM_DATA_ROLE_TEST_DATA` (job role HCM integration specialist, 11 profiles): ProcessId 100004744433931; 1 processed, 0 failed |
| Compare | roles 13 → 14, profiles 127 → 138, only own rows added: PASS |
| Fresh test (another tester, only this skill) | `GAPFILL_AB_B16_DR2F` from the same source: ProcessId 100004743457132; roles 14 → 15, profiles 138 → 149: PASS |
