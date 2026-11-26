---
skill_id: "gosaas.gap-fills.common-features.create-data-role-for-implementation-users"
name: "Create Data Role for Implementation Users: one HCM data role on an implementation job role with View All profiles, by FSM CSV (GoSaaS gap fill)"
description: "Creates ONE new HCM data role for implementation users (an implementation job role such as Human Capital Management Application Administrator plus View All security profiles) through the FSM CSV package of Manage Data Role and Security Profiles. The new role is assigned to nobody. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 22, 2026-11-26. Tested live (own test, fresh test). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_CREATE_DATA_ROLE_FOR_IMPLEMENTATION_USERS"
task_name: "Create Data Role for Implementation Users"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas.gap-fills.common-features.manage-data-roles (same package)"
side_effects:
  - "Step 4 creates a new data role (a security role of category DATA) that inherits the implementation job role and grants View All data. Nobody has it until a security administrator assigns it. No delete by CSV."
---

# Create Data Role for Implementation Users (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** This task's own export is refused (task flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-26). The object it creates, an HCM data role with security profiles, has a working FSM CSV route under the task **Manage Data Role and Security Profiles** (`PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES`); this skill uses that package. Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.

## What it is and when to use
Oracle's implementation steps: HCM implementation users need a data role that joins an implementation job role (for example *Human Capital Management Application Administrator*) with **View All** security profiles (people, organizations, positions, payrolls, ...). Use this skill to create that data role by script.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/create-data-role-for-implementation-users/scripts/impl_data_role.py (offline builder)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's REST client unchanged; never prints the server)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path, E:/... style)
PREFIX= your test prefix, e.g. GAPFILL_XX_
JOB   = the implementation job role code (Step 2), e.g. ORA_HRC_HUMAN_CAPITAL_MANAGEMENT_APPLICATION_ADMINISTRATOR_JOB
SRC   = an existing data role whose profiles are all "View All ..." (Step 1)
DR    = new data role name = PREFIX + short name, at most 30 characters
```
Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page; a valid cached sign-in returns at once). About one hour; on HTTP 401/403 or a hang, sign in again (before a new import, check with an export that the last one did not run). Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name); never print `ASM_SETUP_CSV_METADATA.xml`.

## Prerequisites
1. A source data role with View All profiles (Step 1). 2. The job role (Step 2). Nothing else.

## Step 1. Read-only export and pick SRC (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys,collections; d=sys.argv[1]; p=collections.defaultdict(list); [p[r['DataRoleName']].append(r['SecurityProfileName']) for r in csv.DictReader(open(d+'/ORA_PER_HCM_DATA_ROLE_PROFILE.csv',encoding='utf-8-sig'))]; [print(r['DataRoleName'],'| job',r['InheritedJobRoleCommonName'],'| profiles',len(p[r['DataRoleName']]),'| all View All' if p[r['DataRoleName']] and all(s.startswith('View All') for s in p[r['DataRoleName']]) else '') for r in csv.DictReader(open(d+'/PER_HCM_DATA_ROLE.csv',encoding='utf-8-sig'))]" "<RUN>/exp1/unz"
```
Pick `<SRC>`: a role marked `all View All` (prefer a test role). No ZIP: export again into a NEW folder (up to 3 tries) and use it below. Check `<DR>` is not in the list.

## Step 2. Check the job role exists (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" /hcmRestApi/scim/Roles --query 'filter=name eq "<JOB>"' --query attributes=name,displayName --no-open-browser --output "<RUN>/job.json" > job.log 2>&1
python -I -c "import json; print([r['name'] for r in json.load(open('job.json',encoding='utf-8')).get('Resources',[])])"
```
Expect `['<JOB>']`. To list implementation job roles use `filter=name co "APPLICATION_ADMINISTRATOR_JOB"`.

## Step 3. Build (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<B>" --export-dir exp1/unz --source <SRC> --job <JOB> --new <DR> --prefix <PREFIX> --out-dir pay --zip-name dr.zip
```
Success: `PER_HCM_DATA_ROLE.csv: 1 new row (<DR>, job role <JOB>)`, `ORA_PER_HCM_DATA_ROLE_PROFILE.csv: N new rows`, `wrote pay\dr.zip`. The builder refuses a `<DR>` without the prefix, over 30 characters, or already present; it empties every id column.

## Step 4. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES --task-name "Manage Data Role and Security Profiles" --zip-file "<RUN>/pay/dr.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be absolute. Write down the ProcessId. Success: `1 rows were processed. 0 rows of them failed`, `HCM Data Role` and `HCM Data Role Security Profile` `Completed successfully`. Print only these lines (the log holds the environment name and a user). Dropped connection after the ProcessId: never import again; wait 2 minutes and do Step 5.

## Step 5. Read back (VERIFIED)
Export again into `<RUN>/exp2` (Step 1's first two lines with `exp1` replaced by `exp2`), then:
```bash
cd "<RUN>"; mapfile -t X < <(python -I -c "import csv,zipfile,io,sys; z=zipfile.ZipFile(sys.argv[1]); [print('--expect\nORA_PER_HCM_DATA_ROLE_PROFILE.csv='+r['DataRoleName']+','+r['HrSecuringObject']) for r in csv.DictReader(io.TextIOWrapper(z.open('ORA_PER_HCM_DATA_ROLE_PROFILE.csv'),encoding='utf-8'))]" pay/dr.zip | tr -d '\r')
python -I "<CMP>" exp1/unz exp2/unz --key "PER_HCM_DATA_ROLE.csv=DataRoleName" --key "ORA_PER_HCM_DATA_ROLE_PROFILE.csv=DataRoleName,HrSecuringObject" --expect "PER_HCM_DATA_ROLE.csv=<DR>" "${X[@]}"
python -B "<W>" "<FSCR>" /hcmRestApi/scim/Roles --query 'filter=name eq "<DR>"' --query attributes=name,category --no-open-browser --output "<RUN>/rb.json" > rb.log 2>&1
python -I -c "import json; print([(r['name'],r.get('category')) for r in json.load(open('rb.json',encoding='utf-8')).get('Resources',[])])"
```
Expect `RESULT: PASS` (one role and its profiles added, nothing removed or changed) and `[('<DR>', 'DATA')]`.

## Rules and limits
1. New data roles only; never send a row of an existing role (a re-import updates it). No delete by CSV.
2. Never assign the test role to a user.
3. Tested with the HCM application administrator job role and 11 View All profiles; other job roles: GUESS (the profiles must fit the job's secured objects).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Task's own export | refused (task flag N) |
| Import | `GAPFILL_AB_B22_IDR1`, job `ORA_HRC_HUMAN_CAPITAL_MANAGEMENT_APPLICATION_ADMINISTRATOR_JOB`, 11 View All profiles copied from own test role `GAPFILL_AB_B16_DR1`: ProcessId 100004743461592; 1 processed, 0 failed |
| Read back | roles 16 -> 17, profiles 160 -> 171, nothing else changed: PASS; SCIM role category DATA |
| Fresh test | see STATUS.md |
