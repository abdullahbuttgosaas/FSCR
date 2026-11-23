---
skill_id: "gosaas.gap-fills.common-features.manage-attachment-categories"
name: "Manage Applications Core Attachment Categories (GoSaaS gap fill, short card)"
description: "Short card over FSCR's attachments skill: create a new Applications Core attachment category through the setup-task CSV export and FSM CSV import (FND_APP_ATTACHMENT_CATEGORY package), then read it back with a second export (there is no REST resource). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 3, 2026-11-20. Written and tested live on one test environment. NOT official FSCR."
tested_by_fresh_chat: "See gap_index.csv (fresh_claude_pass) and CHANGELOG.md"
layer: "pillar"
pillar: "Common"
offering: "Common Features"
task_code: "FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES"
task_name: "Manage Applications Core Attachment Categories"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.fusion-api.apps-common.attachments (FSCR; references/attachment-categories.md)"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import process that creates a new attachment category. It may not be deletable; plan as if it stays."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES"
---

# Manage Applications Core Attachment Categories (GoSaaS gap fill, short card)

> **Added by GoSaaS, not part of official FSCR.** FSCR's attachments skill (`core/fusion-api/apps-common/attachments`, file `references/attachment-categories.md`) lists this task code and names the route: task-level CSV export, then **FSM CSV import**. It has no step-by-step recipe and no read-back. This card adds those. It does not edit any FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-20) · **FROM FSCR** = FSCR file · **GUESS** = judgment, not tested.

## What this setup is
An attachment category (for example "Miscellaneous") classifies files attached to records. A category becomes usable on a screen only when it is linked to an attachment entity (the second file of the package). This card creates the **category only**, without entity links (VERIFIED); linking is described as GUESS.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          (FSCR itself contains a folder named "project"; that is fine. The rule below is about RUN.)
GAPS    = the gaps-filled folder (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers; this card needs that folder in place)
RUN     = a NEW empty work folder OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix (GAPFILL_ in our tests)
NAME    = new CategoryName, e.g. GAPFILL_ATC_<something>: upper case, digits, _ ; max 30 characters (GUESS)
UNAME   = display name (UserName column). The helper's prefix check applies to it too, so we used UNAME = NAME.
```

## Step 0. Safe running
FSCR scripts with full path and `python -B`; always `--output-dir` under `RUN`. Git Bash: paths as `E:/...`, and `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.

## Step 1. Export first (also the sign-in check)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file FND_APP_ATTACHMENT_CATEGORY.csv --cols CategoryName,UserName,ApplicationId,ModuleId
```
- If it fails with HTTP 401/403 or an expired token, sign in (FSCR `core/auth/fusion-oauth-authentication`: `python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`, in the background; a person completes the browser page; never type credentials), then run the export again. Sign-in is waiting time.
- Expect 3 files (VERIFIED, about 40 s): `ASM_SETUP_CSV_METADATA.xml`; `FND_APP_ATTACHMENT_CATEGORY.csv` (10 columns: `CategoryName, ApplicationId, CreatedBy, CreationDate, Description, LastUpdateDate, LastUpdateLogin, LastUpdatedBy, ModuleId, UserName`); `ORA_FND_APP_ATTACHMENT_CATEGORY.csv` (8 columns: `CategoryName, EntityName, CreatedBy, CreationDate, LastUpdateDate, LastUpdateLogin, LastUpdatedBy, ModuleId`).
- The export is **scoped** to the Applications Core module (metadata scope `moduleType=APPLICATION`, `moduleKey=FND`). VERIFIED: it held one seeded category before our test. Every row shares one `ApplicationId` and `ModuleId`: copy them from the inspect output. If the export has **no** category row, stop and ask (you would have no ModuleId).
- If the export fails or lacks these files: **stop**, note it, do not import.
- **Before-check:** there is no REST resource for attachment categories (VERIFIED: five likely names all gave HTTP 404), so the only "is the name free" check is that NAME is not in this export. Categories of other modules are not in it; a `GAPFILL_` name makes a clash very unlikely (GUESS).

## Step 2. Build a package with only the new category
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name attach_cat_new.zip --prefix <PREFIX> \
  --key "FND_APP_ATTACHMENT_CATEGORY.csv=CategoryName" --key "ORA_FND_APP_ATTACHMENT_CATEGORY.csv=CategoryName,EntityName" \
  --prefix-col "FND_APP_ATTACHMENT_CATEGORY.csv=CategoryName,UserName" --max-len "CategoryName=30" --max-len "UserName=80" \
  --row "FND_APP_ATTACHMENT_CATEGORY.csv|CategoryName=<NAME>|UserName=<UNAME>|Description=<text>|ApplicationId=<from export>|ModuleId=<from export>"
```
- Fill only those 5 columns; audit columns empty; the entity-link file keeps only its header. VERIFIED (imported cleanly).
- **Entity link (GUESS, not tested):** add `--row "ORA_FND_APP_ATTACHMENT_CATEGORY.csv|CategoryName=<NAME>|EntityName=<an existing entity name>|ModuleId=<same>"`. Entity names come from the attachment entities task export (FSCR `references/attachment-entities.md`). A link makes the category show on that entity's screens for every user.

## Step 3. Import
**Approval:** the person must approve the environment, the task and the exact name; a brief that names all three and says proceed is the approval (note it in your work folder).
FSCR's attachments reference routes the import through `core.data-loader` (FSM CSV Import). We used FSCR's task-level import script, which submits the same FSM CSV import (`setupTaskCSVImports`) for one task. VERIFIED.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES --task-name "Manage Applications Core Attachment Categories" \
  --zip-file "<RUN>/payload/attach_cat_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 50 s. The real result is only in `<RUN>/import_result/*_process_log.txt`; read it with
  `python -I -c "import sys; print(open(sys.argv[1],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<log file>"`
- Success (VERIFIED): `Business object: Application Attachment Category. Status: Completed successfully.`, detail `FndDocumentCategoriesVLSD.xml ... A total of 1 rows were processed. 0 rows of them failed`, `FndDocCategoriesToEntitiesVLSD.xml ... 0 rows`, `Total Objects Failed: 0`. An earlier line may say `Status: In progress` for the same object; the later line is the final one.
- Not complete yet: keep the ProcessId, use FSCR's `get_setup_task_csv_import_result.py`; never import twice. Failed rows: copy the error, change one thing, retry at most 3 times.

## Step 4. Read back (second export, then compare)
Repeat Step 1 with `--output-dir "<RUN>/export_after"` and unzip, then:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_ATTACHMENT_CATEGORY.csv=CategoryName" --key "ORA_FND_APP_ATTACHMENT_CATEGORY.csv=CategoryName,EntityName" \
  --expect "FND_APP_ATTACHMENT_CATEGORY.csv=<NAME>" --rows-out "<RUN>/added_rows.csv"
python -I "<H>/inspect_export.py" "<RUN>/export_after/unz" --file FND_APP_ATTACHMENT_CATEGORY.csv \
  --cols CategoryName,UserName,ApplicationId,Description --where "CategoryName=<NAME>" --json-out "<RUN>/readback_after.json"
```
`RESULT: PASS` = only your category added, nothing removed, no existing row changed; the inspect line shows the stored name, display name and description (1 row). VERIFIED. Evidence (optional): `python -B "<H>/render_readback.py" --json "<RUN>/readback_after.json" --title "..." --png <file.png>`.

## Rules and limits
1. New records only; never import a full export (a matching `CategoryName` would update it).
2. Keep all 3 files, metadata XML unchanged.
3. Test records may stay for good; this card never deletes. Record every category you create.
4. Tested on one environment (release 11.13.26.10.0), category only, no entity link.
5. Python flags: `-B` without `-I` for FSCR scripts and `render_readback.py`; `-I` for the helpers that read files only.

## Worked example (VERIFIED, 2026-11-20). Do not reuse this name.
| Step | Result |
|---|---|
| Export before | 1 category, 0 entity links |
| New record | `GAPFILL_ATC_T1` (display name the same), ApplicationId and ModuleId copied from the seeded row |
| Import | 1 attempt (after the helper refused a display name without the prefix), about 50 s: 1 row, 0 failed |
| Export after + compare | 2 categories, 0 links; added 1, removed 0, changed 0: PASS |
