---
skill_id: "gosaas.gap-fills.common-features.manage-tax-reporting-types"
name: "Manage Tax Reporting Types (GoSaaS gap fill)"
description: "Create a new tax reporting type with one reporting code (text type, regime level, no usage, no association) through FSCR's setup-task CSV export and import, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 3, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_REPORTING_TYPES"
task_name: "Manage Tax Reporting Types"
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
  - "ZX_MANAGE_TAX_REGIMES (the reporting type belongs to an existing regime; for a test use a test regime made with gosaas common-features/manage-tax-regimes)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one reporting type and its codes under one regime. With no usage and no association nothing reports with it. It may not be deletable; plan as if it stays."
---

# Manage Tax Reporting Types (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file. It uses the generic helpers of the gap skill `manage-docseq-categories`.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A tax reporting type is an extra attribute for tax reports (for example a box number on a VAT return). It belongs to a tax regime (and optionally one tax), has a data type, and for a code list has **reporting codes**. **Usages** say which objects may carry it (tax, rate, party tax profile...), and **associations** attach a code to a real object. This skill creates the **type and its codes only**, under a regime you name. Usages and associations change what real tax objects carry, so they are not part of the test.

## When to use
- Someone asks to create a **new** tax reporting type (with codes) for task `ZX_MANAGE_TAX_REPORTING_TYPES`.
- Do **not** use it to change existing types, codes, usages or associations. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
REGIME  = TaxRegimeCode of an EXISTING regime the type belongs to. For a test: a regime whose code starts with PREFIX
          (create one with ../manage-tax-regimes/SKILL.md first if there is none). Never attach a test type to a real regime.
CODE    = new ReportingTypeCode: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME    = new ReportingTypeName, e.g. "GAPFILL XX test reporting type 1" (no "|" character)
VALUE   = one reporting code value (text), e.g. <PREFIX>C1; VNAME = its name. Repeat for more codes.
START   = EffectiveFrom of the type and its codes, yyyy/mm/dd, on or after the regime's EffectiveFrom
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder such as `E:\e\...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_REPORTING_TYPES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; [print(r['ReportingTypeCode'],'|',r['TaxRegimeCode'],'|',r['Tax'] or '-') for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_REPORTING_TYPE.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
Expect 14 files (VERIFIED, 1 to 3 minutes): `ORA_ZX_REPORTING_TYPE.csv` (26 columns: `ReportingTypeCode, TaxRegimeCode, Tax, ReportingTypeDatatypeCode, FormatMask, MinLength, MaxLength, LegalMessageFlag, EffectiveFrom, EffectiveTo, HasReportingCodesFlag, RecordTypeCode, ...audit..., ReportingTypeName, CountryCode, ...`), `ORA_ZX_REPORTING_TYPE_TRANSLATION.csv`, `ORA_ZX_TAX_REPORTING_CODE.csv`, `ORA_ZX_TAX_REPORTING_CODE_TRANSLATION.csv`, `ORA_ZX_TAX_REPORTING_TYPE_USAGE.csv`, 8 association/process files, and `ASM_SETUP_CSV_METADATA.xml`. The last command lists the existing types (it may list none).
- **Network drops are common on tax exports** (`The read operation timed out`, `Remote end closed connection without response`): no ZIP is written. An export is read-only, so run it again into a new folder, one export at a time. VERIFIED
- If it still has no ZIP after 3 tries or lacks these files: **stop**.
- The export does **not** list regimes. Check REGIME exists (want 1 row): `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource taxRegimesLOV --q "TaxRegimeCode='<REGIME>'" --fields TaxRegimeCode --out "<RUN>/regime.json" --expect-count 1`.
- CODE must not be in the list above (the builder also checks). No REST resource for reporting types was found (`taxReportingTypes`, `taxReportingTypesLOV`, `taxReportingTypeCodes`: HTTP 404); the export is the only check.

## Step 3. Build a package with only the new type and codes
Write the rows file (one `--row` line, then its value line; dates `yyyy/mm/dd`):
```bash
cat > "<RUN>/rows.txt" <<EOF
--row
ORA_ZX_REPORTING_TYPE.csv|ReportingTypeCode=<CODE>|TaxRegimeCode=<REGIME>|ReportingTypeDatatypeCode=TEXT|MinLength=1|MaxLength=30|LegalMessageFlag=N|EffectiveFrom=<START>|HasReportingCodesFlag=Y|RecordTypeCode=USER_DEFINED|ReportingTypeName=<NAME>
--row
ORA_ZX_REPORTING_TYPE_TRANSLATION.csv|ORA_ZX_REPORTING_TYPE.ReportingTypeCode=<CODE>|ORA_ZX_REPORTING_TYPE.TaxRegimeCode=<REGIME>|Language=US|SourceLang=US|ReportingTypeName=<NAME>
--row
ORA_ZX_TAX_REPORTING_CODE.csv|ORA_ZX_REPORTING_TYPE.ReportingTypeCode=<CODE>|ORA_ZX_REPORTING_TYPE.TaxRegimeCode=<REGIME>|ReportingCodeCharValue=<VALUE>|EffectiveFrom=<START>|RecordTypeCode=USER_DEFINED|ReportingCodeName=<VNAME>
--row
ORA_ZX_TAX_REPORTING_CODE_TRANSLATION.csv|ORA_ZX_REPORTING_TYPE.ReportingTypeCode=<CODE>|ORA_ZX_REPORTING_TYPE.TaxRegimeCode=<REGIME>|ORA_ZX_TAX_REPORTING_CODE.ReportingCodeCharValue=<VALUE>|ORA_ZX_TAX_REPORTING_CODE.EffectiveFrom=<START>|Language=US|SourceLang=US|ReportingCodeName=<VNAME>
EOF
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name reptype_new.zip --prefix <PREFIX> \
  --key "ORA_ZX_REPORTING_TYPE.csv=ReportingTypeCode,TaxRegimeCode" \
  --key "ORA_ZX_REPORTING_TYPE_TRANSLATION.csv=ORA_ZX_REPORTING_TYPE.ReportingTypeCode,ORA_ZX_REPORTING_TYPE.TaxRegimeCode,Language" \
  --key "ORA_ZX_TAX_REPORTING_CODE.csv=ORA_ZX_REPORTING_TYPE.ReportingTypeCode,ORA_ZX_REPORTING_TYPE.TaxRegimeCode,ReportingCodeCharValue" \
  --key "ORA_ZX_TAX_REPORTING_CODE_TRANSLATION.csv=ORA_ZX_REPORTING_TYPE.ReportingTypeCode,ORA_ZX_TAX_REPORTING_CODE.ReportingCodeCharValue,Language" \
  --prefix-col "ORA_ZX_REPORTING_TYPE.csv=ReportingTypeCode" --prefix-col "ORA_ZX_REPORTING_TYPE.csv=TaxRegimeCode" \
  --max-len "ReportingTypeCode=30" @"<RUN>/rows.txt"
```
- Replace every `<...>` placeholder with its value before running the `cat` command; no `<` or `>` may stay in `rows.txt`.
- For more codes, repeat the code row and its translation row with another VALUE.
- The builder must print `1 new rows` for the type, its translation and each code file, `0 new rows` for every other file. `--prefix-col ...TaxRegimeCode` makes it refuse a real (non-test) regime; drop that one option only if the person approved a real regime.
- Data type `TEXT` **needs `MinLength` 1 or more** (`ZX_MIN_LENGTH_VALUE: Enter a minimum length of 1 or greater for a text or numeric data type`), so keep `MinLength=1|MaxLength=30`. VERIFIED. Other data types are not tested.
- `Tax` stays empty (regime-level type) and is not in the keys: the builder rejects key columns that are empty. VERIFIED

## Step 4. Import
**Approval.** The person must approve the environment, the task, the REGIME and the exact CODE before the import. If their brief names them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_REPORTING_TYPES --task-name "Manage Tax Reporting Types" \
  --zip-file "<RUN>/payload/reptype_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
Print a short summary of the process log (detail objects that processed rows, error texts, totals):
```bash
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
```
- Success (VERIFIED, about 30 s): `Detail Object: TaxReportingType. Status: Completed successfully. ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0`. The codes and translations are loaded with the type and have no line of their own; Step 5 proves them.
- **`0 rows were processed` is a failure.** A row can validate and still fail at the database insert (`JBO-26041`, seen on another tax task): always read `Total Objects Failed`.
- If the script loses the connection after `Started setup task CSV import process: <id>`, the import still runs in Oracle. **Do not import again**; wait 2 minutes and do Step 5.
- Rows failed: copy the `Message Text`, change one thing, retry at most 3 times.

## Step 5. Read back (second export and compare)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_ZX_REPORTING_TYPE.csv=ReportingTypeCode,TaxRegimeCode" \
  --key "ORA_ZX_REPORTING_TYPE_TRANSLATION.csv=ORA_ZX_REPORTING_TYPE.ReportingTypeCode,ORA_ZX_REPORTING_TYPE.TaxRegimeCode,Language" \
  --key "ORA_ZX_TAX_REPORTING_CODE.csv=ORA_ZX_REPORTING_TYPE.ReportingTypeCode,ORA_ZX_REPORTING_TYPE.TaxRegimeCode,ReportingCodeCharValue" \
  --key "ORA_ZX_TAX_REPORTING_CODE_TRANSLATION.csv=ORA_ZX_REPORTING_TYPE.ReportingTypeCode,ORA_ZX_TAX_REPORTING_CODE.ReportingCodeCharValue,Language" \
  --expect "ORA_ZX_REPORTING_TYPE.csv=<CODE>,<REGIME>" --expect "ORA_ZX_REPORTING_TYPE_TRANSLATION.csv=<CODE>,<REGIME>,US" \
  --expect "ORA_ZX_TAX_REPORTING_CODE.csv=<CODE>,<REGIME>,<VALUE>" --expect "ORA_ZX_TAX_REPORTING_CODE_TRANSLATION.csv=<CODE>,<VALUE>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
Give one `--expect` per added row (one code row and one code translation per VALUE). `RESULT: PASS` = only your type, its translation and your codes were added, nothing removed or changed, no usage or association file changed. If someone else changed reporting types between your two exports, judge your own rows plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 14 files, metadata XML unchanged; usage and association files stay header-only.
3. **No usage or association in a test.** They make real taxes, rates or parties carry the type. Not tested; needs the person's explicit approval.
4. Test records may stay for good. This skill never deletes. Record every created type and code.
5. Not tested: tax-level types (`Tax` filled), data types other than `TEXT`, types without codes, end dates.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse these codes; they now exist.
| Step | Result |
|---|---|
| Export before | 0 reporting types; first two tries lost the network, third worked |
| Regime | test regime `GAPFILL_AB_TR1` (made with manage-tax-regimes) |
| New records | type `GAPFILL_AB_RT1` (TEXT, 1 to 30) with code `GAPFILL_AB_C1`, from 2026/01/01 |
| Import | attempt 1 failed (`ZX_MIN_LENGTH_VALUE`, MinLength was empty); attempt 2: 1 type processed, 0 failed, 11 objects succeeded |
| Export after + compare | type, translation, code, code translation each 0 -> 1; removed 0, changed 0; usage and association files unchanged: PASS |
