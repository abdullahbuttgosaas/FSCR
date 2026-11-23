# Big and ignored files (not in git)

Files that are not in git but are not secrets: anything over 50 MB, and what `.gitignore` leaves out. Secrets are never listed here by content (only that they exist, in CONTEXT.md).

## Format (one line per file or folder)

| Name | Path | Machine(s) | Size | Date | What it is | Made by (run/task) | How to get it back |
|---|---|---|---|---|---|---|---|

## Files over 50 MB

None on 2026-11-23 (the biggest file in the folder is 32.1 MB, the git pack of `fscr-official-clone`).

## Ignored on purpose (baseline, 2026-11-23)

| Name | Path | Machine(s) | Size | Date | What it is | Made by (run/task) | How to get it back |
|---|---|---|---|---|---|---|---|
| Oracle FSCR clone | `fscr-official-clone\` | PC, laptop (zip) | 104.6 MB, 6,115 files | 2026-11-17 | official repo, git clone | Abdullah | `git clone https://github.com/oracle/fscr.git` then `git checkout 2801695` |
| Baseline FSCR copy | `fscr-main\fscr-main\` | PC, laptop (zip) | 71.4 MB, 6,120 files | 2026-10-28 | Oracle repo + our project `draft-impl-project-20261028` + 2 edits | runs 1–22 base | clone as above; apply `_patches\`; its `project\` folder also exists in every run copy |
| Run FSCR copies | `fscr-main\_fscr_run_*\fscr-work*\`, `…\fscr-main\`, `…\repo\` (except `project\` and `evidence\`, which are tracked) | PC, laptop (zip) | about 70.9 MB each, 22 copies + run 24 partial (14.9 MB) | 2026-10-28 to 2026-11-15 | Oracle repo copy used by the run | each run | clone as above + `_patches\` |
| Run 25 auth copy | `fscr-main\_fscr_run_25_fill_no_route\work\auth\` | PC, laptop (zip) | 0.1 MB | 2026-11-15 | copy of Oracle `core\auth` (+ a filled fusionEnv.properties, secret) | run 25 | from the Oracle clone `core\auth` |
| Test pack, Oracle part | `fscr-main\fscr-module-test-pack\` (all but the kit files) | PC, laptop (zip) | about 71 MB | 2026-11-17 | Oracle repo inside the pack | run 38 | clone as above; the full pack is `fscr-main\fscr-module-test-pack_v3.zip` (tracked) |
| Old pack zips | `fscr-main\fscr-module-test-pack.zip`, `fscr-main\fscr-module-test-pack_v2.zip` | PC, laptop (zip) | 24.6 MB, 26.7 MB | 2026-11-17 | superseded pack versions (v3 is tracked) | run 38 | rebuild from the pack folder; or Drive/USB |
| Page logs and cache | `Configuration Automation\page\_work\logs\`, `cache\`, `repair_snapshots\`, `matrix\logs\`, `redesign\demo\work\logs\` | PC, laptop (zip) | about 7.6 MB, 535 files | to 2026-11-02 | debug logs of the page tool | Configuration Automation | not needed; made again by running the page |
| Backups | `*.before`, `*.before_signin_change`, `gaps-filled\gap_index_backup_2026-11-20.csv` | PC, laptop (zip) | 0.6 MB | | old copies before an edit | | Drive/USB if ever needed |
| Python caches | `__pycache__\` | both | 6.2 MB | | compiled Python | | made again automatically |
| Sign-in transcripts | `fscr-main\_fscr_run_17_change_impact_discovery\evidence\signin_try3.raw`, `_try4.raw`, `_try5.raw`; `fscr-main\_fscr_run_20_cross_module_subject\evidence\signin.raw` | PC, laptop (zip) | under 1 KB each | 2026-11-09 | raw sign-in output; held back to be safe (may show sign-in addresses) | runs 17, 20 | Drive/USB if needed |
