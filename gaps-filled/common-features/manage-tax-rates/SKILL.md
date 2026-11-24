---
skill_id: "gosaas.gap-fills.common-features.manage-tax-rates"
name: "Manage Tax Rates and Tax Recovery Rates (GoSaaS gap fill)"
description: "Create a new percentage tax rate under an existing tax status (tax owned by the global configuration owner) through FSCR's setup-task CSV export and import (ORA_ZX_TAX_RATE_PERCENT_TYPE), copying the settings of an existing rate and re-sending the parent status unchanged, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 2 (blocked, 2026-11-24); unblocked and tested in batch taxfix, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES"
task_name: "Manage Tax Rates and Tax Recovery Rates"
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
  - "gosaas common-features/manage-profile-options/scripts/copy_parent_rows.py"
  - "ZX_MANAGE_TAX_STATUSES (the status must exist; it needs the regime's global configuration owner option row, see manage-tax-regimes Step 7)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new tax rate (and re-sends its parent status row unchanged). It may not be deletable; plan as if it stays."
---

# Manage Tax Rates and Tax Recovery Rates (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax rate (for example 5 %) belongs to one **tax status** of one tax. It can be limited to a tax jurisdiction, can be the default rate of its status, and has accounts. This skill creates a **percentage** rate with no jurisdiction, not default, and no account row. Recovery, quantity, gross amount, schedule and withheld rates are other files of the same package (not tested).

## When to use
- Someone asks to create a **new** tax rate for task `ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES` under a status that already exists.
- Not for changing existing rates. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
P       = <GAPS>/common-features/manage-profile-options/scripts      (copy_parent_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix for the new rate, e.g. GAPFILL_<INITIALS>_
SPREFIX = the test prefix that STATUS starts with (may differ from PREFIX). If STATUS has no test prefix (a real status): stop and ask.
REGIME, TAX, STATUS = the existing regime, tax and TaxStatusCode the rate belongs to (the person names them)
CODE    = new TaxRateCode: upper case letters, digits and _, starting with PREFIX, max 30
NAME    = new TaxRateName, e.g. "GAPFILL XX rate 1" (no "|" character)
PCT     = the percentage, e.g. 5
FROM    = EffectiveFrom, yyyy/mm/dd: on or after the status's EffectiveFrom
TEMPLATE= TaxRateCode + EffectiveFrom of one existing rate to copy settings from (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 32 files (VERIFIED, 80 to 110 s): the parent statuses `ZX_TAX_STATUS.csv` + `ZX_TAX_STATUS_TRANSLATION.csv`, the percentage rate files `ORA_ZX_TAX_RATE_PERCENT_TYPE.csv` (+ `_TRANSLATION`, `ORA_ZX_TAX_RATE_PERCENT_DEF_ACCOUNT.csv`), the other rate types, and `ASM_SETUP_CSV_METADATA.xml`.
- **Exports are read-only.** If one drops (no ZIP written), run it again into a new folder, one at a time, up to 3 tries; then stop.

## Step 3. Check the parent status, choose a template, check the code
```bash
python -I -c "import csv,sys; [print('STATUS',r['TaxStatusCode'],'|',r['Tax'],'|',r['TaxRegimeCode'],'| owner',r['ContentOwnerPartyTypeCode'],'| from',r['EffectiveFrom']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_STATUS.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
python -I -c "import csv,sys; [print('RATE',r['TaxRateCode'],'| from',r['EffectiveFrom'],'|',r['Tax'],'|',r['TaxStatusCode'],'| owner',r['ContentOwnerPartyTypeCode'],'| jur',r['TaxJurisdictionCode'] or '-','| default',r['DefaultRateFlag']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TAX_RATE_PERCENT_TYPE.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
1. **STATUS must be listed** for TAX and REGIME with owner `GCO`. If not: **stop**; create it first with the gap skill `manage-tax-statuses` (which also checks the regime's global configuration owner option, the prerequisite of the whole chain).
2. **TEMPLATE** = the first listed `RATE` with owner `GCO` and `jur -`. If none, the first rate with owner `GCO` (the jurisdiction is cleared below). If no rate is owned by `GCO`: **stop** (not tested).
3. **CODE is free:** not in the RATE list (the builder checks it again).

## Step 4. Build a package with only the new rate (+ its parent status rows, unchanged)
```bash
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_TAX_RATE_PERCENT_TYPE.csv \
  --match "TaxRateCode=<TEMPLATE code>" --match "EffectiveFrom=<TEMPLATE from>" \
  --set "TaxRateCode=<CODE>" --set "EffectiveFrom=<FROM>" --set "TaxRegimeCode=<REGIME>" --set "Tax=<TAX>" \
  --set "TaxStatusCode=<STATUS>" --set "PercentageRate=<PCT>" --set "DefaultRateFlag=N" --set "TaxRateName=<NAME>" \
  --clear DefaultFlgEffectiveFrom --clear EffectiveTo --clear TaxJurisdictionCode \
  --clear DefaultRecTypeCode --clear DefaultRecRateCode --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_TAX_RATE_PERCENT_TYPE_TRANSLATION.csv \
  --match "ORA_ZX_TAX_RATE_PERCENT_TYPE.TaxRateCode=<TEMPLATE code>" --match "ORA_ZX_TAX_RATE_PERCENT_TYPE.EffectiveFrom=<TEMPLATE from>" --match "Language=US" \
  --set "ORA_ZX_TAX_RATE_PERCENT_TYPE.TaxRateCode=<CODE>" --set "ORA_ZX_TAX_RATE_PERCENT_TYPE.EffectiveFrom=<FROM>" \
  --clear "ORA_ZX_TAX_RATE_PERCENT_TYPE.TaxJurisdictionCode" --set "TaxRateName=<NAME>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name rate_new.zip --prefix <PREFIX> \
  --key "ORA_ZX_TAX_RATE_PERCENT_TYPE.csv=TaxRateCode,EffectiveFrom" \
  --key "ORA_ZX_TAX_RATE_PERCENT_TYPE_TRANSLATION.csv=ORA_ZX_TAX_RATE_PERCENT_TYPE.TaxRateCode,ORA_ZX_TAX_RATE_PERCENT_TYPE.EffectiveFrom,Language" \
  --prefix-col "ORA_ZX_TAX_RATE_PERCENT_TYPE.csv=TaxRateCode" --max-len "TaxRateCode=30" @"<RUN>/rows.txt"
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name rate_new.zip --file ZX_TAX_STATUS.csv --where "TaxStatusCode=<STATUS>" --where "Tax=<TAX>" --where "TaxRegimeCode=<REGIME>" --prefix <SPREFIX>
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name rate_new.zip --file ZX_TAX_STATUS_TRANSLATION.csv --where "ZX_TAX_STATUS.TaxStatusCode=<STATUS>" --where "ZX_TAX_STATUS.Tax=<TAX>" --where "Language=US" --prefix <SPREFIX>
```
- The builder must print `ORA_ZX_TAX_RATE_PERCENT_TYPE.csv: 1 new rows`, `..._TRANSLATION.csv: 1 new rows`, every other file `0 new rows`; each copy must print `copied 1 parent row unchanged`.
- **The parent status rows are required in the ZIP** (hierarchical package; without them FSM processes 0 rows). `--prefix <SPREFIX>` makes the copy stop unless STATUS is your own test status.
- No account row is sent (`ORA_ZX_TAX_RATE_PERCENT_DEF_ACCOUNT.csv` stays header only): VERIFIED accepted for a GCO rate.

## Step 5. Import
**Approval.** The person must approve the environment, the task, STATUS and the exact CODE. If their brief names all of them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES --task-name "Manage Tax Rates and Tax Recovery Rates" \
  --zip-file "<RUN>/payload/rate_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`). `StatusCode: (unknown)` in the script output is normal.
- About 60 s. Short summary:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Row Identifier[^\n]*|Message Text: [^\n]+|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TaxRatePercentType1 ... 1 rows ... 0 failed`, `Detail Object: TaxStatus ... 1 rows ... 0 failed` (the parent, unchanged) and `Total Objects Failed: 0`. **`0 rows were processed` is a failure.**
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 6.
- Row errors: change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_ZX_TAX_RATE_PERCENT_TYPE.csv=TaxRateCode,EffectiveFrom" \
  --key "ORA_ZX_TAX_RATE_PERCENT_TYPE_TRANSLATION.csv=ORA_ZX_TAX_RATE_PERCENT_TYPE.TaxRateCode,ORA_ZX_TAX_RATE_PERCENT_TYPE.EffectiveFrom,Language" \
  --key "ZX_TAX_STATUS.csv=TaxStatusCode,Tax,TaxRegimeCode" \
  --expect "ORA_ZX_TAX_RATE_PERCENT_TYPE.csv=<CODE>,<FROM>" --expect "ORA_ZX_TAX_RATE_PERCENT_TYPE_TRANSLATION.csv=<CODE>,<FROM>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your rate and its translation were added; the status is unchanged. If someone else changed rates between the two exports, judge your own rows and report the extras.

## Rules and limits
1. New records only; never import a full export. Never change a real status or rate.
2. Keep all 32 files, metadata XML unchanged; only the rate, its translation and the unchanged parent status rows go in.
3. Test records may stay for good. This skill never deletes. Record every created rate.
4. Tested only: percentage rate, GCO-owned, no jurisdiction, not default, no account, tax not live. Not tested: other rate types, recovery rates, jurisdiction rates, default rates, accounts, business-unit owned rates.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts; `-I` for the helpers and one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 5 statuses (one is the new test status `GAPFILL_AB_TF_ST1`), 5 percentage rates; 80 s |
| Template | the GCO percentage rate with no jurisdiction |
| New record | `GAPFILL_AB_TF_RT1`, 5 %, from 2026/01/01, on status `GAPFILL_AB_TF_ST1` of test tax `GAPFILL_AB_P1_TX1` |
| Import | 1 attempt, 61 s, ProcessId 100004741411939: rate 1 row and parent status 1 row, 0 failed |
| Export after + compare | 5 to 6 rates; added 1 + 1, removed 0, changed 0; status unchanged: PASS |
