---
skill_id: "gosaas.gap-fills.procurement.manage-compliance-checklist-sections"
name: "Manage Compliance Checklist Sections (GoSaaS gap fill)"
description: "Create a new compliance checklist section (with its US translation and, for an active section, its questions) through FSCR's setup-task CSV export and import, then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 03, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS"
task_name: "Manage Compliance Checklist Sections"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas.gap-fills.procurement.manage-compliance-checklist-questions"
side_effects:
  - "Read-only CSV exports; one CSV import that creates one new checklist section. Plan as if it stays (this skill never deletes)."
---

# Manage Compliance Checklist Sections (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A compliance checklist section groups checklist questions. Templates (task `ORA_PO_COMPLIANCE_CHECKLIST_TEMPLATES`) are built from sections. Use this skill to create a **new** section. Do not use it to change an existing one.
Oracle stores sections as supplier qualification areas with usage code `ORA_CHECKLIST`. VERIFIED

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
BU     = the short code (name) of a business unit with the procurement business function (one that has a row in
         PO_SYSTEM_PARAMETER.csv of task PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION; read only)
NAME   = the new section's internal name, PREFIX + short name (e.g. GAPFILL_AB_SEC1)
TITLE  = the section name users see
QNAME  = (active section only) an ACTIVE checklist question, see the questions skill
```
Pick names that do not exist yet. Do not reuse names from the worked example.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` (Git Bash otherwise rewrites values that start with `/`). VERIFIED
- Shell variables do not survive between tool calls: keep values in files under `RUN`.
- Save every FSCR script's output to a file (`> "<RUN>/<step>.out" 2>&1`) and print only the lines you need: error lines can hold the server address.
- Never read the import log with cat, sed or grep (it holds a user name and the environment name). Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/<import folder>"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. The ProcessId: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<import>.out"`.
- Never print whole export rows: owner columns (`ListName...`, `EmailAddress...`) and audit columns hold names. FSCR's file names start with the environment name: do not copy them into reports.
- If an export makes no ZIP (`Error: Failed calling ...`; the unzip line then fails with `IndexError`), run it again into a **new** folder (read-only) and use that folder in every later command. VERIFIED (it happens often)
- Do not wrap the import in a shell `timeout`. If its connection drops after the ProcessId line, **never import again**: `mkdir -p` the import folder, fetch the log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/<import folder>/recovered_process_log.txt"` (repeat until complete), then use the log reader on that folder.
- `compare_exports.py` counts rows from earlier test runs as "before" rows: counts grow with every run.

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Prerequisites
- A procurement business unit (BU). VERIFIED: a BU without the procurement function was refused in an earlier try (`PrcBuId isn't valid`).
- A **draft** section needs no question. An **active** section needs at least 1 **active** question. VERIFIED (`POQ_AREA_QUES_REQD_ERROR: You must add at least 1 question`).
- The owner is set by Oracle (to the signed-in user) when `DefaultQualOwnerFlag=Y` and the owner columns are empty. VERIFIED. Never type a person's name or email.

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run the export again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 5 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `ORA_POQ_CHECKLIST_SECTION.csv`, `ORA_POQ_CHECKLIST_SECTION_BU_ACCESSES.csv`, `ORA_POQ_CHECKLIST_SECTION_QUESTIONS.csv`, `ORA_POQ_TRANS_CHECKLIST_SECTION.csv`. Our environment started with 0 rows.

## Step 2. Build the package (new section only)
Draft section (no question):
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_POQ_CHECKLIST_SECTION.csv=QualAreaName \
  --row "ORA_POQ_CHECKLIST_SECTION.csv|QualAreaName=<NAME>|RevisionNumber_QualArea=0|ShortCode_QualArea=<BU>|QualAreaDescription=<TITLE>|GlobalFlag=Y|QualAreaStatus=DRAFT|LatestRevisionFlag=Y|DefaultQualOwnerFlag=Y|SectionName=<TITLE>|QualAreaUsageCode=ORA_CHECKLIST" \
  --row "ORA_POQ_TRANS_CHECKLIST_SECTION.csv|ORA_POQ_CHECKLIST_SECTION.QualAreaName=<NAME>|ORA_POQ_CHECKLIST_SECTION.RevisionNumber_QualArea=0|ORA_POQ_CHECKLIST_SECTION.ShortCode_QualArea=<BU>|Language=US|SourceLang=US|SectionName=<TITLE>"
```
Active section: use `QualAreaStatus=ACTIVE` and add one row per question:
`--row "ORA_POQ_CHECKLIST_SECTION_QUESTIONS.csv|ORA_POQ_CHECKLIST_SECTION.QualAreaName=<NAME>|ORA_POQ_CHECKLIST_SECTION.RevisionNumber_QualArea=0|ORA_POQ_CHECKLIST_SECTION.ShortCode_QualArea=<BU>|QuestionName=<QNAME>|RevisionNumber_Question=0|DisplaySequence=1|QuestionUsage=ORA_CHECKLIST"` VERIFIED
- Codes (VERIFIED): status `DRAFT` / `ACTIVE` (lookup `POQ_QUAL_AREA_STATUS`); usage `ORA_CHECKLIST` (lookup `ORA_POQ_ENTITY_USAGE`).
- Leave the owner columns (`ListName_QualArea`, `EmailAddress_QualArea`, `QualOwner_...`) and audit columns empty.
- `GlobalFlag=Y` = usable by all BUs; we did not test BU access rows. GUESS.
- `Language`/`SourceLang` = `US` is our session language. GUESS: use your base language if it is not US.

## Step 3. Import
Approval: the person must approve the environment, the task and NAME before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS --task-name "Manage Compliance Checklist Sections" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result" > "<RUN>/import_result.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import_result.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"
```
Success (VERIFIED): `Compliance Checklist Section. Status: Completed successfully`, `1 rows were processed. 0 rows of them failed`, `IMPORT: PASS` (the log counts only the section, not its translation or question rows).

## Step 4. Read back (second export + compare)
Repeat Step 1 with `export_after` in place of `export_before` (a new folder if it makes no ZIP), then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_POQ_CHECKLIST_SECTION.csv=QualAreaName \
  --key ORA_POQ_TRANS_CHECKLIST_SECTION.csv=ORA_POQ_CHECKLIST_SECTION.QualAreaName+Language \
  --key ORA_POQ_CHECKLIST_SECTION_QUESTIONS.csv=ORA_POQ_CHECKLIST_SECTION.QualAreaName+QuestionName \
  --expect ORA_POQ_CHECKLIST_SECTION.csv=<NAME>
```
`RESULT: PASS` = your section (and its translation and question rows) were added, nothing removed or changed. VERIFIED

## Rules and limits
1. New records only; never import a full export. Sections stay (this skill never deletes).
2. Keep all 5 files in the package; metadata XML unchanged.
3. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | Result |
|---|---|
| Draft section `GAPFILL_AB_B3_CS1` | ProcessId 100004744391888: 1 row, 0 failed; compare PASS (owner set by Oracle) |
| Active section `GAPFILL_AB_B3_CS2`, no question | refused `POQ_AREA_QUES_REQD_ERROR` (100004744391901), not created |
| Active section `GAPFILL_AB_B3_CS3` with active question `GAPFILL_AB_B3_CQ2` | ProcessId 100004744391914: 1 row, 0 failed; compare PASS: section, translation and question row added |
