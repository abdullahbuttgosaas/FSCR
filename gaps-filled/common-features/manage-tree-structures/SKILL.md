---
skill_id: "gosaas.gap-fills.common-features.manage-tree-structures"
name: "Manage Tree Structures: new custom tree structure with one value set data source (GoSaaS gap fill)"
description: "Create one new custom tree structure (status DRAFT, labeling NONE) with one data source on character value set values, its value set parameter and its root relationship, through FSCR's setup-task CSV export and FSM CSV import, then read it back with a second export (there is no REST resource for structures). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 07, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_TREE_STRUCTURES"
task_name: "Manage Tree Structures"
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
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new custom tree structure in DRAFT status. No tree uses it. It may not be deletable; plan as if it stays."
---

# Manage Tree Structures (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. FSCR's `core/fusion-api/apps-common/trees` skill says structure changes are "outside this route" and names no structure REST resource. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A tree structure is the template of a tree: which data sources (view objects) give the node values, how they nest, labeling, versioning and flattening. Trees (Manage Trees and Tree Versions) are built on an **active** structure. Use this skill to create a **new custom** structure. It is created in status **DRAFT**: auditing and activating it are screen steps (not covered). Do not use it to change a seeded or existing structure.

The export holds **no custom structure** to copy (VERIFIED: the task scope gave 2 seeded structures), so the rows are written in full. The values below are the ones that imported cleanly.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
STRUCT  = new TreeStructureCode (also its name), starting with PREFIX, upper case, letters, digits and _ (VERIFIED with 17 characters)
APP     = ApplicationId and MODULE = ModuleId of the owning application: copy BOTH from the GL_ACCT_FLEX row of the export (Step 3)
DS, PID = two new GUIDs (data source id, parameter id) you generate
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
None. The structure is stand-alone. (Its data source uses Oracle's public value set values view; no value set is named on the structure: each tree gives its value set later as a parameter value.)

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_TREE_STRUCTURES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 6 files (VERIFIED, about 50 s): `FND_APP_TREE_STRUCTURE.csv` (33 columns), `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv` (27), `ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE_PARAMETER.csv` (12), `ORA_FND_APP_TREE_STRUCTURE_RELATIONSHIP.csv` (10), `FND_APP_TREE_LABEL.csv` (15), `ASM_SETUP_CSV_METADATA.xml`. STRUCT must not be in the structure file. (Earlier GAPFILL structures do show up in this export after they are made: VERIFIED.)
- No REST check: `fndTreeStructures` answers HTTP 404 (VERIFIED). The export is the only read.

## Step 3. Read APP and MODULE
```bash
python -I -c "import csv,sys; r=[x for x in csv.DictReader(open(sys.argv[1]+'/FND_APP_TREE_STRUCTURE.csv',encoding='utf-8-sig')) if x['TreeStructureCode']=='GL_ACCT_FLEX'][0]; print('APP',r['ApplicationId'],'MODULE',r['ModuleId'])" "<RUN>/export_before/unz"
```
APP and MODULE belong together (one application and its module): copy both from the same row. (VERIFIED with the General Ledger pair of `GL_ACCT_FLEX`. These are seeded application ids, not record ids.)

## Step 4. Build the package (4 rows, written in full)
```bash
DS=$(python -I -c "import uuid;print(uuid.uuid4().hex.upper())"); PID=$(python -I -c "import uuid;print(uuid.uuid4().hex.upper())")
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name structure_new.zip --prefix <PREFIX> \
  --key "FND_APP_TREE_STRUCTURE.csv=TreeStructureCode" \
  --key "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,DataSourceId" \
  --key "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE_PARAMETER.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,ParameterId" \
  --key "ORA_FND_APP_TREE_STRUCTURE_RELATIONSHIP.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,ChildDataSourceId" \
  --prefix-col "FND_APP_TREE_STRUCTURE.csv=TreeStructureCode" \
  --row "FND_APP_TREE_STRUCTURE.csv|TreeStructureCode=<STRUCT>|ApplicationId=<APP>|Status=DRAFT|SharingScheme=OPEN|CreationMode=CUSTOMER|Customizable=Y|TreeNodeTable=FND_TREE_NODE|RowFlattenedTable=FND_TREE_NODE_RF|IdColFlattenedTable=FND_TREE_NODE_CF|RefreshInterval=OFFLINE|Versioning=UPDATE|AllowMultipleRootNodes=Y|RestrictByDate=N|RestrictBySetid=N|LabelingScheme=NONE|AllowRaggedNodes=N|AllowSkipLevelNodes=N|NumberOfTrees=1|AllowNodeLevelSecurity=N|TreeStructureName=<STRUCT>|Description=<short text>|AllowMultipleActiveVers=N|ModuleId=<MODULE>|ProtectedFlag=N" \
  --row "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv|FND_APP_TREE_STRUCTURE.TreeStructureCode=<STRUCT>|DataSourceId=$DS|ViewObjectDefName=oracle.apps.fnd.applcore.flex.vst.model.publicView.CharacterValueSetValuePVO|Pk1Column=Value|Pk2Column=ValueSetCode|MaxDepth=-1|AllowAsTerminalNode=Y|UsageLimit=NONE|AllowNodeLevelSecurity=N|AllowDuplicateNodes=N|DataSourceName=<short name>|AllowAsFreeNode=N" \
  --row "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE_PARAMETER.csv|FND_APP_TREE_STRUCTURE.TreeStructureCode=<STRUCT>|ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.DataSourceId=$DS|ParameterId=$PID|ParameterName=Bind_ValueSetCode|Mandatory=Y|ParameterType=BOUND_VALUE" \
  --row "ORA_FND_APP_TREE_STRUCTURE_RELATIONSHIP.csv|FND_APP_TREE_STRUCTURE.TreeStructureCode=<STRUCT>|ChildDataSourceId=$DS|AllowRangeBasedChild=N"
```
Rules for the rows (all VERIFIED unless marked):
- **`NumberOfTrees` and `RestrictByDate` are required** for a new structure even though the seeded rows leave `RestrictByDate` empty: without them the import fails with `JBO-27014: Attribute NumberOfTrees in FndTreeStructureEO is required` and `... RestrictByDate ... is required`, and nothing is created (try 1). `NumberOfTrees=1`, `RestrictByDate=N` worked.
- **Relationship: only the root row** (`ChildDataSourceId=DS`, `ParentDataSourceId` empty). This is the shape of the seeded single-source structure. **Do not add a self row** (`ParentDataSourceId=DS`, `ChildDataSourceId=DS`): its key is the same child data source, so it **replaces** the root row (try 2 created a structure whose only relationship row was the self row; the root row was gone).
- `DataSourceId` and `ParameterId`: new 32-character upper-case GUIDs you generate; Oracle keeps them (VERIFIED in the after-export).
- `ViewObjectDefName`, `Pk1Column=Value`, `Pk2Column=ValueSetCode`: copied from the seeded accounting flexfield data source (public value set values view). A different view object needs its own key columns (GUESS: read them from a seeded data source that uses it).
- `Status=DRAFT`, `CreationMode=CUSTOMER`, `Customizable=Y`, `ProtectedFlag=N`: the structure is the customer's own. GUESS that `ACTIVE` would be refused or would skip the audit; not tried.
- `FND_TREE_NODE` / `FND_TREE_NODE_RF` / `FND_TREE_NODE_CF`: the generic tree tables. VERIFIED accepted; not used by a tree yet.
- Leave the audit columns, label columns and `BiViewObjectDefName` empty.

## Step 5. Import
**Approval.** The person must approve the environment, the task and STRUCT before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_TREE_STRUCTURES --task-name "Manage Tree Structures" \
  --zip-file "<RUN>/payload/structure_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`).
- Short summary of the log (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED, about 30 s): `A total of 4 rows were processed. 0 rows of them failed`, `Application Tree Structure ... Completed successfully`, `Total Objects Failed: 0`.
- `JBO-27014 ... is required` names a missing column: add it (one change), new STRUCT, retry; at most 3 tries. A refused row creates nothing; check with a new export before the next try.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 6.

## Step 6. Read back (the proof: second export and compare)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_TREE_STRUCTURE.csv=TreeStructureCode" \
  --key "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,DataSourceId" \
  --key "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE_PARAMETER.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,ParameterId" \
  --key "ORA_FND_APP_TREE_STRUCTURE_RELATIONSHIP.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,ParentDataSourceId,ChildDataSourceId" \
  --key "FND_APP_TREE_LABEL.csv=FND_APP_TREE_STRUCTURE.TreeStructureCode,LabelName" \
  --expect "FND_APP_TREE_STRUCTURE.csv=<STRUCT>" --expect "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE.csv=<STRUCT>,$DS" \
  --expect "ORA_FND_APP_TREE_STRUCTURE_DATA_SOURCE_PARAMETER.csv=<STRUCT>,$PID" \
  --expect "ORA_FND_APP_TREE_STRUCTURE_RELATIONSHIP.csv=<STRUCT>,,$DS"
```
`RESULT: PASS` = exactly your 4 rows added, nothing removed or changed (VERIFIED). The new structure row shows `Status` `DRAFT`.

## Rules and limits
1. New structures only. Never re-import or change a seeded or existing structure.
2. The structure stays DRAFT: audit and activation are screen steps, not covered. A tree can only be built on an active structure (GUESS from Oracle's docs), so this test structure is not used by a tree.
3. Not tested: several data sources, labels on a custom structure, row/column flattening, other view objects, set or date restrictions.
4. Test records may stay for good. This skill never deletes.
5. Tested on one environment (release 11.13.26.10.0). Python flags: `-B` without `-I` for FSCR scripts; `-I` for the helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B7_TS1` without `NumberOfTrees` and `RestrictByDate`, root + self relationship rows (ProcessId 100004742421534) | refused: `JBO-27014` for both columns; 0 rows processed, nothing created |
| 2 | same STRUCT, `NumberOfTrees=1`, `RestrictByDate=N` (ProcessId 100004742441558) | created (DRAFT); compare: structure, data source, parameter added, but the relationship file got only the self row (the root row was replaced) |
| 3 | `GAPFILL_AB_B7_TS2`, root relationship row only (ProcessId 100004742423588) | 4 rows processed, 0 failed; compare: exactly 4 rows added: PASS |
| fresh test | `GAPFILL_AB_B7_TS3F`, a new Claude with this skill only (ProcessId 100004743404182) | 4 rows processed, 0 failed; compare: exactly 4 rows added (DRAFT): PASS |
