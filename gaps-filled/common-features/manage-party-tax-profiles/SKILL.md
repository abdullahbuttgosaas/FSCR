---
skill_id: "gosaas.gap-fills.common-features.manage-party-tax-profiles"
name: "Manage Party Tax Profiles (GoSaaS gap fill)"
description: "Create one new tax authority party tax profile for a test legal authority that has none, through FSCR's setup-task CSV export and FSM CSV import (87-file party tax profile package), copying an existing tax authority profile, then read it back with a second export. Step 1 makes the test legal authority without a profile. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 3, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_PARTY_TAX_PROFILES"
task_name: "Manage Party Tax Profiles"
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
  - "gosaas XLE_MANAGE_LEGAL_AUTHORITIES (manage-legal-authorities): Step 1 makes a test legal authority WITHOUT its tax authority profile row"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Step 1 starts one setup-task CSV import of the legal authority task that creates one new legal authority party (no tax profile)."
  - "Step 5 starts one setup-task CSV import that creates one tax authority profile (reporting and collecting flags) for that party. No legal entity, registration or tax points to it. It may not be deletable; plan as if it stays."
---

# Manage Party Tax Profiles (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill that builds these rows. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A party tax profile holds the tax settings of one party for one party type. The task's export (87 files) holds the profiles of tax authorities (`ZX_TAX_AUTHORITY_PROFILE.csv`), legal entities, legal reporting units (establishments), business units and tax partners, plus their registrations and classifications. Third-party (customer and supplier) profiles are **not** in this package (VERIFIED: `ZX_CUSTOMER_TAX_PROFILE.csv` holds customer tax **registrations**, not profiles).

This skill creates **one tax authority profile** (party type `TAX_AUTHORITY`) for **your own test legal authority**:
- Profiles of legal entities, legal reporting units and business units belong to real organizations (shared); this skill does not touch them.
- A legal authority made with the `manage-legal-authorities` skill **already has** a tax authority profile (that skill sends one). So Step 1 makes a new test legal authority **without** that row; then this task adds the profile. A profile is unique per party and party type, so a second one would update the first: never use a party that already has one.

## When to use
- Someone asks to create a **new** party tax profile for task `ORA_ZX_MANAGE_PARTY_TAX_PROFILES`, for a test legal authority.
- Do **not** use it to change existing profiles (any party type). New records only.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T        = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
LA       = <GAPS>/common-features/manage-legal-authorities/SKILL.md    (used in Step 1)
RUN      = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, no folder in its path named exactly "project"
PREFIX   = your test prefix, e.g. GAPFILL_<INITIALS>_
NUM      = PartyNumber of the new test legal authority (Step 1), starting with PREFIX, max 27
NAME     = its party name, e.g. "GAPFILL XX legal authority 3"
TPROF    = PartyNumber of an existing tax authority profile to copy (Step 3)
```

## Step 0 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR puts the environment name in its output file names: never copy those names into evidence.
- If an export reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials.

## Step 1. Prerequisite: a test legal authority WITHOUT a tax authority profile
Follow `<LA>` Steps 2 to 6 with RUN = `<RUN>/la`, NUM and NAME as above, **with these 3 changes** (VERIFIED):
1. Step 4: **leave out** the `template_row.py` line for `ZX_TAX_AUTHORITY_PROFILE.csv` (the last `template_row.py` line). The builder then prints `1 new rows` for **6** files.
2. Step 5: success is `Detail Object: OrganizationParty ... 1 rows ... 0 failed` and `Total Objects Failed: 0`; there is **no** `TaxAuthorityProfileVO` line.
3. Step 6: leave out `--expect "ZX_TAX_AUTHORITY_PROFILE.csv=<NUM>"`; `RESULT: PASS` with 6 added rows. (You may skip Step 6 there: Step 2 below shows the party has no profile, and Step 6 below proves the profile.)
Write down the legal authority's ProcessId too.

## Step 2. Read-only export (after Step 1)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_PARTY_TAX_PROFILES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.log" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; [print(r['PartyNumber'],'|',r['PartyName'],'|',r['RecordTypeCode']) for r in csv.DictReader(open(sys.argv[1]+'/ZX_TAX_AUTHORITY_PROFILE.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
Expect 87 files (VERIFIED, about 2.5 to 3.5 min). **NUM must not be in the list** (no profile yet). If it is, stop: importing would update that profile.

## Step 3. Choose TPROF
TPROF = the first listed profile whose PartyNumber starts with your PREFIX, else the first listed one. VERIFIED (we copied the batch 3 test authority's profile: `ReportingAuthorityFlag`, `CollectingAuthorityFlag` and `ProcessForApplicabilityFlag` are `Y`; the other flags (supplier, customer, site, legal establishment, first party, self assess, offset, use legal entity as subscriber) are `N`).

## Step 4. Build a package with only the new profile
```bash
U="<RUN>/export_before/unz"
python -I "<T>/template_row.py" --export-dir "$U" --file ZX_TAX_AUTHORITY_PROFILE.csv --match "PartyNumber=<TPROF>" \
  --set "PartyNumber=<NUM>" --set "PartyName=<NAME>" --out "<RUN>/rows.txt"
python -I "<H>/build_fsm_package.py" --export-dir "$U" --out-dir "<RUN>/payload" --zip-name ptp_new.zip --prefix <PREFIX> \
  --key "ZX_TAX_AUTHORITY_PROFILE.csv=PartyNumber" --prefix-col "ZX_TAX_AUTHORITY_PROFILE.csv=PartyNumber" --max-rows 80 @"<RUN>/rows.txt" | grep -v ": 0 new rows"
```
`template_row.py` must write 1 row (about 15 columns: flags, `PartyTypeCode=TAX_AUTHORITY`, `RecordTypeCode`, number, name; no ids). The builder must print `ZX_TAX_AUTHORITY_PROFILE.csv: 1 new rows` (the other 86 files keep only their header).

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact NUM before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_PARTY_TAX_PROFILES --task-name "Manage Party Tax Profiles" \
  --zip-file "<RUN>/payload/ptp_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.log"
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(x for x in re.findall(r'Detail Object: [^.]+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_]+|JBO-[0-9]+: [^.]{0,160}',t) if ' 0 rows were processed' not in x))))" "<RUN>/import_result"
```
- **Write down the `ProcessId`** (the grep line). Success (VERIFIED, about 45 s): `Detail Object: TaxAuthorityProfileVO. Status: Completed successfully ... 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0` (about 50 objects processed is normal; the one-liner hides objects with 0 rows).
- **If the script loses the connection after the process started**, do not import again; wait 2 minutes and do Step 6.
- Rows failed: read the message, change one thing, retry at most 3 times.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_TAX_AUTHORITY_PROFILE.csv=PartyNumber" --expect "ZX_TAX_AUTHORITY_PROFILE.csv=<NUM>" \
  --rows-out "<RUN>/added_rows.csv" | grep -E "ZX_TAX_AUTHORITY|PROBLEM|RESULT"
```
`RESULT: PASS` = only your profile was added, nothing removed or changed. Do not print whole rows: they hold user names in the audit columns.

## Rules and limits
1. New records only; never import a full export; never a party that already has a profile of that type.
2. Test records may stay for good. This skill never deletes. Record every created party and profile.
3. Not tested: profiles for legal entities, legal reporting units, business units, tax partners; registrations; party fiscal classifications in this package.

## Worked example (VERIFIED, 2026-11-24). Do not reuse these numbers.
| Step | Result |
|---|---|
| Step 1 | legal authority `GAPFILL_AB_P3_LA3` ("GAPFILL AB P3 legal authority 3") from template 131334 without the profile row: ProcessId 100004741425152, OrganizationParty 1 row, 0 failed, 20 objects |
| Step 2 | 87 files; 3 tax authority profiles, `GAPFILL_AB_P3_LA3` not among them; about 3.5 min |
| Steps 3 to 5 | TPROF `GAPFILL_AB_P3_LA1`; ProcessId 100004741427305: TaxAuthorityProfileVO 1 row, 0 failed, 50 objects |
| Step 6 | profiles 3 -> 4, added `GAPFILL_AB_P3_LA3`, removed 0, changed 0: PASS |
