---
name: manage-payables-lookups
task_code: AP_MANAGE_PAYABLES_LOOKUPS
task_name: Manage Payables Lookups
module: Payables
route: FSM setup CSV export/import (task level), FUN_APP_GENERIC_LOOKUP.csv; REST genericLookups for the type
---

# Manage Payables Lookups (CSV)

## What it is and when to use

Adds a new lookup code to an extensible Payables lookup type (for example `PAY GROUP`) through the FSM setup
CSV import of task `AP_MANAGE_PAYABLES_LOOKUPS` (business object "Financials Generic Lookup"). Payables
lookups are set-enabled "generic" lookups (ViewApplicationId 200, reference data set `COMMON`).

Use it for user-extensible types only (customization level `E` or `U`). Never change predefined codes.

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo |
| `<LOOKUP_TYPE>` | an extensible Payables lookup type, e.g. `PAY GROUP` |
| `<CODE>` | the new lookup code, upper case, max 30 characters (GUESS from FND lookup column size) |
| `<MEANING>` | the display meaning (for a test, start it with your prefix) |
| `<SET_CODE>` | reference data set code; `COMMON` (VERIFIED for PAY GROUP) |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<YOUR_TEST_PREFIX>` | the common start of your new codes (for example your test prefix); a safety check in the builder |
| `<REST_VER>` | `11.13.18.05` |

Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw export CSVs and logs in it hold user names.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour. If you are not allowed to sign in yourself, stop and report on HTTP 401/403; otherwise
sign in again and continue. Never print tokens, server addresses or user names.

## Prerequisites

1. Signed in.
2. Read the lookup type LIVE (never copy ids from an export):
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/genericLookups \
     --q "LookupType='<LOOKUP_TYPE>'" \
     --fields LookupType,ViewApplicationId,ApplicationShortName,ModuleId,CustomizationLevel --out <RUN>/type.json
   ```
   It must return 1 item with CustomizationLevel `E` (extensible) or `U` (user). If it is `S` (system),
   stop: codes cannot be added. Keep ViewApplicationId, ApplicationShortName and ModuleId for the row.
3. The code must be new: after the export below, look for an EXACT LookupCode match under your type
   (`--grep` matches parts of codes). If it exists, choose another code.

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_PAYABLES_LOOKUPS --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip --file FUN_APP_GENERIC_LOOKUP.csv --grep <CODE> --cols LookupType,LookupCode
```

The console line "status (unknown)" is normal. Four CSVs (VERIFIED): `ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv`
and its `_TRANSLATION` (0 rows: types are not exported), `FUN_APP_GENERIC_LOOKUP.csv` (codes, top-level
object) and `FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv` (one row per code and language). The export holds only
non-seeded codes.

## Build rows

`<RUN>/rows.json` with ONE code row and NO translation row (VERIFIED):

```json
{"FUN_APP_GENERIC_LOOKUP.csv": [{"LookupType": "<LOOKUP_TYPE>", "LookupCode": "<CODE>",
  "ViewApplicationId": "<ViewApplicationId from step 2>", "SetCode": "<SET_CODE>",
  "Meaning": "<MEANING>", "Description": "<MEANING>", "EnabledFlag": "Y",
  "ModuleKey": "<ApplicationShortName from step 2>", "ModuleType": "APPLICATION",
  "ModuleId": "<ModuleId from step 2>", "ChangeSinceLastRefresh": "N",
  "CreatedBy": "@SUBMITTER", "LastUpdatedBy": "@SUBMITTER"}]}
```

Why (VERIFIED by failed tries, see CHANGELOG):
- `ChangeSinceLastRefresh` is REQUIRED (`JBO-27014: Attribute ChangeSinceLastRefresh ... is required`).
- Do NOT send a translation row for a NEW code: Oracle creates the US translation itself; an extra
  translation row makes the whole code fail (`JBO-25027 ... LookupGenericTranslation cannot be loaded`).
- `@SUBMITTER` is replaced by the builder with the export's SubmittedBy value (never typed or printed).
  The working load had it; whether it is needed is GUESS.

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --max-len LookupCode=30 --out <RUN>/load.zip
```

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code AP_MANAGE_PAYABLES_LOOKUPS --zip <RUN>/load.zip --run <RUN> --label imp1
```

The console lines "StatusCode: (unknown)" are normal; the "== log" part decides. Success (VERIFIED):
"Detail Object: LookupGeneric1. Status: Completed successfully ... A total of 1 rows were processed. 0 rows
of them failed" and "Total Objects Failed: 0" ("LookupTypeGeneric1 ... 0 rows" is normal). Keep the
ProcessId (`<RUN>/imp1_processid.txt`). If the connection drops after the import started, do NOT import
again: wait 2 minutes and export again to check.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_PAYABLES_LOOKUPS --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/after.zip --file FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv --grep <CODE> \
  --cols LookupType,LookupCode,Language,Meaning
```

Pass = FUN_APP_GENERIC_LOOKUP.csv +1 and FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv +1 (the automatic US row),
`RESULT: OK - only prefix rows added, nothing removed or changed`. REST `genericLookups/<key>/child/lookupCodes`
returned 0 items even for existing codes (VERIFIED), so the export compare is the read-back.

## Rules and limits

- New codes on extensible types only; never re-send existing or predefined codes, never load the full export.
- Other lookup types appear here as a side effect of other setup: e.g. every new invoice hold name also
  creates a code under `HOLD CODE` (VERIFIED). Do not add HOLD CODE codes here; use Manage Invoice Holds.
- To translate your code later, send a translation row for your OWN existing code (GUESS, not tested).

## Worked example (sitting 1)

- `PAY GROUP` / `FSCRT_AK_GF_PG1`: tries 1-3 failed (translation row; then missing ChangeSinceLastRefresh);
  fix: ProcessId 100004744404058, 1 row processed, 0 failed; compare: codes +1, translations +1,
  removed/changed 0 (VERIFIED). Row counts depend on the environment; only "+1, removed/changed 0" matters.
