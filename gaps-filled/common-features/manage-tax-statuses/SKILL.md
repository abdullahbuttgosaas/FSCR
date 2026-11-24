---
skill_id: "gosaas.gap-fills.common-features.manage-tax-statuses"
name: "Manage Tax Statuses (GoSaaS gap fill)"
description: "Create a new tax status under an existing tax owned by the global configuration owner, through FSCR's setup-task CSV export and import (ZX_TAX_STATUS), copying the settings of an existing status, then read it back with a second export. Checks first that the tax's regime has the global configuration owner option (prerequisite, made with manage-tax-regimes Step 7). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 1 (failed 3 times, 2026-11-23); cause found and fixed in batch taxfix, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_STATUSES"
task_name: "Manage Tax Statuses"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
  - "gosaas common-features/manage-tax-regimes/scripts/template_row.py"
  - "ZX_MANAGE_TAXES (the tax must exist)"
  - "ZX_MANAGE_TAX_REGIMES Step 7 (the tax's regime must have the global configuration owner option row)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new tax status. It may not be deletable; plan as if it stays."
---

# Manage Tax Statuses (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax status (for example STANDARD, EXEMPT, ZERO) sits under one tax. Tax rates hang below a status. One status per tax can be the default. A status does nothing on a transaction while its tax is not live for processing.

## When to use
- Someone asks to create a **new** tax status for task `ZX_MANAGE_TAX_STATUSES` under a tax that already exists.
- Not for changing existing statuses. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix for the new status, e.g. GAPFILL_<INITIALS>_
REGIME  = TaxRegimeCode of the tax (the person names it)
TAX     = Tax code of the existing tax (the person names it)
CODE    = new TaxStatusCode: upper case letters, digits and _, starting with PREFIX, max 30
NAME    = new TaxStatusName, e.g. "GAPFILL XX status 1" (no "|" character)
FROM    = EffectiveFrom of the status, yyyy/mm/dd: the tax's EffectiveFrom or later
TEMPLATE= TaxStatusCode of one existing status to copy settings from (Step 4)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials.
- **Exports are read-only.** If one drops (`The read operation timed out`, `Remote end closed connection`, no ZIP written), run it again into a new folder, one export at a time, up to 3 tries; then stop.

Export command used in Steps 2, 3 and 6 (`<TASK_CODE>` and `<OUT>` change):
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code <TASK_CODE> --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<OUT>"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<OUT>"
```

## Step 2. Prerequisite check (taxes export, read-only)
Export `ZX_MANAGE_TAXES` to `<RUN>/export_tax` (about 60 to 95 s). Then:
```bash
python -I -c "import csv,sys; [print('TAX',r['Tax'],'| regime',r['TaxRegimeCode'],'| owner',r['ContentOwnerPartyTypeCode'],r['BuName'] or '-','| live',r['LiveForProcessingFlag'],'| from',r['EffectiveFrom']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX.csv',encoding='utf-8-sig')) if r['Tax']==sys.argv[2] and r['TaxRegimeCode']==sys.argv[3]]" "<RUN>/export_tax/unz" "<TAX>" "<REGIME>"
python -I -c "import csv,sys; print('GCO option row for regime:', any(r['TaxRegimeCode']==sys.argv[2] for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_BU_GCO_TAX_SUB.csv',encoding='utf-8-sig'))))" "<RUN>/export_tax/unz" "<REGIME>"
```
- The first line must print exactly one `TAX` line with `owner GCO -`. No line: the tax does not exist; **stop** (create it with the gap skill `manage-taxes`). Owner `OU`/legal entity: **stop** (not tested).
- The second line must print `True`. If `False`: the regime lacks the **global configuration owner option row**, and Oracle will refuse the status with `ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute` (VERIFIED 3 times before the row existed; then the same status imported fine). Do **`manage-tax-regimes` Step 7** for REGIME first (only if REGIME is your own test regime or the person approves it), then repeat this step. Do not import the status without it.
- FROM must be on or after the tax's `from` date.

## Step 3. Read-only statuses export
Export `ZX_MANAGE_TAX_STATUSES` to `<RUN>/export_before` (about 80 to 230 s). Expect 32 or 33 files (the rate files vary a little): `ZX_TAX_STATUS.csv` (44 columns: `TaxStatusCode, Tax, TaxRegimeCode, PartyNumber, ContentOwnerPartyTypeCode, EffectiveFrom, EffectiveTo, ..., DefaultStatusFlag, DefaultFlgEffectiveFrom, ..., TaxStatusName, ..., BuName, EnterpriseId, RegimeTypeFlag`), `ZX_TAX_STATUS_TRANSLATION.csv`, the rate files, `ASM_SETUP_CSV_METADATA.xml`. There is no tax file in this package: the status refers to its tax by code.
```bash
python -I -c "import csv,sys; [print(r['TaxStatusCode'],'|',r['Tax'],'|',r['TaxRegimeCode'],'| owner',r['ContentOwnerPartyTypeCode'],r['BuName'] or '-','| default',r['DefaultStatusFlag']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_STATUS.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
- **CODE is free:** it must not be listed for TAX and REGIME (the builder checks it again). No REST resource exists for statuses (`taxStatusesLOV`: HTTP 404).
- **DEFAULT:** if TAX has **no** status in the list, the new status is the default (`Y`, VERIFIED). If TAX already has a default status, use `N` (GUESS).

## Step 4. Build a package with only the new status
**TEMPLATE** = the first listed status with `owner GCO -`; `<template's Tax>` is the second column of that line (status codes repeat across taxes, so both are matched). If there is none, the first listed status (then also add `--set "ContentOwnerPartyTypeCode=GCO" --clear BuName --clear EnterpriseId` to the first command; GUESS).
```bash
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_STATUS.csv \
  --match "TaxStatusCode=<TEMPLATE>" --match "Tax=<template's Tax>" \
  --set "TaxStatusCode=<CODE>" --set "Tax=<TAX>" --set "TaxRegimeCode=<REGIME>" --set "TaxStatusName=<NAME>" \
  --set "EffectiveFrom=<FROM>" --set "DefaultStatusFlag=<DEFAULT>" --set "DefaultFlgEffectiveFrom=<FROM>" \
  --clear EffectiveTo --clear DefaultFlgEffectiveTo --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_STATUS_TRANSLATION.csv \
  --match "ZX_TAX_STATUS.TaxStatusCode=<TEMPLATE>" --match "ZX_TAX_STATUS.Tax=<template's Tax>" --match "Language=US" \
  --set "ZX_TAX_STATUS.TaxStatusCode=<CODE>" --set "ZX_TAX_STATUS.Tax=<TAX>" --set "ZX_TAX_STATUS.TaxRegimeCode=<REGIME>" \
  --set "TaxStatusName=<NAME>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name status_new.zip --prefix <PREFIX> \
  --key "ZX_TAX_STATUS.csv=TaxStatusCode,Tax,TaxRegimeCode" \
  --key "ZX_TAX_STATUS_TRANSLATION.csv=ZX_TAX_STATUS.TaxStatusCode,ZX_TAX_STATUS.Tax,ZX_TAX_STATUS.TaxRegimeCode,Language" \
  --prefix-col "ZX_TAX_STATUS.csv=TaxStatusCode" --max-len "TaxStatusCode=30" @"<RUN>/rows.txt"
```
- With `DEFAULT=N`, add `--clear DefaultFlgEffectiveFrom` and drop the `DefaultFlgEffectiveFrom` set (GUESS).
- The builder must print `ZX_TAX_STATUS.csv: 1 new rows`, `ZX_TAX_STATUS_TRANSLATION.csv: 1 new rows`, every other file `0 new rows`.
- If the translation file has no `Language=US` row for the TEMPLATE, use the language your environment has.

## Step 5. Import
**Approval.** The person must approve the environment, the task, TAX and the exact CODE. If their brief names all of them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_STATUSES --task-name "Manage Tax Statuses" \
  --zip-file "<RUN>/payload/status_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`); it is the only key to the full process log later. The script also prints `StatusCode: (unknown)`; that is normal.
- About 60 to 80 s. Short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Row Identifier[^\n]*|Message Text: [^\n]+|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TaxStatus. Status: Completed successfully ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0` (the totals line also shows about 16 objects processed and succeeded: the rate objects with 0 rows; normal). It can take up to about 90 s. **`0 rows were processed` is a failure.**
- `ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute` = the prerequisite of Step 2 is missing (or TAX/REGIME is wrong). Do not retry blindly.
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 6.
- Other row errors: change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second statuses export and compare
Export `ZX_MANAGE_TAX_STATUSES` to `<RUN>/export_after`, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX_STATUS.csv=TaxStatusCode,Tax,TaxRegimeCode" \
  --key "ZX_TAX_STATUS_TRANSLATION.csv=ZX_TAX_STATUS.TaxStatusCode,ZX_TAX_STATUS.Tax,ZX_TAX_STATUS.TaxRegimeCode,Language" \
  --expect "ZX_TAX_STATUS.csv=<CODE>,<TAX>,<REGIME>" --expect "ZX_TAX_STATUS_TRANSLATION.csv=<CODE>,<TAX>,<REGIME>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your status and its translation were added; nothing removed or changed. If someone else changed statuses between the two exports, judge your own rows and report the extras.

## Rules and limits
1. New records only; never import a full export. Never change a real tax.
2. Never make a tax live, never add a business-unit or legal-entity subscription for this task. The GCO option row of the prerequisite is the only setup change outside the status, and only on a test regime or with the person's approval.
3. Test records may stay for good. This skill never deletes. Record every created status.
4. Tested only for statuses of taxes owned by the global configuration owner, on a tax that is not live. Not tested: business-unit owned taxes, a second default status.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts; `-I` for the helpers and one-liners.

## Why the first 3 tries failed (2026-11-23, VERIFIED cause found 2026-11-24)
Batch 3 tried a status on a not-live tax, on a simulation tax, and after a business-unit subscription of the regime: all refused with `ZX_INVALID_VALUE ... Tax attribute`. Field-by-field compare with the one working GCO-owned status in the environment: the tax rows differ only in option flags; the difference is the regime's row in `ORA_ZX_BU_GCO_TAX_SUB.csv` (present for every regime with tax content, missing for the test regime). After adding that row (manage-tax-regimes Step 7), the same kind of status imported on the first try.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Prerequisite | test regime got its GCO option row (ProcessId 100004742409055), read back PASS |
| Template | the one GCO-owned status in the environment |
| New record | `GAPFILL_AB_TF_ST1` on test tax `GAPFILL_AB_P1_TX1` (not live), from 2026/01/01, default Y |
| Import | 1 attempt, 61 s, ProcessId 100004741413261: TaxStatus 1 row, 0 failed |
| Export after + compare | 4 to 5 statuses; added 1 + 1, removed 0, changed 0: PASS |
