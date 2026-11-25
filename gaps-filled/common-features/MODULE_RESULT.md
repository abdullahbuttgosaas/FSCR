# Module result: Common Features (AB)

GoSaaS work, not official FSCR. Newest sitting first. The cards (`*/STATUS.md`) are the truth; `MODULE_TRACKER.csv` shows them.

## Cumulative counts (all sittings, after the second 2026-11-25 sitting)
| Status | Count |
|---|---:|
| tested | 54 |
| written (unsafe to test) | 8 |
| failed | 0 |
| screen-only (proven) | 0 |
| open (left) | 86 |
| **Missing tasks in the module** | **148** |

Matches `MODULE_TRACKER.csv` (tested 54, skipped-unsafe 8, open 86) and `gap_progress.tsv`.

## Sitting 2026-11-25, second (batches 07 and 08)
**Counts this sitting:** 6 tested, 4 written (unsafe to test), 0 failed, 0 screen-only. Sitting limit (10) reached. All 49 "neither" tasks checked for CSV and REST (results in `my_gaps.csv`, see BATCH_08_RESULT.md).

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 07 | Manage Account Hierarchy Labels | tested | 10 | 3 |
| 07 | Manage Tree Labels | tested | 7 | 2 |
| 07 | Manage Trees and Tree Versions | tested | 11 | 4 |
| 07 | Manage Account Hierarchies | tested | 11 | 5 |
| 07 | Manage Tree Structures | tested | 12 | 5 |
| 08 | Manage Ledger Document Sequences | tested | 11 | 5 |
| 08 | Manage Legal Entity Tax Profiles | written (unsafe) | 4 | 1 |
| 08 | Manage Configuration Owner Tax Options | written (unsafe) | 3 | 1 |
| 08 | Manage Intercompany Exceptions | written (unsafe) | 3 | 1 |
| 08 | Manage Legal Reporting Unit Tax Profiles | written (unsafe) | 3 | 1 |
| | **Total** | **6 tested, 4 written** | **75** | **28** |

Fresh tests: 6 of 6 PASS (account hierarchy labels and ledger sequences after one wording fix and a re-test). Sign-ins: 2, under 5 s each (waiting time).

## Sitting 2026-11-25 (batches 05 and 06)
**Counts this sitting:** 6 tested, 4 written (unsafe to test), 0 failed, 0 screen-only. Sitting limit (10) reached.

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 05 | Search Legal Entities | tested | 8 | 2 |
| 05 | Search Legal Reporting Units | tested | 5 | 2 |
| 05 | View Accounting Configuration Summary | tested | 8 | 2 |
| 05 | View Service Clients | tested | 5 | 2 |
| 05 | Manage Data Access Sets | tested | 12 | 5 |
| 06 | Manage Daily Rates | tested | 9 | 3 |
| 06 | Manage Search Profile Options | written | 4 | 1 |
| 06 | Manage Common CRM Business Unit Profile Options | written | 3 | 1 |
| 06 | Map Reports to Work Areas | written | 4 | 1 |
| 06 | Manage Country Default Controls | written | 4 | 1 |
| | **Total** | | **62** | **20** |

Not in any task: sign-in 2.5 min (waiting), 12 planning exports 4.5 min (waiting), set-up and reports about 12 min. Fresh tests ran in parallel, so wall clock was about 35 minutes (02:17 to 02:52).

**Failed tasks:** none.

**Written (unsafe to test), reason and next step:** see `BATCH_06_RESULT.md`. All 4 change a setting every user of the environment gets (seeded profile options, a work-area report link, a country's tax defaults). Next step for each: load-test only on an environment we own, with written approval.

**Test records created (all new; none edited or deleted):**
- `GAPFILL_AB_B5_DAS2`, `GAPFILL_AB_B5_DAS3F`: data access sets (full ledger, read/write) on one existing ledger each; given to no user. (`GAPFILL_AB_B5_DAS1` refused, not created.)
- `GAPFILL_AB_B6_DRT1` (cross rates on, no rules), `GAPFILL_AB_B6_DRT2` (rules EUR, GBP), `GAPFILL_AB_B6_DRT3F` (rules CAD, EUR): conversion rate types, pivot USD; no rates, no ledger uses them.
- View/search tasks: none (existing records were only read).

**New helpers:** `search-legal-entities/scripts/view_record.py` (read-only export viewer that hides audit and person columns; `--match-cols`), `scripts/build_module_tracker.py` (builds `my_gaps.csv` and `MODULE_TRACKER.csv` from the index and the cards).

**Left for the next sitting:** 96 open (47 route only, 49 neither). Start with the "neither" checks (read-only export + REST GET, to prove screen-only or find a route) and the remaining route-only tasks in `my_gaps.csv`, easiest first. Many left are "change existing" or security tasks: expect more "written (unsafe to test)".

## Earlier sittings (before this file existed)
Batches 1 to 4, the batch 1 re-test and the tax-chain fixes (2026-11-15 to 2026-11-24): 42 Common Features gaps tested, 0 failed. Reports: `gaps-filled/BATCH1_PART1..3_RESULT.md`, `BATCH2_*`, `BATCH3_*`, `BATCH_TAXFIX*_RESULT.md`, `BATCH4_*`, `RETEST_BATCH1_RESULT.md`.
