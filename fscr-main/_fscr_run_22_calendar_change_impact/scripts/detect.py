"""Run 22 step 2: (a) cell-by-cell diff EDITED vs BASELINE; (b) live (fresh REST) vs BASELINE for periods and period status.
Local compare only. Writes evidence/detect_results.json and evidence/diff_cells.csv"""
import sys,json,glob,csv,collections
from openpyxl import load_workbook
R=sys.argv[1]; B=R+'/../_fscr_run_21_calendar_workbook/calendar_chain_workbook_ETIA-TEST_BASELINE.xlsx'
wb_b=load_workbook(B,read_only=True); wb_e=load_workbook(R+'/calendar_chain_workbook_ETIA-TEST_EDITED.xlsx',read_only=True)
diff=[]; out={}
for s in wb_b.sheetnames:
    rb=list(wb_b[s].iter_rows(values_only=True)); re_=list(wb_e[s].iter_rows(values_only=True))
    if len(rb)!=len(re_): diff.append((s,'row count',len(rb),len(re_),'',''))
    h=rb[0]
    for i,(a,b) in enumerate(zip(rb,re_),1):
        for j,(x,y) in enumerate(zip(a,b)):
            if x!=y: diff.append((s,i,h[j] if j<len(h) else j,x,y,' | '.join(str(v) for v in a[:7])))
    for i in range(len(rb)+1,len(re_)+1): diff.append((s,i,'(new row)','',' | '.join(str(v) for v in re_[i-1]),''))
with open(R+'/evidence/diff_cells.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Sheet','Row','Column','Baseline','Edited','RowKeys']); w.writerows(diff)
out['edited_vs_baseline']={'cells_or_rows':len(diff),'by_sheet':dict(collections.Counter(d[0]+' | '+str(d[2]) for d in diff))}
# live vs baseline
def rows(s):
    it=wb_b[s].iter_rows(values_only=True); h=next(it); return [dict(zip(h,r)) for r in it]
nd=lambda v: str(v or '').replace('/','-')[:10]
per_b={(r['CalendarName'],r['PeriodName']):(nd(r['StartDate']),nd(r['EndDate']),str(r['AdjustmentPeriodFlag'])) for r in rows('Periods')}
per_l={}
for f in glob.glob(R+'/evidence/rest/live_periods_*.json'):
    for x in json.load(open(f,encoding='utf-8'))['items']:
        per_l[(x['PeriodSetNameId'],x['PeriodNameId'])]=(nd(x['StartDate']),nd(x['EndDate']),'Y' if x['AdjustmentPeriodFlag'] else 'N')
pm=[k for k in set(per_b)|set(per_l) if (per_b.get(k) or ('',)*3)[:2]!=(per_l.get(k) or ('',)*3)[:2]]
out['live_periods_vs_baseline']={'baseline':len(per_b),'live':len(per_l),'differences':sorted(map(list,pm))}
st_b={(str(r['LedgerId']),str(r['ApplicationId']),r['PeriodName']):(r['ClosingStatus'],nd(r['StartDate']),nd(r['EndDate'])) for r in rows('PeriodStatus')}
st_l={}
for f in glob.glob(R+'/evidence/rest/period_status/*.json'):
    for x in json.load(open(f,encoding='utf-8'))['items']:
        st_l[(str(x['LedgerId']),str(x['ApplicationId']),x['PeriodNameId'])]=(x['ClosingStatus'],nd(x['StartDate']),nd(x['EndDate']))
sm=[[*k,st_b.get(k),st_l.get(k)] for k in set(st_b)|set(st_l) if st_b.get(k)!=st_l.get(k)]
out['live_status_vs_baseline']={'baseline':len(st_b),'live':len(st_l),'differences':sm[:50],'n_diff':len(sm)}
json.dump(out,open(R+'/evidence/detect_results.json','w'),indent=1,default=str)
print(json.dumps(out,default=str)[:1500])
