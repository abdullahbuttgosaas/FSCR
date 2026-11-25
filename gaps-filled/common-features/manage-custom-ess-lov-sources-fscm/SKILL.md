---
skill_id: "gosaas.gap-fills.common-features.manage-custom-ess-lov-sources-fscm"
name: "Manage Enterprise Scheduler Job Definitions and Job Sets (FSCM): create a job-parameter list-of-values source by CSV (GoSaaS gap fill)"
description: "Creates one NEW Enterprise Scheduler (ESS) list-of-values source (the object the task's CSV package holds: ATK_ESSMETA_USER_JOB_LOV_SOURCE) through FSCR's setup-task CSV export/import of ORA_ATK_CUSTOM_ESS_FSCM, and proves it with an export compare. Job definitions and job sets themselves are not in the CSV package. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 12, 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ATK_CUSTOM_ESS_FSCM"
task_name: "Manage Enterprise Scheduler Job Definitions and Job Sets for Financial, Supply Chain Management, and Related Applications"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "tested (batch 12)"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (build_fsm_package.py, compare_fsm_exports.py)"
side_effects:
  - "Creates one new list-of-values source. It is only offered when someone builds a job parameter and picks it; nothing uses it otherwise."
---

# Manage Enterprise Scheduler Job Definitions and Job Sets, FSCM (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV); it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
The task page manages custom ESS job definitions, job sets and the **list-of-values (LOV) sources** that job parameters use. The task's CSV package holds **only the LOV sources** (one file, `ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv`, VERIFIED). So by CSV you can list and add LOV sources; job definitions and job sets are made on the task page (not in the package, VERIFIED by the export). The CRM and HCM tasks (`ORA_ATK_CUSTOM_ESS_CRM`, `ORA_ATK_CUSTOM_ESS_HCM`) export the **same** file with the same rows (VERIFIED): gap skills `manage-custom-ess-lov-sources-crm` and `-hcm` point here.
**Safety:** create a NEW source with your prefix. Never re-import an existing source (that is an update).

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN      = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX   = your test prefix, e.g. GAPFILL_<INITIALS>_
LOVNAME  = the new UserDatasourceName, starting with PREFIX (VERIFIED with 19 characters)
DSDEF    = the data source definition: the DatasourceDefName (view object path) of an existing row of the export (Step 3)
TASK     = ORA_ATK_CUSTOM_ESS_FSCM
TASKNAME = Manage Enterprise Scheduler Job Definitions and Job Sets for Financial, Supply Chain Management, and Related Applications
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the server address or user names (the export's `CreatedBy` / `LastUpdatedBy` columns and the process log hold user names: never print those columns). FSCR's output file names hold the environment name: never copy them into a report.
- On HTTP 401/403, an expired token or a hang: sign in as in FSCR `core/auth/fusion-oauth-authentication` (`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`, in the background; a person completes the browser page; never type credentials).

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code <TASK> --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
VERIFIED (about 30 s): 1 CSV + `ASM_SETUP_CSV_METADATA.xml`. `ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv`, columns `ProductShortName, UserDatasourceName, IsValueset, Description, DatasourceDefName` + 5 audit columns; our environment had 98 rows, all `ProductShortName ATK`, `IsValueset N`, "Created from a Seeded Job Definition". If the export stops with no ZIP, run it again into a new folder, up to 3 tries.

## Step 3. Choose DSDEF and check LOVNAME is free
```bash
python -I -c "import csv,sys; r=list(csv.DictReader(open(sys.argv[1]+'/ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv',encoding='utf-8-sig'))); print(len(r),'rows'); print('name taken' if any(x['UserDatasourceName']==sys.argv[2] for x in r) else 'name free'); [print(x['UserDatasourceName'],'|',x['DatasourceDefName']) for x in r[:5]]" "<RUN>/export_before/unz" "<LOVNAME>"
```
Want `name free`. Take DSDEF from one of the printed rows (the view object behind the list; a test source can reuse an existing one, VERIFIED). For a real source use the view object the job parameter needs. `IsValueset=Y` (a value-set based source) was not tried (GUESS).

## Step 4. Build the package (1 row)
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name lov_new.zip --prefix <PREFIX> \
  --key "ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv=UserDatasourceName" \
  --row "ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv|ProductShortName=ATK|UserDatasourceName=<LOVNAME>|IsValueset=N|Description=test LOV source, not used|DatasourceDefName=<DSDEF>"
```
These 5 values were enough; the audit columns stay empty (VERIFIED). The `--key` stops if LOVNAME already exists.

## Step 5. Import
**Approval.** The person must approve the environment, the task and LOVNAME before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code <TASK> --task-name "<TASKNAME>" \
  --zip-file "<RUN>/payload/lov_new.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.log" 2>&1; grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.log"
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
```
- **Write down the ProcessId.** Expected (VERIFIED, about 25 s): `A total of 1 rows were processed. 0 rows of them failed`, `Enterprise Scheduler Job List of Values Source. Status: Completed successfully`, `Total Objects Failed: 0`.
- **Dropped connection after the process started:** do not import again. Fetch the log by ProcessId: `python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code <TASK> --process-id <ProcessId> --wait-seconds 300 --poll-interval 15 --no-open-browser --token-cache auto --output "<RUN>/import_result/x_process_log.txt"`, then the summary line above.
- Failed row: read `Message Text`, change one thing, new LOVNAME, retry; at most 3 tries. `JBO-26041` at the insert: fill `CreatedBy` / `LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it) (GUESS: not needed here).

## Step 6. Read back (the proof)
Export again (Step 2 into `<RUN>/export_after`; check it made a ZIP, else run again into a new folder). Then:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv=UserDatasourceName" --expect "ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv=<LOVNAME>"
```
Want `RESULT: PASS`: only LOVNAME added, 0 removed, 0 changed (VERIFIED). If other people add sources at the same time, their rows also show as added: check that none of them is yours twice and that removed and changed are 0.

## Rules and limits
1. New sources only. Never re-import, change or delete an existing source.
2. A new source changes nothing until a job parameter uses it; test sources may stay. This skill never deletes.
3. Job definitions and job sets are not in the CSV package: they are made on the task page (out of scope here).
4. Tested on one environment (release 11.13.26.10.0). Python: `-B` without `-I` for FSCR scripts; `-I` for helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B12_LOV1`, ATK, a seeded view object (ProcessId 100004743427019) | 1 row processed, 0 failed; compare PASS (98 → 99, 1 added) |
| fresh test | see CHANGELOG.md | |
