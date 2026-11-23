### Initializer findings

| Finding | Status |
|---|---|
| **The dry run now passes** (exit code 0). Run 11b stopped at `Identified task mapping must contain a non-empty tasks array.`; this run supplied 728 rows. | V |
| `--dry-run` writes nothing. `project/` still holds only `README.md`, `_template` and `draft-impl-project-20261028`. It would create `project/twelve-sow-50513scm-oracle-cloud-scm`. | V |
| The initializer validates task **names only** (exact name against `effective/setupTasksAll.json`): 728/728 matched. It does **not** check offering, functional area or `Resolver Sequence`. | V (code read: `validate_identified_task_mapping`) |
| `Resolver Sequence` is checked only later, by `create_project_runbook.py` (unique positive integers). That step was not run: dry-run stops before it, and the SKILL.md says it runs after initialization. | V (code read) |
| SKILL.md gate: "before writing the mapping, read the persisted `setup_task_sequence`". The resolver could not produce one (no script, needs FSM/BOSS), so under the skill's own written gate this mapping **should not be used for a Run Book plan**. The script does not enforce that gate. | V (SKILL.md text) |
| Rows with no FSCR task skill (431) would route to `shared/common/manual-tasks` (FSCR task-context policy). | V (FSCR code output) |
| Runtime: FSCR's skill-path resolution took 11 min 4 s for 728 tasks (it re-reads the catalog and globs `pillars/**` for every task). | V (timed) |
