---
skill_id: "gosaas.gap-fills.common-features.manage-tax-box-allocation-rules"
name: "Manage Tax Box Allocation Rules: a disabled tax box rule through the task's FSM CSV package (GoSaaS gap fill)"
description: "Creates ONE new, disabled tax box allocation rule (rule type DET_TAX_BOX, a tax reporting type and code as the box, periodic or annual) for a tax owned by the global configuration owner, through FSCR's setup-task CSV export and import, and reads it back. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 21 (written), batch 22 (tested), 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_JE_MANAGE_TAX_BOX_ALLOCATION_RULES"
task_name: "Manage Tax Box Allocation Rules"
dataloader_import_mode: "FSM CSV"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "gosaas.gap-fills.common-features.manage-tax-regimes (own regime with its GCO option row, Step 7)"
  - "gosaas.gap-fills.common-features.manage-taxes (own tax, not live)"
  - "gosaas.gap-fills.common-features.manage-tax-reporting-types (own reporting type with at least one code: the box)"
  - "gosaas.gap-fills.common-features.manage-tax-rules (own rule to copy, own determining factor set and condition set)"
side_effects:
  - "Step 4 adds one rule header (disabled), its translation, one result and one result detail. Disabled, it allocates nothing. No delete by CSV."
---

# Manage Tax Box Allocation Rules (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** Runs FSCR's scripts in place; edits no FSCR file. Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.

## What it is and when to use
Tax box allocation (EMEA VAT returns) puts each taxable line in a tax return box. A tax box rule is a tax rule of rule type **`DET_TAX_BOX`** (VERIFIED: the task export's scope is `RuleTypeCode=DET_TAX_BOX`) with a **reporting type** on the header, a **periodicity** (`PERIODIC` or `ANNUAL`, lookup `ZX_RULE_PERIODICITY`, VERIFIED by REST) and a result of type **`CODE`** whose value is the box (a code of that reporting type).
Package (VERIFIED, 14 files, the tax rules package): header `ZX_TAX_RULE_SUPERTYPE.csv` (`ServiceTypeCode`, `ReportingTypeCode`, `PeriodicityCode`), its translation, result `ORA_ZX_TAX_RULE_RESULT.csv` (`ResultTypeCode`, `AlphanumericResult`) and result detail `ORA_TAX_RULE_RESULT_DETAILS.csv` (`ReportingTypeCodeNum`, `ReportingCodeCharValueNum`). No REST resource (`taxBoxAllocationRules` 404, VERIFIED).

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and the filled-in fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder
T      = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
H      = <GAPS>/common-features/manage-docseq-categories/scripts    (build_fsm_package.py, compare_fsm_exports.py)
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path, E:/... style)
PREFIX = your test prefix, e.g. GAPFILL_XX_
REGIME, TAX = your own test regime (with its GCO option row) and tax (not live)
TEMPLATE = TaxRuleCode of your own existing rule on REGIME and TAX (manage-tax-rules), copied for its settings
FSET, CSET = that rule's determining factor set and condition set (Step 2)
RTYPE, BOX = your own reporting type on REGIME and one of its codes (ReportingCodeCharValue)
CODE   = new rule code = PREFIX + short name (max 30 characters)
FROM   = effective from, YYYY/MM/DD, not before the tax's and regime's start
```
Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page; a valid cached sign-in returns at once). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names; never print `ASM_SETUP_CSV_METADATA.xml`.

## Prerequisites (reuse tested gap skills; never create one twice)
1. REGIME with its GCO option row (manage-tax-regimes Step 7) and TAX on it (manage-taxes).
2. RTYPE with at least one code BOX on REGIME (manage-tax-reporting-types). Check with a read-only export of `ZX_MANAGE_TAX_REPORTING_TYPES`: `ORA_ZX_TAX_REPORTING_CODE.csv` must have a row with `ORA_ZX_REPORTING_TYPE.ReportingTypeCode=<RTYPE>` and `ReportingCodeCharValue=<BOX>`.
3. TEMPLATE with its FSET and CSET (manage-tax-rules, manage-tax-factor-sets, manage-tax-condition-sets).

## Step 1. Read-only export (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_JE_MANAGE_TAX_BOX_ALLOCATION_RULES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/e1" > "<RUN>/e1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/e1"
```
14 CSVs + metadata. No ZIP: export again into a NEW folder, up to 3 tries.

## Step 2. Check TEMPLATE and read FSET, CSET (VERIFIED)
```bash
python -I -c "import csv,sys; [print(r['TaxRuleCode'],r['TaxRegimeCode'],r['Tax'],r['ServiceTypeCode'],r['DetFactorTemplCode'],r['Priority'],r['EnabledFlag']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_RULE_SUPERTYPE.csv',encoding='utf-8-sig'))]; [print('CSET',r['TaxRuleCode'],r['ConditionGroupCode'],r['Priority']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TAX_RULE_RESULT.csv',encoding='utf-8-sig'))]" "<RUN>/e1/unz"
```
TEMPLATE must be on REGIME and TAX; FSET = its `DetFactorTemplCode`, CSET = its `ConditionGroupCode`. Note the result `Priority` (RP). CODE must not be in the list.
**Rule order:** the header `Priority` (NP) must not be used yet by another `DET_TAX_BOX` rule on the same REGIME and TAX (VERIFIED: `ZX_RULES_ORDER_EXISTS_GCO_OWN` "A tax rule with this rule order already exists for this combination", nothing created). List the used ones and pick a free number (for example the highest + 10):
```bash
python -I -c "import csv,sys; print('used DET_TAX_BOX priorities:', sorted(int(r['Priority']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_RULE_SUPERTYPE.csv',encoding='utf-8-sig')) if r['ServiceTypeCode']=='DET_TAX_BOX' and r['TaxRegimeCode']==sys.argv[2] and r['Tax']==sys.argv[3]))" "<RUN>/e1/unz" <REGIME> <TAX>
```

## Step 3. Build one package: header, translation, result, result detail (VERIFIED)
```bash
cd "<RUN>"; rm -f rows.txt; E=e1/unz
K="--set TaxRuleCode=<CODE> --set ServiceTypeCode=DET_TAX_BOX --set EffectiveFrom=<FROM> --clear BuName --clear EnterpriseId"
KH="--set Priority=<NP>"; KR="--set Priority1=<NP>"
python -I "<T>/template_row.py" --export-dir $E --file ZX_TAX_RULE_SUPERTYPE.csv --match "TaxRuleCode=<TEMPLATE>" $K $KH --set EnabledFlag=N --set NeverBeenEnabledFlag=Y --set "TaxRuleName=<name>" --set ReportingTypeCode=<RTYPE> --set PeriodicityCode=PERIODIC --clear EffectiveTo --out rows.txt
python -I "<T>/template_row.py" --export-dir $E --file ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv --match "ZX_TAX_RULE_SUPERTYPE.TaxRuleCode=<TEMPLATE>" --match Language=US --set ZX_TAX_RULE_SUPERTYPE.TaxRuleCode=<CODE> --set ZX_TAX_RULE_SUPERTYPE.ServiceTypeCode=DET_TAX_BOX --set ZX_TAX_RULE_SUPERTYPE.Priority=<NP> --set ZX_TAX_RULE_SUPERTYPE.EffectiveFrom=<FROM> --clear ZX_TAX_RULE_SUPERTYPE.BuName --set "TaxRuleName=<name>" --out rows.txt --append
python -I "<T>/template_row.py" --export-dir $E --file ORA_ZX_TAX_RULE_RESULT.csv --match "TaxRuleCode=<TEMPLATE>" $K $KR --set ResultTypeCode=CODE --set AlphanumericResult=<BOX> --clear NumericValue1 --out rows.txt --append
P="ORA_ZX_TAX_RULE_RESULT.ConditionGroupCode=<CSET>|ORA_ZX_TAX_RULE_RESULT.Priority=<RP>|ORA_ZX_TAX_RULE_RESULT.EnabledFlag=Y|ORA_ZX_TAX_RULE_RESULT.TaxRegimeCode=<REGIME>|ORA_ZX_TAX_RULE_RESULT.Tax=<TAX>|ORA_ZX_TAX_RULE_RESULT.TaxRuleCode=<CODE>|ORA_ZX_TAX_RULE_RESULT.ServiceTypeCode=DET_TAX_BOX|ORA_ZX_TAX_RULE_RESULT.Priority1=<NP>|ORA_ZX_TAX_RULE_RESULT.EffectiveFrom=<FROM>|ORA_ZX_TAX_RULE_RESULT.ContentOwnerPartyTypeCode=GCO"
printf -- '--row\n%s\n' "ORA_TAX_RULE_RESULT_DETAILS.csv|$P|AlphanumericValue=<BOX>|RecordTypeCode=USER_DEFINED|ServiceTypeCode=DET_TAX_BOX|ReportingTypeCodeNum=<RTYPE>|TaxRegimeCodeNum=<REGIME>|ReportingCodeCharValueNum=<BOX>|EffectiveFromNum=<FROM>" >> rows.txt
grep -c DET_APPLICABLE rows.txt
python -I "<H>/build_fsm_package.py" --export-dir $E --out-dir pay --zip-name tb.zip --prefix <PREFIX> --key "ZX_TAX_RULE_SUPERTYPE.csv=TaxRuleCode,TaxRegimeCode,Tax" --key "ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv=ZX_TAX_RULE_SUPERTYPE.TaxRuleCode,ZX_TAX_RULE_SUPERTYPE.TaxRegimeCode,ZX_TAX_RULE_SUPERTYPE.Tax,Language" --key "ORA_ZX_TAX_RULE_RESULT.csv=TaxRuleCode,TaxRegimeCode,Tax,ConditionGroupCode" --prefix-col "ZX_TAX_RULE_SUPERTYPE.csv=TaxRuleCode" --max-len "TaxRuleCode=30" @rows.txt
```
- `grep -c DET_APPLICABLE` must print `0` (every rule-type column says `DET_TAX_BOX`). The header `Priority`, the translation's `ZX_TAX_RULE_SUPERTYPE.Priority` and the result's `Priority1` all carry `<NP>`.
- The condition values come from the template's result; `NumericValue1` stays empty (Oracle fills it). Never copy an id from an export.
- `AlphanumericResult` is **required** for a `CODE` result (VERIFIED: `ZX_REQUIRED_VALUE` without it); it holds the box.
- The builder must print `1 new rows` for `ZX_TAX_RULE_SUPERTYPE.csv`, `ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv`, `ORA_ZX_TAX_RULE_RESULT.csv` and `ORA_TAX_RULE_RESULT_DETAILS.csv`, and `0 new rows` for every other file.

## Step 4. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_JE_MANAGE_TAX_BOX_ALLOCATION_RULES --task-name "Manage Tax Box Allocation Rules" --zip-file "<RUN>/pay/tb.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be absolute. Write down the ProcessId. Success: no `1 rows of them failed` line and `Tax Rule Result. Status: Completed successfully`. Dropped connection after the ProcessId: never import again; wait 2 minutes and do Step 5.
If only the header was created (result refused): do not send the header as a new row again. Build the result and detail rows alone against a NEW export, and add the header unchanged with `<GAPS>/common-features/manage-profile-options/scripts/copy_parent_rows.py --export-dir <new export>/unz --payload-dir pay2 --zip-name tb2.zip --file ZX_TAX_RULE_SUPERTYPE.csv --where TaxRuleCode=<CODE> --where TaxRegimeCode=<REGIME> --prefix <PREFIX>` (VERIFIED, batch 22 try 2).

## Step 5. Read back (VERIFIED)
Export again into `<RUN>/e2` (Step 1 with `e1` replaced by `e2`), then:
```bash
cd "<RUN>"; python -I "<H>/compare_fsm_exports.py" e1/unz e2/unz --key "ZX_TAX_RULE_SUPERTYPE.csv=TaxRuleCode,TaxRegimeCode,Tax" --key "ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv=ZX_TAX_RULE_SUPERTYPE.TaxRuleCode,ZX_TAX_RULE_SUPERTYPE.TaxRegimeCode,ZX_TAX_RULE_SUPERTYPE.Tax,Language" --key "ORA_ZX_TAX_RULE_RESULT.csv=TaxRuleCode,TaxRegimeCode,Tax,ConditionGroupCode" --key "ORA_TAX_RULE_RESULT_DETAILS.csv=ORA_ZX_TAX_RULE_RESULT.TaxRuleCode,ReportingTypeCodeNum" --expect "ZX_TAX_RULE_SUPERTYPE.csv=<CODE>,<REGIME>,<TAX>" --expect "ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv=<CODE>,<REGIME>,<TAX>,US" --expect "ORA_ZX_TAX_RULE_RESULT.csv=<CODE>,<REGIME>,<TAX>,<CSET>" --expect "ORA_TAX_RULE_RESULT_DETAILS.csv=<CODE>,<RTYPE>"
```
`RESULT: PASS` = only your 4 rows added, nothing removed or changed. The header shows `ServiceTypeCode DET_TAX_BOX`, `EnabledFlag N`, `ReportingTypeCode <RTYPE>`, `PeriodicityCode PERIODIC`.

## Rules and limits
1. Own regime, tax, reporting type and rule only; the rule header stays disabled (`EnabledFlag=N`).
2. Never import twice; an existing header goes in only unchanged, as a parent.
3. A legal-entity rule (which overrides the global one) and `ANNUAL` were not tested (GUESS).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Try 1 (4 rows, no AlphanumericResult) | ProcessId 100004743462568: header + translation created; result refused `ZX_REQUIRED_VALUE` (AlphanumericResult) |
| Try 2 (result + detail, own header unchanged) | ProcessId 100004744438453: completed successfully |
| Read back | `GAPFILL_AB_B22_TB1` on own regime/tax, reporting type `GAPFILL_AB_RT1`, box `GAPFILL_AB_C1`, PERIODIC, disabled: compare PASS (4 rows added, 0 changed) |
| Fresh test 1 | `GAPFILL_AB_B22_TB2F`: refused `ZX_RULES_ORDER_EXISTS_GCO_OWN` (rule order 10 already used by TB1), nothing created; rule-order step added |
| Re-test | see STATUS.md |
