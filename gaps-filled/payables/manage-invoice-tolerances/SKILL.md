---
name: manage-invoice-tolerances
task_code: AP_MANAGE_INVOICE_TOLERANCES
task_name: Manage Invoice Tolerances
module: Payables
route: FSM setup CSV export/import (task level); REST read-back payablesInvoiceTolerances
---

# Manage Invoice Tolerances (CSV)

## What it is and when to use

Creates an invoice tolerance template (table AP_TOLERANCE_TEMPLATES, business object "Invoice Tolerance
Set") through the FSM setup CSV import of task `AP_MANAGE_INVOICE_TOLERANCES`. A tolerance template sets how
far a matched invoice may differ from the purchase order or receipt before invoice validation places a
matching hold. Templates are assigned to supplier sites later (supplier setup, not this skill).

Two types (VERIFIED in the export): `QUANTITY BASED` (for match basis Quantity) and `AMOUNT BASED` (for
match basis Amount). Oracle doc: a percentage of 0 allows no variance; an empty value allows infinite
variance.

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo (exports hold user names) |
| `<NAME>` | the new tolerance name (GUESS: up to 80 characters; tested with 17) |
| `<DESCRIPTION>` | short neutral description (for a test, start it with your prefix) |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<REST_VER>` | REST version, `11.13.18.05` |
| `<YOUR_TEST_PREFIX>` | the common start of your new names (for example your test prefix); a safety check in the builder |

Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw export CSVs and logs in it hold user names
(`rest_read.py` removes who-fields and links from the JSON it saves).

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour. If you are not allowed to sign in yourself, stop and report on HTTP 401/403; otherwise
sign in again and continue. Never print tokens, server addresses
or user names.

## Prerequisites

1. Signed in. A tolerance template is stand-alone; nothing else must exist.
2. Check the name is free (REST, read only):
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/payablesInvoiceTolerances \
     --q "toleranceName='<NAME>'" --fields toleranceName --out <RUN>/rest_check.json
   ```
   `items: 0` = free. If it exists, pick another name (re-sending it would update it).

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_INVOICE_TOLERANCES --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
```

One CSV, `AP_TOLERANCE_TEMPLATE.csv` (VERIFIED), columns: ToleranceName, Description, PriceTolerance,
QuantityTolerance, LastUpdateDate, LastUpdatedBy, QtyReceivedTolerance, LastUpdateLogin, CreationDate,
CreatedBy, MaxQtyOrdTolerance, MaxQtyRecTolerance, ShipAmtTolerance, RateAmtTolerance, TotalAmtTolerance,
ToleranceType, MaxQtyConTolerance, QtyConsumedTolerance.

## Build rows

`<RUN>/rows.json`, one row. Quantity based example (VERIFIED):

```json
{"AP_TOLERANCE_TEMPLATE.csv": [{"ToleranceName": "<NAME>", "Description": "<DESCRIPTION>",
  "ToleranceType": "QUANTITY BASED", "PriceTolerance": "2", "QuantityTolerance": "5",
  "QtyReceivedTolerance": "5"}]}
```

Column meaning (Oracle doc "Invoice Tolerances"; mapping GUESS from names): QuantityTolerance = ordered
percentage, MaxQtyOrdTolerance = maximum ordered quantity, QtyReceivedTolerance = received percentage,
MaxQtyRecTolerance = maximum received, QtyConsumedTolerance / MaxQtyConTolerance = consumed percentage /
maximum, PriceTolerance = price percentage. For `AMOUNT BASED` use ShipAmtTolerance (schedule amount),
RateAmtTolerance (conversion rate amount), TotalAmtTolerance (total amount) (GUESS: not loaded live).
Leave who-columns and dates empty (VERIFIED: the import fills them).

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --out <RUN>/load.zip
```

(`--prefix` is a safety check: every row must contain it.)

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code AP_MANAGE_INVOICE_TOLERANCES --zip <RUN>/load.zip --run <RUN> --label imp1
```

The console lines "StatusCode: (no result yet)" / "(unknown)" are normal; the process log text decides
success. Keep the ProcessId (`<RUN>/imp1_processid.txt`). Success (VERIFIED): business object "Invoice Tolerance
Set", "A total of 1 rows were processed. 0 rows of them failed". If the connection drops after the import
started, do NOT import again: wait 2 minutes and check with the REST query from Prerequisites.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_INVOICE_TOLERANCES --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/payablesInvoiceTolerances \
  --q "toleranceName='<NAME>'" \
  --fields toleranceName,toleranceType,priceTolerance,quantityTolerance,quantityReceivedTolerance \
  --out <RUN>/rest_readback.json
```

Pass = `RESULT: OK - only prefix rows added, nothing removed or changed` (after = before + 1) and REST returns 1 item with your values. REST attribute names
start in lower case (`toleranceName`); `ToleranceName` in `q` gives HTTP 400 (VERIFIED).

## Rules and limits

- New names only; never re-send an existing template (the import merges by ToleranceName and would update
  it). Never load the full export back.
- Percentages are numbers without a % sign.
- This skill does not assign the template to a supplier site.

## Worked example (sitting 1)

- `FSCRT_AK_GF_TOL1`, QUANTITY BASED, price 2, quantity 5, received 5: import ProcessId 100004744396658,
  1 row processed, 0 failed; only this row added; REST read-back 1 item (VERIFIED). Row counts depend on
  the environment (each test adds one); only "+1, removed/changed 0" matters.
