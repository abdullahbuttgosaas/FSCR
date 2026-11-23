# Run 29: write the proposed tracker row. No Oracle calls.
import csv, os, sys
out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
row = {
    'Module': 'ERP / Common Features',
    'Test status': 'In progress',
    'FSCR coverage': 'Partial',
    'Fit rating': 'Medium',
    'Plan accuracy': 'not run',
    'Runbook quality': 'not run',
    'Execution and validation': 'not run (PROPOSED 3 if a score is wanted)',
    'FSCR skills / workflows used': 'shared/setup-export/task-level-export; pillars/erp/financials/organization-structures (manage-business-unit.md + ora-resource); core/data-loader + Task Hook; core/runbook; financial-reporting-structures/manage-accounting-calendars; core/fusion-api/rest-api-client; FSCR sign-in',
    'Test scenario': 'Create 2 test BUs via FSM CSV and read back; update a BU manager; export BUs, reference data sets, currencies, ledgers, calendars, CoA values, conversion rate types; trace a calendar change to Receivables in a workbook copy',
    'Fusion env / release': 'ETIA-TEST, 11.13.26.10.0',
    'Last tested': '2026-11-09 (Run 22 analysis on a copy; last Oracle write on a Common Features task 2026-11-03, Run 01)',
    'Key findings': '\n'.join([
        '- FSCR export reads every Common Features task with a CSV flag; it worked each time (BUs, sets, ledgers, calendars, CoA values, rate types).',
        '- Skills are guides, not builders: BU create needed a GoSaaS builder; FSCR\'s own rule blocked a BU update.',
        '- 65 of 144 tasks have a skill; most of those skills sit under HCM, CX or SCM. Application Extensions and approvals are weakest.',
        '- FSCR cannot find what uses a record; GoSaaS did all BU and calendar impact tracing.',
        '- Some FSCR rules are useful as is (calendar continuity, BU-to-ledger advice), but advice does not always match real data.']),
    'GoSaaS gap / build needed': '\n'.join([
        '- GoSaaS built a BU CSV package builder and a BU update builder.',
        '- GoSaaS built a REST reader and an export-result fetcher for gaps in FSCR reads.',
        '- GoSaaS built cross-file join and impact scripts plus BU and calendar workbooks.',
        '- GoSaaS wrote the Task Hook rule results (FSCR only checks their shape).',
        '- Still needed: recipes for 49 route-only tasks, task links for apps-common skills, an approvals skill.']),
    'Evidence': '_fscr_run_29_common_features (RUN_REPORT.md, common_features_tasks.csv); runs 01, 02, 03, 05, 09, 18-22 RUN_REPORT.md',
}
with open(os.path.join(out, 'tracker_row.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(row))
    w.writeheader()
    w.writerow(row)
print('ok')
