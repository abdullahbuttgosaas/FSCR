---
skill_id: "gosaas.gap-fills.common-features.manage-tax-condition-sets"
name: "Manage Tax Condition Sets (GoSaaS gap fill)"
description: "Create a new tax condition set (header, one condition, translation) on an existing tax determining factor set through FSCR's setup-task CSV export and import, then read it back with a second export. No tax rule uses it. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 2, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_CONDITION_SETS"
task_name: "Manage Tax Condition Sets"
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
  - "ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS (the factor set must exist)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new condition set with one condition. No tax rule uses it, so no tax result changes. It may not be deletable; plan as if it stays."
---

# Manage Tax Condition Sets (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax condition set is a named list of conditions ("bill-from state = NY") built on one **tax determining factor set**. Each condition uses one factor line of that set (class, class qualifier, factor). A tax rule points to condition sets to decide its result; the condition set alone decides nothing. This skill creates **one condition set with one condition** and no rule.

## When to use
- Someone asks to create a **new** condition set for task `ZX_MANAGE_TAX_CONDITION_SETS` on a factor set that already exists.
- Do **not** use it to change existing condition sets or to create tax rules. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
FSET    = DetFactorTemplCode of the existing determining factor set (the person names it; in a test, your own test set)
CODE    = new ConditionGroupCode: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME    = new ConditionGroupName (display name), e.g. "GAPFILL XX test condition set 1" (no "|" character)
COUNTRY = two-letter country code of the condition set (e.g. US)
CLASS, CQ, FACTOR, PARAM = DeterminingFactorClassCode, DeterminingFactorCqCode, DeterminingFactorCode, TaxParameterCode of ONE factor line of FSET (Step 3)
DTYPE   = data type of that factor (Step 3)
VALUE   = the value to compare with, written as names or codes (never an internal ID); see Step 3
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...` and never `$PWD`, which gives `/e/...`: FSCR then writes to a wrong folder such as `E:\e\...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_CONDITION_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 15 files (VERIFIED, 83 s): `ORA_ZX_TAX_RULE_CONDITION_SET.csv` (header, 129 columns, the first condition repeated in `...1` columns), `ORA_ZX_TAX_RULE_CONDITION.csv` (one row per condition), `ORA_ZX_TAX_RULE_CONDITION_SET_TRANSLATION.csv`, the factor set files `ORA_ZX_TAX_RULE_TEMPLATE.csv` and `ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv` (factor lines), the rule files `ZX_TAX_RULE_SUPERTYPE.csv`, `ORA_ZX_TAX_RULE_RESULT.csv`, the factor file `ZX_RATE_DETERMINATION_RULE.csv`, and `ASM_SETUP_CSV_METADATA.xml`.
- Network drops happen on tax exports (no ZIP is written). An export is read-only: run it again into a new folder, one at a time, up to 3 tries. If it still fails or lacks these files: **stop**.

## Step 3. Check the factor set, pick the factor and value
```bash
python -I -c "import csv,sys; [print(r['ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode'],'|',r['DeterminingFactorClassCode'],r['DeterminingFactorCqCode'],r['DeterminingFactorCode'],'| param',r['TaxParameterCode']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
python -I -c "import csv,sys; [print(r['ConditionGroupCode'],'| set',r['DetFactorTemplCode'],'|',r['DeterminingFactorClass1Code'],r['DeterminingFactorCq1Code'],r['DeterminingFactorCode1'],r['DataType1Code'],r['Operator1Code'],'| value',r['AlphanumericValue1']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TAX_RULE_CONDITION_SET.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
1. FSET must have at least one factor line in the first list; if not, **stop** (create it with the gap skill `manage-tax-factor-sets`). CLASS, CQ, FACTOR and PARAM are copied from **one** of its lines (an empty CQ stays empty).
2. **DTYPE and VALUE:** take them from an existing condition set that uses the same CLASS/FACTOR (second list). For `GEOGRAPHY` / `STATE` the data type is `NUMERIC` and the value is the state **as the environment names it** (ours: the 2-letter code, `NY`); Oracle turns it into its own geography ID during the import (VERIFIED). Never write a number taken from an export (`NumericValue1Trans`, `NumericValueTrans` hold internal IDs). If no condition set uses the factor, the data type is in `ZX_RATE_DETERMINATION_RULE.csv` (`DataTypeCode`) when listed there; otherwise GUESS.
3. CODE must not be in the second list (the builder checks it again). There is no REST resource for condition sets (GUESS, not searched further); the export is the check.

## Step 4. Build a package with only the new condition set
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name condset_new.zip --prefix <PREFIX> \
  --key "ORA_ZX_TAX_RULE_CONDITION_SET.csv=ConditionGroupCode" \
  --key "ORA_ZX_TAX_RULE_CONDITION.csv=ConditionGroupCode,DeterminingFactorClassCode,DeterminingFactorCqCode,DeterminingFactorCode" \
  --key "ORA_ZX_TAX_RULE_CONDITION_SET_TRANSLATION.csv=ORA_ZX_TAX_RULE_CONDITION_SET.ConditionGroupCode,Language" \
  --prefix-col "ORA_ZX_TAX_RULE_CONDITION_SET.csv=ConditionGroupCode" --max-len "ConditionGroupCode=30" \
  --row "ORA_ZX_TAX_RULE_CONDITION_SET.csv|ConditionGroupCode=<CODE>|CountryCode=<COUNTRY>|DetFactorTemplCode=<FSET>|MoreThanMaxCondFlag=N|EnabledFlag=Y|DeterminingFactorCode1=<FACTOR>|TaxParameterCode1=<PARAM>|DataType1Code=<DTYPE>|DeterminingFactorClass1Code=<CLASS>|DeterminingFactorCq1Code=<CQ>|Operator1Code==|AlphanumericValue1=<VALUE>|ValueLow1=<VALUE>|RecordTypeCode=USER_DEFINED|ConditionGroupName=<NAME>" \
  --row "ORA_ZX_TAX_RULE_CONDITION.csv|ORA_ZX_TAX_RULE_CONDITION_SET.ConditionGroupCode=<CODE>|ConditionGroupCode=<CODE>|DeterminingFactorClassCode=<CLASS>|DeterminingFactorCqCode=<CQ>|DeterminingFactorCode=<FACTOR>|TaxParameterCode=<PARAM>|DataTypeCode=<DTYPE>|OperatorCode==|RecordTypeCode=USER_DEFINED|IgnoreFlag=N|AlphanumericValue=<VALUE>|ValueLow=<VALUE>" \
  --row "ORA_ZX_TAX_RULE_CONDITION_SET_TRANSLATION.csv|ORA_ZX_TAX_RULE_CONDITION_SET.ConditionGroupCode=<CODE>|ConditionGroupName=<NAME>|Language=US|SourceLang=US"
```
- `Operator1Code==` and `OperatorCode==` mean the column `Operator1Code` holds `=` (equals). VERIFIED
- The header row repeats the first condition in its `...1` columns; the condition row holds the same values. Both are needed (VERIFIED with both).
- The builder must print `ORA_ZX_TAX_RULE_CONDITION_SET.csv: 1 new rows`, `ORA_ZX_TAX_RULE_CONDITION.csv: 1 new rows`, `ORA_ZX_TAX_RULE_CONDITION_SET_TRANSLATION.csv: 1 new rows`, every other file `0 new rows`. It stops if CODE exists, lacks the prefix or is too long.
- Leave `TaxRegimeCode`, every `NumericValue...` column, the audit columns and every other file empty. The factor set row is **not** needed in the ZIP (the condition set file is not a child of it). VERIFIED

## Step 5. Import
**Approval.** The person must approve the environment, the task, FSET and the exact CODE before the import. If their brief names all of them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_CONDITION_SETS --task-name "Manage Tax Condition Sets" \
  --zip-file "<RUN>/payload/condset_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`); it is the only key to the full process log later.
- About 100 s. Print a short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TaxRuleConditionSet. Status: Completed successfully ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0`. **`0 rows were processed` is a failure** even when the status says "Completed successfully".
- **If the script loses the connection after the process started** (no process log), the import still runs in Oracle. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_ZX_TAX_RULE_CONDITION_SET.csv=ConditionGroupCode" \
  --key "ORA_ZX_TAX_RULE_CONDITION.csv=ConditionGroupCode,DeterminingFactorClassCode,DeterminingFactorCqCode,DeterminingFactorCode" \
  --key "ORA_ZX_TAX_RULE_CONDITION_SET_TRANSLATION.csv=ORA_ZX_TAX_RULE_CONDITION_SET.ConditionGroupCode,Language" \
  --expect "ORA_ZX_TAX_RULE_CONDITION_SET.csv=<CODE>" --expect "ORA_ZX_TAX_RULE_CONDITION.csv=<CODE>,<CLASS>,<CQ>,<FACTOR>" \
  --expect "ORA_ZX_TAX_RULE_CONDITION_SET_TRANSLATION.csv=<CODE>,US" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your condition set, its condition and translation were added; the factor set and rule files are unchanged. In the after-export, `NumericValue1Trans` of your row is now filled by Oracle (the resolved ID): that is expected. If someone else changed condition sets between your two exports, extra rows appear: judge your own rows plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 15 files, metadata XML unchanged; only the condition set, its condition and its translation get rows.
3. **Do not create or change a tax rule that uses the condition set** in a test (that changes tax results).
4. Test records may stay for good. This skill never deletes. Record every created condition set.
5. Tested only: one `GEOGRAPHY / BILL_FROM / STATE` condition with `=`. Other factors, several conditions, condition details and other operators: not tested.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 2 condition sets, 6 factor sets; 83 s |
| New record | `GAPFILL_AB_P2_CS1`, "GAPFILL AB P2 condition set 1", factor set `GAPFILL_AB_FS1` (line GEOGRAPHY / BILL_FROM / STATE), country US, condition STATE = `NY` (NUMERIC) |
| Import | 1 attempt, 99 s: TaxRuleConditionSet 1 row, 0 failed |
| Export after + compare | added 1 + 1 + 1, removed 0, changed 0; Oracle filled the geography ID itself: PASS |
