---
skill_id: "gosaas.gap-fills.common-features.manage-le-configurator-dff"
name: "Manage Legal Entity Configurator Descriptive Flexfield: add a new context with one segment to XLE_LE_INFO_DEV by FSM CSV (GoSaaS gap fill)"
description: "Adds ONE new DISABLED context with ONE text segment to the flexfield XLE_LE_INFO_DEV (Legal Entity Context) through the task's FSM CSV import; the parent row is read live by REST and sent unchanged. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 17, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_MANAGE_APPLICATION_DESCRIPTIVE_FLEXFIELD"
task_name: "Manage Legal Entity Configurator Descriptive Flexfield"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-applcore-dffs (same package and builder)"
side_effects:
  - "Step 3 adds a context and a segment to XLE_LE_INFO_DEV, a flexfield everyone's pages use. An ENABLED context appears in its context list; a test uses EnabledFlag N. The parent row is sent unchanged."
---

# Manage Legal Entity Configurator Descriptive Flexfield (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). Same package and builder as the GoSaaS skill `manage-applcore-dffs`; read FSCR's DFF skill (`core/fusion-api/apps-common/descriptive-flexfields`) for real designs. Runs FSCR's scripts in place, edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
The legal entity configurator flexfield `XLE_LE_INFO_DEV` ("Legal Entity Context": fields for legal entity context details on the legal entity page, one seeded context per country) is the flexfield of this task (GUESS: chosen by name and Oracle's table docs; the task export lists it once it has a user context, VERIFIED). The package (VERIFIED, 13 files) is the standard flexfield package: parent `FND_APP_DESCRIPTIVE_FLEXFIELD.csv`, contexts `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv`, context-sensitive segments `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv`, and others. **Important (VERIFIED):** the task export lists the flexfield only after it has at least one user context. While it has none, the export is header only and the parent row must be read by REST.
Use it to add a context with a field. **For a test**, the context is disabled (`EnabledFlag N`): it exists but no page offers it.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
H     = <GAPS>/common-features/manage-applcore-dffs/scripts   (dff_context_package.py builder, check_dff_rows.py check)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
PREFIX= your test prefix, e.g. GAPFILL_XX_
DFF   = XLE_LE_INFO_DEV
CTX   = new context code = PREFIX + short name (e.g. GAPFILL_XX_CTX1)
SEG   = new segment code = PREFIX + short name, at most 30 characters
COL   = a LE_INFORMATION column (LE_INFORMATION1 to LE_INFORMATION20 per Oracle's table docs; Step 1 lists the global ones), e.g. LE_INFORMATION11
VS    = an existing character value set, e.g. Text 150
DAY   = today's date as the export writes it, yyyy/mm/dd (server date; near midnight use the date the export shows on your row)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; with a valid cached sign-in it returns at once). About one hour. If a step fails with HTTP 401/403 or hangs, sign in again and repeat the step (an import only after checking with an export that it did not run). Never print tokens, the server address or user names; never copy FSCR's output file names; never print the ZIP's `ASM_SETUP_CSV_METADATA.xml` (it holds the environment name and a user).

## Prerequisites
1. Read the flexfield's parent row live (read only, VERIFIED); the builder uses it when the export has none:
   ```bash
   cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/descriptiveFlexfields --query "q=DescriptiveFlexfieldCode='<DFF>'" --query onlyData=true --no-open-browser --output parent.json > parent.log 2>&1
   python -I -c "import json; print([(r['DescriptiveFlexfieldCode'],r['ApplicationId'],r['ProtectedFlag'],r['DeploymentStatus']) for r in json.load(open('parent.json',encoding='utf-8'))['items']])"
   ```
   One row, `ProtectedFlag N`. Note `DeploymentStatus` (VERIFIED `DEPLOYED`).

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code XLE_MANAGE_APPLICATION_DESCRIPTIVE_FLEXFIELD --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys; d,f=sys.argv[1],sys.argv[2]; K='FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode'; rd=lambda n: [r for r in csv.DictReader(open(d+'/'+n,encoding='utf-8-sig')) if r[K]==f]; print('contexts', [r['ContextCode'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv')]); print('global columns', [r['ColumnName'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv')])" "<RUN>/exp1/unz" <DFF>
```
13 CSVs + metadata (`ls "<RUN>/exp1/unz" | wc -l` prints 14). **Case A:** `contexts` is empty: the flexfield has no user context yet (export header only). **Case B:** contexts are listed: once anyone (an earlier test too) has added a context, the export lists the flexfield with ALL its contexts, the seeded ones (if it has any) and earlier test contexts such as the worked example's `GAPFILL_AB_B17_LCX1`. On the tested environment every new run is Case B (VERIFIED). `<CTX>` must not be among them and `<COL>` must not be in `global columns`. No ZIP: run again into a NEW folder, up to 3 tries, and use that folder in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<H>/dff_context_package.py" --export-dir exp1/unz --dff <DFF> --parent-json parent.json --prefix <PREFIX> --context <CTX> --segment <SEG> --column <COL> --value-set "<VS>" --enabled N --out-dir pay --zip-name dff.zip
```
Success: (Case A only) `parent row of <DFF> taken from parent.json (REST read)`, then `FND_APP_DESCRIPTIVE_FLEXFIELD.csv: 1 rows (parent, unchanged)`, `..._CONTEXT.csv: 1 rows`, `..._SEGMENT.csv: 1 rows`, `wrote pay\dff.zip`. In Case B the parent comes from the export, so the `taken from parent.json` line does not appear; the other lines are the same. The builder refuses codes without the prefix, an existing context, a segment code over 30 characters and a column used by a global segment.

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code XLE_MANAGE_APPLICATION_DESCRIPTIVE_FLEXFIELD --task-name "Manage Legal Entity Configurator Descriptive Flexfield" --zip-file "<RUN>/pay/dff.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be an absolute path. Write down the ProcessId. Success: `A total of 3 rows were processed. 0 rows of them failed` and `Business object: Application Descriptive Flexfield. Status: Completed successfully`. Print only these grep lines. No `*_process_log.txt`: read the last lines of `imp.log` and check with Step 4's export before any new try. Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again (Step 1's first two lines with `exp1` replaced by `exp2` everywhere). Then:
- **Case A** (the before-export was empty; now the whole flexfield appears, including 36 seeded country contexts (AR, AT, ... VE) and 95 seeded segments): prove that only your two rows were created or updated today:
  ```bash
  cd "<RUN>"; python -I "<H>/check_dff_rows.py" --export-dir exp2/unz --dff <DFF> --date <DAY> --prefix <PREFIX> --expect-context <CTX> --expect-segment <SEG>
  ```
- **Case B** (the flexfield was already in the before-export):
  ```bash
  cd "<RUN>"; python -I "<CMP>" exp1/unz exp2/unz --key "FND_APP_DESCRIPTIVE_FLEXFIELD.csv=DescriptiveFlexfieldCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=ContextCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=SegmentCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT_SEGMENT.csv=FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode,SegmentCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv=FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode,SegmentCode" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=<CTX>" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=<SEG>"
  ```
Both print `RESULT: PASS` when only your context and segment were added (Case B, VERIFIED by the fresh tests: contexts and segments each go up by exactly 1). `DAY` is needed only in Case A. Check that your context is disabled:
```bash
cd "<RUN>"; python -I -c "import csv,sys; print([(r['ContextCode'],r['EnabledFlag']) for r in csv.DictReader(open('exp2/unz/ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv',encoding='utf-8-sig')) if r['ContextCode']==sys.argv[1]])" <CTX>
```
Expect `[('<CTX>', 'N')]` (VERIFIED). Then run prerequisite 1 again into `parent_after.json`: `DeploymentStatus` unchanged (VERIFIED `DEPLOYED`; no deploy step was needed or run).

## Rules and limits
1. A test loads `--enabled N` only; enabling a context shows it to everyone on the flexfield's pages.
2. New contexts only; never send a changed seeded context or segment. There is no delete by CSV.
3. The other legal entity flexfields (`XLE_LE_ADD_INFO` Legal Entity, `XLE_ETB_INFO_DEV` Legal Reporting Unit Context) were not tried with this task (GUESS).
4. Tested with one text segment (value set `Text 150`); other display types are GUESS. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Before | task export empty (Case A); parent read by REST, `ProtectedFlag N`, `DEPLOYED` |
| Import | context `GAPFILL_AB_B17_LCX1` (disabled) + segment `GAPFILL_AB_B17_LSG1` on `LE_INFORMATION11`, value set `Text 150`: ProcessId 100004743459017; 3 processed, 0 failed |
| Read back | the export now lists the flexfield with 36 seeded country contexts (AR, AT, ... VE) and 95 seeded segments (counts before any own row); only the 2 own rows were created or updated today: `check_dff_rows.py` PASS; `DEPLOYED` before and after |
| Fresh test (another tester, only this skill; Case B) | `GAPFILL_AB_B17_LCX2F` (disabled) + `GAPFILL_AB_B17_LSG2F` on `LE_INFORMATION12`: ProcessId 100004743457166; 3 processed, 0 failed; compare contexts 37 → 38, segments 96 → 97: PASS; `EnabledFlag N`; `DEPLOYED` before and after |
