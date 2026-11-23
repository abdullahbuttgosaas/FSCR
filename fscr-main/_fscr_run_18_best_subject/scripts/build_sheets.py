"""Run 18: build Excel sheets from the FSCR FSM exports (local only)."""
import csv,glob,sys
from openpyxl import Workbook
from openpyxl.styles import Font
csv.field_size_limit(10**9); R=sys.argv[1]
def sheet(task,fname,out,title,extra):
    f=glob.glob(f'{R}/evidence/exports/{task}/csv/**/{fname}',recursive=True)[0]
    rows=list(csv.reader(open(f,encoding='utf-8-sig'))); wb=Workbook(); ws=wb.active; ws.title=title
    for r in rows: ws.append(r)
    for c in ws[1]: c.font=Font(bold=True)
    ws.freeze_panes='A2'
    for i,c in enumerate(rows[0],1): ws.column_dimensions[ws.cell(1,i).column_letter].width=max(12,min(40,len(c)+4))
    s=wb.create_sheet('Source'); s.append(['Pod ETIA-TEST, read-only.']); s.append([f'Route: FSCR task-level FSM CSV export, task {task}, file {fname}.']); [s.append([x]) for x in extra]
    wb.save(f'{R}/{out}'); print(out,len(rows)-1,'rows',len(rows[0]),'cols',rows[0])
sheet('FUN_MANAGE_BUSINESS_UNIT','FUN_BUSINESS_UNIT.csv','business_units_ETIA-TEST.xlsx','BusinessUnits',['Same export also holds: FUN_BU_USAGE.csv (business functions), FUN_BU_SERVICE_PROVIDERS.csv, LE_1214416713655.csv (set assignments).'])
sheet('FND_MANAGE_REFERENCE_DATA_SETS','FND_APP_REFERENCE_DATA_SET.csv','reference_data_sets_ETIA-TEST.xlsx','ReferenceDataSets',['REST setIdSetsLOV returned 39 sets (export: user-visible sets only).'])
sheet('FND_MANAGE_CURRENCIES','FND_APP_REF_CURRENCY.csv','currencies_ETIA-TEST.xlsx','Currencies',['Export holds only 9 currencies; REST currenciesLOV returned 268. The export seems to hold only added or changed currencies (not checked).'])
