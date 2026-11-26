# Manage Supply Orchestration Attachment Categories (FSM CSV)

Task code: `ORA_DOS_MANAGE_SUPPLY_ORCHESTRATION_ATTACHMENT_CATEGORIES`
Offering: Manufacturing and Supply Chain Materials Management · Functional area: Supply Chain Orchestration

## What it is and when to use

Creates one **new** attachment category (`FND_APP_ATTACHMENT_CATEGORY`) through the task's FSM CSV export/import.
Use it when a supply orchestration process needs its own attachment category. It never changes or deletes an existing
category: the package holds only your new row.

## Placeholders

| Placeholder | Meaning | Example |
|---|---|---|
| `<FSCR_ROOT>` | the FSCR pack folder; run every command from it | |
| `<RUN>` | a new run folder OUTSIDE the FSCR folder (exports hold user names); create it yourself first with `mkdir -p "<RUN>/logs"` | |
| `<PREFIX>` | your own test prefix (your initials); it must start with `FSCRT_`, and every row needs it in at least one value (the code does that; `fsm_package.py` drops the package otherwise) | `FSCRT_AB_GF_` |
| `<CATEGORY>` | the new category code: `<PREFIX>` + a short name, upper case, **at most 21 characters** (so that `<DISPLAY_NAME>` stays within 30) | `FSCRT_AB_GF_AC1` |
| `<DISPLAY_NAME>` | user-facing name (`UserName` column). **Must be unique** across all categories and at most 30 characters: use `<CATEGORY>` followed by ` category` | `FSCRT_AB_GF_AC1 category` |
| `<DESCRIPTION>` | free text; use the example unless told otherwise | `Test attachment category` |

## Sign-in

Sign in with FSCR's PKCE login (`core/auth/fusion-oauth-authentication`) before you start (skip it if you are already
signed in), then pass `--token-cache auto --no-open-browser` to every command. On Windows set `PYTHONUTF8=1` (Git
Bash: `export PYTHONUTF8=1`). In Git Bash, the `fusion_rest_client.py` command below starts with `MSYS_NO_PATHCONV=1`
(otherwise `/fscmRestApi/...` is rewritten into a Windows path and the client says "Invalid REST endpoint"). That
setting also stops Git Bash from converting path arguments, so that command passes no path argument: its output is
redirected instead (VERIFIED). The export and import scripts do not need it.

**Output stays private.** FSCR's export and import scripts print file names that start with the environment name, and
their status and log files hold user names. Run every FSCR script exactly as shown below, so its output goes to a log
in `<RUN>/logs`, and read results only with the commands this skill gives (`ls`, `grep -oE`, and the three scripts in
`gaps-filled/supply-planning/scripts/`). Never print a whole log, an existing CSV row, or a file name from
`<RUN>/before`, `<RUN>/after` or `<RUN>/import`. Printing your own new rows (as `compare_exports.py` does) is fine.
If an expected file is missing, run `grep -cE " 401| 403|Unauthorized|Forbidden" "<RUN>/logs/<log>"`: a count above 0
means the sign-in expired; sign in again and repeat that step.

## Prerequisites

1. None. The category is stand-alone. (VERIFIED: created with no other record.)
2. The supply orchestration **ModuleId** is read live in "Build rows", step 1; never copy it from another environment.

## Export (read only)

```bash
mkdir -p "<RUN>/logs"
python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_DOS_MANAGE_SUPPLY_ORCHESTRATION_ATTACHMENT_CATEGORIES --data --wait-seconds 400 --output-dir "<RUN>/before" --token-cache auto --no-open-browser > "<RUN>/logs/export_before.log" 2>&1
ls "<RUN>/before"/*.zip > /dev/null && echo "export written"
```

- The ZIP holds `FND_APP_ATTACHMENT_CATEGORY.csv` (the categories this task exports, about 20 in a typical test
  environment, across a few applications) and `ORA_FND_APP_ATTACHMENT_CATEGORY.csv` (category-to-entity links). VERIFIED.
- The export log may end with `StatusCode: (unknown)`, `StatusCode: (no result yet)` or `ResultCount: 0` although the
  ZIP was written. That is normal: the ZIP is the result. (VERIFIED)
- Check that the code and the display name are both free, and count the values you need (prints counts only, never rows):

  ```bash
  python gaps-filled/supply-planning/scripts/inspect_export.py "<RUN>/before" FND_APP_ATTACHMENT_CATEGORY.csv CategoryName <CATEGORY> ApplicationId
  python gaps-filled/supply-planning/scripts/inspect_export.py "<RUN>/before" FND_APP_ATTACHMENT_CATEGORY.csv UserName "<DISPLAY_NAME>"
  ```

  Both must say `already exists: False`. If either says `True`, pick another `<CATEGORY>` (and so another display name).
  (VERIFIED: a display name already used by another category makes the import fail with `FND_CORE_RCRD_VAL`.)
- Windows: if the export log mentions "No such file or directory", use a shorter `<RUN>` path (the long file name can
  pass the 260-character limit; VERIFIED).

## Build rows

1. Read the ModuleId of the supply orchestration module live, from one of its predefined lookups:

   ```bash
   MSYS_NO_PATHCONV=1 python core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET /fscmRestApi/resources/11.13.18.05/standardLookups --query "q=LookupType='ORA_DOS_DOCUMENT_TYPE'" --query fields=LookupType,ModuleId --query onlyData=true --token-cache auto --no-open-browser > "<RUN>/logs/module.json" 2> "<RUN>/logs/module.log"
   python -c "import json,sys; d=json.load(open(sys.argv[1])); print('items:', len(d['items'])); [print('ModuleId:', i['ModuleId']) for i in d['items']]" "<RUN>/logs/module.json"
   ```

   It must print `items: 1`; use that `ModuleId` (32 hex characters). The predefined categories in the export
   belong to other modules, so this ModuleId need not appear among them. VERIFIED.
2. `ApplicationId`: use the value with the highest count in the `ApplicationId` line printed by `inspect_export.py`
   (`1 x16, 0 x3` means value `1` on 16 rows and `0` on 3; earlier `FSCRT_` test rows are not counted).
   (VERIFIED in one environment: most rows use one value, a few use another. GUESS that this holds everywhere, so read
   it from your export each time.)
3. Write `<RUN>/rows.json` with only your new row:

   ```json
   {"FND_APP_ATTACHMENT_CATEGORY.csv": [{"CategoryName": "<CATEGORY>", "ApplicationId": "<from step 2>",
     "Description": "<DESCRIPTION>", "ModuleId": "<from step 1>", "UserName": "<DISPLAY_NAME>"}]}
   ```

   Leave `CreatedBy`, `CreationDate`, `LastUpdatedBy`, `LastUpdateDate`, `LastUpdateLogin` out (VERIFIED: not needed).
   `UserName` is the category's display name, not a person.
4. Build the package. It copies the export's structure and keeps ONLY your rows. Never import the full export: an FSM
   import merges by key and would re-send every existing category.

   ```bash
   python module-test-kit/scripts/fsm_package.py --export "$(ls "<RUN>/before"/*.zip)" --rows "<RUN>/rows.json" --prefix <PREFIX> --out "<RUN>/load.zip"
   ```

   It prints `wrote load.zip: FND_APP_ATTACHMENT_CATEGORY.csv 1 row(s); all other CSVs header only`. Anything else:
   stop and fix `rows.json`.

## Import

```bash
python shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_DOS_MANAGE_SUPPLY_ORCHESTRATION_ATTACHMENT_CATEGORIES --zip-file "<RUN>/load.zip" --wait-seconds 400 --output-dir "<RUN>/import" --token-cache auto --no-open-browser > "<RUN>/logs/import.log" 2>&1
grep -oE "Started setup task CSV import process: *[0-9]+" "<RUN>/logs/import.log"
python gaps-filled/supply-planning/scripts/import_result.py "<RUN>/import"
```

- The `grep` prints the ProcessId. Keep it: it is the key to the full process log. The files in `<RUN>/import` hold
  the environment name and user names: never open or paste them; `import_result.py` reads them safely.
- `import_result.py` ends with `RESULT: SUCCESS` or `RESULT: ERRORS`. On success it prints a few `In progress` and
  `Completed successfully` lines (all normal), `Total Objects Failed: 0`, and `rows processed` lines: the category
  shows as `rows processed 1, failed 0` (it can appear twice, for the object and its detail) and the empty
  entity-link CSV as `rows processed 0, failed 0`. On errors it prints Oracle's error messages. (VERIFIED, both cases)
- The import log may end with `StatusCode: (unknown)` and `ResultCount: 0` even when the import succeeded. That is
  normal; `import_result.py` and the after-export decide.
- **If the result is ERRORS:** nothing was created (check with the read-back below). Do NOT import the same package
  again. Read the `error` lines: `FND_CORE_RCRD_VAL ... already exists` means the code or display name is taken; pick
  a new `<CATEGORY>` and start again from "Build rows". Any other error: fix one thing at a time.
- If the connection drops after the import started, do not import again: wait 2 minutes and check with a new export.

## Read back

1. Export again:

   ```bash
   python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_DOS_MANAGE_SUPPLY_ORCHESTRATION_ATTACHMENT_CATEGORIES --data --wait-seconds 400 --output-dir "<RUN>/after" --token-cache auto --no-open-browser > "<RUN>/logs/export_after.log" 2>&1
   ```

2. Compare (prints counts and only your rows; who-columns are ignored and never printed):

   ```bash
   python gaps-filled/supply-planning/scripts/compare_exports.py "<RUN>/before" "<RUN>/after" <CATEGORY>
   ```

   Pass: `FND_APP_ATTACHMENT_CATEGORY.csv` shows `added 1 (yours 1) | removed/changed 0`, the links CSV shows
   `removed/changed 0`, and the last line starts with `PASS`. `FAIL` means your row was not created; `CHECK` means
   something else changed: stop and report it.

## Rules and limits

- New categories only. Never re-send or edit an existing row.
- Code at most 21 characters and display name at most 30 (the display name is the code plus ` category`); the display
  name must be unique (VERIFIED).
- The entity links (`ORA_FND_APP_ATTACHMENT_CATEGORY.csv`) are optional and not covered here.
- At the end, check nothing you started is still running: `tasklist //FI "IMAGENAME eq python.exe"` (Git Bash on
  Windows; `pgrep -l python` on Mac) shows no Python from this run, and `netstat -ano | grep ":8765 " | grep LISTEN`
  prints nothing. A Python process from another program may appear briefly; it is not yours.

## Worked example

Category `FSCRT_IR_GF_AC1`: import ProcessId 100004742420025, 1 row processed, read back (added 1, changed 0).
Fresh tests: `FSCRT_IR_GF_ACF` (ProcessId 100004742420054) and `FSCRT_IR_GF_ACR` (100004742419063) read back;
`FSCRT_IR_GF_ACR2` (100004742419086) failed with `FND_CORE_RCRD_VAL` because it reused a display name, which led to
the unique-name rule; `FSCRT_IR_GF_ACR3` (100004742420131) and `FSCRT_IR_GF_ACR4` (100004742423164) read back. Full history: `gaps-filled/supply-planning/attachment-categories/CHANGELOG.md`.
