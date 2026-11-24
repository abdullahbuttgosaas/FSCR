# CHANGELOG: manage-party-tax-profiles (GoSaaS gap fill, not official FSCR)

## 0.1.0 wording fix, 2026-11-24 (batch 4 fix, AB with Claude)
- Step 3: the flag sentence was wrong ("every other flag N"); now names `ReportingAuthorityFlag`, `CollectingAuthorityFlag` and `ProcessForApplicabilityFlag` as `Y` and lists the `N` flags. Also dropped the unclear words "a profile an earlier test made by the legal authority skill" (TPROF = first listed with PREFIX, else first listed).
- Fresh re-test (task name + SKILL.md only): PASS, `GAPFILL_AB_B4FIX_LA5R`: legal authority ProcessId 100004741428757, profile ProcessId 100004741429245, about 11 minutes, no retries. Checked again in the main session: the added profile row matches (3 flags `Y`).
- Tester notes, **not applied**: "first listed" may pick another run's test profile; the legal authority read-back is skipped (allowed); exports can take over 2 minutes (run them in the background); filtering template_row.py output.

## 0.1.0, 2026-11-24 (batch 4 part 3, AB with Claude)
- Read-only export: see `evidence/batch-04/ORA_ZX_MANAGE_PARTY_TAX_PROFILES/02_found.png`.
- Live test: Step 1 legal authority `GAPFILL_AB_P3_LA3` without profile (ProcessId 100004741425152, OrganizationParty 1 row, 0 failed); re-export showed no profile for it; profile import (ProcessId 100004741427305) TaxAuthorityProfileVO 1 row, 0 failed. Export compare (3 -> 4 profiles) PASS.
- Fresh test (task name + SKILL.md only): PASS, `GAPFILL_AB_P3_LA4F`: legal authority ProcessId 100004741428097, profile ProcessId 100004741428317, about 10 minutes, no retries. Checked again in the main session: the added profile row matches.
- Tester notes, **not applied** (tested wording stays on disk): Step 3 should just say "first listed with PREFIX"; Step 3's "every other flag N" is wrong (ProcessForApplicabilityFlag is Y too); Step 1 should name the legal authority template rule; say whether to keep the ZX key in Step 1's builder line (keeping it did no harm); the two skills' log one-liners differ.

## Test records created
- GAPFILL_AB_P3_LA3 profile (live; legal authority GAPFILL_AB_P3_LA3 made without a profile as Step 1); GAPFILL_AB_P3_LA4F profile (fresh test; legal authority GAPFILL_AB_P3_LA4F, site GAPFILL_AB_P3_LA4F_S1); GAPFILL_AB_B4FIX_LA5R profile (fresh re-test; legal authority GAPFILL_AB_B4FIX_LA5R); tax authority profiles on test legal authorities.
