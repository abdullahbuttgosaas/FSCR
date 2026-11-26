# Manage Approved Supplier List Statuses (PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES): create an ASL status by FSM CSV

## What it is and when to use
An approved supplier list (ASL) status (for example Approved, Debarred) controls whether a supplier-item entry can
be used for sourcing and for purchase order approval. Use this skill to create a NEW ASL status through FSCR's setup
task CSV import. FSCR has no skill for this task.
Route: FSM setup CSV (task `PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES`, CSV supported: Y). VERIFIED.
No REST resource found (`approvedSupplierListStatusesLOV` describe: not found). VERIFIED.

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<STATUS>`: the new status name, `<PREFIX>` + a short name, upper case, e.g. `FSCRT_AB_GF_AS1`.
- `<DESCRIPTION>`: free text with neutral test words, e.g. `FSCRT_AB_GF test ASL status` (maximum length not
  tested; about 40 characters worked, VERIFIED).

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. None. A status is a stand-alone record. VERIFIED.

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES`. One CSV:
`PO_APPROVED_SUPPLIER_LIST_STATUS.csv`, keyed by `Status`. Seeded statuses may not appear in the export. VERIFIED.

## Build rows
`<RUN>/rows.json`. VERIFIED:
```json
{"PO_APPROVED_SUPPLIER_LIST_STATUS.csv": [{"Status": "<STATUS>", "StatusDescription": "<DESCRIPTION>",
  "AllowPoApprovalFlag": "N", "AllowSourcingFlag": "N", "AslDefaultFlag": "N"}]}
```
- Flags take `Y` or `N`. Keep `AslDefaultFlag` = `N` on a shared environment: `Y` would make your status the
  default for new ASL entries (GUESS from the column name; not tested).
- Leave CreatedBy, LastUpdatedBy, InactiveDate and Attribute* empty. VERIFIED.
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Approved Supplier List Status. Status: Completed successfully
... 1 rows were processed. 0 rows of them failed". VERIFIED.

## Read back
COMMON_STEPS step 4. Expected: `PO_APPROVED_SUPPLIER_LIST_STATUS.csv` `added 1 ['<STATUS>']`, existing changed 0.
VERIFIED.

## Rules and limits
- New status names only (the name is the key; an existing name would be updated).
- Maximum length of `Status`: not found. 15 characters worked (VERIFIED); `<PREFIX>` already uses 12, so keep the
  short name to 3 characters unless you accept an untested length (GUESS beyond 15).

## Worked example
`FSCRT_MZ_GF_AS1`: import ProcessId 100004743402666 (1 processed, 0 failed); after-export ProcessId 100004743405690:
rows 1 -> 2, existing changed 0. VERIFIED.
