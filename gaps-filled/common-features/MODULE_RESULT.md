# Module result: Common Features (AB)

GoSaaS work, not official FSCR. Newest sitting first. The cards (`*/STATUS.md`) are the truth; `MODULE_TRACKER.csv` shows them.

## Cumulative counts (all sittings, after the third 2026-11-25 sitting)
| Status | Count |
|---|---:|
| tested | 58 |
| written (unsafe to test) | 14 |
| failed | 0 |
| screen-only (proven) | 4 |
| open (left) | 72 |
| **Missing tasks in the module** | **148** |

Matches `MODULE_TRACKER.csv` (tested 58, skipped-unsafe 14, screen-only 4, open 72) and `gap_progress.tsv`.

## Sitting 2026-11-25, third (batches 09 and 10)
**Counts this sitting:** 4 tested, 6 written (unsafe to test), 0 failed, 4 screen-only (proven; not counted in the limit). Sitting limit (10) reached.

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 09 | Manage Tax Registrations | tested | 14 | 3 |
| 09 | Manage Legal Document Sequences | tested | 11 | 6 |
| 09 | Manage Business Unit Document Sequences | tested | 10 | 5 |
| 09 | Manage Partner Organizations | written (unsafe) | 6 | 2 |
| 09 | Create Implementation Users | written (unsafe) | 4 | 0 |
| 10 | Manage Billing Extensions | tested | 10 | 4 |
| 10 | Import Worker Users | written (unsafe) | 3 | 0 |
| 10 | Manage Data Access for Users | written (unsafe) | 5 | 2 |
| 10 | Manage Business Unit Data Access for Users | written (unsafe) | 2 | 1 |
| 10 | Manage Reference Data Set Data Access for Users | written (unsafe) | 1 | 1 |
| | **Total** | **4 tested, 6 written** | **66** | **24** |

Screen-only (proven): Manage Applications Core Messages, Manage Messages, Manage Messages for General Ledger (REST `messages` is read-only: create refused), Manage Cross-Validation Rules (the CSV package has no rule object; REST 404). Reasons in `screen-only.csv`.

Fresh tests: 4 of 4 PASS in the end. Tax registrations failed its read-back as first written (`q=A and B` returns 0 rows; fixed to `;`, re-test PASS). Legal and BU sequences were re-tested after a wording fix (after-export ZIP check; one wrong sentence in the BU skill). Sign-ins: 1 (16 s, waiting time). Failed tasks: none.

Test records created: tax registrations `GAPFILL_AB_B9_TRG2`, `TRG3F`, `TRG4R` and test customer `GAPFILL_AB_B9_CUST3R` with its THIRD_PARTY tax profile; categories `GAPFILL_AB_B9_LC1`, `BC1`; legal sequences `GAPFILL_AB_B9_GSQ1`, `GSQ2F`, `GSQ3R`; BU sequences `GAPFILL_AB_B9_BSQ1`, `BSQ2F`, `BSQ3R`; billing extensions `GAPFILL_AB_B10_BX2`, `BX3F`. Refused, nothing created: `TRG1`, `PRT1`, `BX1`, message `GAPFILL_AB_B9_MSG1`.

New shared helper: `scripts/rest_call.py` (runs FSCR's REST client unchanged, shows Oracle's error text, hides the server address).

**Left for the next sitting:** 72 open (see `BATCH_10_RESULT.md`, "What is left", and `my_gaps.csv`).

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
