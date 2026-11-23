# CHANGELOG: manage-legal-authorities (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-24 (batch 3 part 3, AB with Claude)
- Read-only export: 21 files, 1 legal authority (7 files with rows).
- Live test: `GAPFILL_AB_P3_LA1` (site `GAPFILL_AB_P3_LA1_S1`), template rows from the existing authority with every internal id column cleared; 1 import (ProcessId 100004742406310): OrganizationParty 1 row, TaxAuthorityProfileVO 1 row, 0 failed. Export after + compare: 7 rows added, removed 0, changed 0: PASS. Oracle kept the given party and site numbers.
- Fresh test (task name + SKILL.md only): PASS, `GAPFILL_AB_P3_LA2F`, ProcessId 100004741410612, about 7 minutes; one export retry after a drop (allowed by the skill).
- Tester notes, **not applied**: check the ZIP exists before unzipping; describe what a dropped export looks like; template_row.py gives no warning for a --clear on an empty column; give a grep for the template's SiteUseType / ClassCategory / ClassCode; FirstPartyUsageName stays on the profile row (harmless).

## Test records created
- `GAPFILL_AB_P3_LA1`, `GAPFILL_AB_P3_LA2F` (organization parties, legal authority usage).
