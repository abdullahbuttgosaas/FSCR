---
skill_id: "gosaas.gap-fills.common-features.manage-invoice-method-billing-ext-assignments"
name: "Manage Invoice Methods: Billing Extension Assignments: create a new extension-based invoice method with one billing extension assigned (GoSaaS gap fill)"
description: "Creates one NEW invoice method (BillMethodFlag I) with its translation row and one billing extension assignment through FSCR's setup-task CSV export/import of PJB_MANAGE_INVOICE_METHOD_BILLING_EXTENSION_ASSIGNMENTS, and proves it with an export compare. The same skill, with R instead of I, is used by the revenue-method gap skill. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 12, 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "PJB_MANAGE_INVOICE_METHOD_BILLING_EXTENSION_ASSIGNMENTS"
task_name: "Manage Invoice Methods: Billing Extension Assignments"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "tested (batch 12)"
depends_on:
  - "PJB_MANAGE_BILLING_EXTENSIONS (gap skill manage-billing-extensions: a billing extension whose CallingProcess fits the method)"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (build_fsm_package.py, compare_fsm_exports.py)"
side_effects:
  - "Creates one new invoice method (active) and one assignment of an extension to it. Nothing uses a new method until a contract or bill plan names it."
---

# Manage Invoice Methods: Billing Extension Assignments (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV); it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
In Project Billing an **invoice method** says how invoice amounts are found. An **extension-based** method calls billing extensions (custom procedures, defined with the task Manage Billing Extensions). This task assigns extensions to methods. The task's CSV package holds the method, its translation and its assignments (one hierarchical package: method = parent, assignment = child), so a **new method with its assignment** goes in one ZIP.
**Safety:** create a NEW method with your prefix. Never add an assignment to an existing method (that changes how existing contracts invoice), and never re-import an existing method.
No REST resource was found (`invoiceMethodsLOV`, `billingMethodsLOV`: HTTP 404, VERIFIED): the export is the read-back.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
METHOD  = the new method name, starting with PREFIX (VERIFIED with 18 characters)
EXT     = an existing billing extension name with CallingProcess I (Invoice) (Prerequisite 1)
TASK    = PJB_MANAGE_INVOICE_METHOD_BILLING_EXTENSION_ASSIGNMENTS ; TASKNAME = Manage Invoice Methods: Billing Extension Assignments
FLAG    = I   (I = invoice method; the revenue-method skill uses R)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the server address or user names; FSCR's output file names hold the environment name: never copy those lines into a report. The process log holds the submitter's user name: read it only with the summary command of Step 5.
- On HTTP 401/403, an expired token or a hang: sign in as in FSCR `core/auth/fusion-oauth-authentication` (`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`, in the background; a person completes the browser page; never type credentials).

## Prerequisites
1. **EXT exists with CallingProcess `I`.** Read-only export of task `PJB_MANAGE_BILLING_EXTENSIONS` (as in gap skill `manage-billing-extensions` Step 2, into `<RUN>/ext`) and check: `python -I -c "import csv,sys; print([r['CallingProcess'] for r in csv.DictReader(open(sys.argv[1]+'/PJB_BILLING_EXTENSIONS.csv',encoding='utf-8-sig')) if r['BillingExtensionName']==sys.argv[2]])" "<RUN>/ext/unz" "<EXT>"` → want `['I']` (`['R']` for the revenue skill). If you have none, create one with that skill (a new, unassigned extension with your prefix).
2. **METHOD is free:** not in `ORA_PJB_BILLING_METHOD.csv` of Step 2's export (the build helper also stops if it is).

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code <TASK> --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
VERIFIED (about 30 s): 3 CSV + `ASM_SETUP_CSV_METADATA.xml`:
- `ORA_PJB_BILLING_METHOD.csv` (`BillMethodFlag, BillMethodName, ActiveFlag, BillTypeClassCode, BillMethodDesc, IntercompanyMethod, LaborRateTypeCode, NlRateTypeCode, AsmFlag, CalculationLevelCode, MethodCfgType`)
- `ORA_PJB_BILLING_METHOD_TRANSLATION.csv` (`ORA_PJB_BILLING_METHOD.BillMethodFlag, ORA_PJB_BILLING_METHOD.BillMethodName, Language, BillMethodName, BillMethodDesc, SourceLang`)
- `ORA_PJB_BILLING_ASSIGNMENTS.csv` (`ORA_PJB_BILLING_METHOD.BillMethodFlag, ORA_PJB_BILLING_METHOD.BillMethodName, BillingExtensionName, ActiveFlag, ProcessingOrder, TransactionCode, Name, EventTypeName, EventAdjustFlag`)
The export holds only extension-based methods of this flag (our environment had 0 rows before our first test, VERIFIED; now it holds whatever earlier tests left), so the rows are written in full. If the export stops with no ZIP, run it again into a new folder, up to 3 tries.

## Step 3. Build the package (3 rows)
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name method_new.zip --prefix <PREFIX> \
  --row "ORA_PJB_BILLING_METHOD.csv|BillMethodFlag=<FLAG>|BillMethodName=<METHOD>|ActiveFlag=Y|BillTypeClassCode=AMOUNT_BASED|BillMethodDesc=test method, not used|IntercompanyMethod=N|AsmFlag=N|CalculationLevelCode=LINE" \
  --row "ORA_PJB_BILLING_METHOD_TRANSLATION.csv|ORA_PJB_BILLING_METHOD.BillMethodFlag=<FLAG>|ORA_PJB_BILLING_METHOD.BillMethodName=<METHOD>|Language=US|BillMethodName=<METHOD>|BillMethodDesc=test method, not used|SourceLang=US" \
  --row "ORA_PJB_BILLING_ASSIGNMENTS.csv|ORA_PJB_BILLING_METHOD.BillMethodFlag=<FLAG>|ORA_PJB_BILLING_METHOD.BillMethodName=<METHOD>|BillingExtensionName=<EXT>|ActiveFlag=Y"
```
- These values were enough (VERIFIED). `BillTypeClassCode=AMOUNT_BASED` (classification Amount Based) and `CalculationLevelCode=LINE` (lookup `PJB_EXTENSION_EXECUTION_LEVEL`: `LINE` Contract line, `PROJECT_CONTRACT_LINKAGE` Associated project; read live with `/fscmRestApi/resources/11.13.18.05/standardLookups/PJB_EXTENSION_EXECUTION_LEVEL/child/lookupCodes`, VERIFIED). Oracle sets `MethodCfgType=EXTENSION_BASED` and the assignment's `TransactionCode=BILLING_EVENT` itself, and shows `AsmFlag` empty although `N` was sent (VERIFIED in the after-export; not a change): leave the first two empty.
- **Leave `ProcessingOrder` empty.** With `ProcessingOrder=10` the row is refused: `You must leave the Processing Order attribute blank` (VERIFIED, nothing created).
- Other classifications (rate based, percent complete/spent) need rate types and were not tried (GUESS).

## Step 4. Import
**Approval.** The person must approve the environment, the task, METHOD and EXT before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code <TASK> --task-name "<TASKNAME>" \
  --zip-file "<RUN>/payload/method_new.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.log" 2>&1; grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.log"
```
- **Write down the ProcessId.**
- **Dropped connection after the process started:** the sign is that `<RUN>/import_result` has **no `*_process_log.txt`** (the log then ends with an error such as `getaddrinfo failed` or a time-out). `StatusCode: (no result yet)` lines alone are normal during any run. The import still runs. **Do not import again.** Fetch its log by ProcessId:
  `python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code <TASK> --process-id <ProcessId> --wait-seconds 300 --poll-interval 15 --no-open-browser --token-cache auto --output "<RUN>/import_result/x_process_log.txt"` (VERIFIED), then Step 5.

## Step 5. Check the import log (counts and messages only)
```bash
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
```
Expected (VERIFIED, about 25 to 45 s): `A total of 1 rows were processed. 0 rows of them failed`, both business objects (`Project Billing Extension Assignment`, `Project Invoice and Revenue Method`) `Completed successfully`, `Total Objects Failed: 0`. The log counts only the method row; the export compare (Step 6) proves the assignment.
Failed row: read `Message Text`, change one thing, use a new METHOD, retry; at most 3 tries. A refused row creates nothing (VERIFIED by the after-export).

## Step 6. Read back (the proof)
Export again (Step 2 into `<RUN>/export_after`; check it made a ZIP, else run again into a new folder). Then:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_PJB_BILLING_METHOD.csv=BillMethodName" --key "ORA_PJB_BILLING_ASSIGNMENTS.csv=ORA_PJB_BILLING_METHOD.BillMethodName" \
  --key "ORA_PJB_BILLING_METHOD_TRANSLATION.csv=ORA_PJB_BILLING_METHOD.BillMethodName" \
  --expect "ORA_PJB_BILLING_METHOD.csv=<METHOD>" --expect "ORA_PJB_BILLING_ASSIGNMENTS.csv=<METHOD>" --expect "ORA_PJB_BILLING_METHOD_TRANSLATION.csv=<METHOD>"
```
Want `RESULT: PASS`: in each of the 3 files only METHOD added, 0 removed, 0 changed (VERIFIED). All three `--expect` are needed (without one, the added translation row shows as PROBLEM). The assignment row shows your EXT, `ActiveFlag Y`, `TransactionCode BILLING_EVENT`.

## Rules and limits
1. New methods only. Never add or change an assignment of an existing method; never re-import an existing method.
2. A new method changes nothing until a contract or bill plan uses it; test methods may stay. This skill never deletes.
3. Tested on one environment (release 11.13.26.10.0). Python: `-B` without `-I` for FSCR scripts; `-I` for helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B12_IM1` + extension `GAPFILL_AB_B10_BX2`, `ProcessingOrder=10` (ProcessId 100004744403991; connection dropped, log fetched by ProcessId) | refused: "You must leave the Processing Order attribute blank"; nothing created |
| 2 | `GAPFILL_AB_B12_IM2`, same without ProcessingOrder (100004744404076) | 1 row processed, 0 failed; compare PASS (3 files, 1 added each) |
| fresh test | see CHANGELOG.md | |
