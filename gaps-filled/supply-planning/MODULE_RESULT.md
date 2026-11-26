# Module result: Supply Planning (gap fill)

Filled by IR · test prefix `FSCRT_IR_GF_` · 3 batches

## Cumulative counts (all sittings)

| Missing tasks (route only + neither) | Tested | Written (unsafe to test) | Failed | Screen-only | Left |
|---:|---:|---:|---:|---:|---:|
| 6 | 2 | 1 | 0 | 3 | 0 |

These counts match `MODULE_TRACKER.csv`: 2 tested, 1 written-untested, 3 screen-only, 0 open. Minutes over all sittings: about 64 working and 25 waiting.

## Batch 03 (25/11/2026, live test of Collect Planning Data, approved by IR)

- One POST: net change (type 2), source system GPR, entity UOM_CODES. Oracle refused it ("You must enter a value for the
  TemplateName attribute."), no job started, and a GET showed no new run. Working 6 min, waiting 2 min.
- Status stays **written**: a collection needs a template, templates live only on the Collect Planning Data page, and a
  predefined template would collect far more than the approved units-of-measure run.
- Next step: save a template holding only UOM_CODES on the Collect Planning Data page (or approve a predefined
  template), then POST once with `TemplateName` and run the fresh test.
- Cumulative counts are unchanged.

## Sitting 2 (24/11/2026, batch 02)

| Tested | Written (unsafe to test) | Failed | Screen-only | Left |
|---:|---:|---:|---:|---:|
| 0 | 1 | 0 | 0 | 0 |

| Task | Result | Working min | Waiting min |
|---|---|---:|---:|
| Collect Planning Data | written, unsafe to test: a REST `dataCollections` POST starts a collection into the shared planning data repository; the skill was written from read-only GET, describe and export checks plus Oracle's docs | 4 | 4 |
| **Total** | | **4** | **4** |

- Re-opened because batch 01 had skipped it without a skill. It is not screen-only: REST POST exists (VERIFIED).
- Failed tasks: none. Test records created: none (nothing loaded). ProcessIds: none.
- Left for the next sitting: nothing. No retest is pending; no known wrong sentence is left in a SKILL.md.
- Sign-in waiting: about 4 minutes (an expired sign-in made the first REST call hang until `timeout` stopped it).
- `rebuild_index.py` is still not in this pack, so the index step could not run.

---

## Sitting 1 (24/11/2026, batch 01)

### Counts (sitting 1)

| Missing tasks (route only + neither) | Tested | Failed | Screen-only | Skipped | Left |
|---:|---:|---:|---:|---:|---:|
| 6 | 2 | 0 | 3 | 1 | 0 |

### Per task

| Task | Result | Working min | Waiting min |
|---|---|---:|---:|
| Manage Supply Orchestration Attachment Categories | tested (fresh test ACR5 passed, no errors) | 32 | 11 |
| Manage Planning Profile Options | tested (fresh test POR4 passed, no errors) | 27 | 9 |
| Manage Supply Chain Collaboration Orchestration Process Definitions | screen-only (no CSV: FSCR refuses the export; no REST resource) | 1 | 1 |
| Manage Supply Chain Collaboration Messages | screen-only (no CSV, no REST resource; checked in the module test) | 0 | 0 |
| Configure Remaining Shelf Life Rule | screen-only (no CSV; REST is GET only; checked in the module test) | 0 | 0 |
| Collect Planning Data | skipped: runs a data collection into the shared planning repository that other people's plans use | 0 | 0 |
| **Total** | | **60** | **21** |

Minutes are approximate; the two tasks' fresh-test rounds ran in parallel. Sign-in waiting: 2 minutes.

### Failed tasks

None. (One fresh retest, ACR2, failed on a reused display name; the cause was proven from Oracle's error and the
after-export, the skill was fixed, and later retests passed.)

### Left for the next sitting

No CSV/API gap is left. No retest is pending and no known wrong sentence is left in either SKILL.md; tester
suggestions that are not errors are listed in each CHANGELOG.md.

### Test records created (all new; nothing existing was changed)

- Attachment categories: FSCRT_IR_GF_AC1, FSCRT_IR_GF_ACF, FSCRT_IR_GF_ACR, FSCRT_IR_GF_ACR3, FSCRT_IR_GF_ACR4,
  FSCRT_IR_GF_ACR5 (each read back: added 1, removed/changed 0).
- Planning profile options, each with 3 levels and a site value: FSCRT_IR_GF_PO1, FSCRT_IR_GF_POF, FSCRT_IR_GF_POR,
  FSCRT_IR_GF_POR2, FSCRT_IR_GF_POR3, FSCRT_IR_GF_POR4 (each read back: added 1 + 3 + 1, removed/changed 0).

### Notes

- `rebuild_index.py` and the gaps-filled pack's index files are not in this pack, so the index step could not run.
- Records use `FSCRT_IR_GF_` because the pack's CLAUDE.md requires `FSCRT_<initials>_`; evidence is `.txt` because
  CLAUDE.md allows PNG images only from `make_images.py`.
- Run folders (exports and logs with user names) are in a `gwsupply-planning` folder next to the pack, outside it.
