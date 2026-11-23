---
skill_id: "gosaas.gap-fills.common-features.manage-party-fiscal-classifications"
name: "Manage Party Fiscal Classifications (GoSaaS gap fill)"
description: "Create a new party fiscal classification type, based on an existing trading community class category, through FSCR's setup-task CSV export and import (ORA_ZX_PARTY_CLASS package), copying an existing type, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 3, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS"
task_name: "Manage Party Fiscal Classifications"
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
  - "at least one existing party fiscal classification type (its class category is reused)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new party fiscal classification type. No tax regime, party or rule uses it, so it changes no tax result. It may not be deletable; plan as if it stays."
---

# Manage Party Fiscal Classifications (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A party fiscal classification type lets tax rules test how a supplier, customer or other party is classified. Each type points to a trading community **class category** (`OwnerTableCode=HZ_CLASS_CATEGORY`, `OwnerIdChar=<category code>`); the codes of that category become the type's codes. A type does nothing until a tax regime is associated with it and a rule uses it. This skill creates the **type only** (no regime association, no codes of its own), reusing the class category of an existing type.

## When to use
- Someone asks to create a **new** party fiscal classification type for task `ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS`.
- Do **not** use it to change existing types, to add tax regime associations or to classify parties. New records only.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
           If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T        = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
RUN      = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX   = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE     = new ClassificationTypeCode: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
NAME     = new ClassificationTypeName, e.g. "GAPFILL XX party fiscal class 1" (no "|" character)
TEMPLATE = ClassificationTypeCode of one existing party fiscal classification type (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect about 70 files (VERIFIED, 150 to 200 s). The ones this skill uses: `ORA_ZX_PARTY_CLASS.csv` (36 columns: `ClassificationTypeCode, ClassificationTypeCategCode, ClassificationTypeLevelCode, ClassificationTypeName, EffectiveFrom, EffectiveTo, OwnerIdChar, OwnerTableCode, RecordTypeCode, ...`) and `ORA_ZX_PARTY_CLASS_TRANSLATION.csv`. The same package holds the other fiscal classification families (product, transaction, legal party, user defined); leave them alone.
- If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries. If it still fails: **stop**.

## Step 3. Choose a template type and check the code
```bash
python -I -c "import csv,sys; [print(r['ClassificationTypeCode'],'|',r['ClassificationTypeName'],'| categ',r['ClassificationTypeCategCode'],'| class category',r['OwnerIdChar'],'| from',r['EffectiveFrom'],'to',r['EffectiveTo'] or '-','|',r['RecordTypeCode']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_PARTY_CLASS.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
1. **TEMPLATE** = the **first listed** type whose code does not start with a test prefix and that has no end date. The new type copies its category code (`PARTY_FISCAL_CLASS`), level and **class category** (`OwnerIdChar`). VERIFIED
2. Reusing the class category of an existing type was **accepted** (two types now point to the same category, both work in the export). VERIFIED. If the person names another class category, put it in `OwnerIdChar` with `--set`; that was not tested (GUESS).
3. If the file has **no row**, **stop**: a type written out in full was not tested.
4. **CODE is free:** it must not be in the list (the builder checks it again).

## Step 4. Build a package with only the new type
```bash
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_PARTY_CLASS.csv \
  --match "ClassificationTypeCode=<TEMPLATE>" \
  --set "ClassificationTypeCode=<CODE>" --set "ClassificationTypeName=<NAME>" \
  --set "EffectiveFrom=<yyyy/mm/dd>" --set "RecordTypeCode=USER_DEFINED" --clear EffectiveTo --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_ZX_PARTY_CLASS_TRANSLATION.csv \
  --match "ORA_ZX_PARTY_CLASS.ClassificationTypeCode=<TEMPLATE>" --match "Language=US" \
  --set "ORA_ZX_PARTY_CLASS.ClassificationTypeCode=<CODE>" --set "ClassificationTypeName=<NAME>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name pfc_new.zip --prefix <PREFIX> \
  --key "ORA_ZX_PARTY_CLASS.csv=ClassificationTypeCode" \
  --key "ORA_ZX_PARTY_CLASS_TRANSLATION.csv=ORA_ZX_PARTY_CLASS.ClassificationTypeCode,Language" \
  --prefix-col "ORA_ZX_PARTY_CLASS.csv=ClassificationTypeCode" --max-len "ClassificationTypeCode=30" @"<RUN>/rows.txt"
```
- `RecordTypeCode=USER_DEFINED`: seeded templates say `SEEDED`; user-made rows in this package say `USER_DEFINED`. VERIFIED
- `EffectiveFrom`: the first day of this year or today (we used 2026/01/01). VERIFIED
- The builder must print `ORA_ZX_PARTY_CLASS.csv: 1 new rows`, `ORA_ZX_PARTY_CLASS_TRANSLATION.csv: 1 new rows` and every other file `0 new rows`. It stops if CODE exists, lacks the prefix or is too long.
- If the translation file has no `Language=US` row for TEMPLATE, use the language your environment has.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact CODE before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS --task-name "Manage Party Fiscal Classifications" \
  --zip-file "<RUN>/payload/pfc_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later; the ESS request number does not open it.
- About 2 minutes. Print a short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: PartyFiscalClassificationType. Status: Completed successfully ... A total of 1 rows were processed. 0 rows of them failed`, the other classification families `0 rows were processed` (normal: you sent none), and `Total Objects Failed: 0` (about 41 objects processed is normal). **`PartyFiscalClassificationType ... 0 rows were processed` is a failure.**
- **If the script loses the connection after the process started**, the import still runs in Oracle. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_ZX_PARTY_CLASS.csv=ClassificationTypeCode" \
  --key "ORA_ZX_PARTY_CLASS_TRANSLATION.csv=ORA_ZX_PARTY_CLASS.ClassificationTypeCode,Language" \
  --expect "ORA_ZX_PARTY_CLASS.csv=<CODE>" --expect "ORA_ZX_PARTY_CLASS_TRANSLATION.csv=<CODE>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your type and its translation were added; all other files unchanged. Oracle may fill `Delimiter` (`/`) itself; that is normal. VERIFIED. If someone else changed fiscal classifications between your two exports, judge your own rows plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep every file and the metadata XML unchanged in layout; only the new type and its translation go in.
3. Never add a tax regime association (`ORA_ZX_PARTY_CLASS_TYPE_TAX_REGIME`) or class codes in a test: they make the type usable by tax rules.
4. Test records may stay for good. This skill never deletes. Record every created type.
5. No REST resource was searched; the export compare is the proof.
6. Not tested: a class category not already used by another type, types with regime associations, end-dated types, the other fiscal classification families in the same package.
7. Tested on one environment (release 11.13.26.10.0).
8. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `template_row.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 2 party fiscal classification types (both seeded); about 200 s |
| Template | the first listed type (seeded, class category of supplier types) |
| New record | `GAPFILL_AB_P3_PFC1`, "GAPFILL AB P3 party fiscal class 1", from 2026/01/01, `USER_DEFINED`, same class category |
| Import | 1 attempt (ProcessId 100004741402751), about 2 min: PartyFiscalClassificationType 1 row, 0 failed |
| Export after + compare | 3 types; added 1 + 1, removed 0, changed 0, all other files unchanged: PASS |
