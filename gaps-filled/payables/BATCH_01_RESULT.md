# Batch 01 - Payables gap fill (sitting 1, 2026-11-25, initials AK)

## Time log

| Time | Step |
| --- | --- |
| 21:12 | sitting start; token expired, sign-in started (port 8765 free) |
| 21:17 | sign-in complete (waiting time, not task time) |
| 21:17-21:23 | Manage Invoice Holds and Releases: export, own test, skill, fresh test F, fix, retest R |
| 21:20-21:27 | Manage Invoice Tolerances: export, own test, REST, skill, fresh test F, fix, retest R |
| 21:23-21:29 | Manage Aging Periods: export, own test, skill, fresh test F |
| 21:27-21:39 | Manage Payables Lookups: export, 3 failed tries + proven fix, skill, fresh test F |
| 21:35-21:49 | Manage Disbursement Lookups: export, own test, skill, fresh test F, fix, retest R |
| 21:40-21:44 | screen-only checks of the 7 tasks with CSV flag N (not counted toward the limit) |

## Tasks

| Task code | Task | Status | Working min | Waiting min | Test records | Import ProcessIds |
| --- | --- | --- | --- | --- | --- | --- |
| AP_MANAGE_INVOICE_HOLDS_AND_RELEASES | Manage Invoice Holds and Releases | tested | 9 | 3 | FSCRT_AK_GF_HLD1, _HLD1F, _HLD1R | 100004744396632, 100004744393889, 100004744391997 |
| AP_MANAGE_INVOICE_TOLERANCES | Manage Invoice Tolerances | tested | 7 | 3 | FSCRT_AK_GF_TOL1, _TOL1F, _TOL1R | 100004744396658, 100004744403910, 100004744397350 |
| AP_MANAGE_AGING_PERIODS | Manage Aging Periods | tested | 7 | 3 | FSCRT_AK_GF_AGE1, _AGE1F | 100004744404007, 100004744396714 |
| AP_MANAGE_PAYABLES_LOOKUPS | Manage Payables Lookups | tested | 12 | 5 | FSCRT_AK_GF_PG1, _PG1F (PAY GROUP) | failed tries 100004744396738, 100004744403973, 100004744397542; ok 100004744404058, 100004744404109 |
| IBY_MANAGE_LOOKUPS:_DISBURSEMENTS | Manage Disbursement Lookups | tested | 11 | 4 | FSCRT_AK_GF_BCB1, _BCB1F, _BCB1R (IBY_BANK_CHARGE_BEARER) | 100004743426030, 100004743426058, 100004744396882 |

Screen-only (7): IBY_MANAGE_SYSTEM_SECURITY_OPTIONS, IBY_INTEGRATE_EXTERNAL_PAYMENT_SYSTEMS,
IBY_MANAGE_BI_PUBLISHER_TEMPLATES, IBY_VIEW_VALIDATIONS, AP_DEFINE_AUTOMATED_INVOICE_PROCESSING_CONFIGURATION,
ORA_MANAGE_PAYABLES_WORKFLOW_RULES, IBY_GRANT_PAYMENT_FUNCTION_ACCESS (live task flags N/N, FSCR export refused,
no REST resource: see screen-only.csv).

## Problems and findings

- Payables lookups: a translation row for a NEW code makes the code fail (JBO-25027); `ChangeSinceLastRefresh`
  is required (JBO-27014). Fixed after 3 tries plus a column-by-column compare with a working code.
- Each new invoice hold also creates a `HOLD CODE` lookup code (seen in the Payables lookups export).
- REST: `payablesInvoiceTolerances` reads tolerances (lower-case attribute names in `q`); `genericLookups`
  reads lookup types; `standardLookups/<type>/child/lookupCodes` reads IBY codes; no REST for hold names or
  aging periods (404).
- The two IBY lookup tasks share package AND export scope (IBY module codes): run their tests one after the other.
- Helper fixes: `rest_read.py` no longer saves who-fields in its JSON (tester found user names in the saved
  file); `inspect_export.py --metadata` hides the environment field; `gf_import.py` hides "Submitted By".
- Evidence is plain text (.txt): the pack's CLAUDE.md allows PNG images only through make_images.py (max 4).

## Left after this batch

28 open tasks (see MODULE_TRACKER.csv). Batch 02 started: Manage Payment Codes (own test passed),
Manage Payment System Connectivity Lookups (export done).
