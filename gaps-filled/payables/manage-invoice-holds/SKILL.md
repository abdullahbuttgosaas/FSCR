---
name: manage-invoice-holds
task_code: AP_MANAGE_INVOICE_HOLDS_AND_RELEASES
task_name: Manage Invoice Holds and Releases
module: Payables
route: FSM setup CSV export/import (task level)
---

# Manage Invoice Holds and Releases (CSV)

## What it is and when to use

Creates a user-defined invoice hold or release name (table AP_HOLD_CODES, business object "Approval Code")
through the FSM setup CSV import of task `AP_MANAGE_INVOICE_HOLDS_AND_RELEASES`. Use it to add a new hold
name (for example a manual hold that blocks payment) or a new release name. It never changes the
predefined holds that invoice validation uses.

Oracle allows user-defined names only for these types (Oracle doc "Invoice Holds and Releases"):
holds `INVOICE HOLD REASON` and `LINE HOLD REASON` (shown as "Invoice Line Reason"); releases
`INVOICE RELEASE REASON`, `HOLD QUICK RELEASE REASON`, `INV QUICK RELEASE REASON`,
`MATCHING RELEASE REASON`, `VARIANCE RELEASE REASON`. VERIFIED live for `INVOICE HOLD REASON`; GUESS for the
others.

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo (exports hold user names) |
| `<CODE>` | the new hold name, upper case, max 25 characters (column limit, VERIFIED: longest existing code is 25) |
| `<HOLD_TYPE>` | one of the user-definable types above |
| `<DESCRIPTION>` | short description |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<YOUR_TEST_PREFIX>` | the common start of your new codes (for example your test prefix); a safety check in the builder |

Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw CSVs and logs in it hold user names.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour; on HTTP 401/403 or a hang, sign in again and continue (if you are not allowed to sign in
yourself, stop and report it). Never print tokens, server addresses
or user names.

## Prerequisites

1. Signed in (above). No other setup record is needed: a hold name is stand-alone.
2. Check the code does not exist yet: run the export below and search for `<CODE>` (step "Export").
   `--grep` matches parts of codes, so look for an EXACT HoldLookupCode match in the rows it shows.
   If it exists, choose another code; never re-send an existing code (the import would update it).

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_INVOICE_HOLDS_AND_RELEASES --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip --file AP_HOLD_CODE.csv --grep <CODE>
```

The package holds one CSV, `AP_HOLD_CODE.csv` (VERIFIED), columns: HoldLookupCode, HoldType,
LastUpdateDate, LastUpdatedBy, UserReleaseableFlag, UserUpdateableFlag, InactiveDate, PostableFlag,
LastUpdateLogin, CreationDate, CreatedBy, ExternalDescription, HoldInstruction, WaitBeforeNotifyDays,
ReminderDays, InitiateWorkflowFlag, DspDescription. Note the row count (it is the "before" count).

## Build rows

Write `<RUN>/rows.json` with ONE new row (only these columns; leave the rest empty):

```json
{"AP_HOLD_CODE.csv": [{"HoldLookupCode": "<CODE>", "HoldType": "<HOLD_TYPE>",
  "UserReleaseableFlag": "Y", "UserUpdateableFlag": "Y", "PostableFlag": "N",
  "InitiateWorkflowFlag": "N", "DspDescription": "<DESCRIPTION>"}]}
```

- UserReleaseableFlag `Y` = users can release it manually; PostableFlag `N` = the invoice cannot be
  accounted while on this hold (Oracle doc). InitiateWorkflowFlag `Y` would route it to the holds
  resolution workflow (GUESS: then WaitBeforeNotifyDays/ReminderDays apply).
- Who-columns stay empty (VERIFIED: the import fills them).

Build a package that holds only this row (every other CSV keeps its header only):

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --max-len HoldLookupCode=25 --out <RUN>/load.zip
```

(`--prefix` is a safety check: every row must contain your test prefix. Outside a test, pass the common
start of your codes.)

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code AP_MANAGE_INVOICE_HOLDS_AND_RELEASES \
  --zip <RUN>/load.zip --run <RUN> --label imp1
```

The console lines "StatusCode: (no result yet)" / "(unknown)" are normal; the process log text decides
success. Keep the printed ProcessId (saved in `<RUN>/imp1_processid.txt`); it is the key to the full process log.
Success looks like (VERIFIED): business object "Approval Code" ... "A total of 1 rows were processed. 0 rows
of them failed". If the connection drops after the import started, do NOT import again: wait 2 minutes,
then fetch the log with `--process-id <ProcessId>` or export again and look for `<CODE>`.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_INVOICE_HOLDS_AND_RELEASES --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/after.zip --file AP_HOLD_CODE.csv --grep <CODE>
```

The compare prints "before N, after N+1, added 1, removed/changed 0" per CSV.
Pass = after count is before + 1, `RESULT: OK`, and the row shows your values. There is no REST resource
for hold names (VERIFIED: `payablesHoldCodes` and `invoiceHoldCodes` return 404), so the export compare is
the read-back.

## Rules and limits

- New codes only. Never re-send an existing code, a predefined (ORA_ or seeded) hold, or the full export:
  the import merges by HoldLookupCode and would update the existing row.
- HoldLookupCode max 25 characters.
- Do not try to create types that do not allow user-defined names (matching, variance, account, funds,
  period, insufficient information holds); invoice validation owns them.
- Nothing can be deleted by CSV; to retire a hold later, set InactiveDate on a screen or by a new import of
  that same code (that is an update: only for your own code).

## Worked example (sitting 1)

- Code `FSCRT_AK_GF_HLD1`, type `INVOICE HOLD REASON`: import ProcessId 100004744396632, 1 row processed,
  0 failed; only that row added (VERIFIED). Row counts depend on the environment (each test adds one);
  only "+1, removed/changed 0" matters.
