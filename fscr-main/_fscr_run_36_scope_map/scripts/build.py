# Run 36: one scope map for the FSCR Module Test Tracker. Read-only, no network, no Oracle.
# Method inputs (official FSCR repo only):
#   fscr-main/knowledge/setup-task-catalog/effective/{setupTasksAll,offering-functional-area-task-catalog,pillars-offerings-mapping}.json
#   work/02_route_audit.out.json = Run 07's route audit script re-run on the repo in this folder (scripts/02_route_audit.py)
# Comparison/cross-check inputs only (not used to assign anything): Run 07 tasks.csv, Run 29 and Run 32 task CSVs.
# Usage: python build.py   (writes the CSVs into the run folder)
import collections, csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from rules import *

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(RUN)
CAT = os.path.join(BASE, 'fscr-main', 'knowledge', 'setup-task-catalog', 'effective')
load = lambda p: json.load(open(p, encoding='utf-8'))
items = load(os.path.join(CAT, 'setupTasksAll.json'))['items']
offs = load(os.path.join(CAT, 'offering-functional-area-task-catalog.json'))['offerings']
pm = {i['offeringShortName']: i['pillar'] for i in load(os.path.join(CAT, 'pillars-offerings-mapping.json'))['items']}
audit = load(os.path.join(RUN, 'work', '02_route_audit.out.json'))

# ---- catalog joins
t_areas = collections.defaultdict(set); t_offs = collections.defaultdict(set)
a_name, a_offs = {}, collections.defaultdict(set)
cf29 = set()
for osn, off in offs.items():
    for fsn, f in off['functionalAreas'].items():
        a_name[fsn] = f['functionalAreaName']; a_offs[fsn].add(osn)
        for k in f['tasks']:
            c = k['taskShortName']; t_areas[c].add(fsn); t_offs[c].add(osn)
            if pm.get(osn) == 'ERP' and fsn.startswith('ORA_ASK_'):
                cf29.add(c)

# ---- area -> row
def area_row(fsn):
    if fsn in AREA_OVERRIDE:
        return AREA_OVERRIDE[fsn] + ('area override',)
    if fsn.startswith('ORA_ASK_'):
        return (CF, 'ORA_ASK_ shared setup area (Run 29 rule)', 'ORA_ASK_')
    d = {OFFERING_DEFAULT[o] for o in a_offs[fsn] if o in OFFERING_DEFAULT}
    if not d:
        return (UNM, NO_ROW, 'offering default')
    rows = {r for r, _ in d}
    if len(rows) > 1:
        raise SystemExit(f'area {fsn} has conflicting offering defaults {d}; add an AREA_OVERRIDE')
    return (d.pop()[0], 'offering default: ' + '; '.join(sorted(r for _, r in {OFFERING_DEFAULT[o] for o in a_offs[fsn] if o in OFFERING_DEFAULT})), 'offering default')
AREA_ROW = {fsn: area_row(fsn) for fsn in a_name}

def family(code):
    p = code.split('_'); return p[1] if p[0] == 'ORA' and len(p) > 1 else p[0]

def fam_row(code, name):
    r = FAMILY.get(family(code))
    if r is None: return None
    if isinstance(r, list):
        for rx, row in r:
            if rx is None or re.search(rx, name, re.I): return row
    return r

def assign(code, name):
    areas = t_areas.get(code, set())
    if code in TASK_OVERRIDE:
        r, why = TASK_OVERRIDE[code]; return r, 'task override', why
    if code in cf29:
        return CF, 'Run 29 rule', 'in an ORA_ASK_ area of an ERP offering (Run 29 Common Features rule)'
    if any(a.startswith('ORA_ASK_') for a in areas):
        return CF, 'ORA_ASK_ (non-ERP offering)', 'in an ORA_ASK_ shared area of a non-ERP offering only'
    fr = fam_row(code, name)
    if fr is not None:
        return fr, 'family ' + family(code), FAMILY_REASON.get(fr, F)
    if not areas:
        return UNM, 'no offering', 'task is in no enabled offering and has no family rule'
    votes = collections.Counter(AREA_ROW[a][0] for a in areas)
    real = {r: n for r, n in votes.items() if r != UNM}
    if not real:
        return UNM, 'area vote', 'all its areas have no tracker row'
    top = max(real.values()); cands = [r for r in ORDER if real.get(r) == top]
    if family(code) == 'OKC' and OKC_TIE in cands: cands = [OKC_TIE]
    r = cands[0]
    why = 'area ' + '; '.join(sorted(a_name[a] for a in areas if AREA_ROW[a][0] == r))
    if len(real) > 1: why += f' (areas split {dict(real)}; most areas, tie by tracker order' + (', OKC tie -> Procurement' if family(code) == 'OKC' else '') + ')'
    return r, 'area vote', why

# ---- levels (Run 07 / Run 29 definitions, recomputed from the rebuilt route audit)
def route_label(rec):
    if rec['routes']: return rec['routes']
    if rec.get('manual'): return ['MANUAL_ONLY']
    if rec.get('unclear'): return ['UNCLEAR']
    return ['NONE_DECLARED']
by_task = collections.defaultdict(list)
for rec in audit['skills']:
    by_task[rec['task_code']].append(rec)

rows = []
for it in items:
    code, name = it['TaskCode'], it.get('TaskName', '')
    recs = by_task.get(code, [])
    kinds = {r['kind'] for r in recs}
    skill = ('both' if kinds == {'skill', 'task guide'} else 'SKILL.md' if kinds == {'skill'} else 'task guide only' if kinds else 'none')
    routes = sorted({x for r in recs for x in route_label(r)})
    flag = it.get('CSVExportImportSupportedFlag') or 'UNKNOWN'
    level = 'a' if recs else ('b' if flag == 'Y' else 'c')
    row, basis, why = assign(code, name)
    pillar = next((p for p, r in ROWS if r == row), '-')
    rows.append({'task_code': code, 'task_name': name,
        'functional_area': '; '.join(sorted(a_name[a] for a in t_areas.get(code, ()))) or '(no offering)',
        'offering': '; '.join(sorted(offs[o]['offeringName'] for o in t_offs.get(code, ()))) or '(no offering)',
        'tracker_pillar': pillar, 'tracker_row': row, 'level': level,
        'skill_but_no_route': 'Y' if recs and not set(routes) & {'FSM_CSV', 'REST'} else 'N',
        'skill_or_guide': skill, 'csv_flag': flag, 'routes_declared': ', '.join(routes) or '-',
        'assign_basis': basis, 'assign_reason': why,
        'skill_paths': ' | '.join(r['path'] for r in recs)})
rows.sort(key=lambda r: (ORDER.index(r['tracker_row']), r['functional_area'], r['task_name']))
def write(name, rs, hdr=None):
    with open(os.path.join(RUN, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=hdr or list(rs[0])); w.writeheader(); w.writerows(rs)
write('module_scope_map.csv', rows)

# ---- cross-check against Run 07 tasks.csv (must be identical in skill, CSV flag, routes)
r07 = {x['TaskCode']: x for x in csv.DictReader(open(os.path.join(BASE, '_fscr_run_07_inventory', 'out', 'tasks.csv'), encoding='utf-8'))}
mism = [r['task_code'] for r in rows if r['task_code'] not in r07 or r07[r['task_code']]['Skill'] != r['skill_or_guide']
        or r07[r['task_code']]['CSV export/import (catalog)'] != r['csv_flag']
        or set(r07[r['task_code']]['Route(s) declared'].split(', ')) - {'-'} != set(r['routes_declared'].split(', ')) - {'-'}]
print('tasks', len(rows), 'unique codes', len({r['task_code'] for r in rows}), '| Run 07 mismatches:', len(mism), mism[:5])

# ---- counts per row
def cnt(rs):
    c = collections.Counter(r['level'] for r in rs)
    return len(rs), c['a'], c['b'], c['c'], sum(r['skill_but_no_route'] == 'Y' for r in rs)
def coverage(n, a):
    if n == 0: return 'Unknown', 'no catalog task assigned to this row'
    if a == 0: return 'None', 'no task in this row has an FSCR skill or guide'
    pct = 100 * a / n
    if pct >= 75: return 'Full', f'{a}/{n} ({pct:.0f}%) tasks have a skill or guide (rule: >=75% = Full)'
    return 'Partial', f'{a}/{n} ({pct:.0f}%) tasks have a skill or guide (rule: 1-74% = Partial)'
out = []
for p, r in ROWS + [('-', UNM)]:
    rs = [x for x in rows if x['tracker_row'] == r]
    n, a, b, c, snr = cnt(rs); cov, cr = coverage(n, a) if r != UNM else ('-', 'not a tracker row')
    out.append({'pillar': p, 'row': r, 'total_tasks': n, 'a_skill_or_guide': a, 'b_route_no_skill': b, 'c_neither': c,
                'a_strict_skill_and_route': a - snr, 'skill_but_no_route': snr, 'missing_N_of_total': f'{b + c}/{n}',
                'proposed_coverage': cov, 'coverage_basis': cr})
n, a, b, c, snr = cnt(rows)
out.append({'pillar': 'ALL', 'row': 'All catalog tasks', 'total_tasks': n, 'a_skill_or_guide': a, 'b_route_no_skill': b, 'c_neither': c,
            'a_strict_skill_and_route': a - snr, 'skill_but_no_route': snr, 'missing_N_of_total': f'{b + c}/{n}', 'proposed_coverage': '-', 'coverage_basis': ''})
write('module_counts.csv', out)

# ---- area_to_row.csv (410 areas). tasks_assigned_here = tasks of the area whose final row equals the area row.
final = {r['task_code']: r['tracker_row'] for r in rows}
ar = []
for fsn in sorted(a_name, key=lambda f: a_name[f]):
    row, why, how = AREA_ROW[fsn]
    ts = [c for c in {k['taskShortName'] for o in offs.values() if fsn in o['functionalAreas'] for k in o['functionalAreas'][fsn]['tasks']}]
    moved = collections.Counter(final[c] for c in ts if final[c] != row)
    ar.append({'area_code': fsn, 'area': a_name[fsn], 'offerings': '; '.join(sorted(offs[o]['offeringName'] for o in a_offs[fsn])),
               'row': row, 'reason': f'{how}: {why}', 'area_tasks': len(ts), 'tasks_in_this_row': len(ts) - sum(moved.values()),
               'tasks_sent_elsewhere': '; '.join(f'{k} {v}' for k, v in moved.most_common()) or '-'})
write('area_to_row.csv', ar)

# ---- sensitivity.csv
sens = []
for kind, key, alt, note in SENSITIVITY:
    if kind == 'area':
        hit = [r for r in rows if r['task_code'] in {k['taskShortName'] for o in offs.values() if key in o['functionalAreas'] for k in o['functionalAreas'][key]['tasks']}
               and r['tracker_row'] == AREA_ROW[key][0]]
        label, chosen = a_name[key], AREA_ROW[key][0]
    elif kind == 'offering':
        tr = OFFERING_DEFAULT[key][0]
        hit = [r for r in rows if key in t_offs.get(r['task_code'], ()) and r['tracker_row'] == tr]
        label, chosen = offs[key]['offeringName'] + ' (offering)', tr
    elif kind == 'family':
        hit = [r for r in rows if r['assign_basis'] == 'family ' + key]; label = f'task family {key}_'
        chosen = '; '.join(sorted({r['tracker_row'] for r in hit})) or '-'
    elif kind == 'task':
        hit = [r for r in rows if r['task_code'] == key]; label = hit[0]['task_name']; chosen = hit[0]['tracker_row']
    else:
        hit = ([r for r in rows if r['assign_basis'] == 'no offering'] if key.startswith('no offering') else
               [r for r in rows if r['assign_basis'] == 'ORA_ASK_ (non-ERP offering)'] if key.startswith('ORA_ASK_') else
               [r for r in rows if r['task_code'].split('_')[0] in ('OKC',) and 'OKC tie' in r['assign_reason']])
        label = key; chosen = '; '.join(sorted({r['tracker_row'] for r in hit})) or '-'
    lv = collections.Counter(r['level'] for r in hit)
    sens.append({'kind': kind, 'key': key, 'name': label, 'tasks_affected': len(hit), 'chosen_row': chosen, 'alternative_row': alt,
                 'affected_a_b_c': f"{lv['a']}/{lv['b']}/{lv['c']}", 'note': note})
write('sensitivity.csv', sens)

# ---- comparison with filled rows (Run 29 / Run 32)
r29 = {x['task_code'] for x in csv.DictReader(open(os.path.join(BASE, '_fscr_run_29_common_features', 'common_features_tasks.csv'), encoding='utf-8'))}
p32 = list(csv.DictReader(open(os.path.join(BASE, '_fscr_run_32_procurement_coverage', 'procurement_tasks.csv'), encoding='utf-8')))
old = {CF: r29, PRC: {x['task_code'] for x in p32 if x['row_tag'] in ('Procurement', 'Shared')},
       SSM: {x['task_code'] for x in p32 if x['row_tag'] == 'Sourcing and Supplier Management'}}
byc = {r['task_code']: r for r in rows}
cmp_rows = []
for row, oset in old.items():
    nset = {c for c, r in byc.items() if r['tracker_row'] == row}
    for c in sorted(oset - nset):
        r = byc[c]; cmp_rows.append({'row': row, 'change': 'left the row', 'task_code': c, 'task_name': r['task_name'], 'now_in': r['tracker_row'],
                                    'level': r['level'], 'basis': r['assign_basis'], 'reason': r['assign_reason'], 'functional_area': r['functional_area']})
    for c in sorted(nset - oset):
        r = byc[c]; cmp_rows.append({'row': row, 'change': 'joined the row', 'task_code': c, 'task_name': r['task_name'], 'now_in': row,
                                    'level': r['level'], 'basis': r['assign_basis'], 'reason': r['assign_reason'], 'functional_area': r['functional_area']})
write('work/comparison_detail.csv', cmp_rows)
for row, oset in old.items():
    nset = {c for c, r in byc.items() if r['tracker_row'] == row}
    om = sum(byc[c]['level'] != 'a' for c in oset); nm = sum(byc[c]['level'] != 'a' for c in nset)
    print(f'{row}: old {len(oset)} ({om} missing) -> new {len(nset)} ({nm} missing); left {len(oset - nset)}, joined {len(nset - oset)}')
    print('   left to:', collections.Counter(byc[c]['tracker_row'] for c in oset - nset).most_common())
    print('   joined by basis:', collections.Counter(byc[c]['assign_basis'] for c in nset - oset).most_common())
sup = [x for x in p32 if x['row_tag'] == 'Sourcing and Supplier Management' and 'Suppliers' in x['functional_area'].split('; ') and byc[x['task_code']]['tracker_row'] != SSM]
print('Run 32 S&SM tasks listed under Suppliers that moved out:', len(sup), collections.Counter(byc[x['task_code']]['tracker_row'] for x in sup).most_common())
for r in out: print(r['pillar'], r['row'], r['total_tasks'], r['a_skill_or_guide'], r['b_route_no_skill'], r['c_neither'], r['skill_but_no_route'], r['missing_N_of_total'], r['proposed_coverage'])
print('basis counts', collections.Counter(r['assign_basis'].split(' ')[0] for r in rows))
