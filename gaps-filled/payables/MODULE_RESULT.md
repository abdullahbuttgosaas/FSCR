# Payables - gap fill result (FSM CSV / REST gaps)

Module: Payables (ERP). Initials: AK. Test prefix: FSCRT_AK_GF_. Gaps: 40 tasks (33 route only, 7 neither),
from evidence/Payables/data/scope_tasks.csv (coverage.csv: 6/46 tasks with a skill or guide).

## Cumulative counts (all sittings)

| Status | Count |
| --- | --- |
| tested | 9 |
| written (unsafe to test) | 0 |
| failed (proven cause + next step) | 1 |
| screen-only | 7 |
| left (open) | 23 |
| total gaps | 40 |

## Sitting 1 - 2026-11-25 (batches 01-02)

Counts this sitting: tested 9, written-unsafe 0, failed 1, screen-only 7 (checks; not counted toward the
limit), left 23. Sitting limit of 10 reached.

| Task code | Task | Status | Working min | Waiting min |
| --- | --- | --- | --- | --- |
| AP_MANAGE_INVOICE_HOLDS_AND_RELEASES | Manage Invoice Holds and Releases | tested | 9 | 3 |
| AP_MANAGE_INVOICE_TOLERANCES | Manage Invoice Tolerances | tested | 7 | 3 |
| AP_MANAGE_AGING_PERIODS | Manage Aging Periods | tested | 7 | 3 |
| AP_MANAGE_PAYABLES_LOOKUPS | Manage Payables Lookups | tested | 12 | 5 |
| IBY_MANAGE_LOOKUPS:_DISBURSEMENTS | Manage Disbursement Lookups | tested | 11 | 4 |
| IBY_MANAGE_PAYMENT_CODES | Manage Payment Codes | tested | 8 | 3 |
| IBY_MANAGE_LOOKUPS:_EXTERNAL_CONNECTIVITY | Manage Payment System Connectivity Lookups | tested | 7 | 3 |
| AP_MANAGE_TAX_REGIONS | Manage Tax Regions | tested | 8 | 3 |
| IBY_MANAGE_PAYMENT_METHODS | Manage Payment Methods | tested | 9 | 3 |
| IBY_MANAGE_PAYMENT_SYSTEMS | Manage Payment Systems | failed | 10 | 5 |
| **Total** | | | **88** | **35** |

Plus sign-in waiting: 5 minutes (21:12-21:17), and a second sign-in started at 22:00 that was not needed
(stopped at the end). Screen-only checks: about 4 working minutes.

### Failed tasks

- IBY_MANAGE_PAYMENT_SYSTEMS: create refused with FND_CMN_CMPLT_FLDS "You must complete the required
  fields" in 3 tries and in an exact round trip of a working screen-created payment system (ProcessId
  100004743428187), so the exported columns are not enough to create a payment system. Nothing was created
  (export compare: added 0). Next step: try a 10-character Suffix (FSCRT_AK_2); then read the task's CSV
  template export (read only) for mandatory attributes (e.g. Securityscheme, Activestatus, Supportedop);
  then retry. See manage-payment-systems/STATUS.md.

### Screen-only (7)

IBY_MANAGE_SYSTEM_SECURITY_OPTIONS, IBY_INTEGRATE_EXTERNAL_PAYMENT_SYSTEMS, IBY_MANAGE_BI_PUBLISHER_TEMPLATES,
IBY_VIEW_VALIDATIONS, AP_DEFINE_AUTOMATED_INVOICE_PROCESSING_CONFIGURATION, ORA_MANAGE_PAYABLES_WORKFLOW_RULES,
IBY_GRANT_PAYMENT_FUNCTION_ACCESS: live task flags CSV N / export-import N, FSCR export refuses them, no REST
resource (Oracle's Financials REST endpoint list; probes 404). Reasons in screen-only.csv.

### Left for the next sitting (23, easiest first; see my_gaps.csv)

IBY_MANAGE_CODE_MAP_GROUPS, AP_MANAGE_PAYABLES_DOCUMENT_SEQUENCES, AP_MANAGE_INTEREST_RATES,
IBY_MANAGE_TRANSMISSION_CONFIGURATIONS, IBY_MANAGE_FORMATS, AP_MANAGE_DISTRIBUTION_SETS,
AP_MANAGE_PAYABLES_DESCRIPTIVE_FLEXFIELDS, IBY_MANAGE_FLEXFIELDS:_DISBURSEMENTS,
IBY_MANAGE_FLEXFIELDS:_EXTERNAL_CONNECTIVITY, AP_MANAGE_PAYABLES_PROFILE_OPTIONS,
ORA_MANAGE_PAYABLES_QUEUE_DEFINITIONS, ORA_IBY_MANAGE_USER_DEFINED_RULES_FOR_EMP_BANK_ACCT_APPROVALS,
IBY_MANAGE_PAYMENT_METHOD_DEFAULTING_RULES, AP_MANAGE_REPORTING_ENTITIES,
ORA_AP_MANAGE_PAYMENT_PROCESS_REQUEST_TEMPLATE, IBY_MANAGE_PAYMENT_PROCESS_PROFILES,
ORA_IBY_MANAGE_VIRTUAL_CARD_PROGRAMS, AP_MANAGE_TAX_CODES, AP_MANAGE_WITHHOLDING_GROUPS,
AP_MANAGE_WITHHOLDING_CERTIFICATES, AP_MANAGE_TAX_REPORTING_AND_WITHHOLDING_TAX_OPTIONS,
ORA_MANAGE_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS, IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS.
Plus the next step of IBY_MANAGE_PAYMENT_SYSTEMS.

### Test records created (all new; nothing existing edited or deleted)

| Task | Records |
| --- | --- |
| Invoice holds | FSCRT_AK_GF_HLD1, FSCRT_AK_GF_HLD1F, FSCRT_AK_GF_HLD1R (each also adds a HOLD CODE lookup code, done by Oracle) |
| Invoice tolerances | FSCRT_AK_GF_TOL1, FSCRT_AK_GF_TOL1F, FSCRT_AK_GF_TOL1R |
| Aging periods | FSCRT_AK_GF_AGE1, FSCRT_AK_GF_AGE1F (3 lines each) |
| Payables lookups (PAY GROUP) | FSCRT_AK_GF_PG1, FSCRT_AK_GF_PG1F |
| Disbursement lookups (IBY_BANK_CHARGE_BEARER) | FSCRT_AK_GF_BCB1, FSCRT_AK_GF_BCB1F, FSCRT_AK_GF_BCB1R |
| Payment codes (PAYMENT_REASON) | FSCRT_AK_GF_PR1, FSCRT_AK_GF_PR1F |
| Connectivity lookups (IBY_SEC_CRED_TYPES) | FSCRT_AK_GF_SCT1, FSCRT_AK_GF_SCT1F |
| Income tax regions | FSCRT_AK_1, FSCRT_AK_F (10-character limit; long names start with FSCRT_AK_GF_) |
| Payment methods | FSCRT_AK_GF_PM1, FSCRT_AK_GF_PM1F (6 usage rules each) |

### Notes for the next sitting

- Helpers: gaps-filled/payables/scripts (gf_export, gf_import, inspect_export, build_fsm_package with
  @SUBMITTER, compare_fsm_exports, rest_read with --child, make_evidence, build_tracker).
- Evidence is text (.txt) because the pack's CLAUDE.md allows PNGs only through make_images.py (max 4).
- WORK folder (outside the pack, not in git): ../gwpayables (exports hold user names; never upload it).
