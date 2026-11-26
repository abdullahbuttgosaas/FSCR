# CHANGELOG - Manage Time Unit Mappings (ORA_OKC_MANAGE_TIME_UNIT_MAPPINGS)

## 2026-11-26 (sitting 1, batch 02)
- Skill written from the live export and Oracle errors; own test: Prerequisite: unit ZK1 / FSCRT_AK_GF_U1 created by REST POST after two 400 refusals (UOMClassCode not accepted; then "BaseUomFlag is required"), each confirmed by GET as not created. Mapping FSCRT_AK_GF_TU1: export 100004744431254, import 100004743456567 (1 row, 0 failed), after-export 100004744432864: 1 new row, 0 existing changed. Safe way chosen: mapping an existing unit would change other contracts, so own unit first.
- Fresh test F: Unit ZKF / FSCRT_AK_GF_UF by REST (201); mapping FSCRT_AK_GF_TUF: export 100004744434635, import 100004744433739, after-export 100004744436295: 1 new row, 0 changed. PASS, no wrong sentence.
- Tester F suggestions (not applied): check the unit name is unused before the POST; say UOMClass is a numeric value; mention the .txt next to the ZIP.
- rest_write.py added to common-features: FSCR REST client prints Oracle gzipped error bodies unreadable; the wrapper reuses FSCR unchanged and only unzips the error.
