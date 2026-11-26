# Manage Pricing Totals (ORA_QP_MANAGE_PRICING_TOTALS_DEFINITIONS) - create a new pricing total by FSM CSV

## What it is and when to use
Pricing setup task **Manage Pricing Totals**. A pricing total (for example a shipping total) is calculated by a
pricing algorithm and can be shown on transactions. Use this skill to add a **new total that is not enabled for
transactions** through FSCR's task-level CSV import. It never changes an existing total or algorithm.
Route: FSM CSV; read back with a second export.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders (exports hold user names) | |
| `<PREFIX>` | your test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new TotalCode, e.g. `<PREFIX>TOA` | **upper case letters and underscores only, no digits** (see Rules); 15 chars VERIFIED |
| `<ALG>` | AlgorithmName of an existing pricing algorithm | read from the export (prerequisite 1) |

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
1. An existing pricing algorithm that calculates the total. Read the AlgorithmName values in use from the export
   (VERIFIED: `Calculate Shipping Charges`). The algorithm is only referenced, not changed.

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_PRICING_TOTALS_DEFINITIONS <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 3
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --find <CODE>
```
One CSV, `ORA_QP_PRICING_TOTAL_DEFINITION.csv` (VERIFIED): TotalCode, Description, Name,
PricingGuidelineEnabledFlag, ReturnNullTotalFlag, SeededFlag, TransactionEnabledFlag, AlgorithmName.

## Build rows
```json
{"ORA_QP_PRICING_TOTAL_DEFINITION.csv": [{"TotalCode": "<CODE>", "Name": "<CODE> test total", "Description": "test total",
  "PricingGuidelineEnabledFlag": "N", "ReturnNullTotalFlag": "Y", "SeededFlag": "N", "TransactionEnabledFlag": "N",
  "AlgorithmName": "<ALG>"}]}
```
`TransactionEnabledFlag` `N` keeps the total off every transaction (VERIFIED accepted).

## Import
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json --prefix <PREFIX> --out <RUN>/<CODE>.zip
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> ORA_QP_MANAGE_PRICING_TOTALS_DEFINITIONS <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Never import the full export (the import merges by key and would re-send existing records). Keep the ProcessId.
Success (VERIFIED): business object "Pricing Total", detail `TotalDefinitionSetup` "A total of 1 rows were processed. 0 rows of them failed". If the connection drops after the import started, never import again: wait 2 minutes and
export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_PRICING_TOTALS_DEFINITIONS <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: `+ ORA_QP_PRICING_TOTAL_DEFINITION.csv: <CODE>` and `existing changed or missing 0`.

## Rules and limits
- New records only; never edit or delete an existing record.
- Never print tokens, server addresses, environment names or user names; keep exports and logs in `<RUN>`.
- **TotalCode must not contain digits** (VERIFIED: `FSCRT_AK_GF_TO1` was refused with QP_CMN_INVALID_CODE "You must
  enter code that's in uppercase, can be up to 30 characters, and doesn't contain spaces"; the same row with
  `FSCRT_AK_GF_TOA` loaded). The refused row created nothing (VERIFIED by export).

## Worked example (VERIFIED live)
`FSCRT_AK_GF_TOA` (algorithm Calculate Shipping Charges): export ProcessId 100004743455521; try 1 with code ending
`1` refused (ProcessId 100004744431339); import ProcessId 100004744433010 (1 row, 0 failed); after-export ProcessId
100004744431379: 1 new row, 0 existing changed.
