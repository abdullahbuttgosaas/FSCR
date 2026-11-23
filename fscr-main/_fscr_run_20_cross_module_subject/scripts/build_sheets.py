"""Run 20: unzip the 3 GL exports and save the main file of each as an Excel sheet (local only).
Also prints the files, row counts and columns, and the rows that the live chains use."""
import csv, glob, os, sys, zipfile, json
from openpyxl import Workbook
from openpyxl.styles import Font
csv.field_size_limit(10**9)
R = sys.argv[1]; E = R + '/evidence/exports/'
MAIN = {'GL_MANAGE_ACCOUNTING_CALENDARS': 'accounting_calendars_ETIA-TEST.xlsx',
        'GL_MANAGE_CONVERSION_RATE_TYPES': 'conversion_rate_types_ETIA-TEST.xlsx',
        'GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SET_VALUES': 'coa_value_set_values_ETIA-TEST.xlsx'}
summary = {}
for task, out in MAIN.items():
    zs = glob.glob(E + task + '/*.zip')
    if not zs:
        summary[task] = 'NO EXPORT'; print(task, 'NO EXPORT'); continue
    d = E + task + '/csv'; os.makedirs(d, exist_ok=True); zipfile.ZipFile(zs[0]).extractall(d)
    files = sorted(glob.glob(d + '/**/*.csv', recursive=True))
    wb = Workbook(); wb.remove(wb.active); info = {}
    for f in files:
        rows = list(csv.reader(open(f, encoding='utf-8-sig', errors='replace')))
        name = os.path.basename(f)[:-4]
        info[name] = {'rows': len(rows) - 1, 'cols': rows[0] if rows else []}
        if len(rows) - 1 > 50000:
            continue
        ws = wb.create_sheet(name[:31])
        for r in rows:
            ws.append(r)
        for c in ws[1]:
            c.font = Font(bold=True)
        ws.freeze_panes = 'A2'
    s = wb.create_sheet('Source'); s.append(['Pod ETIA-TEST, read-only.']); s.append([f'Route: FSCR task-level FSM CSV export, task {task}. One sheet per CSV file in the export zip.'])
    wb.save(R + '/' + out); summary[task] = info
    print('##', task, '->', out)
    for n, i in info.items():
        print('  ', n, i['rows'], 'rows', len(i['cols']), 'cols', i['cols'][:14])
json.dump(summary, open(R + '/evidence/export_summary.json', 'w'), indent=1)
