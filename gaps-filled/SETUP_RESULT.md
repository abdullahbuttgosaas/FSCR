# Gap filling setup (result)

GoSaaS work, not official FSCR. Done by Claude for AB on 2026-11-20. Paper work only: no Oracle call, no sign-in, no FSCR file changed (FSCR was only read: `fscr-main\_fscr_run_36_scope_map\module_scope_map.csv` and `module_counts.csv`). Checked at the end: 0 files under `fscr-main` are newer than the start of this work (2026-11-20 17:06, the old index time).

## What I built

| Item | What |
|---|---|
| `gap_index_backup_2026-11-20.csv` | byte-identical copy of `gap_index.csv` before any change (150 rows, CRLF) |
| 12 x `STATUS.md` | one beside each finished `SKILL.md`: the 10 in `common-features\`, `general-ledger\manage-journal-categories`, `receivables\manage-alternate-name-mapping-rules` |
| `gap_index.csv` | extended from 150 to 935 rows (19 modules), new last column `screen_only`; CRLF kept |
| `rebuild_index.py` | rebuilds `gap_index.csv` and `gap_progress.tsv` from the cards and `screen-only.csv` files; standard library only |
| `gap_progress.tsv` | per-module progress, written by the script (CRLF) |
| `README.md` | new layout, STATUS.md card format, screen-only rule, `GAPFILL_<INITIALS>_` prefix, how to run the rebuild |
| `GAPS_PLAN.md` | new section 0 with the real batch 1 times; Tax Lookup Codes and LE Configurator Lookups marked done; P1 marked done; prefix question answered |

No other file was changed. The 2 one-off helper scripts (card writer, index extender) ran from Claude's scratchpad and were deleted.

## 1. STATUS.md cards

Facts come only from `gap_index.csv`, the three `BATCH1_PART*_RESULT.md` files and each `CHANGELOG.md`.

- `minutes_to_write` and `minutes_to_test` are the index values (the index's minutes_to_write is "working minutes: write + own live test" from the batch reports).
- `waiting_minutes` is the "Waiting min (Oracle)" column of the batch reports (sign-in not counted). For the 2 older GL/AR skills it is `unknown`; the AR note keeps the "about 8 of 12 test minutes were sign-in timeouts" fact.
- `minutes_to_write` is `unknown` for the 2 older skills (index blank: "skill writing not timed").
- `route` means how the record is created: `FSM CSV` for the 10 batch-1 skills and Journal Categories (REST is only their read-back), `REST` for Alternate Name Mapping Rules (REST POST).
- `depends_on` is `none` for all 12 (index blank).
- `test_records` lists the GAPFILL_ records from each CHANGELOG. Journal Categories: `unknown` (its CHANGELOG only says "FSCRT_ rows"). Alternate Name Mapping Rules: only `FSCRT_R25 Payer A` is named in the allowed sources, so the field says "others unknown".
- `retest_after_wording_fix: pending` is on **10** cards: Value Sets and Transaction Calendars (added on your decision, 2026-11-20; see "could not verify") and the 8 cards where a CHANGELOG says wording changed after the fresh test and was not re-tested: Standard Lookups, Geography Lookups, Resource Note Type, Tax Lookup Codes, LE Configurator Lookups, Conversion Rate Types, Journal Categories (Run 26c fixes after the 26b cold test), Alternate Name Mapping Rules (Run 27c fixes after the 27b cold test). For the last two the fixes were checked offline and with one read-only GET, but no new fresh-Claude test.
- Not marked: Document Sequence Categories (only a helper option `--json-out` was added after its fresh test), Attachment Categories (tester notes not applied).

## 2. Count checks (gap_index.csv)

| Module | Missing (module_counts.csv) | Rows in index | Added |
|---|---:|---:|---:|
| Common Features | 148 | 148 | 0 (existing rows kept) |
| Security | 0 | 0 | 0 |
| General Ledger | 155 | 155 | 154 (+ existing Journal Categories) |
| Payables | 40 | 40 | 40 |
| Receivables | 74 | 74 | 73 (+ existing Alternate Name Mapping Rules) |
| Cash Management | 19 | 19 | 19 |
| Fixed Assets | 18 | 18 | 18 |
| Expenses | 33 | 33 | 33 |
| Revenue Management | 22 | 22 | 22 |
| Project Financial Management | 199 | 199 | 199 |
| Purchasing | 11 | 11 | 11 |
| Procurement | 26 | 26 | 26 |
| Sourcing and Supplier Management | 26 | 26 | 26 |
| Inventory Management | 73 | 73 | 73 |
| Order Management | 35 | 35 | 35 |
| Manufacturing | 5 | 5 | 5 |
| Cost Management | 30 | 30 | 30 |
| Supply Planning | 6 | 6 | 6 |
| Maintenance | 15 | 15 | 15 |
| **Total** | **935** | **935** | **785** |

**No mismatch.** Other checks:
- The 148 existing Common Features task codes are exactly the scope map's Common Features b + c tasks (0 missing, 0 extra); their levels match (99 b = "route only", 49 c = "neither").
- Journal Categories is level b in General Ledger and Alternate Name Mapping Rules is level c in Receivables in the scope map, so both count toward those modules' Missing.
- The first 151 lines of the new index are the old rows unchanged (checked field by field) plus `screen_only`. Later, by your choice, their status `not started` was renamed to `open` (see Problems 1).
- No duplicate task codes; no HCM, Logistics or PLM rows; 936 lines, all CRLF.
- New rows: same 16 columns + `screen_only = unknown`; `level` written as "route only" (b) / "neither" (c) like the existing rows; `area` = the scope map's functional area; `status = open`; `ease`, `depends_on`, `pattern_group` empty (not ranked yet); `notes` = "added 2026-11-20 from Run 36 scope map; level b|c; routes declared: ...". Rows are sorted by task name within each module.

## 3. rebuild_index.py tests

**On the 12 real cards:** 12 found, 12 applied, no problems, exit 0. Common Features 10 tested, General Ledger 1, Receivables 1, every other module 0 (as expected). Total 12 of 935, 1.3% done. The only change it made to the index: `screen_only` went from `unknown` to `no` on those 12 rows (a tested card proves a route); every other field already matched the cards. A second run changed nothing.

**On a temporary copy** of gaps-filled in Claude's scratchpad (deleted afterwards):
- Round A, 3 bad cards + a junk `STATUS.md` inside `evidence\`: a `tested` card with no SKILL.md; a second card for `HZ_MANAGE_GEOGRAPHY_LOOKUPS`; a card with status `done`, no `route` key and module `Global HR`. Result: exit 1, 5 problems printed (no SKILL.md; missing key route; unknown status; module not in list; 2 cards for one code, neither applied). The evidence decoy was skipped. Good cards were still applied.
- Round B: a card with an unknown task code, a card in a non-module folder `hcm\`, and `screen-only.csv` files with 2 good rows, an unknown code, a code from another module and a code that has a card. Result: exit 1, 5 problems printed; the 2 good rows became `screen-only` (Payables: Open 38, Screen-only 2). After deleting the lists, a rerun set both rows back to open with a warning.
- CRLF was kept in `gap_index.csv` and `gap_progress.tsv` in every run.

## Problems found

1. **Status words differed.** The 138 untouched Common Features rows said `not started`; the 785 new rows say `open`. On your answer (2026-11-20) the 138 rows were renamed to `open`; nothing else in them changed. The index now has 923 `open` and 12 `tested` rows. The rebuild still counts an old `not started` value as Open, in case one comes back from the backup.
2. **Batch 1 evidence is not inside the module folder.** It is in `gaps-filled\evidence\batch-01\<task-folder>\`, and the batch reports point there. I did not move it; the README says new batches use `<module>\evidence\batch-NN\<task-folder>\`.
3. **The index has no columns for `waiting_minutes`, `route` or `test_records`** (the brief said same columns plus `screen_only`), so those stay on the cards only. The rebuild never overwrites the index `notes` column, so the long batch notes are kept.
4. **The old README rule 5 names (`ZZ_TEST_` or `FSCRT_`) never matched batch 1** (`GAPFILL_`). Now replaced by `GAPFILL_<INITIALS>_`.
5. **"Missing" in gap_progress.tsv is the number of index rows per module**, not a value read from FSCR; the script does not read FSCR. It equals module_counts.csv today.
6. **Index column is called `task_id`**, while the cards and the brief say `task_code`. Same values; I kept the column name.

## Could not verify

- **Value Sets and Transaction Calendars retest flag.** Part 3 says the "token-hang advice" was applied as wording after the fresh tests and not re-tested, and names the value-sets and calendar skills. But the Value Sets CHANGELOG puts the timeout advice in its live-test section (before its fresh test), and the Transaction Calendars `SKILL.md` contains no `timeout 120` text. I could not tell from the allowed sources whether either skill changed after its fresh test, so at first I did not add the retest line to them. **Your decision (2026-11-20): treat both as pending**, so both cards now have the line. Which wording changed after their fresh tests is still not confirmed.
- **Test record names for the 2 older skills** are not in the allowed sources (they may be in their SKILL.md worked examples or the run folders, which I was told not to use for facts).
- **Fresh-test minutes for Journal Categories (4)** come from the index; its note says "fix Run 26c = 4 min", so the index value may be the fix time, not a fresh-test time.
- **Screen-only status** of every task is still `unknown`; nothing was checked in Oracle.

## Cleanup

- Temporary test copy and the scratchpad helper scripts: deleted.
- No server, listener or background process was started for the work; the one slow background `find` used for the FSCR check finished on its own (exit 0). At the end no Python process was running and no stray `E:\e\` folder existed.
