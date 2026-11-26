---
skill_id: "gosaas.gap-fills.common-features.manage-china-financial-data-export-options"
name: "Manage Enterprise Financial Data Export Options for China: FSM CSV route blocked by a missing privilege (GoSaaS gap fill, FAILED)"
description: "Records the FSM CSV route of JA_MANAGE_ENTERPRISE_FINANCIAL_DATA_EXPORT_OPTIONS_FOR_CHINA and why it could not be used: the task export is refused with access denied (web service permission) for the sign-in user. No record was created. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 16, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "JA_MANAGE_ENTERPRISE_FINANCIAL_DATA_EXPORT_OPTIONS_FOR_CHINA"
task_name: "Manage Enterprise Financial Data Export Options for China"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "a sign-in user with the localization role that may export / import this object (see Prerequisites)"
side_effects:
  - "None while blocked: the export is read only and was refused."
---

# Manage Enterprise Financial Data Export Options for China (GoSaaS gap fill, FAILED)

> **STATUS: FAILED (2026-11-26).** The FSM CSV route exists (CSV flag Y), but the sign-in user may not call the object's export service: Oracle's process log says `access denied ("oracle.wsm.security.WSFunctionPermission" ".../apacLocalizations/financialReports/dataExport/financialDataExportService/FinancialDataExp... (export operation)" "invoke")` and "Review and report the errors for this object to product Financials for Asia/Pacific". Both the data export and the template export were refused (VERIFIED). Without an export there is no file layout, so nothing was loaded.
> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
China enterprise financial data export (GB/T 24589) options: system parameters, depreciation method assignment, subsidiary account sources and mappings, cash flow statement and DFF assignments. Package objects (from the export metadata, VERIFIED): ORA_JA_CN_SYSTEM_PARAMETER, ORA_JA_CN_METHOD_ASSIGNMENT, ORA_JA_CN_SUB_ACC_SOURCES, ORA_JA_CN_SUB_ACC_MAPPING, ORA_JA_CN_SUB_CFS_ASSIGNMENT, ORA_JA_CN_SUB_DFF_ASSIGNMENT (China Golden Tax / financial data export setup).
Use this skill only after the privilege below is granted; until then the task is done on its page.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in coreuthusionEnv.properties). Read only.
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name).

## Prerequisites
1. The sign-in user needs a role that may invoke the object's export/import web service (the localization role of Financials for Asia/Pacific; GUESS which one: ask the security administrator to compare with the privileges of a localization implementation role). Without it, Step 1 fails as below.

## Step 1. Read-only export (VERIFIED: refused here)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code JA_MANAGE_ENTERPRISE_FINANCIAL_DATA_EXPORT_OPTIONS_FOR_CHINA --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; z=zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]); print([n for n in z.namelist()])" "<RUN>/exp1"
```
Working: CSV files are listed. **Blocked (seen here):** only `ASM_SETUP_CSV_METADATA.xml`, with process status `COMPLETED_ERRORS`. To read the reason, download the process log into `<RUN>` (`get_setup_task_csv_export_result.py --task-code ... --process-id <ProcessId> --download-log`, run from inside `<RUN>`: it writes into a `discovery` folder under the current folder) and grep only `Status details: access denied`.

## Step 2 to 4 (GUESS, not run)
After the privilege is granted: build ONE new row with your prefix from the export's columns (`<GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py`), import once with `import_setup_task_csv.py`, export again and compare (`compare_fsm_exports.py`), as in the other GoSaaS Common Features skills.

## Rules and limits
1. Do not ask for the privilege for a test user without the environment owner's approval.
2. Country setup: a test needs a legal entity of that country (GUESS).
3. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Data export | ProcessId 100004744431867: COMPLETED_ERRORS, access denied (web service permission) |
| Template export | template export also refused (COMPLETED_ERRORS) |
