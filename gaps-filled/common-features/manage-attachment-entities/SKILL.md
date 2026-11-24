---
skill_id: "gosaas.gap-fills.common-features.manage-attachment-entities"
name: "Manage Applications Core Attachment Entities (GoSaaS gap fill)"
description: "Create a new Applications Core attachment entity through FSCR's setup-task CSV export and FSM CSV import (FND_APP_ATTACHMENT_ENTITY package), with the application id and module id read live by REST, then read it back with a second export (there is no REST resource). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 1, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES"
task_name: "Manage Applications Core Attachment Entities"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.apps-common.attachments (FSCR reference attachment-entities.md: route only)"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new attachment entity. No category is linked, so no screen shows it. It may not be deletable; plan as if it stays."
---

# Manage Applications Core Attachment Entities (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's attachments reference names this task but only routes it (export + data loader); it gives no row content. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
An attachment **entity** registers a table (and its primary key columns) that attachments can be stored against. **Categories** are then linked to an entity (a different task, `manage-attachment-categories`); only a linked category makes attachments show on a screen. This skill creates **one entity with no category link**, so nothing changes for users.

## When to use
- Someone asks to create a **new** attachment entity for task `FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES`.
- Do **not** use it to change existing entities or to link categories. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
ENTITY  = new EntityName, upper case letters, digits and _, starting with PREFIX (max 40, GUESS)
UNAME   = UserEntityName (the name people see), e.g. "GAPFILL <INITIALS> test entity"
TABLE   = the table the entity points to, and PK1 = its first primary key column.
          The person names them; if not, use FND_LOOKUP_TYPES and LOOKUP_TYPE (an Applications Core table every environment has). VERIFIED
MODULE  = the Applications Core ModuleId, read in Step 3
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED, about 40 s): `FND_APP_ATTACHMENT_ENTITY.csv` (20 columns: `EntityName, ApplicationId, ..., DataObjectCode, DefaultFolder, DmRepository, ..., ModuleId, Pk1Column..Pk5Column, TableName, UserEntityName, CategorySecurityEnabled, ExpirationEnabled` + audit), `ORA_FND_APP_ATTACHMENT_CATEGORY.csv` (category links) and `ASM_SETUP_CSV_METADATA.xml` (scope `moduleType=APPLICATION`, `moduleKey=FND`).
- The export may be **empty** (VERIFIED: 0 entities, 0 links). That is normal: the row is written in full.
- ENTITY must not be in the entity file (the builder checks again). If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries; then **stop**.

## Step 3. Module id (live, REST)
The entity needs the Applications Core `ApplicationId` (always `0`, VERIFIED) and `ModuleId`. Read the ModuleId from the seeded `YES_NO` lookup, which every environment has (never copy it from an export or another environment):
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource standardLookups --q "LookupType='YES_NO'" \
  --fields LookupType,ModuleId --out "<RUN>/fnd_module.json" --expect-count 1
python -I -c "import json,sys;print(json.load(open(sys.argv[1]))['items'][0]['ModuleId'])" "<RUN>/fnd_module.json"
```
Keep it as MODULE; check it is not empty. Exit 2 = sign-in or privilege problem.

## Step 4. Build a package with only the new entity
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name attachment_entity_new.zip --prefix <PREFIX> \
  --key "FND_APP_ATTACHMENT_ENTITY.csv=EntityName" --key "ORA_FND_APP_ATTACHMENT_CATEGORY.csv=CategoryName,EntityName" \
  --prefix-col "FND_APP_ATTACHMENT_ENTITY.csv=EntityName" --max-len "EntityName=40" \
  --row "FND_APP_ATTACHMENT_ENTITY.csv|EntityName=<ENTITY>|ApplicationId=0|ModuleId=<MODULE>|DataObjectCode=<ENTITY>|TableName=<TABLE>|Pk1Column=<PK1>|UserEntityName=<UNAME>|CategorySecurityEnabled=N|ExpirationEnabled=N"
```
- **`DataObjectCode` is required** (VERIFIED: without it the import says `JBO-27014: Attribute DataObjectCode in FndDocumentEntitiesEO is required` and `0 rows were processed`). Give it the same text as ENTITY, upper case: the existing entities in other modules use the upper-case entity name as their data object code (VERIFIED). It was accepted with no data security object behind it.
- Leave `DefaultFolder`, `DmRepository`, `Pk2Column..Pk5Column`, the audit columns and the category file empty. VERIFIED
- Builder must print `FND_APP_ATTACHMENT_ENTITY.csv: 1 new rows` and `ORA_FND_APP_ATTACHMENT_CATEGORY.csv: 0 new rows`.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact ENTITY (and TABLE) before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES --task-name "Manage Applications Core Attachment Entities" \
  --zip-file "<RUN>/payload/attachment_entity_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later.
- About 50 s. Print a short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: [^.]+\.xml\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|JBO-[0-9]+: [^.]{0,120}',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `FndDocumentEntitiesVLSD.xml ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0` (the category object shows `0 rows`, normal). **`0 rows were processed` for the entity object is a failure**, even with "Completed successfully".
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: copy the error, change one thing, retry at most 3 times. A generic database error at the insert (for example `JBO-26041`): first fill `CreatedBy` and `LastUpdatedBy` with the export metadata's `SubmittedBy` (read it at run time, never print it). GUESS (not needed here).

## Step 6. Read back: second export and compare (the proof; no REST resource)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_ATTACHMENT_ENTITY.csv=EntityName" --key "ORA_FND_APP_ATTACHMENT_CATEGORY.csv=CategoryName,EntityName" \
  --expect "FND_APP_ATTACHMENT_ENTITY.csv=<ENTITY>" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your entity was added, nothing removed or changed. Check in `added_rows.csv` that `TableName`, `Pk1Column`, `DataObjectCode` and `UserEntityName` are what you sent (print only those columns; the audit columns hold user names).

## Rules and limits
1. New records only; never import a full export.
2. No category link in a test (a link makes the category show on that entity's screens for every user).
3. Test records may stay for good. This skill never deletes. Record every created entity.
4. Not tested: composite keys (Pk2..Pk5), `DefaultFolder` / `DmRepository`, `CategorySecurityEnabled=Y`, entities of other applications (the export scope is FND only).
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 0 entities, 0 links; 43 s |
| Module id | from `YES_NO`, application 0 |
| Try 1 | `GAPFILL_AB_P1_AE1` without `DataObjectCode`: `JBO-27014 ... DataObjectCode ... is required`, 0 rows processed, **not created** (ProcessId 100004741418453) |
| Diagnosis | read-only export of the all-modules task `FND_MANAGE_ATTACHMENT_ENTITIES`: 22 working entities, each with `DataObjectCode` = upper-case entity name |
| Try 2 | `GAPFILL_AB_P1_AE2`, table `FND_LOOKUP_TYPES`, key `LOOKUP_TYPE`, `DataObjectCode=GAPFILL_AB_P1_AE2` (ProcessId 100004741416829), about 50 s: 1 row processed, 0 failed |
| Export after + compare | 1 entity; added 1, removed 0, changed 0: PASS |
