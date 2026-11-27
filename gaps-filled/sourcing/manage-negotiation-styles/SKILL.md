---
skill_id: "gosaas.gap-fills.sourcing.manage-negotiation-styles"
name: "Manage Negotiation Styles (GoSaaS gap fill)"
description: "Create a new negotiation style by copying the rows of the seeded style Standard_Negotiation under a new code through FSCR's setup-task CSV export and import, then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing batch 02, 2026-11-27. Written and tested live on one test environment. NOT official FSCR."
task_code: "PON_MANAGE_NEGOTIATION_STYLES"
task_name: "Manage Negotiation Styles"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only exports and REST reads; one CSV import that creates one new negotiation style (style row, its translation and one row per document type: Auction, RFQ, RFI). There is no delete by CSV: plan as if it stays."
---

# Manage Negotiation Styles (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-27) · **GUESS** = judgment, not tested.

## What it is and when to use
A negotiation style controls which features a negotiation (auction, RFQ, RFI) shows: lines, requirements, team scoring, two-stage evaluation and so on. Oracle seeds three styles (`Standard_Negotiation`, `Simple_Negotiation`, `ORA_Two_Stage_Negotiation`, `SystemFlag=Y`). VERIFIED. This skill creates a NEW style by copying the seeded `Standard_Negotiation` rows unchanged under a new code and name (`SystemFlag=N`). Use it to add a style; it never changes an existing style. There is no REST resource for styles (VERIFIED: `negotiationStyles`, `supplierNegotiationStyles`, `sourcingNegotiationStyles` give HTTP 404), so the second export is the read-back.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project".
         Check: `git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"` must print the OK line.
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
STY    = new style code: PREFIX + short name (upper case, digits, _), e.g. GAPFILL_AB_STY1
SNAME  = its display name, e.g. GAPFILL AB Style 1 (no "|")
SRC    = the style to copy: Standard_Negotiation (seeded)
```
Every `<FSCR>`, `<GAPS>`, `<RUN>`, `<...>` in the commands below is a placeholder: put the real value in its place before you run the command.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`, and never pass `$PWD`: FSCR's REST client then fails with `No module named 'rest_client_common'`). VERIFIED
- Shell variables do **not** survive from one tool call to the next: set them again in every call.
- **Never read the import log with cat, sed or grep** (it holds the environment name and the submitting user). Read it only with `python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. VERIFIED
- **Never print the export CSVs whole** (`CreatedBy` / `LastUpdatedBy` hold user names) and never print the metadata XML. Print only the columns shown below. Existing records may carry people's names: do not copy them into reports.
- FSCR's export and import file names start with the environment name; do not copy them into reports.
- Save each export's output to a file and print only whether a ZIP was written. If no ZIP was written, run the export again into a new folder (read-only; up to 3 times) and use **that** folder in every later command.
- Save the import's screen output to `<RUN>/import.out`; the ProcessId is on the line `Started setup task CSV import process: <n>`. `grep -o` on `import.out` is safe; never print `import.out` whole. Do not wrap the import in a shell `timeout`.
- No ProcessId line after an error: **do not import again.** Repeat the Step 4 read-back every minute for 10 minutes; if the record shows up, go on; if not, nothing was created (prove it with the after-export); a second import needs the person's approval again.
- Connection dropped **after** the ProcessId line: the import still runs; **never import again**. Fetch its log with `cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code PON_MANAGE_NEGOTIATION_STYLES --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"`, then read it with `read_import_log.py`.

## Sign-in
- If a call says HTTP 401/403, or hangs with no output (an expired token waits for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead.
- Never print tokens, the server address or user names.

## Prerequisites
None to create: the source style `Standard_Negotiation` is seeded and is in the export (Step 1 checks it).

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PON_MANAGE_NEGOTIATION_STYLES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "
import csv,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.csv')): print(os.path.basename(f), sum(1 for _ in csv.DictReader(open(f,encoding='utf-8-sig'))), 'rows')
" "<RUN>/export_before/unz"
```
Expect 5 files (VERIFIED): the metadata XML, `PON_NEGOTIATION_STYLES.csv`, `PON_NEGOTIATION_STYLES_TRANSLATION.csv`, `PON_DOCTYPE_STYLES.csv` (one row per style and document type), `PON_DOCTYPE_STYLES_TRANSLATION.csv`. Ours held 5 styles and 15 document-type rows. List the styles (safe columns only):
```bash
python -I -c "
import csv,sys
for r in csv.DictReader(open(sys.argv[1]+'/PON_NEGOTIATION_STYLES.csv',encoding='utf-8-sig')): print(r['StyleCode'],'|',r['Status'],'| system',r['SystemFlag'])
" "<RUN>/export_before/unz"
```
`Standard_Negotiation` must be listed and STY must not be. VERIFIED

## Step 2. Build the package (copy of the seeded style under the new code)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/sourcing/scripts/clone_rows.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key-col StyleCode --key-col PON_NEGOTIATION_STYLES.StyleCode --source Standard_Negotiation --new <STY> \
  --set "PON_NEGOTIATION_STYLES.csv|StyleName=<SNAME>|Description=<text>|SystemFlag=N|Status=ACTIVE" \
  --set "PON_NEGOTIATION_STYLES_TRANSLATION.csv|StyleName=<SNAME>|Description=<text>"
```
- `clone_rows.py` takes every row of `Standard_Negotiation` in the 4 files, puts STY in the style code columns, empties the audit columns and applies the `--set` changes. It stops if STY is already in the export or the source is missing. VERIFIED
- Expect `PON_DOCTYPE_STYLES.csv: 3 row(s)`, `PON_DOCTYPE_STYLES_TRANSLATION.csv: 3 row(s)`, `PON_NEGOTIATION_STYLES.csv: 1 row(s)`, `PON_NEGOTIATION_STYLES_TRANSLATION.csv: 1 row(s)`. VERIFIED
- `SystemFlag=N` marks it as your own style (a seeded copy would keep `Y`). VERIFIED (read back as N)

## Step 3. Import
Approval: the person must approve the environment, the task and the new record's name before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code PON_MANAGE_NEGOTIATION_STYLES --task-name "Manage Negotiation Styles" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Keep the ProcessId. Success (VERIFIED): `Supplier Negotiation Styles : Enabled Document Type ... Completed successfully`, `Supplier Negotiation Style ... Completed successfully`, `Total Objects Failed: 0`, `IMPORT: PASS`. The log counts only 1 row for the document types; the export in Step 4 shows all 3.

## Step 4. Read back (second export)
Run this step also when the import failed.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PON_MANAGE_NEGOTIATION_STYLES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key PON_NEGOTIATION_STYLES.csv=StyleCode --key PON_NEGOTIATION_STYLES_TRANSLATION.csv=PON_NEGOTIATION_STYLES.StyleCode \
  --key PON_DOCTYPE_STYLES.csv=PON_NEGOTIATION_STYLES.StyleCode --key PON_DOCTYPE_STYLES_TRANSLATION.csv=PON_NEGOTIATION_STYLES.StyleCode \
  --expect PON_NEGOTIATION_STYLES.csv=<STY>
python -I -c "
import csv,sys
for r in csv.DictReader(open(sys.argv[1]+'/PON_NEGOTIATION_STYLES.csv',encoding='utf-8-sig')):
    if r['StyleCode']==sys.argv[2]: print('STYLE',r['StyleCode'],'|',r['StyleName'],'|',r['Status'],'| system',r['SystemFlag'])
for r in csv.DictReader(open(sys.argv[1]+'/PON_DOCTYPE_STYLES.csv',encoding='utf-8-sig')):
    if r['PON_NEGOTIATION_STYLES.StyleCode']==sys.argv[2]: print('  DOCTYPE',r['InternalName'],'enabled',r['EnabledFlag'])
" "<RUN>/export_after/unz" <STY>
```
`RESULT: PASS` = nothing removed or changed and STY added (the compare keys by style, so the document-type file shows "added 1" while its row count grows by 3). Then the style must print with your name, `ACTIVE`, `system N`, and 3 document types (BUYER_AUCTION, REQUEST_FOR_QUOTE, REQUEST_FOR_INFORMATION) enabled as in the source. VERIFIED

## Rules and limits
1. New styles only; never send an existing style code (it would update it).
2. The new style is ACTIVE: buyers can pick it when they create a negotiation. Test styles stay (no delete by CSV).
3. To change features of the new style, add more `--set` columns (for example `TeamScoringEnabledFlag=N`): GUESS, not tested.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-27). Do not reuse these names.
Counts are from our run; later runs see more rows (every test adds records). That is expected.
| Step | Result |
|---|---|
| Export before | 5 files; 5 styles, 15 document-type rows |
| Package | copy of `Standard_Negotiation` as `GAPFILL_AB_S2_STY1` "GAPFILL AB Style 1": 1 + 1 + 3 + 3 rows |
| Import | ProcessId 100004743464567: 2 objects, 0 failed |
| Export after | 6 styles, 18 document-type rows; added only the new style, 0 removed, 0 changed: PASS; ACTIVE, system N, 3 document types enabled |
