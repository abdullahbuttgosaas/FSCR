---
skill_id: "gosaas.gap-fills.procurement.manage-contract-procurement-integrations"
name: "Manage Contract and Procurement System Integrations (GoSaaS gap fill)"
description: "Create a new contract deliverable target system (purchasing system integration) through FSCR's setup-task CSV export and import, then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 01, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "OKC_MANAGE_CONTRACTS_DELIVERABLE_PROCUREMENT_SYSTEM_LOOKUPS"
task_name: "Manage Contract and Procurement System Integrations"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.3.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only CSV exports; one CSV import that creates one new target system row. Plan as if it stays; Oracle marks such rows as not deletable on the screen (isdeleteDisabled)."
---

# Manage Contract and Procurement System Integrations (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
Contract deliverables of type "purchasing" can create documents in a purchasing system. This task lists those **target systems**. Oracle seeds one internal row, `ORA_PURCHASING` ("Oracle Fusion Purchasing", `FusionInternalYn=Y`, `IntegrationType=DIRECT`). You can add more rows:
- **(A) an internal target** (`FusionInternalYn=Y`, `IntegrationType=DIRECT`): needs no address or account. **VERIFIED** (tested path of this skill).
- **(B) an external purchasing system** (`FusionInternalYn=N`): Oracle requires the system's endpoint URL and the user name of an account on that system (VERIFIED, see the worked example), and most likely its password (GUESS). **Not tested**: it needs real sign-in details of a real external system, which must be entered by the person who owns them, never by an agent.

Do not use this skill to change the seeded row or another existing row.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ (build_csv_package.py, compare_exports.py)
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE   = new TargetSystemCode, PREFIX + short name (upper case, digits, _), e.g. GAPFILL_AB_TS1
NAME   = display name; DESC = description
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Without it Git Bash rewrites values that start with `/` (for example `/usr/tmp/`) into Windows paths. VERIFIED (it happened once).
- Shell variables do **not** survive from one tool call to the next. Save any value you need later (module id, codes) in a file under `RUN` and read it back, or set it again in the same call.
- **Never read the import log with cat, sed or grep**: it is one long line holding the environment name and the submitting user name. Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"`. It prints only the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. VERIFIED
- FSCR's export and import file names start with the environment name; do not copy them into reports.
- If an export prints `Error: Failed calling ...` (network) and writes no ZIP, run it again into a new folder (it is read-only; up to 3 times). VERIFIED
- Do **not** wrap the import in a shell `timeout`: once the ProcessId is printed the import runs on in Oracle. The script's own `--wait-seconds` is enough. Save the import output to a file so the ProcessId is not lost.
- Row counts in exports grow with every test run (rows from earlier test runs are normal). The worked example counts are from our first run.

- The ProcessId is on the line `Started setup task CSV import process: <n>` of the import output. Save the output to a file and print only that line: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"`.
- If the before- or after-export had to be re-run into a new folder, use **that** folder (the one holding the ZIP) in every later command instead of `export_before` / `export_after`.
- If an import's connection drops after the ProcessId line (`Error: Failed calling ...` printed **with** a ProcessId), the import still runs in Oracle: **never import again**. Fetch its log into the import folder with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code <TASK CODE> --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"`; if it says the process is not complete, run it again. Then read it with `read_import_log.py "<RUN>/import_result"`. VERIFIED

## Sign-in
- Run FSCR scripts with their full path and `python -B`; set `PYTHONUTF8=1`. In Git Bash write paths as `E:/...` (never `/e/...`) and set `MSYS_NO_PATHCONV=1`.
- If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
  `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). VERIFIED
- Never print tokens, the server address or user names.

## Prerequisites
- Path A: none.
- Path B: the external system's endpoint URL, an integration account on it and its password, given by the person who owns that system. An agent must not type a password; stop and hand Step 2 for path B to that person (GUESS: they may prefer the screen for the password).

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code OKC_MANAGE_CONTRACTS_DELIVERABLE_PROCUREMENT_SYSTEM_LOOKUPS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 2 files (VERIFIED): the metadata XML and `ORA_OKC_DTS_PO_INTEG.csv` with columns `TargetSystemCode, UserName, CsfKeyName, TopologyManagerCode, ActiveYn, InactiveDate, FusionInternalYn, CreatedBy, LastUpdatedBy, Name, Description, Password, EndPointUrl, IntegrationType, isdeleteDisabled`. It holds every target system (the seeded `ORA_PURCHASING` + any test rows). List only the codes (never the `UserName`/`Password` columns of other rows):
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I -c "import csv,sys; print([r['TargetSystemCode'] for r in csv.DictReader(open(sys.argv[1],encoding='utf-8'))])" "<RUN>/export_before/unz/ORA_OKC_DTS_PO_INTEG.csv"
```
If CODE is in the list, pick another code.

## Step 2. Build the row (path A)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_OKC_DTS_PO_INTEG.csv=TargetSystemCode \
  --row "ORA_OKC_DTS_PO_INTEG.csv|TargetSystemCode=<CODE>|ActiveYn=Y|FusionInternalYn=Y|IntegrationType=DIRECT|Name=<NAME>|Description=<DESC>"
```
- Leave `UserName`, `Password`, `CsfKeyName`, `TopologyManagerCode`, `EndPointUrl`, `InactiveDate`, `isdeleteDisabled` and audit columns empty (VERIFIED by the fresh test: a row with both empty was created).
- The builder copies the metadata XML unchanged and stops if CODE lacks the prefix or is already in the export.

## Step 3. Import
Approval: the person must approve the environment, the task and CODE before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code OKC_MANAGE_CONTRACTS_DELIVERABLE_PROCUREMENT_SYSTEM_LOOKUPS --task-name "Manage Contract and Procurement System Integrations" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
- Keep the ProcessId. `StatusCode: (unknown)` is normal; read the result only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"` (never cat/grep the log: it holds a user name). Success (VERIFIED): `Business object: Contract and Procurement Integration Setup. Status: Completed successfully`, `1 rows were processed. 0 rows of them failed`.
- `FND_CMN_REQ_ATTRIB_API_SERV: You must provide a value for the Endpoint URL attribute` or `... User Name attribute` = you sent `FusionInternalYn=N` (path B) without those values. Nothing is created. VERIFIED
- A dropped connection after the ProcessId: never import again; fetch and read the log as the shell section says (recovered_process_log.txt).

## Step 4. Read back (second export + compare)
Repeat Step 1 into `<RUN>/export_after`, then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_OKC_DTS_PO_INTEG.csv=TargetSystemCode --expect ORA_OKC_DTS_PO_INTEG.csv=<CODE>
```
`RESULT: PASS` = only your row was added, nothing removed or changed. VERIFIED. If a folder has no export, export again. GUESS: no public REST resource for these rows; the export is the read-back.

## Rules and limits
1. New records only; a row with an existing TargetSystemCode would update it.
2. Never type, copy or print a password or another row's user name.
3. Oracle may fill `InactiveDate` with the load time and keep `isdeleteDisabled=Y` (seen on our row); the row stays active (`ActiveYn=Y`). VERIFIED for a copied row.
4. Test rows stay (no delete on the screen). Record every code.
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | Row | ProcessId | Result |
|---|---|---|---|
| 1 | `GAPFILL_AB_B1_TS1`, external (`FusionInternalYn=N`), no URL | 100004744391264 | refused: Endpoint URL required; nothing created |
| 2 | `GAPFILL_AB_B1_TS2`, external + test URL (reserved `.invalid` domain) | 100004743405950 | connection dropped after start; log fetched by ProcessId: refused, User Name required; nothing created |
| 3 | `GAPFILL_AB_B1_TS3`, external + URL + `IntegrationType=DIRECT` | 100004744393274 | refused: User Name required; nothing created |
| round trip | `GAPFILL_AB_B1_TS4R`: the seeded row copied unchanged with a new code, name and description (internal, DIRECT) | 100004744392872 | 1 processed, 0 failed |
| compare | export before 1 row, after 2; added 1, removed 0, changed 0 | | PASS |
