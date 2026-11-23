# Run 05 ledger: FSCR breadth sample of 40 skills (read-only, ETIA-TEST)

Start 2026-11-03 09:40:15 +05:00.

## Setup
- **Working copy:** `fscr-work5`, a copy of the original repo.
- **Checks at start:** original repo and Run 03 verified unchanged; Run 04 hashed (`run04_hashes_start.md5`).
- **Usage at start** (`get_usage`): context 836,944 (84%); 5-hour 81%; weekly 40%. Context size, not billed tokens.
- **Sign-in:**
  - The token had 288 s left.
  - My first login call used an invalid flag ("fusion_login.py: error: unrecognized arguments: --force-login"), so nothing ran.
  - Re-ran your exact command in the background. Browser single sign-on completed with no password; the process exited.

## Sample (seed 20261103, `scripts/sample40.py`)
- **Population:** 1,123 skill files with a `type:` front matter (router excluded), 32 excluded as tested in Runs 01–04.
- **Stratified** ERP 10, SCM 10, HCM 12, CX 4, shared/core 4. Types proportional within each area, largest-remainder rounding.
- **No replacements made.**
- The type labels found are wider than the brief's four: e.g. verification, validation, assessment, export, support in shared. The quotas used the labels as they are.

## Grading (`scripts/analyze40.py`, rules fixed in its docstring before grading)
- **Detection fix after calibration:** fields are listed as backticked CamelCase column names in `ora-resource` tables, which my first detector missed. Re-graded. Evidence: `evidence/analysis40.json`.
- **Grades:**
  - 0 = 28
  - 1 = 7 (ERP 3, SCM 1, HCM 2, CX 1)
  - 3 = 5 (ERP 3, CX 1, shared 1)
  - 2 = 0
- **Ledger update after skills 1–40** (graded together by script).

## Routing (8 tasks, `evidence/routing8.txt`)
- **I followed the router text;** FSCR did not run anything.
- **All 8 reach the exact task skill.** 4 resolve one offering; 4 first stop for the user to choose among 2–6 offerings.
- **Modes:** 7 assisted, 1 hybrid.

## HCM checks
- **Declared routes across all HCM task files:** FSM 190, REST 75, HDL 22, ESS 1.
- **Dependency graph:** `knowledge/dependency-graphs/hcm-dependency-graph.json` (86 nodes, 281 edges). It contains 2 of the 8 sampled HCM task codes, both with **0 edges**, so it cannot order the sampled tasks.

## Exports
- 20 sampled tasks have catalog CSV export Y. Template + data exports started in the background at about 09:47 (`evidence/exports/export_all.log`).

## Midway usage (about 09:45, `get_usage`)
- Context 865,913 (87%); 5-hour 86%; weekly 41%. Context size, not billed tokens.

## End, 10:08:20 (28 min)
- **Exports:** 40 processes (IDs in `evidence/export_process_ids.txt`). One data download failed on DNS (inventory zones); its template was retrieved.
- **Field comparison:** `evidence/field_compare.json`; `ledger.csv` written for all 40 skills.
- **Checks:** Runs 01 to 04 and the original repo hash-identical. The `fscr-work5` copy is identical to the original repo (no export wrote an existing file). No Python process, nothing on port 8765.
- **Usage at end** (`get_usage`): context 868,988 (87%); 5-hour 87%; weekly 41%.
