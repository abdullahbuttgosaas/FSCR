---
skill_id: "gosaas.gap-fills.common-features.set-help-options"
name: "Set Help Options: read the help configuration and change one option by setup-task CSV (GoSaaS gap fill)"
description: "Reads the single help configuration row (ATK_KRH_CONFIG: help enabled, announcements, forums, Oracle University and Support links, URLs) through FSCR's setup-task CSV export of ATK_CONFIGURE_HELP_SETTINGS, and changes one option by importing that same row with only one value changed, then reads it back by export compare. Tested on a shared environment as test-and-restore. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 13, 2026-11-25. Tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ATK_CONFIGURE_HELP_SETTINGS"
task_name: "Set Help Options"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "tested (batch 13, test-and-restore)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "set-help-options/scripts/one_value_package.py (GoSaaS, offline)"
  - "gosaas common-features/manage-docseq-categories/scripts (inspect_export.py)"
side_effects:
  - "Step 2 is read only."
  - "Step 4 changes one help option for every user."
  - "Step 6 (test only) sets the old value back."
---

# Set Help Options (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has only a manual card for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
The help options are **one row** (`ConfigId` 1) in `ATK_KRH_CONFIG.csv`. Its option columns (VERIFIED, export): `HelpEnabled`, `AnnouncementEnabled`, `DiscussionForumEnabled`, `CustomerForumEnabled`, `OracleUnivEnabled`, `OracleSupportEnabled`, `IncludeUpk`, `RemoteHelpPortalFlag`, `RemoteUserRatingFlag`, `SecureCustomHelp` (`Y`/`N`), `SitemapHierarchyType`, and text columns `Logo`, `Url`, `DefaultContentLocation`, `PrivacyStmtUrl`, `UpkWebserverAgent`, `UpkAllDemoUrl`, `CompanyName`, `TechLibraryUrl`, `CustomerForumUrl`, `OracleSupportUrl`, `OracleUniversityUrl`. The export also holds the help content files (`ATK_KR_TOPIC`, `ORA_ATK_KR_TITLE`, `ORA_ATK_KR_GRAPHICS`, the same as the task Manage Help Content); the package of this skill sends those files with headers only.

Use it to read the help options, or to change **one** option at a time when the environment owner asks.

## Placeholders
```text
FSCR  = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS  = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
S     = <GAPS>/common-features/set-help-options/scripts
H     = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN   = a NEW empty work folder, OUTSIDE FSCR and outside any git repo
COL   = the option column to change (one of the list above)
OLD   = COL's value in the before-export (Step 2)
NEW   = the new value (Y or N for a flag; not OLD)
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens or the server address; the export's file names and `CreatedBy`/`LastUpdatedBy` columns hold the environment name and user names: never copy them into a report.

## Prerequisites
1. Setup-task export and import rights.
2. For a real change: the environment owner's approval (every user sees the help options). For a **test** on a shared environment: only a flag, as test-and-restore (Steps 2 to 6), done within a few minutes. Never test a text column (a blank in the CSV may not clear a value; GUESS), so a text change cannot be proven restorable.

## Step 2. Read-only export (VERIFIED)
```bash
mkdir -p "<RUN>"; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ATK_CONFIGURE_HELP_SETTINGS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/before" > "<RUN>/before.log" 2>&1
tail -1 "<RUN>/before.log" | grep -q "^Wrote .*zip" && echo EXPORT OK || echo "EXPORT FAILED: stop, re-run into a new folder"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/before"
python -I "<H>/inspect_export.py" "<RUN>/before/unz"
python -I -c "import csv,sys; r=next(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))); print({k:v for k,v in r.items() if v in ('Y','N') or k=='SitemapHierarchyType'})" "<RUN>/before/unz/ATK_KRH_CONFIG.csv"
```
VERIFIED (about 60 s): 5 files: `ATK_KRH_CONFIG.csv` (28 columns, **1 row**), `ATK_KR_TOPIC.csv`, `ORA_ATK_KR_TITLE.csv`, `ORA_ATK_KR_GRAPHICS.csv`, metadata. Go on only after `EXPORT OK`. Write OLD down. If the export fails with any network error (for example `getaddrinfo failed` or `WinError 10060`), run it again into a new folder (for example `before2`) and use that folder instead of `before` in Steps 3, 5 and 6.

## Step 3. Build the package (VERIFIED)
```bash
python -I "<S>/one_value_package.py" "<RUN>/before/unz" "<RUN>/p1" help1.zip <COL> <NEW>
```
Prints `COL: 'OLD' -> 'NEW'` and `wrote ...zip`. The package holds the export's config row with only COL changed and the who-columns blank, the three content files with headers only, and the metadata unchanged. It stops unless the export has exactly 1 config row.

## Step 4. Import (VERIFIED)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ATK_CONFIGURE_HELP_SETTINGS --task-name "Set Help Options" \
  --zip-file "<RUN>/p1/help1.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp1" > "<RUN>/imp1.log" 2>&1
```
Write down the `ProcessId` (`Started setup task CSV import process: N` in `imp1.log`). `imp1.log` may end with `StatusCode: (unknown)` or a `Wrote ...json` line: both are normal. The result is in `<RUN>/imp1/*_process_log.txt` (one long line; VERIFIED, about 40 s): `Help Configuration. Status: Completed successfully`, `A total of 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0` (an earlier `Status: In progress` and a line `Help Topic. Status: Completed successfully` for the empty content files are normal). Read it with `grep -o "Business object: [A-Za-z ]*. Status: [A-Za-z ]*\|A total of [0-9]* rows were processed. [0-9]* rows of them failed\|Total Objects Failed: [0-9]*" "<RUN>"/imp1/*_process_log.txt`. If the connection drops after the process started, **do not import again**: fetch the log with `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ATK_CONFIGURE_HELP_SETTINGS --process-id <N> --output "<RUN>/imp1/log.txt"` and go on with Step 5.

## Step 5. Read back (VERIFIED)
Run Step 2 again (export, check, unzip) with every `before` replaced by `mid`, then compare the config row:
```bash
python -I -c "import csv,sys; a,b=[next(csv.DictReader(open(p+'/ATK_KRH_CONFIG.csv',encoding='utf-8-sig'))) for p in sys.argv[1:3]]; print({k:(a[k],b[k]) for k in a if a[k]!=b[k] and not k.startswith(('Created','Creation','LastUpdate'))})" "<RUN>/before/unz" "<RUN>/mid/unz"
```
PASS = exactly `{'COL': ('OLD', 'NEW')}` (`LastUpdateDate` also changes; it is left out). The content files keep their row counts.

## Step 6. Set it back (test only, VERIFIED)
Step 3 with the mid-export and OLD (`"<RUN>/mid/unz" "<RUN>/p2" help2.zip <COL> <OLD>`), Step 4 with `help2.zip` into `<RUN>/imp2`, Step 2 with every `before` replaced by `after`, Step 5's compare of `before` with `after` → PASS = `{}` (nothing differs).

## Rules and limits
1. One option per import. Never send rows in the topic, title or graphics files from this skill (that is Manage Help Content).
2. Always write OLD down; a test is finished only when Step 6's compare shows `{}`.
3. Seen on one environment (release 11.13.26.10.0).

## Worked example (2026-11-25)
| Step | Record | Result |
|---|---|---|
| before | `OracleUnivEnabled` `N` | 1 config row, 5 topics, 10 titles |
| import 1 (`Y`) | ProcessId 100004743427336 | PASS; compare `{'OracleUnivEnabled': ('N', 'Y')}` |
| import 2 (back to `N`) | ProcessId 100004743428382 | PASS; before vs after `{}`; topics 5, titles 10 |
| fresh test (F) | ProcessIds 100004744404768, 100004743428451 | PASS; compares `{'OracleUnivEnabled': ('N', 'Y')}` then `{}` |
| re-test (R) after wording fix | ProcessIds 100004744404906, 100004743428470 | PASS; same compares |
