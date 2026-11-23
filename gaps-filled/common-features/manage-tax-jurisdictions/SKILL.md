---
skill_id: "gosaas.gap-fills.common-features.manage-tax-jurisdictions"
name: "Manage Tax Jurisdictions (GoSaaS gap fill)"
description: "Create a new tax jurisdiction (one geography, for example a state) for an existing tax through FSCR's setup-task CSV export and import (ZX_JURISDICTION package), then read it back with an export of the taxes package. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 2, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_JURISDICTIONS"
task_name: "Manage Tax Jurisdictions"
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
  - "Starts one setup-task CSV import that creates one new tax jurisdiction. On a tax that is not live, no transaction uses it. It may not be deletable; plan as if it stays."
---

# Manage Tax Jurisdictions (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax jurisdiction ties a tax to one geography (for example the state of New York for a state sales tax). Rates can then be set per jurisdiction. The jurisdiction's geography type is normally the tax's **zone geography type** (`ZoneGeographyType` of the tax, for example `STATE`). This skill creates **one jurisdiction** for one tax.

## When to use
- Someone asks to create a **new** tax jurisdiction for task `ZX_MANAGE_TAX_JURISDICTIONS` for a tax that already exists.
- Do **not** use it to change existing jurisdictions, to add jurisdiction rates, tax accounts or thresholds. New records only.

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
CODE    = new TaxJurisdictionCode: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME    = new TaxJurisdictionName, e.g. "GAPFILL XX test jurisdiction 1" (no "|" character)
FROM    = EffectiveFrom, yyyy/mm/dd, on or after the tax's EffectiveFrom (we used the tax's start date)
STATE   = the geography (here a US state), written exactly as the environment writes it in existing jurisdictions (Step 3); names only, never an ID
PREC    = PrecedenceLevel, unique among TAX's own jurisdictions (Step 3.4)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...` and never `$PWD`, which gives `/e/...`: FSCR then writes to a wrong folder such as `E:\e\...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Two read-only exports
The jurisdictions package is the one you **import** into, but its export lists **no** jurisdictions (VERIFIED: 0 rows, although the environment had 5). Existing jurisdictions and your new one show up in the **taxes** package (`ORA_ZX_TRAN_TAX_JURISDICTION.csv`), so export both:
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_JURISDICTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/jur_export"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAXES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/tax_before"
python -I -c "import sys,zipfile,glob; [zipfile.ZipFile(glob.glob(d+'/*.zip')[0]).extractall(d+'/unz') for d in sys.argv[1:]]" "<RUN>/jur_export" "<RUN>/tax_before"
```
- Jurisdictions export (VERIFIED, 44 to 68 s): 5 files: `ZX_JURISDICTION.csv` (69 columns), `ZX_JURISDICTION_TRANSLATION.csv` (`ZX_JURISDICTION.TaxJurisdictionCode, ZX_JURISDICTION.TaxRegimeCode, ZX_JURISDICTION.Tax, ..., Language, ..., SourceLang, TaxJurisdictionName`), tax account and threshold files, `ASM_SETUP_CSV_METADATA.xml`.
- Taxes export (VERIFIED, 76 to 107 s): 23 files including `ZX_TAX.csv` and `ORA_ZX_TRAN_TAX_JURISDICTION.csv` (+ translation).
- Network drops happen on tax exports (no ZIP is written). An export is read-only: run it again into a new folder, one at a time, up to 3 tries. If it still fails or lacks these files: **stop**.

## Step 3. Check the tax and choose the geography
```bash
python -I -c "import csv,sys; [print(r['Tax'],'|',r['TaxRegimeCode'],'| from',r['EffectiveFrom'],'| zone type',r['ZoneGeographyType'],'| country',r['CountryCode'],'| live',r['LiveForProcessingFlag']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX.csv',encoding='utf-8-sig'))]" "<RUN>/tax_before/unz"
python -I -c "import csv,sys; [print(r['TaxJurisdictionCode'],'|',r['TaxRegimeCode'],'|',r['Tax'],'| prec',r['PrecedenceLevel'],'|',r['GeographyType'],'| code',r['GeographyCode'] or '-','| name',r['GeographyName'],'| el1',r['GeographyElement1'],'| el2',r['GeographyElement2'] or '-') for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TRAN_TAX_JURISDICTION.csv',encoding='utf-8-sig'))]" "<RUN>/tax_before/unz"
```
1. TAX of REGIME must be in the first list; if not, **stop** (create it with the gap skill `manage-taxes`). Note its `from` date and `zone type`.
2. **Geography (the important part).** Find an existing jurisdiction (second list) whose `GeographyType` is the tax's zone type, and write your geography **the same way**: the same columns filled and the same naming style. Ours, for type `STATE`: `GeographyCode` empty, `GeographyName` = the state as a 2-letter code (`NY`), `GeographyElement1` = the country name (`United States`), `GeographyElement2` = the state again (`NY`). VERIFIED. (The precedence level is chosen in point 4.) Change only the state (to one that exists in the environment) and keep the rest of the style.
   - **Wrong style = nothing created:** with `GeographyName=New York` (full name) the import said `Geography 'null' has to be imported prior to import of this Tax Jurisdiction BO`, and with `GeographyCode=NY` added it said `Geography 'NY' has to be imported ...`; both ended `0 rows were processed` (VERIFIED). Copy the style of a working row.
   - If no jurisdiction of that geography type exists to copy, the style is a GUESS: try it once and read the message.
3. CODE must not be in the second list for TAX. Use a geography that TAX has no jurisdiction for yet (GUESS: Oracle may refuse two jurisdictions of one tax on the same geography). **To be sure the state exists**, take one that another tax's jurisdiction already uses in the second list (VERIFIED with `NY` and `CA`).
4. **PREC (precedence level) must be unique per tax.** Look at the `prec` values of TAX's own jurisdictions in the second list: if TAX has none, PREC = `300`; otherwise PREC = the highest of them + 10 (for example 310). With 300 already used by the tax, Oracle refused the row: `This precedence level already exists. Create unique precedence levels for tax jurisdictions that apply to the same tax.` (VERIFIED; 310 then worked). Older rows of other taxes may share a value; that does not matter.

## Step 4. Build a package with only the new jurisdiction
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/jur_export/unz" --out-dir "<RUN>/payload" \
  --zip-name jur_new.zip --prefix <PREFIX> \
  --key "ZX_JURISDICTION.csv=TaxJurisdictionCode,TaxRegimeCode,Tax" \
  --key "ZX_JURISDICTION_TRANSLATION.csv=ZX_JURISDICTION.TaxJurisdictionCode,ZX_JURISDICTION.TaxRegimeCode,ZX_JURISDICTION.Tax,Language" \
  --prefix-col "ZX_JURISDICTION.csv=TaxJurisdictionCode" --max-len "TaxJurisdictionCode=30" \
  --row "ZX_JURISDICTION.csv|TaxJurisdictionCode=<CODE>|TaxRegimeCode=<REGIME>|Tax=<TAX>|EffectiveFrom=<FROM>|DefaultJurisdictionFlag=N|InnerCityJurisdictionFlag=N|PrecedenceLevel=<PREC>|RecordTypeCode=USER_DEFINED|TaxJurisdictionName=<NAME>|GeographyUse=MASTER_REF|GeographyType=STATE|GeographyName=<STATE>|CountryCode=US|RegimeTypeFlag=I|GeographyElement1=United States|GeographyElement2=<STATE>" \
  --row "ZX_JURISDICTION_TRANSLATION.csv|ZX_JURISDICTION.TaxJurisdictionCode=<CODE>|ZX_JURISDICTION.TaxRegimeCode=<REGIME>|ZX_JURISDICTION.Tax=<TAX>|Language=US|SourceLang=US|TaxJurisdictionName=<NAME>"
```
- `<STATE>` is the state written as in Step 3 (ours: `NY`, `CA`); `<PREC>` comes from Step 3.4.
- The row above is the VERIFIED US state form. For another country or geography type, replace `GeographyType`, `GeographyName`, `CountryCode`, `PrecedenceLevel` and the `GeographyElement...` columns with what the copied row of Step 3 has (GUESS, not tested); add `GeographyCode` only if the copied row has one.
- The builder must print `ZX_JURISDICTION.csv: 1 new rows`, `ZX_JURISDICTION_TRANSLATION.csv: 1 new rows`, every other file `0 new rows`. It stops if CODE exists in this package, lacks the prefix or is too long (the jurisdictions export is empty, so Step 3's list is the real check).
- No parent tax row is needed (the jurisdiction file is not a child in this package). VERIFIED

## Step 5. Import
**Approval.** The person must approve the environment, the task, TAX, the geography and the exact CODE before the import. If their brief names all of them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_JURISDICTIONS --task-name "Manage Tax Jurisdictions" \
  --zip-file "<RUN>/payload/jur_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`); it is the only key to the full process log later.
- About 40 to 60 s. Print a short summary of the process log (it also prints geography warnings):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Tax Jurisdiction BO is dependent[^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TaxJurisdiction. Status: Completed successfully ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0`. **`0 rows were processed` is a failure**, also when it says "Completed with warnings" (that is the geography message of Step 3).
- **If the script loses the connection after the process started** (no process log), the import still runs in Oracle. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed or 0 processed: copy the message, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second taxes export and compare
Repeat the **taxes** export of Step 2 with `--output-dir "<RUN>/tax_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/tax_before/unz" "<RUN>/tax_after/unz" \
  --key "ZX_TAX.csv=Tax,TaxRegimeCode" \
  --key "ORA_ZX_TRAN_TAX_JURISDICTION.csv=TaxJurisdictionCode,TaxRegimeCode,Tax" \
  --key "ORA_ZX_TRAN_TAX_JURISDICTION_TRANSLATION.csv=ORA_ZX_TRAN_TAX_JURISDICTION.TaxJurisdictionCode,ORA_ZX_TRAN_TAX_JURISDICTION.TaxRegimeCode,ORA_ZX_TRAN_TAX_JURISDICTION.Tax,Language" \
  --expect "ORA_ZX_TRAN_TAX_JURISDICTION.csv=<CODE>,<REGIME>,<TAX>" \
  --expect "ORA_ZX_TRAN_TAX_JURISDICTION_TRANSLATION.csv=<CODE>,<REGIME>,<TAX>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your jurisdiction and its translation were added; the tax, regime and subscription files are unchanged. Oracle fills `TaxAcctEntityCode=JURISDICTION` itself. If someone else changed taxes between your two exports, extra rows appear: judge your own rows plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 5 files, metadata XML unchanged; only the jurisdiction and its translation get rows.
3. Do not make the tax live, add rates, tax accounts or thresholds in a test.
4. Test records may stay for good. This skill never deletes. Record every created jurisdiction.
5. Tested only: a US state jurisdiction on a tax that is **not live** (test regime). On that tax a tax status was refused (see `manage-tax-statuses`), but the jurisdiction was accepted. Other countries, geography types, default or inner-city jurisdictions: not tested.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Exports before | jurisdictions package 0 rows; taxes package 13 taxes, 5 jurisdictions (state names written as 2-letter codes) |
| New record | `GAPFILL_AB_P2_JR1`, "GAPFILL AB P2 jurisdiction 1", state `NY`, for test tax `GAPFILL_AB_P1_TX1` (zone type STATE, not live) of test regime `GAPFILL_AB_TR1`, from 2026/01/01 |
| Import | attempt 1 (`GeographyName=New York`) and 2 (+ `GeographyCode=NY`): 0 rows, geography warning, nothing created; attempt 3 (style copied from existing rows): 1 row, 0 failed, 61 s |
| Taxes export after + compare | 6 jurisdictions; added 1 + 1, removed 0, changed 0: PASS |
