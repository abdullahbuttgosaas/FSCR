# Procurement batch 02: result (2026-11-25, AB with Claude)

## Continuation after the spend-limit reset (same day): batch 02 finished
| Task | Status | Write / test / wait min | Test (ProcessIds) |
|---|---|---|---|
| Manage Purchasing Profile Options | **tested** | 4 / 2 / 2 | fresh PO2F, PO3R, PO4R (100004744396141): PASS |
| Specify Contract Clause Import XML File Location | **tested** | 6 / 6 / 4 | test-and-restore. Own: 100004744391334 / 100004744391355. Fresh: 100004744396393 / 100004744395169, SAME: PASS |
| Manage Collaboration Messaging Configuration | **tested** | 6 / 7 / 5 | test-and-restore. Own: 100004744393468 / 100004744394251. Fresh F: 100004743407969 / 100004744391850 (one wrong sentence, fixed). Re-test R: 100004744396452 / 100004744393644, compare PASS |
| Manage Channel Settings | **tested** | 6 / 7 / 5 | test-and-restore. Own: 100004744393512 / 100004744394843. Fresh: 100004744395141 / 100004744395154, compare PASS |
| Configure Electronic Signature for Procurement Documents | **written (unsafe to test)** | 5 / 1 / 1 | export only (0 rows); a load needs DocuSign / Adobe Sign credentials an agent must not enter |

Notes:
- Test-and-restore only for the 3 shared settings: every test value was put back and proved equal to the first export / REST read.
- The XML location option did have a site value (`/usr/tmp/`); the earlier note below ("0 rows, no old value") was wrong: REST is the source.
- `build_csv_package.py --edit-row` now takes a two-column key (`Col=v&Col2=v2`) for channel setting values.
- Network drops: several exports gave no ZIP and were re-run into new folders; two imports dropped after the ProcessId and their logs were fetched by ProcessId (never re-imported).

---

## First part (stopped early)

Planned: Purchasing Profile Options, Specify Contract Clause Import XML File Location, Collaboration Messaging Configuration, Channel Settings, Electronic Signature. **Only 1 task was done** before the sitting stopped: the org reached its monthly Claude spend limit (fresh testers stopped at about 17:30; resets 2026-11-28 20:00 PKT). No fresh test can run until then, so no more loads were started.

## Time log
| Step | Start | Finish | Minutes |
|---|---|---|---|
| Purchasing profile option: build, import, REST read-back | 17:26 | 17:30 | 4 |
| Skill written | 17:35 | 17:39 | 4 |

## Tasks
| Task | Status | Write / test / wait min | Test records (ProcessId) |
|---|---|---|---|
| PO_MANAGE_PURCHASING_PROFILE_OPTIONS, Manage Purchasing Profile Options | written (fresh test pending) | 4 / 2 / 2 | GAPFILL_AB_B2_PO1 (100004743407091): 5 rows, 0 failed; REST profileOptions PASS |

## Findings from the read-only exports (for the next sitting)
- **Clause import XML file location** (`OKC_CLAUSE_IMP_FILE_LOCATION`): the export has 0 rows (no value set anywhere). A site value would be new, but there is no "old value" to restore by CSV. Next: check its levels by REST. Try a USER-level value if that level is enabled, or a new option as in PO1.
- **Collaboration Messaging Configuration:** 3 files. One parameter row (key `MsgParamId`), 7 business-process enable rows, 21 parameter-data rows. All are existing rows: a test must be test-and-restore (export first, change one value, restore it, compare).
- **Channel Settings:** 26 settings, 5 values per business unit. Some settings cannot be changed after saving (for example the calendar). Next: pick a changeable setting and decide new value row vs test-and-restore.
- **Electronic Signature:** `ORA_ZCA_ESIGNATURE_SETUP` (0 rows) holds a DocuSign / Adobe Sign account (user, password, API key, tokens). A load needs real provider credentials, which an agent must not enter. Next sitting: write the skill and mark it written with that reason (it is not screen-only).

## What is left
- Fresh test of PO1's skill with a new name (GAPFILL_AB_B2_PO2F).
- The 4 other batch 02 tasks, then batches 03+ (see `my_gaps.csv`).
