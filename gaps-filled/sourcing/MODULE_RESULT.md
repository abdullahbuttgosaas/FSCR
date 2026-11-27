# Sourcing and Supplier Management: module result

Owner AB. Prefix `GAPFILL_AB_`. Cards (`*/STATUS.md`) are the truth; `MODULE_TRACKER.csv` shows them.

## Cumulative counts (all sittings)
| Status | Count |
|---|---:|
| tested | 17 |
| written (unsafe to test) | 0 |
| failed | 0 |
| screen-only | 3 |
| open (left) | 6 |
| **total missing tasks** | **26** |

---

## Sitting 2 (2026-11-28, batches 03 and 04)

**Counts this sitting:** 7 tested, 0 written-unsafe, 0 failed, 3 screen-only. 6 left.

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 03 | Manage Supplier Qualification Models | tested | 7 | 7 |
| 03 | Manage Sourcing Descriptive Flexfields | tested | 6 | 8 |
| 03 | Manage Supplier Qualification Descriptive Flexfields | tested | 6 | 8 |
| 03 | Manage Supplier Qualification Rule Sets | tested | 7 | 6 |
| 03 | Configure Party Relationships for Supplier Match | tested | 12 | 9 |
| 04 | Configure Supplier Qualification Controls | tested | 6 | 4 |
| 04 | Create Supplier in Procurement | tested | 5 | 1 |
| 04 | Configure Negotiation Award Outbound Service | screen-only | 2 | 1 |
| 04 | Manage Integration with Oracle Verification Services | screen-only | 2 | 1 |
| 04 | Specify User Category for New Supplier Users | screen-only | 2 | 1 |
| | **Total** | | **55** | **46** |

Wall clock about 41 minutes (00:02 to 00:43); batch 04 ran while batch 03 fresh tests ran.

**Failed tasks:** none.

**Test records created (all new, none edited):**
- Qualification models `GAPFILL_AB_S3_QM1`, `QM2F`, `QM3R` (own test units, DRAFT test areas).
- DFF contexts (disabled): `GAPFILL_AB_S3_SDX1/SDX2F/SDX3R/SDX4R` (PON_PROGRAM_HEADERS), `QDX1/QDX2F/QDX3R/QDX4R` (POQ_INITIATIVES).
- Rule sets `GAPFILL_AB_S3_RS1`, `RS2F` (INACTIVE).
- Relationship types + supplier match rows `GAPFILL_AB_S3_RT1`, `RT2F`, `RT3R`; 2 orphan role lookups from refused tries (own texts).
- Suppliers `GAPFILL_AB_S4_SUP1` (12331), `SUP2F` (12332), PROSPECTIVE.
- Qualification controls: no record; one shared flag changed and restored twice (final value same as before).

**Left for the next sitting (6, all "neither"):** Load Supplier Interface through Scheduled Process, Upload Supplier Import File, Manage Supplier Negotiation Approvals, Manage Supplier Negotiation Award Approvals, Manage Sourcing Messages, Manage Supplier Qualification Messages.

Reports: `BATCH_03_RESULT.md`, `BATCH_04_RESULT.md`. Screen-only list: `screen-only.csv`.

---

## Sitting 1 (2026-11-27, batches 01 and 02)

**Counts this sitting:** 10 tested, 0 written-unsafe, 0 failed, 0 screen-only. 16 left.

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 01 | Manage Assessment Outcome Lookup | tested | 13 | 4 |
| 01 | Manage Qualification Outcome Lookup | tested | 13 | 4 |
| 01 | Manage Standards Organization Lookup | tested | 13 | 4 |
| 01 | Manage Subject Lookup | tested | 13 | 4 |
| 01 | Manage Sourcing Lookups | tested | 13 | 4 |
| 02 | Manage Sourcing Value Sets | tested | 15 | 5 |
| 02 | Manage Supplier Qualification Value Sets | tested | 15 | 5 |
| 02 | Manage Negotiation Styles | tested | 13 | 4 |
| 02 | Manage Attribute Lists | tested | 15 | 5 |
| 02 | Manage Qualification Areas | tested | 14 | 4 |
| | **Total** | | **137** | **43** |

Minutes are each task's share of its batch (tasks of a batch ran in parallel; wall clock for both batches about 37 minutes, 23:18 to 23:55, plus about 1 minute sign-in).

**Failed tasks:** none.

**Test records created (all new, none edited):**
- Lookup codes: `GAPFILL_AB_S1_AO1/AO2F/AO3R/AO4R` (POQ_ASSESSMENT_OUTCOME), `QO1/QO2F/QO3R/QO4R` (ORA_POQ_QUALIFICATION_OUTCOME), `SO1/SO2F/SO3R` (POQ_STDS_ORG), `SJ1/SJ2F/SJ3R` (POQ_SUBJECT), `SL1`, `SL3R` (PON_LINE_ATTRIBUTE_GROUPS), `SL2F` (PON_HEADER_ATTRIBUTE_GROUPS).
- Value sets: `GAPFILL_AB_S2_SVS1/SVS2F/SVS3R` (Sourcing module), `QVS1/QVS2F/QVS3R` (Supplier Qualification module), each with values `GAPFILL_A`, `GAPFILL_B`.
- Negotiation styles: `GAPFILL_AB_S2_STY1`, `STY2F` (copies of Standard_Negotiation, ACTIVE, SystemFlag N).
- Attribute lists: `GAPFILL_AB_S2_ATL1`, `ATL2F` (ACTIVE, 1 group GENERAL, 1 text attribute).
- Qualification areas: `GAPFILL_AB_S2_QA1` (own unit BU1), `QA2F` (own unit BU2F), DRAFT, 1 outcome each.

**New helpers** (`sourcing\scripts\`): `scope_lookup_types.py`, `clone_rows.py`; copied from Procurement: `build_module_tracker.py`, `build_csv_package.py`, `compare_exports.py`, `lookup_type_row.py`, `read_import_log.py`.

**Left for the next sitting (16, easiest first):** Manage Qualification Models (needs a qualification area: use the DRAFT test areas), Manage Sourcing Descriptive Flexfields and Supplier Qualification DFFs (disabled context), Manage Supplier Qualification Rule Sets, Configure Party Relationships for Supplier Match, Configure Supplier Qualification Controls (likely one shared setting: test-and-restore or written-unsafe), then the 10 "neither" tasks (prove CSV and REST before screen-only): Configure Negotiation Award Outbound Service, Create Supplier in Procurement, Load Supplier Interface through Scheduled Process, Manage Integration with Oracle Verification Services, Manage Sourcing Messages, Manage Supplier Negotiation Approvals, Manage Supplier Negotiation Award Approvals, Manage Supplier Qualification Messages, Specify User Category for New Supplier Users, Upload Supplier Import File.

Reports: `BATCH_01_RESULT.md`, `BATCH_02_RESULT.md`.
