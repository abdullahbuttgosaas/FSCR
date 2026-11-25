---
skill_id: "gosaas.gap-fills.common-features.manage-segment-value-security-rules"
name: "Manage Segment Value Security Rules: create a General Ledger value set with segment value security enabled, by FSM CSV (GoSaaS gap fill)"
description: "Creates ONE new General Ledger value set with SecurityEnabledFlag Y and its own data security object name, plus its values, through the task's value set package (FND_APP_FLEX_VALUE_SET + values) by FSM CSV import, with an export compare as proof. The security policies (which role sees which values) are the separate task Manage Chart of Accounts Configurations. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 15, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_SEGMENT_VALUE_SECURITY_RULES"
task_name: "Manage Segment Value Security Rules"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Step 3 creates a new value set (security enabled) and its values. Nothing existing changes. Switching security on for an EXISTING value set used by a chart of accounts would hide values from users without a policy: not done by this skill."
---

# Manage Segment Value Security Rules (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
Segment value security limits which values of a chart of accounts segment a user may use. It has two parts: (1) the **value set** is marked secured (`SecurityEnabledFlag Y`, with a `DataSecurityObjectName`), which this task's package holds (VERIFIED: the export is the General Ledger value sets, a few of them secured; counts grow as tests add rows); (2) **policies** that grant a role some values: task Manage Chart of Accounts Configurations (`gosaas common-features/manage-coa-configurations`).
Use this skill to create a new secured value set (for example before attaching it to a new chart of accounts). **Do not** switch security on for a value set in use by a real chart of accounts in a test: users without a policy lose access to its values.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
VS    = new value set code = PREFIX + short name, at most 30 characters (e.g. GAPFILL_XX_SVS1)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In the commands, replace each `<NAME>` with its value (or set shell variables first). All paths are absolute, so a command works from any folder.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. The General Ledger `ModuleId` (Step 2), so the value set lands in this task's scope. Never copy it from an export.

## Step 1. Read-only export (VERIFIED, about 1 to 2 minutes)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code GL_MANAGE_SEGMENT_VALUE_SECURITY_RULES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
grep -c "\"<VS>\"" "<RUN>/exp1/unz/FND_APP_FLEX_VALUE_SET.csv"
```
6 CSVs (plus `ASM_SETUP_CSV_METADATA.xml`): `FND_APP_FLEX_VALUE_SET` (value sets), `ORA_FND_APP_FLEX_VALUE_SET_VALUE` (values), and 4 related/validation files. The grep must print 0. No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Read the General Ledger ModuleId live (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/standardLookups --query onlyData=true --query "q=LookupType LIKE 'GL_%'" --query limit=40 --query fields=LookupType,ModuleId --no-open-browser --output glm.json > glm.log 2>&1
python -I -c "import json,collections; c=collections.Counter(i['ModuleId'] for i in json.load(open('glm.json',encoding='utf-8'))['items'] if i.get('ModuleId')); print(c.most_common(1)[0][0])" > m.txt
M=$(cat m.txt); echo ${#M}
```
The last line must print 32. (VERIFIED: it equals the `ModuleId` of the secured value sets in the export.) A GET timeout is safe to repeat.

## Step 3. Build and import (VERIFIED)
```bash
cd "<RUN>"; python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name svs.zip --prefix <PREFIX> \
 --key "FND_APP_FLEX_VALUE_SET.csv=ValueSetCode" --key "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=FND_APP_FLEX_VALUE_SET.ValueSetCode,Value" \
 --prefix-col "FND_APP_FLEX_VALUE_SET.csv=ValueSetCode" \
 --row "FND_APP_FLEX_VALUE_SET.csv|ValueSetCode=<VS>|ModuleId=$M|Description=Test secured value set|ValidationType=INDEP|ValueDataType=VARCHAR2|ValueSubtype=TEXT|MaximumLength=10|UppercaseOnlyFlag=Y|ZeroFillFlag=N|SecurityEnabledFlag=Y|DataSecurityObjectName=<VS>" \
 --row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=T1|Description=Test value|EnabledFlag=Y|SummaryFlag=N"
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code GL_MANAGE_SEGMENT_VALUE_SECURITY_RULES --task-name "Manage Segment Value Security Rules" --zip-file "<RUN>/pay/svs.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}|ORA-[0-9]+: [^.\]{0,160}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`$M` is from Step 2; in a new shell run `M=$(cat "<RUN>/m.txt")` first (never print it). Before the import, check the builder printed 1 new row for each of the two files. `DataSecurityObjectName` is a free name for the secured object; using VS is fine (VERIFIED). Success: `A total of 2 rows were processed. 0 rows of them failed` (value set + value), `Application Flexfield Value Set. Status: Completed successfully`. Write down the ProcessId. Print only the grep lines (the log holds the environment name and user). Dropped connection: never import again; wait 2 minutes and read back.

## Step 4. Read back (VERIFIED)
Export again (Step 1 with `exp2`, both lines), then:
```bash
python -I "<CMP>" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --key "FND_APP_FLEX_VALUE_SET.csv=ValueSetCode" --key "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=FND_APP_FLEX_VALUE_SET.ValueSetCode,Value" --expect "FND_APP_FLEX_VALUE_SET.csv=<VS>" --expect "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=<VS>,T1"
python -I -c "import csv,sys; r=[r for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig')) if r['ValueSetCode']==sys.argv[2]][0]; print(r['SecurityEnabledFlag'], r['DataSecurityObjectName'])" "<RUN>/exp2/unz/FND_APP_FLEX_VALUE_SET.csv" "<VS>"
```
`RESULT: PASS` (value set +1, value +1, nothing else) and `Y <VS>`.

## Rules and limits
1. New value sets only; never switch security on an existing value set in a test.
2. Next step for a working rule: a policy for a role (manage-coa-configurations skill).
3. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only; your counts will differ)
| Step | Result |
|---|---|
| Import | `GAPFILL_AB_B15_SVS1` + value `T1`: ProcessId 100004744413699; 2 processed, 0 failed |
| Compare | value sets 105 → 106, values 1161 → 1162, nothing else changed: PASS; `SecurityEnabledFlag Y` |
| Fresh test | `GAPFILL_AB_B15_SVS2F`: ProcessId 100004743432393; 106 → 107, 1162 → 1163: PASS |
| Re-test | `GAPFILL_AB_B15_SVS3R`: ProcessId 100004743435641; 107 → 108, 1163 → 1164: PASS |
