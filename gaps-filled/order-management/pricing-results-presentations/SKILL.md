# Manage Pricing Results Presentations (ORA_QP_MANAGE_PRICING_RESULTS_PRESENTATIONS) - create a new presentation by FSM CSV

## What it is and when to use
Pricing setup task **Manage Pricing Results Presentations**. A results presentation decides which pricing results
(price breakdown, margin, and so on) the order or quote shows, based on a presentation template. Use this skill to
add a **new presentation** through FSCR's task-level CSV import. It never changes an existing presentation.
Route: FSM CSV; read back with a second export (no REST resource used).

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders (exports hold user names) | |
| `<PREFIX>` | your test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new ResultPresentationCode, e.g. `<PREFIX>RP1` | upper case; 15 chars VERIFIED |

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
1. A presentation template (seeded). Read the TemplateCode values in use from the export (VERIFIED: `PRICE_BREAKDOWN`).

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_PRICING_RESULTS_PRESENTATIONS <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 3
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --find <CODE>
```
One CSV, `ORA_QP_PRICING_RESULTS_PRESENTATION_TEMPLATE.csv` (VERIFIED): ResultPresentationCode, Name,
Description, TemplateCode, DataSelectionFlag, SeededFlag, AttributeCategory, Attribute* (flexfield, leave empty),
Retrieved (no CreatedBy/LastUpdatedBy columns).

## Build rows
`<RUN>/rows.json`:
```json
{"ORA_QP_PRICING_RESULTS_PRESENTATION_TEMPLATE.csv": [{"ResultPresentationCode": "<CODE>", "Name": "<CODE>",
  "Description": "test presentation", "TemplateCode": "PRICE_BREAKDOWN", "DataSelectionFlag": "ALL_APPLICABLE",
  "SeededFlag": "N", "Retrieved": "Y"}]}
```
- DataSelectionFlag values seen on existing rows (VERIFIED): `ALL_APPLICABLE`, `SELECTED_DISPLAY`. `ALL_APPLICABLE`
  needs no child rows.
- Leave the Attribute columns empty (VERIFIED). The import log may also list business object "Pricing Results
  Presentation Template ... already processed": that is normal, not a skip.

## Import
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json --prefix <PREFIX> --out <RUN>/<CODE>.zip
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> ORA_QP_MANAGE_PRICING_RESULTS_PRESENTATIONS <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Never import the full export (the import merges by key and would re-send existing records). Keep the ProcessId.
Success (VERIFIED): detail object `PricingResultsPresentationHeaderP1` "A total of 1 rows were processed. 0 rows of them failed". If the connection drops after the import started, never import again: wait 2 minutes and
export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_PRICING_RESULTS_PRESENTATIONS <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: `+ ORA_QP_PRICING_RESULTS_PRESENTATION_TEMPLATE.csv: <CODE>` and `existing changed or missing 0`.

## Rules and limits
- New records only; never edit or delete an existing record.
- Never print tokens, server addresses, environment names or user names; keep exports and logs in `<RUN>`.

## Worked example (VERIFIED live)
`FSCRT_AK_GF_RP1`: export ProcessId 100004743456353, import ProcessId 100004743455639 (1 row, 0 failed), after-export
ProcessId 100004744432691: 1 new row, 0 existing changed.
