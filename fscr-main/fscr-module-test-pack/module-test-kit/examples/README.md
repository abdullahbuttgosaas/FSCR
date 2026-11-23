# Examples: three finished module tests

Read these before your first run. Each folder has only:
- `RESULT.md`: the run report (copied from the run, with run-folder paths removed)
- `tracker_row.md`: the final values as published in the tracker, in the kit format (owner and tester names left out)
- `images/`: the table images from that run

| Module | Run | Plan | Runbook | Execution | Fit |
|---|---|---:|---:|---:|---|
| Common Features (ERP) | 30 | 4 | 4 | 4 | High |
| Procurement (SCM) | 33 | 3 | 3 | 3 | Medium |
| Sourcing and Supplier Management (SCM) | 34 | 3 | 3 | 3 | Medium |

Notes:
- These runs came before this kit. They used up to 5 images and older task counts (from the coverage runs before the
  scope map). A new run uses the scope map counts and makes exactly the 4 images `make_images.py` builds.
- The scores in `tracker_row.md` are the published values. Where a RESULT.md proposed a different score, the published
  value was decided after review.
- The Common Features `03_runbook.png` checks owner and validation fields. Later runs dropped those criteria (see
  PLAYBOOK lessons), so do not copy that part.
