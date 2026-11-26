---
skill_id: "gosaas.gap-fills.procurement.manage-contract-terms-dff"
name: "Manage Contract Terms Descriptive Flexfields: add a disabled context with one segment by FSM CSV (GoSaaS gap fill)"
description: "Adds ONE new DISABLED context with ONE text segment to a contract terms (OKC) descriptive flexfield, for example OKC_ARTICLES_DESCFLEX (Clause), through FSCR's setup-task CSV export and import, then proves by a second export that only the new rows were added and that the flexfield stays deployed. No deployment is needed or run. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 04 (2026-11-25, written), re-opened and tested in batch 07 (2026-11-27). NOT official FSCR."
task_code: "ORA_OKC_MANAGE_CONTRACT_TERMS_DESCRIPTIVE_FLEXFIELDS"
task_name: "Manage Contract Terms Descriptive Flexfields"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.2.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gaps-filled common-features/manage-applcore-dffs (builder dff_context_package.py, check check_dff_rows.py)"
side_effects:
  - "Adds a context and a segment to a flexfield used by everyone. A DISABLED context (EnabledFlag N) is not offered on any page. There is no delete by CSV: plan as if it stays."
  - "The flexfield's parent row is sent unchanged (Oracle needs it in the same ZIP); the read-back proves it did not change."
---

# Manage Contract Terms Descriptive Flexfields (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog routes this task (CSV flag Y) but has no skill. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-27) · **GUESS** = not run live.
> Version 0.1.0 (2026-11-25) said a test needs a flexfield deployment and is unsafe. That was wrong: a DISABLED context loads without any deployment and the flexfield stays `DEPLOYED` (VERIFIED here and on three Common Features flexfields).

## What it is and when to use
Descriptive flexfields (DFFs) add extra fields to contract terms objects. The task export is the standard flexfield package for module OKC (13 CSVs + `ASM_SETUP_CSV_METADATA.xml`). The files used here:
- `FND_APP_DESCRIPTIVE_FLEXFIELD.csv`: the flexfield (parent, sent unchanged)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv`: contexts (new row)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv`: context-sensitive segments (new row)
- `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv`: global segments (read only: their columns cannot be reused)

**Important (VERIFIED):** the export lists a flexfield only after it has at least one user context. While none of the OKC flexfields has one, the export is header only (Case A) and the parent row is read by REST. After the first context exists, the export lists the flexfield with all its contexts (Case B).
OKC flexfields seen by REST: `OKC_ARTICLES_DESCFLEX` (Clause) and `OKC_LINES_DESC_FLEX` (Contract Line). Only the Clause flexfield was tested.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds procurement\ and common-features\)
H     = <GAPS>/common-features/manage-applcore-dffs/scripts   (dff_context_package.py builder, check_dff_rows.py check)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); create it first: mkdir -p "<RUN>"
PREFIX= your test prefix, e.g. GAPFILL_XX_
DFF   = OKC_ARTICLES_DESCFLEX (Clause)
CTX   = new context code = PREFIX + short name (e.g. GAPFILL_XX_CCX1)
SEG   = new segment code = PREFIX + short name, at most 30 characters
COL   = a free ATTRIBUTE column: ATTRIBUTE1 to ATTRIBUTE15 (GUESS from Oracle's OKC tables; ATTRIBUTE11 and the fresh test's column VERIFIED). Not a column of a global segment (Step 1 lists them)
VS    = an existing character value set, e.g. Text 150
DAY   = the date the export writes on your new row, yyyy/mm/dd (Case A only; read it in Step 4, the server may be on another date than you)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; a valid cached sign-in returns at once). About one hour. If a step fails with HTTP 401/403 or hangs, sign in again and repeat the step (an import only after an export shows it did not run). Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name); never print `ASM_SETUP_CSV_METADATA.xml`.

## Prerequisites
1. Read the flexfield's parent row live (read only, VERIFIED):
   ```bash
   cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/descriptiveFlexfields --query "q=DescriptiveFlexfieldCode='<DFF>'" --query onlyData=true --no-open-browser --output parent.json > parent.log 2>&1
   python -I -c "import json; print([(r['DescriptiveFlexfieldCode'],r['Name'],r['ProtectedFlag'],r['DeploymentStatus']) for r in json.load(open('parent.json',encoding='utf-8'))['items']])"
   ```
   One row, `ProtectedFlag N`. Note `DeploymentStatus` (VERIFIED `DEPLOYED`). To list OKC flexfields: same call with `q=DescriptiveFlexfieldCode LIKE 'OKC%'`.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_OKC_MANAGE_CONTRACT_TERMS_DESCRIPTIVE_FLEXFIELDS --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys; d,f=sys.argv[1],sys.argv[2]; K='FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode'; rd=lambda n: [r for r in csv.DictReader(open(d+'/'+n,encoding='utf-8-sig')) if r[K]==f]; print('contexts', [r['ContextCode'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv')]); print('global columns', [r['ColumnName'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv')]); print('context columns', sorted({r['ColumnName'] for r in rd('ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv')}))" "<RUN>/exp1/unz" <DFF>
```
**Case A:** `contexts` is empty (no user context yet; every CSV has 0 rows). **Case B:** contexts are listed (for example the worked example's `GAPFILL_AB_B7_CCX1`). `<CTX>` must not be among them; `<COL>` must not be in `global columns`, and pick one not yet in `context columns` to keep it simple. No ZIP: run again into a NEW folder, up to 3 tries, and use that folder in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<H>/dff_context_package.py" --export-dir exp1/unz --dff <DFF> --parent-json parent.json --prefix <PREFIX> --context <CTX> --segment <SEG> --column <COL> --value-set "<VS>" --enabled N --out-dir pay --zip-name dff.zip
```
Success: (Case A only) `parent row of <DFF> taken from parent.json (REST read)`, then `FND_APP_DESCRIPTIVE_FLEXFIELD.csv: 1 rows (parent, unchanged)`, `..._CONTEXT.csv: 1 rows`, `..._SEGMENT.csv: 1 rows`, `wrote pay\dff.zip`. The builder refuses codes without the prefix, an existing context, a segment code over 30 characters and a column used by a global segment.

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_OKC_MANAGE_CONTRACT_TERMS_DESCRIPTIVE_FLEXFIELDS --task-name "Manage Contract Terms Descriptive Flexfields" --zip-file "<RUN>/pay/dff.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be an absolute path. Write down the ProcessId. Success: `A total of 3 rows were processed. 0 rows of them failed` and `Business object: Application Descriptive Flexfield. Status: Completed successfully`. Print only these grep lines (the log holds the environment name and a user). No `*_process_log.txt`: read the last lines of `imp.log` and check with Step 4's export before any new try. Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again: Step 1's first two lines with `exp1` replaced by `exp2` everywhere. Then:
- **Case A** (before-export was empty): read `<DAY>` from your new context row, then prove that only your two rows were created or updated that day:
  ```bash
  cd "<RUN>"; python -I -c "import csv,sys; print([r['CreationDate'][:10] for r in csv.DictReader(open('exp2/unz/ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv',encoding='utf-8-sig')) if r['ContextCode']==sys.argv[1]])" <CTX>
  python -I "<H>/check_dff_rows.py" --export-dir exp2/unz --dff <DFF> --date <DAY> --prefix <PREFIX> --expect-context <CTX> --expect-segment <SEG>
  ```
- **Case B** (the flexfield was already in the before-export):
  ```bash
  cd "<RUN>"; python -I "<CMP>" exp1/unz exp2/unz --key "FND_APP_DESCRIPTIVE_FLEXFIELD.csv=DescriptiveFlexfieldCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=ContextCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=SegmentCode" --key "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT_SEGMENT.csv=FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode,SegmentCode" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv=<CTX>" --expect "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv=<SEG>"
  ```
Both print `RESULT: PASS` when only your context and segment were added. Check your context is disabled:
```bash
cd "<RUN>"; python -I -c "import csv,sys; print([(r['ContextCode'],r['EnabledFlag']) for r in csv.DictReader(open('exp2/unz/ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv',encoding='utf-8-sig')) if r['ContextCode']==sys.argv[1]])" <CTX>
```
Expect `[('<CTX>', 'N')]`. Then run Prerequisite 1 again into `parent_after.json`: `DeploymentStatus` unchanged (VERIFIED `DEPLOYED` before and after; no deploy step needed or run).

## Rules and limits
1. A test loads `--enabled N` only. Enabling a context shows it to everyone on the flexfield's pages; that is a real change for the flexfield owner to approve.
2. New contexts only; never send a changed parent, context or segment row (a re-import updates it for everyone). No delete by CSV.
3. Tested on `OKC_ARTICLES_DESCFLEX` with one text segment (value set `Text 150`). `OKC_LINES_DESC_FLEX` and other display types: GUESS.
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-27, codes and ProcessIds only)
| Step | Result |
|---|---|
| Before | task export 13 CSVs, all 0 rows (Case A); parent `OKC_ARTICLES_DESCFLEX` read by REST, `ProtectedFlag N`, `DEPLOYED` |
| Import | context `GAPFILL_AB_B7_CCX1` (disabled) + segment `GAPFILL_AB_B7_CSG1` on `ATTRIBUTE11`, value set `Text 150`: ProcessId 100004743464073; 3 processed, 0 failed |
| Read back | export now: flexfield 1, context 1, context segment (selector) 1, segment 1; `check_dff_rows.py` PASS (only the 2 own rows touched; parent changed 0); `EnabledFlag N`; `DEPLOYED` before and after |
