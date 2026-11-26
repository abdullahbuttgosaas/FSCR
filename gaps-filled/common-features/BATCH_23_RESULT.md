# Batch 23 result: Common Features (AB), guided journeys, publish account hierarchies, resource teams, messages

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (tenth Common Features sitting, second batch). No test record was created in this batch (every create try was refused; the other tasks were not loadable or unsafe). Work folder outside the repo.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 23:08 | 23:12 | 4 | Guided journeys: describe, list, 4 REST tries (all refused, nothing created) |
| 23:12 | 23:13 | 1 | Publish account hierarchies: export read (trees package), 4 REST names |
| 23:13 | 23:16 | 3 | Resource teams: Import Management activities, object list (433), one activity refused |
| 23:16 | 23:24 | 8 | Messages: Oracle docs (file format, process), valueSets describe, scheduler REST check |
| 23:24 | 23:30 | 6 | Skills (3), cards, screen-only.csv, evidence |

## Results
| # | Task | Status | Working min | Waiting min | Proof |
|---|---|---|---:|---:|---|
| 1 | Guided Journeys | screen-only | 8 | 2 | REST journeys refuses the guided category on create and on duplicate of a working guided journey |
| 2 | Publish Account Hierarchies | written (unsafe) | 6 | 3 | export = trees package, no publish column; publish writes the shared balances cube, no unpublish |
| 3 | Manage Resource Teams | screen-only | 7 | 4 | no Import Management object (433 listed); ObjectCode ResourceTeam refused |
| 4 | Manage Messages | **failed** | 8 | 2 | file route found; process job path not published or readable |
| 5 | Manage Applications Core Messages | **failed** | 3 | 1 | same as Manage Messages |
| | **Total** | **2 screen-only, 1 written, 2 failed** | **32** | **12** | |

## Problems and findings
1. **Guided journeys:** REST `journeys` (hcm) has create and duplicateJourney, but create defaults the level to personal ("Level cannot be set") and refuses category `ORA_GUIDED`; the round trip (duplicateJourney action on an existing guided journey) gives the same refusal. Proven screen-only for REST; HCM Data Loader was not tried (not a CSV/REST setup route).
2. **Resource teams:** Oracle documents a Resource Team import object, but this release's Import Management lists 433 objects and none is a resource team (only queue-team links). Screen-only with proof.
3. **Publish account hierarchies:** the task's FSM package is the trees package (already covered by manage-trees-and-tree-versions); the publish itself is a scheduled process into the shared balances cube. Written unsafe.
4. **Messages (both tasks):** Oracle's docs give a real route (pipe-delimited MESSAGES file + scheduled process Upload Comma-Separated Values File for Import Process, file type MESSAGES). It could not be run by script: the job package and definition are not published, the `valueSets` REST resource the docs point to has no upload action, and the scheduler REST API returns empty job names. **Failed with next step:** AB reads the job name once on the Scheduled Processes page (or MOS 2174930.1); then the skill's Steps 3 to 5 run with a prefix message.
5. A scheduler REST read returned a link with the server address into a work-folder file (outside the repo, not copied anywhere).

## What is left
See `MODULE_RESULT.md`.
