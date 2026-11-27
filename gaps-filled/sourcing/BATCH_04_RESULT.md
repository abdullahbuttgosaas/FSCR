# Sourcing batch 04 result (sitting 2, 2026-11-28)

Module: Sourcing and Supplier Management. Filled by AB with Claude. Prefix `GAPFILL_AB_S4_`. Work folder outside the repo (`gw\src\s2`).

## Time log
| Step | Start | Finish | Minutes |
|---|---|---|---:|
| Read-only exports / flag checks (waiting) | 00:27 | 00:28 | 1 |
| REST probes and own tests (controls test-and-restore, supplier POST) | 00:28 | 00:33 | 5 |
| Skills and cards (2 skills, 3 screen-only cards) | 00:33 | 00:36 | 3 |
| Fresh round F (2 in parallel) | 00:35 | 00:38 | 3 |
| Final own read-back | 00:42 | 00:42 | 1 |

## Tasks
| Task | Status | Working min | Waiting min | Test records (ProcessId) |
|---|---|---:|---:|---|
| Configure Supplier Qualification Controls | tested | 6 | 4 | test-and-restore: own Y->N (100004744440678) back Y (100004744440698); fresh Y->N (100004744441931) back Y (100004744442345) |
| Create Supplier in Procurement | tested | 5 | 1 | REST: SUP1 (supplier number 12331), SUP2F (12332), PROSPECTIVE |
| Configure Negotiation Award Outbound Service | screen-only | 2 | 1 | none |
| Manage Integration with Oracle Verification Services | screen-only | 2 | 1 | none |
| Specify User Category for New Supplier Users | screen-only | 2 | 1 | none |

## Problems and findings
1. **Qualification controls** is one global row with no create: test-and-restore on the notifications flag only; restore proved by compare with the first export (changed 0). Final row: NOT_ALLOWED, ALLOWED, Y.
2. **Create Supplier:** CSV export refused (flag N); REST `suppliers` create works (HTTP 201). The suppliers stay PROSPECTIVE (no sites, no contacts).
3. **Screen-only proof** (on each card): CSV export refused (flag N) and 5-6 REST names gave 404; for user category also 6 POZ profile options checked, none for user category.

## What is left (6, all "neither")
Load Supplier Interface through Scheduled Process, Upload Supplier Import File (FBDI pair: check the import scheduled process and UCM upload), Manage Supplier Negotiation Approvals, Manage Supplier Negotiation Award Approvals (approval rules: check BPM REST), Manage Sourcing Messages, Manage Supplier Qualification Messages (check messages CSV/REST before screen-only).
