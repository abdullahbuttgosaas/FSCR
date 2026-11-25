# Module result: Common Features (AB)

GoSaaS work, not official FSCR. Newest sitting first. The cards (`*/STATUS.md`) are the truth; `MODULE_TRACKER.csv` shows them.

## Cumulative counts (all sittings, after the sixth sitting 2026-11-26)
| Status | Count |
|---|---:|
| tested | 81 |
| written (unsafe to test) | 5 |
| failed | 1 |
| screen-only (proven) | 8 |
| open (left) | 53 |
| **Missing tasks in the module** | **148** |

Matches `MODULE_TRACKER.csv` (tested 81, skipped-unsafe 5, failed 1, screen-only 8, open 53) and `gap_progress.tsv` (which counts the failed task under Open: 54).

## Sitting 2026-11-26, sixth (batches 14 and 15)
**Counts this sitting:** 9 tested (3 of them re-opened from written-unsafe: Legal Entity Tax Profiles, Legal Reporting Unit Tax Profiles, Configuration Owner Tax Options), 0 written, 1 failed (Manage Application Tax Options), 0 screen-only. Sitting limit (10) reached. Details in `BATCH_14_RESULT.md` and `BATCH_15_RESULT.md`.

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 14 | Manage Legal Entity Tax Profiles | tested (was written, unsafe) | 11 | 4 |
| 14 | Manage Legal Reporting Unit Tax Profiles | tested (was written, unsafe) | 10 | 4 |
| 14 | Manage Configuration Owner Tax Options | tested (was written, unsafe) | 10 | 3 |
| 14 | Manage Legal Entity Financial Information | tested | 13 | 5 |
| 14 | Manage Legal Reporting Unit Financial Information | tested | 10 | 4 |
| 15 | Manage Associated Business Entities | tested | 19 | 6 |
| 15 | Manage Application Tax Options | failed (row not tied to the named business unit; proof by refused re-send was not valid) | 16 | 7 |
| 15 | Manage Set Assignments for Set Determinant Type | tested | 13 | 5 |
| 15 | Manage Segment Value Security Rules | tested | 10 | 3 |
| 15 | Manage Chart of Accounts Configurations | tested | 9 | 3 |
| | **Total** | **9 tested, 1 failed** | **121** | **44** |

Fresh tests: 9 of 10 PASS (application tax options FAIL); 9 re-tests after wording fixes, all PASS; prerequisite skills test-legal-entity and test-business-unit fresh and re-tested PASS. Sign-ins: 3 (renewals). New helpers: `scripts/own_row_package.py`, `scripts/compare_own_update.py`.

Test records created: test legal entities `GAPFILL_AB_B14_LE1`, `LE2F`, `LE3R` (each with its own main reporting unit and tax profiles; tax profiles, owner AP row and ActivityCode changed only on these); test business units `GAPFILL_AB_B15_BU1`, `BU2F`, `BU3`, `BU4F`, `BU5R`; associations LE1→BU3, LE2F→BU4F, LE3R→BU5R; reference data sets `GAPFILL_AB_B15_SET1`, `SET2F`, `SET3R` with SET assignments `PJF_RATES`→`COMMON`; secured value sets `GAPFILL_AB_B15_SVS1`, `SVS2F`, `SVS3R` (value `T1`); policies `GAPFILL_AB_B15_SVP1`, `SVP2F`, `SVP3R` (role General Accountant on SVS1). **Possible leftover:** one AP application tax options row from the first load (ProcessId 100004744413261) whose business unit Oracle may not have resolved; it cannot be seen by export or REST. AB to check on the page.

What is left (53 open + 5 written + 1 failed): application tax options (find the business unit column, check the page), Intercompany Exceptions and Associated Balancing Segments (need a test ledger), a test worker chain (Import Worker Users, Partner Organizations, resource organizations), descriptive flexfields, country-only tasks, and the other "neither" tasks.

## Sitting 2026-11-25, fifth (batch 13)
**Counts this sitting:** 4 tested (1 of them re-opened from written: Country Default Controls), 0 written, 0 failed, 1 screen-only (Manage Help Content, failed until 2026-11-26). One batch, asked for after the fourth sitting. Details in `BATCH_13_RESULT.md`.

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 13 | Manage Country Default Controls | tested (was written) | 8 | 3 |
| 13 | Set Help Options | tested (test-and-restore) | 10 | 4 |
| 13 | Manage Help Content | screen-only (was failed: CSV exists but cannot create a new topic; PrimaryHierarchyIds rejected on insert; the page creates the hierarchy ID) | 18 | 12 |
| 13 | Enable Click to Dial | tested (SITE test-and-restore, REST) | 7 | 0 |
| 13 | Configure Guided Learning | tested (SITE test-and-restore, REST) | 5 | 1 |
| | **Total** | **4 tested, 1 screen-only** | **48** | **20** |

Fresh tests: 4 of 4 PASS; 4 re-tests after wording fixes, all PASS. Sign-ins: 1. Test records: country rows `AQ`, `BV`, `HM` (every default N); help flag `OracleUnivEnabled`, `HZ_ENABLE_CLICK_TO_DIAL`, `FND_GUIDED_LEARNING_ENABLED` each changed and set back (old value proven by read-back); help content tries `GAPFILL_AB_B13_HT1` to `HT10` refused and a round trip of an existing topic (no change), nothing left.

What is left (60 open): a test legal entity chain (unlocks 4 written + LE financial info / balancing segments / business entities), a test worker chain (Import Worker Users, Partner Organizations, resource organizations), help content only by the page or a whole configuration package, descriptive flexfields, country-only tasks, and the other "neither" tasks.

## Sitting 2026-11-25, fourth (batches 11 and 12)
**Counts this sitting:** 10 tested (5 of them re-opened from written-unsafe under the new rule "a new prefix record nobody uses is not unsafe"), 0 written, 0 failed, 3 screen-only (proven; not counted in the limit). Sitting limit (10) reached.

| Batch | Task | Status | Working min | Waiting min |
|---|---|---|---:|---:|
| 11 | Create Implementation Users | tested (was written) | 10 | 1 |
| 11 | Manage Data Access for Users | tested (was written) | 8 | 1 |
| 11 | Manage Business Unit Data Access for Users | tested (was written) | 5 | 1 |
| 11 | Manage Reference Data Set Data Access for Users | tested (was written) | 4 | 1 |
| 11 | Manage Search Profile Options | tested (was written; USER level) | 7 | 1 |
| 12 | Manage Invoice Methods: Billing Extension Assignments | tested | 16 | 4 |
| 12 | Manage Revenue Methods: Billing Extension Assignments | tested | 7 | 3 |
| 12 | Manage ESS Job Definitions and Job Sets (FSCM) | tested | 9 | 2 |
| 12 | Manage ESS Job Definitions and Job Sets (CRM) | tested | 4 | 2 |
| 12 | Manage ESS Job Definitions and Job Sets (HCM) | tested | 4 | 2 |
| | **Total** | **10 tested** | **74** | **18** |

Screen-only (proven): Manage Languages, Manage Territories, Manage Time Zones (REST `languagesLOV`, `territoriesLOV`, `timezonesLOV` are get-only; plain resources 404; no FSM CSV). Reasons in `screen-only.csv`.

Fresh tests: 10 of 10 PASS; 2 re-tests after wording fixes (implementation users, invoice methods), both PASS. Sign-ins: 1 (waiting time). Failed tasks: none. Network drops (DNS) hit 2 imports and 2 exports; no import was repeated (log fetched by ProcessId).

Re-judged written cards that stay written (reasons in each STATUS.md): Common CRM BU Profile Options (SITE only), Map Reports to Work Areas (no delete, shows to all), Intercompany Exceptions + LE / LRU Tax Profiles + Configuration Owner Tax Options (safe way = a new test legal entity: long chain, next), Import Worker Users + Partner Organizations (safe way = a new test worker, then resource, then partner: next). Country Default Controls re-judged as safe (new row for an unused country): first task of the next sitting.

Test records created: test users `GAPFILL_AB_B11_U1`, `U2F`, `U3R` (mailbox @example.com, nobody signs in; U1 and U2F got General Accountant, Buyer, Order Administrator for the grant tests); 6 data access grants on U1 / U2F (data access sets `GAPFILL_AB_B5_DAS2`, `DAS3F`; business units; reference data sets); USER search values on U1 and U2F; invoice methods `GAPFILL_AB_B12_IM2`, `IM3F`, `IM4R`; revenue methods `GAPFILL_AB_B12_RM1`, `RM2F`; LOV sources `GAPFILL_AB_B12_LOV1` to `LOV6F`. Refused, nothing created: `IM1`, 2 grant tries, 1 profile value try.

What is left for the next sitting (64 open): Country Default Controls (ready), a test legal entity chain (unlocks 4 written + LE financial info / balancing segments / business entities), a test worker chain (unlocks Import Worker Users, Partner Organizations, resource organizations), help settings and help content, descriptive flexfields, country-only tasks, and the other "neither" tasks one by one.

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
