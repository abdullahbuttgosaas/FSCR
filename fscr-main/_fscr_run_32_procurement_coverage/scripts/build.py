# Run 32: Procurement tasks. Read-only. Same inputs/definitions as Run 29.
import json,csv,collections,os,sys
base=sys.argv[1]; out=os.path.join(base,'_fscr_run_32_procurement_coverage')
cat=os.path.join(base,'fscr-main/knowledge/setup-task-catalog/effective')
o=json.load(open(os.path.join(cat,'offering-functional-area-task-catalog.json'),encoding='utf-8'))['offerings']
inv={x['TaskCode']:x for x in csv.DictReader(open(os.path.join(base,'_fscr_run_07_inventory/out/tasks.csv'),encoding='utf-8'))}
r29={x['task_code'] for x in csv.DictReader(open(os.path.join(base,'_fscr_run_29_common_features/common_features_tasks.csv'),encoding='utf-8'))}
# in-scope areas (catalog functionalAreaShortName -> tag). Tag is MY area-level mapping (not from a tracker file).
SCOPE={'ORA_PO_PURCHASING_FOUNDATION':'Purchasing','ORA_PO_PURCHASING_CAT_FA':'Purchasing','ORA_EXTERNAL_PURCHASE_PRICES':'Purchasing',
 'ORA_PO_PROC_FOUNDATION_FA':'Procurement','ORA_PO_APPROVAL_MANAGEMENT_FA':'Procurement','ORA_PO_PRC_TRX_ACC_RULES_FA':'Procurement',
 'PO_SSP_DEPLOYED':'Procurement','OKC_PROC_CONTRACTS_ENABLED':'Procurement','ORA_PO_COMPLIANCE_CHECKLISTS_FA':'Procurement',
 'ORA_EGP_SUPPLIERS':'Sourcing and Supplier Management','PO_SOURCING_DEPLOYED':'Sourcing and Supplier Management',
 'ORA_PO_QUALIFICATION_DEPLOYED':'Sourcing and Supplier Management','PO_SUP_PORTAL_DEPLOYED':'Sourcing and Supplier Management'}
# borderline areas NOT in scope (reported only in area_counts.csv as sensitivity)
BORDER=['ORA_EGP_FA_ITEMS','WSH_ENABLE_RECEIVING','CMR_RECEIPT_ACCOUNTING','ORA_CJM_SUPPLIER_INCENTIVES','ORA_SUS_SUSTAINABILITY','ORA_EGP_SUPPLIER_FOR_PIM','FIN_PAYABLES_DEPLOYED']
def collect(areas):
    t=collections.OrderedDict()
    for osn,off in o.items():
        for fsn,f in off['functionalAreas'].items():
            if fsn in areas:
                for k in f['tasks']:
                    d=t.setdefault(k['taskShortName'],dict(name=k['taskName'],areas={},offs=set()))
                    d['areas'][fsn]=f['functionalAreaName']; d['offs'].add(off['offeringName'])
    return t
def routes(x): return [s.strip() for s in x['Route(s) declared'].split(',') if s.strip() and s.strip()!='-']
def level(x):
    if x['Skill']!='none': return 'a'
    return 'b' if x['CSV export/import (catalog)']=='Y' else 'c'
def row(code,d,tagmap):
    x=inv[code]; rt=routes(x); sk=x['Skill']!='none'
    tags={tagmap[a] for a in d['areas'] if a in tagmap}
    tag=tags.pop() if len(tags)==1 else 'Shared'
    return {'task':d['name'],'task_code':code,'functional_area':'; '.join(d['areas'].values()),'row_tag':tag,'level':level(x),
      'skill_or_guide':x['Skill'],'csv_flag':x['CSV export/import (catalog)'],'routes_declared':x['Route(s) declared'],
      'skill_but_no_csv_rest_route':'Y' if sk and not set(rt)&{'FSM_CSV','REST'} else 'N','offerings':'; '.join(sorted(d['offs']))}
t=collect(SCOPE); dup=[c for c in t if c in r29]
rows=[row(c,d,SCOPE) for c,d in t.items() if c not in r29]
rows.sort(key=lambda r:(r['row_tag'],r['functional_area'],r['task']))
with open(os.path.join(out,'procurement_tasks.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def cnt(rs):
    c=collections.Counter(r['level'] for r in rs)
    return [len(rs),c['a'],c['b'],c['c'],sum(r['skill_but_no_csv_rest_route']=='Y' for r in rs),c['b']+c['c'],'%d/%d'%(c['b']+c['c'],len(rs))]
hdr=['group','in_scope','tasks','a_skill_and_route','b_route_no_skill','c_neither','a_but_skill_names_no_csv_rest_route','missing_no_skill','missing_N_of_total']
res=[]
for fsn,tg in SCOPE.items():
    rs=[r for r in rows if r['functional_area'].split('; ')[0]==o['PO_PROCUREMENT']['functionalAreas'][fsn]['functionalAreaName'] or o['PO_PROCUREMENT']['functionalAreas'][fsn]['functionalAreaName'] in r['functional_area'].split('; ')]
    res.append([o['PO_PROCUREMENT']['functionalAreas'][fsn]['functionalAreaName']+' ['+tg+']','Y']+cnt(rs))
for tg in ['Procurement','Sourcing and Supplier Management','Purchasing','Shared']:
    res.append(['TAG '+tg,'Y']+cnt([r for r in rows if r['row_tag']==tg]))
res.append(['ROW Procurement (SCM 24) = Procurement + Shared','Y']+cnt([r for r in rows if r['row_tag'] in('Procurement','Shared')]))
res.append(['ALL in-scope unique tasks','Y']+cnt(rows))
tb=collect(BORDER)
for fsn in BORDER:
    nm=[f['functionalAreas'][fsn]['functionalAreaName'] for f in o.values() if fsn in f['functionalAreas']][0]
    ds={c:d for c,d in tb.items() if fsn in d['areas'] and c not in r29 and c not in t}
    res.append([nm+' (borderline, not counted)','N']+cnt([row(c,d,{fsn:'x'}) for c,d in ds.items()]))
with open(os.path.join(out,'area_counts.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(hdr); w.writerows(res)
for r in res: print(r)
print('dup removed (in Run 29):',len(dup),dup)
print('multi-area',[(r['task_code'],r['functional_area']) for r in rows if ';' in r['functional_area']][:50])
print('skill no route list',[r['task_code'] for r in rows if r['skill_but_no_csv_rest_route']=='Y'])
print('missing inv',[c for c in t if c not in inv])
