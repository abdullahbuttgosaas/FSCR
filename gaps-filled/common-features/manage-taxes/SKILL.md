---
skill_id: "gosaas.gap-fills.common-features.manage-taxes"
name: "Manage Taxes (GoSaaS gap fill)"
description: "Create a new transaction tax under an existing tax regime through FSCR's setup-task CSV export and import (ZX_TAX package), copying the settings of an existing tax, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 1, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAXES"
task_name: "Manage Taxes"
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
  - "gosaas common-features/manage-profile-options/scripts/copy_parent_rows.py"
  - "ZX_MANAGE_TAX_REGIMES (the regime the tax belongs to must exist)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new tax (and re-sends its parent regime row unchanged). The tax is not live for processing. It may not be deletable; plan as if it stays."
---

# Manage Taxes (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A tax (for example a state sales tax or a VAT) belongs to one tax regime. It holds the tax currency, rounding, the geography it applies to, and many option flags. Statuses, rates, jurisdictions, formulas and rules hang below it. A tax does nothing on a transaction until it is **live for processing** (`LiveForProcessingFlag=Y`) or enabled for simulation (`S`), and its regime is subscribed. This skill creates the **tax only**, not live (`N`).

## When to use
- Someone asks to create a **new** tax for task `ZX_MANAGE_TAXES` under a regime that already exists.
- Do **not** use it to change existing taxes, to make a tax live, or to add regime subscriptions. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
P       = <GAPS>/common-features/manage-profile-options/scripts      (copy_parent_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix for the new tax, e.g. GAPFILL_<INITIALS>_
RPREFIX = the test prefix that REGIME starts with (for example GAPFILL_<INITIALS>_). It may be shorter than PREFIX. If REGIME has no test prefix (a real regime): stop and ask (Step 4).
REGIME  = TaxRegimeCode of the existing regime the new tax belongs to (the person names it; in a test, your own test regime)
TAX     = new Tax code: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME    = new TaxFullName (display name), e.g. "GAPFILL XX test tax 1" (no "|" character)
TEMPLATE= Tax code of one existing tax to copy settings from (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAXES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 23 files (VERIFIED, 77 to 93 s): `ZX_TAX.csv` (about 160 columns, one row per tax), `ZX_TAX_TRANSLATION.csv` (`ZX_TAX.Tax, ZX_TAX.TaxRegimeCode, ZX_TAX.ContentOwnerPartyNumber, ZX_TAX.ContentOwnerPartyTypeCode, ZX_TAX.BuName, Language, SourceLang, TaxFullName, ...`), the parent regime files `ZX_TAX_REGIME.csv` and `ZX_TAX_REGIME_TRANSLATION.csv`, subscription, jurisdiction, account and threshold files, and `ASM_SETUP_CSV_METADATA.xml`.
- **Network drops happen on tax exports** (no ZIP is written; `The read operation timed out` or `Remote end closed connection`). An export is read-only: run it again into a new folder, one export at a time, up to 3 tries. If it still fails or lacks these files: **stop**.

## Step 3. Choose a template tax and check the code
1. **List the regimes and taxes:**
   ```bash
   python -I -c "import csv,sys; [print(r['Tax'],'|',r['TaxRegimeCode'],'| owner',r['ContentOwnerPartyTypeCode'],r['BuName'] or '-','| live',r['LiveForProcessingFlag']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
   python -I -c "import csv,sys; [print(r['TaxRegimeCode'],'| from',r['EffectiveFrom']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_REGIME.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
   ```
   REGIME must be in the regime list; if not, **stop** (create it first with the gap skill `manage-tax-regimes`).
2. **TEMPLATE** = the **first listed** existing tax owned by the global configuration owner (`owner GCO -`) that is **not live** (`live N`) and whose code does not start with a test prefix (if none is not live, the first GCO tax). The new tax copies its currency, rounding, geography and option flags. VERIFIED
3. **TAX is free:** it must not be in the tax list for REGIME (the builder checks it again). There is **no REST resource** for taxes (`taxes`, `taxesLOV`, `transactionTaxesLOV`: HTTP 404, VERIFIED), so the export is the check.

## Step 4. Build a package with only the new tax (+ its parent regime rows, unchanged)
```bash
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX.csv \
  --match "Tax=<TEMPLATE>" --set "Tax=<TAX>" --set "TaxRegimeCode=<REGIME>" --set "TaxFullName=<NAME>" \
  --set "EffectiveFrom=<yyyy/mm/dd>" --set "LiveForProcessingFlag=N" \
  --clear EffectiveTo --clear DefaultTaxStatusCode --clear DefaultTaxRateCode --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_TRANSLATION.csv \
  --match "ZX_TAX.Tax=<TEMPLATE>" --match "Language=US" \
  --set "ZX_TAX.Tax=<TAX>" --set "ZX_TAX.TaxRegimeCode=<REGIME>" --set "TaxFullName=<NAME>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name tax_new.zip --prefix <PREFIX> \
  --key "ZX_TAX.csv=Tax,TaxRegimeCode" --key "ZX_TAX_TRANSLATION.csv=ZX_TAX.Tax,ZX_TAX.TaxRegimeCode,Language" \
  --prefix-col "ZX_TAX.csv=Tax" --max-len "Tax=30" @"<RUN>/rows.txt"
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name tax_new.zip --file ZX_TAX_REGIME.csv --where "TaxRegimeCode=<REGIME>" --prefix <RPREFIX>
python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name tax_new.zip --file ZX_TAX_REGIME_TRANSLATION.csv --where "ZX_TAX_REGIME.TaxRegimeCode=<REGIME>" --where "Language=US" --prefix <RPREFIX>
```
- `EffectiveFrom` must be on or after the regime's `EffectiveFrom` (printed by the regime list in Step 3; we used the regime's start date, `yyyy/mm/dd`). VERIFIED
- `DefaultTaxStatusCode` and `DefaultTaxRateCode` are cleared: a new tax has no status or rate yet. `LiveForProcessingFlag=N` keeps the tax out of every transaction. VERIFIED
- The builder must print `ZX_TAX.csv: 1 new rows`, `ZX_TAX_TRANSLATION.csv: 1 new rows` and every other file `0 new rows`; each `copy_parent_rows.py` must print `copied 1 parent row unchanged`. It stops if TAX exists, lacks the prefix or is too long.
- **The parent regime row is required in the ZIP** (hierarchical package; without a parent, FSM processes 0 rows). `copy_parent_rows.py --prefix <RPREFIX>` only copies **your own** test regime (give the regime's prefix, not the tax's longer PREFIX, or it stops with `does not start with`). If the person names a real (not test) regime: **stop** and ask; re-sending a real regime row was not tested.
- If the translation file has no `Language=US` row for the TEMPLATE, use the language your environment has.

## Step 5. Import
**Approval.** The person must approve the environment, the task, REGIME and the exact TAX before the import. If their brief names all of them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAXES --task-name "Manage Taxes" \
  --zip-file "<RUN>/payload/tax_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later; the ESS request number in Scheduled Processes does not open it.
- About 80 s. Print a short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TransactionTax. Status: Completed successfully ... A total of 1 rows were processed. 0 rows of them failed`, also `Detail Object: TaxRegime ... 1 rows ... 0 failed` (the parent row, re-sent unchanged), and `Total Objects Failed: 0`. **`0 rows were processed` is a failure** even when the status says "Completed successfully".
- **If the script loses the connection after the process started** (no process log), the import still runs in Oracle. **Do not import again.** Wait 2 minutes and do Step 6: if the tax is there, the import worked.
- Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX.csv=Tax,TaxRegimeCode" --key "ZX_TAX_TRANSLATION.csv=ZX_TAX.Tax,ZX_TAX.TaxRegimeCode,Language" \
  --key "ZX_TAX_REGIME.csv=TaxRegimeCode" --key "ZX_TAX_REGIME_TRANSLATION.csv=ZX_TAX_REGIME.TaxRegimeCode,Language" \
  --expect "ZX_TAX.csv=<TAX>,<REGIME>" --expect "ZX_TAX_TRANSLATION.csv=<TAX>,<REGIME>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your tax and its translation were added; the regime and every subscription file are unchanged. If someone else changed taxes between your two exports, extra rows appear: judge your own rows (added) plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 23 files, metadata XML unchanged; only the tax, its translation and the unchanged parent regime rows go in.
3. **Never make the tax live** (`Y`) or enabled for simulation (`S`) in a test, and never add a subscription. Both change real tax results and need the person's explicit approval.
4. Test records may stay for good. This skill never deletes. Record every created tax.
5. **Children of a new tax:** a tax formula on the new tax imported fine (gap skill `manage-tax-formulas`). A **tax status** on it was **rejected** (`ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute`, see `manage-tax-statuses`): statuses seem to need a live or simulation tax on a subscribed regime. GUESS
6. Not tested: taxes owned by a business unit (`OU`) or legal entity, withholding taxes, offset taxes, tax accounts, thresholds.
7. Tested on one environment (release 11.13.26.10.0).
8. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `template_row.py`, `build_fsm_package.py`, `copy_parent_rows.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 9 taxes, 15 regimes; 93 s |
| Template | an existing GCO tax that is not live |
| New record | `GAPFILL_AB_P1_TX1`, "GAPFILL AB P1 tax 1", regime `GAPFILL_AB_TR1` (test regime, no subscription), from 2026/01/01, not live |
| Import | 1 attempt, 78 s: TransactionTax 1 row, 0 failed; parent TaxRegime 1 row, 0 failed |
| Export after + compare | 10 taxes; added 1 + 1, removed 0, changed 0; regime and all subscription files unchanged: PASS |
