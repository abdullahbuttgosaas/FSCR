# Run 29: Common Features tasks. Read-only. Inputs: FSCR catalog (effective) + Run 07 tasks.csv.
import json,csv,collections,os,sys
base=sys.argv[1]; out=os.path.join(base,'_fscr_run_29_common_features')
cat=os.path.join(base,'fscr-main/knowledge/setup-task-catalog/effective')
o=json.load(open(os.path.join(cat,'offering-functional-area-task-catalog.json'),encoding='utf-8'))['offerings']
pm={i['offeringShortName']:i['pillar'] for i in json.load(open(os.path.join(cat,'pillars-offerings-mapping.json'),encoding='utf-8'))['items']}
inv={x['TaskCode']:x for x in csv.DictReader(open(os.path.join(base,'_fscr_run_07_inventory/out/tasks.csv'),encoding='utf-8'))}
AREAS=['Initial Users','Enterprise Profile','Legal Structures','Financial Reporting Structures','Organization Structures','Workforce Structures','Users and Security','Application Extensions']
t=collections.OrderedDict()
for osn,off in o.items():
    if pm.get(osn)!='ERP': continue
    for fsn,f in off['functionalAreas'].items():
        if not fsn.startswith('ORA_ASK_'): continue
        for k in f['tasks']:
            d=t.setdefault(k['taskShortName'],dict(name=k['taskName'],areas=set(),offs=set(),csvcat=set(),eicat=set()))
            d['areas'].add(f['functionalAreaName']); d['offs'].add(off['offeringName'])
            d['csvcat'].add(k.get('csvExportImportSupportedFlag')); d['eicat'].add(k.get('exportImportSupportedFlag'))
def routes(x): return [s.strip() for s in x['Route(s) declared'].split(',') if s.strip() and s.strip()!='-']
def level(x):
    if x['Skill']!='none': return 'Route + instructions'
    return 'Route, no instructions' if x['CSV export/import (catalog)']=='Y' else 'No route, no instructions'
rows=[]
for code,d in t.items():
    x=inv[code]; rt=routes(x); sk=x['Skill']!='none'
    rows.append({'task_code':code,'task_name':d['name'],
      'functional_areas':'; '.join(a for a in AREAS if a in d['areas']),
      'erp_offerings':'; '.join(sorted(d['offs'])),
      'financials_offering':'Y' if 'Financials' in d['offs'] else 'N',
      'run07_area':x['Area'],
      'skill_or_guide':x['Skill'],'skill_paths':x['Skill paths'],
      'csv_flag':x['CSV export/import (catalog)'],
      'rest_flag':('Y (skill declares REST)' if 'REST' in rt else ('N (skill names no REST)' if sk else 'not scanned (no skill)')),
      'routes_declared':x['Route(s) declared'],
      'level':level(x),
      'skill_names_no_csv_rest_route':'Y' if sk and not set(rt)&{'FSM_CSV','REST'} else 'N',
      'level_under_438_definition':('No route (skill names no CSV/REST)' if sk and not set(rt)&{'FSM_CSV','REST'} else level(x)),
      'run07_status':x['Status'],'tested_in_our_runs':x['Tested in our runs'] or x['Run 04 result']})
rows.sort(key=lambda r:(AREAS.index(r['functional_areas'].split('; ')[0]),r['task_name']))
with open(os.path.join(out,'common_features_tasks.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
L=['Route + instructions','Route, no instructions','No route, no instructions']
def cnt(rs,fin=False):
    c=collections.Counter(r['level'] for r in rs); n=sum(r['skill_names_no_csv_rest_route']=='Y' for r in rs)
    return [len(rs)]+[c[l] for l in L]+[n, n+c['No route, no instructions']]
hdr=['area','tasks']+L+['skill_but_no_csv_rest_route','no_route_under_438_def']
res=[]
for a in AREAS: res.append([a]+cnt([r for r in rows if a in r['functional_areas'].split('; ')]))
res.append(['ALL (unique tasks)']+cnt(rows))
res.append(['Financials offering only (unique)']+cnt([r for r in rows if r['financials_offering']=='Y']))
with open(os.path.join(out,'area_counts.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(hdr); w.writerows(res)
for r in res: print(r)
print(collections.Counter(r['run07_area'] for r in rows))
print('multi-area tasks',sum(';' in r['functional_areas'] for r in rows))
