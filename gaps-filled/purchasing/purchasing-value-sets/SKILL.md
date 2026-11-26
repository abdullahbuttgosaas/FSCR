# Manage Purchasing Value Sets (PO_MANAGE_PURCHASING_VALUE_SETS): create an independent value set by FSM CSV

## What it is and when to use
Value sets in the Purchasing module hold the allowed values for Purchasing flexfield segments. Use this skill to
create a NEW independent value set with its values through FSCR's setup task CSV import. FSCR has no skill for it.
Route: FSM setup CSV (task `PO_MANAGE_PURCHASING_VALUE_SETS`, CSV supported: Y). VERIFIED.
Read-back also by REST `valueSets`. VERIFIED.

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<VS_CODE>`: new value set code, `<PREFIX>` + short name, upper case, e.g. `FSCRT_AB_GF_VS1`.
- `<VALUE>`: a value, e.g. `<PREFIX>V1` (must fit `MaximumLength`). Values are unique only within their value set,
  so the same value text in another set is fine. VERIFIED.
- `<MODULE_ID>`: the Purchasing module ID, read live (prerequisite 1).

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. Read the Purchasing module ID live (VERIFIED: the `ORA_PO_*` lookup types all carry it, and it is the module
   the task exports):
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query "q=LookupType LIKE 'ORA_PO%'" --query fields=LookupType,ModuleId --query limit=200 \
     --output <RUN>/po_module.json "/fscmRestApi/resources/11.13.18.05/standardLookups" > <RUN>/rest.log 2>&1
   python3 -c "import json;print({i['ModuleId'] for i in json.load(open('<RUN>/po_module.json'))['items'] if i['LookupType'].startswith('ORA_PO_')})"
   ```
   Exactly one ID must print; that is `<MODULE_ID>`.
2. Check `<VS_CODE>` is free:
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query "q=ValueSetCode='<VS_CODE>'" --output <RUN>/vs_check.json \
     "/fscmRestApi/resources/11.13.18.05/valueSets" > <RUN>/rest.log 2>&1
   python3 -c "import json;print(len(json.load(open('<RUN>/vs_check.json'))['items']))"
   ```
   It must print `0`. VERIFIED.

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `PO_MANAGE_PURCHASING_VALUE_SETS`. Six CSVs. The export holds only user-created value sets of
the module (it may be empty, or hold earlier test sets), so rows are written in full from this skill, not copied. You need `FND_APP_FLEX_VALUE_SET.csv` (the set) and
`ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv` (its values, linked by `FND_APP_FLEX_VALUE_SET.ValueSetCode`). VERIFIED.

## Build rows
Codes are Oracle's codes, not meanings: validation type `INDEP` (not INDEPENDENT), data type `VARCHAR2`, subtype
`TEXT` (seen on existing Purchasing value sets via REST `valueSets`). VERIFIED.
```json
{"FND_APP_FLEX_VALUE_SET.csv": [{"ValueSetCode": "<VS_CODE>", "ModuleId": "<MODULE_ID>",
   "Description": "<VS_CODE> test value set", "ValidationType": "INDEP", "ValueDataType": "VARCHAR2",
   "ValueSubtype": "TEXT", "MaximumLength": "20", "UppercaseOnlyFlag": "N", "ZeroFillFlag": "N",
   "SecurityEnabledFlag": "N"}],
 "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv": [{"FND_APP_FLEX_VALUE_SET.ValueSetCode": "<VS_CODE>", "Value": "<VALUE>",
   "Description": "<VS_CODE> test value 1", "EnabledFlag": "Y", "SummaryFlag": "N"}]}
```
- Add more value rows for more values (same `ValueSetCode`). Each value must be at most `MaximumLength`. VERIFIED (1 value).
- Table-validated or dependent sets need the other CSVs: not covered here (GUESS).
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Application Flexfield Value Set ... A total of 2 rows were
processed. 0 rows of them failed" (set + value). VERIFIED.

## Read back
1. COMMON_STEPS step 4: `FND_APP_FLEX_VALUE_SET.csv` and `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv` each
   `added 1 ['<VS_CODE>']` (the values CSV lists the parent value set code, not the value), all other CSVs added 0,
   existing changed 0. VERIFIED.
2. REST (VERIFIED):
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query "q=ValueSetCode='<VS_CODE>'" \
     --query fields=ValueSetCode,ValidationType,ValueDataType,MaximumLength --output <RUN>/vs_after.json \
     "/fscmRestApi/resources/11.13.18.05/valueSets" > <RUN>/rest.log 2>&1
   python3 -c "import json;print([(i['ValueSetCode'],i['ValidationType'],i['MaximumLength']) for i in json.load(open('<RUN>/vs_after.json'))['items']])"
   ```
   Pass = one tuple: your code, `INDEP`, your maximum length.

## Rules and limits
- Create your own value set only. Never add values to a value set other people's flexfields use.
- A value set is not used until a flexfield segment points to it (see the Purchasing DFF skill, which is written
  but not tested because a deploy changes shared pages).

## Worked example
`FSCRT_MZ_GF_VS1` with value `FSCRT_MZ_GF_V1`: import ProcessId 100004743402716 (2 rows, 0 failed); after-export
ProcessId 100004743405729: sets 0 -> 1, values 0 -> 1, existing changed 0; REST returns INDEP, max length 20. VERIFIED.
