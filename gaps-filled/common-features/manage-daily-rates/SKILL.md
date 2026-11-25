---
skill_id: "gosaas.gap-fills.common-features.manage-daily-rates"
name: "Manage Daily Rates: rate type with cross-rate rules (GoSaaS gap fill)"
description: "Load the CSV part of the Manage Daily Rates task: a new conversion rate type with cross rates (pivot currency) and its cross-rate rule rows (contra currencies), through FSCR's setup-task CSV export and FSM CSV import (GL_DAILY_CONVERSION_TYPE + ORA_GL_CONVERSION_RATE_RULE), then read it back with a second export. The daily rate VALUES are not in this CSV package (Oracle marks them as an external data load). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 06, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_DAILY_RATES"
task_name: "Manage Daily Rates"
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
  - "gosaas common-features/manage-conversion-rate-types (plain rate types without cross rates)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new conversion rate type with cross-rate rules. The new type shows in every rate type list; no ledger or rate uses it. It may not be deletable; plan as if it stays."
---

# Manage Daily Rates: rate type with cross-rate rules (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
"Manage Daily Rates" holds the exchange rates per rate type, currency pair and date. Its **setup-task CSV package** carries only the setup around the rates (VERIFIED):
- `GL_DAILY_CONVERSION_TYPE.csv`: the conversion rate types, with the **cross-rate** options (`EnableCrossRateFlag`, `PivotCurrencyCode`, `UserOverrideCrossRateFlag`, `EnforceInverseRateFlag`);
- `ORA_GL_CONVERSION_RATE_RULE.csv`: the **cross-rate rule** rows of a type: the contra currencies for which Oracle computes cross rates through the pivot currency.

The **rate values** are not in it. The import log itself says so: `Business object: Conversion Rate. Status: Data Load Pending. You must load the data for this business object` (VERIFIED). Rates are loaded another way: the daily rates spreadsheet or file-based data import (GUESS, not tested here).

Use this skill when someone asks to create a **new rate type with cross-rate rules** through the Manage Daily Rates task. For a plain rate type (no cross rates) the batch 1 skill `manage-conversion-rate-types` is enough. Do **not** use this skill to change an existing type or its rules (that is an update of a shared record), or to load rate values.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
TYPE    = new rate type name (UserConversionType), starting with PREFIX, at most 30 characters (GUESS)
PIVOT   = the pivot currency code, e.g. USD
CONTRA  = one or more contra currency codes, e.g. EUR and GBP (enabled currencies, different from PIVOT)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
None outside this import: the new type and its rules go in **one** package (the rules are child rows of the type, so the type row must be in the same ZIP). PIVOT and CONTRA must be enabled currencies (GUESS: any currency already used by another rate type in the export is enabled).

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code GL_MANAGE_DAILY_RATES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED, about 30 s): `GL_DAILY_CONVERSION_TYPE.csv` (32 columns, all rate types, seeded ones too), `ORA_GL_CONVERSION_RATE_RULE.csv` (9 columns: `GL_DAILY_CONVERSION_TYPE.UserConversionType`, `FromCurrency`, `ToCurrency`, `EnabledFlag` + audit) and `ASM_SETUP_CSV_METADATA.xml`. Success = exit 0 and a ZIP in the folder. TYPE must not be in the type file (the builder checks). If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries; then stop.
- Look at a working cross-rate type first: `python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_before/unz" --value "<a type with EnableCrossRateFlag=Y>"`. In every working rule row `FromCurrency` = `ToCurrency` = the contra currency and `EnabledFlag` = `N` (VERIFIED, 10 rows on 5 types).

## Step 3. Build a package with only the new type and its rules
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name rate_type_new.zip --prefix <PREFIX> \
  --key "GL_DAILY_CONVERSION_TYPE.csv=UserConversionType" \
  --key "ORA_GL_CONVERSION_RATE_RULE.csv=GL_DAILY_CONVERSION_TYPE.UserConversionType,FromCurrency,ToCurrency" \
  --prefix-col "GL_DAILY_CONVERSION_TYPE.csv=UserConversionType" --max-len "UserConversionType=30" \
  --row "GL_DAILY_CONVERSION_TYPE.csv|UserConversionType=<TYPE>|Description=<short text>|SecurityFlag=N|PivotCurrencyCode=<PIVOT>|EnforceInverseRateFlag=Y|UserOverrideCrossRateFlag=N|EnableCrossRateFlag=Y" \
  --row "ORA_GL_CONVERSION_RATE_RULE.csv|GL_DAILY_CONVERSION_TYPE.UserConversionType=<TYPE>|FromCurrency=<CONTRA 1>|ToCurrency=<CONTRA 1>|EnabledFlag=N" \
  --row "ORA_GL_CONVERSION_RATE_RULE.csv|GL_DAILY_CONVERSION_TYPE.UserConversionType=<TYPE>|FromCurrency=<CONTRA 2>|ToCurrency=<CONTRA 2>|EnabledFlag=N"
```
- **Rule rows need `EnabledFlag=N`** (VERIFIED). With `EnabledFlag=Y` the import says "Completed successfully" and creates the type, but **drops the rule rows without any error** (try 1, below). `N` is the value of every working rule row. (GUESS: the flag does not switch the cross rate off; the rule is active as long as the type has `EnableCrossRateFlag=Y`.)
- `FromCurrency` and `ToCurrency` both = the contra currency (VERIFIED: the shape of all working rows).
- Leave the `Fem*` columns, `Attribute*` and the audit columns empty. VERIFIED
- Builder must print `GL_DAILY_CONVERSION_TYPE.csv: 1 new rows` and `ORA_GL_CONVERSION_RATE_RULE.csv: <n> new rows`.

## Step 4. Import
**Approval.** The person must approve the environment, the task, TYPE, PIVOT and CONTRA before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code GL_MANAGE_DAILY_RATES --task-name "Manage Daily Rates" \
  --zip-file "<RUN>/payload/rate_type_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later.
- About 30 s. Short summary (counts and messages only, no user names):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED): `A total of 1 rows were processed. 0 rows of them failed` (only the type is counted), `Conversion Rate Rule ... Completed successfully`, `Conversion Rate ... Data Load Pending` (normal: rate values are not in the package), `Total Objects Failed: 0`. **The log does not count the rule rows: Step 5 is the only proof that they came in.**
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 5.
- Rows failed: copy the message, change one thing, retry at most 3 times with a new TYPE name. A generic database error at the insert (for example `JBO-26041`): fill `CreatedBy` and `LastUpdatedBy` with the export metadata's `SubmittedBy` (read it at run time, never print it). GUESS (not needed here).

## Step 5. Read back: second export and compare (the proof)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "GL_DAILY_CONVERSION_TYPE.csv=UserConversionType" \
  --key "ORA_GL_CONVERSION_RATE_RULE.csv=GL_DAILY_CONVERSION_TYPE.UserConversionType,FromCurrency,ToCurrency" \
  --expect "GL_DAILY_CONVERSION_TYPE.csv=<TYPE>" \
  --expect "ORA_GL_CONVERSION_RATE_RULE.csv=<TYPE>,<CONTRA 1>,<CONTRA 1>" --expect "ORA_GL_CONVERSION_RATE_RULE.csv=<TYPE>,<CONTRA 2>,<CONTRA 2>"
```
`RESULT: PASS` = only your type and its rule rows were added, nothing removed or changed (VERIFIED). A `PROBLEM` on the rule file with the type added = the rule rows were dropped (see Step 3).
- No REST check: the read-only REST resources we tried for rate types and rates did not answer to a name filter (VERIFIED: `conversionRateTypesLOV` 404; `currencyRates` with `q=UserConversionType=...` 400). The export compare is the proof.

## Rules and limits
1. New records only; never import a full export (it would update every rate type, seeded ones too).
2. Never add rules to an existing type: the type row would have to change too (pivot, cross-rate flag), which is an update of a shared record.
3. Test records may stay for good. This skill never deletes. Record every created type.
4. Not tested: loading rate values (spreadsheet or file-based import), `UserOverrideCrossRateFlag=Y`, `SecurityFlag=Y`, FEM columns.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py`, `view_record.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 16 types, 10 rule rows; about 30 s |
| Try 1 | `GAPFILL_AB_B6_DRT1` (pivot USD, cross rates on) + rules EUR, GBP with `EnabledFlag=Y` (ProcessId 100004743401986): type created, **rules not created**, no error; compare: types added 1, rules added 0 |
| Diagnosis | every working rule row has `EnabledFlag=N`; changed only that |
| Try 2 | `GAPFILL_AB_B6_DRT2` + rules EUR, GBP with `EnabledFlag=N` (ProcessId 100004742421461), about 30 s |
| Export after + compare | types added 1, rules added 2, removed 0, changed 0: PASS |
