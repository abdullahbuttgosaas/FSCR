# Order Management - gap fill result

## Cumulative counts (all sittings)
| Status | Count |
|---|---:|
| tested | 10 |
| written (unsafe to test) | 0 |
| failed | 0 |
| screen-only | 9 |
| left (open) | 16 |
| **Missing tasks in total** | **35** |

## Sitting 1 - 2026-11-26 (batches 01-02), filled by AK
Counts this sitting: tested 10, written-unsafe 0, failed 0, screen-only 9 (checks, not counted), left 16.

| Task | Status | Working min | Waiting min |
|---|---|---:|---:|
| Manage Status Values | tested | 10 | 6 |
| Manage Task Types | tested | 10 | 6 |
| Manage Jeopardy Priorities | tested | 10 | 6 |
| Manage Channel Program Types | tested | 10 | 6 |
| Manage Pricing Matrix Types | tested | 10 | 6 |
| Manage Pricing Results Presentations | tested | 10 | 5 |
| Manage Pricing Totals | tested | 10 | 5 |
| Manage Time Unit Mappings | tested | 12 | 5 |
| Manage External Service Details for Algorithms | tested | 12 | 6 |
| Manage Order Attachment Categories | tested | 12 | 6 |
| **Total** | | **106** | **57** |

Plus sign-in waiting 2 minutes and about 6 working minutes for the 9 screen-only checks (not task time).

Failed tasks: none. Unsafe tasks: none.

Screen-only (9, `screen-only.csv`): Manage Channel Messages; Run Migrate Pending Approvals to BPM Workflow Process;
Collect Order Reference Data; Generate Bucket Sets for Business Rules; Load Order Reference Data from Flat Files;
Manage External Interface Transformation Style Sheets; Manage Integration with Oracle Fusion Distributed Order
Orchestration; Publish Extensible Flexfield Attributes; Review Collected Order Reference Data. Each: Oracle's CSV
export returns no ProcessId and no REST resource exists (GET 404); 5 are scheduled processes, not setup records.

Left for the next sitting (16, easiest first in my_gaps.csv): Manage Constraint Entities; Manage Jeopardy Thresholds;
Manage Task Status Conditions; Manage Processing Constraints; Manage Upstream and Fulfillment Source Systems; Manage
Order Attributes That Identify Change; Manage Pricing Process Assignments; Manage Product Transformation Rules; Manage
Orchestration Process Definitions; Manage Order Descriptive Flexfields; Manage Pricing Descriptive Flexfields; Manage
Posttransformation Defaulting Rules; Manage Pretransformation Defaulting Rules; Manage Pretransformation Rules for
Sales Orders; Manage Process Assignment Rules for Sales Orders; Manage External Integration Routing Rules for Sales
Orders. Ready prerequisites: test task types FSCRT_AK_GF_TT1/_TTF/_TTR and status codes FSCRT_AK_GF_ST1/_STF/_STR (for
Jeopardy Thresholds and Task Status Conditions).

Test records created (all new, FSCRT_AK_GF_ names; nothing existing edited or deleted):
- Status codes FSCRT_AK_GF_ST1, _STF, _STR (+ translations)
- Task types FSCRT_AK_GF_TT1, _TTF, _TTR (+ Create/Inbound services, translations)
- Jeopardy priorities FSCRT_AK_GF_JP1 (1000-1010), _JPF (1020-1030), _JPR (1040-1050)
- Channel program types FSCRT_AK_GF_PT1, _PTF, _PTR (Draft, + 2 qualifiers each)
- Pricing matrix types FSCRT_AK_GF_MT1, _MTF, _MTR (inactive)
- Pricing results presentations FSCRT_AK_GF_RP1, _RPF, _RPR
- Pricing totals FSCRT_AK_GF_TOA, _TOF (not enabled for transactions)
- Units of measure ZK1 (FSCRT_AK_GF_U1), ZKF (FSCRT_AK_GF_UF); time unit mappings FSCRT_AK_GF_TU1, _TUF
- External services FSCRT_AK_GF_WS1, _WSF (no URL)
- Attachment categories FSCRT_AK_GF_AC2, _ACF on the order header; FSCRT_AK_GF_AC1 (outside the DOO module)

Shared helpers written: `gaps-filled/common-features/scripts/` (export_task.sh, import_task.sh, read_import_log.py,
build_fsm_package.py, compare_fsm_exports.py, inspect_export.py, rest_read.py, rest_write.py, gf_tracker.py,
write_card.py). No FSCR file was changed.
