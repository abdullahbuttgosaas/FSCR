"""Run 21: re-open the workbook and check it against Run 20 (13 ledgers, 37 BUs, AR options BUU1 + AMNA BU, 3 txn-type rows)
and against the raw sources. Writes evidence/check_results.json (local, read-only)."""
import json,sys,collections
from openpyxl import load_workbook
R=sys.argv[1]; wb=load_workbook(R+'/calendar_chain_workbook_ETIA-TEST.xlsx',read_only=True)
def rows(s):
    it=wb[s].iter_rows(values_only=True); h=next(it); return [dict(zip(h,r)) for r in it if r and r[0] not in (None,'(no rows)')]
G='GoSaaS MFG'; r20=json.load(open(R+'/../_fscr_run_20_cross_module_subject/evidence/deep_check.json'))['calendar_to_ar'][G]
out={'mismatches':[],'empty':[],'checks':[]}
def chk(name,got,exp):
    ok=got==exp; out['checks'].append({'check':name,'workbook':got,'expected':exp,'ok':ok})
    if not ok: out['mismatches'].append(f'{name}: workbook {got} vs expected {exp}')
L=[r for r in rows('Ledgers') if r['CalendarName']==G]; B=[r for r in rows('BusinessUnits') if r['CalendarName']==G]
A=[r for r in rows('ReceivablesOptions') if r['CalendarName']==G]; T=[r for r in rows('ReceivablesTxnTypes') if r['CalendarName']==G]
chk('Ledgers on GoSaaS MFG',len(L),13); chk('Ledger names = Run 20 list',sorted(r['LedgerName'] for r in L),sorted(r20['ledgers']))
chk('Business units on those ledgers',len(B),37)
chk('Receivables option BUs',sorted(r['BusinessUnitName'] for r in A),sorted(['BUU1','AMNA BU'])); chk('Receivables option BUs = Run 20',sorted(r['BusinessUnitName'] for r in A),sorted(b for b,_ in r20['ar_bus']))
chk('Receivables txn-type rows',len(T),3)
chk('Ledger IDs filled',sum(1 for r in rows('Ledgers') if not r['LedgerId']),0); chk('BU IDs filled',sum(1 for r in rows('BusinessUnits') if not r['BusinessUnitId']),0)
P=[r for r in rows('Periods') if r['CalendarName']==G]; chk('GoSaaS MFG periods = Run 20 count',len(P),r20['periods_defined'])
dec=[r for r in P if r['PeriodName']=='Dec-26']; chk('Dec-26 period present',[(r['StartDate'],r['EndDate']) for r in dec],[('2026/12/01','2026/12/31')])
S=[r for r in rows('PeriodStatus') if r['CalendarName']==G and r['PeriodName']=='Dec-26' and str(r['ApplicationId'])=='222']
out['dec26_receivables_status']=dict(collections.Counter(r['StatusMeaning'] for r in S)); chk('Dec-26 Receivables status rows (one per ledger)',len(S),13)
out['status_by_app_GoSaaS']={a:dict(collections.Counter(r['StatusMeaning'] for r in rows('PeriodStatus') if r['CalendarName']==G and str(r['ApplicationId'])==a)) for a in ('101','200','222')}
for s in wb.sheetnames:
    if s in ('README','Changes'): continue
    rr=rows(s); per=collections.Counter(r.get('CalendarName') for r in rr)
    for c in ('GoSaaS MFG','N24Ledger','GS Account'):
        if not per[c]: out['empty'].append(f'{s} / {c}')
out['changes_sheet_rows']=wb['Changes'].max_row-1
json.dump(out,open(R+'/evidence/check_results.json','w'),indent=1)
for c in out['checks']: print('OK ' if c['ok'] else 'BAD',c['check'],'|',str(c['workbook'])[:80])
print('MISMATCHES',out['mismatches']); print('EMPTY',out['empty']); print('Dec-26 AR status',out['dec26_receivables_status']); print('status by app',out['status_by_app_GoSaaS']); print('Changes rows',out['changes_sheet_rows'])
