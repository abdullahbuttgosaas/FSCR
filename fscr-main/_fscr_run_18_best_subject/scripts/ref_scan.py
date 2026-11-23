"""Run 17: scan every export CSV cell for references to order type codes and price list names/IDs (read-only, local)."""
import csv,glob,json,os,re,collections,sys
csv.field_size_limit(10**9)
B=sys.argv[1]
ot=[x['LookupCode'] for x in json.load(open(B+'/rest/ot_lookup_codes.json',encoding='utf-8'))['items']]
pl=json.load(open(B+'/rest/pl_all.json',encoding='utf-8'))['items']
plk=[x['PriceListName'] for x in pl]+[str(x['PriceListId']) for x in pl]
hits=collections.defaultdict(list); kw=collections.Counter()
for f in glob.glob(B+'/exports/*/csv/**/*.csv',recursive=True):
    task=f.replace(os.sep,'/').split('/exports/')[1].split('/')[0]; name=os.path.basename(f)
    for i,row in enumerate(csv.reader(open(f,encoding='utf-8-sig',errors='replace'))):
        if i==0: continue
        for c in row:
            if task=='DOO_MANAGE_ORCHESTRATION_LOOKUPS': continue
            for k in ot:
                if len(k)>3 and re.search(r'(?<![A-Za-z0-9_])'+re.escape(k)+r'(?![A-Za-z0-9_])',c): hits['OT:'+k].append(f'{task}/{name}#{i}')
            for k in plk:
                if k in c: hits['PL:'+k].append(f'{task}/{name}#{i}')
            for w in ('OrderTypeCode','ORDER_TYPE','TransactionTypeCode','PriceList','EBS','E-Business','OIC','integration'):
                if w.lower() in c.lower(): kw[(task,name,w)]+=1
json.dump({'hits':hits,'keyword_cells':{' | '.join(k):v for k,v in kw.items()}},open(B+'/ref_scan.json','w'),indent=1)
print('hits',{k:len(v) for k,v in hits.items()}); [print(' | '.join(k),v) for k,v in sorted(kw.items())]
