---
skill_id: "gosaas.gap-fills.common-features.manage-application-tax-options"
name: "Manage Application Tax Options: add tax options for one business unit and application by FSM CSV (GoSaaS gap fill)"
description: "Adds the application tax options (defaulting order for tax classification codes, rounding, inclusive tax, exemptions) of ONE business unit for ONE application (ZX_APPLICATION_TAX_OPTIONS) by FSM CSV import. The task export never shows these rows (VERIFIED: 0 rows before and after), so the read-back is Oracle's own uniqueness check. Tested on a test business unit made for the test. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 15, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_APPLICATION_TAX_OPTIONS"
task_name: "Manage Application Tax Options"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/test-business-unit (for a test)"
side_effects:
  - "Step 3 adds the tax options of the business unit for that application: tax defaulting and rounding on that business unit's transactions of that application."
---

# Manage Application Tax Options (GoSaaS gap fill)

> **STATUS: FAILED (2026-11-26). Do not use this skill to load real options.** The fresh test proved that the import does not tie the row to the business unit named in `Name`: a brand-new business unit (`GAPFILL_AB_B15_BU2F`, ProcessId 100004743432577) and a business unit name that does not exist (`GAPFILL_AB_B15_NOSUCHBU`, ProcessId 100004744415341) are both refused with `ZX_APPL_OU_UNIQUE`. So the first load (try 1 below) most likely stored a row whose business unit Oracle did not resolve, and every later AP row collides with it. The refusal in Step 4 is therefore **not** proof. Open questions: which column Oracle uses to find the business unit (the export has `EnterpriseId`, `EventClassCode`, `EntityCode` too) and whether the try-1 row is visible on the page (check Manage Application Tax Options in the page for application AP). Next step: look on the page, then retry with the identifier column Oracle expects.

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
Application tax options hold, for one **business unit** and one **application** (Payables `AP`, Receivables `AR`, Purchasing, ...), the order in which a tax classification code is defaulted on transaction lines (`DefOptionHier1Code` to `DefOptionHier7Code`), rounding, precision, inclusive tax and exemption handling. One row per business unit and application: Oracle refuses a second one with `ZX_APPL_OU_UNIQUE` (VERIFIED).
Use it to set those options for a business unit. **For a test**, use your own test business unit: a row for a real business unit changes its real transactions.
**Read-back limit (VERIFIED):** the task's export does not show these rows, not even a row that exists (0 rows before and after a successful load). There is no REST resource (`applicationTaxOptions`, `taxApplicationOptions`: HTTP 404). Proof is Step 4.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py   (offline builder, new rows only)
W     = <GAPS>/common-features/scripts/rest_call.py   (FSCR's REST client, readable errors)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
BU    = the business unit name (for a test: your own, starting with PREFIX)
APP   = application short name, e.g. AP
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. The business unit exists and has **no** tax options for APP yet. **For a test:** make a NEW business unit with `<GAPS>/common-features/test-business-unit/SKILL.md` (a new one is the only way to be sure it has no options, because the export cannot show them). Use each test business unit for one test per application.
2. The defaulting codes of APP, read live (Step 2).

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ZX_MANAGE_APPLICATION_TAX_OPTIONS --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
```
1 CSV `ZX_APPLICATION_TAX_OPTIONS.csv` (header only, VERIFIED) + metadata: it gives the layout. Key columns: `Name` (business unit name), `ApplicationShortName`. No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Read the defaulting codes (read only, VERIFIED for AP)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/ZX_AP_DEFAULT_HIERARCHY/child/lookupCodes" --query onlyData=true --query fields=LookupCode,Meaning,EnabledFlag --no-open-browser --output hier.json > hier.log 2>&1
python -I -c "import json; print([(i['LookupCode'],i['Meaning']) for i in json.load(open('hier.json',encoding='utf-8'))['items']])"
```
AP codes (VERIFIED): `REFERENCE_DOCUMENT`, `SHIP_FROM_PARTY_SITE`, `SHIP_FROM_PARTY`, `NATURAL_ACCOUNT`, `FINANCIAL_OPTIONS`, `INVOICE_HEADER`, `TEMPLATE`. Other applications: `ZX_AR_DEFAULT_HIERARCHY`, `ZX_PO_DEFAULT_HIERARCHY`, `ZX_PA_DEFAULT_HIERARCHY` (GUESS that they work the same). A GET timeout is safe to repeat.

## Step 3. Build and import (VERIFIED for AP)
```bash
cd "<RUN>"; python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name ato.zip --prefix <PREFIX> \
 --key "ZX_APPLICATION_TAX_OPTIONS.csv=Name,ApplicationShortName" --prefix-col "ZX_APPLICATION_TAX_OPTIONS.csv=Name" \
 --row "ZX_APPLICATION_TAX_OPTIONS.csv|Name=<BU>|ApplicationShortName=AP|DefOptionHier1Code=REFERENCE_DOCUMENT|DefOptionHier2Code=SHIP_FROM_PARTY_SITE|DefOptionHier3Code=SHIP_FROM_PARTY|DefOptionHier4Code=NATURAL_ACCOUNT|DefOptionHier5Code=FINANCIAL_OPTIONS|InclusiveTaxUsedFlag=N|TaxUseCustomerExemptFlag=N|TaxUseProductExemptFlag=N|TaxUseLocExcRateFlag=N|TaxAllowCompoundFlag=N|TaxRoundingRule=NEAREST|TaxPrecision=2|UseTaxClassificationFlag=N|AllowTaxRoundingOvrdFlag=N|HomeCountryDefaultFlag=N|RecordTypeCode=USER_DEFINED"
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ZX_MANAGE_APPLICATION_TAX_OPTIONS --task-name "Manage Application Tax Options" --zip-file "<RUN>/pay/ato.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed`, `Application Tax Option. Status: Completed successfully`. (The defaulting order is optional for Oracle: a row without it also loads, VERIFIED; give it, because it is the point of the task.) Print only the grep lines: the log holds the environment name and user. Dropped connection: never import again blind; first do Step 4's check.

## Step 4. Read back (VERIFIED)
1. Export again (Step 1 with `exp2`): the file stays at 0 rows. That is expected and is **not** proof.
2. Proof: send the **same** package once more. Oracle must refuse it with `ZX_APPL_OU_UNIQUE` ("Tax options for this combination of business unit and application already exist") and `1 rows of them failed`. The refusal creates and changes nothing. Any other result: stop and report.
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ZX_MANAGE_APPLICATION_TAX_OPTIONS --task-name "Manage Application Tax Options" --zip-file "<RUN>/pay/ato.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp_check" > "<RUN>/imp_check.log" 2>&1
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Message Code: [A-Z_0-9]+" "<RUN>"/imp_check/*_process_log.txt | sort -u
```
Only for a business unit that had no options before Step 3 (a new test business unit) does this prove that Step 3 made the row.

## Rules and limits
1. One row per business unit and application; a test uses only your own new test business unit.
2. No delete and no visible read-back through CSV or REST; the page shows the options (screen not used here).
3. Tested on one environment (release 11.13.26.10.0), application AP.

## Worked example (2026-11-26, codes and ProcessIds only)
| Try | Result |
|---|---|
| 1 | `GAPFILL_AB_B15_BU1` (new, no options), AP, without defaulting order: ProcessId 100004744413261, 1 processed, 0 failed; export still 0 rows |
| 2 | same business unit and AP, with the defaulting order: ProcessId 100004743431825, refused `ZX_APPL_OU_UNIQUE`: proves try 1 created the row; nothing changed |
| fresh | new `GAPFILL_AB_B15_BU2F` (100004744412883), AP: ProcessId 100004743432577, refused `ZX_APPL_OU_UNIQUE` |
| probe | name that does not exist, AP: ProcessId 100004744415341, refused `ZX_APPL_OU_UNIQUE`: the name is not what Oracle checks; test FAILED |
