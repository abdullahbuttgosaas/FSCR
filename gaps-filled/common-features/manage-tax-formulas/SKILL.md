---
skill_id: "gosaas.gap-fills.common-features.manage-tax-formulas"
name: "Manage Tax Formulas (GoSaaS gap fill)"
description: "Create a new taxable-basis tax formula for an existing tax through FSCR's setup-task CSV export and import (ZX_TAX_FORMULA package), then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 1, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_TAX_FORMULAS"
task_name: "Manage Tax Formulas"
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
  - "ZX_MANAGE_TAXES (the tax and its regime must exist)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new tax formula. No tax rule points to it, so it changes no tax result. It may not be deletable; plan as if it stays."
---

# Manage Tax Formulas (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A tax formula says how a tax is calculated. A **taxable basis** formula (`FormulaTypeCode=TAXABLE_BASIS`) says what amount the rate is applied to (for example the line amount) and whether discounts and charges count. A tax uses a formula only when the tax's default formula or a tax rule points to it. This skill creates a **taxable basis formula** for one tax and points nothing to it.

## When to use
- Someone asks to create a **new** tax formula for task `ORA_ZX_MANAGE_TAX_FORMULAS`.
- Do **not** use it to change existing formulas, to make a tax use the formula, or to create tax calculation (`TAX_CALCULATION`) formulas (not tested). New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
REGIME  = TaxRegimeCode of the tax (the person names it; in a test, your own test regime)
TAX     = Tax code of an existing tax of REGIME (in a test, your own test tax)
CODE    = new FormulaCode: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME    = new FormulaName (display name), e.g. "GAPFILL XX test formula 1" (no "|" character)
FROM    = EffectiveFrom, yyyy/mm/dd, on or after the tax's EffectiveFrom (we used the tax's start date)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_TAX_FORMULAS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; [print(r['FormulaCode'],'|',r['TaxRegimeCode'],'|',r['Tax'],'|',r['FormulaTypeCode']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_FORMULA.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
Expect 19 files (VERIFIED, 81 to 99 s): `ZX_TAX_FORMULA.csv` (59 columns), `ZX_TAX_FORMULA_TRANSLATION.csv` (`ZX_TAX_FORMULA.EffectiveFrom, ZX_TAX_FORMULA.FormulaCode, ZX_TAX_FORMULA.TaxRegimeCode, ZX_TAX_FORMULA.EnabledFlag, ZX_TAX_FORMULA.ContentOwnerPartyTypeCode, ZX_TAX_FORMULA.ContentOwnerPartyNumber, ..., FormulaDescription, FormulaName, Language, ..., SourceLang`), formula detail and quick-rule files, the tax rule files, and `ASM_SETUP_CSV_METADATA.xml`. The environment may have **no formula at all** (ours had none), so this skill writes the rows in full instead of copying one.
- **Network drops happen on tax exports** (no ZIP is written). An export is read-only: run it again into a new folder, one at a time, up to 3 tries. If it still fails or lacks these files: **stop**.
- **The tax must exist:** check it in the `ZX_MANAGE_TAXES` export (see `../manage-taxes/SKILL.md` Step 3). There is no REST resource for taxes or formulas (`taxFormulasLOV`: HTTP 404, VERIFIED). CODE must not be in the formula list above (the builder checks it again).

## Step 3. Build a package with only the new formula
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name formula_new.zip --prefix <PREFIX> \
  --key "ZX_TAX_FORMULA.csv=FormulaCode,TaxRegimeCode" \
  --key "ZX_TAX_FORMULA_TRANSLATION.csv=ZX_TAX_FORMULA.FormulaCode,ZX_TAX_FORMULA.TaxRegimeCode,Language" \
  --prefix-col "ZX_TAX_FORMULA.csv=FormulaCode" --max-len "FormulaCode=30" \
  --row "ZX_TAX_FORMULA.csv|EffectiveFrom=<FROM>|FormulaCode=<CODE>|TaxRegimeCode=<REGIME>|Tax=<TAX>|EnabledFlag=Y|ContentOwnerPartyTypeCode=GCO|FormulaTypeCode=TAXABLE_BASIS|TaxableBasisTypeCode=LINE_AMOUNT|CashDiscountApplFlag=N|VolumeDiscountApplFlag=N|TradingDiscountApplFlag=N|TransportChargeApplFlag=N|TransferChargeApplFlag=N|InsuranceChargeApplFlag=N|OtherChargeApplFlag=N|PackingChargeApplFlag=N|RecordTypeCode=USER_DEFINED|FormulaName=<NAME>|RegimeTypeFlag=I" \
  --row "ZX_TAX_FORMULA_TRANSLATION.csv|ZX_TAX_FORMULA.EffectiveFrom=<FROM>|ZX_TAX_FORMULA.FormulaCode=<CODE>|ZX_TAX_FORMULA.TaxRegimeCode=<REGIME>|ZX_TAX_FORMULA.EnabledFlag=Y|ZX_TAX_FORMULA.ContentOwnerPartyTypeCode=GCO|FormulaName=<NAME>|Language=US|SourceLang=US"
```
- The builder must print `ZX_TAX_FORMULA.csv: 1 new rows`, `ZX_TAX_FORMULA_TRANSLATION.csv: 1 new rows`, every other file `0 new rows`. It stops if CODE exists, lacks the prefix or is too long.
- `ContentOwnerPartyTypeCode=GCO` makes the global configuration owner the owner (Oracle filled `ContentOwnerPartyId=-99` itself; never type an ID). Use it for a tax owned by GCO. VERIFIED. For a tax owned by a business unit: not tested.
- `TaxableBasisTypeCode=LINE_AMOUNT` (rate applied to the line amount) and all `...ApplFlag=N` (no discount or charge changes the basis) are VERIFIED. Other basis types (for example `QUANTITY`, `ASSESSABLE_VALUE`, `PRIOR_TAX`) are GUESS, not tested.
- Leave the audit columns, `EffectiveTo`, the attribute columns and every other file empty.

## Step 4. Import
**Approval.** The person must approve the environment, the task, TAX and the exact CODE before the import. If their brief names all of them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_TAX_FORMULAS --task-name "Manage Tax Formulas" \
  --zip-file "<RUN>/payload/formula_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`); it is the only key to the full process log later.
- About 30 s. Print a short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TaxFormula. Status: Completed successfully ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0`. **`0 rows were processed` is a failure** even when the status says "Completed successfully".
- **If the script loses the connection after the process started** (no process log), the import still runs in Oracle. **Do not import again.** Wait 2 minutes and do Step 5: if the formula is there, the import worked.
- Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 5. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX_FORMULA.csv=FormulaCode,TaxRegimeCode" \
  --key "ZX_TAX_FORMULA_TRANSLATION.csv=ZX_TAX_FORMULA.FormulaCode,ZX_TAX_FORMULA.TaxRegimeCode,Language" \
  --expect "ZX_TAX_FORMULA.csv=<CODE>,<REGIME>" --expect "ZX_TAX_FORMULA_TRANSLATION.csv=<CODE>,<REGIME>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your formula and its translation were added; no rule file changed. If someone else added formulas between your two exports, extra rows appear: judge your own rows (added) plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 19 files, metadata XML unchanged; only the formula and its translation get rows.
3. **Do not point a tax or a rule to the formula in a test.** That changes how the tax is calculated and needs the person's explicit approval.
4. Test records may stay for good. This skill never deletes. Record every created formula.
5. Not tested: tax calculation formulas, formula details (`ORA_ZX_TAX_FORMULA_DET.csv`), compounding, formulas owned by a business unit, formulas without a tax.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 0 formulas; 81 s |
| New record | `GAPFILL_AB_P1_FM1`, "GAPFILL AB P1 formula 1", taxable basis, line amount, for test tax `GAPFILL_AB_P1_TX1` of test regime `GAPFILL_AB_TR1`, from 2026/01/01 |
| Import | 1 attempt, 29 s: TaxFormula 1 row, 0 failed |
| Export after + compare | 1 formula, 1 translation; added 1 + 1, removed 0, changed 0; rule files unchanged: PASS |
