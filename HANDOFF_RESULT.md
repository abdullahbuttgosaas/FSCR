# Handoff result: git setup of the FSCR work folder

2026-11-23, PC `DESKTOP-TJ1S90V`. Repo: `E:\GoSaaS\Configuration Automation v2.1`, branch `main`, remote `origin` = https://github.com/abdullahbuttgosaas/FSCR.git

| Time log | |
|---|---|
| Start | 2026-11-23 16:30 (+05:00) |
| Finish | 2026-11-23 16:50 (+05:00) |
| Minutes | about 20 |

## Result in one look

| Item | Result |
|---|---|
| Baseline commit | `83eff8a` "Baseline: FSCR work folder (gaps-filled, runs 1-38 reports/results/evidence, kit, context notes)" |
| Tracked files | **5,261 files, 194,989,931 bytes (186.0 MB)**; git stores it as about 69 MB compressed |
| Push to GitHub | **NOT DONE.** The push was blocked by this session's safety check (sending the folder to an outside service). The commits are only on the PC. Run the push yourself (see "What to do"). |
| Remote state | `origin` was **empty** (no branch, no README "first commit"), so there was nothing to merge. |
| Clone check | Cloned the local repo into `E:\GoSaaS\_clone_check`: **5,261 / 5,261 files present, 0 SHA-256 differences**; `python rebuild_index.py` in the clone: **935 rows, 12 tested, "No problems"**, and its output was byte-identical to the committed files. Folder deleted afterwards. (Checked from the local repo, not from GitHub, because the push did not happen.) |
| Long paths | Windows `LongPathsEnabled` = **1 (on)**. `core.longpaths true` set locally and globally. **138 tracked paths are over 240 characters** (longest 307 here, 290 in the clone); all added, committed, cloned and hash-checked fine. The other ~5,960 long paths are inside the ignored Oracle copies. |
| Git config (local + global) | `core.longpaths true`, `core.autocrlf false` (global was `true` before), `core.safecrlf false`. `.gitattributes`: `* -text`. |
| Secrets | none staged (checked by name and by content; see below) |
| Files over 50 MB | none (largest tracked: `fscr-main\fscr-module-test-pack_v3.zip`, 26.7 MB) |

## Tracked vs ignored, per class (classes from `E:\GoSaaS\FSCR_INVENTORY\INVENTORY.md`)

| Class | Tracked | Ignored | Why |
|---|---|---|---|
| A small and important | 3,991 files, 62.0 MB | 30 files in `fscr-main\fscr-main\project\` (its copy exists in every run copy's `project\`, which is tracked); 44 edited Oracle files inside copies (the fix is kept once in `_patches\`; `env.properties` only has a run ID); 4 `signin*.raw` sign-in transcripts (held back to be safe) | your rules |
| B big but meaningful | 1,256 files, 123.8 MB (zips, exports, hash lists, big evidence JSON, `Configuration Automation\page\_work` builds and screenshots) | none | track B unless over 50 MB |
| C Oracle FSCR | 0 | 146,133 files, 1,751 MB: `fscr-official-clone\`, `fscr-main\fscr-main\`, the Oracle part of the test pack, the repo copy in each run folder (its `project\` and `evidence\` are tracked; Oracle's own `project\README.md` and `project\_template\` are not) | download again: clone oracle/fscr at 2801695 (how-to in `.gitignore` and `_patches\README.md`) |
| D secrets | 0 | 28 files: `fscr-signin-values.txt`, `Configuration Automation\.env`, `Configuration Automation\.session\state.json`, 25 filled `fusionEnv.properties` | never sync; templates tracked: `fscr-signin-values.txt.example`, `Configuration Automation\.env.example` (already existed), `Configuration Automation\.session\state.json.example`, `_patches\fusionEnv.properties.example` |
| E junk | 0 | 642 files, 65.7 MB: 2 old pack zips, page logs/cache/snapshots, `__pycache__`, `.before*` backups, `gap_index_backup_2026-11-20.csv`, `.setup_ok` | not needed |

New files added by this setup (only new files; no existing file was edited, moved or deleted): `.gitignore`, `.gitattributes`, `README.md`, `CONTEXT.md`, `SYNC_RULES.md`, `CHANGELOG.md`, `BIG_FILES.md`, `LAPTOP_SETUP.md`, `HANDOFF_RESULT.md`, `fscr-signin-values.txt.example`, `Configuration Automation\.session\state.json.example`, `_patches\README.md`, `_patches\payment_terms_fsm_package.py`, `_patches\payment_terms_fsm_package.py.patch`, `_patches\fusionEnv.properties.example`.

## Problems and notes

1. **Push not done** (blocked by the session's safety check, not by GitHub). Nothing was sent to GitHub. Git Credential Manager already has a GitHub sign-in on this PC (`git ls-remote` worked without asking), so the push should not ask you to log in.
2. **`Configuration Automation\.gitignore`** (that project's own file) hides `_work\`, `*.zip` and `.session\` inside that folder. The 565 class B files in `Configuration Automation\page\_work\` and `state.json.example` were added with `git add -f`; they stay tracked, but **new** files there need `git add -f` (written in CONTEXT.md section 13).
3. `fusionEnv.properties.example` is in `_patches\`, not next to each `fusionEnv.properties`, because every real one sits inside an ignored Oracle copy.
4. Correction to the inventory: Run 37 **is** mentioned in `gaps-filled\GAPS_PLAN.md` (37, 37b, 37c on 2026-11-18, work folder `E:\GoSaaS\gw\r37`, outside the repo). Run 31 is still not found. The STATUS cards mention runs 26a/26c and 27a/27c, which have no folders here (unconfirmed).
5. The global `core.autocrlf` changed from `true` to `false` on this PC, as asked; this affects other repos on this PC too.

## Secret check of the staged files

- By name: no `fscr-signin-values.txt`, `.env`, `state.json`, `fusionEnv.properties`, key or token-cache file staged.
- By content (password, secret, client_secret, BEGIN PRIVATE KEY): **0 private keys; 0 lines with a value-looking assignment.** 202 lines in 142 files mention the words in plain text or code (reports, prompts, sign-in instructions, scripts that read FSCR's token cache). Binary files (xlsx, zip, png, pdf) were not searched inside. File and line numbers only:

- `.gitignore` : 4, 10
- `BIG_FILES.md` : 3, 21
- `CHANGELOG.md` : 5
- `CONTEXT.md` : 21, 24, 193, 215, 218, 219
- `Configuration Automation/.env.example` : 4
- `Configuration Automation/.gitignore` : 1
- `Configuration Automation/CLAUDE.md` : 921
- `Configuration Automation/Lookup types/package-route/script3.py` : 12
- `Configuration Automation/README.md` : 17, 23, 50
- `Configuration Automation/SHARING.md` : 7, 8
- `Configuration Automation/_frozen/customers_v1/CLAUDE.md` : 499
- `Configuration Automation/_frozen/customers_v1/common/check_setup.py` : 1, 100, 157
- `Configuration Automation/_frozen/customers_v1/common/claude_tool.py` : 3, 4, 501
- `Configuration Automation/_frozen/customers_v1/common/oracle.py` : 124, 125, 129
- `Configuration Automation/_frozen/customers_v1/common/session_check.py` : 44
- `Configuration Automation/_frozen/customers_v1/page/oracle_today.py` : 5
- `Configuration Automation/_frozen/customers_v1/page/server.py` : 654, 724
- `Configuration Automation/_frozen/customers_v2/CLAUDE.md` : 800
- `Configuration Automation/_frozen/customers_v2/common/check_setup.py` : 1, 100, 157
- `Configuration Automation/_frozen/customers_v2/common/claude_tool.py` : 3, 4, 501
- `Configuration Automation/_frozen/customers_v2/common/oracle.py` : 124, 125, 129
- `Configuration Automation/_frozen/customers_v2/common/session_check.py` : 44
- `Configuration Automation/_frozen/customers_v2/page/oracle_today.py` : 5
- `Configuration Automation/_frozen/customers_v2/page/server.py` : 819, 898
- `Configuration Automation/common/check_setup.py` : 1, 100, 157
- `Configuration Automation/common/claude_tool.py` : 3, 4, 501
- `Configuration Automation/common/oracle.py` : 124, 125, 129
- `Configuration Automation/common/session_check.py` : 44
- `Configuration Automation/page/_work/briefing/PRESENTER_BRIEFING.md` : 248, 395
- `Configuration Automation/page/_work/look/fail_signin.txt` : 4, 5
- `Configuration Automation/page/_work/matrix/repair_snapshots/3be82ecaa2_1/Lookup types/package-route/script3.py` : 12
- `Configuration Automation/page/_work/matrix/repair_snapshots/9f2439c756_2r/Lookup types/package-route/script3.py` : 12
- `Configuration Automation/page/oracle_today.py` : 5
- `Configuration Automation/page/server.py` : 829, 908
- `LAPTOP_SETUP.md` : 32
- `README.md` : 4
- `SYNC_RULES.md` : 10
- `_fscr_run_38_cold_test/REPORT.md` : 9
- `_patches/README.md` : 11
- `fscr-access-requirements.md` : 24, 25, 71
- `fscr-main/FSCR_Creation_Tokens_calls.csv` : 251, 410
- `fscr-main/FSCR_Full_Context.md` : 525
- `fscr-main/_fscr_evidence_pack/gap_fills/run_28_token_estimate/RUN_REPORT.md` : 3
- `fscr-main/_fscr_run_01/RUN_REPORT.md` : 43
- `fscr-main/_fscr_run_01/evidence/corrections_backup/RUN_REPORT.md` : 40
- `fscr-main/_fscr_run_01/evidence/corrections_backup/ledger.md` : 61
- `fscr-main/_fscr_run_01/fscr-work/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_01/fscr-work/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_01/fscr-work/project/fscrt-run01-om-setup/README.md` : 15
- `fscr-main/_fscr_run_01/ledger.md` : 61
- `fscr-main/_fscr_run_02_understand/fscr-work2/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_02_understand/fscr-work2/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_02_understand/fscr-work2/project/fscrt-run01-om-setup/README.md` : 15
- `fscr-main/_fscr_run_03_change/RUN_REPORT.md` : 189
- `fscr-main/_fscr_run_03_change/evidence/corrections_backup/RUN_REPORT.md` : 166
- `fscr-main/_fscr_run_03_change/evidence/part4/ledger_part4_append.md` : 6
- `fscr-main/_fscr_run_03_change/fscr-work3/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_03_change/fscr-work3/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_03_change/fscr-work3/project/fscrt-run01-om-setup/README.md` : 15
- `fscr-main/_fscr_run_03_change/ledger.md` : 210
- `fscr-main/_fscr_run_04_create16/fscr-work4/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_04_create16/fscr-work4/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_04_create16/fscr-work4/project/fscrt-run01-om-setup/README.md` : 15
- `fscr-main/_fscr_run_04_create16/fscr-work4/project/fscrt-run04-create16/README.md` : 15
- `fscr-main/_fscr_run_04_create16/patches/remit-to/fsm_task_adapter.py` : 1772
- `fscr-main/_fscr_run_05_breadth/fscr-work5/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_05_breadth/fscr-work5/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_05_breadth/ledger.md` : 12
- `fscr-main/_fscr_run_06_requirements/fscr-work6/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_06_requirements/fscr-work6/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_06_requirements/fscr-work6/project/fscrt-run04-create16/README.md` : 15
- `fscr-main/_fscr_run_08_compare/RUN_REPORT.md` : 174
- `fscr-main/_fscr_run_08_compare/fscr-work8/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_08_compare/fscr-work8/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_09_impact/RUN_REPORT.md` : 118
- `fscr-main/_fscr_run_09_impact/fscr-work9/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_09_impact/fscr-work9/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_10_drive_reference/downloads/01_checklists_capture.txt` : 15
- `fscr-main/_fscr_run_11_project_intake/fscr-main/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_11_project_intake/fscr-main/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_11b_project_intake/repo/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_11b_project_intake/repo/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_12_project_planning/repo/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_12_project_planning/repo/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_14_part2_intake/fscr-main/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_14_part2_intake/fscr-main/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_15_part2_planning/fscr-main/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_15_part2_planning/fscr-main/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_16_sow_only_wave_plan/fscr-main/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_16_sow_only_wave_plan/fscr-main/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_17_change_impact_discovery/fscr-work17/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_17_change_impact_discovery/fscr-work17/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_18_best_subject/fscr-work18/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_18_best_subject/fscr-work18/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_19_bu_workbook/fscr-work19/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_19_bu_workbook/fscr-work19/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_20_cross_module_subject/RUN_REPORT.md` : 148
- `fscr-main/_fscr_run_20_cross_module_subject/fscr-work20/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_20_cross_module_subject/fscr-work20/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_21_calendar_workbook/fscr-work21/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_21_calendar_workbook/fscr-work21/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_22_calendar_change_impact/fscr-work22/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_22_calendar_change_impact/fscr-work22/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_28_token_estimate/RUN_REPORT.md` : 3
- `fscr-main/_fscr_run_30_common_features_test/NOTES.md` : 18
- `fscr-main/_fscr_run_30_common_features_test/runbook/runbook-plan.json` : 25
- `fscr-main/_fscr_run_33_procurement_test/evidence/oracle_docs/expenses_26c/enable-pretty-good-privacy-pgp-for-corporate-card-transaction.html.txt` : 2
- `fscr-main/_fscr_run_33_procurement_test/evidence/oracle_docs/expenses_26c/how-downloading-corporate-card-transaction-files-from-american.html.txt` : 2
- `fscr-main/_fscr_run_33_procurement_test/evidence/oracle_docs/expenses_26c/set-up-to-receive-american-express-gl1025-tokenized-files.html.txt` : 2
- `fscr-main/_fscr_run_33_procurement_test/evidence/oracle_docs/expenses_26c/upload-visa-mastercard-and-diner-s-club-corporate-card.html.txt` : 2
- `fscr-main/_fscr_run_33_procurement_test/evidence/oracle_docs/oapro_26c/import-flexfields-lookups-or-profile-values-using-web-services.html.txt` : 2
- `fscr-main/_fscr_run_33_procurement_test/evidence/oracle_docs/oapro_26d/import-flexfields-lookups-or-profile-values-using-web-services.html.txt` : 2
- `fscr-main/_fscr_run_33_procurement_test/evidence/project_state_copy/README.md` : 15
- `fscr-main/_fscr_run_36_scope_map/work/02_route_audit.out.json` : 9412, 9502, 9554
- `fscr-main/_fscr_run_demo_FSCR_Demo_Sheet_1_Run_Now/RUN_REPORT.md` : 81
- `fscr-main/_fscr_run_demo_FSCR_Demo_Sheet_1_Run_Now/fscr-work-demo/project/draft-impl-project-20261028/README.md` : 15
- `fscr-main/_fscr_run_demo_FSCR_Demo_Sheet_1_Run_Now/fscr-work-demo/project/draft-impl-project-20261028/artifacts/shared/reporting/fscr-claims-verification-20261029.md` : 137
- `fscr-main/_fscr_run_demo_FSCR_Demo_Sheet_1_Run_Now/fscr-work-demo/project/fscrt-run01-om-setup/README.md` : 15
- `fscr-main/_fscr_spec/ROUTE_AUDIT/01_survey_fields.out.json` : 1008
- `fscr-main/_fscr_spec/ROUTE_AUDIT/02_route_audit.out.json` : 9412, 9502, 9554
- `fscr-main/fscr-module-test-pack/CHANGES.md` : 43, 45
- `fscr-main/fscr-module-test-pack/CLAUDE.md` : 9, 11
- `fscr-main/fscr-module-test-pack/SETUP.md` : 28
- `fscr-main/fscr-module-test-pack/module-test-kit/PLAYBOOK.md` : 14, 15, 231
- `fscr-main/fscr-module-test-pack/module-test-kit/SHEET_FILL_GUIDE.md` : 21
- `fscr-main/fscr-module-test-pack/module-test-kit/prompts/module_test.md` : 13, 15, 33
- `fscr-main/fscr-module-test-pack/module-test-kit/prompts/verify.md` : 38
- `fscr-main/fscr-module-test-pack/module-test-kit/scripts/build_evidence.py` : 17, 30, 86, 90
- `fscr-main/fscr-module-test-pack/module-test-kit/scripts/make_images.py` : 13, 31, 159
- `fscr-main/fscr-module-test-pack/module-test-kit/scripts/secret_scan.py` : 1, 5, 6, 7, 10, 12, 36, 39
- `fscr-main/fscr-module-test-pack/module-test-kit/scripts/tracker_row.py` : 21, 142
- `fscr-main/fscr-module-test-pack/project/fscrt-ab-security/README.md` : 15
- `fscr-main/fscr-module-test-pack_v3.zip` : 77566, 199413
- `gaps-filled/BATCH1_PART1_RESULT.md` : 42
- `gaps-filled/BATCH1_PART2_RESULT.md` : 38
- `gaps-filled/BATCH1_PART3_RESULT.md` : 66
- `gaps-filled/PEOPLE_PROMPT.md` : 20
- `gaps-filled/README.md` : 31
- `gaps-filled/_drive_ready/gaps-filled/PEOPLE_PROMPT.md` : 20
- `gaps-filled/common-features/manage-docseq-categories/SKILL.md` : 154
- `gaps-filled/common-features/manage-standard-lookups/SKILL.md` : 153
- `gaps-filled/common-features/manage-tax-lookup-codes/SKILL.md` : 188


## What to do next

On the PC (PowerShell, in the repo folder):
```
git push -u origin main
```
Then on the laptop, follow `LAPTOP_SETUP.md` (after the push; `git fetch` needs the commits on GitHub).
