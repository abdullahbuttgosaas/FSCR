---
skill_id: "gosaas.gap-fills.common-features.manage-tax-factor-sets"
name: "Manage Tax Determining Factor Sets (GoSaaS gap fill)"
description: "Create a new tax determining factor set (header, translation and factor lines copied from one existing set) through FSCR's setup-task CSV export and import, then read it back with a second export. No condition set or rule uses it. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 3, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS"
task_name: "Manage Tax Determining Factor Sets"
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
  - "gosaas common-features/manage-tax-regimes/scripts/template_row.py"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new determining factor set. No tax condition set or tax rule uses it, so no calculation changes. It may not be deletable; plan as if it stays."
---

# Manage Tax Determining Factor Sets (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file. It uses the generic helpers of the gap skill `manage-docseq-categories` and `template_row.py` of the gap skill `manage-tax-regimes`.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A tax determining factor set lists the facts a tax rule looks at (for example "bill-from state", "product fiscal classification"). Each **factor line** has a class (`GEOGRAPHY`, `PRODUCT`...), a class qualifier (`BILL_FROM`, `SHIP_TO`...) and a factor (`STATE`, `COUNTRY`...). Tax condition sets and tax rules are built **on** a factor set; the set alone decides nothing. This skill creates a **new set by copying the lines of one existing set**, so every line is a combination Oracle already accepted. Condition sets and rules are not part of the test.

## When to use
- Someone asks to create a **new** determining factor set for task `ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS`.
- Do **not** use it to change existing sets, condition sets or rules. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE    = new DetFactorTemplCode: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME    = new DetFactorTemplName, e.g. "GAPFILL XX test factor set 1" (no "|" character)
TEMPLATE= DetFactorTemplCode of one existing set to copy (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder such as `E:\e\...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 15 files (VERIFIED, 1 to 4 minutes): `ORA_ZX_TAX_RULE_TEMPLATE.csv` (the sets: `DetFactorTemplCode, TaxRegimeCode, TemplateUsageCode, RecordTypeCode, ...audit..., DetFactorTemplName, DetFactorTemplDesc, ..., Tax, ServiceTypeCode, Name, UsageTypeFlag`), `ORA_ZX_TAX_RULE_TEMPLATE_TRANSLATION.csv`, `ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv` (the factor lines: `ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode, DeterminingFactorClassCode, DeterminingFactorCqCode, DeterminingFactorCode, RequiredFlag, RecordTypeCode, ..., TaxRegimeDetLevelCode, TaxParameterCode, ...`), condition set, condition, rule, rule result and supertype files, and `ASM_SETUP_CSV_METADATA.xml`.
- **Network drops are common on tax exports** (`The read operation timed out`, `Remote end closed connection without response`): no ZIP is written. An export is read-only, so run it again into a new folder, one export at a time. VERIFIED
- If it still has no ZIP after 3 tries or lacks these files: **stop**.
- No REST resource for factor sets was found (`taxDeterminingFactorSets`, `taxDeterminingFactorSetsLOV`, `taxRuleTemplates`: HTTP 404); the export compare is the read-back.

## Step 3. Choose a template set and list its lines
```bash
python -I -c "import csv,sys; d=sys.argv[1]; L=list(csv.DictReader(open(d+'/ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv',encoding='utf-8-sig'))); [print(r['DetFactorTemplCode'],'| regime',r['TaxRegimeCode'] or '-','| usage',r['TemplateUsageCode'],'| lines:',[(l['DeterminingFactorClassCode'],l['DeterminingFactorCqCode'],l['DeterminingFactorCode']) for l in L if l['ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode']==r['DetFactorTemplCode']]) for r in csv.DictReader(open(d+'/ORA_ZX_TAX_RULE_TEMPLATE.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
- **TEMPLATE** = the set whose lines the person wants. If they name none, take one with **no regime** (`regime -`), so the new set is not tied to any regime; prefer a code that does not start with a test prefix. VERIFIED
- CODE must not be in this list (the builder also checks).
- If the environment has no set at all, this skill cannot be used (no template); stop and report it.

## Step 4. Build a package with only the new set
One `template_row.py` call per row: the header, its translation, then **one call per factor line** of the TEMPLATE (add `--match` on the line's class, qualifier and factor so each call selects exactly one row):
```bash
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_TAX_RULE_TEMPLATE.csv \
  --match "DetFactorTemplCode=<TEMPLATE>" --set "DetFactorTemplCode=<CODE>" --set "DetFactorTemplName=<NAME>" --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_TAX_RULE_TEMPLATE_TRANSLATION.csv \
  --match "ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode=<TEMPLATE>" --match "Language=US" \
  --set "ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode=<CODE>" --set "DetFactorTemplName=<NAME>" --out "<RUN>/rows.txt" --append
# repeat for each line (CLASS, CQ, FACTOR from the Step 3 list):
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv \
  --match "ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode=<TEMPLATE>" --match "DeterminingFactorClassCode=<CLASS>" \
  --match "DeterminingFactorCqCode=<CQ>" --match "DeterminingFactorCode=<FACTOR>" \
  --set "ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode=<CODE>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name factorset_new.zip --prefix <PREFIX> \
  --key "ORA_ZX_TAX_RULE_TEMPLATE.csv=DetFactorTemplCode" \
  --key "ORA_ZX_TAX_RULE_TEMPLATE_TRANSLATION.csv=ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode,Language" \
  --key "ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv=ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode,DeterminingFactorClassCode,DeterminingFactorCqCode,DeterminingFactorCode" \
  --prefix-col "ORA_ZX_TAX_RULE_TEMPLATE.csv=DetFactorTemplCode" --max-len "DetFactorTemplCode=30" @"<RUN>/rows.txt"
```
- If a line's qualifier (`DeterminingFactorCqCode`) is empty, leave that `--match` out and use `--match` on the columns that are filled; the call must select exactly 1 row.
- The builder must print `1 new rows` for the set and its translation, one new row per copied line in `ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv`, and nothing for any other file. It stops if CODE already exists (importing it would **update** that set), lacks the prefix, or is too long.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact CODE before the import. If their brief names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS --task-name "Manage Tax Determining Factor Sets" \
  --zip-file "<RUN>/payload/factorset_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
Print a short summary of the process log (detail objects that processed rows, error texts, totals):
```bash
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
```
- Success (VERIFIED, about 30 s): `Detail Object: TaxRuleConditionSetTemplate. Status: Completed successfully. ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0`. The factor lines are loaded with the set and have no line of their own; Step 6 proves them.
- **`0 rows were processed` is a failure.** A row can validate and still fail at the database insert (`JBO-26041`, seen on another tax task): always read `Total Objects Failed`.
- If the script loses the connection after `Started setup task CSV import process: <id>`, the import still runs in Oracle. **Do not import again**; wait 2 minutes and do Step 6.
- Rows failed: copy the `Message Text`, change one thing, retry at most 3 times.

## Step 6. Read back (second export and compare)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_ZX_TAX_RULE_TEMPLATE.csv=DetFactorTemplCode" \
  --key "ORA_ZX_TAX_RULE_TEMPLATE_TRANSLATION.csv=ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode,Language" \
  --key "ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv=ORA_ZX_TAX_RULE_TEMPLATE.DetFactorTemplCode,DeterminingFactorClassCode,DeterminingFactorCqCode,DeterminingFactorCode" \
  --expect "ORA_ZX_TAX_RULE_TEMPLATE.csv=<CODE>" --expect "ORA_ZX_TAX_RULE_TEMPLATE_TRANSLATION.csv=<CODE>,US" \
  --expect "ORA_ZX_TAX_RULE_COND_DETAIL_TEMP.csv=<CODE>,<CLASS>,<CQ>,<FACTOR>" \
  --rows-out "<RUN>/added_rows.csv"
```
Give one `--expect` per copied factor line. `RESULT: PASS` = only your set, its translation and its lines were added, nothing removed or changed, and no condition set, rule or result file changed. If someone else changed factor sets between your two exports, judge your own rows plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 15 files, metadata XML unchanged; every file except the set, its translation and its lines stays header-only.
3. **No condition set or rule in a test** (task Manage Tax Condition Sets / tax rules): they change tax results. Not tested; needs the person's explicit approval.
4. Test records may stay for good. This skill never deletes. Record every created set.
5. Not tested: sets tied to a regime or tax, lines that are not copied from an existing set, sets with several lines.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `template_row.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 4 sets, 4 lines; first two tries lost the network, third worked |
| Template | the one set with no regime; 1 line (`GEOGRAPHY`, `BILL_FROM`, `STATE`) |
| New record | `GAPFILL_AB_FS1`, name "GAPFILL AB test factor set 1" |
| Import | 1 attempt, about 30 s: 1 set processed, 0 failed, 7 objects succeeded |
| Export after + compare | sets 4 -> 5, translations 4 -> 5, lines 4 -> 5; removed 0, changed 0; condition sets, rules and results unchanged: PASS |
