# Manage Time Unit Mappings (ORA_OKC_MANAGE_TIME_UNIT_MAPPINGS) - map a new test time unit by FSM CSV

## What it is and when to use
Order Management / Sales Contracts setup task **Manage Time Unit Mappings**. A mapping tells contracts and
subscriptions how a unit of measure of class Time (the "user" unit) converts to a base time unit (DAY, MONTH,
YEAR...). Use this skill to create **your own test time unit and its mapping**. Mapping an existing unit would
change how other people's contracts read that unit, so this skill first creates a new unit by REST, then maps it.
Route: REST `unitsOfMeasure` (prerequisite, POST once) + FSM CSV for the mapping; read back with a second export.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders (exports hold user names) | |
| `<PREFIX>` | your test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<UOM>` | new 3-character unit code, e.g. `ZK1` | must be unused (prerequisite 1); 3 characters VERIFIED |
| `<UOMNAME>` | unit name, e.g. `<PREFIX>U1` | holds the prefix |
| `<CODE>` | ConversionCode of the mapping, e.g. `<PREFIX>TU1` | holds the prefix; existing rows use a GUID, any unique text is accepted (VERIFIED) |
| `<BASE>` | base unit, e.g. `DAY` | one of the BaseUomCode values in the export (VERIFIED: DAY, MONTH, YEAR) |

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
1. Your own time unit of measure (Inventory data, created by REST; GET first, POST once):
   - check the code is free: `python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/unitsOfMeasure --q "UOMCode='<UOM>'" --fields UOMCode`
     (must say 0 items; try another code if not);
   - read the Time class value live from an existing time unit:
     `python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/unitsOfMeasure --q "UOMCode='SEC'" --fields UOMClass,UOMClassCode`
     (VERIFIED: UOMClassCode TIME; use the `UOMClass` value it returns as `<CLASS>`);
   - write `<RUN>/uom.json`:
     `{"UOMCode": "<UOM>", "UOM": "<UOMNAME>", "UOMClass": "<CLASS>", "Description": "test time unit", "StandardConversion": 7200, "BaseUnitFlag": false}`
   - POST once: `python3 gaps-filled/common-features/scripts/rest_write.py /fscmRestApi/resources/11.13.18.05/unitsOfMeasure <RUN>/uom.json --fields UOMCode,UOM,UOMClassCode`
     (VERIFIED: without BaseUnitFlag Oracle answers 400 "Attribute BaseUomFlag ... is required"; FSCR's REST client
     prints Oracle's gzipped error unreadable, `rest_write.py` unzips it). If the call drops, GET before any retry.

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_OKC_MANAGE_TIME_UNIT_MAPPINGS <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 3
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --find <CODE>
```
One CSV, `ORA_OKC_TIME_UNIT_MAPPING.csv` (VERIFIED): ConversionCode, UserUomCode, BaseUomCode,
ConversionRate, ActiveFlag. Check `<UOM>` is not already a UserUomCode (`--find <UOM>`).

## Build rows
```json
{"ORA_OKC_TIME_UNIT_MAPPING.csv": [{"ConversionCode": "<CODE>", "UserUomCode": "<UOM>", "BaseUomCode": "<BASE>",
  "ConversionRate": "12", "ActiveFlag": "Y"}]}
```
ConversionRate = how many `<UOM>` make one `<BASE>` (GUESS from Oracle's docs; 12 was accepted for a 2-hour unit
against DAY).

## Import
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json --prefix <PREFIX> --out <RUN>/<CODE>.zip
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> ORA_OKC_MANAGE_TIME_UNIT_MAPPINGS <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Never import the full export (the import merges by key and would re-send existing records). Keep the ProcessId.
Success (VERIFIED): detail object `TimeUnitOfMeasure1` "A total of 1 rows were processed. 0 rows of them failed". If the connection drops after the import started, never import again: wait 2 minutes and
export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_OKC_MANAGE_TIME_UNIT_MAPPINGS <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: `+ ORA_OKC_TIME_UNIT_MAPPING.csv: <CODE>` with UserUomCode `<UOM>`, and `existing changed or missing 0`.

## Rules and limits
- New records only; never edit or delete an existing record.
- Never print tokens, server addresses, environment names or user names; keep exports and logs in `<RUN>`.
- Never map an existing unit (it changes other people's contracts); always create your own unit first.

## Worked example (VERIFIED live)
Unit `ZK1` / `FSCRT_AK_GF_U1` created by REST POST (class TIME, 7200 seconds). Mapping `FSCRT_AK_GF_TU1` (ZK1 to DAY,
rate 12): export ProcessId 100004744431254, import ProcessId 100004743456567 (1 row, 0 failed), after-export
ProcessId 100004744432864: 1 new row, 0 existing changed.
