---
skill_id: "gosaas.gap-fills.common-features.manage-account-hierarchies"
name: "Manage Account Hierarchies: new account hierarchy (tree, DRAFT version, parent and child nodes) (GoSaaS gap fill)"
description: "Create one new account hierarchy on the accounting flexfield structure GL_ACCT_FLEX: a tree, its data source parameters, one DRAFT version and nodes (a parent value with child values) of a test value set, through FSCR's setup-task CSV export and FSM CSV import. All ids are read live by REST from a template tree (helper tree_rows.py). Read back by REST (fndTreeNodes) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 07, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_ACCOUNT_HIERARCHIES"
task_name: "Manage Account Hierarchies"
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
  - "gosaas common-features/manage-value-sets (FND_MANAGE_APPLCORE_VALUE_SETS: the test value set with a parent value)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one account hierarchy tree with a DRAFT version and nodes. A draft hierarchy is not used by reporting, allocations or cross-validation until it is audited, made active and published (screen or other tasks, not covered). It may not be deletable; plan as if it stays."
---

# Manage Account Hierarchies (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag). FSCR's `core/fusion-api/apps-common/trees` skill covers trees and nodes by REST; this skill is the tested **CSV route** for account hierarchies. It runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
An account hierarchy is a tree on the accounting flexfield structure `GL_ACCT_FLEX` that rolls segment values up to **parent values** (values with `SummaryFlag=Y`). Its task package is the tree package limited to `GL_ACCT_FLEX` (VERIFIED: every row of the export is on that structure). A hierarchy has versions; nodes live in a version: a **root** node is a parent value (the structure's "parent values" data source), a **child** node is a detail value ("detail values" data source).
Use this skill to create a **new** hierarchy with one DRAFT version and a small set of nodes on a **test** value set. Do not use it to change an existing hierarchy or to put test values into a real chart of accounts.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-trees-and-tree-versions/scripts   (tree_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
TEMPLATE= TreeCode of an existing GL_ACCT_FLEX tree that has nodes (only read)
TREE    = new TreeCode (also TreeName), starting with PREFIX, upper case, letters, digits and _ (VERIFIED with 17 characters)
VS      = a TEST value set (independent, character) holding PARENT (SummaryFlag=Y) and CHILD (SummaryFlag=N)
PARENT  = a parent value of VS; CHILD = a detail value of VS
START   = version start date, YYYY/MM/DD
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
1. **Test value set VS with a parent and a child value.** Check first: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource valueSets --q "ValueSetCode='<VS>'" --fields ValueSetCode,ValidationType --out "<RUN>/vs.json"`.
   If it does not exist, create it once with the gap skill `<GAPS>/common-features/manage-value-sets/SKILL.md` (task FND_MANAGE_APPLCORE_VALUE_SETS), with these value rows (VERIFIED in our test):
   `--row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=<PARENT>|Description=<text>|EnabledFlag=Y|SummaryFlag=Y|SortOrder=1"` and the same with `Value=<CHILD>|SummaryFlag=N|SortOrder=2`. Follow that skill's own steps (export, build, import, read back). Never create it twice.
2. **Template tree TEMPLATE**: any existing `GL_ACCT_FLEX` tree with nodes (it is only read). List them: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource fndTrees --q "TreeStructureCode='GL_ACCT_FLEX'" --fields TreeCode --out "<RUN>/trees.json"`.

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code GL_MANAGE_ACCOUNT_HIERARCHIES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 6 files (VERIFIED, about 1 minute): `FND_APP_TREE.csv`, `ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv`, `ORA_FND_APP_TREE_VERSION.csv`, `ORA_FND_APP_TREE_VERSION_NODE.csv`, `ORA_FND_APP_TREE_DATA_SOURCE_LABEL.csv`, `ASM_SETUP_CSV_METADATA.xml`, all rows on `GL_ACCT_FLEX`. TREE must not be in `FND_APP_TREE.csv`.
- If the export stops with no ZIP (for example `The read operation timed out`), run it again into a new folder; it is read-only. Up to 3 tries (VERIFIED: a second try worked).
- Pick TEMPLATE here: trees with their node counts:
  `python -I -c "import csv,sys,collections; c=collections.Counter(r['ORA_FND_APP_TREE_VERSION.TreeCode'] for r in csv.DictReader(open(sys.argv[1]+'/ORA_FND_APP_TREE_VERSION_NODE.csv',encoding='utf-8-sig'))); [print(n,t) for t,n in c.most_common(10)]" "<RUN>/export_before/unz"`
  Any tree in that list has nodes. START: use the first day of the current year if the brief gives no date (any date works for a draft version: GUESS).

## Step 3. Build the package (helper reads every id live)
```bash
python -B "<T>/tree_rows.py" --fscr "<FSCR>" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name hierarchy_new.zip --prefix <PREFIX> --structure GL_ACCT_FLEX --template-tree "<TEMPLATE>" \
  --tree <TREE> --value-set <VS> --start-date <START> --root <PARENT> --child <CHILD>:<PARENT>
```
Want: `FND_APP_TREE.csv: 1 new rows`, `ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv: 6 new rows`, `ORA_FND_APP_TREE_VERSION.csv: 1 new rows`, `ORA_FND_APP_TREE_VERSION_NODE.csv: 2 new rows`, and a `TREE_VERSION_ID=` line. A `STOP:` line means nothing was written.
The helper first prints `template value set: <code>`: the value set of TEMPLATE's nodes. On account hierarchies it is often named like the tree itself (VERIFIED: two different trees showed a value set with the tree's own name); that is not an error. Every parameter value equal to it becomes VS.
The node rows (VERIFIED shape, the same as existing account hierarchy nodes):
- root: new GUID `TreeNodeId`, empty `ParentTreeNodeId`, `DataSourceId` = the template's depth-0 (parent values) data source, `Pk1StartValue=PARENT`, `Pk2StartValue=VS`, `Depth=0`, `ChildCount`=number of children;
- child: new GUID `TreeNodeId`, `ParentTreeNodeId` = the root's id, `DataSourceId` = the template's leaf (detail values) data source, `Pk1StartValue=CHILD`, `Pk2StartValue=VS`, `Depth=1`, `ChildCount=0`, `ParentDataSourceId`/`ParentPk1Value`/`ParentPk2Value` = the root's data source, PARENT and VS.
- No label on the nodes: `GL_ACCT_FLEX` has optional label enforcement (`OptionalLabelEnforcement=Y` in the structures export). VERIFIED accepted without labels.
- More values: repeat `--root` and `--child VALUE:PARENT` (only one level below a root is supported by the helper).

## Step 4. Import
**Approval.** The person must approve the environment, the task, TREE, VS and the values before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code GL_MANAGE_ACCOUNT_HIERARCHIES --task-name "Manage Account Hierarchies" \
  --zip-file "<RUN>/payload/hierarchy_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`).
- Short summary of the log (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED, about 30 s): `Application Tree ... Completed successfully`, `Total Objects Failed: 0` (plus an `In progress` line and per-file row counts: normal). Step 5 is the proof.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 5.
- Rows failed: copy the message, change one thing, retry at most 3 times with a new TREE. `JBO-26041` at the insert: fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it). GUESS

## Step 5. Read back (the proof)
1. REST nodes:
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource fndTreeNodes \
  --finder "TSCodeAndTCodeRowFinder;TreeCode=<TREE>,TreeStructureCode=GL_ACCT_FLEX" \
  --fields TreeCode,Pk1StartValue,Pk2StartValue,Depth --out "<RUN>/readback.json" \
  --expect "Pk1StartValue=<PARENT>,Depth=0" --expect "Pk1StartValue=<CHILD>,Depth=1"
```
Want 2 rows and `READBACK: PASS` (VERIFIED). The version: `fndTreeVersions` with finder `AllVersionsRowFinder;TreeCode=<TREE>,TreeStructureCode=GL_ACCT_FLEX` shows `Status=DRAFT`.
2. Export again (Step 2 into `<RUN>/export_after`, unzip) and compare (node key = tree, value, value set, version id, because node ids are new GUIDs):
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_TREE.csv=TreeStructureCode,TreeCode" \
  --key "ORA_FND_APP_TREE_VERSION.csv=TreeStructureCode,TreeCode,TreeVersionName" \
  --key "ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv=FND_APP_TREE.TreeStructureCode,FND_APP_TREE.TreeCode,ParameterId" \
  --key "ORA_FND_APP_TREE_DATA_SOURCE_LABEL.csv=FND_APP_TREE.TreeStructureCode,FND_APP_TREE.TreeCode,TreeLabelId" \
  --key "ORA_FND_APP_TREE_VERSION_NODE.csv=ORA_FND_APP_TREE_VERSION.TreeCode,Pk1StartValue,Pk2StartValue,ORA_FND_APP_TREE_VERSION.TreeVersionId" \
  --expect "FND_APP_TREE.csv=GL_ACCT_FLEX,<TREE>" --expect "ORA_FND_APP_TREE_VERSION.csv=GL_ACCT_FLEX,<TREE>,<TREE>_V1" \
  --expect "ORA_FND_APP_TREE_VERSION_NODE.csv=<TREE>,<PARENT>,<VS>,<TREE_VERSION_ID>" \
  --expect "ORA_FND_APP_TREE_VERSION_NODE.csv=<TREE>,<CHILD>,<VS>,<TREE_VERSION_ID>" \
  --expect "ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv=GL_ACCT_FLEX,<TREE>,<ParameterId 1>" ... (one per ParameterId in the payload's parameter file)
```
`TREE_VERSION_ID` is the value the helper printed. List the ParameterIds with `python -I -c "import csv,sys; [print(r['ParameterId']) for r in csv.DictReader(open(sys.argv[1],encoding='utf-8'))]" "<RUN>/payload/ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER.csv"`. `RESULT: PASS` = only your tree, version, 6 parameters and nodes added (VERIFIED).

## Rules and limits
1. New hierarchies only, on a **test** value set. Never re-import or change an existing hierarchy, version or node; never import a full export.
2. The version stays DRAFT: audit, activation, flattening and publishing (task "Publish Account Hierarchies") are not covered and must not be run on a test tree in a shared environment without a decision.
3. Not tested: ranges, referenced trees, labels on nodes, deeper levels, a value set attached to a real chart of accounts.
4. Test records may stay for good. This skill never deletes.
5. Tested on one environment (release 11.13.26.10.0). Python flags: `-B` without `-I` for FSCR scripts, `rest_read.py` and `tree_rows.py`; `-I` for the other helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Prerequisite | value set `GAPFILL_AB_B7_AHVS` with `P100` (SummaryFlag Y) and `D110` (N) by the value set skill (ProcessId 100004742423615), read back by REST |
| Export before | 46 trees, 92 versions, 1916 nodes (all `GL_ACCT_FLEX`) |
| Import | tree `GAPFILL_AB_B7_AH1`, 6 parameters, version `GAPFILL_AB_B7_AH1_V1` DRAFT, root `P100`, child `D110` (ProcessId 100004742421559), about 30 s (rows built by the builder with the same values `tree_rows.py` writes; the helper was dry-run checked against them) |
| Read back | REST fndTreeNodes 2 rows (P100 depth 0, D110 depth 1); export compare: tree 1, version 1, parameters 6, nodes 2 added, nothing else changed: PASS |
