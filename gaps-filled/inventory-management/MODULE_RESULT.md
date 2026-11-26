# Gap fill: Inventory Management (tester HF, prefix FSCRT_HF_GF_)

## Cumulative counts (all sittings)

| tested | written-unsafe | failed | screen-only | left |
|---:|---:|---:|---:|---:|
| 10 | 0 | 0 | 0 | 63 |

## Sitting 1, continued after sign-in (26/11/2026 17:36 to 18:13)

Sign-in through the tester's Chrome at 17:36 (waiting time). Two batches of 5, all tested by the tester's own live
test plus fresh sub-agent tests; every wording fix was re-tested in this sitting (no retest pending).

### Counts this sitting

| tested | written-unsafe | failed | screen-only | left |
|---:|---:|---:|---:|---:|
| 10 | 0 | 0 | 0 | 63 |

### Tasks

| Task | Batch | Status | Working min | Waiting min | Test records |
|---|---|---|---:|---:|---|
| INV_MANAGE_INVENTORY_TRANSACTION_REASONS | 01 | tested | 11 | 7 | FSCRT_HF_GF_RSN1, RSN1F, RSN1R, RSN2R, RSN3R |
| INV_MANAGE_LOT_EXPIRATION_ACTIONS | 01 | tested | 11 | 7 | FSCRT_HF_GF_LEA1, LEA1F, LEA1R, LEA2R, LEA3R |
| INV_MANAGE_LOT_GRADES | 01 | tested | 11 | 7 | FSCRT_HF_GF_LG1, LG1F, LG1R, LG2R, LG3R |
| WSH_MANAGE_RELEASE_SEQUENCE_RULES | 01 | tested | 13 | 9 | FSCRT_HF_GF_RSR1, RSR1F, RSR1R, RSR2R, RSR3R |
| WSH_MANAGE_SHIPPING_COST_TYPES | 01 | tested | 13 | 9 | FSCRT_HF_GF_SCT1, SCT1F, SCT1R, SCT2R, SCT3R |
| INV_MANAGE_MATERIAL_STATUSES | 02 | tested | 16 | 9 | FSCRT_HF_GF_MS1, MS1F, MS1R |
| INV_MANAGE_PICKING_RULES | 02 | tested | 12 | 7 | FSCRT_HF_GF_PR1, PR1F, PR1R |
| INV_MANAGE_PICK_SLIP_GROUPING_RULES | 02 | tested | 12 | 7 | FSCRT_HF_GF_PSG1, PSG1F, PSG1R |
| INV_MANAGE_INVENTORY_LOOKUPS | 02 | tested | 14 | 9 | FSCRT_HF_GF_LK1 (code C1), LK1F (C1F), LK1R (C1R) |
| ORA_INV_MANAGE_INVENTORY_VALUE_SETS | 02 | tested | 14 | 9 | FSCRT_HF_GF_VS1 (value V1), VS1F (V1F), VS1R (V1R) |
| **Total** | | | **127** | **80** | 41 records (+ child codes/values) |

Minutes are shares of batches that ran 5 tasks in parallel.

### Failed tasks
None. Six first tries failed and were fixed by the second try (causes in each CHANGELOG): JBO-26041 empty
ObjectVersionNumber (release sequence rules), JBO-27014 Amount required (shipping cost types), INV_INT_TRXTYPCODE
non-status-controlled type (material statuses), ModuleId required (lookups, value sets).

### Left for the next sitting
63 tasks (58 route only and 5 neither; see my_gaps.csv, easiest first). The 5 "neither"
tasks still need the read-only export and REST check before they can be listed as screen-only.

### Test records created (all new, nothing existing changed)
All FSCRT_HF_GF_ records in the table above. ProcessIds are in BATCH_01_RESULT.md and BATCH_02_RESULT.md.


## Sitting 1, first attempt (26/11/2026, started 26/11/2026 17:28)

Stopped before batch 01: the Oracle sign-in could not be started. The earlier token had expired, and the
sign-in address (which holds the sign-in values) could not be opened in a browser on the tester's computer
without Claude reading or writing those values, which this run forbids. No Oracle call was made and no test
record was created.

Done offline: my_gaps.csv (73 missing tasks: 68 route only, 5 neither, ordered easiest first) and
MODULE_TRACKER.csv (all 73 rows, status open).

Next step: sign in (see the note to the tester) and paste the prompt again; batch 01 starts with
Inventory Transaction Reasons, Lot Expiration Actions, Lot Grades, Release Sequence Rules and Shipping Cost Types.

### Counts (this sitting = total)

| tested | written-unsafe | failed | screen-only | left |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 73 |

Working minutes: 0 on tasks. Waiting minutes: sign-in attempt only.
