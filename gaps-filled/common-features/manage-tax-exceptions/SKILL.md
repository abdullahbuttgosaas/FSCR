---
skill_id: "gosaas.gap-fills.common-features.manage-tax-exceptions"
name: "Manage Tax Exceptions (GoSaaS gap fill)"
description: "Create one new tax exception (a discount or special rate for one product fiscal classification code on one tax rate) through FSCR's setup-task CSV export and FSM CSV import, row written in full (the export is often empty), then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 3, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_EXCEPTIONS"
task_name: "Manage Tax Exceptions"
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
  - "gosaas ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES (manage-tax-rates): a test tax rate on a NOT live test tax (its regime has the GCO row of manage-tax-regimes Step 7)"
  - "gosaas ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS (manage-product-fiscal-classifications): a test product category code"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one tax exception. On a tax that is not live it changes no transaction. It may not be deletable; plan as if it stays."
---

# Manage Tax Exceptions (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill that builds this row. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax exception changes the tax rate for one product (an item, or a product fiscal classification code): a discount or surcharge (`RateModifier` percent) or a special rate. File `ZX_TAX_EXCEPTION.csv` (one file, no children). This skill creates **one exception for one product fiscal classification code on one test tax rate**, the row written in full with codes only (no ids).
- **Test rule:** use **your own test rate on a tax that is not live** and **your own test product category code**. An exception on a live tax changes tax on real transactions: that needs the person's explicit approval and is not covered here.

## When to use
- Someone asks to create a **new** tax exception for task `ZX_MANAGE_TAX_EXCEPTIONS`.
- Do **not** use it to change or end-date existing exceptions. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
REF     = new ExceptionReferenceNumber, upper case, starting with PREFIX (it is the only text that marks the row as yours)
REGIME, TAX, STATUS, RATE = codes of your test tax rate (Step 1)
PCODE   = your test product category code (type PRODUCT_CATEGORY) (Step 1)
FROM    = start date yyyy/mm/dd, on or after the rate's start date
```

## Step 0 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR puts the environment name in its output file names: never copy those names into evidence.
- If an export reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials.

## Step 1. Prerequisites (read-only checks)
1. **Test rate.** Export `ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES` read-only (as in Step 2, other task code, folder `<RUN>/rates`, about 2 min) and list your rates:
   `python -I -c "import csv,sys; [print(r['TaxRegimeCode'],r['Tax'],r['TaxStatusCode'],r['TaxRateCode'],r['EffectiveFrom'],r['PercentageRate']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TAX_RATE_PERCENT_TYPE.csv',encoding='utf-8-sig')) if r['TaxRateCode'].startswith(sys.argv[2])]" "<RUN>/rates/unz" <PREFIX>`
   Pick one row: REGIME, TAX, STATUS, RATE. If you have none, create one first with the `manage-tax-rates` skill (its tax must be **not live**). VERIFIED
2. **Test product category code.** Export `ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS` read-only and list codes starting with PREFIX in `ORA_ZX_PRODUCT_CLASS_CODE.csv` (type `PRODUCT_CATEGORY`). If you have none, create one with the `manage-product-fiscal-classifications` skill. VERIFIED
3. **Lookups** (seeded; checked live in our test): `ExceptionClassCode` from `ZX_EXCEPTION_CLASS` (`PRODUCTFC` = product fiscal classification, `ITEM` = item), `ExceptionTypeCode` from `ZX_EXCEPTION_TYPE` (`DISCOUNT` = discount or surcharge, `SPECIAL_RATE`), `ExceptionReasonCode` from `ZX_EXCEPTION_REASON` (for example `OTHER`). To check one: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource "standardLookups/ZX_EXCEPTION_TYPE/child/lookupCodes" --fields LookupCode,Meaning --out "<RUN>/lk.json"`.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_EXCEPTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.log" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 2 files (VERIFIED, about 40 s): `ZX_TAX_EXCEPTION.csv` (may have 0 rows) and the metadata XML. REF must not be in the file's `ExceptionReferenceNumber` column (the builder checks).

## Step 3. Build a package with only the new exception
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name exc_new.zip \
  --prefix <PREFIX> --key "ZX_TAX_EXCEPTION.csv=ExceptionReferenceNumber" --prefix-col "ZX_TAX_EXCEPTION.csv=ExceptionReferenceNumber" \
  --row "ZX_TAX_EXCEPTION.csv|ExceptionClassCode=PRODUCTFC|ClassificationTypeCode=PRODUCT_CATEGORY|ClassificationCode=<PCODE>|TaxRegimeCode=<REGIME>|Tax=<TAX>|TaxStatusCode=<STATUS>|TaxRateCode=<RATE>|ExceptionTypeCode=DISCOUNT|RateModifier=10|ExceptionReasonCode=OTHER|EffectiveFrom=<FROM>|ContentOwnerPartyTypeCode=GCO|RecordTypeCode=USER_DEFINED|ExceptionReferenceNumber=<REF>"
```
- `ContentOwnerPartyTypeCode=GCO`: the global configuration owner, the same owner as the test rate (VERIFIED). If your rate has another owner, copy the rate's owner columns (GUESS).
- `RateModifier=10` with `DISCOUNT` = 10 % discount (VERIFIED accepted). The builder must print `1 new rows`.

## Step 4. Import
**Approval.** The person must approve the environment, the task, REF and the rate and code used before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_EXCEPTIONS --task-name "Manage Tax Exceptions" \
  --zip-file "<RUN>/payload/exc_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.log"
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: [^.]+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_]+|JBO-[0-9]+: [^.]{0,160}|ZX_[A-Z_]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
```
- **Write down the `ProcessId`** (the grep line). Success (VERIFIED, about 25 s): `Detail Object: TaxException. Status: Completed successfully ... 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`.
- **If the script loses the connection after the process started**, do not import again; wait 2 minutes and do Step 5.
- Rows failed: read the message, change one thing, retry at most 3 times.

## Step 5. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX_EXCEPTION.csv=ExceptionReferenceNumber" --expect "ZX_TAX_EXCEPTION.csv=<REF>" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your exception was added. Oracle adds `RegimeTypeFlag=I` (VERIFIED). Do not print whole rows: they hold user names in the audit columns.

## Rules and limits
1. New records only; never import a full export. Never on a live tax without explicit approval.
2. Test records may stay for good. This skill never deletes. Record every created REF.
3. Not tested: item exceptions (`ITEM`, needs an item and an organization), `SPECIAL_RATE`, jurisdiction-level exceptions, other content owners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this reference.
| Step | Result |
|---|---|
| Prerequisites | rate `GAPFILL_AB_TF_RT1` (5 %) on status `GAPFILL_AB_TF_ST1`, tax `GAPFILL_AB_P1_TX1` (not live), regime `GAPFILL_AB_TR1`; product category code `GAPFILL_AB_P2_PCC1` |
| Export before | 2 files, 0 exceptions; about 40 s |
| Import | 1 attempt (ProcessId 100004741425074): TaxException 1 row, 0 failed |
| Export after + compare | `GAPFILL_AB_P3_EXC1`: 0 -> 1, removed 0, changed 0: PASS |
