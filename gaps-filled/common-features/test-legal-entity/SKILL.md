---
skill_id: "gosaas.gap-fills.common-features.test-legal-entity"
name: "Test legal entity: create your own prefixed legal entity (with its main reporting unit) by FSM CSV, as a prerequisite (GoSaaS gap fill)"
description: "Creates ONE new legal entity whose identifier and name start with your prefix, with a new legal address, its identifying registration and its main legal reporting unit, through the Manage Legal Entity FSM CSV package, run with FSCR's export/import scripts. Oracle then makes the legal entity tax profile and the reporting unit tax profile by itself. Used as the safe target for the legal entity tasks (tax profiles, financial information, configuration owner tax options). Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 14, 2026-11-26. Tested live on one test environment. NOT official FSCR."
task_code: "XLE_MANAGE_LEGAL_ENTITY (prerequisite only; FSCR has its own guide for the task)"
type: "fsm-csv"
version: "0.1.0"
status: "tested (batch 14)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Step 4 creates a new legal entity, a new location (legal address), a party, a main legal reporting unit, 2 registrations and (made by Oracle) 2 tax profiles. The CSV route cannot delete them; they stay. Nothing existing is changed."
---

# Test legal entity (GoSaaS prerequisite skill)

> **Added by GoSaaS, not part of official FSCR.** Runs FSCR's scripts in place; edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
Several setup tasks change a record that Oracle keeps **one per legal entity** (its tax profile, its reporting unit's tax profile, its financial information, configuration owner tax options). Changing a real legal entity changes real tax and accounting. The safe way is to make **your own** legal entity first (a new record with your prefix that nobody uses) and change only that one. This skill makes it. It is not a gap of its own: FSCR has a planning guide for Manage Legal Entity; this skill is the short, tested route.

Choices made (VERIFIED): country **US**, identifying jurisdiction **United States Income Tax**, `LegalEmployerFlag N` and `PsuFlag N` (no HCM legal employer or payroll unit is made), `TransactingEntityFlag Y` (Oracle's default).

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py   (offline builder, new rows only)
W     = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's REST client unchanged; readable errors)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (exports hold user names)
PREFIX= your test prefix, e.g. GAPFILL_XX_
LE    = your new identifier, = PREFIX + short name, upper case, e.g. GAPFILL_XX_LE1 (also used as the name)
ADDR  = "<LE> Address 1/ALBANY, NY 12200"   (the address natural key; see Step 3)
```
Paths as `E:/...` in Git Bash, never `$PWD` or `/e/...`. Set `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type or print credentials). A sign-in lasts about an hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names.

## Prerequisites
1. Read access to legal entities; the right to create legal entities (Legal Entities Administration).
2. Check that LE does not exist yet (Step 2). Never create it twice.

## Step 1. Read-only export (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code XLE_MANAGE_LEGAL_ENTITY --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
```
No ZIP = the export failed: run it again into a NEW folder (up to 3 tries). The ZIP holds 7 CSVs + `ASM_SETUP_CSV_METADATA.xml`: `XLE_ENTITY_PROFILE` (top), `XLE_ETB_PROFILE` (reporting units), `XLE_REGISTRATION`, `ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION`, `XLE_LE_LEGAL_ADDRESS`, and 2 registration-function files (header only). Do not copy the ZIP's file names anywhere (they hold the environment name).

## Step 2. Check LE is new and read the jurisdiction (read only, VERIFIED)
Run the REST calls from `<RUN>` (`cd "<RUN>"`), so `--output` files land there. A network error or timeout on a GET (for example `WinError 10060`) is safe: run the same GET again.
- `grep -c "<LE>" <RUN>/exp1/unz/XLE_ENTITY_PROFILE.csv` must print 0. Also by REST: `python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV --query onlyData=true --query "q=LegalEntityIdentifier='<LE>'" --no-open-browser --output le.json` → `count` 0.
- Jurisdiction: `.../legalJurisdictionsLOV --query onlyData=true --query "q=Name='United States Income Tax'"` → 1 row (`LegalEntityRegistrationCode EIN/TIN`, `LegalReportingUnitRegistrationCode RN`). The jurisdiction **name** goes in the registration rows.

## Step 3. Build the package (offline, VERIFIED)
Five new rows, all keyed on your own values. `OrigSystemReference` on the address is **required** for a new address (without it: `JBO-27014: Attribute OrigSystemReference in LocationEO is required`, then `LocationId in RegistrationEO is required`). `LegalAddress` (on the legal entity) and `FormattedAddress` (on both registrations) must equal the address row's `LeFormattedAddress`: address line, `/`, city in capitals, `, `, state, space, postal code.
```bash
cd "<RUN>"; N=<LE>; A="$N Address 1/ALBANY, NY 12200"
python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name le.zip --prefix <PREFIX> \
 --key "XLE_ENTITY_PROFILE.csv=LegalEntityIdentifier" --key "XLE_LE_LEGAL_ADDRESS.csv=Address1" --key "XLE_REGISTRATION.csv=RegistrationNumber" --key "ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv=RegistrationNumber" --key "XLE_ETB_PROFILE.csv=Name" \
 --prefix-col "XLE_ENTITY_PROFILE.csv=LegalEntityIdentifier" --prefix-col "XLE_ENTITY_PROFILE.csv=Name" \
 --row "XLE_LE_LEGAL_ADDRESS.csv|Address1=$N Address 1|City=Albany|State=NY|PostalCode=12200|Country=US|ActualContentSource=USER_ENTERED|AddressStyle=POSTAL_ADDR_US|CreatedByModule=XLE_CREATE_LE|EffectiveDate=<today yyyy/mm/dd>|InternalFlag=Y|StatusFlag=A|OrigSystemReference=${N}_ADDR|LeFormattedAddress=$A" \
 --row "XLE_ENTITY_PROFILE.csv|LegalEntityIdentifier=$N|Name=$N|AttributeCategory=US|LeInformationContext=US|LegalEmployerFlag=N|PsuFlag=N|TransactingEntityFlag=Y|GeographyCode=US|TerritoryShortName=United States|TerritoryCode=US|LegalAddress=$A|RegistrationCodeEtbValue=${N}_LRU|RegistrationCodeLeValue=${N}_REG" \
 --row "XLE_REGISTRATION.csv|XLE_ENTITY_PROFILE.LegalEntityIdentifier=$N|RegisteredName=$N|RegistrationNumber=${N}_REG|SourceTable=XLE_ENTITY_PROFILES|Name=United States Income Tax|IdentifyingFlag=Y|FormattedAddress=$A" \
 --row "XLE_ETB_PROFILE.csv|XLE_ENTITY_PROFILE.LegalEntityIdentifier=$N|Name=$N|EtbInformationContext=US|MainEstablishmentFlag=Y|GeographyCode=US|GeographyName=United States|GeographyType=COUNTRY|GeographyUse=MASTER_REF|GeographyCodeTransient=US|GeographyTypeTransient=COUNTRY|GeographyUseTransient=MASTER_REF|GeographyNameTransient=United States|GeographyElement1=United States" \
 --row "ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv|XLE_ENTITY_PROFILE.LegalEntityIdentifier=$N|XLE_ETB_PROFILE.Name=$N|RegisteredName=$N|RegistrationNumber=${N}_LRU|SourceTable=XLE_ETB_PROFILES|Name=United States Income Tax|IdentifyingFlag=Y|FormattedAddress=$A"
```
Replace `<today yyyy/mm/dd>` in the address row (the only placeholder inside the command that is not a variable). The builder refuses a key that already exists; on success it prints one "N new rows" line per file and "wrote pay\le.zip". The 2 registration-function files stay header only.

## Step 4. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code XLE_MANAGE_LEGAL_ENTITY --task-name "Manage Legal Entity" --zip-file "<RUN>/pay/le.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
```
Write down the **ProcessId** (the number). The result is in `<RUN>/imp/*_process_log.txt` (FSCR's log may end with `StatusCode: (unknown)`, which is normal). Success = `A total of 1 rows were processed. 0 rows of them failed` and `Business object: Legal Entity. Status: Completed successfully` (an extra `Status: In progress` line next to it is normal). **Dropped connection after the import started:** never import again; wait 2 minutes and check Step 5 first.

**Read the log safely:** the process log and the file names in `<RUN>/imp` hold the environment name and the submitting user; never print the whole log, never list that folder into a report. Print only the result lines:
```bash
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```


## Step 5. Read back (VERIFIED)
- REST `legalEntitiesLOV` with `q=LegalEntityIdentifier='<LE>'` → 1 row, `Name` = LE.
- A new export: run Step 1 again with `exp2` in place of `exp1` (both the export and the unzip line). Then count rows with a CSV reader (a field can span lines, so `wc -l` can miscount):
  ```bash
  python -I -c "import csv,sys,glob,os; [print(os.path.basename(f), sum(1 for _ in csv.reader(open(f,encoding='utf-8-sig')))-1, sum(1 for _ in csv.reader(open(f.replace(sys.argv[1],sys.argv[2]),encoding='utf-8-sig')))-1) for f in sorted(glob.glob(sys.argv[1]+'/*.csv'))]" "<RUN>/exp1/unz" "<RUN>/exp2/unz"
  ```
  Each of the 5 files has exactly 1 more row in `exp2` (`grep -c "<LE>"` → 1 in each); the 2 function files still 0.
- Oracle also makes (VERIFIED): the legal entity tax profile (`ZX_LEGAL_ENTITY_TAX_PROFILE`, `PartyTypeCode FIRST_PARTY`) and the reporting unit tax profile (`ZX_ESTABLISHMENT_TAX_PROFILE`, `PartyTypeCode LEGAL_ESTABLISHMENT`, `LegalEstablishmentName` = LE). Those are what the tax profile skills change. Optional check: export task `ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES` (as in Step 1, task code changed; no ZIP: run again into a NEW folder) and `grep -c "<LE>" .../unz/ZX_LEGAL_ENTITY_TAX_PROFILE.csv` → 1; for the unit, task `ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES`, file `ZX_ESTABLISHMENT_TAX_PROFILE.csv` → 1.

## Rules and limits
- Only your own prefixed identifier and name. The legal entity is not assigned to any ledger, business unit or employer: nothing else uses it.
- One legal entity per tester; reuse it for all the legal entity tasks (GET first).
- Different country: change the address, territory, geography, contexts and jurisdiction together (GUESS: not tested).

## Worked example (codes and ProcessIds only)
- 2026-11-26 `GAPFILL_AB_B14_LE1`: try 1 refused (no `OrigSystemReference`; nothing created, REST count 0), ProcessId 100004743429459; try 2 created, ProcessId 100004743430091; after-export +1 row in each of 5 files.
- 2026-11-26 fresh test `GAPFILL_AB_B14_LE2F`: ProcessId 100004744412079, first try, +1 row in each of 5 files: PASS.
