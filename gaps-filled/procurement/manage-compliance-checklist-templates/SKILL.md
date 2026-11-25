---
skill_id: "gosaas.gap-fills.procurement.manage-compliance-checklist-templates"
name: "Manage Compliance Checklist Templates (GoSaaS gap fill)"
description: "Create a new draft compliance checklist template that uses an existing active checklist section, through FSCR's setup-task CSV export and import, then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 03, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_PO_COMPLIANCE_CHECKLIST_TEMPLATES"
task_name: "Manage Compliance Checklist Templates"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas.gap-fills.procurement.manage-compliance-checklist-sections"
side_effects:
  - "Read-only CSV exports; one CSV import that creates one new checklist template. Plan as if it stays (this skill never deletes)."
---

# Manage Compliance Checklist Templates (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A compliance checklist template lists the sections a buyer's checklist will have. Use this skill to create a **new draft** template. Do not use it to change an existing one.
Oracle stores it as a supplier qualification model with usage **`CHECKLIST`** (not `ORA_CHECKLIST`). VERIFIED

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
BU     = the short code (name) of a business unit with the procurement business function (one that has a row in
         PO_SYSTEM_PARAMETER.csv of task PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION; read only)
NAME   = the new template's internal name, PREFIX + short name (e.g. GAPFILL_AB_T1)
TITLE  = a description
SEC    = an ACTIVE checklist section (revision 0) owned by BU, see the sections skill
```
Pick names that do not exist yet. Do not reuse names from the worked example.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` (Git Bash otherwise rewrites values that start with `/`). VERIFIED
- Shell variables do not survive between tool calls: keep values in files under `RUN`.
- Save every FSCR script's output to a file (`> "<RUN>/<step>.out" 2>&1`) and print only the lines you need: error lines can hold the server address.
- Never read the import log with cat, sed or grep (it holds a user name and the environment name). Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/<import folder>"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. The ProcessId: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<import>.out"`.
- Never print whole export rows: owner columns (`ListName...`, `EmailAddress...`) and audit columns hold names. FSCR's file names start with the environment name: do not copy them into reports.
- If an export makes no ZIP (`Error: Failed calling ...`; the unzip line then fails with `IndexError`), run it again into a **new** folder (read-only) and use that folder in every later command. VERIFIED (it happens often)
- Do not wrap the import in a shell `timeout`. If its connection drops after the ProcessId line, **never import again**: `mkdir -p` the import folder, fetch the log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ORA_PO_COMPLIANCE_CHECKLIST_TEMPLATES --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/<import folder>/recovered_process_log.txt"` (repeat until complete), then use the log reader on that folder.
- `compare_exports.py` counts rows from earlier test runs as "before" rows: counts grow with every run.

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Prerequisites
- An **active** checklist section SEC (sections skill: an active section needs an active question). GUESS: a draft section may not be accepted; we used an active one.
- A procurement BU (as in the sections skill).

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_PO_COMPLIANCE_CHECKLIST_TEMPLATES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run the export again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 4 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `ORA_POQ_CHECKLIST_TEMPLATE.csv`, `ORA_POQ_CHECKLIST_TEMPLATE_BUSINESS_UNITS.csv`, `ORA_POQ_CHECKLIST_TEMPLATE_SECTIONS.csv`. Our environment started with 0 rows.

## Step 2. Build the package (new template + one section row)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_POQ_CHECKLIST_TEMPLATE.csv=QualModelName \
  --row "ORA_POQ_CHECKLIST_TEMPLATE.csv|QualModelName=<NAME>|RevisionNumber=0|ShortCode_QualModel=<BU>|QualModelDescription=<TITLE>|GlobalFlag=Y|QualModelStatus=DRAFT|QualModelLevel=SUPPLIER|LatestRevisionFlag=Y|QualModelUsageCode=CHECKLIST" \
  --row "ORA_POQ_CHECKLIST_TEMPLATE_SECTIONS.csv|ORA_POQ_CHECKLIST_TEMPLATE.QualModelName=<NAME>|ORA_POQ_CHECKLIST_TEMPLATE.RevisionNumber=0|ORA_POQ_CHECKLIST_TEMPLATE.ShortCode_QualModel=<BU>|DisplaySequence=1|QualAreaName=<SEC>|RevisionNumber_QualModelArea=0|ShortCode=<BU>|QualAreaUsageCode=ORA_CHECKLIST|ObjectVersionNumber1=1"
```
Two traps (both VERIFIED):
- **`QualModelUsageCode=CHECKLIST`**. With `ORA_CHECKLIST` the import says success, but the template is **invisible** (not in the export, not in REST). Our test templates GAPFILL_AB_B3_CT2 and CT4 were lost this way.
- **`ObjectVersionNumber1=1`** on the section row. Without it the import fails with `JBO-56012 ... JBO-26048` (SQLException).
Codes: status `DRAFT` (`POQ_QUAL_MODEL_STATUS`), level `SUPPLIER` (`POQ_QUAL_MODEL_LEVEL`). Leave owner and audit columns empty (Oracle sets the owner). VERIFIED

## Step 3. Import
Approval: the person must approve the environment, the task and NAME before this step.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_PO_COMPLIANCE_CHECKLIST_TEMPLATES --task-name "Manage Compliance Checklist Templates" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result" > "<RUN>/import_result.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import_result.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"
```
Success (VERIFIED): `Compliance Checklist Template. Status: Completed successfully`, `1 rows were processed. 0 rows of them failed`, `IMPORT: PASS`. **Success in the log is not enough** (see the usage-code trap): always do Step 4.

## Step 4. Read back (second export + compare)
Repeat Step 1 with `export_after` (a new folder if it makes no ZIP), then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_POQ_CHECKLIST_TEMPLATE.csv=QualModelName \
  --key ORA_POQ_CHECKLIST_TEMPLATE_SECTIONS.csv=ORA_POQ_CHECKLIST_TEMPLATE.QualModelName+QualAreaName \
  --expect ORA_POQ_CHECKLIST_TEMPLATE.csv=<NAME> --expect "ORA_POQ_CHECKLIST_TEMPLATE_SECTIONS.csv=<NAME>+<SEC>"
```
`RESULT: PASS` = template and its section row added, nothing removed or changed. VERIFIED. REST `supplierQualificationModels` lists only qualification models, not checklist templates (VERIFIED): the export is the read-back.

## Rules and limits
1. New records only. Templates stay (this skill never deletes). Activating a template was not tested.
2. Keep all 4 files in the package; metadata XML unchanged.
3. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | Result |
|---|---|
| CT1: usage ORA_CHECKLIST + draft section row | failed JBO-56012 (100004744396548), not created |
| CT2: usage ORA_CHECKLIST, no section | log success (100004744396561) but invisible in export and REST |
| CT3: + active section, no ObjectVersionNumber1 | failed JBO-56012 (100004744396574) |
| CT4: ORA_CHECKLIST + ObjectVersionNumber1=1 | log success (100004744393701) but invisible |
| CT5: **CHECKLIST** + ObjectVersionNumber1=1, section `GAPFILL_AB_B3_CS3` | ProcessId 100004744396588: 1 row, 0 failed; compare PASS (template + section row added) |
