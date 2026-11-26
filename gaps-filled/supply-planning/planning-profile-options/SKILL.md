# Manage Planning Profile Options (FSM CSV)

Task code: `ORA_MSC_MANAGE_PLANNING_PROFILE_OPTIONS`
Offering: Supply Chain Planning · Functional area: Supply Chain Planning Configuration

## What it is and when to use

Creates one **new** planning profile option: its definition (`FND_APP_PROFILE_OPTION`), its levels
(`ORA_FND_APP_PROFILE_OPTION_LEVEL`) and a site value (`FND_APP_PROFILE_VALUE`), through the task's FSM CSV
export/import. Use it for a custom planning profile option. It never changes an existing option or its values: setting
a value on a predefined option changes behaviour for everyone on the environment and is out of scope.

## Placeholders

| Placeholder | Meaning | Example (format only) |
|---|---|---|
| `<FSCR_ROOT>` | the FSCR pack folder; run every command from it | |
| `<RUN>` | a new run folder OUTSIDE the FSCR folder (exports hold user names) | |
| `<PREFIX>` | your own test prefix (your initials); every row must contain it (`fsm_package.py` rejects rows without it) | `FSCRT_AB_GF_` |
| `<OPTION>` | the new profile option code: `<PREFIX>` + a short name, upper case | `FSCRT_AB_GF_PO1` |
| `<OPTION_NAME>` | user-facing name: `<OPTION>` followed by ` test option` | `FSCRT_AB_GF_PO1 test option` |
| `<VALUE>` | the site-level value; use `Y` unless told otherwise | `Y` |
| `<START_DATE>` | today's date, format `YYYY/MM/DD` | `2026/11/24` |

## Sign-in

Sign in with FSCR's PKCE login (`core/auth/fusion-oauth-authentication`) before you start (skip it if you are already
signed in; the first export's 401/403 check below tells you), then pass `--token-cache auto --no-open-browser` to
every command. On Windows set `PYTHONUTF8=1`.

**Output stays private.** FSCR's export and import scripts print file names that start with the environment name, and
their status and log files hold user names. Run every FSCR script exactly as shown below, so its output goes to a log
in `<RUN>/logs`, and read results only with the commands this skill gives (`ls`, `grep`, and the three scripts in
`gaps-filled/supply-planning/scripts/`). Never print a whole log, an existing CSV row, or a file name from
`<RUN>/before`, `<RUN>/after` or `<RUN>/import`. Printing your own new rows (as `compare_exports.py` does) is fine.
If an expected file is missing, run `grep -cE " 401| 403|Unauthorized|Forbidden" "<RUN>/logs/<log>"`: a count above 0
means the sign-in expired; sign in again and repeat that step.

## Prerequisites

1. None. The option is stand-alone. (VERIFIED: created with no other record.)
2. The planning `ApplicationId` and `ModuleId` are read from your own export in "Build rows", step 1.

## Export (read only)

```bash
mkdir -p "<RUN>/logs"
python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_MSC_MANAGE_PLANNING_PROFILE_OPTIONS --data --wait-seconds 400 --output-dir "<RUN>/before" --token-cache auto --no-open-browser > "<RUN>/logs/export_before.log" 2>&1
ls "<RUN>/before"/*.zip > /dev/null && echo "export written"
```

- The ZIP holds `FND_APP_PROFILE_OPTION.csv` (the task's planning options), `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv`
  (3 levels per option: SITE, PRODUCT, USER) and `FND_APP_PROFILE_VALUE.csv` (values). VERIFIED.
- The export log may end with `StatusCode: (unknown)`, `StatusCode: (no result yet)` or `ResultCount: 0` although the
  ZIP was written. That is normal.
- Check the code is free and count the values you need (prints counts only, never rows; earlier `FSCRT_` test
  options are left out of the counts):

  ```bash
  python gaps-filled/supply-planning/scripts/inspect_export.py "<RUN>/before" FND_APP_PROFILE_OPTION.csv ProfileOptionName <OPTION> ApplicationId ModuleId
  ```

  If it says `<OPTION> already exists: True`, pick another code.
- Windows: if the export log mentions "No such file or directory", use a shorter `<RUN>` path (260-character limit).

## Build rows

1. `ApplicationId` and `ModuleId`: take them from the counts `inspect_export.py` printed. All rows share one
   `ApplicationId` (the planning application). `ModuleId` differs between rows (planning has more than one module);
   take the `ModuleId` with the highest count. They are this environment's values, read at run time; do not reuse them
   anywhere else. (VERIFIED: one ApplicationId and two ModuleId values; the most-used one loads.)
2. Write `<RUN>/rows.json` with only your new rows:

   ```json
   {
    "FND_APP_PROFILE_OPTION.csv": [{"ProfileOptionName": "<OPTION>", "ApplicationId": "<app id>", "ModuleId": "<module id>",
      "Description": "<OPTION_NAME>", "StartDateActive": "<START_DATE>", "UserProfileOptionName": "<OPTION_NAME>"}],
    "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv": [
      {"FND_APP_PROFILE_OPTION.ProfileOptionName": "<OPTION>", "FND_APP_PROFILE_OPTION.ApplicationId": "<app id>", "LevelName": "SITE", "UpdateableFlag": "Y", "EnabledFlag": "Y"},
      {"FND_APP_PROFILE_OPTION.ProfileOptionName": "<OPTION>", "FND_APP_PROFILE_OPTION.ApplicationId": "<app id>", "LevelName": "PRODUCT", "UpdateableFlag": "N", "EnabledFlag": "N"},
      {"FND_APP_PROFILE_OPTION.ProfileOptionName": "<OPTION>", "FND_APP_PROFILE_OPTION.ApplicationId": "<app id>", "LevelName": "USER", "UpdateableFlag": "N", "EnabledFlag": "N"}],
    "FND_APP_PROFILE_VALUE.csv": [{"FND_APP_PROFILE_OPTION.ProfileOptionName": "<OPTION>", "FND_APP_PROFILE_OPTION.ApplicationId": "<app id>",
      "LevelName": "SITE", "LevelValue": "SITE", "ProfileOptionValue": "<VALUE>"}]
   }
   ```

   Send all three levels, the way every existing option has them (VERIFIED). Leave the who-columns (`CreatedBy`,
   `CreationDate`, `LastUpdatedBy`, `LastUpdateDate`, `LastUpdateLogin`) out (VERIFIED: not needed).
3. Build the package with ONLY your rows. Never import the full export: an FSM import merges by key and would re-send
   every existing option and value.

   ```bash
   python module-test-kit/scripts/fsm_package.py --export "$(ls "<RUN>/before"/*.zip)" --rows "<RUN>/rows.json" --prefix <PREFIX> --out "<RUN>/load.zip"
   ```

   Before importing, check what it printed: `FND_APP_PROFILE_OPTION.csv 1 row(s)`,
   `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv 3 row(s)`, `FND_APP_PROFILE_VALUE.csv 1 row(s)`, every other CSV header only.

## Import

```bash
python shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_MSC_MANAGE_PLANNING_PROFILE_OPTIONS --zip-file "<RUN>/load.zip" --wait-seconds 400 --output-dir "<RUN>/import" --token-cache auto --no-open-browser > "<RUN>/logs/import.log" 2>&1
grep -oE "Started setup task CSV import process: *[0-9]+" "<RUN>/logs/import.log"
python gaps-filled/supply-planning/scripts/import_result.py "<RUN>/import"
```

- The `grep` prints the ProcessId. Keep it: it is the key to the full process log. The files in `<RUN>/import` hold
  the environment name and user names: never open or paste them; `import_result.py` reads them safely.
- `import_result.py` ends with `RESULT: SUCCESS` (expected: `3 x Completed successfully`, `rows processed 5, failed 0`
  for 1 option + 3 levels + 1 value, `Total Objects Failed: 0`) or `RESULT: ERRORS` with Oracle's error messages.
  (VERIFIED)
- The import log may end with `StatusCode: (unknown)` and `ResultCount: 0` even when the import succeeded. That is
  normal; `import_result.py` and the after-export decide.
- **If the result is ERRORS:** nothing may have been created (check with the read-back below). Do NOT import the same
  package again. Read the `error` lines, fix one thing at a time (a taken code: pick a new `<OPTION>`), and start
  again from "Build rows".
- If the connection drops after the import started, do not import again: wait 2 minutes and check with a new export.

## Read back

1. Export again:

   ```bash
   python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_MSC_MANAGE_PLANNING_PROFILE_OPTIONS --data --wait-seconds 400 --output-dir "<RUN>/after" --token-cache auto --no-open-browser > "<RUN>/logs/export_after.log" 2>&1
   ls "<RUN>/after"/*.zip > /dev/null && echo "export written"
   ```

2. Compare (prints counts and only your rows; who-columns are ignored and never printed):

   ```bash
   python gaps-filled/supply-planning/scripts/compare_exports.py "<RUN>/before" "<RUN>/after" <OPTION>
   ```

   Pass: option `added 1 (yours 1)`, levels `added 3 (yours 3)`, value `added 1 (yours 1)`, every CSV
   `removed/changed 0`, and the last line starts with `PASS`. `FAIL` means your rows were not created; `CHECK` means
   something else changed: stop and report it.

## Rules and limits

- New options only. Never send a row for an existing option, and never set a value on a predefined option.
- At the end, check nothing you started is still running: `tasklist //FI "IMAGENAME eq python.exe"` (Git Bash on
  Windows; `pgrep -l python` on Mac) shows no Python from this run, and `netstat -ano | grep ":8765 " | grep LISTEN`
  prints nothing. A Python process from another program may appear briefly; it is not yours.

## Worked example

Option `FSCRT_IR_GF_PO1` (site value `Y`): import ProcessId 100004742419023, 5 rows processed, read back (1 + 3 + 1
added, 0 changed). Fresh tests `FSCRT_IR_GF_POF` (100004742421074), `FSCRT_IR_GF_POR` (100004742423051),
`FSCRT_IR_GF_POR2` (100004742422229) and `FSCRT_IR_GF_POR3` (100004742419116) all read back. Full history:
`gaps-filled/supply-planning/planning-profile-options/CHANGELOG.md`.
