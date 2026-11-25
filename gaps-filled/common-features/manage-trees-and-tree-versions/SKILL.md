---
skill_id: "gosaas.gap-fills.common-features.manage-trees-and-tree-versions"
name: "Manage Trees and Tree Versions: new tree with one DRAFT version (GoSaaS gap fill)"
description: "Create one new tree on an existing active tree structure (tested on the accounting flexfield structure GL_ACCT_FLEX) with its data source parameters and one DRAFT version, through FSCR's setup-task CSV export and FSM CSV import (FND_APP_TREE, ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER, ORA_FND_APP_TREE_VERSION). All ids are read live by REST from a template tree by the helper scripts/tree_rows.py. Read back by REST (fndTreeVersions) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 07, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_TREES_AND_TREE_VERSIONS"
task_name: "Manage Trees and Tree Versions"
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
  - "gosaas common-features/manage-trees-and-tree-versions/scripts/tree_rows.py"
  - "gosaas common-features/manage-value-sets (a value set for the tree, if you need a new one)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new tree and one DRAFT version. A draft version is not used by any process until it is audited and made active (screen steps, not covered). It may not be deletable; plan as if it stays."
---

# Manage Trees and Tree Versions (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag). FSCR's `core/fusion-api/apps-common/trees` skill creates trees by REST (`POST fndTrees`) under its own project workflow; this skill is the **CSV route** and was tested live. It runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A tree is an instance of a tree structure (for example an account hierarchy on `GL_ACCT_FLEX`); a tree has one or more **versions** (date ranges), and the nodes live in a version. Use this skill to create a **new tree with one empty DRAFT version**. To add nodes as well, use the "Manage Account Hierarchies" gap skill (same package, same helper, `--root`/`--child`). Do not use it to change an existing tree or version.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-trees-and-tree-versions/scripts   (tree_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
STRUCT  = the tree structure code (tested: GL_ACCT_FLEX)
TEMPLATE= TreeCode of an existing tree of STRUCT that HAS nodes (copy its parameters)
TREE    = new TreeCode (also TreeName), starting with PREFIX, upper case, letters, digits and _ (VERIFIED with 17 characters)
VS      = the value set code the new tree uses (an existing character value set, Prerequisite 1)
START   = version start date, YYYY/MM/DD
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
1. **A value set VS** (independent, character) for the new tree. Use a test value set you made earlier, or make one with the gap skill `manage-value-sets` (FND_MANAGE_APPLCORE_VALUE_SETS). Check it exists:
   `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource valueSets --q "ValueSetCode='<VS>'" --fields ValueSetCode,ValidationType,ValueDataType --out "<RUN>/vs.json" --expect-count 1` (VERIFIED). Do not point a test tree at a value set that real charts of accounts use.
2. **A template tree TEMPLATE of STRUCT that has nodes** (any existing tree; it is only read). List trees: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource fndTrees --q "TreeStructureCode='<STRUCT>'" --fields TreeStructureCode,TreeCode --out "<RUN>/trees.json"` (VERIFIED; note: `fndTrees` with `q` on two columns joined by `and` returned 0 rows, one column works).
3. STRUCT must be **active** (VERIFIED for `GL_ACCT_FLEX`: status ACTIVE in the structures export).

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_TREES_AND_TREE_VERSIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 10 files (VERIFIED, 1 to 2 minutes): `FND_APP_TREE.csv` (11 columns), `ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv`, `ORA_FND_APP_TREE_VERSION.csv` (23), `ORA_FND_APP_TREE_VERSION_NODE.csv` (34), `ORA_FND_APP_TREE_DATA_SOURCE_LABEL.csv`, four HCM files (`ORA_FND_APP_TREE_PER_..._TREE_STRUCTURE.csv`) and `ASM_SETUP_CSV_METADATA.xml`. TREE must not be in `FND_APP_TREE.csv`.

## Step 3. Build the package (helper reads every id live)
```bash
python -B "<T>/tree_rows.py" --fscr "<FSCR>" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name tree_new.zip --prefix <PREFIX> --structure <STRUCT> --template-tree "<TEMPLATE>" \
  --tree <TREE> --value-set <VS> --start-date <START>
```
What it does (VERIFIED): REST `fndTreeNodes` (finder `TSCodeAndTCodeRowFinder`) on TEMPLATE gives the structure's data source ids and TEMPLATE's value set (the `Pk2StartValue` of its nodes; give `--template-value-set` if the nodes show more than one); REST `fndTreeDataSourceParams` (finder `TreeDataSourceParamsRowFinder`) per data source gives the `ParameterId`/`ParameterValue` tuples; every value equal to TEMPLATE's value set becomes VS. Then it writes, through `build_fsm_package.py`:
- 1 `FND_APP_TREE.csv` row (`SetId=0`),
- 1 parameter row per template parameter (6 for `GL_ACCT_FLEX`: summary flag, value set code and view criteria for each of its 2 data sources),
- 1 `ORA_FND_APP_TREE_VERSION.csv` row: new GUID `TreeVersionId`, `Status=DRAFT`, `ChangedSinceValidation=Y`, `LevelCount=0`, `NodeCount=0`, START to 4712/12/31, name `<TREE>_V1`.
Want: `FND_APP_TREE.csv: 1 new rows`, `ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv: 6 new rows`, `ORA_FND_APP_TREE_VERSION.csv: 1 new rows` and a `TREE_VERSION_ID=` line. A `STOP:` line means nothing was written: fix what it says.
- The rows follow FSCR's trees skill rules: a new version is DRAFT; the tree's parameter tuples must match an existing same-structure tree (here copied from TEMPLATE, with only the value set changed).

## Step 4. Import
**Approval.** The person must approve the environment, the task, TREE, VS and STRUCT before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_TREES_AND_TREE_VERSIONS --task-name "Manage Trees and Tree Versions" \
  --zip-file "<RUN>/payload/tree_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`).
- Short summary of the log (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED, about 30 s): `Application Tree ... Completed successfully`, `Total Objects Failed: 0`. The log also shows an `Application Tree ... In progress` line and row counts per file (0, 1, 7): normal. The log is not the proof: Step 5 is.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 5.
- Rows failed: copy the message, change one thing, retry at most 3 times with a new TREE. `JBO-26041` at the insert: fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it). GUESS

## Step 5. Read back (the proof)
1. REST:
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource fndTreeVersions \
  --finder "AllVersionsRowFinder;TreeCode=<TREE>,TreeStructureCode=<STRUCT>" \
  --fields TreeStructureCode,TreeCode,TreeVersionName,Status,EffectiveStartDate,EffectiveEndDate \
  --out "<RUN>/readback.json" --expect "TreeCode=<TREE>,Status=DRAFT"
```
Want 1 row and `READBACK: PASS` (VERIFIED).
2. Export again (Step 2 into `<RUN>/export_after`, unzip) and compare:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_TREE.csv=TreeStructureCode,TreeCode" \
  --key "ORA_FND_APP_TREE_VERSION.csv=TreeStructureCode,TreeCode,TreeVersionName" \
  --key "ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv=FND_APP_TREE.TreeStructureCode,FND_APP_TREE.TreeCode,ParameterId" \
  --key "ORA_FND_APP_TREE_DATA_SOURCE_LABEL.csv=FND_APP_TREE.TreeStructureCode,FND_APP_TREE.TreeCode,TreeLabelId" \
  --key "ORA_FND_APP_TREE_VERSION_NODE.csv=ORA_FND_APP_TREE_VERSION.TreeVersionId,TreeNodeId" \
  --expect "FND_APP_TREE.csv=<STRUCT>,<TREE>" --expect "ORA_FND_APP_TREE_VERSION.csv=<STRUCT>,<TREE>,<TREE>_V1" \
  --expect "ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv=<STRUCT>,<TREE>,<ParameterId 1>" ... (one --expect per ParameterId in the payload's parameter file)
```
List the ParameterIds with `python -I -c "import csv,sys; [print(r['ParameterId']) for r in csv.DictReader(open(sys.argv[1],encoding='utf-8'))]" "<RUN>/payload/ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv"`. `RESULT: PASS` = only your tree, version and parameters added (VERIFIED).

## Rules and limits
1. New trees only. Never re-import or change an existing tree or version; never import a full export.
2. The version stays DRAFT. Audit, activation and flattening are screen steps (FSCR's trees skill says the same); not covered.
3. Tested on `GL_ACCT_FLEX` only. Other structures (HCM department or organization trees, project task hierarchies) have other parameters and node tables: GUESS that the helper works for them as long as TEMPLATE has nodes.
4. Test records may stay for good. This skill never deletes.
5. Tested on one environment (release 11.13.26.10.0). Python flags: `-B` without `-I` for FSCR scripts, `rest_read.py` and `tree_rows.py`; `-I` for the other helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 49 trees (45 on `GL_ACCT_FLEX`), 95 versions; 1 to 2 minutes |
| Rows | tree `GAPFILL_AB_B7_TR1`, 6 parameters copied from an existing account tree with the value set replaced by a test value set, version `GAPFILL_AB_B7_TR1_V1` DRAFT from 2026/01/01 (the same rows `tree_rows.py` writes; the helper was dry-run checked against them) |
| Import | ProcessId 100004742423501, about 30 s, `Total Objects Failed: 0` |
| Read back | REST fndTreeVersions 1 row DRAFT; export compare: tree 1, version 1, parameters 6 added, nothing else changed: PASS |
