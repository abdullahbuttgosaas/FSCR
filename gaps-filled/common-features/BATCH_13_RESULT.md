# Batch 13 result: Common Features (AB), country default controls, help options and content, click to dial, guided learning

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (fifth Common Features sitting, one batch, asked for after the fourth sitting). One test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file edited. Work folder outside the repo. No existing record was edited or deleted; two SITE profile values and one help flag were changed and set back (test-and-restore, old value known, under the sitting-4 rule).

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 22:35 | 22:35 | 0 | Sign-in renewed |
| 22:36 | 22:38 | 2 | 4 read-only exports in parallel (waiting) |
| 22:38 | 22:40 | 2 | Click-to-dial scope and guided-learning option found by REST; guided-learning CSV refused (flag N) |
| 22:39 | 22:42 | 3 | Country AQ import + compare; click to dial and guided learning test-and-restore |
| 22:42 | 22:48 | 6 | Help content: 7 tries, all refused |
| 22:48 | 22:52 | 4 | Help settings test-and-restore (2 imports, 2 exports) |
| 22:52 | 22:58 | 6 | 5 skills written (1 failed card), helper one_value_package.py |
| 22:58 | 23:08 | 10 | Fresh tests (4 in parallel), wording fixes, re-tests R (3) |
| 23:01 | 23:12 | 11 | Cards, evidence, reports, index |
| 23:15 | 00:05 | 18 | Help content retry (asked by AB): docs research, round trip, 3 tries; about 20 min lost to an expired sign-in (waiting) |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records (ProcessId) |
|---|---|---|---:|---:|---|---|
| 1 | Manage Country Default Controls | tested (was written) | 6 + 2 | 3 | PASS, re-test R PASS | `AQ` (100004743428300); fresh `BV` (100004743427417); re-test `HM` (100004744404860) |
| 2 | Set Help Options | tested | 6 + 4 | 4 | PASS, re-test R PASS | OracleUnivEnabled N→Y→N (100004743427336, 100004743428382); fresh (100004744404768, 100004743428451); re-test (100004744404906, 100004743428470) |
| 3 | Manage Help Content | **screen-only** (was failed; retried) | 4 + 14 | 12 | not run | `GAPFILL_AB_B13_HT1` to `HT10`, all refused (HT1-7: 100004743427290, …428359, …426241, …429152, …428368, …426250, …426259; HT8-10: 100004744404985, 100004743427714, 100004743429241); round trip of an existing topic 100004744404970 (PASS, no change) |
| 4 | Enable Click to Dial | tested | 5 + 2 | 0 | PASS, re-test R PASS | SITE `HZ_ENABLE_CLICK_TO_DIAL` N→Y→N (3 s; fresh 4 s; re-test 5 s) |
| 5 | Configure Guided Learning | tested | 3 + 2 | 1 | PASS, re-test R PASS | SITE `FND_GUIDED_LEARNING_ENABLED` Y→N→Y (about 25 s; fresh 4 s; re-test 3 s) |
| | **Total** | **4 tested, 1 screen-only** | **48** | **20** | 4 of 4 (+4 re-tests) | |

## Problems and findings
1. **Country rows are safe for an unused country:** `CountryCode` + the 4 default flags `N` import first try; Oracle adds `RegimeTypeFlag I`. Countries have no name column, so the test records are uninhabited territories (`AQ`, `BV`, `HM`). The CSV route has no delete: the 3 rows stay (no effect on any transaction).
2. **Profile tasks with SITE-only options:** click to dial's option is named only in the export metadata scope (`HZ_ENABLE_CLICK_TO_DIAL`); the CSV export holds 0 rows (seeded values left out). REST PATCH of `siteProfileOptionValues/SITE` works; test-and-restore takes seconds when both body files are written first.
3. **Guided learning** has no CSV package (FSCR flag N); the option `FND_GUIDED_LEARNING_ENABLED` was found by REST search (link to the task is a GUESS from the name). Its lookup is `FND_SANDBOX_YESNO_TYPE`, not `YES_NO` (the fresh tester caught the wrong sentence).
4. **Help settings** are one config row: re-importing it with one flag changed works, and the content files can go header only.
5. **Help content create fails by CSV (retried 2026-11-26):** docs research, a REST probe (no help resource), a round trip of an existing topic (passes, no change) and 3 more tries (blank levels, type `OP`, an extra `PrimaryHierarchyIds` column) all end in the same error, whatever value is sent. Conclusion: the hierarchy id is made only by the page; CSV create is not possible on this release. Status changed from failed to **screen-only** on 2026-11-26 (AB): CSV exists but cannot create a new topic. Before the retry: `TopicId` and `Changed` are required, the title must be in the title file, then `PrimaryHierarchyIds isn't valid` every time, even with an existing topic's values. Nothing stayed behind (after-export: topics 5, titles 10).
6. Two fresh testers found that the import result is in `*_process_log.txt`, not in the FSCR import log (which ends with `StatusCode: (unknown)`); both skills now say so. One tester saw `WinError 10060` (network) on an export and re-ran it into a new folder.

## What is left
See `MODULE_RESULT.md` (60 open). Next: a test legal entity chain, a test worker chain, help content with valid hierarchy ids, descriptive flexfields, and the other "neither" tasks.
