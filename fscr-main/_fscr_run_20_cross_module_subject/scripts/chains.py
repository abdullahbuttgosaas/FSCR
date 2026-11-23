"""Run 20: trace cross-module chains in live ETIA-TEST data (Run 18 exports reused; local, read-only).
Chain 1: GL accounting calendar -> GL primary ledgers (PeriodSetName) -> business units (PrimaryLedgerName) -> Receivables system options (BUName)
Chain 2: GL conversion rate type -> Receivables system options (CrossCurrencyRateType) and GL ledger translation rate types
Chain 3: GL segment values -> Receivables system options account segments (LocationTaxAccountSegments)"""
import csv,glob,json,sys,collections
csv.field_size_limit(10**9); R=sys.argv[1]; E18=R+'/../_fscr_run_18_best_subject/evidence/exports/'
C=lambda t,n: list(csv.DictReader(open(glob.glob(E18+f'{t}/csv/**/{n}',recursive=True)[0],encoding='utf-8-sig')))
led=C('GL_MANAGE_PRIMARY_LEDGERS','GL_PRIMARY_LEDGER.csv'); bu=C('FUN_MANAGE_BUSINESS_UNIT','FUN_BUSINESS_UNIT.csv')
so=C('AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS','AR_SYSTEM_OPTIONS.csv')
out={}
# chain 1
cal=collections.defaultdict(lambda:{'ledgers':[],'bus':[],'ar_option_bus':[]})
l2c={l['Name']:l['PeriodSetName'] for l in led}
for l in led: cal[l['PeriodSetName']]['ledgers'].append(l['Name'])
for b in bu:
    c=l2c.get(b['PrimaryLedgerName'])
    if c: cal[c]['bus'].append(b['Name'])
so_bus={s['BUName']:s for s in so}
for c,v in cal.items(): v['ar_option_bus']=[b for b in v['bus'] if b in so_bus]
# also: AR options LedgerName -> calendar (second path, no BU hop)
for s in so:
    c=l2c.get(s['LedgerName']); s['_cal']=c
out['chain1']={c:{'ledgers':len(v['ledgers']),'bus':len(v['bus']),'ar_option_bus':v['ar_option_bus'],'ledger_names':v['ledgers'][:12]} for c,v in sorted(cal.items(),key=lambda kv:(len(kv[1]['ar_option_bus']),len(kv[1]['bus'])),reverse=True)}
out['chain1_ar_options_ledger_check']=[{'BU':s['BUName'],'LedgerName':s['LedgerName'],'calendar':s['_cal']} for s in so]
# chain 2
out['chain2_ar']=dict(collections.Counter(s['CrossCurrencyRateType'] or '(blank)' for s in so))
out['chain2_ar_bus_corporate']=[s['BUName'] for s in so if s['CrossCurrencyRateType']=='Corporate']
out['chain2_gl']=[{'ledger':l['Name'],'avg':l['PeriodAverageRateTypeTrans'],'end':l['PeriodEndRateTypeTrans']} for l in led if l['PeriodAverageRateTypeTrans'] or l['PeriodEndRateTypeTrans']]
# chain 3
seg=collections.Counter(); segrows=collections.defaultdict(list)
for s in so:
    vals=[v.strip() for v in s['LocationTaxAccountSegments'].split('\n') if v.strip()]
    for i,v in enumerate(vals): seg[(i+1,v)]+=1; segrows[(i+1,v)].append(s['BUName'])
out['chain3_segments']={f'segment{k[0]}={k[1]}':c for k,c in seg.most_common(12)}
json.dump(out,open(R+'/evidence/chains.json','w'),indent=1)
for k,v in out.items(): print('##',k); print('  ',json.dumps(v)[:1400])
