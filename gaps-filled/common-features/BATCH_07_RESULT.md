# Batch 07 result: Common Features (AB), trees and tree labels

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (second Common Features sitting). Tested on one test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file was edited. Work folder outside the repo. Record names `GAPFILL_AB_B7_<name>`; no existing record was edited or deleted.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 03:03 | 03:09 | 6 | Planning exports of the open gaps; sign-in (4 s) |
| 03:07 | 03:15 | 8 | Labels (AHL, TL) and trees (TR): exports, builds, live tests |
| 03:15 | 03:32 | 17 | Tree structures (3 tries), test value set, account hierarchy live test |
| 03:32 | 03:45 | 13 | Skills tidied; fresh tests AHL, TL, TR, AH (waiting) |
| 03:48 | 03:55 | 7 | AHL re-test, TS fresh test (waiting); sign-in 03:50 (3 s) |
| 03:55 | 04:00 | 5 | Cards, evidence, tracker, reports |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records / ProcessIds |
|---|---|---|---:|---:|---|---|
| 1 | Manage Account Hierarchy Labels (`ORA_GL_MANAGE_ACCOUNT_HIERARCHY_LABELS`) | tested | 4 + 6 | 3 | PASS (re-test after a wording fix) | `GAPFILL_AB_B7_AHL1` (100004743403129); fresh `AHL2F` (100004743403403); re-test `AHL3R` (100004743404147) |
| 2 | Manage Tree Labels (`FND_MANAGE_TREE_LABELS`) | tested | 3 + 4 | 2 | PASS | `GAPFILL_AB_B7_TL1` (100004742423488); fresh `TL2F` (100004743403630) |
| 3 | Manage Trees and Tree Versions (`FND_MANAGE_TREES_AND_TREE_VERSIONS`) | tested | 6 + 5 | 4 | PASS | `GAPFILL_AB_B7_TR1` (100004742423501); fresh `TR2F` (100004743403418) |
| 4 | Manage Account Hierarchies (`GL_MANAGE_ACCOUNT_HIERARCHIES`) | tested | 5 + 6 | 5 | PASS | value set `GAPFILL_AB_B7_AHVS` (100004742423615); `GAPFILL_AB_B7_AH1` (100004742421559); fresh `AH2F` (100004743402217) |
| 5 | Manage Tree Structures (`FND_MANAGE_TREE_STRUCTURES`) | tested (try 3) | 6 + 6 | 5 | PASS | `GAPFILL_AB_B7_TS1` (refused 100004742421534; 100004742441558); `TS2` (100004742423588); fresh `TS3F` (100004743404182) |
| | **Total** | **5 tested** | **51** | **19** | 5 of 5 | |

## Problems and findings
1. **Tree structure needs `NumberOfTrees` and `RestrictByDate`** (try 1: JBO-27014, nothing created).
2. **A self relationship row replaces the root relationship row** (try 2: structure created, but the relationship file kept only the self row). The skill sends the root row only. `GAPFILL_AB_B7_TS1` stays as a DRAFT structure; nothing uses it.
3. **Account hierarchy labels: export row counts change** because GAPFILL structures show up in later exports. The fresh tester found the fixed count sentence wrong; wording changed to "at least", re-test `AHL3R` PASS.
4. **REST:** `fndTreeStructures` 404; `fndTrees` with `q` on two columns joined by `and` returns 0 rows (one column works). Ids are read with finders: `fndLabels` TreeStructureCodeRowFinder, `fndTreeVersions` AllVersionsRowFinder, `fndTreeNodes` TSCodeAndTCodeRowFinder, `fndTreeDataSourceParams` TreeDataSourceParamsRowFinder.
5. **New helper** `manage-trees-and-tree-versions/scripts/tree_rows.py` builds tree, parameter, version and node rows from a template tree read live by REST; account hierarchies reuse it.
6. Trees and hierarchies are left in DRAFT (not audited, activated or published).

## What is left
See BATCH_08_RESULT.md.
