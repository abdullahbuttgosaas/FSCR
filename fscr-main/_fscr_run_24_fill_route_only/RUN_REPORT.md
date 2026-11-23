# Run 24: fill a "route only" gap (Manage Journal Categories)

**Result: FILLED.** 3 new journal categories were created in ETIA-TEST and proven to exist. It took 1 import attempt and no fixes. VERIFIED

**Tags:** VERIFIED = seen in files or the pod · FROM FSCR = FSCR file and line · FROM ORACLE DOCS = link · GUESS = my judgment.

## Numbers
| Item | Value |
|---|---|
| Start / end | 2026-11-15 15:57:12 / 16:02:45 (+05:00). VERIFIED (`start_time.txt`, `finish_time.txt`) |
| Total minutes | about 6 (5 min 33 s). VERIFIED |
| Import attempts | 1 (succeeded); fixes needed: 0. VERIFIED |
| Oracle processes | export 100004736427669 (before), import 100004736418670, export 100004737393007 (after). VERIFIED |
| Records created | 3, all named FSCRT_. No updates, no deletes. VERIFIED |
| Tokens | My own token use is not visible to me. FSCR's export script logged an estimate of 2,782 and 2,863 output tokens (chars/4 method). VERIFIED (`fscr-work24/project/run24*/artifacts/shared/token-usage/`) |

## What was created (proof in `verify_rows.csv` and `evidence/verify_rest_journalCategoriesLOV.json`)
| Name (= key) | Description | Created by |
|---|---|---|
| FSCRT_Run24 Accrual | FSCR test category for accrual journals. Run 24. | Configuration.TEST, 2026/11/15 11:01 UTC |
| FSCRT_Run24 Payroll | FSCR test category for payroll journals. Run 24. | same |
| FSCRT_Run24 Reclass | FSCR test category for reclass journals. Run 24. | same |

**Checks (VERIFIED)**
- **REST read:** `journalCategoriesLOV` filtered on `FSCRT_%` returns these 3 rows exactly.
- **Export before and after:** 144 rows before, 147 after. Exactly these 3 were added and none removed. 0 existing rows changed (a full row-by-row compare).
- **Translation file:** it has a US row for each of the 3.

## Steps
1. **Read FSCR.** I read the generic import skill, the task-level import and export skills, and the GL lookup notes (file list below). FSCR has no skill for this task. VERIFIED
2. **Copy, do not edit.** I copied FSCR's `core/auth`, `core/project-mgmt`, `shared/setup-export`, `shared/setup-import` and `knowledge/setup-task-catalog` into `fscr-work24/`. The scripts ran from that copy. The 45 original FSCR files have the same MD5 at the end as at the start. VERIFIED
3. **Sign-in:** none needed. The token cached by Run 23 was still valid, with about 48 minutes left. Nothing was started on port 8765. VERIFIED
4. **Export existing data.** I ran FSCR `export_setup_task_csv.py --data`. The package holds 3 files: `GL_JOURNAL_CATEGORY_DEF.csv` (27 columns), `GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv` (11 columns) and `ASM_SETUP_CSV_METADATA.xml`. All 144 rows were Oracle seed data, and none was named FSCRT_. VERIFIED (`export_existing/`)
5. **Build the CSV.** `scripts/build_package.py` copies the exported headers and the metadata XML unchanged and writes only the 3 new rows.
   - Fields filled: name, display name, key (all the same value) and description. Every other column is blank.
   - Package: `payload/gl_journal_categories_fscrt.zip`. VERIFIED
   - Only new rows were included, so existing rows could not be updated.
6. **Import.** I ran FSCR `import_setup_task_csv.py` (POST `setupTaskCSVImports`, then polling, then the log). The log reads: "A total of 3 rows were processed. 0 rows of them failed". VERIFIED (`evidence/import_attempt1/`)
7. **Verify.** A REST read plus a second FSCR export (above). VERIFIED

## Problems met
- **FSCR export script crashed on first run.** The error was `ModuleNotFoundError: token_usage_logger`. The cause was mine: my partial copy left out `core/project-mgmt`, and the export scripts import from it. I fixed it by copying that folder too. This was not an Oracle error and not an import attempt. VERIFIED (`evidence/export_existing.log` holds the second, successful run)
- **The import script polls for only 3 minutes** (FROM FSCR `shared/setup-import/task-level-import/SKILL.md:83`). That was enough here: it finished in about 1 minute. VERIFIED
- **The FSCR log prints "StatusCode: (unknown)" even when it succeeds.** The real result is only in the downloaded ProcessLog. VERIFIED
- **Test rows stay.** Oracle does not let you delete journal categories, so these 3 rows remain in ETIA-TEST. GUESS, based on the Oracle note under Sources about category deletion.

## What FSCR provided vs what Claude had to add

| Need | FSCR provided | Claude added or fixed |
|---|---|---|
| Sign-in and token | Yes: `core/auth` (reused the Run 23 token). FROM FSCR `shared/setup-import/task-level-import/SKILL.md:75` | nothing |
| Task code and the CSV-supported check | Yes: catalog plus script check. FROM FSCR `.../task-level-import/SKILL.md:102-105` | nothing |
| Export of current data | Yes: `task-level-export` script. FROM FSCR `shared/setup-export/task-level-export/SKILL.md:209-213` | had to copy `core/project-mgmt` so it would run outside the repo |
| CSV layout (files, columns, required fields) | **No.** No skill or guide for this task. VERIFIED | worked it out from the ETIA-TEST export plus Oracle docs |
| Rules for editing a package | **No** | Oracle docs: keep every CSV, keep the metadata XML, keep formats |
| Field limits (name 25 characters, name = key) | **No.** FSCR only names `journalCategoriesLOV` fields (FROM FSCR `pillars/erp/financials/general-ledger/manage-reporting-currencies/ora-resource/ora_reference_lookups.md:29`) | Oracle table docs (25 characters); names kept to 19 characters |
| Safe package (new rows only, no updates) | **No** | `scripts/build_package.py`, plus a name check against the export before import |
| Import call, polling, log download | Yes: `import_setup_task_csv.py` / `fsm_csv_import_engine.py`. FROM FSCR `shared/setup-import/fsm-csv-import/SKILL.md:80-82` | nothing |
| Proof the rows exist | Partly: export script; the LOV is named in GL notes | REST read script plus a before/after row compare |

**Short version:** FSCR provided the plumbing: sign-in, export, import and polling. Claude added the task-specific part: the file layout, the 3 rows, the safety rules and the proof. VERIFIED for this one task. For other one-file setups this is likely similar. GUESS

## FSCR files used (read or run from the copy)
- `shared/setup-import/fsm-csv-import/SKILL.md` and `scripts/fsm_csv_import_engine.py`
- `shared/setup-import/task-level-import/SKILL.md` and `scripts/import_setup_task_csv.py` (plus its helper scripts)
- `shared/setup-export/task-level-export/SKILL.md` and `scripts/export_setup_task_csv.py` (plus its helpers)
- `shared/setup-export/fsm-csv-export/scripts/*` (imported by the export script)
- `core/auth/fusion-oauth-authentication/scripts/*` and `core/auth/fusionEnv.properties`
- `core/project-mgmt/scripts/*` (token-usage logger)
- `knowledge/setup-task-catalog/release/setupTasksAll.json`
- Read for context only: `pillars/erp/financials/general-ledger/manage-reporting-currencies/ora-resource/ora_reference_lookups.md:29`

## Sources (Oracle docs)
- [Export and Import CSV File Packages](https://docs.oracle.com/en/cloud/saas/applications-common/24c/oafsm/export-and-import-csv-file-packages.html): keep every CSV file, keep formats.
- [Manage Role Definitions Using CSV File Packages](https://docs.oracle.com/en/cloud/saas/human-resources/24a/ochus/manage-role-definitions-using-csv-file-packages.html): do not change `ASM_SETUP_CSV_METADATA.xml`, zip the CSVs and the XML together.
- [Create a setup task CSV import (REST)](https://docs.oracle.com/en/cloud/saas/applications-common/25b/farca/op-fscmrestapi-resources-11.13.18.05-setuptaskcsvimports-post.html)
- [GL_JE_CATEGORIES_B table](https://docs.oracle.com/en/cloud/saas/financials/25b/oedmf/gljecategoriesb-16864.html): category name, 25 characters.
- [Journal category help, E-Business Suite](https://ap1.mclaneco.com/OA_HTML/HelpServlet/US/GL/@t_categ): a category cannot be deleted. This is EBS, not Fusion, so GUESS for Fusion.

## Clean-up
- **No new process:** this run started no sign-in listener and no server. The only background work was the FSCR scripts, which ran in the foreground and exited.
- **Final check:** port 8765 is free and no Python process is running. VERIFIED
