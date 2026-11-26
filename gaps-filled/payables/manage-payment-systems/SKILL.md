---
name: manage-payment-systems
task_code: IBY_MANAGE_PAYMENT_SYSTEMS
task_name: Manage Payment Systems
module: Payables
route: FSM setup CSV export/import (task level) - CREATE NOT WORKING YET (status failed, see Rules and limits)
---

# Manage Payment Systems (CSV) - status: failed (create path not proven)

## What it is and when to use

A payment system is the bank or payment processor that receives payment files from Oracle Payments (table
IBY_BEPINFO; business object "Payment System", detail "PaymentSystemInfo"), with its supported formats,
transmission protocols, payment schemes, account option names/values and keys. Task
`IBY_MANAGE_PAYMENT_SYSTEMS`.

This skill documents the export and the package layout (VERIFIED). Creating a NEW payment system through
the CSV import failed in sitting 1, even as an exact round trip of a working record (see Rules and limits).
Do not use it to create records until a later sitting marks it tested.

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo |
| `<SUFFIX>` | payment system code ("Suffix" column) |
| `<NAME>` | payment system name |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack |
| `<YOUR_TEST_PREFIX>` | the common start of your new codes; a safety check in the builder |
| `<REST_VER>` | `11.13.18.05` |

Create `<RUN>` first. Do not share it: the export holds user names AND the columns Bepusername, Beppassword,
Psusername, Pspassword (payment system credentials) and connection URLs. Never print those columns; view the
export only through `inspect_export.py --cols` with chosen columns.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). On HTTP 401/403
sign in again (or stop and report if you are not allowed to). Never print tokens, server addresses or user names.

## Prerequisites

1. Signed in.
2. GUESS: a bank (`BankName` must name an existing bank: a made-up name gave the error "Row Identifier:
   BankId" in try 1, VERIFIED). Check it read only:
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/cashBanks \
     --q "BankName='<BANK_NAME>'" --fields BankName,CountryName --out <RUN>/bank.json
   ```
   For a test, create your own bank first (Manage Banks; not covered here).
3. Seeded values used read only: a payment format code, a transmission protocol code (e.g. FTP_PUT) and a
   payment scheme (e.g. BANKACCOUNT) (VERIFIED in the export).

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code IBY_MANAGE_PAYMENT_SYSTEMS --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
```

Eight CSVs (VERIFIED): `IBY_PAYMENT_SYSTEM.csv` (57 columns, key Suffix), and children keyed by
`IBY_PAYMENT_SYSTEM.Suffix`: `ORA_IBY_PAYMENT_SYSTEM_FORMAT.csv` (PaymentFormatCode, StartDate, EndDate,
CodeMapGroupCode), `ORA_IBY_PAYMENT_SYSTEM_KEY.csv` (Key1, Ownertype, Defaults), `ORA_IBY_PAYMENT_SYSTEM_SCHEME.csv`
(Pmtschemename), `ORA_IBY_PAYMENT_SYSTEM_TRAN.csv` (TransmitProtocolCode), `ORA_IBY_PAYMENT_SYSTEM_ACC_NAME.csv`
(+ `_TRANSLATION`) and `ORA_IBY_PAYMENT_SYSTEM_ACC_VAL.csv` (account option values per BU).

## Build rows (shape tried in sitting 1 - NOT accepted)

```json
{"IBY_PAYMENT_SYSTEM.csv": [{"Suffix": "<SUFFIX>", "Name": "<NAME>", "BepType": "PROCESSOR",
   "BankName": "<BANK_NAME>", "HomeCountry": "US", "StartDate": "2026/01/01", "EndDate": "4712/12/31"}],
 "ORA_IBY_PAYMENT_SYSTEM_FORMAT.csv": [{"IBY_PAYMENT_SYSTEM.Suffix": "<SUFFIX>", "PaymentFormatCode": "<FORMAT>"}],
 "ORA_IBY_PAYMENT_SYSTEM_KEY.csv": [{"IBY_PAYMENT_SYSTEM.Suffix": "<SUFFIX>", "Key1": "<KEY>", "Ownertype": "PAYEE"}],
 "ORA_IBY_PAYMENT_SYSTEM_SCHEME.csv": [{"IBY_PAYMENT_SYSTEM.Suffix": "<SUFFIX>", "Pmtschemename": "BANKACCOUNT"}],
 "ORA_IBY_PAYMENT_SYSTEM_TRAN.csv": [{"IBY_PAYMENT_SYSTEM.Suffix": "<SUFFIX>", "TransmitProtocolCode": "FTP_PUT"}]}
```

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --out <RUN>/load.zip
```

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code IBY_MANAGE_PAYMENT_SYSTEMS --zip <RUN>/load.zip --run <RUN> --label imp1
```

Result in sitting 1 (VERIFIED): "Detail Object: PaymentSystemInfo ... 1 rows of them failed", "Row Identifier:
<SUFFIX>. Message Code: FND_CMN_CMPLT_FLDS. Message Text: You must complete the required fields." The log
does not name the field. A refused row creates nothing (VERIFIED by a new export: added 0).

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code IBY_MANAGE_PAYMENT_SYSTEMS --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
```

There is no REST resource for payment systems (VERIFIED: `paymentSystems`, `externalPaymentSystems` 404).

## Rules and limits

- PROVEN CAUSE (sitting 1): an exact round trip of a working, screen-created payment system (every exported
  column copied; only Suffix and Name changed; who-columns from SubmittedBy) is refused with
  FND_CMN_CMPLT_FLDS. So the export does not carry every field that the import requires to CREATE a
  payment system; the missing field is not named in the log.
- NEXT STEP: (1) test whether the Suffix length matters with a 10-character code that keeps the record
  prefix rule (e.g. `FSCRT_XX_2`; the working records have 4-10 characters); (2) if still refused, compare
  with Oracle's "Payment System" CSV import template (setupTaskCSVTemplateExports for this task, read only)
  for mandatory attributes, e.g. Securityscheme, Activestatus, Supportedop; (3) only then retry.
- Never re-send an existing payment system (the import merges by Suffix and would update it, including its
  credentials). Never load the full export back.
