---
skill_id: "gosaas.gap-fills.common-features.manage-tax-rules"
name: "Manage Tax Rules (GoSaaS gap fill)"
description: "Create a new, DISABLED tax rule (header + translation + one rule result) for a tax owned by the global configuration owner, through FSCR's setup-task CSV export and import (ZX_TAX_RULE_SUPERTYPE + ORA_ZX_TAX_RULE_RESULT), copying an existing rule's settings and an existing condition set, then read it back with a second export. Checks first that the tax's regime has the global configuration owner option (prerequisite, manage-tax-regimes Step 7). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 2 (failed 3 times, 2026-11-24); cause found and fixed in batch taxfix, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_RULES"
task_name: "Manage Tax Rules"
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
  - "ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS and ZX_MANAGE_TAX_CONDITION_SETS (the factor set and condition set must exist)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new DISABLED tax rule with one result. A disabled rule is never evaluated. It may not be deletable; plan as if it stays."
---

# Manage Tax Rules (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax rule decides one step of tax determination (for example "is this tax applicable") for one tax. It is built on a determining factor set; each **rule result** row points to a condition set and gives the result (for example `NOT_APPLICABLE`). Rules are evaluated by priority. This skill creates the rule **disabled** (`EnabledFlag=N`): it is never evaluated until a person enables it on purpose.

## When to use
- Someone asks to create a **new** tax rule for task `ZX_MANAGE_TAX_RULES` on an existing tax, with an existing factor set and condition set.
- Not for changing or enabling existing rules. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix for the new rule, e.g. GAPFILL_<INITIALS>_
REGIME, TAX = the existing regime and tax (owner: global configuration owner) the rule is for
FSET    = DetFactorTemplCode of the existing determining factor set (usage TAX_RULES)
CSET    = ConditionGroupCode of the existing condition set built on FSET
CODE    = new TaxRuleCode: upper case letters, digits and _, starting with PREFIX, max 30
NAME    = new TaxRuleName, e.g. "GAPFILL XX rule 1" (no "|" character)
FROM    = EffectiveFrom, yyyy/mm/dd: on or after the tax's EffectiveFrom
TEMPLATE= TaxRuleCode of one existing rule to copy settings from (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials.
- **Exports are read-only.** If one drops (no ZIP written), run it again into a new folder, one at a time, up to 3 tries; then stop.

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
Export `ZX_MANAGE_TAXES` to `<RUN>/export_tax`. Then:
```bash
python -I -c "import csv,sys; [print('TAX',r['Tax'],'| regime',r['TaxRegimeCode'],'| owner',r['ContentOwnerPartyTypeCode'],r['BuName'] or '-','| live',r['LiveForProcessingFlag'],'| from',r['EffectiveFrom']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX.csv',encoding='utf-8-sig')) if r['Tax']==sys.argv[2] and r['TaxRegimeCode']==sys.argv[3]]" "<RUN>/export_tax/unz" "<TAX>" "<REGIME>"
python -I -c "import csv,sys; print('GCO option row for regime:', any(r['TaxRegimeCode']==sys.argv[2] for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_BU_GCO_TAX_SUB.csv',encoding='utf-8-sig'))))" "<RUN>/export_tax/unz" "<REGIME>"
```
- Exactly one `TAX` line with `owner GCO -` is needed; else **stop** (create the tax with the gap skill `manage-taxes`; business-unit owned taxes are not tested).
- The second line must print `True`. If `False`, Oracle refuses the rule with `ZX_RECRATE_DATE_INVALID: Enter a date range that's within the date range of the parent tax of {TAX_START_DATE} to {TAX_END_DATE}` with **empty placeholders** (the tax is not found; VERIFIED 3 times before the row existed). Do **`manage-tax-regimes` Step 7** for REGIME first (only on your own test regime or with the person's approval), then repeat this step.
- In our test the tax also had a status and a rate when the rule was imported. Whether a rule needs them is not tested (GUESS: no).

## Step 3. Read-only rules export, template, condition
Export `ZX_MANAGE_TAX_RULES` to `<RUN>/export_before` (40 to 120 s). Expect 15 files (the same files as the condition sets package): `ZX_TAX_RULE_SUPERTYPE.csv` (rule header), `ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv`, `ORA_ZX_TAX_RULE_RESULT.csv` (results, with the condition repeated in `...1` columns), `ORA_ZX_TAX_RULE_CONDITION_SET.csv`, `ORA_ZX_TAX_RULE_TEMPLATE.csv` (factor sets) and others, `ASM_SETUP_CSV_METADATA.xml`.
```bash
python -I -c "import csv,sys; [print('RULE',r['TaxRuleCode'],'|',r['Tax'],'|',r['ServiceTypeCode'],'| owner',r['ContentOwnerPartyTypeCode'],r['BuName'] or '-','| enabled',r['EnabledFlag']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_RULE_SUPERTYPE.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
python -I -c "import csv,sys; [print('CSET',r['ConditionGroupCode'],'| fset',r['DetFactorTemplCode'],'|',r['DeterminingFactorClass1Code'],r['DeterminingFactorCq1Code'],r['DeterminingFactorCode1'],r['Operator1Code'],r['AlphanumericValue1']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TAX_RULE_CONDITION_SET.csv',encoding='utf-8-sig')) if r['ConditionGroupCode']==sys.argv[2]]" "<RUN>/export_before/unz" "<CSET>"
```
1. **TEMPLATE** = the first listed `RULE` with service `DET_APPLICABLE_TAXES` (an applicability rule). If none exists: **stop** (not tested).
2. **CSET** must print exactly one line, with `fset <FSET>`; else **stop** (make it with the gap skill `manage-tax-condition-sets`). Note its 5 condition values: class, qualifier, factor, operator, value (for example `GEOGRAPHY BILL_FROM STATE = NY`). Only **one-condition** sets are tested.
3. **CODE is free:** not in the RULE list for TAX (the builder checks it again).

## Step 4. Build a package with only the new rule
```bash
K='--set TaxRegimeCode=<REGIME> --set Tax=<TAX> --set TaxRuleCode=<CODE> --set EffectiveFrom=<FROM> --set ContentOwnerPartyTypeCode=GCO --clear BuName --clear EnterpriseId'
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_RULE_SUPERTYPE.csv \
  --match "TaxRuleCode=<TEMPLATE>" $K --set DetFactorTemplCode=<FSET> --set EnabledFlag=N --set NeverBeenEnabledFlag=Y \
  --set "TaxRuleName=<NAME>" --clear EffectiveTo --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv \
  --match "ZX_TAX_RULE_SUPERTYPE.TaxRuleCode=<TEMPLATE>" --match Language=US \
  --set ZX_TAX_RULE_SUPERTYPE.TaxRegimeCode=<REGIME> --set ZX_TAX_RULE_SUPERTYPE.Tax=<TAX> --set ZX_TAX_RULE_SUPERTYPE.TaxRuleCode=<CODE> \
  --set ZX_TAX_RULE_SUPERTYPE.EffectiveFrom=<FROM> --set ZX_TAX_RULE_SUPERTYPE.ContentOwnerPartyTypeCode=GCO --clear ZX_TAX_RULE_SUPERTYPE.BuName \
  --set "TaxRuleName=<NAME>" --out "<RUN>/rows.txt" --append
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_TAX_RULE_RESULT.csv \
  --match "TaxRuleCode=<TEMPLATE>" $K --set ConditionGroupCode=<CSET> --set ConditionGroupCode1=<CSET> \
  --set DetFactorTemplCode=<FSET> --set DetFactorTemplCode1=<FSET> \
  --set DeterminingFactorClass1Code=<class> --set DeterminingFactorCq1Code=<qualifier> --set DeterminingFactorCode1=<factor> \
  --set Operator1Code=<operator> --set AlphanumericValue1=<value> --clear NumericValue1 --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name rule_new.zip --prefix <PREFIX> \
  --key "ZX_TAX_RULE_SUPERTYPE.csv=TaxRuleCode,TaxRegimeCode,Tax" \
  --key "ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv=ZX_TAX_RULE_SUPERTYPE.TaxRuleCode,ZX_TAX_RULE_SUPERTYPE.TaxRegimeCode,ZX_TAX_RULE_SUPERTYPE.Tax,Language" \
  --key "ORA_ZX_TAX_RULE_RESULT.csv=TaxRuleCode,TaxRegimeCode,Tax,ConditionGroupCode" \
  --prefix-col "ZX_TAX_RULE_SUPERTYPE.csv=TaxRuleCode" --max-len "TaxRuleCode=30" @"<RUN>/rows.txt"
```
- The 5 condition values come from the CSET line of Step 3. **`NumericValue1` stays empty**: it holds an internal id (for a geography condition, the geography id); Oracle fills it itself from the condition set (VERIFIED). Never copy an id from an export.
- `EnterpriseId` and `BuName` are empty for a GCO-owned rule, as on every GCO-owned row in the tax exports (VERIFIED).
- The result keeps the template's result (applicability rule: `ResultTypeCode=APPLICABILITY`, `AlphanumericResult=NOT_APPLICABLE`) and is enabled; the **rule header** is disabled, so nothing is evaluated.
- The builder must print `ZX_TAX_RULE_SUPERTYPE.csv: 1 new rows`, `ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv: 1 new rows`, `ORA_ZX_TAX_RULE_RESULT.csv: 1 new rows`, every other file `0 new rows`.

## Step 5. Import
**Approval.** The person must approve the environment, the task, TAX, CSET and the exact CODE. If their brief names all of them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_RULES --task-name "Manage Tax Rules" \
  --zip-file "<RUN>/payload/rule_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`**. `StatusCode: (unknown)` in the script output is normal.
- About 40 s. Short summary:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Row Identifier[^\n]*|Message Text: [^\n]+|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TaxRule1 ... 1 rows ... 0 failed`, `Detail Object: TaxRuleResult1 ... 1 rows ... 0 failed`, `Total Objects Failed: 0`. **`0 rows were processed` is a failure.**
- `ZX_RECRATE_DATE_INVALID` with empty `{TAX_START_DATE}` placeholders = the prerequisite of Step 2 is missing. With filled dates: FROM is outside the tax's dates.
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 6.
- Other row errors: change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second rules export and compare
Export `ZX_MANAGE_TAX_RULES` to `<RUN>/export_after`, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX_RULE_SUPERTYPE.csv=TaxRuleCode,TaxRegimeCode,Tax" \
  --key "ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv=ZX_TAX_RULE_SUPERTYPE.TaxRuleCode,ZX_TAX_RULE_SUPERTYPE.TaxRegimeCode,ZX_TAX_RULE_SUPERTYPE.Tax,Language" \
  --key "ORA_ZX_TAX_RULE_RESULT.csv=TaxRuleCode,TaxRegimeCode,Tax,ConditionGroupCode" \
  --expect "ZX_TAX_RULE_SUPERTYPE.csv=<CODE>,<REGIME>,<TAX>" \
  --expect "ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv=<CODE>,<REGIME>,<TAX>,US" \
  --expect "ORA_ZX_TAX_RULE_RESULT.csv=<CODE>,<REGIME>,<TAX>,<CSET>" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your rule header, its translation and its result were added; nothing removed or changed. Also check the new header row shows `EnabledFlag` `N`.

## Rules and limits
1. New records only; never import a full export. **Keep the rule disabled** (`EnabledFlag=N`) in any test; enabling it changes tax results and needs the person's explicit decision.
2. Never take IDs from an export (`NumericValue1` stays empty).
3. Test records may stay for good. This skill never deletes. Record every created rule.
4. Tested only: applicability rule, GCO owner, one-condition geography condition set, not-live tax. Not tested: other rule types (status, rate, taxable basis...), business-unit owned rules, several results.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts; `-I` for the helpers and one-liners.

## Why the first 3 tries failed (2026-11-24, VERIFIED cause)
Batch 3 tried the same rows 3 times (owner GCO from the tax start, a month later, owner = a test business unit that subscribes the regime): all refused with `ZX_RECRATE_DATE_INVALID` and empty placeholders. The cause is the same as for tax statuses: the test regime had no global configuration owner option row (`ORA_ZX_BU_GCO_TAX_SUB.csv`). After adding it (manage-tax-regimes Step 7), the rule imported on the first try.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Prerequisite | test regime got its GCO option row; the tax also had a status and a rate |
| Template | the one existing applicability rule (business-unit owned; owner changed to GCO) |
| New record | `GAPFILL_AB_TF_RL1`, disabled, on test tax `GAPFILL_AB_P1_TX1`, factor set `GAPFILL_AB_FS1`, condition set `GAPFILL_AB_P2_CS1` (STATE = NY), result NOT_APPLICABLE |
| Import | 1 attempt, 40 s, ProcessId 100004742410090: TaxRule1 and TaxRuleResult1 1 row each, 0 failed |
| Export after + compare | rules 1 to 2, results 1 to 2, translations 1 to 2; nothing removed or changed; header `EnabledFlag N`; Oracle filled `NumericValue1` itself |
