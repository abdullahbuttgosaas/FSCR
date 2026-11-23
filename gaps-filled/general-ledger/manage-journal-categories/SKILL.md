---
skill_id: "gosaas.gap-fills.erp.financials.general-ledger.manage-journal-categories"
name: "Manage Journal Categories Setup Task Guidance (GoSaaS gap fill)"
description: "Create new General Ledger journal categories (test-prefixed names, new rows only) through FSCR's generic setup-task CSV export and import scripts, then prove the rows exist. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill. Run 24, one test environment, 2026-11-15. Cold-tested in Run 26b, wording fixed in Run 26c. NOT official FSCR."
tested_by_fresh_chat: "Yes, Run 26b (2026-11-15); made generic and re-tested by a fresh chat 2026-11-24 (PASS). See CHANGELOG.md"
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
version: "0.3.0"
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

> **Added by GoSaaS, not part of official FSCR. Origin: Run 24, one test environment. Cold-tested by a fresh chat in Run 26b; fixed in Run 26c (see `CHANGELOG.md`).**
> FSCR has no skill for this task. This file does not edit any FSCR file.
> Labels: **VERIFIED** = seen in run files (Run 24 or Run 26b) or a check we ran · **FROM FSCR** = FSCR file and line · **FROM ORACLE DOCS** = link · **GUESS** = my judgment, not tested.

## What this setup is
A journal category is a label (for example "Accrual" or "Payroll") that accountants attach to journal entries so they can sort and report them. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/financials/25b/oedmf/gljecategoriesb-16864.html

## When to use
- A user asks to create new journal categories in a Fusion environment, and the task is `GL_MANAGE_JOURNAL_CATEGORIES` ("Manage Journal Categories").
- Do **not** use it to change or remove existing categories. This skill adds new rows only.
- Test environments only until a person says otherwise. Every name must start with your test prefix (`PREFIX` below).

## Placeholders used below
```text
FSCR   = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties,
         and whose fusionEnv.properties is filled in for the approved environment (not a template with <...> values).
         In a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main. Read only, never edit.
GAP    = the folder that holds this SKILL.md (its helpers are in GAP\scripts)
GAPS   = the gaps-filled folder two levels above this SKILL.md (Step 7A uses its generic rest_read.py)
RUN    = a NEW empty folder you create for this run, OUTSIDE FSCR
         (its path must NOT contain a folder named exactly "project", see Rules and limits)
PREFIX = your test prefix, e.g. GAPFILL_ or whatever your test environment requires. Every new name starts with it.
NAME1..NAME3 = your new category names, e.g. "<PREFIX>Accrual" (check the 25-character limit).
         Create only as many as the brief approves (1 to 3); drop the unused --row / --expect lines.
```
Do **not** copy names from the worked examples at the end: those rows already exist, and the helper will refuse them.

## Step 0. Run FSCR in place (no copy, no edit)
- Run every FSCR script with its full path from `FSCR`, and always add `-B` so Python does not write `__pycache__` folders into FSCR.
- Send every output to `RUN` with `--output-dir`. Both FSCR scripts have this option: FROM FSCR `shared/setup-export/task-level-export/scripts/export_setup_task_csv.py:106` and `shared/setup-import/task-level-import/scripts/import_setup_task_csv.py:68`.
- Why this matters: without `--output-dir`, the export script writes into `FSCR\project\<id>\exports\...` (FROM FSCR `shared/setup-export/task-level-export/SKILL.md:181-185`), which would add files inside FSCR.
- Running in place works. VERIFIED in Run 26b: export, import and second export all ran from `FSCR` with `-B` and `--output-dir`, and the FSCR folder had 6,120 files before and after, with no new files.
- Do not print tokens, Authorization headers, token cache contents or full base64 payloads. FROM FSCR `shared/setup-import/fsm-csv-import/SKILL.md:132-134`.

## Step 1. Sign in (only if needed)
1. Check for a usable token first by running Step 2. If a script says the token is rejected or expired (HTTP 401/403, or the Step 7A helper exits 2), sign in again. VERIFIED in Run 26b: the saved token worked, so sign-in was skipped.
2. FROM FSCR `shared/setup-import/task-level-import/SKILL.md:130-133`:
   ```bash
   python3 -B "<FSCR>/core/auth/fusion-oauth-authentication/scripts/fusion_login.py" --service standard --token-cache auto
   ```
   (`--service standard` was the form used in Runs 23 and 24: VERIFIED. Not exercised in Run 26b, because no sign-in was needed.) The properties file `FSCR\core\auth\fusionEnv.properties` must name the environment the person approved; check it before the import.
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
Use our helper (offline, makes no Oracle call). Put **your own** prefix, names and descriptions in:
```bash
python3 -I "<GAP>/scripts/build_package.py" \
  --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --prefix "<PREFIX>" \
  --row "NAME1|Test category for accrual journals." \
  --row "NAME2|Test category for payroll journals." \
  --row "NAME3|Test category for reclass journals." \
  --zip-name gl_journal_categories_new.zip
```
The helper copies the headers and the metadata XML from the export, writes only your rows, and stops if:
- a name does not start with `--prefix` (default `FSCRT_` if you leave it out, so always pass it), is longer than 25 characters, or is repeated;
- a name already exists in the export (a clash would **update** that row);
- more than 3 rows are asked for (the Run 24 limit; change with `--max-rows` only if allowed).

It prints `wrote <RUN>/payload/gl_journal_categories_new.zip`. VERIFIED (Run 26b). `-I` is fine here because this helper uses only the Python standard library.

## Step 5. Import
**Confirmation rule.** Before the import, the environment, the task and the exact rows must be approved by the person. FROM FSCR `shared/setup-import/task-level-import/SKILL.md:65-67, 80`.
- If the person's brief already names the environment, the task (or "journal categories") and the exact names to create, and tells you to proceed without asking, that **is** the approval. Do not stop to ask again. Write one line in a run log file in RUN (e.g. `<RUN>/RUN_LOG.md`): "Import approved by the brief: <environment>, <task>, <names>." (This is how Run 26b proceeded. VERIFIED)
- If any of the three is missing, or your rows differ from what the brief names, stop and ask before importing.

```bash
cd "<FSCR>"
python3 -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code GL_MANAGE_JOURNAL_CATEGORIES --task-name "Manage Journal Categories" \
  --zip-file "<RUN>/payload/gl_journal_categories_new.zip" \
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
**A. REST read (read-only).** Use the generic GoSaaS read helper `rest_read.py`, which takes the FSCR folder as an argument. It lives in the gaps-filled folder two levels above this SKILL.md, at `<GAPS>/common-features/manage-docseq-categories/scripts/rest_read.py` (`GAPS` = the gaps-filled folder). Run it **without** `-I`, once per new name:
```bash
python -B "<GAPS>/common-features/manage-docseq-categories/scripts/rest_read.py" --fscr "<FSCR>" \
  --resource journalCategoriesLOV --q "UserJeCategoryName='NAME1'" \
  --fields UserJeCategoryName,Description --out "<RUN>/verify_rest_1.json" \
  --expect "UserJeCategoryName=NAME1" --expect-count 1
```
- `READBACK: PASS` = exactly one category with that name. Exit 2 = sign-in, privilege or HTTP problem. Repeat with NAME2/NAME3 (and `verify_rest_2.json`, ...) if you created more. VERIFIED (re-test 2026-11-24: this resource and these fields answer HTTP 200).
- Why no `-I`: FSCR's sign-in code needs `pywin32` on Windows, which lives in the user site-packages folder that `-I` hides ("Windows Fusion OAuth storage requires pywin32"). VERIFIED (Run 26b)
- Do **not** use `GAP/scripts/rest_read_categories.py`: it finds FSCR only from its old folder and fails elsewhere with `No module named 'fusion_auth'` (VERIFIED, re-test 2026-11-24). It is kept for history only.

**B. Second export, then compare (offline compare):**
```bash
# repeat Step 2 with --output-dir "<RUN>/export_after", unzip to <RUN>/export_after/unz
python3 -I "<GAP>/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --prefix "<PREFIX>" --expect "NAME1" --expect "NAME2" --expect "NAME3" \
  --rows-out "<RUN>/verify_rows.csv"
```
Always pass `--prefix` (the default `FSCRT_` makes other names FAIL). `RESULT: PASS` means: only the expected rows were added, none were removed, no existing row changed, and each new row has a US translation row. VERIFIED: PASS on Run 24 (144 → 147) and Run 26b (147 → 150). `-I` is fine here (standard library only).

Save `verify_rows.csv` and the `verify_rest_*.json` files as the proof.

## Rules and limits
1. **Keep every file in the package.** All 3 files, including an unchanged metadata XML. FROM ORACLE DOCS (links in Step 3).
2. **New rows only.** Never import a full export. The import matches on the category name, so a matching name would change that row. GUESS about the matching rule; the helper refuses any name that already exists, so it cannot happen with this helper.
3. **Names.** At most **25 characters** (FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/financials/25b/oedmf/gljecategoriesb-16864.html, the category name column). In test environments start with your test prefix. The name is the identity of the row, so do not reuse names. VERIFIED: letters, digits, `_` and spaces worked (Runs 24, 26b). GUESS: other characters were not tried.
4. **Test rows may stay for good.** Oracle's older E-Business Suite help says a category cannot be deleted once saved (https://ap1.mclaneco.com/OA_HTML/HelpServlet/US/GL/@t_categ). That is not Fusion's own documentation, so treat it as a **GUESS** for Fusion (not tested), and plan as if test rows stay in the environment. This skill never deletes or updates.
5. **Limit.** At most 3 rows per run was the Run 24 rule. It is not an Oracle limit.
6. **Do not let FSCR write inside FSCR.** The export script writes into `FSCR\project\<id>\...` and a token-usage log if no `--output-dir` is given, or if the output path contains a folder named exactly `project` (FROM FSCR `export_setup_task_csv.py:271-278, 355`). Use a run folder without such a folder name.
7. **Language.** Only the `US` translation row was tried. GUESS: other languages need extra rows in the translation file.
8. **One environment tested.** One test environment, release 11.13.26.10.0. VERIFIED (Runs 24, 26b, re-test 2026-11-24). Other environments and releases are untested.
9. **Sign-in needs a person.** The browser sign-in page must be completed by the user. Do not read or type credentials.
10. **What a fresh chat has tested.** Run 26b (fresh chat, skill only) confirmed: running FSCR in place, reusing the saved token, Steps 2 to 7B. VERIFIED. The 2026-11-24 re-test confirmed the generic wording (placeholders, `--prefix`). VERIFIED. Still not tested by a fresh chat: the sign-in step (`fusion_login.py --service standard` on port 8765) and the `get_setup_task_csv_import_result.py` fallback. GUESS that they work as written.
11. **Python flags.** Use `-B` for FSCR scripts and for `rest_read.py`. Use `-I` only for the offline helpers (`build_package.py`, `compare_exports.py`) and the unzip one-liner. VERIFIED (Run 26b)

## Worked examples (VERIFIED)
Use these to see what good output looks like. **Do not reuse these names**; they now exist in our test environment. Process numbers are from that environment.

| Item | Run 24 | Run 26b (fresh chat, skill only) |
|---|---|---|
| Environment | one test environment, 11.13.26.10.0 | same |
| Export before | process 100004736427669: 144 rows, no FSCRT_ rows | process 100004736427677: 147 rows, 3 FSCRT_ rows (Run 24) |
| New rows | `FSCRT_Run24 Accrual`, `FSCRT_Run24 Payroll`, `FSCRT_Run24 Reclass` | `FSCRT_Run26 Accrual`, `FSCRT_Run26 Payroll`, `FSCRT_Run26 Reclass` |
| Import | process 100004736418670, request 4,461,578, attempt 1: "3 rows were processed. 0 rows of them failed" | process 100004737392040, request 4,461,602, attempt 1: same result |
| Export after | process 100004737393007: 147 rows; added 3, removed 0, changed 0 | process 100004736418683: 150 rows; added 3, removed 0, changed 0 |
| REST read | 3 FSCRT_ rows (HTTP 200) | 6 FSCRT_ rows = 3 earlier + 3 new (HTTP 200), after dropping `-I` |
| Time | about 6 minutes | about 4 minutes |

Pattern for your run: names `<PREFIX><Word>` (name = display name = key), a short description.

Full evidence is kept in the GoSaaS run folders of Runs 24 and 26b (not needed to use this skill).
