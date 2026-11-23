"""Run 22 step 1: apply the 2 test edits to a COPY of the EDIT workbook (local file only, nothing sent to Oracle)
and log each changed cell in the Changes sheet. Output: calendar_chain_workbook_ETIA-TEST_EDITED.xlsx"""
import sys
from openpyxl import load_workbook
R=sys.argv[1]; wb=load_workbook(R+'/calendar_chain_workbook_ETIA-TEST_EDIT.xlsx')
EDITS=[('1','GoSaaS MFG'),('2','GS Account')]; log=[]
def hdr(ws): return {c.value:i for i,c in enumerate(ws[1],1)}
for chg,cal in EDITS:
    for sname,old,new in (('Periods','2026/12/31','2026/12/24'),('PeriodStatus','2026-12-31','2026-12-24')):
        ws=wb[sname]; h=hdr(ws); pcol='PeriodName'
        for r in range(2,ws.max_row+1):
            if ws.cell(r,h['CalendarName']).value==cal and ws.cell(r,h[pcol]).value=='Dec-26':
                c=ws.cell(r,h['EndDate']); assert c.value==old,(sname,r,c.value)
                c.value=new
                key=f"{cal} | Dec-26" if sname=='Periods' else f"{cal} | {ws.cell(r,h['LedgerName']).value} | app {ws.cell(r,h['ApplicationId']).value} | Dec-26"
                log.append((sname,f'Change {chg}: {key} (row {r})','EndDate',old,new))
ch=wb['Changes']
for l in log: ch.append(list(l))
wb.save(R+'/calendar_chain_workbook_ETIA-TEST_EDITED.xlsx')
from collections import Counter
print('logged',len(log),Counter((l[0],l[1].split(':')[0]) for l in log))
