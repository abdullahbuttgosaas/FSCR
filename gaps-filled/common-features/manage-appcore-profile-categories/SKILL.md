---
skill_id: "gosaas.gap-fills.common-features.manage-appcore-profile-categories"
name: "Manage Applications Core Profile Categories (GoSaaS gap fill)"
description: "Create a new profile category and link profile options to it through FSCR's setup-task CSV export and import (FND_APP_PROFILE_CATEGORY package), then read it back with a second export and compare (no REST resource found). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 1, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES"
task_name: "Manage Applications Core Profile Categories"
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
  - "a profile option to link (for a test: your own option made with gosaas common-features/manage-profile-options)"
reused_by:
  - "common-features/manage-profile-categories (FND_MANAGE_PROFILE_CATEGORIES)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new profile category and its option links. It may not be deletable; plan as if it stays."
---

# Manage Applications Core Profile Categories (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a manual card only for profile categories (no skill for this task code). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A profile category groups profile options (for example "options that all signed-in users may read through REST"). A category has a name, a display name and a list of options with a display order. Seeded categories control real behaviour, so tests use a **new** category that links only **your own test option**.

## When to use
- Someone asks to create a **new** profile category (with option links) for task `FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES`.
- Do **not** use it to add options to seeded categories or to change existing categories. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties
          (in a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main). Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment
          share the saved sign-in (VERIFIED: two different copies both worked with one sign-in).
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
CAT     = new category Name, upper case letters, digits and _, starting with PREFIX
DISPLAY = category DisplayName
OPTION  = profile option to link (in a test: an option starting with PREFIX), and its ApplicationId (OPTAPP)
```
Pick a CAT that does not exist yet. Do not reuse the worked-example names at the end.

## Step 0 and Step 1 (safe run, sign-in)
Exactly as in `../manage-profile-options/SKILL.md` Steps 0 and 1 (FSCR in place, `python -B`, `--output-dir` under RUN, Git Bash `E:/...` paths and `MSYS_NO_PATHCONV=1`, `timeout 120` before REST reads, background sign-in on the redirect port only if the export reports an expired token).

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED, about 40 seconds; counts grow with every earlier test):
- `FND_APP_PROFILE_CATEGORY.csv` (11 columns): `Name, ApplicationId, ModuleId, Enabled, Description, DisplayName` + 5 audit columns
- `ORA_FND_APP_PROFILE_CATEGORY_OPTION.csv` (9): `FND_APP_PROFILE_CATEGORY.Name, ProfileOptionName, ProfileOptionApplicationId, DisplaySequence` + audit
- `ASM_SETUP_CSV_METADATA.xml`: scope `moduleType=APPLICATION`, `moduleKey=FND`, `mode=search`
- Seeded categories are in it (the option file has well over 1,000 rows). If it fails or lacks these files: **stop**.

## Step 3. Module id and checks
1. **ModuleId** of the new category: read the Applications Core ModuleId from the seeded `YES_NO` lookup, exactly as in `../manage-profile-options/SKILL.md` Step 3 (two commands). Keep it as MODULE; never leave it empty. Do **not** copy it from the export: the seeded categories carry a different module id than the one `YES_NO` gives, and only the `YES_NO` one was tested (VERIFIED: every test category made with it shows in this task's export).
2. **CAT is free:** it must not be in `FND_APP_PROFILE_CATEGORY.csv` (the builder also checks). No REST resource was found for categories (`profileCategories`, `profileOptionCategories`, `applicationProfileCategories` all gave HTTP 404, VERIFIED), so the export is the proof here.
3. **OPTION exists:** read it by REST and note its ApplicationId as OPTAPP:
   ```bash
   timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions --q "ProfileOptionName='<OPTION>'"      --fields ProfileOptionName,ApplicationId --out "<RUN>/option.json" --expect-count 1
   ```

## Step 4. Build a package with only the new rows
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name profile_category_new.zip --prefix <PREFIX> \
  --key "FND_APP_PROFILE_CATEGORY.csv=Name,ApplicationId" \
  --key "ORA_FND_APP_PROFILE_CATEGORY_OPTION.csv=FND_APP_PROFILE_CATEGORY.Name,ProfileOptionName,ProfileOptionApplicationId" \
  --prefix-col "FND_APP_PROFILE_CATEGORY.csv=Name" --prefix-col "ORA_FND_APP_PROFILE_CATEGORY_OPTION.csv=ProfileOptionName" \
  --row "FND_APP_PROFILE_CATEGORY.csv|Name=<CAT>|ApplicationId=0|ModuleId=<MODULE>|Enabled=Y|Description=<text>|DisplayName=<DISPLAY>" \
  --row "ORA_FND_APP_PROFILE_CATEGORY_OPTION.csv|FND_APP_PROFILE_CATEGORY.Name=<CAT>|ProfileOptionName=<OPTION>|ProfileOptionApplicationId=<OPTAPP>|DisplaySequence=1"
```
- One `--row` per linked option (DisplaySequence 1, 2, ...). The second `--prefix-col` makes the builder refuse any option that is not yours; drop it only with the person's approval to link real options (not tested).
- The new category row and its option rows go in the **same** ZIP (the option rows are children of the category). VERIFIED

## Step 5. Import
**Approval.** The person must approve the environment, the task, CAT and the linked options before the import. If their brief already names all of this and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES --task-name "Manage Applications Core Profile Categories" \
  --zip-file "<RUN>/payload/profile_category_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
Read `<RUN>/import_result/*_process_log.txt` with the one-liner in the profile options skill (Step 5). Success: `Detail Object: ProfileCategorySD.xml ... A total of 2 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0` (1 category + 1 link). VERIFIED, 22 to 40 s. `0 rows were processed` = nothing was created. Not complete yet: keep the ProcessId and use FSCR's `get_setup_task_csv_import_result.py`; never import twice. Rows failed: copy the error, change one thing, retry at most 3 times.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_PROFILE_CATEGORY.csv=Name,ApplicationId" \
  --key "ORA_FND_APP_PROFILE_CATEGORY_OPTION.csv=FND_APP_PROFILE_CATEGORY.Name,ProfileOptionName,ProfileOptionApplicationId" \
  --expect "FND_APP_PROFILE_CATEGORY.csv=<CAT>,0" \
  --expect "ORA_FND_APP_PROFILE_CATEGORY_OPTION.csv=<CAT>,<OPTION>,<OPTAPP>" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = exactly your category and its links were added, nothing removed or changed. Give one `--expect` per added row. VERIFIED.
**Someone else imported at the same time?** If the compare says FAIL only because of extra added rows that are not yours (another tester's category, made between your two exports), and it shows `removed 0` and `changed 0`, judge your own rows: each of your `--expect` rows must be in the added list. Write the extra rows in your report. VERIFIED (two testers ran at once in our fresh tests). Avoid it by not running two imports of this package at the same time. `added_rows.csv` shows what Oracle stored (Enabled, DisplayName). For evidence, `inspect_export.py ... --where Name=<CAT> --json-out <file>` then `render_readback.py --json <file>`.

## Rules and limits
1. New records only; never import a full export (a matching Name would update that category).
2. Keep all 3 files, metadata XML unchanged.
3. Test records may stay for good. This skill never deletes. Record them in your change log.
4. Not tested: linking seeded options, categories of applications other than 0, translations.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags as in the profile options skill (Rule 6).

## Worked example (VERIFIED, 2026-11-23). Do not reuse these names; they now exist.
| Step | Result |
|---|---|
| Export before | 2 categories, 1,574 option links; 40 s |
| New records | category `GAPFILL_AB_PC1` (application 0, enabled) + link to option `GAPFILL_AB_PO1`, sequence 1 |
| Import | 1 attempt, 22 s: 2 rows processed, 0 failed |
| Export after + compare | 3 categories, 1,575 links; added 1 + 1, removed 0, changed 0: PASS |
