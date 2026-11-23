"""Run 20: exact rows for each of the top 3 chains (B setup -> link Y -> A rows). Local, read-only."""
import csv,glob,json,sys,collections
csv.field_size_limit(10**9); R=sys.argv[1]; E20=R+'/evidence/exports/'; E18=R+'/../_fscr_run_18_best_subject/evidence/exports/'
def C(base,t,n): return list(csv.DictReader(open(glob.glob(base+f'{t}/csv/**/{n}',recursive=True)[0],encoding='utf-8-sig')))
rt=C(E20,'GL_MANAGE_CONVERSION_RATE_TYPES','GL_DAILY_CONVERSION_TYPE.csv'); rr=C(E20,'GL_MANAGE_CONVERSION_RATE_TYPES','ORA_GL_CONVERSION_RATE_RULE.csv')
ps=C(E20,'GL_MANAGE_ACCOUNTING_CALENDARS','GL_PERIOD_SET.csv'); pd=C(E20,'GL_MANAGE_ACCOUNTING_CALENDARS','GL_PERIOD_DEF.csv')
vs=C(E20,'GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SET_VALUES','ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv')
led=C(E18,'GL_MANAGE_PRIMARY_LEDGERS','GL_PRIMARY_LEDGER.csv'); so=C(E18,'AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS','AR_SYSTEM_OPTIONS.csv')
o={}
# chain 2: rate type
o['rate_types']=[{k:r[k] for k in ('UserConversionType','Description') } for r in rt]
corp=[r for r in rt if r['UserConversionType']=='Corporate']; o['corporate_row']=corp
o['corporate_rate_rules']=[r for r in rr if r['GL_DAILY_CONVERSION_TYPE.UserConversionType']=='Corporate']
o['ar_options_using_corporate']=[{'BU':s['BUName'],'Ledger':s['LedgerName']} for s in so if s['CrossCurrencyRateType']=='Corporate']
o['gl_ledgers_using_corporate']=[l['Name'] for l in led if 'Corporate' in (l['PeriodAverageRateTypeTrans'],l['PeriodEndRateTypeTrans'])]
o['ar_option_rate_types_not_in_export']=sorted({s['CrossCurrencyRateType'] for s in so if s['CrossCurrencyRateType']} - {r['UserConversionType'] for r in rt})
# chain 1: calendar
l2c={l['Name']:l['PeriodSetName'] for l in led}
by=collections.defaultdict(list)
for s in so: by[l2c.get(s['LedgerName'],'?')].append((s['BUName'],s['LedgerName']))
o['calendars']=len(ps)
o['calendar_to_ar']={c:{'ledgers':[l['Name'] for l in led if l['PeriodSetName']==c],'ar_bus':v,'periods_defined':sum(1 for p in pd if p['PeriodSetName']==c),'in_calendar_export':any(p['PeriodSetName']==c for p in ps)} for c,v in by.items()}
# chain 3: segment values used in AR options account segments
seg=collections.Counter(); where=collections.defaultdict(set)
for s in so:
    for i,v in enumerate([x.strip() for x in s['LocationTaxAccountSegments'].split('\n') if x.strip()]): seg[v]+=1; where[v].add(s['BUName'])
val=collections.defaultdict(list)
for v in vs: val[v['Value']].append((v['FND_APP_FLEX_VALUE_SET.ValueSetCode'],v['EnabledFlag'],v['EndDateActive']))
o['segment_values']={v:{'ar_rows':c,'value_sets':val.get(v,[])} for v,c in seg.most_common(10)}
json.dump(o,open(R+'/evidence/deep_check.json','w'),indent=1)
for k,v in o.items(): print('##',k,'|',json.dumps(v)[:900])
