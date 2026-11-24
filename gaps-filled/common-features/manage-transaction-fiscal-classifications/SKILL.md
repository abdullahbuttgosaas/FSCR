---
skill_id: "gosaas.gap-fills.common-features.manage-transaction-fiscal-classifications"
name: "Manage Transaction Fiscal Classifications (GoSaaS gap fill)"
description: "Create one new transaction business category code (a transaction fiscal classification code) under an existing parent code, through FSCR's setup-task CSV export and FSM CSV import of the tax fiscal classification package, with its translation and denormalized rows built by a helper from a template code, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 2, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS"
task_name: "Manage Transaction Fiscal Classifications"
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
  - "gosaas common-features/manage-profile-options/scripts/copy_parent_rows.py"
  - "gosaas common-features/manage-transaction-fiscal-classifications/scripts/fiscal_code_rows.py"
reused_by:
  - "common-features/manage-transaction-based-fiscal-classifications (family user)"
  - "common-features/manage-product-fiscal-classifications (family product)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new classification code with its translation and denormalized rows. The seeded parent type row is sent unchanged. It may not be deletable; plan as if it stays."
---

# Manage Transaction Fiscal Classifications (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill that creates these codes. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
Transaction fiscal classifications are the codes of the seeded type `TRX_BUSINESS_CATEGORY` (transaction business categories). Level-1 codes (for example `PURCHASE_TRANSACTION`) are seeded and tied to event classes; customers add codes **under** them. This skill adds **one new code under an existing parent**, copied from a template code that already sits under a parent. No tax rule, tax default or transaction uses the new code until someone sets it up.

## When to use
- Someone asks to create a **new** transaction fiscal classification code for task `ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS`.
- Do **not** use it to change or end-date existing codes, or to add level-1 codes. New records only.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
           If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts            (generic helpers)
SK       = <GAPS>/common-features/manage-profile-options/scripts              (copy_parent_rows.py)
S        = <GAPS>/common-features/manage-transaction-fiscal-classifications/scripts   (fiscal_code_rows.py)
RUN      = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, no folder in its path named exactly "project"
PREFIX   = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE     = the new ClassificationCode: upper case letters, digits and _, starting with PREFIX (max 30, GUESS)
NAME     = the new ClassificationName (no "|"), e.g. "Gapfill <INITIALS> TBC1"
TEMPLATE = an existing code that has a parent (Step 3); PARENT = that template's ParentClassificationCode
FROM     = EffectiveFrom, yyyy/mm/dd (first day of this year or today)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL, the server address or user names (the export and the process log hold user names: print only the lines this skill shows).
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect about 73 files (VERIFIED, 2 to 2.5 minutes): every tax fiscal classification family. This task uses `ORA_ZX_TRANSACTION.csv` (the type, 1 row `TRX_BUSINESS_CATEGORY`), `ORA_ZX_TRANSACTION_CODE.csv` (codes, about 250), `ORA_ZX_TRANSACTION_CODE_TRANSLATION.csv`, `ORA_ZX_TRAN_DENORM_CLASS_CODE.csv` and its `_TRANSLATION`.
- If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries; then **stop**.

## Step 3. Choose TEMPLATE and PARENT, check CODE
```bash
python -I -c "import csv,sys; [print(r['ClassificationCode'],'| parent',r['ParentClassificationCode'],'|',r['RecordTypeCode'],'| country',r['CountryCode'] or '-') for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_TRANSACTION_CODE.csv',encoding='utf-8-sig')) if r['ParentClassificationCode']]" "<RUN>/export_before/unz" | head -40
```
1. **TEMPLATE**: a code **with a parent**. Prefer one with `USER_DEFINED` (made by a customer, so known to work); otherwise the first listed. VERIFIED (we used a `USER_DEFINED` code under `PURCHASE_PREPAYMENTTRANSACTION`). PARENT = its parent; the new code lands under the same parent.
2. If the same TEMPLATE code sits under several parents, pass `--template-parent <PARENT>` in Step 4 (the helper stops otherwise).
3. CODE must not be in the list (the helper and the builder check again).

## Step 4. Build: 4 rows from the helper, then the parent type row unchanged
```bash
python -I "<S>/fiscal_code_rows.py" --export-dir "<RUN>/export_before/unz" --family trx \
  --template-code "<TEMPLATE>" --template-parent "<PARENT>" --code <CODE> --name "<NAME>" --from <FROM> --out "<RUN>/rows.txt"
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name fc_new.zip --prefix <PREFIX> --max-rows 80 \
  --key "ORA_ZX_TRANSACTION_CODE.csv=ClassificationTypeCode,ClassificationCode,ParentClassificationCode" \
  --key "ORA_ZX_TRANSACTION_CODE_TRANSLATION.csv=ORA_ZX_TRANSACTION_CODE.ClassificationTypeCode,ORA_ZX_TRANSACTION_CODE.ClassificationCode,ORA_ZX_TRANSACTION_CODE.ParentClassificationCode,Language" \
  --key "ORA_ZX_TRAN_DENORM_CLASS_CODE.csv=ClassificationTypeCode,ClassificationCode,ConcatClassifCode" \
  --key "ORA_ZX_TRAN_DENORM_CLASS_CODE_TRANSLATION.csv=ORA_ZX_TRAN_DENORM_CLASS_CODE.ClassificationTypeCode,ORA_ZX_TRAN_DENORM_CLASS_CODE.ClassificationCode,ORA_ZX_TRAN_DENORM_CLASS_CODE.ConcatClassifCode,Language" \
  --prefix-col "ORA_ZX_TRANSACTION_CODE.csv=ClassificationCode" --max-len "ClassificationCode=30" @"<RUN>/rows.txt"
python -I "<SK>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name fc_new.zip --file ORA_ZX_TRANSACTION.csv --where ClassificationTypeCode=TRX_BUSINESS_CATEGORY
```
- The helper prints `wrote 4 rows` and the `PARENT:` line (the type file and type code to copy). The builder must print `1 new rows` for the 4 files above and `0 new rows` for every other file. Import the ZIP that `copy_parent_rows.py` re-zipped.
- What the helper does: copies the template's code, translation, denormalized and denormalized translation rows; puts CODE and NAME wherever the template's code and name were (also at the end of the path columns such as `ConcatClassifCode`); `RecordTypeCode=USER_DEFINED`; `EffectiveFrom=<FROM>`; clears `EffectiveTo`, `CountryCode` (so the code is not limited to the template's country; add `--keep-country` to keep it) and the audit columns.
- **The parent type row is required** (VERIFIED: without it the import says `Parent row is missing in file ORA_ZX_TRANSACTION.csv` and processes **0 objects**). It is a seeded row sent **unchanged**; the Step 6 compare proves it stays unchanged. This is the only seeded row the package may hold.
- **The denormalized rows are needed** (VERIFIED: a code sent without them was created, but Oracle did **not** build its denormalized row, which screens and rules use for lookups; with them, all 4 rows exist).

## Step 5. Import
**Approval.** The person must approve the environment, the task, the exact CODE and its PARENT before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS --task-name "Manage Transaction Fiscal Classifications" \
  --zip-file "<RUN>/payload/fc_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later.
- About 1.5 minutes. Print a short summary of the process log (row counts, totals, errors only; no user names):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(x for x in re.findall(r'Detail Object: [^.]+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Parent row is missing[^.]{0,120}|JBO-[0-9]+: [^.]{0,160}|ZX_[A-Z_]+: [^.]{0,160}',t) if ' 0 rows were processed' not in x))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: TransactionBusinessCategoryType ... A total of 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`, about 42 objects processed. The log counts the **type** row only; the code rows do not get their own line. So the import log alone does **not** prove the code: Step 6 does.
- `Total Objects Processed: 0` = nothing was imported (see the parent row above).
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: copy the error, change one thing, retry at most 3 times. A generic database error at the insert (for example `JBO-26041`): first fill `CreatedBy` and `LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never printed). GUESS (not needed here).

## Step 6. Read back: second export and compare (the proof)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then (PATH = `<PARENT>/<CODE>`)
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_ZX_TRANSACTION.csv=ClassificationTypeCode" \
  --key "ORA_ZX_TRANSACTION_CODE.csv=ClassificationTypeCode,ClassificationCode,ParentClassificationCode" \
  --key "ORA_ZX_TRANSACTION_CODE_TRANSLATION.csv=ORA_ZX_TRANSACTION_CODE.ClassificationTypeCode,ORA_ZX_TRANSACTION_CODE.ClassificationCode,ORA_ZX_TRANSACTION_CODE.ParentClassificationCode,Language" \
  --key "ORA_ZX_TRAN_DENORM_CLASS_CODE.csv=ClassificationTypeCode,ClassificationCode,ConcatClassifCode" \
  --key "ORA_ZX_TRAN_DENORM_CLASS_CODE_TRANSLATION.csv=ORA_ZX_TRAN_DENORM_CLASS_CODE.ClassificationTypeCode,ORA_ZX_TRAN_DENORM_CLASS_CODE.ClassificationCode,ORA_ZX_TRAN_DENORM_CLASS_CODE.ConcatClassifCode,Language" \
  --expect "ORA_ZX_TRANSACTION_CODE.csv=TRX_BUSINESS_CATEGORY,<CODE>,<PARENT>" \
  --expect "ORA_ZX_TRANSACTION_CODE_TRANSLATION.csv=TRX_BUSINESS_CATEGORY,<CODE>,<PARENT>,US" \
  --expect "ORA_ZX_TRAN_DENORM_CLASS_CODE.csv=TRX_BUSINESS_CATEGORY,<CODE>,<PATH>" \
  --expect "ORA_ZX_TRAN_DENORM_CLASS_CODE_TRANSLATION.csv=TRX_BUSINESS_CATEGORY,<CODE>,<PATH>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your 4 rows were added; the type row `ORA_ZX_TRANSACTION.csv` shows `changed 0`; nothing else removed or changed. VERIFIED. If someone else changed fiscal classifications between your two exports, judge your own rows plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. The package holds your 4 rows and the seeded type row unchanged; nothing else.
3. Test records may stay for good. This skill never deletes. Record every created code.
4. Not tested: level-1 codes, codes at level 3 or deeper (GUESS: the helper keeps the template's path, so a level-3 template gives a level-3 code), languages other than US, `--keep-country`.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts; `-I` for the helpers and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 73 files; 252 codes, 252 denormalized rows; about 2 min |
| Template | a `USER_DEFINED` code under `PURCHASE_PREPAYMENTTRANSACTION` |
| Try 1 | `GAPFILL_AB_P2_TBC1`, code + translation only, no parent row: `Parent row is missing in file ORA_ZX_TRANSACTION.csv`, 0 objects processed, nothing created (ProcessId 100004742413180) |
| Try 2 | same + seeded type row unchanged (ProcessId 100004741417628): code and translation created; **no denormalized row** built by Oracle |
| Try 3 | `GAPFILL_AB_P2_TBC2`, all 4 rows + type row (ProcessId 100004741418933), about 1.5 min: compare added 1 + 1 + 1 + 1, type row changed 0: PASS |
