---
skill_id: "gosaas.gap-fills.common-features.test-business-unit"
name: "Test business unit: create your own prefixed business unit by FSM CSV, as a prerequisite (GoSaaS gap fill)"
description: "Creates ONE new business unit whose name starts with your prefix (no ledger, no legal entity, no business functions; default set COMMON; optionally an existing location as a reference) through the Manage Business Unit FSM CSV package, run with FSCR's export/import scripts. Used as the safe target for business-unit tasks (application tax options, associated business entities). Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 15, 2026-11-26. Tested live on one test environment. NOT official FSCR."
task_code: "FUN_MANAGE_BUSINESS_UNIT (prerequisite only; FSCR routes the task itself)"
type: "fsm-csv"
version: "0.1.1"
status: "tested (batch 15)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Step 3 creates a new business unit (an organization). The CSV route cannot delete it; it stays. Nothing existing is changed; a location named in it is only referenced."
---

# Test business unit (GoSaaS prerequisite skill)

> **Added by GoSaaS, not part of official FSCR.** Runs FSCR's scripts in place; edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
Some tasks store one record **per business unit** (application tax options; legal associations of a reporting unit to a business unit). Doing that on a real business unit changes real transactions. The safe way is **your own** business unit: a new record with your prefix that nobody uses. This skill makes it. A business unit made this way has no ledger, no legal entity, no business functions, and uses the seeded set `COMMON` (VERIFIED).
- Needs a **location** (`InternalLocationCode`) if you will associate it with a legal reporting unit (Associated Business Entities): without one, Oracle cannot identify the business unit there (VERIFIED). Give it at creation; the location is only referenced, not changed.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py   (offline builder, new rows only)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (exports hold user names); when this skill is a prerequisite, use its own RUN, not the task's (same folder names exp1, pay, imp)
BU    = your business unit name = PREFIX + short name, e.g. GAPFILL_XX_BU1
LOC   = optional: the code of an existing active location. Needed for legal associations: then copy the `BusinessEntityLocation` of an `OPERATING_UNIT` row in the Manage Associated Business Entities export (a location known to work; VERIFIED). Leave out if not needed.
```
Git Bash: paths as `E:/...` (never `$PWD` or `/e/...`); `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name).

## Prerequisites
1. The right to create business units. 2. BU does not exist yet (Step 1). Never create it twice.

## Step 1. Read-only export and check (VERIFIED, about 1 to 2 minutes)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code FUN_MANAGE_BUSINESS_UNIT --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
grep -c "\"<BU>\"" "<RUN>/exp1/unz/FUN_BUSINESS_UNIT.csv"
```
4 CSVs: `FUN_BUSINESS_UNIT` (one row per business unit), `FUN_BU_USAGE`, `FUN_BU_SERVICE_PROVIDERS`, and a set-assignment file. The grep must print 0. No ZIP: run again into a NEW folder, up to 3 tries. For LOC follow the LOC placeholder above (copy a location known to work; do not pick one by count). If the import wait drops, the last grep finds no process log: that is the case described under Step 3.

## Step 2. Build (offline, VERIFIED)
`OrganizationCode` is `<BU>$$?$$FUN_BUSINESS_UNIT` (VERIFIED: the form Oracle uses for business units made by CSV). In bash the `$` signs must be escaped as below.
```bash
cd "<RUN>"; N=<BU>
python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name bu.zip --prefix <PREFIX> --key "FUN_BUSINESS_UNIT.csv=Name" --prefix-col "FUN_BUSINESS_UNIT.csv=Name" \
 --row "FUN_BUSINESS_UNIT.csv|Name=$N|DefaultSetCode=COMMON|OrganizationCode=$N\$\$?\$\$FUN_BUSINESS_UNIT|Status=A|Classification=FUN_BUSINESS_UNIT|EffectiveStartDate=0001/01/01|EffectiveEndDate=4712/12/31|OrgInformationContext=FUN_BUSINESS_UNIT|ClassificationCode=FUN_BUSINESS_UNIT|ProfitCenterFlag=N"
grep -c '\$\$?\$\$FUN_BUSINESS_UNIT' pay/FUN_BUSINESS_UNIT.csv    # must print 1
```
With a location add `|InternalLocationCode=<LOC>|LocationSetCode=COMMON` to the row (VERIFIED). Give the location **now**: a later change means a second import of the same business unit.

## Step 3. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code FUN_MANAGE_BUSINESS_UNIT --task-name "Manage Business Unit" --zip-file "<RUN>/pay/bu.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed` (a second line with 0 rows is normal) and `Business Unit. Status: Completed successfully`. The log and file names in `imp` hold the environment name and user: print only the grep lines. **ProcessId printed but the wait failed (network error, no process log):** never import again; wait 2 minutes and do Step 4. **No ProcessId (network error on the first call):** do not import again in the same sitting; wait at least 10 minutes and prove with a new export that nothing changed (VERIFIED once: nothing had changed).

## Step 4. Read back (VERIFIED)
Export again (Step 1 with `exp2`, both lines). `FUN_BUSINESS_UNIT.csv` holds your BU (with LOC if given; check by name: other people may add rows at the same time, so the count can grow by more than 1); the other 3 files keep their counts (Oracle adds no usage or set rows for a business unit without functions).

## Rules and limits
- Prefix name only; no ledger, legal entity, manager or business function: nothing else uses it.
- Reuse one test business unit for several tasks (check first).

## Worked example (2026-11-26, codes and ProcessIds only)
- `GAPFILL_AB_B15_BU1` (no location): ProcessId 100004743431274, +1 row. A later attempt to add a location timed out before a ProcessId; 10 minutes later the export showed BU1 unchanged; not retried.
- `GAPFILL_AB_B15_BU3` (with an existing location): ProcessId 100004744412442, +1 row with the location.
- Fresh tests: `GAPFILL_AB_B15_BU2F` (ProcessId 100004744412883, wait dropped, read back present) and `GAPFILL_AB_B15_BU4F` with a location (100004743435021): both PASS.
