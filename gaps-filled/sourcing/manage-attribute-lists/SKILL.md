---
skill_id: "gosaas.gap-fills.sourcing.manage-attribute-lists"
name: "Manage Attribute Lists (GoSaaS gap fill)"
description: "Create a new line attribute list with one attribute group and one attribute through FSCR's setup-task CSV export and import (rows written in full), then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing batch 02, 2026-11-27. Written and tested live on one test environment. NOT official FSCR."
task_code: "PON_MANAGE_ATTRIBUTE_LISTS"
task_name: "Manage Attribute Lists"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only exports and REST reads; one CSV import that creates one new attribute list with one group and one text attribute. There is no delete by CSV: plan as if it stays."
---

# Manage Attribute Lists (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-27) · **GUESS** = judgment, not tested.

## What it is and when to use
An attribute list is a reusable set of line attributes (questions a supplier answers per negotiation line, for example warranty or packaging) that a buyer can add to a negotiation line. The task's package has 4 files: the list (`PON_LINE_ATTR_LISTS`), its attribute groups (`ORA_PON_LIST_ATTRIBUTE_GROUPS`, one per section), its attributes (`PON_LIST_ATTRIBUTES`) and acceptable-value scores (`PON_LIST_ATTR_SCORES`). VERIFIED. This skill creates a NEW list with one group and one optional text attribute. There is no REST resource for attribute lists (VERIFIED: `attributeLists`, `negotiationAttributeLists` give HTTP 404), so the second export is the read-back.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project".
         Check: `git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"` must print the OK line.
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
LIST   = new list name: PREFIX + short name, e.g. GAPFILL_AB_ATL1
SECTION= a line attribute group code from the lookup type PON_LINE_ATTRIBUTE_GROUPS (read live in Step 2), e.g. GENERAL
ATTR   = the attribute's question text, e.g. GAPFILL AB test attribute (no "|")
```
Every `<FSCR>`, `<GAPS>`, `<RUN>`, `<...>` in the commands below is a placeholder: put the real value in its place before you run the command.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`, and never pass `$PWD`: FSCR's REST client then fails with `No module named 'rest_client_common'`). VERIFIED
- Shell variables do **not** survive from one tool call to the next: set them again in every call.
- **Never read the import log with cat, sed or grep** (it holds the environment name and the submitting user). Read it only with `python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. VERIFIED
- **Never print the export CSVs whole** (`CreatedBy` / `LastUpdatedBy` hold user names) and never print the metadata XML. Print only the columns shown below. Existing records may carry people's names: do not copy them into reports.
- FSCR's export and import file names start with the environment name; do not copy them into reports.
- Save each export's output to a file and print only whether a ZIP was written. If no ZIP was written, run the export again into a new folder (read-only; up to 3 times) and use **that** folder in every later command.
- Save the import's screen output to `<RUN>/import.out`; the ProcessId is on the line `Started setup task CSV import process: <n>`. `grep -o` on `import.out` is safe; never print `import.out` whole. Do not wrap the import in a shell `timeout`.
- No ProcessId line after an error: **do not import again.** Repeat the Step 4 read-back every minute for 10 minutes; if the record shows up, go on; if not, nothing was created (prove it with the after-export); a second import needs the person's approval again.
- Connection dropped **after** the ProcessId line: the import still runs; **never import again**. Fetch its log with `cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code PON_MANAGE_ATTRIBUTE_LISTS --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"`, then read it with `read_import_log.py`.

## Sign-in
- If a call says HTTP 401/403, or hangs with no output (an expired token waits for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead.
- Never print tokens, the server address or user names.

## Prerequisites
None to create. SECTION must be an enabled code of the lookup type `PON_LINE_ATTRIBUTE_GROUPS` (Step 2 reads it live).

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PON_MANAGE_ATTRIBUTE_LISTS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "
import csv,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.csv')): print(os.path.basename(f), sum(1 for _ in csv.DictReader(open(f,encoding='utf-8-sig'))), 'rows')
" "<RUN>/export_before/unz"
```
Expect 5 files (VERIFIED): the metadata XML and the 4 CSVs named above. On our environment all 4 were **empty** (no list ever made), so the rows are written in full below. If LIST is already in `PON_LINE_ATTR_LISTS.csv`, pick another name.

## Step 2. Check SECTION live and build the package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/standardLookups/PON_LINE_ATTRIBUTE_GROUPS?expand=lookupCodes&onlyData=true" --no-open-browser --output "<RUN>/groups.json" > "<RUN>/groups.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys; c={x['LookupCode']:x['EnabledFlag'] for x in json.load(open(sys.argv[1]))['lookupCodes']}
sys.exit('STOP: SECTION is not an enabled code of PON_LINE_ATTRIBUTE_GROUPS') if c.get(sys.argv[2])!='Y' else print('SECTION ok')
" "<RUN>/groups.json" <SECTION> && \
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key PON_LINE_ATTR_LISTS.csv=AttributeListName \
  --row "PON_LINE_ATTR_LISTS.csv|AttributeListName=<LIST>|Description=<text>|ListStatus=ACTIVE|AttrLevel=LINE|TwoPartFlag=N" \
  --row "ORA_PON_LIST_ATTRIBUTE_GROUPS.csv|PON_LINE_ATTR_LISTS.AttributeListName=<LIST>|AuctionHeaderId=-1|LineNumber=-1|SectionName=<SECTION>|AttrGroupSeqNumber=10" \
  --row "PON_LIST_ATTRIBUTES.csv|PON_LINE_ATTR_LISTS.AttributeListName=<LIST>|ORA_PON_LIST_ATTRIBUTE_GROUPS.AttrGroupSeqNumber=10|AuctionHeaderId=-1|LineNumber=-1|SectionName=<SECTION>|AttrGroupSeqNumber=10|SequenceNumber=10|AttributeName=<ATTR>|Datatype=TXT|ResponseType=OPTIONAL|AttrLevel=LINE|AttrDispSeqNumber=10|DisplayTargetFlag=N"
```
- **`AuctionHeaderId=-1` and `LineNumber=-1` are required** on the group and attribute rows: a list is not tied to a real negotiation, and -1 is the placeholder. Without them Oracle refuses every row: `JBO-27014: Attribute AuctionHeaderId in SourcingRequirementSectionEO is required` (and in `SourcingRequirementAndAttributeEO`), all 4 objects fail and nothing is created. VERIFIED (try 1 failed, try 2 with -1 passed; the after-export keeps -1)
- Expect `ORA_PON_LIST_ATTRIBUTE_GROUPS.csv: 1 row(s)`, `PON_LINE_ATTR_LISTS.csv: 1 row(s)`, `PON_LIST_ATTRIBUTES.csv: 1 row(s)`, `PON_LIST_ATTR_SCORES.csv: 0 row(s)`. VERIFIED
- `Datatype` TXT = text answer; `ResponseType` OPTIONAL = the supplier may leave it empty. VERIFIED (accepted). Other values (NUM, DAT, REQUIRED, DISPLAY_ONLY), scores and two-part lists: GUESS, not tested.

## Step 3. Import
Approval: the person must approve the environment, the task and the new record's name before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code PON_MANAGE_ATTRIBUTE_LISTS --task-name "Manage Attribute Lists" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Keep the ProcessId. Success (VERIFIED): 4 business objects (List Attribute Group, Line Attribute List, List Attribute, List Attribute Score) `Completed successfully`, `Total Objects Failed: 0`, `IMPORT: PASS`.

## Step 4. Read back (second export)
Run this step also when the import failed (a refused file creates nothing; the after-export proves it).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PON_MANAGE_ATTRIBUTE_LISTS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
python -I -c "
import csv,sys,glob,os
skip=('CreatedBy','LastUpdatedBy','CreationDate','LastUpdateDate','LastUpdateLogin')
for f in sorted(glob.glob(sys.argv[1]+'/*.csv')):
    rows=[r for r in csv.DictReader(open(f,encoding='utf-8-sig')) if sys.argv[2] in (r.get('AttributeListName'),r.get('PON_LINE_ATTR_LISTS.AttributeListName'))]
    print(os.path.basename(f), len(rows), 'row(s) of LIST')
    for r in rows: print('   ',{k:v for k,v in r.items() if v and k not in skip})
" "<RUN>/export_after/unz" <LIST>
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key PON_LINE_ATTR_LISTS.csv=AttributeListName --key ORA_PON_LIST_ATTRIBUTE_GROUPS.csv=PON_LINE_ATTR_LISTS.AttributeListName \
  --key PON_LIST_ATTRIBUTES.csv=PON_LINE_ATTR_LISTS.AttributeListName --key PON_LIST_ATTR_SCORES.csv=PON_LINE_ATTR_LISTS.AttributeListName \
  --expect PON_LINE_ATTR_LISTS.csv=<LIST>
```
PASS = LIST has 1 list row (ACTIVE, LINE), 1 group row and 1 attribute row with your values, 0 score rows, and the compare prints `RESULT: PASS` (nothing removed or changed). VERIFIED

## Rules and limits
1. New lists only; never send an existing list name (it would update it).
2. The new list is ACTIVE: buyers can add it to negotiation lines. Test lists stay (no delete by CSV).
3. One group and one attribute were tested; more attributes = more `PON_LIST_ATTRIBUTES.csv` rows with new `SequenceNumber` values (GUESS).
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-27). Do not reuse these names.
Counts are from our run; later runs see more rows (every test adds records). That is expected.
| Step | Result |
|---|---|
| Export before | 5 files, all 4 CSVs empty |
| Try 1 | no AuctionHeaderId: ProcessId 100004743465828, JBO-27014 AuctionHeaderId required, 4 objects failed; export proves nothing created |
| Try 2 | `GAPFILL_AB_S2_ATL1`, section GENERAL, AuctionHeaderId/LineNumber -1: ProcessId 100004744440351, 4 objects, 0 failed |
| Export after | 1 list (ACTIVE, LINE), 1 group, 1 attribute (TXT, OPTIONAL), 0 scores: PASS |
