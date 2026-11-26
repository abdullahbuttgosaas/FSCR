# Batch 02 - Payables gap fill (sitting 1, 2026-11-25, initials AK)

## Time log

| Time | Step |
| --- | --- |
| 21:44-21:53 | Manage Payment Codes: export, try 1 refused (EndDate), try 2 ok, skill, fresh test F |
| 21:44-21:56 | Manage Payment System Connectivity Lookups: export (shared scope found), own test after the disbursement retest, skill, fresh test F |
| 21:53-21:59 | Manage Tax Regions: export, try 1 refused (length), try 2 ok, skill, fresh test F |
| 21:56-22:05 | Manage Payment Methods: export, own test, skill, fresh test F |
| 21:59-22:06 | Manage Payment Systems: export, 3 tries + prerequisite check + 2 round trips, all refused -> failed with proven cause |
| 22:00 | second sign-in started at the 45-minute mark; not needed in the end (no 401/403 before the sitting limit); listener stopped |

## Tasks

| Task code | Task | Status | Working min | Waiting min | Test records | Import ProcessIds |
| --- | --- | --- | --- | --- | --- | --- |
| IBY_MANAGE_PAYMENT_CODES | Manage Payment Codes | tested | 8 | 3 | FSCRT_AK_GF_PR1, _PR1F | refused 100004743427065; ok 100004744404205, 100004743427101 |
| IBY_MANAGE_LOOKUPS:_EXTERNAL_CONNECTIVITY | Manage Payment System Connectivity Lookups | tested | 7 | 3 | FSCRT_AK_GF_SCT1, _SCT1F (IBY_SEC_CRED_TYPES) | 100004743427114, 100004743426159 |
| AP_MANAGE_TAX_REGIONS | Manage Tax Regions | tested | 8 | 3 | FSCRT_AK_1, FSCRT_AK_F (long names carry FSCRT_AK_GF_) | refused 100004743425947; ok 100004743427182, 100004743425983 |
| IBY_MANAGE_PAYMENT_METHODS | Manage Payment Methods | tested | 9 | 3 | FSCRT_AK_GF_PM1, _PM1F | 100004743428080, 100004743427230 |
| IBY_MANAGE_PAYMENT_SYSTEMS | Manage Payment Systems | failed | 10 | 5 | none (all refused; export: added 0) | 100004743426216, 100004743428155, 100004743429062, 100004743429083, 100004743428187 |

## Problems and findings

- Payment codes: `EndDate` is required (JBO-27014); 4712/12/31 = open.
- Income tax regions: RegionShortName max 10 characters (JBO-27040 at 15). The 12-character GF prefix cannot
  be the key. A name without FSCRT_ was rejected as against the pack rule (and blocked); `FSCRT_AK_1` keeps
  the pack rule and the long name carries `FSCRT_AK_GF_`.
- The two IBY lookup tasks export the same codes (all user codes of the IBY module): tests ran one after
  the other.
- Payment systems: FND_CMN_CMPLT_FLDS even for an exact round trip of a working record, so the export lacks
  a field the import requires. Next step in the card.
- Payment methods: usage rows must be in the same package as the method; the log counts only the method.

## Left after this batch

23 open tasks (see MODULE_TRACKER.csv / my_gaps.csv); 1 failed task with a next step. Sitting limit (10)
reached: no further batch in this sitting.
