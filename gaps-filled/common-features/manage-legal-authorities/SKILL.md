---
skill_id: "gosaas.gap-fills.common-features.manage-legal-authorities"
name: "Manage Legal Authorities (GoSaaS gap fill)"
description: "Create a new legal authority (an organization party with a legal authority usage, an address, a legislative category and a tax authority profile) through FSCR's setup-task CSV export and import (XLE legal authority package), copying an existing legal authority, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 3, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_MANAGE_LEGAL_AUTHORITIES"
task_name: "Manage Legal Authorities"
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
  - "at least one existing legal authority (it is the template)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new organization party (legal authority usage, one address, one classification, one tax authority profile). No legal entity, registration or tax points to it. It may not be deletable; plan as if it stays."
---

# Manage Legal Authorities (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A legal authority is a government body (for example a tax office) that legal entities and tax registrations can point to. In Oracle it is a trading community **organization party** with the party usage `LEGAL_AUTHORITY`, an identifying address, a legislative category classification and a tax authority profile (reporting / collecting flags). This skill creates **one new legal authority** by copying every setting of an existing one and changing its number, name and street.

## When to use
- Someone asks to create a **new** legal authority for task `XLE_MANAGE_LEGAL_AUTHORITIES`.
- Do **not** use it to change existing authorities, or to link an authority to a legal entity, registration or tax. New records only.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
           If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T        = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
RUN      = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX   = your test prefix, e.g. GAPFILL_<INITIALS>_
NUM      = new PartyNumber: upper case letters, digits and _, starting with PREFIX, max 27 (so NUM + "_S1" fits 30; GUESS)
SITE     = new PartySiteNumber = <NUM>_S1
NAME     = new party name, e.g. "GAPFILL XX legal authority 1" (no "|" character)
STREET   = new Address1, e.g. "1 GAPFILL Test Street"
TEMPLATE = PartyNumber of one existing legal authority (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code XLE_MANAGE_LEGAL_AUTHORITIES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 21 files (VERIFIED, 99 to 200 s). With rows: `XLE_LEGAL_AUTHORITY_PARTY.csv` (key `PartyNumber`), `ORA_XLE_LEGALAUTH_PARTY_PROFILE.csv`, `ORA_XLE_LEGALAUTH_PARTY_USAGE.csv`, `ORA_XLE_LEGALAUTH_PARTY_ADDRESS.csv`, `ORA_XLE_LEGALAUTH_PARTY_ADDRESS_USAGE.csv`, `ORA_XLE_LEGALAUTH_PARTY_CLASSIFICATION.csv`, `ZX_TAX_AUTHORITY_PROFILE.csv`. The child files point to the party by `XLE_LEGAL_AUTHORITY_PARTY.PartyNumber`. Phone, e-mail, URL and relationship files may be empty; leave them empty.
- If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries. If it still fails: **stop**.

## Step 3. Choose a template and check the number and name
```bash
python -I -c "import csv,sys; d=sys.argv[1]; p={r['PartyNumber']:r for r in csv.DictReader(open(d+'/ORA_XLE_LEGALAUTH_PARTY_PROFILE.csv',encoding='utf-8-sig'))}; [print(n,'|',p[n]['PartyName'],'|',p[n]['PrimaryAddressCity'],p[n]['PrimaryAddressCountry']) for n in [r['PartyNumber'] for r in csv.DictReader(open(d+'/XLE_LEGAL_AUTHORITY_PARTY.csv',encoding='utf-8-sig'))] if n in p]" "<RUN>/export_before/unz"
```
1. **TEMPLATE** = the **first listed** legal authority whose number and name do not start with a test prefix and that has a row in each of the 7 files above. The new authority copies its country, city, state, postal code, currency, legislative category and tax authority flags. VERIFIED. If the person wants another country or city, copy a template in that country; changing the geography by hand was not tested (GUESS).
2. If there is **no legal authority**, **stop**: rows written out in full were not tested.
3. **NUM and NAME are free:** neither may be in the list (the builder checks NUM again).
4. **PartyNumber:** Oracle normally numbers parties itself. Here the import **kept the number we gave** (`<NUM>`) and the site number (`<SITE>`). VERIFIED. If your environment ignores given party numbers, Step 6 shows the new party under another number: then compare by NAME (see Step 6) and report it.

## Step 4. Build a package with only the new authority
Never copy internal ids: the `--clear` lines below remove every id-like column of the template (party, location and site ids, derived address texts). VERIFIED
```bash
U="<RUN>/export_before/unz"; P=XLE_LEGAL_AUTHORITY_PARTY.PartyNumber; D=<yyyy/mm/dd>
python -I "<T>/template_row.py" --export-dir "$U" --file XLE_LEGAL_AUTHORITY_PARTY.csv --match "PartyNumber=<TEMPLATE>" \
  --set "PartyNumber=<NUM>" --clear MapAddress --clear TotalPartyUsageCount --clear TotalSourceSystemCount --clear FirstPartyUsageName --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "$U" --file ORA_XLE_LEGALAUTH_PARTY_PROFILE.csv --match "$P=<TEMPLATE>" \
  --set "$P=<NUM>" --set "PartyNumber=<NUM>" --set "PartyName=<NAME>" --set "OrganizationName=<NAME>" \
  --set "UniqueNameAlias=<NAME>" --set "PartyUniqueName=<NAME>" --set "PrimaryAddressLine1=<STREET>" --set "MapAddress=<STREET>" \
  --clear PartyId1 --clear IdenAddrLocationId --clear IdenAddrPartySiteId --clear SellToPartySiteId --clear PartyIdString \
  --clear LastSourceUpdateDate --clear FormattedMultilineAddress --clear TotalPartyUsageCount --clear TotalSourceSystemCount \
  --out "<RUN>/rows.txt" --append
python -I "<T>/template_row.py" --export-dir "$U" --file ORA_XLE_LEGALAUTH_PARTY_USAGE.csv --match "$P=<TEMPLATE>" \
  --set "$P=<NUM>" --set "EffectiveStartDate=$D" --out "<RUN>/rows.txt" --append
python -I "<T>/template_row.py" --export-dir "$U" --file ORA_XLE_LEGALAUTH_PARTY_ADDRESS.csv --match "$P=<TEMPLATE>" \
  --set "$P=<NUM>" --set "PartyNumber=<NUM>" --set "PartySiteNumber=<SITE>" --set "StartDateActive=$D" --set "Address1=<STREET>" \
  --out "<RUN>/rows.txt" --append
python -I "<T>/template_row.py" --export-dir "$U" --file ORA_XLE_LEGALAUTH_PARTY_ADDRESS_USAGE.csv --match "$P=<TEMPLATE>" \
  --set "$P=<NUM>" --set "ORA_XLE_LEGALAUTH_PARTY_ADDRESS.PartySiteNumber=<SITE>" --set "BeginDate=$D" --clear FormattedAddress \
  --out "<RUN>/rows.txt" --append
python -I "<T>/template_row.py" --export-dir "$U" --file ORA_XLE_LEGALAUTH_PARTY_CLASSIFICATION.csv --match "$P=<TEMPLATE>" \
  --set "$P=<NUM>" --set "StartDateActive=$D" --out "<RUN>/rows.txt" --append
python -I "<T>/template_row.py" --export-dir "$U" --file ZX_TAX_AUTHORITY_PROFILE.csv --match "PartyNumber=<TEMPLATE>" \
  --set "PartyNumber=<NUM>" --set "PartyName=<NAME>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "$U" --out-dir "<RUN>/payload" --zip-name la_new.zip --prefix <PREFIX> \
  --key "XLE_LEGAL_AUTHORITY_PARTY.csv=PartyNumber" --key "ORA_XLE_LEGALAUTH_PARTY_PROFILE.csv=$P" \
  --key "ORA_XLE_LEGALAUTH_PARTY_USAGE.csv=$P,PartyUsageCode" --key "ORA_XLE_LEGALAUTH_PARTY_ADDRESS.csv=$P,PartySiteNumber" \
  --key "ORA_XLE_LEGALAUTH_PARTY_ADDRESS_USAGE.csv=$P,ORA_XLE_LEGALAUTH_PARTY_ADDRESS.PartySiteNumber,SiteUseType" \
  --key "ORA_XLE_LEGALAUTH_PARTY_CLASSIFICATION.csv=$P,ClassCategory,ClassCode" --key "ZX_TAX_AUTHORITY_PROFILE.csv=PartyNumber" \
  --prefix-col "XLE_LEGAL_AUTHORITY_PARTY.csv=PartyNumber" --max-len "PartyNumber=30" @"<RUN>/rows.txt"
```
- `D`: the first day of this year or today (we used 2026/01/01). VERIFIED
- `template_row.py` must report 1 row for each of the 7 files; if a `--match` finds no row (the template lacks that file's row), choose another TEMPLATE. If a `--clear` column does not exist in your export, drop that `--clear`.
- The builder must print `1 new rows` for those 7 files and `0 new rows` for every other file. It stops if NUM exists, lacks the prefix or is too long.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact NUM and NAME before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code XLE_MANAGE_LEGAL_AUTHORITIES --task-name "Manage Legal Authorities" \
  --zip-file "<RUN>/payload/la_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later; the ESS request number does not open it.
- About 2 minutes. Print a short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: OrganizationParty ... A total of 1 rows were processed. 0 rows of them failed`, `Detail Object: TaxAuthorityProfileVO ... 1 rows ... 0 failed`, and `Total Objects Failed: 0` (about 20 objects processed is normal). **`0 rows were processed` is a failure.**
- **If the script loses the connection after the process started**, the import still runs in Oracle. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then (same `P` as Step 4)
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "XLE_LEGAL_AUTHORITY_PARTY.csv=PartyNumber" --key "ORA_XLE_LEGALAUTH_PARTY_PROFILE.csv=$P" \
  --key "ORA_XLE_LEGALAUTH_PARTY_USAGE.csv=$P,PartyUsageCode" --key "ORA_XLE_LEGALAUTH_PARTY_ADDRESS.csv=$P,PartySiteNumber" \
  --key "ORA_XLE_LEGALAUTH_PARTY_ADDRESS_USAGE.csv=$P,ORA_XLE_LEGALAUTH_PARTY_ADDRESS.PartySiteNumber,SiteUseType" \
  --key "ORA_XLE_LEGALAUTH_PARTY_CLASSIFICATION.csv=$P,ClassCategory,ClassCode" --key "ZX_TAX_AUTHORITY_PROFILE.csv=PartyNumber" \
  --expect "XLE_LEGAL_AUTHORITY_PARTY.csv=<NUM>" --expect "ORA_XLE_LEGALAUTH_PARTY_PROFILE.csv=<NUM>" \
  --expect "ORA_XLE_LEGALAUTH_PARTY_USAGE.csv=<NUM>,LEGAL_AUTHORITY" \
  --expect "ORA_XLE_LEGALAUTH_PARTY_ADDRESS.csv=<NUM>,<SITE>" \
  --expect "ORA_XLE_LEGALAUTH_PARTY_ADDRESS_USAGE.csv=<NUM>,<SITE>,<SiteUseType of the template>" \
  --expect "ORA_XLE_LEGALAUTH_PARTY_CLASSIFICATION.csv=<NUM>,<ClassCategory of the template>,<ClassCode of the template>" \
  --expect "ZX_TAX_AUTHORITY_PROFILE.csv=<NUM>" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your authority's 7 rows were added, nothing removed or changed. (`SiteUseType`, `ClassCategory` and `ClassCode` are the template's values, printed in `rows.txt`.) If someone else changed legal authorities between your two exports, judge your own rows plus `removed 0` and `changed 0`, and report the extras. If NUM is missing but a party named NAME was added under another number (Step 3, point 4), report that number and treat the import as done; never import again.

## Rules and limits
1. New records only; never import a full export.
2. Keep every file and the metadata XML unchanged in layout; only the 7 new rows go in.
3. Never link the test authority to a legal entity, registration, tax or jurisdiction in a test.
4. Test records may stay for good. This skill never deletes. Record every created authority.
5. No REST resource was searched; the export compare is the proof.
6. Not tested: other countries or a hand-made address, phones, e-mails, URLs, contacts (relationship files), authorities without a tax authority profile.
7. Tested on one environment (release 11.13.26.10.0).
8. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `template_row.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this number; it now exists.
| Step | Result |
|---|---|
| Export before | 1 legal authority (a US tax authority, reporting and collecting); about 200 s |
| Template | that authority |
| New record | `GAPFILL_AB_P3_LA1` "GAPFILL AB P3 legal authority 1", site `GAPFILL_AB_P3_LA1_S1`, street "1 GAPFILL Test Street", same city and country, from 2026/01/01 |
| Import | 1 attempt (ProcessId 100004742406310), about 2 min: OrganizationParty 1 row, TaxAuthorityProfileVO 1 row, 0 failed |
| Export after + compare | 2 authorities; 7 rows added (party, profile, usage, address, address usage, classification, tax profile), removed 0, changed 0: PASS |
