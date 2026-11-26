---
name: manage-payment-methods
task_code: IBY_MANAGE_PAYMENT_METHODS
task_name: Manage Payment Methods
module: Payables
route: FSM setup CSV export/import (task level), parent method + usage rules in one package; REST read-back disbursementPaymentMethodsLOV
---

# Manage Payment Methods (disbursement payment methods, CSV)

## What it is and when to use

Creates an Oracle Payments disbursement payment method (tables IBY_PAYMENT_METHODS_B/_TL and its usage rules
IBY_APPLICABLE_PMT_MTHDS; business object "DisbursementPaymentMethod") through the FSM setup CSV import of task
`IBY_MANAGE_PAYMENT_METHODS`. A payment method (for example check, wire, EFT) is chosen on invoices and
payments; its usage rules say for which applications, payees, business units, legal entities and
transaction types it may be used.

This skill creates a method enabled for Payables only, usable for all payees, business units, legal
entities and transaction types, domestic and foreign. It does not change defaulting rules, so no existing
invoice or supplier gets the new method by default.

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo |
| `<CODE>` | the new payment method code, upper case, max 30 characters (GUESS; tested with 15) |
| `<NAME>` | the method name shown to users (for a test, start it with your prefix) |
| `<START_DATE>` | `YYYY/MM/DD` (from date) |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<YOUR_TEST_PREFIX>` | the common start of your new codes (for example your test prefix); a safety check in the builder |
| `<REST_VER>` | `11.13.18.05` |

Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw export CSVs and logs in it hold user names.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour. If you are not allowed to sign in yourself, stop and report on HTTP 401/403; otherwise
sign in again and continue. Never print tokens, server addresses or user names.

## Prerequisites

1. Signed in. A payment method with "all" usage rules needs no other record.
2. The code must be new (REST, read only; `items: 0` = free):
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/disbursementPaymentMethodsLOV \
     --q "PaymentMethodCode='<CODE>'" --fields PaymentMethodCode,PaymentMethodName --out <RUN>/check.json
   ```

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code IBY_MANAGE_PAYMENT_METHODS --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
```

"status (unknown)" is normal. Five CSVs (VERIFIED):
- `ORA_IBY_FD_PARENT_PAY_MET.csv`: the method (87 columns: code, name, flags, dates, DFF attributes).
- `IBY_FD_PAYMENT_METHOD.csv`: usage rules, child of the method (ApplicableTypeCode, ApplicableValueFrom/To,
  PaymentFlow, ApplicationShortName, BuName, LEName, ExcludeFromApplicFlag).
- `ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION.csv`: names per language.
- `ORA_PMT_METHOD_VALIDATION_ASSIGNMENT.csv` and `ORA_PAYMENT_METHOD_VALIDATION_VALUE.csv`: validations.

## Build rows

`<RUN>/rows.json`: ONE method row plus its usage rows, in the same package (usage rows are children and
are processed only with their parent). No translation row (Oracle creates the US one, VERIFIED). No
validation rows (optional, GUESS).

```json
{"ORA_IBY_FD_PARENT_PAY_MET.csv": [{"PaymentMethodCode": "<CODE>", "PaymentMethodName": "<NAME>",
   "Description": "<NAME>", "SeededFlag": "N", "StartDate": "<START_DATE>", "EndDate": "4712/12/31",
   "PmtEnableAp": "Y", "PmtEnableAr": "N", "PmtEnableCe": "N", "SupportBillsPayableFlag": "N",
   "PaymentFormatAplFlag": "O", "BankChargeBearerAplFlag": "O", "PaymentReasonAplFlag": "O",
   "PaymentReasonComntAplFlag": "O", "RemittanceMessage1AplFlag": "O", "RemittanceMessage2AplFlag": "O",
   "RemittanceMessage3AplFlag": "O", "UniqueRemittanceIdAplFlag": "O", "UriCheckDigitAplFlag": "O",
   "DeliveryChannelAplFlag": "O", "SettlementPriorityAplFlag": "O", "ExclusivePmtAplFlag": "O",
   "ExternalBankAcctAplFlag": "O"}],
 "IBY_FD_PAYMENT_METHOD.csv": [
   {"ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode": "<CODE>", "PaymentMethodCode": "<CODE>",
    "ApplicableTypeCode": "CROSS_BORDER_FLAG", "ApplicableValueTo": "FOREIGN_AND_DOMESTIC",
    "PaymentFlow": "DISBURSEMENTS", "ApplicationShortName": "AP"},
   {"ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode": "<CODE>", "PaymentMethodCode": "<CODE>",
    "ApplicableTypeCode": "FOREIGN_CURRENCY_FLAG", "ApplicableValueTo": "FOREIGN_AND_DOMESTIC",
    "PaymentFlow": "DISBURSEMENTS", "ApplicationShortName": "AP"},
   {"ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode": "<CODE>", "PaymentMethodCode": "<CODE>",
    "ApplicableTypeCode": "PAYEE", "PaymentFlow": "DISBURSEMENTS", "ApplicationShortName": "AP"},
   {"ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode": "<CODE>", "PaymentMethodCode": "<CODE>",
    "ApplicableTypeCode": "PAYER_LE", "PaymentFlow": "DISBURSEMENTS", "ApplicationShortName": "AP"},
   {"ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode": "<CODE>", "PaymentMethodCode": "<CODE>",
    "ApplicableTypeCode": "PAYER_ORG", "PaymentFlow": "DISBURSEMENTS", "ApplicationShortName": "AP"},
   {"ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode": "<CODE>", "PaymentMethodCode": "<CODE>",
    "ApplicableTypeCode": "PAY_PROC_TRXN_TYPE", "PaymentFlow": "DISBURSEMENTS", "ApplicationShortName": "AP"}]}
```

- The `*AplFlag` columns say whether a payment attribute is used by the method; `O` = optional (VERIFIED as
  the values a screen-created method has; other values GUESS: `R` required, `N` not used).
- A usage row with an empty ApplicableValueFrom/To = "all" for that type (VERIFIED as the shape of a
  screen-created method). To limit the method, use BuName / LEName or values (GUESS, not tested).
- Leave who-columns and dates of creation empty (VERIFIED).

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --max-len PaymentMethodCode=30 --out <RUN>/load.zip
```

The builder must report `ORA_IBY_FD_PARENT_PAY_MET.csv 1 row(s), IBY_FD_PAYMENT_METHOD.csv 6 row(s)`.

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code IBY_MANAGE_PAYMENT_METHODS --zip <RUN>/load.zip --run <RUN> --label imp1
```

The console lines "StatusCode: (no result yet)" / "(unknown)" are normal. In the process-log lines that
gf_import prints look for (VERIFIED): "Detail Object: DisbursementPaymentMethod. Status: Completed
successfully ... 1 rows were processed. 0 rows of them failed" and "Total Objects Failed: 0" (the log counts
only the method; the export compare proves the usage rows). Keep the ProcessId (`<RUN>/imp1_processid.txt`).
If the connection drops after the import started, do NOT import again: wait 2 minutes and run the REST check
of Prerequisites step 2.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code IBY_MANAGE_PAYMENT_METHODS --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/disbursementPaymentMethodsLOV \
  --q "PaymentMethodCode='<CODE>'" --fields PaymentMethodCode,PaymentMethodName,FromDate,EndDate --out <RUN>/rest_readback.json
```

Pass (VERIFIED) = ORA_IBY_FD_PARENT_PAY_MET.csv +1, IBY_FD_PAYMENT_METHOD.csv +6,
ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION.csv +1 (automatic), validation CSVs +0,
`RESULT: OK - only prefix rows added, nothing removed or changed`, and REST returns 1 item.

## Rules and limits

- New methods only; never re-send an existing method or its usage rows (the import merges by code and would
  update them); never load the full export back.
- A new method appears in the payment method lists of Payables; give it a clear test name. Do not add it to
  defaulting rules or supplier sites in a test.

## Worked example (sitting 1)

- `FSCRT_AK_GF_PM1` (Payables only, 6 "all" usage rules): ProcessId 100004743428080, 1 row processed, 0 failed;
  compare: method +1, usage +6, translation +1, validations 0, removed/changed 0; REST LOV 1 item (VERIFIED).
  Row counts depend on the environment.
