---
skill_id: "gosaas.gap-fills.common-features.manage-tree-labels"
name: "Manage Tree Labels: new label on a label-enabled tree structure (GoSaaS gap fill)"
description: "Create one new tree label on an existing tree structure whose labeling scheme is not NONE, through FSCR's setup-task CSV export and FSM CSV import (FND_APP_TREE_LABEL with its parent structure and data source rows copied unchanged), then read it back by REST (fndLabels) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 07, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_TREE_LABELS"
task_name: "Manage Tree Labels"
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
  - "Starts one setup-task CSV import that creates one new label on an existing tree structure. No tree node uses it. It may not be deletable; plan as if it stays."
---

# Manage Tree Labels (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. FSCR's `core/fusion-api/apps-common/trees` skill names label definitions (`fndLabels` POST) as a provisional REST route; this skill uses the tested CSV route instead. It runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A tree label is a name that can be put on tree nodes (for example a level name). Labels belong to a **tree structure** and to one of its **data sources** (the one whose row has a `LabelViewObjectDefName`). A structure with labeling scheme `NONE` takes no labels. Use this skill to add a **new** label to a structure that already allows labels. Do not use it to change an existing label. (For the accounting flexfield structure `GL_ACCT_FLEX` there is also the narrower gap skill "Manage Account Hierarchy Labels"; same rows.)

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
P       = <GAPS>/common-features/manage-profile-options/scripts      (copy_parent_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
STRUCT  = TreeStructureCode of the structure (must be in the export, LabelingScheme not NONE)
DS      = DataSourceId of the structure's label data source (Step 3)
LABEL   = new LabelName (also LabelShortName), starting with PREFIX, upper case, letters, digits and _ (VERIFIED with 17 characters)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
1. A tree structure with labeling scheme `LEVEL`, `GROUP` or `DEPTH` (not `NONE`) that is in this task's export. Check in Step 2. VERIFIED: the task scope exported the seeded `GL_ACCT_FLEX` (`GROUP`) and an HCM department structure (`NONE`), plus any custom structures; only `GL_ACCT_FLEX` took labels there. If no structure in the export allows labels: stop and report it.
2. The structure row and the label data source row are **parents** of the label row: they go into the package **unchanged** (Step 4). Step 6 must show them "changed 0".

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_TREE_LABELS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 6 files (VERIFIED, about 30 to 50 s): `FND_APP_TREE_STRUCTURE.csv`, `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv`, `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE_PARAMETER.csv`, `ORA_FND_APP_TREE_STRUCTURE_RELATIONSHIP.csv`, `FND_APP_TREE_LABEL.csv` (15 columns) and `ASM_SETUP_CSV_METADATA.xml`. Row counts change over time: custom structures made by others or by earlier test runs show up here too (VERIFIED). Take it **right before** your import: Step 6 compares against it.
- If the export stops with no ZIP (for example `The read operation timed out`), run it again into a new folder; it is read-only. Up to 3 tries (VERIFIED).
- Pick STRUCT: `python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_before/unz" --value <STRUCT>` shows its rows. Its `LabelingScheme` must not be `NONE`.

## Step 3. Find DS and check the name is free
- In `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv`, DS is the STRUCT row that has `LabelViewObjectDefName` filled (VERIFIED for `GL_ACCT_FLEX`: one such row, its "parent values" data source). This is the parent row you copy in Step 4.
- Confirm it live by REST (existing labels of the structure carry the same id):
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource fndLabels \
  --finder "TreeStructureCodeRowFinder;TreeStructureCode=<STRUCT>" \
  --fields TreeStructureCode,DataSourceId,LabelId,LabelName --out "<RUN>/labels_before.json"
```
  VERIFIED: 9 rows on `GL_ACCT_FLEX`, all with the same DataSourceId as the export row. If the structure has no labels yet, the export row is the only source (GUESS: still correct, the label data source is defined on the structure).
- LABEL must not be in the REST list or in `FND_APP_TREE_LABEL.csv`.

## Step 4. Build the package: one label row + the two parent rows unchanged
```bash
LID=$(python -I -c "import uuid;print(uuid.uuid4().hex.upper())")
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name label_new.zip --prefix <PREFIX> \
  --key "FND_APP_TREE_LABEL.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,LabelName" \
  --prefix-col "FND_APP_TREE_LABEL.csv=LabelName" \
  --row "FND_APP_TREE_LABEL.csv|FND_APP_TREE_STRUCTURE.TreeStructureCode=<STRUCT>|ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.DataSourceId=<DS>|LabelId=$LID|EffectiveStartDate=<YYYY/MM/DD>|EffectiveEndDate=4712/12/31|SetId=0|LabelName=<LABEL>|LabelShortName=<LABEL>|Description=<short text>"
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name label_new.zip --file FND_APP_TREE_STRUCTURE.csv --where TreeStructureCode=<STRUCT>
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name label_new.zip --file ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv --where DataSourceId=<DS>
```
- `LabelId`: a new 32-character upper-case GUID you generate; Oracle keeps it (VERIFIED). Dates `YYYY/MM/DD`; `SetId=0` as on the existing labels (VERIFIED; a structure restricted by set may need another SetId: GUESS). Audit columns and `IconName` empty.
- No `--prefix` on `copy_parent_rows.py`: the parents may be seeded; they are copied, never edited.

## Step 5. Import
**Approval.** The person must approve the environment, the task, STRUCT and LABEL before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_TREE_LABELS --task-name "Manage Tree Labels" \
  --zip-file "<RUN>/payload/label_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`).
- Short summary of the log (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED, about 25 s): `A total of 3 rows were processed. 0 rows of them failed`, `Application Tree Label ... Completed successfully`, `Total Objects Failed: 0`.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 6.
- Rows failed: copy the message, change one thing, retry at most 3 times with a new LABEL. `JBO-26041` at the insert: fill `CreatedBy`/`LastUpdatedBy` of the label row with the export metadata's `SubmittedBy` (read at run time, never print it). GUESS

## Step 6. Read back (the proof)
1. REST: Step 3's read with `--q "LabelName='<LABEL>'" --expect "LabelName=<LABEL>,DataSourceId=<DS>"` and a new `--out`: `READBACK: PASS`. VERIFIED
2. Export again (Step 2 into `<RUN>/export_after`, unzip) and compare:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_TREE_LABEL.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,LabelName" \
  --key "FND_APP_TREE_STRUCTURE.csv=TreeStructureCode" \
  --key "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,DataSourceId" \
  --expect "FND_APP_TREE_LABEL.csv=<STRUCT>,<LABEL>"
```
`RESULT: PASS` = only your label added; parents `changed 0`. If the compare shows one more added label that is not yours, someone else added it between your exports (VERIFIED once in our test: our own other label, made from an older "before" export); the result is then FAIL only for that reason: say so, and check your own label is there with `changed 0` elsewhere.

## Rules and limits
1. New labels only; never change, end-date or re-import an existing label or structure.
2. Parent rows go in only unchanged. A parent `changed` in the compare: stop and report.
3. Labels are not put on nodes here (that is part of a tree version).
4. Test records may stay for good. This skill never deletes.
5. Tested on one environment (release 11.13.26.10.0), structure `GL_ACCT_FLEX` only. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for the other helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export | 2 structures, 3 data sources, 9 labels; about 47 s |
| Import | `GAPFILL_AB_B7_TL1` on `GL_ACCT_FLEX` (ProcessId 100004742423488): 3 rows processed, 0 failed |
| Export after + compare | `GAPFILL_AB_B7_TL1` added, parents changed 0. (The "before" export was older than another label we made a minute earlier, `GAPFILL_AB_B7_AHL1`, so that one showed as an extra added row.) |
