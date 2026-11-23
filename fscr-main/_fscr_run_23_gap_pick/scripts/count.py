# Run 23: re-count from Run 07 tasks.csv (built from FSCR catalog setupTasksAll.json). Read-only.
import json
import csv,collections,sys,os
base=sys.argv[1]
r=list(csv.DictReader(open(os.path.join(base,'_fscr_run_07_inventory/out/tasks.csv'),encoding='utf-8')))
def routes(x): return set(s.strip() for s in x['Route(s) declared'].split(',') if s.strip() and s.strip()!='-')
def area(x): return x['Area'] if x['Area'] in ('ERP','SCM','HCM','CX') else 'Other'
def cls(x):
    sk=x['Skill']!='none'; csvy=x['CSV export/import (catalog)']=='Y'
    if sk: return 'skill_route' if routes(x)&{'FSM_CSV','REST'} else 'skill_noroute'
    return 'route_only' if csvy else 'noskill_noroute'
rows=[];tot=collections.Counter()
for a in ['ERP','SCM','HCM','CX','Other']:
    t=[x for x in r if area(x)==a]; c=collections.Counter(cls(x) for x in t)
    row=dict(area=a,total=len(t),with_skill_or_guide=c['skill_route']+c['skill_noroute'],
      skill_but_no_csv_rest_route=c['skill_noroute'],route_only_csv_no_skill=c['route_only'],
      no_skill_no_route=c['noskill_noroute'],no_standard_route_total=c['skill_noroute']+c['noskill_noroute'])
    rows.append(row); tot.update({k:v for k,v in row.items() if k!='area'})
rows.append(dict(area='Total',**tot))
out=os.path.join(base,'_fscr_run_23_gap_pick')
with open(os.path.join(out,'area_counts.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for x in rows: print(x)
# ERP/SCM gap list
def module(code):
    p=code.split('_')[0]; return p
g=[x for x in r if area(x) in('ERP','SCM') and cls(x)!='skill_route']
with open(os.path.join(out,'gaps_erp_scm.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Area','CodePrefix','TaskCode','TaskName','GapType','CSVflag','RoutesDeclared'])
    for x in sorted(g,key=lambda x:(area(x),x['TaskCode'])):
        w.writerow([area(x),module(x['TaskCode']),x['TaskCode'],x['TaskName'],cls(x),x['CSV export/import (catalog)'],x['Route(s) declared']])
for a in('ERP','SCM'):
    c=collections.Counter((module(x['TaskCode']),cls(x)) for x in g if area(x)==a)
    m=collections.defaultdict(dict)
    for (p,k),v in c.items(): m[p][k]=v
    print(a,len([x for x in g if area(x)==a]))
    for p,d in sorted(m.items(),key=lambda i:-sum(i[1].values())): print(' ',p,d)

# --- module = functional area name(s) from offering-functional-area-task-catalog, offerings in the same pillar
cat=os.path.join(base,'fscr-main/knowledge/setup-task-catalog/effective')
o=json.load(open(os.path.join(cat,'offering-functional-area-task-catalog.json'),encoding='utf-8'))['offerings']
pm={i['offeringShortName']:(i['pillar'],i['offeringName']) for i in json.load(open(os.path.join(cat,'pillars-offerings-mapping.json'),encoding='utf-8'))['items']}
fa=collections.defaultdict(list)
for osn,off in o.items():
    pil,on=pm.get(osn,('Unmapped',off.get('offeringName')))
    for fsn,f in off.get('functionalAreas',{}).items():
        for t in f.get('tasks',[]):
            fa[t['taskShortName']].append((pil,on,f['functionalAreaName']))
def mod(x):
    a=area(x); l=[i for i in fa.get(x['TaskCode'],[]) if i[0]==a] or fa.get(x['TaskCode'],[])
    if not l: return ('(none)','(none)')
    c=collections.Counter((i[1],i[2]) for i in l).most_common(1)[0][0]; return c
with open(os.path.join(out,'gaps_erp_scm.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Area','Offering','Module (functional area)','TaskCode','TaskName','GapType','CSVflag','RoutesDeclared'])
    for x in sorted(g,key=lambda x:(area(x),mod(x),x['TaskCode'])):
        w.writerow([area(x),*mod(x),x['TaskCode'],x['TaskName'],cls(x),x['CSV export/import (catalog)'],x['Route(s) declared']])
with open(os.path.join(out,'gaps_by_module.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Area','Module (functional area)','route_only_csv_no_skill','no_skill_no_route','skill_but_no_csv_rest_route','total_gaps'])
    for a in ('ERP','SCM'):
        m=collections.defaultdict(collections.Counter)
        for x in g:
            if area(x)==a: m[mod(x)[1]][cls(x)]+=1
        for k,c in sorted(m.items(),key=lambda i:-sum(i[1].values())):
            w.writerow([a,k,c['route_only'],c['noskill_noroute'],c['skill_noroute'],sum(c.values())])
