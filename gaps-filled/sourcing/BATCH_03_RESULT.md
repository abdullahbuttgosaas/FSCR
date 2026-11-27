# Sourcing batch 03 result (sitting 2, 2026-11-28)

Module: Sourcing and Supplier Management. Filled by AB with Claude. Prefix `GAPFILL_AB_S3_`. Work folder outside the repo (`gw\src\s2`).

## Time log
| Step | Start | Finish | Minutes |
|---|---|---|---:|
| Sign-in (waiting) | 00:02 | 00:02 | 0 |
| Read-only exports of the 5 tasks (waiting) | 00:02 | 00:03 | 1 |
| Own tests (models, 2 DFFs, rule sets, relationship type 5 tries + match row) | 00:04 | 00:20 | 16 |
| Skills written (5) | 00:20 | 00:30 | 10 |
| Fresh round F (5 in parallel) | 00:30 | 00:34 | 4 |
| Wording fixes + re-tests R / R2 | 00:35 | 00:41 | 6 |
| Final own read-back of all records | 00:42 | 00:42 | 1 |

## Tasks
| Task | Status | Working min | Waiting min | Test records (ProcessId) |
|---|---|---:|---:|---|
| Manage Supplier Qualification Models | tested | 7 | 7 | QM1 (100004744440460), QM2F (100004744440645), QM3R (100004744441922) |
| Manage Sourcing Descriptive Flexfields | tested | 6 | 8 | SDX1 (100004743464718), SDX2F (100004744442287), SDX3R (100004744442314), SDX4R (100004744441956) |
| Manage Supplier Qualification Descriptive Flexfields | tested | 6 | 8 | QDX1 (100004744442213), QDX2F (100004744442270), QDX3R (100004744441909), QDX4R (100004744443166) |
| Manage Supplier Qualification Rule Sets | tested | 7 | 6 | try 1 refused (100004744441515, nothing created), RS1 (100004743464733), RS2F (100004743464790) |
| Configure Party Relationships for Supplier Match | tested | 12 | 9 | type tries 1-4 refused, type RT1 (100004744441598) + row (100004743464762), RT2F (100004743466695 / 100004744442300), RT3R (100004743466917 / 100004743464856) |

All names start with `GAPFILL_AB_S3_`. Models are on our own test units and DRAFT test areas; DFF contexts are disabled (deployed, used by nobody); rule sets are INACTIVE; relationship types are our own and used by no party.

## Problems and findings
1. **Qualification model export** lists only some models (an ACTIVE model of another unit was not listed); read back by REST too.
2. **Rule set status:** `DRAFT` refused (FND_CMN_INVALID_ATTRB_API_SERV); valid values ACTIVE / INACTIVE come from lookup `POQ_RULE_SET_STATUS`, readable only by `standardLookups` (not `commonLookups`). Used INACTIVE.
3. **Relationship type by CSV** needs the role texts (Name), `CreatedByModule = HZ_RM_UI`, and different subject and object plurals. Refused tries leave role lookups behind (2 orphans with our own texts, harmless) and a leftover makes the next try a duplicate. REST `relationshipTypes` is read only. The HZ export can lag.
4. **Supplier match list** was empty before; now it holds only our 3 types.
5. Fresh testers found 3 wrong sentences (model "0 rows in every file", DFF "Step 1's first two lines" and "cached sign-in returns at once", match "export holds 0 type rows"); each fixed and re-tested PASS with no wrong sentence.

## What is left
After batch 04: 6 tasks (see BATCH_04_RESULT.md).
