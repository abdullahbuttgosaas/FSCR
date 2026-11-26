# Manage Jeopardy Priorities (DOO_MANAGE_JEOPARDY_PRIORITIES) - create a new jeopardy priority by FSM CSV

## What it is and when to use
Order Management (Orders) setup task **Manage Jeopardy Priorities**. A jeopardy priority maps a range of jeopardy
scores (minimum to maximum) to a priority code (seeded: HIGH, MEDIUM, LOW). Use this skill to add a **new priority
code with its own score range** through FSCR's task-level CSV import. It never changes the seeded priorities or
their ranges (those are shared settings used by every order).

Route: FSM CSV. No public REST resource (VERIFIED: GET `jeopardyPriorities` returns 404); read back with an export.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders | |
| `<PREFIX>` | test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new priority code, e.g. `<PREFIX>JP1` | 15 chars VERIFIED |
| `<MIN>`, `<MAX>` | score range of the new code | integers; must not overlap an existing range (see below) |

## Notes for every run (VERIFIED in fresh tests)
- Use a new, empty `<RUN>` and separate empty `before/` and `after/` folders: the compare step expects exactly one
  ZIP in each. FSCR names its output files after the environment, so never list, print or share the file names in
  `<RUN>` or the raw logs; quote only ProcessIds, codes and counts.
- If a sign-in is still valid (token cache), do not sign in again; sign in only on 401/403.
- Check a code is free: `python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --find <CODE>`
  must print 0 rows for every CSV.
- `import_task.sh` prints interim lines such as "StatusCode: (unknown)" or "(no result yet)": ignore them. Judge the
  import only by `read_import_log.py`: the final "Status: Completed successfully" line and "Total Objects Failed: 0".
  An "In progress" line before it, other detail objects with "0 rows were processed", and child business objects
  marked "This object was already processed" are normal.
- Code length: the codes in the worked examples are 15 characters and work; longer codes were not tested (GUESS:
  the column allows more). With a 12-character prefix such as `FSCRT_XX_GF_`, keep the suffix to 3 characters.

## Sign-in
`python3 core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser`
(the person signs in in the browser; never type or print a password or token). On 401/403 sign in again.

## Prerequisites
1. None (stand-alone record, VERIFIED).

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_JEOPARDY_PRIORITIES <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 10
```
One CSV, `DOO_JEOPARDY_PRIORITY.csv` (VERIFIED), columns JeopardyPriorityCode, OrchestrationApplicationCode,
MaximumScore, MinimumScore, CreatedBy, LastUpdatedBy. Note every existing range and check `<CODE>` is not already there.

## Build rows
Read the highest MaximumScore of **all** rows in the export (seeded and test rows) and choose `<MIN>` at least 10
above it, so the new range shares no value with any other range (VERIFIED: 1000-1010 after a maximum of 999, and
1020-1030 after a maximum of 1010). Do not copy the ranges of the worked example: those records exist now. The
seeded ranges share their end points (LOW 0-60, MEDIUM 60-150, HIGH 150-999); whether a shared end point is allowed
for a new code was not tested, so avoid it. An overlapping range could change the priority of existing scores
(GUESS: not tested).
```json
{"DOO_JEOPARDY_PRIORITY.csv": [{"JeopardyPriorityCode": "<CODE>", "OrchestrationApplicationCode": "DOO",
  "MinimumScore": "<MIN>", "MaximumScore": "<MAX>"}]}
```
Leave CreatedBy / LastUpdatedBy empty (VERIFIED).
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json \
  --prefix <PREFIX> --out <RUN>/<CODE>.zip
```
Never import the full export (it would re-send the seeded HIGH/MEDIUM/LOW rows).

## Import
```bash
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> DOO_MANAGE_JEOPARDY_PRIORITIES <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Keep the ProcessId. Success (VERIFIED): business object "Orchestration Jeopardy Priority", detail
`JeopardyPrioritySetupVO` "1 rows were processed. 0 rows of them failed". If the connection drops after the import
started, never import again; wait 2 minutes and export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_JEOPARDY_PRIORITIES <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: `+ DOO_JEOPARDY_PRIORITY.csv: <CODE>` and `existing changed or missing 0`.

## Rules and limits
- New records only. Never change the range of HIGH, MEDIUM, LOW or anyone else's code.
- Never print tokens, server addresses or user names; keep exports and logs in `<RUN>`.

## Worked example (VERIFIED live)
`FSCRT_AK_GF_JP1`, range 1000-1010: export ProcessId 100004743455297, import ProcessId 100004744431219 (1 row,
0 failed), after-export ProcessId 100004743456337: 1 new row, 0 existing changed.
