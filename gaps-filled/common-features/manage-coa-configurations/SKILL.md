---
skill_id: "gosaas.gap-fills.common-features.manage-coa-configurations"
name: "Manage Chart of Accounts Configurations: add a segment value security policy by FSM CSV (GoSaaS gap fill)"
description: "Adds ONE segment value security policy (ORA_SEG_VAL_SECURITY_POLICIES: role + secured value set + condition) through the chart of accounts configuration package by FSM CSV import; the chart of accounts options and the global security usage rows stay out of the file. Tested on a secured value set made for the test (no chart of accounts uses it). Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 15, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_MANAGE_COA_CONFIG"
task_name: "Manage Chart of Accounts Configurations"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "GL_MANAGE_SEGMENT_VALUE_SECURITY_RULES (a secured value set; gosaas manage-segment-value-security-rules)"
side_effects:
  - "Step 3 adds a policy: users with the role may use the named values of that value set. On a value set used by a real chart of accounts this changes what users can post to."
  - "The package also holds the chart of accounts options and the one global segment value security usage row: this skill never sends them."
---

# Manage Chart of Accounts Configurations (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
The task's package (VERIFIED, 4 objects) holds: `ORA_GL_CHART_OF_ACCOUNTS_OPTIONS` (one row per chart of accounts instance, e.g. allow the same intercompany value), `ORA_GL_SVSBF_USAGES` (ONE global row: which business functions apply segment value security), `ORA_SEG_VAL_SECURITY_POLICIES` (policies: a role may use some values of a secured value set) and `ORA_SEG_VAL_SECURITY_ASSIGNMENT` (policy assignments per user). This skill adds a **policy**. The options rows and the global usage row are shared settings: never send them in a test (a re-import updates them for everyone).
Use it to grant a role access to values of a secured value set. **For a test**, use your own new secured value set that no chart of accounts uses: then the policy changes nobody's access.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py   (files without rows stay header only)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
POL   = new policy name = PREFIX + short name (e.g. GAPFILL_XX_SVP1)
VS    = the secured value set (for a test: your own, from manage-segment-value-security-rules)
VAL   = a value of VS (e.g. T1)
ROLE  = the role code (e.g. ORA_GL_GENERAL_ACCOUNTANT_JOB)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. A secured value set VS with value VAL. **For a test:** make your own with `<GAPS>/common-features/manage-segment-value-security-rules/SKILL.md` (check first: run that skill's Step 1 export and unzip lines with its RUN = `<RUN>/pre_svs`, skip its grep; in `FND_APP_FLEX_VALUE_SET.csv` the row `ValueSetCode=<VS>` must have `SecurityEnabledFlag Y`, and `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv` must hold `<VS>`,`<VAL>`; create only if missing).
2. The role exists (read only, VERIFIED):
   ```bash
   cd "<RUN>"; python -B "<W>" "<FSCR>" /hcmRestApi/scim/Roles --query 'filter=name eq "<ROLE>"' --query attributes=name,displayName,category --no-open-browser --output role.json > role.log 2>&1
   python -I -c "import json; print([(r.get('name'),r.get('category')) for r in json.load(open('role.json',encoding='utf-8')).get('Resources',[])])"
   ```
   One row = it exists.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_MANAGE_COA_CONFIG --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
grep -c "\"<POL>\"" "<RUN>/exp1/unz/ORA_SEG_VAL_SECURITY_POLICIES.csv"
```
4 CSVs + metadata; the grep must print 0 (the policy file may already hold earlier policies). No ZIP: run again into a NEW folder, up to 3 tries, and use that folder instead of `exp1` in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
Only the policy file gets a row; the other 3 files stay header only (the builder does this).
```bash
cd "<RUN>"; python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name coa.zip --prefix <PREFIX> \
 --key "ORA_SEG_VAL_SECURITY_POLICIES.csv=PolicyName" --prefix-col "ORA_SEG_VAL_SECURITY_POLICIES.csv=PolicyName" --prefix-col "ORA_SEG_VAL_SECURITY_POLICIES.csv=ValueSetCode" \
 --row "ORA_SEG_VAL_SECURITY_POLICIES.csv|PolicyName=<POL>|ValueSetCode=<VS>|RoleCommonName=<ROLE>|ConditionOperatorCode=EQUALS|ConditionFromValue=<VAL>|ConditionFilterEnabledFlag=Y|PolicyDescription=Test policy on an unused value set|StartDate=<today yyyy/mm/dd>"
```
Replace `<today yyyy/mm/dd>` with today's local date. Success: the builder prints `1 new rows` for the policy file.
The `--prefix-col ValueSetCode` makes the builder refuse any value set without your prefix: drop it only for an approved real change. Condition operators other than `EQUALS` (ranges, tree nodes) are GUESS.

## Step 3. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_MANAGE_COA_CONFIG --task-name "Manage Chart of Accounts Configurations" --zip-file "<RUN>/pay/coa.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed` (plus a 0-rows line), every `Business object` line `Completed successfully` (the names differ a little from the file names, e.g. `Segment Value Security Configuration` for the usage row; one may also show `In progress`: normal). Print only the grep lines (the log holds the environment name and user). Dropped connection: never import again; wait 2 minutes and read back.

## Step 4. Read back (VERIFIED)
Export again (Step 1's export and unzip lines with `exp2`), then:
```bash
python -I "<CMP>" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --key "ORA_SEG_VAL_SECURITY_POLICIES.csv=PolicyName" --expect "ORA_SEG_VAL_SECURITY_POLICIES.csv=<POL>"
```
`RESULT: PASS` = policy +1; the options (per chart of accounts) and the usage row unchanged.

## Rules and limits
1. A test adds a policy only on your own unused value set; never send the options or usage rows.
2. Assigning policies to users (`ORA_SEG_VAL_SECURITY_ASSIGNMENT`) was not tested.
3. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Value set | `GAPFILL_AB_B15_SVS1` (secured, value `T1`) |
| Import | policy `GAPFILL_AB_B15_SVP1`, role `ORA_GL_GENERAL_ACCOUNTANT_JOB`, `EQUALS T1`: ProcessId 100004743433661; 1 processed, 0 failed |
| Compare | (your counts will differ) policies 0 → 1; options 6 → 6, usage 1 → 1, assignments 0 → 0, nothing changed: PASS |
| Fresh test | policy `GAPFILL_AB_B15_SVP2F` on `GAPFILL_AB_B15_SVS1`: ProcessId 100004744415062; policies 1 → 2, rest unchanged: PASS |
| Re-test | policy `GAPFILL_AB_B15_SVP3R`: ProcessId 100004744414677; policies 2 → 3, rest unchanged: PASS |
