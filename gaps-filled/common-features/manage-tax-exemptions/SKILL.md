---
skill_id: "gosaas.gap-fills.common-features.manage-tax-exemptions"
name: "Manage Tax Exemptions (GoSaaS gap fill)"
description: "Create one new tax exemption for a test customer through FSCR's setup-task CSV export and FSM CSV import, row written in full (the export is often empty), then read it back with a second export and REST. Step 1 makes the test customer and its third-party tax profile by REST. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 3 (failed) and batch 4 fix (tested), 2026-11-24. Tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_TAX_EXEMPTIONS"
task_name: "Manage Tax Exemptions"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (fusion_rest_client.py, used in place for Step 1 and the read-back)"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
  - "Step 1 prerequisite: a test customer (CRM REST accounts, POST) with a THIRD_PARTY party tax profile (REST partyTaxProfiles, POST)"
  - "gosaas ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES (manage-tax-rates): a test tax rate on a NOT live test tax"
side_effects:
  - "Starts setup-task CSV export processes and REST reads (read-only for Fusion data)."
  - "Step 1 creates, by REST, one customer organization (sales account of type customer, no address, no customer account) and one third-party party tax profile for it, unless they already exist."
  - "Step 5 starts one setup-task CSV import that creates one tax exemption. On a tax that is not live it changes no transaction. None of these may be deletable; plan as if they stay."
---

# Manage Tax Exemptions (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill that builds this row. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax exemption lowers or replaces the tax for one **customer** (or customer site) on one tax: a discount (`RateModifier` percent) or a special rate, backed by a certificate number. File `ZX_TAX_EXEMPTION.csv` (one file; the other 7 files of the package are legal reporting unit registrations and VAT reporting setups, not used here).
- Oracle keeps exemptions on the **third-party tax profile of customers and customer sites only** (not suppliers, legal reporting units or tax authorities). The import finds that profile by party number and `TaxProfilePartyTypeCode=THIRD_PARTY`. Without it every row fails with `JBO-27014: Attribute PartyTaxProfileId in TaxExemptionEO is required` (VERIFIED: 3 refused tries on a tax authority party).
- **Test rule:** use **your own test customer** (Step 1) and **your own test rate on a tax that is not live**. An exemption for a real customer or on a live tax changes real tax: that needs the person's explicit approval and is not covered here.

## When to use
- Someone asks to create a **new** tax exemption for task `ORA_ZX_MANAGE_TAX_EXEMPTIONS`.
- Do **not** use it to change, suspend or end exemptions. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
C       = <FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py   (FSCR REST client)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
CUST    = the test customer's organization name, starting with PREFIX, e.g. GAPFILL_XX_CUST1
PNUM    = its party number (Oracle gives it in Step 1; read it, never type it from memory)
CERT    = new ExemptCertificateNumber, upper case, starting with PREFIX
REGIME, TAX, STATUS, RATE = codes of your test tax rate (Step 1)
FROM    = start date yyyy/mm/dd, on or after the rate's start date
```

## Step 0 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` / `--output` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST calls. Never print tokens, headers, the sign-in URL, the server address or user names: send REST output to a file with `--output`, send the client's own messages to a log, and print only the fields named below. FSCR puts the environment name in its output file names: never copy those names into evidence.
- If a call reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials.

A small reader used below (prints only chosen fields of a saved REST answer; define it again in every new shell):
```bash
show() { python -I -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); it=d.get('items',[d]); print('count',d.get('count',len(it))); [print({k:x.get(k) for k in sys.argv[2].split(',')}) for x in it]" "$1" "$2"; }
```

## Step 1. Prerequisites
**1a. Test rate (read-only).** Export `ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES` read-only as in Step 2 (other task code, folder `<RUN>/rates`, about 2 min) and list your rates:
`python -I -c "import csv,sys; [print(r['TaxRegimeCode'],r['Tax'],r['TaxStatusCode'],r['TaxRateCode'],r['EffectiveFrom'],r['ContentOwnerPartyTypeCode']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TAX_RATE_PERCENT_TYPE.csv',encoding='utf-8-sig')) if r['TaxRateCode'].startswith(sys.argv[2])]" "<RUN>/rates/unz" <PREFIX>`
Pick the first row with owner `GCO`: REGIME, TAX, STATUS, RATE. If there is none, create one first with the `manage-tax-rates` skill (its tax must be **not live**). VERIFIED

**1b. Test customer (REST). Check first, create only if missing.**
```bash
cd "<RUN>"
timeout 120 python -B "<C>" "/crmRestApi/resources/11.13.18.05/accounts?q=OrganizationName='<CUST>'&onlyData=true&fields=PartyNumber,OrganizationName,Type" \
  --no-open-browser --output cust_get.json > cust_get.log 2>&1; show cust_get.json PartyNumber,OrganizationName,Type
```
- `count 1`: the customer exists; PNUM = its `PartyNumber`. Go to 1c.
- `count 0`: create it (one call; if the call drops, run the GET again before any second POST, never POST twice):
```bash
timeout 120 python -B "<C>" "/crmRestApi/resources/11.13.18.05/accounts" --method POST \
  --body '{"OrganizationName":"<CUST>","Type":"ZCA_CUSTOMER"}' --no-open-browser --output cust_post.json > cust_post.log 2>&1
tail -2 cust_post.log | grep -o "HTTP [0-9]*"; show cust_post.json PartyNumber,OrganizationName,Type
```
  Want `HTTP 201` and `Type ZCA_CUSTOMER`. PNUM = the printed `PartyNumber` (Oracle numbers it; VERIFIED). `ZCA_CUSTOMER` is the account type "customer"; name and type are enough (VERIFIED).

**1c. Third-party tax profile (REST). Check first, create only if missing.**
```bash
timeout 120 python -B "<C>" "/fscmRestApi/resources/11.13.18.05/partyTaxProfiles?q=PartyNumber='<PNUM>'&onlyData=true" \
  --no-open-browser --output ptp_get.json > ptp_get.log 2>&1; show ptp_get.json PartyNumber,PartyTypeCode,PartyTaxProfileId
```
- A row with `PartyTypeCode THIRD_PARTY`: the profile exists. Go to Step 2.
- `count 0` (VERIFIED: a new customer has none): create it with one call (same rule: GET again before any second POST):
```bash
timeout 120 python -B "<C>" "/fscmRestApi/resources/11.13.18.05/partyTaxProfiles" --method POST \
  --body '{"PartyTypeCode":"THIRD_PARTY","PartyNumber":"<PNUM>"}' --no-open-browser --output ptp_post.json > ptp_post.log 2>&1
tail -2 ptp_post.log | grep -o "HTTP [0-9]*"; show ptp_post.json PartyNumber,PartyTypeCode,PartyTaxProfileId
```
  Want `HTTP 201`, `PartyTypeCode THIRD_PARTY` and a `PartyTaxProfileId` (a number; do not copy it anywhere, the CSV finds the profile by party number).

**1d. Lookups** (seeded; checked live in our test): `ExemptionStatusCode` from `ZX_EXEMPTION_STATUS` (`PRIMARY`), `ExemptionTypeCode` from `ZX_EXEMPTION_TYPE` (`DISCOUNT`, `SPECIAL_RATE`, ...), `ExemptReasonCode` from `ZX_EXEMPTION_REASON_CODE` (for example `OPERATION`). To check one: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource "standardLookups/ZX_EXEMPTION_REASON_CODE/child/lookupCodes" --fields LookupCode,Meaning --out "<RUN>/lk.json"`.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_TAX_EXEMPTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.log" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 8 files (VERIFIED, about 75 s). `ZX_TAX_EXEMPTION.csv` may have 0 rows (VERIFIED) or earlier test exemptions. CERT must not be in its `ExemptCertificateNumber` column (the builder checks).

## Step 3. Build a package with only the new exemption
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name exm_new.zip \
  --prefix <PREFIX> --key "ZX_TAX_EXEMPTION.csv=ExemptCertificateNumber" --prefix-col "ZX_TAX_EXEMPTION.csv=ExemptCertificateNumber" \
  --row "ZX_TAX_EXEMPTION.csv|ExemptCertificateNumber=<CERT>|ContentOwnerPartyTypeCode=GCO|EffectiveFrom=<FROM>|ExemptionStatusCode=PRIMARY|ExemptReasonCode=OPERATION|TaxRegimeCode=<REGIME>|Tax=<TAX>|TaxStatusCode=<STATUS>|TaxRateCode=<RATE>|PartyTaxPartyNumber=<PNUM>|PartyTaxPartyName=<CUST>|TaxProfilePartyTypeCode=THIRD_PARTY|PartyTypeCode=THIRD_PARTY|ExemptionTypeCode=DISCOUNT|RateModifier=10|RecordTypeCode=USER_DEFINED" | grep -v ": 0 new rows"
```
- `TaxProfilePartyTypeCode=THIRD_PARTY` with the customer's party number is what lets Oracle find the profile (VERIFIED). `ContentOwnerPartyTypeCode=GCO` matches the test rate's owner (VERIFIED). `DISCOUNT` with `RateModifier=10` = 10 % discount (VERIFIED).
- The builder must print `ZX_TAX_EXEMPTION.csv: 1 new rows`.

## Step 4. (no separate step: the approval below comes before the import)
**Approval.** The person must approve the environment, the task, CUST (Step 1 REST creates), CERT and the rate used before any create. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.

## Step 5. Import
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_TAX_EXEMPTIONS --task-name "Manage Tax Exemptions" \
  --zip-file "<RUN>/payload/exm_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.log"
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: [^.]+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_]+|JBO-[0-9]+: [^.]{0,160}|ZX_[A-Z_]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
```
- **Write down the `ProcessId`** (the grep line). Success (VERIFIED, about 40 s): `Detail Object: TaxExemption1. Status: Completed successfully ... 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`.
- `JBO-27014 ... PartyTaxProfileId ... is required` = Step 1c was skipped or PNUM is wrong. Fix that; a failed row creates nothing (VERIFIED).
- **If the script loses the connection after the process started**, do not import again; wait 2 minutes and do Step 6.
- Other failures: read the message, change one thing, retry at most 3 times.

## Step 6. Read back: second export, compare and REST
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX_EXEMPTION.csv=ExemptCertificateNumber" --expect "ZX_TAX_EXEMPTION.csv=<CERT>" \
  --rows-out "<RUN>/added_rows.csv" | grep -E "ZX_TAX_EXEMPTION|PROBLEM|RESULT"
cd "<RUN>"; timeout 120 python -B "<C>" "/fscmRestApi/resources/11.13.18.05/taxExemptions?q=ExemptCertificateNumber='<CERT>'&onlyData=true" \
  --no-open-browser --output exm_get.json > exm_get.log 2>&1
show exm_get.json ExemptCertificateNumber,PartyName,PartyNumber,PartyTypeCode,Tax,ExemptionStatusCode,ExemptionTypeCode,RateModifier
```
`RESULT: PASS` (only your exemption added, nothing removed or changed) and REST `count 1` with your CUST, `THIRD_PARTY`, `PRIMARY`, `DISCOUNT`, `10` = done (VERIFIED). Oracle adds `RegimeTypeFlag=I` and fills `TaxProfilePartyName`. Do not print whole rows: they hold user names in the audit columns.

## Rules and limits
1. New records only; never import a full export. Never a real customer or a live tax without explicit approval.
2. Never POST twice: always GET first (Steps 1b, 1c).
3. Test records may stay for good. This skill never deletes. Record the customer, its profile and every CERT.
4. Not tested: customer sites (`THIRD_PARTY_SITE`), special rates, item- or jurisdiction-limited exemptions, customers with accounts and addresses.

## Worked example (VERIFIED, 2026-11-24). Do not reuse these names.
| Step | Result |
|---|---|
| 1a | rate `GAPFILL_AB_TF_RT1` (5 %, GCO) on status `GAPFILL_AB_TF_ST1`, tax `GAPFILL_AB_P1_TX1` (not live), regime `GAPFILL_AB_TR1` |
| 1b | no `GAPFILL_AB_B4FIX_CUST1` before; POST accounts: HTTP 201, Oracle party number given, type `ZCA_CUSTOMER` |
| 1c | no profile before; POST partyTaxProfiles: HTTP 201, `THIRD_PARTY`, profile id given |
| 2 | 8 files, 0 exemptions; about 75 s |
| 5 | `GAPFILL_AB_B4FIX_EXM1`, 1 attempt (ProcessId 100004742416701): TaxExemption1 1 row, 0 failed |
| 6 | 0 -> 1, removed 0, changed 0: PASS; REST taxExemptions count 1 |
| History | batch 4 part 3: 3 tries on a tax authority party refused (`PartyTaxProfileId` required); the customer + profile of Step 1 fixed it |
