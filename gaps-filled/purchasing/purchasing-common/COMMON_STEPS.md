# Common steps for Purchasing FSM CSV gap-fill skills

Every Purchasing gap-fill skill in this folder uses the same FSCR export / import route. Paths are relative to the
FSCR root (the folder that holds `core/`, `shared/` and `gaps-filled/`). Run every command from the FSCR root.

## Placeholders

| Placeholder | Meaning |
|---|---|
| `<RUN>` | an empty run folder OUTSIDE the FSCR checkout (exports contain user names). One `<RUN>` per task: when a skill tells you to create a prerequisite with another skill, give that one its own sub-folder (e.g. `<RUN>/prereq`) so the before/after/import files do not mix |
| `<PREFIX>` | your test prefix, upper case, ending in `_`, e.g. `FSCRT_AB_GF_` |
| `<TASK_CODE>` | the setup task code given in the skill |
| `$S` | a shell variable you set once per shell: `S=gaps-filled/purchasing/purchasing-common/scripts` |

In free-text fields (Meaning, Description) use neutral test words. Each skill's row template either gives the text
(usually your new code followed by a few words) or a `<DESCRIPTION>` placeholder for free text of your own.

## Keep environment and user names out of notes

The FSCR scripts name their output files after the environment (export ZIPs, import result JSON, process logs) and
print those names in their "Wrote ..." console lines. The files also hold user names. So:
- send each FSCR command's console output to a log file in `<RUN>` (`> <RUN>/<step>.log 2>&1`) and read only the
  ProcessId line from it (`grep -o "process: [0-9]*" <RUN>/<step>.log`). This includes the REST client
  (`fusion_rest_client.py ... --output <file>`): add `> <RUN>/rest.log 2>&1` and read only the `--output` file;
- `$S/inspect_export.py` masks who-columns and e-mail columns (`<who>`), so its sample rows are safe to read;
- read process logs only through `$S/log_summary.py`, which drops user and environment names;
- never copy a file name, console line or raw log into notes or evidence.

## Sign-in (VERIFIED)

Use FSCR's own login (`core/auth/fusion-oauth-authentication/SKILL.md`). If a token is cached, no action is needed;
every command below uses `--token-cache auto`. A sign-in lasts about an hour: on HTTP 401/403 or a hanging call,
run `python3 core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser`,
sign in in the browser, and continue. That login starts a temporary listener on port 8765 which stops by itself
after "Login complete"; check the port is free afterwards (`ss -ltn | grep 8765` prints nothing). Never print
tokens, server addresses or user names.

Before the steps, set the scripts variable in your shell: `S=gaps-filled/purchasing/purchasing-common/scripts`.
ProcessIds are not issued in time order: a later export can have a lower ProcessId than an earlier import.

## 1. Read-only export (before) (VERIFIED)

```bash
python3 shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code <TASK_CODE> --data \
  --wait-seconds 300 --token-cache auto --no-open-browser --output-dir <RUN>/before > <RUN>/export_before.log 2>&1
grep -o "process: [0-9]*" <RUN>/export_before.log
python3 $S/inspect_export.py <RUN>/before/*.zip --rows 3
python3 $S/inspect_export.py <RUN>/before/*.zip --match <your new key>
```
`inspect_export.py` always prints each CSV's name, row count and header. Your key is free when the `--match` run
prints no `row:` line. The export may already hold rows from earlier test runs; that is normal.

## 2. Build the package (VERIFIED)

Write `<RUN>/rows.json` with the rows the skill gives: your new rows, plus (only where the skill says so) existing
parent rows under `_unchanged_parents`, copied exactly as Oracle holds them. Then:
```bash
python3 $S/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json --prefix <PREFIX> \
  --out <RUN>/package.zip
```
Never import the full export and never add other existing rows: an FSM import merges by key and would re-send
those records.

## 3. Import (VERIFIED)

```bash
python3 shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code <TASK_CODE> \
  --zip-file <RUN>/package.zip --wait-seconds 300 --token-cache auto --no-open-browser \
  --output-dir <RUN>/import > <RUN>/import.log 2>&1
grep -o "process: [0-9]*" <RUN>/import.log
python3 $S/log_summary.py <RUN>/import/*process_log.txt
```
- Write down the import ProcessId: it is the key to the full log.
- The import script's own status lines ("StatusCode: (no result yet)", "StatusCode: (unknown)") do not show the
  result, even on success. The result is the "Business object ... Status" and "Total Objects" lines that
  `log_summary.py` prints.
- If the connection drops after the import started, do NOT import again: wait 2 minutes, then check with step 4.
- If the import is still running after 300 s, fetch the result later with
  `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code <TASK_CODE> --process-id <id> --token-cache auto --no-open-browser --output <RUN>/import/result.json`.

## 4. Read back (VERIFIED)

```bash
python3 shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code <TASK_CODE> --data \
  --wait-seconds 300 --token-cache auto --no-open-browser --output-dir <RUN>/after > <RUN>/export_after.log 2>&1
grep -o "process: [0-9]*" <RUN>/export_after.log
python3 $S/compare_fsm_exports.py --before <RUN>/before/*.zip --after <RUN>/after/*.zip --prefix <PREFIX>
```
Pass = your key is in `added` of each CSV you loaded, every CSV shows `existing removed or changed 0`, and
`added without prefix 0` (a skill that sends an unchanged parent row says what to expect instead). For child CSVs
the `added` list shows the PARENT key (the first column), not the child value. Other keys with your prefix in
`added` come from other people testing with the same prefix at the same time: that is not a failure. Row counts in
worked examples are from one run; expect "before N, after N + your rows".

## Rules

- New records only. Never change or delete an existing record.
- A refused row creates nothing: confirm with step 4 before you try again; change one thing per try.
- Module and lookup IDs are read live by REST in the skill, never copied from an export of another environment.
