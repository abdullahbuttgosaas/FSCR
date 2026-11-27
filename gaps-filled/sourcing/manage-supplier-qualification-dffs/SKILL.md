---
skill_id: "gosaas.gap-fills.sourcing.manage-supplier-qualification-dffs"
name: "Manage Supplier Qualification Descriptive Flexfields: add a disabled context with one segment by FSM CSV (GoSaaS gap fill)"
description: "Adds ONE new DISABLED context with ONE text segment to a Supplier Qualification (POQ) descriptive flexfield, for example POQ_INITIATIVES (Initiatives), through FSCR's setup-task CSV export and import, then proves by a second export that only the new rows were added and that the flexfield stays deployed. No deployment is needed or run. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing and Supplier Management batch 03, 2026-11-28. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_DESCRIPTIVE_FLEXFIELDS"
task_name: "Manage Supplier Qualification Descriptive Flexfields"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.2"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gaps-filled common-features/manage-applcore-dffs (builder dff_context_package.py, check check_dff_rows.py)"
side_effects:
  - "Adds a context and a segment to a flexfield used by everyone. A DISABLED context (EnabledFlag N) is not offered on any page. There is no delete by CSV: plan as if it stays."
  - "The flexfield's parent row is sent unchanged (Oracle needs it in the same ZIP); the read-back proves it did not change."
---

# Manage Supplier Qualification Descriptive Flexfields (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog routes this task (CSV flag Y) but has no skill. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-28) · **GUESS** = not run live.

## What it is and when to use
Descriptive flexfields (DFFs) add extra fields to Supplier Qualification objects (qualifications, assessments, initiatives). The task export is the standard flexfield package scoped to the Supplier Qualification module (`PrcPoqCommon`): 13 CSVs + `ASM_SETUP_CSV_METADATA.xml`. The files used here:
- `FND_APP_DESCRIPTIVE_FLEXFIELD.csv`: the flexfield (parent, sent unchanged)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv`: contexts (new row)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv`: context-sensitive segments (new row)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv`: global segments (read only: their columns cannot be reused)

**Two cases (VERIFIED):** the export lists a flexfield only after it has at least one user context. **Case A**: the flexfield is not in the export (our first export had 0 rows in every file); its parent row is read by REST. **Case B**: the flexfield is in the export with its contexts (true for `POQ_INITIATIVES` after our test).

Supplier Qualification flexfields seen by REST (VERIFIED, all `ProtectedFlag N`, `DEPLOYED`, ApplicationId 10129): `POQ_ASSESSMENTS` (Assessments), `POQ_INITIATIVES` (Initiatives), `POQ_QUALIFICATIONS` (Qualifications). Only `POQ_INITIATIVES` was tested.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds sourcing\ and common-features\)
H     = <GAPS>/common-features/manage-applcore-dffs/scripts   (dff_context_package.py builder, check_dff_rows.py check)
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); create it first: mkdir -p "<RUN>"
PREFIX= your test prefix, e.g. GAPFILL_XX_
DFF   = the flexfield code, e.g. POQ_INITIATIVES
CTX   = new context code = PREFIX + short name (e.g. GAPFILL_XX_QDX1)
SEG   = new segment code = PREFIX + short name, at most 30 characters
COL   = a free ATTRIBUTE column, e.g. ATTRIBUTE10 (ATTRIBUTE1 to ATTRIBUTE20: GUESS from Oracle's tables; ATTRIBUTE10 VERIFIED). Not a column of a global segment and not one already used by another context's segment (Step 1 lists them)
VS    = an existing character value set, e.g. Text 150 (VERIFIED)
DAY   = the date the export writes on your new row, yyyy/mm/dd (Case A only; read it in Step 4: the server may be on another date than you)
```
Every `<...>` below is a placeholder: put the real value in its place. Git Bash: paths as `E:/...`; start every call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; shell variables do not survive between calls.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person completes the browser page on port 8765). Run it only when needed: while the cached sign-in is valid (about one hour) every step below uses it without this command. If a step fails with HTTP 401/403 or hangs, sign in and repeat the step (an import only after an export shows it did not run). Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name); never print `ASM_SETUP_CSV_METADATA.xml`, export CSVs whole or the import log whole.

## Prerequisites
1. Read the flexfield's parent row live (read only, VERIFIED):
   ```bash
   export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
   cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/descriptiveFlexfields --query "q=DescriptiveFlexfieldCode='<DFF>'" --query onlyData=true --no-open-browser --output "<RUN>/parent.json" > "<RUN>/parent.log" 2>&1; echo "rc=$?"
   python -I -c "import json,sys; print([(r['DescriptiveFlexfieldCode'],r['Name'],r['ProtectedFlag'],r['DeploymentStatus']) for r in json.load(open(sys.argv[1],encoding='utf-8'))['items']])" "<RUN>/parent.json"
   ```
   One row, `ProtectedFlag N`. Note `DeploymentStatus` (VERIFIED `DEPLOYED`). To list the Supplier Qualification flexfields use `--query "q=DescriptiveFlexfieldCode LIKE 'POQ%'"`.

## Step 1. Read-only export (about 1 minute)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_DESCRIPTIVE_FLEXFIELDS --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys; d,f=sys.argv[1],sys.argv[2]; K='FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode'; rd=lambda n: [r for r in csv.DictReader(open(d+'/'+n,encoding='utf-8-sig')) if r[K]==f]; print('flexfield in export:', any(r['DescriptiveFlexfieldCode']==f for r in csv.DictReader(open(d+'/FND_APP_DESCRIPTIVE_FLEXFIELD.csv',encoding='utf-8-sig')))); print('contexts', [r['ContextCode'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv')]); print('global columns', [r['ColumnName'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv')]); print('context columns', sorted({r['ColumnName'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv')}))" "<RUN>/exp1/unz" "<DFF>"
```
`flexfield in export: False` = **Case A**; `True` = **Case B**. `<CTX>` must not be among `contexts`; `<COL>` must not be in `global columns` or `context columns`. No ZIP: run again into a NEW folder, up to 3 tries, and use that folder in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<RUN>"; python -I "<H>/dff_context_package.py" --export-dir exp1/unz --dff <DFF> --parent-json parent.json --prefix <PREFIX> --context <CTX> --segment <SEG> --column <COL> --value-set "<VS>" --enabled N --out-dir pay --zip-name dff.zip
```
Success: (Case A only) `parent row of <DFF> taken from parent.json (REST read)`, then `FND_APP_DESCRIPTIVE_FLEXFIELD.csv: 1 rows (parent, unchanged)`, `..._CONTEXT.csv: 1 rows`, `..._SEGMENT.csv: 1 rows`, `wrote pay\dff.zip`. In Case B the parent row is copied from the export. The builder refuses codes without the prefix, an existing context, a segment code over 30 characters and a column used by a global segment.

## Step 3. Import ONCE (VERIFIED)
Approval: the person must approve the environment, the task and the new codes before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
mkdir -p "<RUN>/imp"; cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_DESCRIPTIVE_FLEXFIELDS --task-name "Manage Supplier Qualification Descriptive Flexfields" --zip-file "<RUN>/pay/dff.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/imp"
```
`--zip-file` must be an absolute path. Write down the ProcessId. Success: `Business object: Application Descriptive Flexfield. Status: Completed successfully`, `A total of 3 rows were processed. 0 rows of them failed`, `IMPORT: PASS`. Never print `imp.log` or the process log whole (they hold the environment name and a user): the `grep -o` line and `read_import_log.py` above are the only safe reads. No ProcessId line: do not import again; check with Step 4's export first. Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again: run Step 1's export command AND its unzip line (the two lines after `export PYTHONUTF8...`) with `exp1` replaced by `exp2` everywhere. Then:
- **Case A** (flexfield was not in the before-export): read `<DAY>` from your new context row, then prove that only your two rows were created or updated that day:
  ```bash
  export PYTHONUTF8=1
  cd "<RUN>"; python -I -c "import csv,sys; print([r['CreationDate'][:10] for r in csv.DictReader(open('exp2/unz/ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv',encoding='utf-8-sig')) if r['ContextCode']==sys.argv[1]])" <CTX>
  python -I "<H>/check_dff_rows.py" --export-dir exp2/unz --dff <DFF> --date <DAY> --prefix <PREFIX> --expect-context <CTX> --expect-segment <SEG>
  ```
- **Case B** (flexfield was already in the before-export):
  ```bash
  export PYTHONUTF8=1
  cd "<RUN>"; python -I "<GAPS>/sourcing/scripts/compare_exports.py" exp1/unz exp2/unz --key "FND_APP_DESCRIPTIVE_FLEXFIELD.csv=DescriptiveFlexfieldCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode+ContextCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode+SegmentCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT_SEGMENT.csv=FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode+ContextCode+SegmentCode" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=<DFF>+<CTX>" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=<DFF>+<SEG>"
  ```
Both print `RESULT: PASS` when only your context and segment were added (in Case B other people's new contexts between your two exports would also show as added; nothing may be removed or changed). Check your context is disabled:
```bash
export PYTHONUTF8=1
cd "<RUN>"; python -I -c "import csv,sys; print([(r['ContextCode'],r['EnabledFlag']) for r in csv.DictReader(open('exp2/unz/ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv',encoding='utf-8-sig')) if r['ContextCode']==sys.argv[1]])" <CTX>
```
Expect `[('<CTX>', 'N')]`. Then run Prerequisite 1 again with `parent.json`/`parent.log` renamed `parent_after.json`/`parent_after.log`: `DeploymentStatus` unchanged (VERIFIED `DEPLOYED` before and after; no deploy step needed or run).

## Rules and limits
1. A test loads `--enabled N` only. Enabling a context shows it to everyone on the flexfield's pages; that is a real change for the flexfield owner to approve.
2. New contexts only; never send a changed parent, context or segment row (a re-import updates it for everyone). No delete by CSV.
3. Tested on `POQ_INITIATIVES` with one text segment (value set `Text 150`, column ATTRIBUTE10). Other Supplier Qualification flexfields and display types: GUESS.
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-28, codes and ProcessIds only)
| Step | Result |
|---|---|
| Before | task export 13 CSVs, all 0 rows (Case A); parent `POQ_INITIATIVES` read by REST, `ProtectedFlag N`, `DEPLOYED` |
| Import | context `GAPFILL_AB_S3_QDX1` (disabled) + segment `GAPFILL_AB_S3_QDS1` on `ATTRIBUTE10`, value set `Text 150`: ProcessId 100004744442213; 3 processed, 0 failed |
| Read back | export now: flexfield 1, context 1, context segment 1 (the built-in ATTRIBUTE_CATEGORY selector row, not the new segment; it does not grow), segment 1; `check_dff_rows.py` PASS (only the 2 own rows touched on the server date 2026/11/27); `EnabledFlag N`; `DEPLOYED` before and after |
