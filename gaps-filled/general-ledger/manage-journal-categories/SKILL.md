---
skill_id: "gosaas.gap-fills.erp.financials.general-ledger.manage-journal-categories"
name: "Manage Journal Categories Setup Task Guidance (GoSaaS gap fill)"
description: "Create new General Ledger journal categories (FSCRT_ test names, new rows only) through FSCR's generic setup-task CSV export and import scripts, then prove the rows exist. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill. Run 24, ETIA-TEST, 2026-11-15. Cold-tested in Run 26b, wording fixed in Run 26c. NOT official FSCR."
tested_by_fresh_chat: "Yes, Run 26b (2026-11-15): worked using only the skill, 1 import attempt, about 4 minutes; fixes applied in Run 26c"
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "General Ledger"
functional_area_code: "ORA_FIN_GENERAL_LEDGER"
task_code: "GL_MANAGE_JOURNAL_CATEGORIES"
task_name: "Manage Journal Categories"
parent_skill_id: "erp.financials.general-ledger"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
inputs:
  - "fusion_environment_context"
  - "new_category_names_and_descriptions"
outputs:
  - "csv_package_zip"
  - "import_process_log"
  - "verification_rows"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "shared.setup-import.fsm-csv-import"
side_effects:
  - "Creates a setup task CSV export process (read-only for Fusion data)."
  - "Creates a setup task CSV import process that adds journal categories in the target environment. Journal categories may not be deletable (see Rules and limits)."
required_privileges:
  - "Export Import Functional Setups User (ORA_ASM_FUNCTIONAL_SETUPS_USER_ABSTRACT) plus task privileges for GL_MANAGE_JOURNAL_CATEGORIES (FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/applications-common/25c/oafsm/automate-export-and-import-of-csv-file-packages.html)"
---

# Manage Journal Categories (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR. Origin: Run 24, ETIA-TEST. Cold-tested by a fresh chat in Run 26b; fixed in Run 26c (see `CHANGELOG.md`).**
> FSCR has no skill for this task. This file does not edit any FSCR file.
> Labels: **VERIFIED** = seen in run files (Run 24 or Run 26b) or a check we ran · **FROM FSCR** = FSCR file and line · **FROM ORACLE DOCS** = link · **GUESS** = my judgment, not tested.

## What this setup is
A journal category is a label (for example "Accrual" or "Payroll") that accountants attach to journal entries so they can sort and report them. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/financials/25b/oedmf/gljecategoriesb-16864.html

## When to use
- A user asks to create new journal categories in a Fusion environment, and the task is `GL_MANAGE_JOURNAL_CATEGORIES` ("Manage Journal Categories").
- Do **not** use it to change or remove existing categories. This skill adds new rows only.
- Test environments only until a person says otherwise. In ETIA-TEST every name must start with `FSCRT_`.

## Placeholders used below
```text
FSCR   = E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main            (read only, never edit)
GAP    = E:\GoSaaS\Configuration Automation v2.1\fscr-main\_gap_fills\journal-categories
RUN    = a NEW folder you create for this run, for example ...\fscr-main\_fscr_run_NN_journal_categories
         (its path must NOT contain a folder named exactly "project", see Rules and limits)
NN     = your run number. Replace every "RunNN" / "Run NN" below with your own value.
NAME1..NAME3 = your new category names, e.g. "FSCRT_RunNN Accrual" (check the 25-character limit)
```
Do **not** copy names from the worked examples at the end: those rows already exist, and the helper will refuse them.

## Step 0. Run FSCR in place (no copy, no edit)
- Run every FSCR script with its full path from `FSCR`, and always add `-B` so Python does not write `__pycache__` folders into FSCR.
- Send every output to `RUN` with `--output-dir`. Both FSCR scripts have this option: FROM FSCR `shared/setup-export/task-level-export/scripts/export_setup_task_csv.py:106` and `shared/setup-import/task-level-import/scripts/import_setup_task_csv.py:68`.
- Why this matters: without `--output-dir`, the export script writes into `FSCR\project\<id>\exports\...` (FROM FSCR `shared/setup-export/task-level-export/SKILL.md:181-185`), which would add files inside FSCR.
- Running in place works. VERIFIED in Run 26b: export, import and second export all ran from `FSCR` with `-B` and `--output-dir`, and the FSCR folder had 6,120 files before and after, with no new files.
- Do not print tokens, Authorization headers, token cache contents or full base64 payloads. FROM FSCR `shared/setup-import/fsm-csv-import/SKILL.md:132-134`.

## Step 1. Sign in (only if needed)
1. Check for a usable token first by running Step 2. If a script says the token is rejected or expired (the REST helper prints `TOKEN_EXPIRED`), sign in again. VERIFIED in Run 26b: the saved token worked, so sign-in was skipped.
2. FROM FSCR `shared/setup-import/task-level-import/SKILL.md:130-133`:
   ```bash
   python3 -B "<FSCR>/core/auth/fusion-oauth-authentication/scripts/fusion_login.py" --service standard --token-cache auto
   ```
   (`--service standard` was the form used in Runs 23 and 24: VERIFIED. Not exercised in Run 26b, because no sign-in was needed.) The properties file `FSCR\core\auth\fusionEnv.properties` must say `environment=ETIA-TEST` (VERIFIED, Run 26b).
3. Sign-in uses the redirect `http://127.0.0.1:8765/oauth/callback` (VERIFIED: `fusionEnv.properties` line 4 and the Run 23 login log). It starts a short listener on port 8765 that exits when sign-in completes. If the browser page is not completed, stop the listener afterwards.
4. The token is cached under the user's home folder `.fusionaim` (outside FSCR). VERIFIED (Runs 23, 24, 26b).

## Step 2. Read-only export of the existing categories
This gives the exact file layout and the list of names already in use.
```bash
cd "<FSCR>"
python3 -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code GL_MANAGE_JOURNAL_CATEGORIES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
```
- `--data` exports the populated rows; without it you get only a template. FROM FSCR `shared/setup-export/task-level-export/SKILL.md:209-221`.
- The script writes a ZIP and prints `Wrote ...zip`. Unzip it into `<RUN>/export_before/unz` (works in Git Bash and PowerShell; VERIFIED in Run 26c on the Run 26b ZIP):
  ```bash
  python3 -I -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "<the zip path it printed>" "<RUN>/export_before/unz"
  ```
- Expect 3 files: `ASM_SETUP_CSV_METADATA.xml`, `GL_JOURNAL_CATEGORY_DEF.csv`, `GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv`. VERIFIED (Runs 24, 26b)
- Row counts seen: Run 24 had 144 rows (all seed data); Run 26b had 147 (144 + the 3 Run 24 test rows). Each export took about 1 minute. VERIFIED. Expect a higher number if more test runs happened since.

## Step 3. Package layout (exact)
The ZIP has exactly 3 files. All 3 must be in the package you import. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/applications-common/24c/oafsm/export-and-import-csv-file-packages.html (keep every CSV; an empty file keeps only its header row).

| File | Role |
|---|---|
| `ASM_SETUP_CSV_METADATA.xml` | Package description. Copy it **unchanged** from the export. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/human-resources/24a/ochus/manage-role-definitions-using-csv-file-packages.html |
| `GL_JOURNAL_CATEGORY_DEF.csv` | One row per category |
| `GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv` | One row per category per language (`US` used in Runs 24 and 26b) |

**`GL_JOURNAL_CATEGORY_DEF.csv`, 27 columns in this order (VERIFIED: export and metadata XML):**
`JeCategoryName, UserJeCategoryName, JeCategoryKey, LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin, Attribute1..Attribute5, ConsolidationFlag, Description, AttributeCategory, AttributeDate1..AttributeDate5, AttributeNumber1..AttributeNumber5, DisallowMjeFlag`

**`GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv`, 11 columns in this order (VERIFIED):**
`GL_JOURNAL_CATEGORY_DEF.JeCategoryName, JeCategoryName, LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin, UserJeCategoryName, Language, SourceLang, Description`

**Values for a new row (VERIFIED: this combination worked in Runs 24 and 26b):**
- Fill only `JeCategoryName`, `UserJeCategoryName`, `JeCategoryKey` (all three the same text) and `Description`. In the translation file also `Language=US` and `SourceLang=US`.
- Leave every other column empty, including dates, "created by" and the flags.
- Write every field in double quotes, UTF-8, header row first, no BOM (the export has none). Keep the header exactly as exported.
- 128 of the 144 seed rows have name = key; 16 do not. GUESS: name = key is the safe choice for new rows (it worked twice).

## Step 4. Build a package that holds only the new rows
Use our helper (offline, makes no Oracle call). Put **your own** names and run number in:
```bash
python3 -I "<GAP>/scripts/build_package.py" \
  --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --row "FSCRT_RunNN Accrual|FSCR test category for accrual journals. Run NN." \
  --row "FSCRT_RunNN Payroll|FSCR test category for payroll journals. Run NN." \
  --row "FSCRT_RunNN Reclass|FSCR test category for reclass journals. Run NN." \
  --zip-name gl_journal_categories_fscrt.zip
```
The helper copies the headers and the metadata XML from the export, writes only your rows, and stops if:
- a name does not start with `FSCRT_`, is longer than 25 characters, or is repeated;
- a name already exists in the export (a clash would **update** that row);
- more than 3 rows are asked for (the Run 24 limit; change with `--max-rows` only if allowed).

It prints `wrote <RUN>/payload/gl_journal_categories_fscrt.zip`. VERIFIED (Run 26b). `-I` is fine here because this helper uses only the Python standard library.

## Step 5. Import
**Confirmation rule.** Before the import, the environment (ETIA-TEST), the task and the exact rows must be approved by the person. FROM FSCR `shared/setup-import/task-level-import/SKILL.md:65-67, 80`.
- If the person's brief already names the environment, the task (or "journal categories") and the exact names to create, and tells you to proceed without asking, that **is** the approval. Do not stop to ask again. Write one line in your run log: "Import approved by the brief: <environment>, <task>, <names>." (This is how Run 26b proceeded. VERIFIED)
- If any of the three is missing, or your rows differ from what the brief names, stop and ask before importing.

```bash
cd "<FSCR>"
python3 -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code GL_MANAGE_JOURNAL_CATEGORIES --task-name "Manage Journal Categories" \
  --zip-file "<RUN>/payload/gl_journal_categories_fscrt.zip" \
  --token-cache auto --wait-seconds 180 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- The script sends the ZIP as base64 to `setupTaskCSVImports` (POST), polls up to `--wait-seconds`, then downloads the process log. FROM FSCR `shared/setup-import/fsm-csv-import/SKILL.md:80-82`; FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/applications-common/25b/farca/op-fscmrestapi-resources-11.13.18.05-setuptaskcsvimports-post.html
- If it prints "Import process is not complete yet", keep the `ProcessId`, then run `get_setup_task_csv_import_result.py` (FROM FSCR `shared/setup-import/task-level-import/SKILL.md:200-210`) rather than starting a second import.
- Time: about 1 minute in Run 24, about 22 seconds in Run 26b. VERIFIED

## Step 6. Read the result
Open `<RUN>/import_result/*_process_log.txt`. **The real result is only in this log.** The script prints `StatusCode: (unknown)` even on success (VERIFIED, Runs 24 and 26b).
- The log is one long line with the text `\r\n` written literally instead of line breaks (VERIFIED, Run 26b). That is normal; search it for the phrases below.

Look for:
- `Business object: Journal Category. Status: Completed successfully.`
- `A total of 3 rows were processed. 0 rows of them failed and 0 rows completed with warnings.` (the number is your row count)
- `Total Objects Failed: 0`

If a row failed, copy the exact error into your report, change one thing, and retry at most 3 times (limit from the Run 24 brief).

## Step 7. Verify two ways
**A. REST read (read-only).** Run it **without** the `-I` flag:
```bash
python3 -B "<GAP>/scripts/rest_read_categories.py" --prefix FSCRT_ --out "<RUN>/verify_rest.json" \
  --before-dir "<RUN>/export_before/unz" \
  --expect "NAME1" --expect "NAME2" --expect "NAME3"
```
- Why no `-I`: the helper loads FSCR's sign-in code, which needs `pywin32` on Windows. `pywin32` is installed in the user site-packages folder, and `-I` hides that folder. With `-I`, Run 26b failed with "Windows Fusion OAuth storage requires pywin32"; without it, it worked (HTTP 200). VERIFIED (Run 26b; the no-`-I` form with `--before-dir` and `--expect` gave `REST CHECK: PASS` in Run 26c)
- It does one GET on `journalCategoriesLOV` with `q=UserJeCategoryName LIKE 'FSCRT_%'` and prints name, display name and description.
- **What to expect:** your new rows **plus every FSCRT_ row from earlier runs** (for example the Run 24 and Run 26b rows). It is not only your rows. VERIFIED (Run 26b saw 6 rows: 3 from Run 24 + 3 new).
- **Exact check** (the helper does this and prints `REST CHECK: PASS` or `FAIL`):
  1. every name you passed with `--expect` is in the result;
  2. REST row count = (rows starting with `FSCRT_` in the before export) + (number of new rows). Example from Run 26b: 3 + 3 = 6. VERIFIED
  If the helper prints `hasMore=true`, the result was cut off and the count is not reliable (GUESS: unlikely below 500 rows).

**B. Second export, then compare (offline compare):**
```bash
# repeat Step 2 with --output-dir "<RUN>/export_after", unzip to <RUN>/export_after/unz
python3 -I "<GAP>/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --expect "NAME1" --expect "NAME2" --expect "NAME3" \
  --rows-out "<RUN>/verify_rows.csv"
```
`RESULT: PASS` means: only the expected rows were added, none were removed, no existing row changed, and each new row has a US translation row. VERIFIED: PASS on Run 24 (144 → 147) and Run 26b (147 → 150). `-I` is fine here (standard library only).

Save `verify_rows.csv` and `verify_rest.json` as the proof.

## Rules and limits
1. **Keep every file in the package.** All 3 files, including an unchanged metadata XML. FROM ORACLE DOCS (links in Step 3).
2. **New rows only.** Never import a full export. The import matches on the category name, so a matching name would change that row. GUESS about the matching rule; the helper refuses any name that already exists, so it cannot happen with this helper.
3. **Names.** At most **25 characters** (FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/financials/25b/oedmf/gljecategoriesb-16864.html, the category name column). In test environments start with `FSCRT_`. The name is the identity of the row, so do not reuse names. VERIFIED: letters, digits, `_` and spaces worked (Runs 24, 26b). GUESS: other characters were not tried.
4. **Test rows may stay for good.** Oracle's older E-Business Suite help says a category cannot be deleted once saved (https://ap1.mclaneco.com/OA_HTML/HelpServlet/US/GL/@t_categ). That is not Fusion's own documentation, so treat it as a **GUESS** for Fusion (not tested), and plan as if test rows stay in the environment. This skill never deletes or updates.
5. **Limit.** At most 3 rows per run was the Run 24 rule. It is not an Oracle limit.
6. **Do not let FSCR write inside FSCR.** The export script writes into `FSCR\project\<id>\...` and a token-usage log if no `--output-dir` is given, or if the output path contains a folder named exactly `project` (FROM FSCR `export_setup_task_csv.py:271-278, 355`). Use a run folder without such a folder name.
7. **Language.** Only the `US` translation row was tried. GUESS: other languages need extra rows in the translation file.
8. **One environment tested.** Only ETIA-TEST, release 11.13.26.10.0. VERIFIED (Runs 24, 26b). Other environments and releases are untested.
9. **Sign-in needs a person.** The browser sign-in page must be completed by the user. Do not read or type credentials.
10. **What a fresh chat has tested.** Run 26b (fresh chat, skill only) confirmed: running FSCR in place, reusing the saved token, Steps 2 to 7B, and `rest_read_categories.py` once run without `-I`. VERIFIED. Still not tested by a fresh chat: the sign-in step (`fusion_login.py --service standard` on port 8765) and the `get_setup_task_csv_import_result.py` fallback. GUESS that they work as written.
11. **Python flags.** Use `-B` for FSCR scripts and for `rest_read_categories.py`. Use `-I` only for the offline helpers (`build_package.py`, `compare_exports.py`) and the unzip one-liner. VERIFIED (Run 26b)

## Worked examples (VERIFIED)
Use these to see what good output looks like. **Do not reuse these names**; they now exist in ETIA-TEST.

| Item | Run 24 | Run 26b (fresh chat, skill only) |
|---|---|---|
| Environment | ETIA-TEST, 11.13.26.10.0 | ETIA-TEST, 11.13.26.10.0 |
| Export before | process 100004736427669: 144 rows, no FSCRT_ rows | process 100004736427677: 147 rows, 3 FSCRT_ rows (Run 24) |
| New rows | `FSCRT_Run24 Accrual`, `FSCRT_Run24 Payroll`, `FSCRT_Run24 Reclass` | `FSCRT_Run26 Accrual`, `FSCRT_Run26 Payroll`, `FSCRT_Run26 Reclass` |
| Import | process 100004736418670, request 4,461,578, attempt 1: "3 rows were processed. 0 rows of them failed" | process 100004737392040, request 4,461,602, attempt 1: same result |
| Export after | process 100004737393007: 147 rows; added 3, removed 0, changed 0 | process 100004736418683: 150 rows; added 3, removed 0, changed 0 |
| REST read | 3 FSCRT_ rows (HTTP 200) | 6 FSCRT_ rows = 3 earlier + 3 new (HTTP 200), after dropping `-I` |
| Time | about 6 minutes | about 4 minutes |

Pattern for your run: names `FSCRT_RunNN <Word>` (name = display name = key), description "FSCR test category for <word> journals. Run NN."

Full evidence: `_fscr_run_24_fill_route_only\RUN_REPORT.md` and `_fscr_run_26b_skill_test\RUN_REPORT.md`, `RUN_LOG.md`, `proof\`.
