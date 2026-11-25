---
skill_id: "gosaas.gap-fills.common-features.manage-account-hierarchy-labels"
name: "Manage Account Hierarchy Labels: new label on the accounting flexfield tree structure (GoSaaS gap fill)"
description: "Create one new tree label on the accounting flexfield hierarchy structure (GL_ACCT_FLEX, labeling scheme GROUP) through FSCR's setup-task CSV export and FSM CSV import (FND_APP_TREE_LABEL with its parent structure and data source rows copied unchanged), then read it back by REST (fndLabels) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 07, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_GL_MANAGE_ACCOUNT_HIERARCHY_LABELS"
task_name: "Manage Account Hierarchy Labels"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
  - "gosaas common-features/manage-profile-options/scripts/copy_parent_rows.py"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new label on the GL_ACCT_FLEX structure. The label shows in the label list of account hierarchies; no tree node uses it. It may not be deletable; plan as if it stays."
---

# Manage Account Hierarchy Labels (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. FSCR's `core/fusion-api/apps-common/trees` skill covers trees and nodes by REST but not this CSV route. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
An account hierarchy label (for example "Parent1") is a **tree label** of the accounting flexfield tree structure `GL_ACCT_FLEX`. The structure uses labeling scheme **GROUP**: a label is assigned to tree nodes by choice, for example to mark the level of a parent account. Labels belong to the structure's **parent values** data source. Use this skill to add a **new** label. Do not use it to rename or end-date an existing label (that is an update of a shared record).

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
P       = <GAPS>/common-features/manage-profile-options/scripts      (copy_parent_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
LABEL   = new LabelName (also LabelShortName), starting with PREFIX, upper case, letters, digits and _ (VERIFIED with 18 characters)
DS      = the DataSourceId of GL_ACCT_FLEX's parent values data source (read live in Step 3)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
None to create. The structure `GL_ACCT_FLEX` is seeded and must be in the export (Step 2). Its structure row and its parent values data source row are **parents** of the label row: they go into the package **unchanged** (Step 4). This is allowed for a seeded parent only because it is copied byte for byte; Step 6 must show it "changed 0".

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_GL_MANAGE_ACCOUNT_HIERARCHY_LABELS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 6 files (VERIFIED, about 30 s): `FND_APP_TREE_STRUCTURE.csv` (at least the `GL_ACCT_FLEX` row), `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv` (at least its 2 rows: detail values and parent values), `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE_PARAMETER.csv`, `ORA_FND_APP_TREE_STRUCTURE_RELATIONSHIP.csv`, `FND_APP_TREE_LABEL.csv` (the labels, 15 columns) and `ASM_SETUP_CSV_METADATA.xml`. Custom structures made by other people (or earlier test runs) and their labels can be in these files too (VERIFIED: a later export had 3 structures and 11 labels): that is normal, the steps below only use the `GL_ACCT_FLEX` rows. Take this export **right before** your import: Step 6 compares against it, and labels another person adds in between would show up as extra rows.
- If the export stops with no ZIP (for example `The read operation timed out`), run it again into a new folder; it is read-only. Up to 3 tries (VERIFIED: a second try worked).

## Step 3. Read the data source id live and check the name is free
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource fndLabels \
  --finder "TreeStructureCodeRowFinder;TreeStructureCode=GL_ACCT_FLEX" \
  --fields TreeStructureCode,DataSourceId,LabelId,LabelName,LabelShortName --out "<RUN>/labels_before.json"
```
- All existing labels share one `DataSourceId`: that is **DS** (VERIFIED: 9 labels, one data source, the one whose `DataSourceName` in the export is "Accounting Flexfield Hierarchy Parent Values"). Check that the same id is a row of `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv`.
- LABEL must not be in the list (REST and `FND_APP_TREE_LABEL.csv`).

## Step 4. Build the package: one label row + the two parent rows unchanged
```bash
LID=$(python -I -c "import uuid;print(uuid.uuid4().hex.upper())")
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name label_new.zip --prefix <PREFIX> \
  --key "FND_APP_TREE_LABEL.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,LabelName" \
  --prefix-col "FND_APP_TREE_LABEL.csv=LabelName" \
  --row "FND_APP_TREE_LABEL.csv|FND_APP_TREE_STRUCTURE.TreeStructureCode=GL_ACCT_FLEX|ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.DataSourceId=<DS>|LabelId=$LID|EffectiveStartDate=<YYYY/MM/DD>|EffectiveEndDate=4712/12/31|SetId=0|LabelName=<LABEL>|LabelShortName=<LABEL>|Description=<short text>"
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name label_new.zip --file FND_APP_TREE_STRUCTURE.csv --where TreeStructureCode=GL_ACCT_FLEX
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name label_new.zip --file ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv --where DataSourceId=<DS>
```
- `LabelId` is a new 32-character upper-case GUID that you generate; Oracle keeps it (VERIFIED: the after-export shows the same id). Dates as `YYYY/MM/DD` (VERIFIED). `SetId=0` like every existing label (VERIFIED). Leave `IconName` and the audit columns empty.
- Do **not** add `--prefix` to `copy_parent_rows.py` here: the parents are seeded; they are copied unchanged, never edited.
- Payload check: label file 1 row, structure file 1 row, data source file 1 row, parameter and relationship files header only (VERIFIED).

## Step 5. Import
**Approval.** The person must approve the environment, the task and LABEL before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_GL_MANAGE_ACCOUNT_HIERARCHY_LABELS --task-name "Manage Account Hierarchy Labels" \
  --zip-file "<RUN>/payload/label_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`): the only key to the full process log.
- About 25 s. Short summary (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED): `A total of 3 rows were processed. 0 rows of them failed` (structure, data source, label), `Application Tree Label ... Completed successfully`, `Total Objects Failed: 0`.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 6.
- Rows failed: copy the message, change one thing, retry at most 3 times with a new LABEL. A generic database error at the insert (`JBO-26041`): fill `CreatedBy` and `LastUpdatedBy` of the label row with the export metadata's `SubmittedBy` (read at run time, never print it). GUESS (not needed here).

## Step 6. Read back (the proof)
1. REST: repeat Step 3 with `--q "LabelName='<LABEL>'" --expect "LabelName=<LABEL>,DataSourceId=<DS>"` and a new `--out`. Want `READBACK: PASS`. VERIFIED
2. Export again (Step 2 with `--output-dir "<RUN>/export_after"`, unzip) and compare:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_TREE_LABEL.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,LabelName" \
  --key "FND_APP_TREE_STRUCTURE.csv=TreeStructureCode" \
  --key "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv=DataSourceId" \
  --expect "FND_APP_TREE_LABEL.csv=GL_ACCT_FLEX,<LABEL>"
```
`RESULT: PASS` = only your label added; the structure and data source rows show `changed 0` (VERIFIED). A label added by someone else between your two exports would show as an extra added row: check its name, it is not yours.

## Rules and limits
1. New labels only. Never change, end-date or re-import an existing label or the structure.
2. The two parent rows go in only unchanged (`copy_parent_rows.py` without editing). If the compare shows a parent row `changed`, stop and report it.
3. The label is not assigned to any tree node here (assignments belong to a tree version: see the "Manage Account Hierarchies" gap skill).
4. Test records may stay for good. This skill never deletes.
5. Tested on one environment (release 11.13.26.10.0). Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for the other helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 9 labels (Parent1..Parent9), 1 structure, 2 data sources; about 30 s |
| REST fndLabels | 9 rows, one DataSourceId (parent values) |
| Import | `GAPFILL_AB_B7_AHL1` (ProcessId 100004743403129): 3 rows processed, 0 failed, about 25 s |
| Export after + compare | labels added 1, structure and data source changed 0: PASS |
