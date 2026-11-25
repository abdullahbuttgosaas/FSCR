---
skill_id: "gosaas.gap-fills.common-features.manage-help-content"
name: "Manage Help Content: read custom help topics by setup-task CSV; new topics are refused (GoSaaS gap fill, SCREEN-ONLY for create)"
description: "Reads the custom help topics, titles and graphics through FSCR's setup-task CSV export of ORA_ATK_MANAGE_HELP_CONTENT. Creating a new custom topic through the CSV import FAILED in 10 tries (Oracle: 'The value of the attribute PrimaryHierarchyIds isn't valid', even with the hierarchy values of an existing topic). Use the Manage Help Content page for new topics. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 13, 2026-11-25. Export VERIFIED; import FAILED on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ATK_MANAGE_HELP_CONTENT"
task_name: "Manage Help Content"
dataloader_import_mode: "FSM"
type: "export"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
status: "screen-only for create (batch 13: a new topic refused in 10 tries; round trip of an existing topic passes)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Step 2 is read only."
---

# Manage Help Content (GoSaaS gap fill, SCREEN-ONLY for create)

> **Added by GoSaaS, not part of official FSCR.** FSCR has only a manual card for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.
> **Status: screen-only for create.** CSV exists but cannot create a new topic: `PrimaryHierarchyIds` is rejected on insert; the Manage Help Content page creates the hierarchy ID. The read (Step 2) works. Creating a new topic by CSV import was refused every time (Step 3 records what was tried). Create topics on the Manage Help Content page.

## What it is
Custom help: topics (`ATK_KR_TOPIC.csv`, 45 columns: `TopicId`, `OrigTitle`, `Title`, `FileType` `TEXT` or `URL`, `Document` (hex HTML), `Url`, `Source` `CUSTOM_TOPIC`, `Hidden`, hierarchy columns `PrimaryHierarchyType`, `PrimaryLevel1Id`..`PrimaryLevel6Id`, `SearchIds`, `SearchHelpkeys` (the page help keys the topic is attached to), release and audit columns), titles (`ORA_ATK_KR_TITLE.csv`: `OrigTitle`, `DocIdent` `HC`, `SeenMark`, `InfoType`), and graphics (`ORA_ATK_KR_GRAPHICS.csv`: `Filename`, `MimeType`, `Content` hex). Only custom topics are exported, not Oracle's (VERIFIED).

## Placeholders
```text
FSCR = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H    = <GAPS>/common-features/manage-docseq-categories/scripts
RUN  = a NEW empty work folder, OUTSIDE FSCR and outside any git repo
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...`, `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. On HTTP 401/403 sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page; never type credentials). The export's `CreatedBy`/`LastUpdatedBy` columns and file names hold user and environment names: never copy them into a report.

## Step 2. Read-only export (VERIFIED)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_ATK_MANAGE_HELP_CONTENT --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export" > "<RUN>/export.log" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export"
python -I "<H>/inspect_export.py" "<RUN>/export/unz"
```
VERIFIED (about 60 s): 4 files (topics, titles, graphics, metadata). Our environment: 5 custom topics, 10 titles, 0 graphics. The `Document` column can be long: before `csv` reads it, call `csv.field_size_limit(10**9)`.

## Step 3. Create a topic by CSV: FAILED (what was tried)
Packages built with `<H>/build_fsm_package.py` (new rows only), imported with FSCR's `import_setup_task_csv.py --task-code ORA_ATK_MANAGE_HELP_CONTENT --task-name "Manage Help Content"`. A hidden `URL` topic with a prefix title:

| Try | Change from the try before | Oracle's answer |
|---|---|---|
| 1 | topic row only, `TopicId` blank | `JBO-27014: Attribute TopicId in TopicEO is required` |
| 2 | new unused `TopicId` | `Attribute Changed in TopicEO is required` |
| 3 | `Changed` date + `Release`, `SearchReleases` | `The value of the attribute OrigTitle isn't valid` |
| 4 | a title row in `ORA_ATK_KR_TITLE.csv` (`OrigTitle`, `DocIdent=HC`, `SeenMark=0`, `InfoType=meaning`) | title row processed, topic: `The value of the attribute PrimaryHierarchyIds isn't valid` |
| 5 | hierarchy columns blank | `Attribute PrimaryHierarchyType in TopicEO is required` |
| 6 | hierarchy back + `SearchHelpkeys` of an existing topic | `PrimaryHierarchyIds isn't valid` |
| 7 | every column as on an existing `URL` topic (`Hidden=0`, its release) | `PrimaryHierarchyIds isn't valid` |

Retry (2026-11-26, 3 more tries, each after a written diagnosis):

| Step | Diagnosis before it | What was sent | Oracle's answer |
|---|---|---|---|
| research | Oracle docs: help hierarchies have types and nodes (tables `ATK_KRH_HIERARCHY_TYPES`, type of at most 4 characters; `ATK_KRH_HIERARCHY_ITEMS`; `ATK_KRH_HIERARCHY_INTERSECTION`). Cloud docs only describe help windows and moving all added help with a configuration package. No public note names `PrimaryHierarchyIds` | - | - |
| REST probe | is there a resource to read the nodes? | `helpTopics`, `helpHierarchies`, `helpHierarchyItems`, `customHelpTopics`, `helpContents`, `helpKeys` | all HTTP 404: the nodes cannot be read |
| round trip | does Oracle accept the page's own values at all? | the existing `URL` topic and its title row, exactly as exported (ProcessId 100004744404970) | `Completed successfully`; the after-export is identical (no change found, so the insert check did not run) |
| compare | my try-7 row vs that row, column by column | - | only `TopicId`, the 3 title columns, `Changed` and the blank who-columns differ |
| try 8 | `OM_HC` under `OM_HC` may be an invalid path for a new row | type `OM_HC`, all levels blank (100004744404985) | `Attribute PrimaryLevel1Id in TopicEO is required` |
| try 9 | maybe the type must be a real type code (help settings name `OP`; `OM_HC` has 5 characters) | type `OP`, level 1 `OP` (100004743427714) | `PrimaryHierarchyIds isn't valid` |
| try 10 | `PrimaryHierarchyIds` is not a package column, so it is empty on insert | an extra column `PrimaryHierarchyIds=OM_HC`, declared in the metadata attribute list (100004743429241) | `PrimaryHierarchyIds isn't valid` |

After the retry the export still shows 5 topics and 10 titles: nothing was left behind.

**Conclusion:** the error does not depend on the hierarchy values sent (`OM_HC` and `OP` fail the same way, and an extra column is ignored). The insert needs a hierarchy id that only the Manage Help Content page creates (GUESS: from the hierarchy node tables, which no REST resource or CSV file exposes). Creating a custom help topic by setup-task CSV is not possible on this release: create it on the page, or move help between environments with a whole configuration package (Oracle's documented way). Changing an existing topic by CSV was not tested beyond the unchanged round trip.

Lessons (VERIFIED): `TopicId` and `Changed` are required; the title must exist in the title file of the same package; the hierarchy value `OM_HC` that the existing topics show is refused for a new topic. The after-export showed no new title or topic (titles 10, topics 5): the title rows did not stay. GUESS: the importer checks the hierarchy against a list the export does not hold (`PrimaryHierarchyIds` is not a CSV column).

## Rules and limits
1. Use Step 2 to read. Do not retry the CSV create: 10 tries and a round trip show the hierarchy id cannot be sent by CSV.
2. Never change or re-import an existing topic (that would change help other users see).
3. Seen on one environment (release 11.13.26.10.0).
