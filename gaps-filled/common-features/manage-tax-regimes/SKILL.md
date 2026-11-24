---
skill_id: "gosaas.gap-fills.common-features.manage-tax-regimes"
name: "Manage Tax Regimes (GoSaaS gap fill)"
description: "Create a new transaction tax regime (header + translation, no subscription, no taxes) through FSCR's setup-task CSV export and import, copying the settings of one existing regime, then read it back by REST (taxRegimesLOV) and a second export. Step 7 adds the global configuration owner option row to a regime, the prerequisite for tax statuses, rates and rules. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 3, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_REGIMES"
task_name: "Manage Tax Regimes"
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
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new tax regime. With no subscription and no taxes it calculates nothing. It may not be deletable; plan as if it stays."
---

# Manage Tax Regimes (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file. It uses the generic helpers of the gap skill `manage-docseq-categories` and `scripts/template_row.py` in this folder.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A tax regime is the root of the transaction tax set-up: the set of tax rules of one country (or a group of countries) that share one tax authority. Taxes, statuses, rates, jurisdictions, reporting types and rules hang below it. A regime does nothing until it is **subscribed** by a business unit, legal entity or the global configuration owner, and has taxes. This skill creates the **regime header only** (with its translation row). A subscription changes how real transactions are taxed, so it is not part of the test.

## When to use
- Someone asks to create a **new** tax regime for task `ZX_MANAGE_TAX_REGIMES`.
- Do **not** use it to change existing regimes, subscriptions or usages. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T       = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
P       = <GAPS>/common-features/manage-profile-options/scripts      (copy_parent_rows.py, Step 7 only)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE    = new TaxRegimeCode: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME    = new TaxRegimeName (display name), e.g. "GAPFILL XX test regime 1" (no "|" character)
TEMPLATE= TaxRegimeCode of one existing regime to copy settings from (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder such as `E:\e\...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads (an expired token makes them hang silently). Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_REGIMES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 10 files (VERIFIED, 1 to 4 minutes): `ZX_TAX_REGIME.csv` (95 columns, one row per regime), `ZX_TAX_REGIME_TRANSLATION.csv` (`ZX_TAX_REGIME.TaxRegimeCode, CreatedBy, CreationDate, Language, LastUpdateDate, LastUpdateLogin, LastUpdatedBy, SourceLang, TaxRegimeName`), the subscription and usage files `ZX_TAX_REGIME_SUBSCRIPTION.csv`, `ZX_BU_REGIME_SUBSCRIPTION.csv`, `ORA_ZX_BU_REGIME_USAGE.csv`, `ORA_ZX_BU_REGIME_SUB_DETAIL.csv`, `ORA_ZX_BU_GCO_TAX_SUB.csv`, `ORA_ZX_BU_REGIME_TAX_PROFILE.csv`, `ORA_ZX_SERVICE_SUBSCRIPTION_EXCLUSION.csv`, and `ASM_SETUP_CSV_METADATA.xml`.
- **Network drops are common on tax exports** (`The read operation timed out`, `Remote end closed connection without response`): no ZIP is written. An export is read-only, so just run it again (into a new folder), one export at a time. VERIFIED
- If it still has no ZIP after 3 tries or lacks these files: **stop**.

## Step 3. Choose a template regime and check the code
1. **List the regimes** (code, country, parent, sub-regime flag, start date):
   ```bash
   python -I -c "import csv,sys; [print(r['TaxRegimeCode'],'|',r['CountryOrGroupCode'],r['CountryCode'],'| parent',r['ParentRegimeCode'] or '-','| sub',r['HasSubRegimeFlag'],'| from',r['EffectiveFrom']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_REGIME.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
   ```
2. **TEMPLATE** = one existing regime of the country the person wants (if they name no country, take the first listed regime that meets the rest of this rule; for a test the country does not matter because nothing subscribes to the new regime) with `CountryOrGroupCode=COUNTRY`, no parent (`-`) and `sub N`. Prefer one whose code does **not** start with a test prefix. The new regime copies its tax currency, rounding, precision and option flags; a subscription is never copied (it lives in other files). VERIFIED
3. **Code is free** (REST):
   ```bash
   timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource taxRegimesLOV --q "TaxRegimeCode='<CODE>'" \
     --fields TaxRegimeCode --out "<RUN>/readback_before.json" --expect-absent
   ```
   Want `0 row(s)`, `READBACK: PASS`. Exit 2 = sign-in or privilege problem, not "absent". (`taxRegimes` gives HTTP 404; use `taxRegimesLOV`. VERIFIED)

## Step 4. Build a package with only the new regime
```bash
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_REGIME.csv \
  --match "TaxRegimeCode=<TEMPLATE>" --set "TaxRegimeCode=<CODE>" --set "TaxRegimeName=<NAME>" \
  --set "EffectiveFrom=<yyyy/mm/dd>" --clear EffectiveTo --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_REGIME_TRANSLATION.csv \
  --match "ZX_TAX_REGIME.TaxRegimeCode=<TEMPLATE>" --match "Language=US" \
  --set "ZX_TAX_REGIME.TaxRegimeCode=<CODE>" --set "TaxRegimeName=<NAME>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name regime_new.zip --prefix <PREFIX> \
  --key "ZX_TAX_REGIME.csv=TaxRegimeCode" --key "ZX_TAX_REGIME_TRANSLATION.csv=ZX_TAX_REGIME.TaxRegimeCode,Language" \
  --prefix-col "ZX_TAX_REGIME.csv=TaxRegimeCode" --max-len "TaxRegimeCode=30" @"<RUN>/rows.txt"
```
- `template_row.py` copies every filled column of the TEMPLATE row, empties the audit columns, applies `--set`/`--clear`, and prints only column names (no values).
- `EffectiveFrom`: the first day the regime is valid, `yyyy/mm/dd` (we used the first day of the current year). VERIFIED
- The builder must print `ZX_TAX_REGIME.csv: 1 new rows`, `ZX_TAX_REGIME_TRANSLATION.csv: 1 new rows`, every other file `0 new rows`. It stops if CODE already exists in the export (importing it would **update** that regime), lacks the prefix, or is too long.
- If the translation file has no `Language=US` row for the TEMPLATE, use the language your environment has (look at the file).

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact CODE before the import. If their brief names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_REGIMES --task-name "Manage Tax Regimes" \
  --zip-file "<RUN>/payload/regime_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- The result is in `<RUN>/import_result/*_process_log.txt` (one long line with literal `\r\n`, `\t`, `\/`; it repeats the same detail lines many times). Print a short summary (detail objects that processed rows, error texts, totals):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [1-9][0-9]* rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TaxRegime. Status: Completed successfully. ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0`. The regime row is reported as detail object `TaxRegime` under another business object's name (for example a subscription object); the "Tax Regime" object line itself may only say "already processed". That is normal. **`0 rows were processed` is a failure** even when the status says "Completed successfully". A row can validate and still fail at the database insert (`JBO-26041`, seen on another tax task): always read the object status and `Total Objects Failed`.
- **If the script loses the connection after `Started setup task CSV import process: <id>`** (no process log), the import still runs in Oracle. **Do not import again.** Wait 1 to 2 minutes and do Step 6 A: if the regime is there, the import worked. VERIFIED (our live import ran this way)
- Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back two ways
**A. REST:**
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource taxRegimesLOV --q "TaxRegimeCode='<CODE>'" \
  --fields TaxRegimeCode,TaxRegimeName --out "<RUN>/readback_after.json" --expect "TaxRegimeCode=<CODE>" --expect-count 1
```
`READBACK: PASS` = exactly one regime with your code. VERIFIED

**B. Second export and compare:** repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX_REGIME.csv=TaxRegimeCode" --key "ZX_TAX_REGIME_TRANSLATION.csv=ZX_TAX_REGIME.TaxRegimeCode,Language" \
  --expect "ZX_TAX_REGIME.csv=<CODE>" --expect "ZX_TAX_REGIME_TRANSLATION.csv=<CODE>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your regime and its translation were added, nothing removed or changed, and no subscription or usage file changed. If someone else changed regimes between your two exports, extra rows appear: judge your own rows (added) plus `removed 0` and `changed 0`, and report the extras.

## Step 7 (only when asked). Prerequisite for tax statuses, rates and rules: the global configuration owner (GCO) option
Oracle refuses **tax statuses, tax rates and tax rules** owned by the global configuration owner on a tax whose regime has **no GCO configuration option row** (status import: `ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute`; rule import: `ZX_RECRATE_DATE_INVALID ... {TAX_START_DATE} to {TAX_END_DATE}` with empty placeholders). A new regime made by Steps 1 to 6 has no such row. VERIFIED. Do this step when the person asks for it, or when a statuses/rates/rules skill sends you here.

Extra placeholder: `REGIME` = the TaxRegimeCode that needs the row (your own test regime in a test). `REGIME` must already exist and must **not** be listed in `ORA_ZX_BU_GCO_TAX_SUB.csv` yet.
1. **Export** as in Step 2, into a new `RUN`, with `--output-dir "<RUN>/export_before"`, and unzip to `<RUN>/export_before/unz`. List the regimes that have the GCO row, and the start date of REGIME:
   ```bash
   python -I -c "import csv,sys; [print(r['TaxRegimeCode'],'| org',r['FirstPtyOrgId'],'| view',r['ViewOptionsCode'],'| from',r['EffectiveFrom']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_BU_GCO_TAX_SUB.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
   python -I -c "import csv,sys; [print(r['TaxRegimeCode'],'| from',r['EffectiveFrom']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_REGIME.csv',encoding='utf-8-sig')) if r['TaxRegimeCode']==sys.argv[2]]" "<RUN>/export_before/unz" "<REGIME>"
   ```
   If REGIME is already in the first list: nothing to do, stop here. `GCOTEMPLATE` = the first listed regime of the first list (any one works: the row holds no regime-specific value; `FirstPtyOrgId`/`ParentFirstPtyOrgId` are `-99`, Oracle's fixed id of the global configuration owner, and `SubscriptionOptionId` is `0`). If the list is empty: **stop** (not tested).
2. **Build** (the row copied from GCOTEMPLATE, never typed in; the parent regime rows copied unchanged):
   ```bash
   python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_BU_GCO_TAX_SUB.csv \
     --match "TaxRegimeCode=<GCOTEMPLATE>" --set "ZX_TAX_REGIME.TaxRegimeCode=<REGIME>" --set "TaxRegimeCode=<REGIME>" \
     --set "EffectiveFrom=<REGIME start, yyyy/mm/dd>" --clear EffectiveTo --out "<RUN>/rows_gco.txt"
   python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
     --zip-name regime_gco_sub.zip --prefix <PREFIX> \
     --key "ORA_ZX_BU_GCO_TAX_SUB.csv=TaxRegimeCode,FirstPtyOrgId" --prefix-col "ORA_ZX_BU_GCO_TAX_SUB.csv=TaxRegimeCode" @"<RUN>/rows_gco.txt"
   python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
     --zip-name regime_gco_sub.zip --file ZX_TAX_REGIME.csv --where "TaxRegimeCode=<REGIME>" --prefix <PREFIX>
   python -I "<P>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
     --zip-name regime_gco_sub.zip --file ZX_TAX_REGIME_TRANSLATION.csv --where "ZX_TAX_REGIME.TaxRegimeCode=<REGIME>" --where "Language=US" --prefix <PREFIX>
   ```
   with `P = <GAPS>/common-features/manage-profile-options/scripts`. Here PREFIX is the test prefix REGIME starts with. The builder must print `ORA_ZX_BU_GCO_TAX_SUB.csv: 1 new rows` and 0 for the rest; each copy must print `copied 1 parent row unchanged`.
3. **Import** as in Step 5 with `--zip-file "<RUN>/payload/regime_gco_sub.zip"` and its own `--output-dir`. Write down the ProcessId. Success (VERIFIED): business object `Business Unit GCO Tax Subscription ... Completed successfully`, `Detail Object: TaxRegime ... 1 rows ... 0 failed` (the parent), `Total Objects Failed: 0`. The GCO row itself gets **no** detail line, so only Step 7.4 proves it. The Step 5 one-liner does not show business object lines; print them with:
   ```bash
   python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)); print(chr(10).join(sorted(set(re.findall(r'Business object: Business Unit GCO Tax Subscription\. Status: [^.]+',t)))))" "<RUN>/import_result"
   ```
   Quote every `--match`/`--where` value: regime codes can hold spaces.
4. **Read back:** export again (Step 2 with `--output-dir "<RUN>/export_after"`, unzip to `<RUN>/export_after/unz`), then
   ```bash
   python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
     --key "ORA_ZX_BU_GCO_TAX_SUB.csv=TaxRegimeCode,FirstPtyOrgId" --key "ZX_TAX_REGIME.csv=TaxRegimeCode" \
     --expect "ORA_ZX_BU_GCO_TAX_SUB.csv=<REGIME>,-99" --rows-out "<RUN>/added_rows.csv"
   ```
   `RESULT: PASS` = exactly that one row added, nothing removed or changed.
- **Effect:** the regime's content (taxes, statuses, rates, rules) becomes visible to the global configuration owner. It does **not** make any tax live and adds **no** business unit or legal entity subscription, so no transaction is taxed differently while the regime's taxes are not live (`N`). VERIFIED (2026-11-24: status, rate and disabled rule then imported on a not-live test tax; the regime also had a test business-unit subscription at that time).

## Rules and limits
1. New records only; never import a full export.
2. Keep all 10 files, metadata XML unchanged; every file except the regime and its translation stays header-only (Step 7: only the GCO row and the unchanged parent rows).
3. **No business-unit or legal-entity subscription or usage in a test.** That makes the regime apply to real transactions. It is **not** part of this skill and needs the person's explicit approval. The GCO option of Step 7 is allowed when asked (see its "Effect").
4. Test records may stay for good. This skill never deletes. Record every created regime.
5. Not tested: regimes for a country group, parent/sub-regimes, tax reporting configuration, regimes without a template.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for `template_row.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 12 regimes; several tries (network drops) |
| Template | an existing country regime with no parent; settings copied |
| New record | `GAPFILL_AB_TR1`, name "GAPFILL AB test regime 1", from 2026/01/01, no subscription |
| Import | 1 attempt; the script lost the connection after the process started; REST showed the regime 1 minute later |
| REST read-back | 1 row, code and name match: PASS |
| Export after + compare | 13 regimes, 13 translations; added 1 + 1, removed 0, changed 0; all 7 subscription and usage files unchanged: PASS |
