---
skill_id: "gosaas.gap-fills.common-features.map-reports-to-work-areas"
name: "Map Reports to Work Areas (GoSaaS gap fill, written, not load-tested)"
description: "Read the report-to-work-area mappings (which BI reports show in the Reports and Analytics panel of a work area), and, when a person approves it, add a mapping through FSCR's setup-task CSV export/import of ATK_DEFINE_REPORT_MAPPING. WRITTEN ONLY: the import was not run, because a mapping shows the report in that work area to every user. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 06, 2026-11-25. Export seen live on one test environment; the import was NOT run (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ATK_DEFINE_REPORT_MAPPING"
task_name: "Map Reports to Work Areas"
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
  - "gosaas common-features/search-legal-entities/scripts/view_record.py (export viewer)"
  - "an existing BI catalog report (its catalog path) and an existing work area"
side_effects:
  - "Steps 2 and 3 are read only."
  - "Step 5 (import, not run here) adds a report link to a work area's Reports and Analytics panel for every user who opens that work area."
---

# Map Reports to Work Areas (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> **Status: written, not load-tested.** The export was run live (VERIFIED). The import was **not** run on our shared test environment: a new mapping shows a report in a work area to every user. Steps 4 to 6 are **GUESS**, built from the export's layout and the tested FSM recipe of earlier gap fills.

## What it is and when to use
Many work areas have a **Reports and Analytics** panel. This task says which BI catalog reports appear in it, per work area. Use the skill to list the current mappings (safe), or, on an environment you own and with approval, to map one more report to a work area.

## Placeholders
```text
FSCR      = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS      = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H         = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
V         = <GAPS>/common-features/search-legal-entities/scripts/view_record.py
RUN       = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
WORKAREA  = the work area's internal node name, as the export shows it (e.g. itemNode_product_management_ideas)
REPORT    = the report's display name, and RPATH its full BI catalog path (e.g. /shared/Custom/<folder>/<report>)
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens, headers, the server address or user names; FSCR's output file names hold the environment name, never copy them into a report.

## Prerequisites
1. The report exists in the BI catalog at RPATH, and the users of the work area may run it (a mapping does not grant access, GUESS).
2. The work area exists (take WORKAREA from Step 2's export, or from a working mapping).
3. For Step 5 only: written approval from whoever owns the environment, naming WORKAREA, REPORT and RPATH.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ATK_DEFINE_REPORT_MAPPING --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 45 s), 3 files:
- `ATK_RPANE_REPORT_MAPPING.csv`: `Pillar`, `ProductShortName`, `WorkareaName`, `UserWorkareaName` + audit (11 rows on 4 work areas in our export, all `ProductShortName=ATK`, `Pillar` empty);
- `ORA_REPORTS_AND_ANALYTICS_MAPPING_REPORT.csv`: `ReportName`, `ReportPath` + audit (13 rows, paths under `/shared/Custom/...`);
- `ASM_SETUP_CSV_METADATA.xml`: scope `isAdminUi=Y`, `BIPSConnName=BIPresentationServer`. The report file is the **child** of the work area file (XML path `.../AtkRpaneWorkareaSvcVORow/AtkRpaneReportsMappingSvc/...`), but the child CSV has **no parent key column** (VERIFIED), so which report belongs to which work area cannot be read from the CSV alone (GUESS: the loader links them by row order or by an internal key).

## Step 3. Look at the mappings (read only)
```bash
python -I "<V>" "<RUN>/export_before/unz" --value "<WORKAREA>" --file ATK_RPANE_REPORT_MAPPING.csv
python -I "<V>" "<RUN>/export_before/unz" --value "<REPORT>" --file ORA_REPORTS_AND_ANALYTICS_MAPPING_REPORT.csv
```
No REST resource for these mappings was found (GUESS: none is published). The export is the read-back.

## Step 4. Build the rows (GUESS: not run)
Because the child file has no parent key, build the package as **one parent row + its one child row**, so there is no doubt which report belongs to which work area:
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name report_map.zip \
  --prefix "" --max-rows 2 \
  --row "ATK_RPANE_REPORT_MAPPING.csv|ProductShortName=ATK|WorkareaName=<WORKAREA>|UserWorkareaName=<WORKAREA>" \
  --row "ORA_REPORTS_AND_ANALYTICS_MAPPING_REPORT.csv|ReportName=<REPORT>|ReportPath=<RPATH>"
```
GUESS: an existing work area row sent again with only one child adds that child and leaves the other reports of the work area in place; this was **not** verified. Before any import on an environment you own, test it there with a report nobody uses, and compare the before/after exports (Step 6).

## Step 5. Import (GUESS: not run; only with the approval of Prerequisite 3)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ATK_DEFINE_REPORT_MAPPING --task-name "Map Reports to Work Areas" \
  --zip-file "<RUN>/payload/report_map.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
Write down the `ProcessId`. If the connection drops after the process started, do not import again: wait 2 minutes and do Step 6. A generic database error at the insert (`JBO-26041`): fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it).

## Step 6. Read back
Repeat Step 2 into `export_after`, then compare whole rows (no keys, because the child has no key column):
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --expect "ORA_REPORTS_AND_ANALYTICS_MAPPING_REPORT.csv=<REPORT>,<RPATH>"
```
GUESS: PASS = only your report row added; the work area file unchanged (or one row added if the work area had no mapping before; then add its `--expect` too).

## Rules and limits
1. Steps 2 and 3 are safe anywhere. Steps 4 to 6 change what every user of the work area sees: only on an environment you own, with written approval.
2. Never map a test report on a shared test environment (why this skill was not load-tested).
3. Not tested: the import, the parent/child linking, removing a mapping.
4. Export seen on one environment (release 11.13.26.10.0).

## Worked example (read part only, VERIFIED 2026-11-25)
| Step | Result |
|---|---|
| Export | 3 files: 11 work area mapping rows (4 work areas), 13 report rows; about 45 s |
| Import | not run (unsafe: a mapping shows to every user of the work area) |
