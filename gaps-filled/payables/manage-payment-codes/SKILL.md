---
name: manage-payment-codes
task_code: IBY_MANAGE_PAYMENT_CODES
task_name: Manage Payment Codes
module: Payables
route: FSM setup CSV export/import (task level), IBY_PAYMENT_CODE.csv; REST read-back paymentCodesLOV
---

# Manage Payment Codes (CSV)

## What it is and when to use

Creates an Oracle Payments payment code (table IBY_PAYMENT_CODES; business object "Payment Code") through the
FSM setup CSV import of task `IBY_MANAGE_PAYMENT_CODES`. Payment codes are the values a payment file can
carry: payment reasons, delivery channels, bank instructions, local instruments and service levels.

Types in the data (VERIFIED): `PAYMENT_REASON`, `DELIVERY_CHANNEL`, `BANK_INSTRUCTION`, `LOCAL_INSTRUMENT`,
`SERVICE_LEVEL`. Loaded live: `PAYMENT_REASON`; the others use the same columns (GUESS).

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo |
| `<TYPE>` | one of the payment code types above |
| `<CODE>` | the new payment code, upper case (tested with 16 characters; longest existing code 19) |
| `<FORMAT_VALUE>` | the value written in the payment file, e.g. `PR1` |
| `<TERRITORY>` | optional two-letter country code (empty = all countries) |
| `<MEANING>` | name shown to users (for a test, start it with your prefix) |
| `<START_DATE>` | `YYYY/MM/DD` |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<YOUR_TEST_PREFIX>` | the common start of your new codes (for example your test prefix); a safety check in the builder |
| `<REST_VER>` | `11.13.18.05` |

Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw export CSVs and logs in it hold user names.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour. If you are not allowed to sign in yourself, stop and report on HTTP 401/403; otherwise
sign in again and continue. Never print tokens, server addresses or user names.

## Prerequisites

1. Signed in. A payment code is stand-alone.
2. The code must be new (REST, read only; `items: 0` = free):
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/paymentCodesLOV \
     --q "PaymentCode='<CODE>'" --fields PaymentCode,PaymentCodeType --out <RUN>/code_check.json
   ```

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code IBY_MANAGE_PAYMENT_CODES --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
```

"status (unknown)" is normal. Two CSVs (VERIFIED): `IBY_PAYMENT_CODE.csv` (PaymentCodeType, PaymentCode,
TerritoryCode, FormatValue, SeededFlag, Meaning, StartDate, Description, EndDate, EndDateDsp, Code, who/date
columns) and `IBY_PAYMENT_CODE_TRANSLATION.csv` (one row per code and language).

## Build rows

`<RUN>/rows.json`, ONE code row and NO translation row (VERIFIED: Oracle creates the US translation):

```json
{"IBY_PAYMENT_CODE.csv": [{"PaymentCodeType": "<TYPE>", "PaymentCode": "<CODE>", "TerritoryCode": "<TERRITORY>",
  "FormatValue": "<FORMAT_VALUE>", "SeededFlag": "N", "Meaning": "<MEANING>", "Description": "<MEANING>",
  "StartDate": "<START_DATE>", "EndDate": "4712/12/31"}]}
```

- `EndDate` is REQUIRED (VERIFIED: without it `JBO-27014: Attribute EndDate in PaymentCodeEO is required`).
  `4712/12/31` = no end, as in the existing rows.
- `SeededFlag` `N` (all existing rows have N).
- Leave who-columns, `EndDateDsp` and `Code` empty (VERIFIED).

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --out <RUN>/load.zip
```

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code IBY_MANAGE_PAYMENT_CODES --zip <RUN>/load.zip --run <RUN> --label imp1
```

The console lines "StatusCode: (no result yet)" / "(unknown)" are normal. In the process-log lines that
gf_import prints look for (VERIFIED): "Detail Object: PaymentCode. Status: Completed successfully ... 1 rows
were processed. 0 rows of them failed" and "Total Objects Failed: 0". Keep the ProcessId
(`<RUN>/imp1_processid.txt`). If the connection drops after the import started, do NOT import again: wait
2 minutes and run the REST check of Prerequisites step 2.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code IBY_MANAGE_PAYMENT_CODES --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/paymentCodesLOV \
  --q "PaymentCode='<CODE>'" --out <RUN>/rest_readback.json
```

Pass = IBY_PAYMENT_CODE.csv +1, IBY_PAYMENT_CODE_TRANSLATION.csv +1, `RESULT: OK - only prefix rows added,
nothing removed or changed`, and REST returns 1 item (PaymentCodeName = your meaning, PaymentCodeAlias = your
format value, EndDate 4712-12-31) (VERIFIED).

## Rules and limits

- New codes only; never re-send existing codes (the import merges by type + code); never load the full export.
- A new code shows up in payment file choices (e.g. payment reasons on invoices); give it a clear meaning.

## Worked example (sitting 1)

- `PAYMENT_REASON` / `FSCRT_AK_GF_PR1`, format value PR1: try 1 (no EndDate) refused, ProcessId
  100004743427065; try 2 ProcessId 100004744404205, 1 row processed, 0 failed; compare codes +1,
  translations +1, removed/changed 0; REST 1 item (VERIFIED). Row counts depend on the environment.
