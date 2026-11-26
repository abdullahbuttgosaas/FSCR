# Manage External Purchase Prices Lookups (ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_LOOKUPS): create a lookup type and code by FSM CSV

## What it is and when to use
Standard lookups that belong to the External Purchase Prices module. Use this skill to create a NEW user lookup type
with one or more codes in that module through FSCR's setup task CSV import. FSCR has no skill for this task.
Route: FSM setup CSV (task `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_LOOKUPS`, CSV supported: Y). VERIFIED.
Read-back also works by REST `standardLookups` (create is also offered there, but this skill uses the CSV route).

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<TYPE>`: new lookup type, `<PREFIX>` + short name, upper case, e.g. `FSCRT_AB_GF_LK1` (max 30, GUESS).
- `<LOOKUP_CODE>`: new code, e.g. `<PREFIX>A`.
- `<MODULE_ID>`: the External Purchase Prices module ID, read live (prerequisite 1).

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. Read the module ID live (VERIFIED: every `ORA_SCH_EPP%` lookup type carries the module's ID):
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query "q=LookupType LIKE 'ORA_SCH_EPP%'" --query fields=LookupType,ModuleId \
     --query limit=3 --output <RUN>/epp_module.json "/fscmRestApi/resources/11.13.18.05/standardLookups" > <RUN>/rest.log 2>&1
   python3 -c "import json;print({i['ModuleId'] for i in json.load(open('<RUN>/epp_module.json'))['items']})"
   ```
   Exactly one ID must print; that is `<MODULE_ID>`. If the set is empty, stop (the module is not available).
2. Check `<TYPE>` is not used (separate output file):
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query "q=LookupType='<TYPE>'" --output <RUN>/type_check.json \
     "/fscmRestApi/resources/11.13.18.05/standardLookups" > <RUN>/rest.log 2>&1
   python3 -c "import json;print(len(json.load(open('<RUN>/type_check.json'))['items']))"
   ```
   It must print `0`. Lookup codes are unique only within their type, so the same `<LOOKUP_CODE>` may exist under
   another type; check the TYPE, not the code. VERIFIED.

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_LOOKUPS`. Two CSVs:
`FND_APP_STANDARD_LOOKUP.csv` (types) and `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv` (codes, linked by
`FND_APP_STANDARD_LOOKUP.LookupType`). Only user-defined types of the module are exported; seeded types are not. VERIFIED.

## Build rows
`<RUN>/rows.json` (the parent type row must be in the same package as its codes). VERIFIED:
```json
{"FND_APP_STANDARD_LOOKUP.csv": [{"LookupType": "<TYPE>", "Meaning": "<TYPE> test lookup",
   "Description": "<TYPE> test lookup type", "ModuleId": "<MODULE_ID>", "CustomizationLevel": "U",
   "RestAccessSecured": "AUTH"}],
 "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv": [{"FND_APP_STANDARD_LOOKUP.LookupType": "<TYPE>", "LookupCode": "<LOOKUP_CODE>",
   "Meaning": "<TYPE> value A", "Description": "<TYPE> test code", "EnabledFlag": "Y",
   "StartDateActive": "2026/01/01", "DisplaySequence": "1"}]}
```
- `CustomizationLevel` `U` = user lookup (the only level to create). VERIFIED.
- `RestAccessSecured` `AUTH` (as seeded types of the module use) makes the type readable by REST. VERIFIED.
  (`SECURE` also loads, but REST may hide such types: GUESS from an earlier run.)
- Dates use `YYYY/MM/DD`. VERIFIED.
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Application Standard Lookup ... A total of 2 rows were
processed. 0 rows of them failed" (type + code). VERIFIED.

## Read back
1. COMMON_STEPS step 4: both CSVs `added 1 ['<TYPE>']`, existing changed 0. VERIFIED.
2. REST (VERIFIED, type and codes):
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query fields=LookupCode,Meaning,EnabledFlag --output <RUN>/codes_after.json \
     "/fscmRestApi/resources/11.13.18.05/standardLookups/<TYPE>/child/lookupCodes" > <RUN>/rest.log 2>&1
   python3 -c "import json;print([i['LookupCode'] for i in json.load(open('<RUN>/codes_after.json'))['items']])"
   ```
   It prints your code(s).

## Rules and limits
- Never add codes to a seeded (`S`) or extensible (`E`) type in this task; create your own `U` type.
- A second code later: send the parent type row again unchanged plus the new code row (hierarchical package).
  GUESS (not tested).

## Worked example
Type `FSCRT_MZ_GF_LK1`, code `FSCRT_MZ_GF_A`: import ProcessId 100004742441892 (2 rows, 0 failed); after-export
ProcessId 100004743404730: types 1 -> 2, codes 1 -> 2, existing changed 0. VERIFIED.
