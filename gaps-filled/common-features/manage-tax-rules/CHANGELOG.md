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

## 0.2.0, 2026-11-24 (batch taxfix, AB with Claude): TESTED
- Old process log read again by ProcessId (100004742403274): row `GAPFILL_AB_TR1, GAPFILL_AB_P1_TX1, <BU id>, DET_APPLICABLE_TAXES, 2026-02-01, , GAPFILL_AB_P2_RL1, 10`, `ZX_RECRATE_DATE_INVALID` with empty placeholders: the tax was not found by the rule's tax lookup.
- Real cause (field-by-field compare with the working setup): the test regime had no global configuration owner option row (`ORA_ZX_BU_GCO_TAX_SUB.csv`). The tax rows differ only in option flags.
- After manage-tax-regimes Step 7: same rows (disabled GCO applicability rule, `EnterpriseId` empty like every GCO row) imported first try as `GAPFILL_AB_TF_RL1` (ProcessId 100004742410090). Export compare: header, translation and result added, nothing changed; Oracle filled `NumericValue1` itself.
- SKILL.md rewritten as a full recipe with the prerequisite check (taxes export: tax + GCO row).
- Fresh test (15:12-15:18): PASS. `GAPFILL_AB_TF_RL2F` on tax `GAPFILL_AB_TF_TX2` (regime with GCO row only), condition set `GAPFILL_AB_P2_CS2F` (STATE = CA), ProcessId 100004741413821, compare PASS, EnabledFlag N. Notes NOT applied (keep tested wording): quote codes with spaces; 15 files include the XML; `--set Operator1Code==` looks odd but works.

## Test records created (batch taxfix)
`GAPFILL_AB_TF_RL1` (live), `GAPFILL_AB_TF_RL2F` (fresh test). Both **disabled**.
