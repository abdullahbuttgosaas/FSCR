---
skill_id: "gosaas.gap-fills.common-features.manage-billing-extensions"
name: "Manage Billing Extensions: new project billing extension definition (GoSaaS gap fill)"
description: "Create one new project billing extension definition (not assigned to any invoice or revenue method) through FSCR's setup-task CSV export and FSM CSV import (PJB_BILLING_EXTENSIONS), then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 10, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "PJB_MANAGE_BILLING_EXTENSIONS"
task_name: "Manage Billing Extensions"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories (generic helper scripts build_fsm_package.py, compare_fsm_exports.py)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one billing extension definition. It does nothing until someone assigns it to an invoice or revenue method (other tasks). It may not be deletable; plan as if it stays."
---

# Manage Billing Extensions (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A billing extension (Project Billing) names a procedure that Oracle calls while it creates invoices or revenue, for example to add billing events. This task only **defines** the extension (name, calling process, procedure name, order, flags). It runs only after it is assigned to an invoice method or revenue method (separate tasks "Manage Invoice Methods / Revenue Methods: Billing Extension Assignments"). Use this skill to create **one new, unassigned** definition.
**Safety:** a new definition changes nothing on its own. Never assign it to a method on a shared environment, and never change an existing extension.
There is no REST resource for it (`billingExtensions`: HTTP 404, VERIFIED); the export is the read-back.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
W       = <GAPS>/common-features/scripts/rest_call.py                (REST reads; runs FSCR's client unchanged)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
EXT     = new BillingExtensionName, starting with PREFIX (VERIFIED with 18 characters)
PROC    = the procedure name to store, e.g. <PREFIX>PKG.<short> (VERIFIED: Oracle does not check that it exists when the definition is saved)
CALL    = calling process code: I = Invoice or R = Revenue (Prerequisite 1)
START   = StartDateActive, YYYY/MM/DD (if the brief gives none: the first day of the current year)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
1. **CALL code, read live** (lookup `PJB_BILL_EXT_CALL_PROCESS`):
   `cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/standardLookups/PJB_BILL_EXT_CALL_PROCESS --query expand=lookupCodes --query onlyData=true --no-open-browser --output call.json > call.log 2>&1`
   then `python -I -c "import json; print([(c['LookupCode'],c['Meaning'],c['EnabledFlag']) for c in json.load(open('call.json'))['lookupCodes']])"` → VERIFIED: `I` Invoice, `R` Revenue. The meaning (`INVOICE`) is **not** accepted: try 1 failed with `PJB_BILL_EXT_PROC_INVALID You must set the billing extension calling process option for either invoice or revenue` (VERIFIED, nothing created).
2. EXT is free: after Step 2, EXT must not be in `PJB_BILLING_EXTENSIONS.csv` (the build helper also stops if it is).

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PJB_MANAGE_BILLING_EXTENSIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 1 CSV + `ASM_SETUP_CSV_METADATA.xml` (VERIFIED, about 1 minute): `PJB_BILLING_EXTENSIONS.csv`, 33 columns (`BillingExtensionName, CallingProcess, ProcedureName, ProcessingOrder, StartDateActive, EndDateActive, ExtensionDesc, BeforePreProcessFlag, BeforeDeletionFlag, AfterDraftCreationFlag, TrxIndependentFlag, AmtReqdFlag, PercentageReqdFlag, DefaultEventDescription, PredefinedFlag, AttributeCategory, Attribute1..15, EventTypeName, CostPlanTypeName`). Our environment had **0 rows** (VERIFIED), so the row is written in full (Step 3). If the export stops with no ZIP, run it again into a new folder, up to 3 tries.

## Step 3. Build the package (1 row)
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name billing_ext_new.zip --prefix <PREFIX> \
  --key "PJB_BILLING_EXTENSIONS.csv=BillingExtensionName" \
  --prefix-col "PJB_BILLING_EXTENSIONS.csv=BillingExtensionName" \
  --row "PJB_BILLING_EXTENSIONS.csv|BillingExtensionName=<EXT>|CallingProcess=<CALL>|ProcedureName=<PROC>|ProcessingOrder=10|StartDateActive=<START>|ExtensionDesc=test billing extension, not assigned|BeforePreProcessFlag=N|BeforeDeletionFlag=N|AfterDraftCreationFlag=N|TrxIndependentFlag=N|AmtReqdFlag=N|PercentageReqdFlag=N|PredefinedFlag=N"
```
- These columns were enough (VERIFIED). Leave `EndDateActive`, `EventTypeName`, `CostPlanTypeName`, `DefaultEventDescription` and the attributes empty. `PredefinedFlag=N` always (Y is for Oracle's own).
- Not tried: `TrxIndependentFlag=Y`, `AmtReqdFlag`/`PercentageReqdFlag=Y`, an event type (GUESS: an event type must exist first).

## Step 4. Import
**Approval.** The person must approve the environment, the task and EXT before the import. If their brief names it (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code PJB_MANAGE_BILLING_EXTENSIONS --task-name "Manage Billing Extensions" \
  --zip-file "<RUN>/payload/billing_ext_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`).
- Short summary of the log (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED, about 45 s): `A total of 1 rows were processed. 0 rows of them failed`, `Project Billing Extension. Status: Completed successfully`, `Total Objects Failed: 0`.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 5.
- Failed row: copy the message, change one thing, new EXT, retry; at most 3 tries. A refused row creates nothing (VERIFIED: the after-export did not hold try 1). `JBO-26041` at the insert: fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it). GUESS

## Step 5. Read back (the proof)
Export again (Step 2 into `<RUN>/export_after`). **Check it made a ZIP** first; if not, run it again into a new folder (up to 3 tries) and use that folder. Then:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "PJB_BILLING_EXTENSIONS.csv=BillingExtensionName" --expect "PJB_BILLING_EXTENSIONS.csv=<EXT>"
python -I -c "import csv,sys; [print({k:r[k] for k in ('BillingExtensionName','CallingProcess','ProcedureName','ProcessingOrder','StartDateActive','PredefinedFlag')}) for r in csv.DictReader(open(sys.argv[1]+'/PJB_BILLING_EXTENSIONS.csv',encoding='utf-8-sig')) if r['BillingExtensionName']==sys.argv[2]]" "<RUN>/export_after/unz" "<EXT>"
```
`RESULT: PASS` (only your row added, 0 removed, 0 changed) and the row shows your CALL, PROC and START (VERIFIED).

## Rules and limits
1. New, unassigned definitions only. Never change, end-date or re-import an existing extension; never assign one to a method on a shared environment.
2. Oracle stores the procedure name without checking it (VERIFIED); a real extension needs a real procedure, which is outside this skill.
3. Test records may stay for good. This skill never deletes.
4. Tested on one environment (release 11.13.26.10.0). Python flags: `-B` without `-I` for FSCR scripts and `rest_call.py`; `-I` for the other helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B10_BX1`, `CallingProcess=INVOICE` (ProcessId 100004743405841) | refused: `PJB_BILL_EXT_PROC_INVALID`; 1 row processed, 1 failed; not in the after-export |
| 2 | `GAPFILL_AB_B10_BX2`, `CallingProcess=I`, order 10, from 2026/01/01 (ProcessId 100004743406265) | 1 row processed, 0 failed; export compare: 1 added, 0 changed: PASS |
