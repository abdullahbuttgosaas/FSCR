---
skill_id: "gosaas.gap-fills.common-features.manage-search-profile-options"
name: "Manage Search Profile Options (GoSaaS gap fill, written, not load-tested)"
description: "Read, and when a person approves it, change the SITE value of the seeded search profile options (Search Method Default and the hide-sensitive-attributes option) through FSCR's setup-task CSV export/import of ZCA_MANAGE_SEARCH_PROFILE_OPTIONS, with the current value read by REST. WRITTEN ONLY: the import step was not run on the shared test environment because it changes search for every user. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 06, 2026-11-25. Export and REST reads seen live on one test environment; the import was NOT run (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZCA_MANAGE_SEARCH_PROFILE_OPTIONS"
task_name: "Manage Search Profile Options"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-profile-options (full profile recipe) and manage-admin-profile-values (SITE values)"
  - "gosaas common-features/manage-profile-options/scripts/copy_parent_rows.py"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Steps 2 and 3 are read only."
  - "Step 5 (import) changes a seeded SITE value: it takes effect at once for every user of the environment. Run it only on an environment you own, with written approval."
---

# Manage Search Profile Options (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> **Status: written, not load-tested.** The export and the REST reads were run live (VERIFIED). The import was **not** run on our shared test environment: the task only edits seeded options whose SITE value every user gets. Steps 4 to 6 are therefore **GUESS**, built from the tested profile-value recipe (`manage-admin-profile-values`, batch 2) and this task's export.

## What it is and when to use
The task holds the profile options that control the global search in Fusion (application `ZCA`). Its export scope is two named, **seeded** options in `edit` mode (VERIFIED, from the export's `ASM_SETUP_CSV_METADATA.xml`):
| Option | User name | Values |
|---|---|---|
| `ZCA_SEARCH_DEFAULT_OPTION` | Search Method Default | e.g. `KEYWORD_SEARCH` (the SITE value we read, VERIFIED) |
| `ZCA_SEARCH_HIDE_SENSITIVE_ATTR` | hide sensitive attributes in search (GUESS from the code) | not found by REST in our release (VERIFIED: `profileOptions` 0 rows), so it may not exist in every release |

Use the skill when someone asks what these options are set to (Steps 2 and 3, safe) or asks to change them on an environment they own (Steps 4 to 6, with approval). Do **not** create new options here (use `manage-profile-options`).

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
OPTION  = ZCA_SEARCH_DEFAULT_OPTION (or the other option of the scope)
NEWVAL  = the new SITE value the person approved
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; `timeout 120` before REST reads. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens, headers, the server address or user names; FSCR's output file names hold the environment name, never copy them into a report.

## Prerequisites
1. Read access to `profileOptions` and the export privilege for this task.
2. For Step 5 only: written approval from whoever owns the environment, naming OPTION, the level (SITE) and NEWVAL, because every user is affected.

## Step 2. Read the options and their current value by REST (read only)
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions --q "ProfileOptionName='<OPTION>'" \
  --fields ProfileOptionName,ApplicationShortName,UserProfileOptionName --out "<RUN>/option.json" --expect-count 1
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions/<OPTION>/child/siteProfileOptionValues \
  --fields LevelValue,ProfileOptionValue --out "<RUN>/site_before.json"
```
VERIFIED: `ZCA_SEARCH_DEFAULT_OPTION` (application ZCA) has SITE value `KEYWORD_SEARCH`. Always pass `--fields`: without it the read also prints `CreatedBy` / `LastUpdatedBy` (user names). An unknown field in `--fields` gives HTTP 400 (VERIFIED: `SQLValidation`).

## Step 3. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZCA_MANAGE_SEARCH_PROFILE_OPTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 40 s): 4 files, `FND_APP_PROFILE_OPTION.csv` (13 columns), `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv` (10), `FND_APP_PROFILE_VALUE.csv` (10: `FND_APP_PROFILE_OPTION.ProfileOptionName`, `FND_APP_PROFILE_OPTION.ApplicationId`, `LevelName`, `LevelValue`, `ProfileOptionValue` + audit), all with **0 rows**, and the metadata. The export leaves seeded options out (as batch 4 saw for ZX options), so the export cannot be the read-back here: use REST (Step 2).

## Step 4. Build the value row (GUESS: not run)
A value is a child row of its option (hierarchical package): the parent option row must be in the same ZIP, unchanged (lesson from `manage-admin-profile-values`, VERIFIED there for own options). Here the parent is seeded and the export has no row for it, so the parent row must be written from REST, with exactly the seeded values (`ProfileOptionName`, `ApplicationId`, `ModuleId`, `UserProfileOptionName`, `Description`, `SqlValidation`, dates). GUESS: if any parent value differs, the import updates the seeded option; a round trip (rule from batch 4) on an environment you own should be done first.
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name search_value.zip \
  --prefix ZCA_ --key "FND_APP_PROFILE_OPTION.csv=ProfileOptionName" \
  --row "FND_APP_PROFILE_OPTION.csv|ProfileOptionName=<OPTION>|ApplicationId=<from REST>|ModuleId=<from REST>|UserProfileOptionName=<from REST>|...all other columns exactly as REST shows them" \
  --row "FND_APP_PROFILE_VALUE.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<OPTION>|FND_APP_PROFILE_OPTION.ApplicationId=<from REST>|LevelName=SITE|LevelValue=SITE|ProfileOptionValue=<NEWVAL>"
```
NEWVAL must be one of the option's allowed values (read the option's `SQLValidation` through REST field names your release accepts, or the option's lookup) (GUESS).

## Step 5. Import (GUESS: not run; only with the approval of Prerequisite 2)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZCA_MANAGE_SEARCH_PROFILE_OPTIONS --task-name "Manage Search Profile Options" \
  --zip-file "<RUN>/payload/search_value.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
Write down the `ProcessId`. If the connection drops after the process started, do not import again: wait 2 minutes and read back (Step 6). A generic database error at the insert (`JBO-26041`): fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it).

## Step 6. Read back (REST)
Repeat the second call of Step 2 into `site_after.json`; the SITE `ProfileOptionValue` must be NEWVAL, and `profileOptions` must show the option unchanged.

## Rules and limits
1. Steps 2 and 3 are safe anywhere. Steps 4 to 6 change a setting for every user: only on an environment you own, with written approval; note the old value (Step 2) so it can be set back.
2. Never change these options on a shared test environment for a test (that is why this skill was not load-tested).
3. Not tested: the import, the parent row written from REST, USER-level values (GUESS: the task's levels are in `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv`).
4. Export and REST seen on one environment (release 11.13.26.10.0).

## Worked example (read part only, VERIFIED 2026-11-25)
| Step | Result |
|---|---|
| REST `profileOptions` | `ZCA_SEARCH_DEFAULT_OPTION`, application ZCA, "Search Method Default"; `ZCA_SEARCH_HIDE_SENSITIVE_ATTR`: 0 rows |
| REST site value | `KEYWORD_SEARCH` |
| Export | 4 files, 0 rows (scope: the 2 named options, mode `edit`), about 40 s |
| Import | not run (unsafe: changes search for every user) |
