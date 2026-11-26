---
name: manage-disbursement-lookups
task_code: "IBY_MANAGE_LOOKUPS:_DISBURSEMENTS"
task_name: Manage Disbursement Lookups
module: Payables
route: FSM setup CSV export/import (task level), FUN_APP_GENERIC_LOOKUP.csv; REST genericLookups + standardLookups
---

# Manage Disbursement Lookups (CSV)

## What it is and when to use

Adds a new lookup code to an extensible Oracle Payments (IBY) lookup type used by disbursements (for example
`IBY_BANK_CHARGE_BEARER`) through the FSM setup CSV import of task `IBY_MANAGE_LOOKUPS:_DISBURSEMENTS`
(business object "Financials Generic Lookup"). IBY types are standard lookups: ViewApplicationId 0, owning
application FND (VERIFIED).

Use it for extensible types only (CustomizationLevel `E` or `U`). Never change predefined codes.

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo |
| `<LOOKUP_TYPE>` | an extensible IBY lookup type, e.g. `IBY_BANK_CHARGE_BEARER` |
| `<CODE>` | the new lookup code, upper case, max 30 characters (GUESS from FND lookup column size) |
| `<MEANING>` | the display meaning (for a test, start it with your prefix) |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<YOUR_TEST_PREFIX>` | the common start of your new codes (for example your test prefix); a safety check in the builder |
| `<REST_VER>` | `11.13.18.05` |

The task code contains a colon: always quote it on the command line (`"IBY_MANAGE_LOOKUPS:_DISBURSEMENTS"`).
Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw export CSVs and logs in it hold user names.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour. If you are not allowed to sign in yourself, stop and report on HTTP 401/403; otherwise
sign in again and continue. Never print tokens, server addresses or user names.

## Prerequisites

1. Signed in.
2. (Optional) list the extensible IBY types:
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/genericLookups \
     --q "LookupType LIKE 'IBY%';CustomizationLevel<>'S'" --limit 200 --fields LookupType,CustomizationLevel \
     --out <RUN>/types.json
   ```
3. Read your type LIVE (never copy ids from an export):
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/genericLookups \
     --q "LookupType='<LOOKUP_TYPE>'" \
     --fields LookupType,ViewApplicationId,ApplicationShortName,ModuleId,CustomizationLevel --out <RUN>/type.json
   ```
   It must return 1 item with CustomizationLevel `E` or `U`. ViewApplicationId, ApplicationShortName and
   ModuleId go into the row (`rest_read.py` saves the whole item in `<RUN>/type.json`; `--fields` only
   chooses what is printed).
4. The code must be new (REST, read only; `items: 0` = free):
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py \
     --endpoint /fscmRestApi/resources/<REST_VER>/standardLookups/<LOOKUP_TYPE>/child/lookupCodes \
     --q "LookupCode='<CODE>'" --fields LookupCode,Meaning --out <RUN>/code_check.json
   ```

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code "IBY_MANAGE_LOOKUPS:_DISBURSEMENTS" --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
```

"status (unknown)" is normal. Four CSVs (VERIFIED): `ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv` and
`_TRANSLATION` (types, not exported: 0 rows), `FUN_APP_GENERIC_LOOKUP.csv` (codes) and
`FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv`. Only non-seeded codes are exported, so the CSVs can be empty; the
headers are all the builder needs.

## Build rows

`<RUN>/rows.json` with ONE code row and NO translation row, shaped like this:

```json
{"FUN_APP_GENERIC_LOOKUP.csv": [{"LookupType": "<LOOKUP_TYPE>", "LookupCode": "<CODE>",
  "ViewApplicationId": "<ViewApplicationId>", "SetCode": "COMMON",
  "Meaning": "<MEANING>", "Description": "<MEANING>", "EnabledFlag": "Y",
  "ModuleKey": "<ApplicationShortName>", "ModuleType": "APPLICATION", "ModuleId": "<ModuleId>",
  "ChangeSinceLastRefresh": "N", "CreatedBy": "@SUBMITTER", "LastUpdatedBy": "@SUBMITTER"}]}
```

Write it from `<RUN>/type.json` with this snippet (fill CODE and MEANING; nothing is typed by hand):

```bash
python3 - <<'PY'
import json
RUN, CODE, MEANING = "<RUN>", "<CODE>", "<MEANING>"
t = json.load(open(RUN + "/type.json"))["items"][0]
row = {"LookupType": t["LookupType"], "LookupCode": CODE, "ViewApplicationId": str(t["ViewApplicationId"]),
       "SetCode": "COMMON", "Meaning": MEANING, "Description": MEANING, "EnabledFlag": "Y",
       "ModuleKey": t["ApplicationShortName"], "ModuleType": "APPLICATION", "ModuleId": t["ModuleId"],
       "ChangeSinceLastRefresh": "N", "CreatedBy": "@SUBMITTER", "LastUpdatedBy": "@SUBMITTER"}
json.dump({"FUN_APP_GENERIC_LOOKUP.csv": [row]}, open(RUN + "/rows.json", "w"), indent=1)
print("rows.json written")
PY
```

- `ChangeSinceLastRefresh` N is REQUIRED; a translation row for a NEW code makes the row fail; Oracle creates
  the US translation itself (VERIFIED on the same business object in Manage Payables Lookups).
- `SetCode` `COMMON` was accepted for a ViewApplicationId 0 type (VERIFIED).
- `@SUBMITTER` is replaced by the builder with the export's SubmittedBy value (never typed or printed).

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --max-len LookupCode=30 --out <RUN>/load.zip
```

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code "IBY_MANAGE_LOOKUPS:_DISBURSEMENTS" --zip <RUN>/load.zip \
  --run <RUN> --label imp1
```

The console lines "StatusCode: (no result yet)" / "(unknown)" are normal. In the process-log lines that
gf_import prints look for (VERIFIED): "Detail Object: LookupGeneric1. Status: Completed successfully ...
1 rows were processed. 0 rows of them failed" and "Total Objects Failed: 0". Keep the ProcessId
(`<RUN>/imp1_processid.txt`). If the connection drops after the import started, do NOT import again: wait
2 minutes and run the REST check of Prerequisites step 4.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code "IBY_MANAGE_LOOKUPS:_DISBURSEMENTS" --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/rest_read.py \
  --endpoint /fscmRestApi/resources/<REST_VER>/standardLookups/<LOOKUP_TYPE>/child/lookupCodes \
  --q "LookupCode='<CODE>'" --fields LookupCode,Meaning,EnabledFlag --out <RUN>/rest_readback.json
```

Pass = codes +1, translations +1 (the two type CSVs stay at 0 rows), `RESULT: OK - only prefix rows added, nothing removed or changed`, and
REST returns 1 item with your meaning (VERIFIED).

## Rules and limits

- New codes on extensible IBY types only; never re-send existing or predefined codes; never load the full
  export back.
- A new code appears in the lists that use the type (e.g. bank charge bearer choices); give it a clear
  test meaning so nobody picks it by mistake.

## Worked example (sitting 1)

- `IBY_BANK_CHARGE_BEARER` / `FSCRT_AK_GF_BCB1`: ProcessId 100004743426030, 1 row processed, 0 failed;
  export compare codes +1, translations +1, removed/changed 0; REST standardLookups 1 item (VERIFIED). Row
  counts depend on the environment; only "+1, removed/changed 0" matters.
