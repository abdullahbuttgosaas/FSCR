# Batch 01 result: Supply Planning

Filled by IR · 24/11/2026 · test prefix `FSCRT_IR_GF_` (the pack's CLAUDE.md requires `FSCRT_<initials>_`, so it is
used instead of the prompt's `GAPFILL_IR_`)

## Time log

| Step | Start | Finish |
|---|---|---|
| Sign-in (waiting) | 20:33 | 20:35 |
| Gap list, skill drafts | 20:35 | 20:42 |
| Own live tests (export, load, read back) | 20:42 | 20:47 |
| Fresh tests and wording fixes (5 rounds) | 20:46 | 21:09 |
| Reports | 21:09 | 21:12 |

## Tasks

| Task | Status | Working min | Waiting min | Records (read back) | Import ProcessIds |
|---|---|---:|---:|---|---|
| ORA_DOS_MANAGE_SUPPLY_ORCHESTRATION_ATTACHMENT_CATEGORIES | tested | 32 | 11 | FSCRT_IR_GF_AC1, ACF, ACR, ACR3, ACR4, ACR5 | 100004742420025, 100004742420054, 100004742419063, (ACR2 failed: 100004742419086), 100004742420131, 100004742423164, 100004742421147 |
| ORA_MSC_MANAGE_PLANNING_PROFILE_OPTIONS | tested | 27 | 9 | FSCRT_IR_GF_PO1, POF, POR, POR2, POR3, POR4 | 100004742419023, 100004742421074, 100004742423051, 100004742422229, 100004742419116, 100004742422357 |
| ORA_VCS_MANAGE_PROCESS_DEFINTIONS | screen-only | 1 | 1 | none | none (FSCR refused the export: CSV flag N) |

Minutes are approximate: the fresh-test rounds for the two tasks ran in parallel, and waiting time includes Oracle
exports/imports run by the fresh testers.

## Problems and findings

- **Display names of attachment categories must be unique.** Retest ACR2 reused the skill's example display name and
  Oracle refused it (`FND_CORE_RCRD_VAL: A record with the value ... already exists`); 0 rows were created and the
  after-export showed nothing changed. The skill now builds the display name from the code and checks it first.
- **FSCR's task import reports `StatusCode: (unknown)` and `ResultCount: 0` even on success.** Only the process log
  and an after-export show the result; `scripts/import_result.py` reads the log safely.
- **FSCR's export and import scripts print file names that start with the environment name.** The skills send all
  script output to a log and read it only through grep and three helper scripts (`scripts/inspect_export.py`,
  `scripts/compare_exports.py`, `scripts/import_result.py`).
- **Git Bash:** REST paths need `MSYS_NO_PATHCONV=1`, which also stops path conversion of other arguments; the REST
  step therefore redirects output instead of using `--output`.
- **Windows path length:** the export ZIP name is long; deep run folders can pass the 260-character limit.
- My own `compare_exports.py` first printed PASS when nothing was added (found by retest ACR2); fixed to print FAIL.
- `rebuild_index.py`, `gap_index.csv`, `README.md` and the `common-features*/scripts` helpers of the gaps-filled pack
  are not in this pack, so the index could not be rebuilt. The STATUS.md key order follows the prompt.
- Evidence is UTF-8 text (`.txt`), not PNG: the pack's CLAUDE.md allows PNG images only from `make_images.py`.

## What is left

Nothing for CSV/API gaps of Supply Planning. Screen-only: 3 tasks (`screen-only.csv`). Skipped with reason: Collect
Planning Data (runs a collection into the shared planning repository).
