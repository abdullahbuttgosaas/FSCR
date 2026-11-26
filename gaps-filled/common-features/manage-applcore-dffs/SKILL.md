---
skill_id: "gosaas.gap-fills.common-features.manage-applcore-dffs"
name: "Manage Applications Core Descriptive Flexfields: add a new context with one segment by FSM CSV (GoSaaS gap fill)"
description: "Adds ONE new context with ONE context-sensitive text segment to an Applications Core descriptive flexfield in the task's scope (for example Attached Documents DFF FND_ATTACHED_DOCUMENTS) through FSM CSV import; the flexfield's parent row goes in unchanged. For a test the context is DISABLED, so no page offers it. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 16, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_APPLCORE_DESCRIPTIVE_FLEXFIELDS"
task_name: "Manage Applications Core Descriptive Flexfields"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "core.fusion-api.apps-common.descriptive-flexfields (FSCR's DFF rules; read for real designs)"
side_effects:
  - "Step 3 adds a context and a segment to a flexfield used by everyone. An ENABLED context appears in that flexfield's context list on its pages. A test uses EnabledFlag N."
  - "The flexfield's parent row is sent unchanged (Oracle needs it in the same ZIP); the read-back proves it did not change."
---

# Manage Applications Core Descriptive Flexfields (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). FSCR's general DFF skill (`core/fusion-api/apps-common/descriptive-flexfields`) holds the design rules; this skill is the tested load path for this task. It runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
This task's package (VERIFIED, 13 files) holds the Applications Core flexfields that already have user contexts or segments (on the test environment: `FND_VS_VALUES_B` Value Set Values, `FND_ATTACHED_DOCUMENTS` Attached Documents DFF). The files used here:
- `FND_APP_DESCRIPTIVE_FLEXFIELD.csv`: the flexfield (parent, sent unchanged)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv`: contexts (new row)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv`: context-sensitive segments (new row; NOT `..._CONTEXT_SEGMENT.csv`, which holds the context selector)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv`: global segments (read only: their columns cannot be reused)
Use it to add a context with a field. **For a test**, the context is disabled (`EnabledFlag N`): it exists but no page offers it.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
P     = <GAPS>/common-features/manage-applcore-dffs/scripts/dff_context_package.py   (offline package builder)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
PREFIX= your test prefix, e.g. GAPFILL_XX_
DFF   = flexfield code from the export, e.g. FND_ATTACHED_DOCUMENTS
CTX   = new context code = PREFIX + short name (e.g. GAPFILL_XX_CTX1)
SEG   = new segment code = PREFIX + short name, at most 30 characters (e.g. GAPFILL_XX_SEG1)
COL   = a table column not used by a global segment of DFF (Step 1 lists the used ones), e.g. ATTRIBUTE3
VS    = an existing character value set, e.g. Text 150 (it must be in the export's segment rows or exist live)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; with a valid cached sign-in it returns at once and opens no browser). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name).

## Prerequisites
The flexfield must be in the task export: Step 1 lists the usable flexfields, and `<P>` refuses one it does not find.
1. Note the flexfield's deployment status before (read only, VERIFIED):
   ```bash
   cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/descriptiveFlexfields --query "q=DescriptiveFlexfieldCode='<DFF>'" --query onlyData=true --no-open-browser --output dff_before.json > dff_before.log 2>&1
   python -I -c "import json; print([(r['DescriptiveFlexfieldCode'],r['Name'],r['DeploymentStatus']) for r in json.load(open('dff_before.json',encoding='utf-8'))['items']])"
   ```

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code FND_MANAGE_APPLCORE_DESCRIPTIVE_FLEXFIELDS --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys; print([(r['DescriptiveFlexfieldCode'],r['Name']) for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))])" "<RUN>/exp1/unz/FND_APP_DESCRIPTIVE_FLEXFIELD.csv"
```
13 CSVs + metadata. The last line lists the flexfields you can use. In the child files the flexfield code is in the column `FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode`. List the existing contexts and the columns already used for your DFF:
```bash
python -I -c "import csv,sys; d,f=sys.argv[1],sys.argv[2]; K='FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode'; rd=lambda n: [r for r in csv.DictReader(open(d+'/'+n,encoding='utf-8-sig')) if r[K]==f]; print('contexts', [r['ContextCode'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv')]); print('global columns', [r['ColumnName'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv')]); print('context columns', sorted({r['ColumnName'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv')}))" "<RUN>/exp1/unz" <DFF>
```
`<CTX>` must not be in `contexts`; `<COL>` must not be in `global columns` (a column used by another flexfield does not matter). Context-sensitive segments of different contexts may share a column (GUESS, as on other flexfields). No ZIP: run again into a NEW folder, up to 3 tries, and use that folder in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<P>" --export-dir exp1/unz --dff <DFF> --prefix <PREFIX> --context <CTX> --segment <SEG> --column <COL> --value-set "<VS>" --enabled N --out-dir pay --zip-name dff.zip
```
Success: three lines `FND_APP_DESCRIPTIVE_FLEXFIELD.csv: 1 rows (parent, unchanged)`, `..._CONTEXT.csv: 1 rows`, `..._SEGMENT.csv: 1 rows`, then `wrote pay\dff.zip`. The builder refuses codes without the prefix, an existing context, a segment code over 30 characters and a column used by a global segment. It leaves `MultirowFlag`, `TranslatableFlag` and `AdvancedQueryFlag` empty (a GoSaaS colleague saw `N` refused there on another DFF) and makes the API names (`ContextIdentifier`, `SegmentIdentifier`) from the codes.

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code FND_MANAGE_APPLCORE_DESCRIPTIVE_FLEXFIELDS --task-name "Manage Applications Core Descriptive Flexfields" --zip-file "<RUN>/pay/dff.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be an absolute path. Write down the ProcessId. Success: `A total of 3 rows were processed. 0 rows of them failed` (parent + context + segment) and `Business object: Application Descriptive Flexfield. Status: Completed successfully`. Print only these grep lines (the log holds the environment name and user). Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again (Step 1's first two lines with `exp2`), then:
```bash
cd "<RUN>"; python -I "<CMP>" exp1/unz exp2/unz --key "FND_APP_DESCRIPTIVE_FLEXFIELD.csv=DescriptiveFlexfieldCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=ContextCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=SegmentCode" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=<CTX>" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=<SEG>"
```
`RESULT: PASS` = context +1 and segment +1, the flexfield rows `changed 0`, nothing removed. Then run the prerequisite 1 lines again with `dff_after`: `DeploymentStatus` stays as before (VERIFIED: `DEPLOYED` before and after; no deploy step was needed or run).

## Rules and limits
1. A test loads `--enabled N` only. Enabling a context (`Y`) shows it on the flexfield's pages for everyone: only for an approved real change.
2. New contexts only: never send a changed parent, context or segment row (a re-import updates it for everyone). There is no delete by CSV.
3. Only flexfields in this task's export can be used; a flexfield with no user context yet is not in the export (GUESS: it then needs a parent row read by REST, as in the GoSaaS Purchasing DFF skill).
4. Tested with one text segment (TEXT_BOX, value set `Text 150`) on `FND_ATTACHED_DOCUMENTS`; other display types and flexfields are GUESS.
5. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Export | flexfields `FND_VS_VALUES_B`, `FND_ATTACHED_DOCUMENTS`; contexts 4, segments 5 |
| Import | context `GAPFILL_AB_B16_CTX1` (disabled) + segment `GAPFILL_AB_B16_SEG1` on `ATTRIBUTE3`, value set `Text 150`, DFF `FND_ATTACHED_DOCUMENTS`: ProcessId 100004744435230; 3 processed, 0 failed |
| Compare | contexts 4 → 5, segments 5 → 6, flexfields 2 → 2 changed 0: PASS; REST `DeploymentStatus` DEPLOYED before and after |
| Fresh test (another tester, only this skill) | `GAPFILL_AB_B16_CTX2F` + `SEG2F` on `ATTRIBUTE4`: ProcessId 100004744434847; contexts 5 → 6, segments 6 → 7: PASS (ProcessIds are not in time order) |
