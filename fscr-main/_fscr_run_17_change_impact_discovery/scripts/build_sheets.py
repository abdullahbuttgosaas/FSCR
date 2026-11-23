"""Run 17: build the two Excel sheets from the read-only exports (local only)."""
import csv,glob,json,sys
from openpyxl import Workbook
from openpyxl.styles import Font
csv.field_size_limit(10**9); R=sys.argv[1]
def save(path,title,cols,rows,note):
    wb=Workbook(); ws=wb.active; ws.title=title; ws.append(cols)
    for c in ws[1]: c.font=Font(bold=True)
    for r in rows: ws.append([r.get(c,'') if r.get(c) is not None else '' for c in cols])
    ws.freeze_panes='A2'
    for i,c in enumerate(cols,1): ws.column_dimensions[ws.cell(1,i).column_letter].width=max(12,min(45,len(c)+4))
    n=wb.create_sheet('Source'); [n.append([x]) for x in note]; wb.save(path); print(path,len(rows),'rows',len(cols),'cols',cols)
f=glob.glob(R+'/evidence/exports/DOO_MANAGE_ORCHESTRATION_LOOKUPS/csv/**/ORA_FND_APP_STANDARD_LOOKUP_CODE.csv',recursive=True)[0]
rows=[r for r in csv.DictReader(open(f,encoding='utf-8-sig')) if r['FND_APP_STANDARD_LOOKUP.LookupType']=='ORA_DOO_ORDER_TYPES']
cols=list(rows[0].keys())
save(R+'/order_types_ETIA-TEST.xlsx','OrderTypes',cols,rows,['Pod ETIA-TEST, read-only.','Route: FSCR task-level FSM CSV export, task DOO_MANAGE_ORCHESTRATION_LOOKUPS (Manage Order Lookups), file ORA_FND_APP_STANDARD_LOOKUP_CODE.csv, filtered to lookup type ORA_DOO_ORDER_TYPES.','Cross-check: REST standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes returned the same count.'])
p=json.load(open(R+'/evidence/rest/pl_all.json',encoding='utf-8'))['items']
cols=[c for c in p[0] if c!='@context']
save(R+'/price_lists_ETIA-TEST.xlsx','PriceLists',cols,p,['Pod ETIA-TEST, read-only.','Route: REST GET /fscmRestApi/resources/11.13.18.05/priceLists (all pages). No FSM export exists for price lists (catalog flag N).'])
