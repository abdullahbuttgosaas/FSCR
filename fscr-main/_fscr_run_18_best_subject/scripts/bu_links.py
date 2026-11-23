"""Run 18: per-business-unit link counts across the BU export and REST reads (local, read-only)."""
import csv,glob,json,collections,sys
csv.field_size_limit(10**9); R=sys.argv[1]; E=R+'/evidence/'
def C(n): return list(csv.DictReader(open(glob.glob(E+'exports/FUN_MANAGE_BUSINESS_UNIT/csv/**/'+n,recursive=True)[0],encoding='utf-8-sig')))
bu=C('FUN_BUSINESS_UNIT.csv'); use=C('FUN_BU_USAGE.csv'); sp=C('FUN_BU_SERVICE_PROVIDERS.csv'); sa=C('LE_1214416713655.csv')
pl=json.load(open(E+'rest/price_lists.json',encoding='utf-8'))['items']; da=json.load(open(E+'rest/data_access.json',encoding='utf-8'))['items']
code={b['Name']:b['OrganizationCode'] for b in bu}
f=collections.Counter(u['FUN_BUSINESS_UNIT.Name'] for u in use)
s=collections.Counter(); [s.update([x['ClientBuName'],x['ProviderBuName']]) for x in sp]
a=collections.Counter(code_to for code_to in (x['OrganizationCode'] for x in sa)); inv={v:k for k,v in code.items()}
p=collections.Counter(x.get('BusinessUnit') for x in pl); d=collections.Counter(x.get('SecurityContextValue') for x in da if x.get('SecurityContext')=='Business unit')
rows=[]
for b in bu:
    n=b['Name']; rows.append(dict(bu=n,status=b['Status'],default_set=b['DefaultSetCode'],ledger=b['PrimaryLedgerName'],le=b['LegalEntityName'],currency=b['DefaultCurrencyCode'],
      functions=f[n],service_provider_links=s[n],set_assignments=a[b['OrganizationCode']],price_lists=p[n],data_access=d[n]))
for r in rows: r['link_types']=sum(1 for k in ('functions','service_provider_links','set_assignments','price_lists','data_access') if r[k])+bool(r['ledger'])+bool(r['le'])
rows.sort(key=lambda r:(r['link_types'],r['price_lists']+r['functions']),reverse=True)
json.dump(rows,open(E+'bu_links.json','w'),indent=1)
print('totals: BUs',len(bu),'| statuses',dict(collections.Counter(b['Status'] for b in bu)),'| default sets',collections.Counter(b['DefaultSetCode'] for b in bu).most_common(4))
print('functions rows',len(use),'module ids',len({u['ModuleId'] for u in use}),'| service-provider rows',len(sp),'| set assignment rows',len(sa))
for r in rows[:8]: print(r)
