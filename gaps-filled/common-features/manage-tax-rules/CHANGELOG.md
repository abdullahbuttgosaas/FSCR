# CHANGELOG: manage-tax-rules (GoSaaS gap fill, not official FSCR)

## 0.0.1, 2026-11-24 (batch 3 part 2, AB with Claude): FAILED
- Read-only exports: 15 files (the same files as the condition sets package), 1 existing rule (an applicability rule owned by a business unit). A second rules export was taken after the new condition set `GAPFILL_AB_P2_CS1` existed.
- Rows: rule header + translation + one rule result, template rows from the existing rule (`template_row.py`), rule **disabled** (`EnabledFlag=N`), on test tax `GAPFILL_AB_P1_TX1`, factor set `GAPFILL_AB_FS1`, condition set `GAPFILL_AB_P2_CS1`, result `NOT_APPLICABLE`; the internal geography ID (`NumericValue1`) left empty.
- Attempt 1 (ProcessId 100004741398794): rule from 2026/01/01, owner GCO: `ZX_RECRATE_DATE_INVALID: Enter a date range that's within the date range of the parent tax of {TAX_START_DATE} to {TAX_END_DATE}.` (placeholders not filled: the tax was not found). Result row failed with it.
- Attempt 2 (ProcessId 100004741399835): rule from 2026/02/01: same error.
- Attempt 3 (ProcessId 100004742403274): owner `OU`, `BuName` = the test business unit that subscribes `GAPFILL_AB_TR1` since batch 3 part 1: same error. Stopped at the 3-attempt limit.
- Rules export after attempt 3: all 15 files unchanged (nothing created).
- Not tried (changes real setup, needs a person): a GCO subscription of the test regime, or a rule on a live tax. No fresh test.

## Test records created
None. `GAPFILL_AB_P2_RL1` was tried 3 times and does not exist.
