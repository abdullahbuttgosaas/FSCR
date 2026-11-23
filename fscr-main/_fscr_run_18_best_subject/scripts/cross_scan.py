"""Run 18: count rows in the AR/AP/GL exports that point to a business unit, a reference data set or a currency
(local, read-only). Matching is exact cell match, so names inside free text are not counted."""
import csv, glob, json, os, sys, collections
csv.field_size_limit(10**9)
R = sys.argv[1]; E = R + '/evidence/'
bu = list(csv.DictReader(open(glob.glob(E + 'exports/FUN_MANAGE_BUSINESS_UNIT/csv/**/FUN_BUSINESS_UNIT.csv', recursive=True)[0], encoding='utf-8-sig')))
bu_names = {b['Name'] for b in bu}
sets = {r['SetCode'] for r in json.load(open(E + 'rest/ref_sets.json', encoding='utf-8'))['items']}
curs = {r['CurrencyCode'] for r in json.load(open(E + 'rest/currencies.json', encoding='utf-8'))['items']}
TASKS = ['AR_MANAGE_RECEIVABLES_PAYMENT_TERMS', 'AP_MANAGE_PAYMENT_TERMS', 'AR_MANAGE_TRANSACTION_TYPES',
         'GL_MANAGE_PRIMARY_LEDGERS', 'AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS']
out = {}
for t in TASKS:
    zs = glob.glob(E + f'exports/{t}/*.zip')
    if not zs:
        out[t] = 'NO EXPORT'; continue
    d = E + f'exports/{t}/csv'; os.makedirs(d, exist_ok=True)
    import zipfile; zipfile.ZipFile(zs[0]).extractall(d)
    res = {'BU': collections.Counter(), 'SET': collections.Counter(), 'CUR': collections.Counter(), 'files': {}}
    for f in glob.glob(d + '/**/*.csv', recursive=True):
        rows = list(csv.DictReader(open(f, encoding='utf-8-sig', errors='replace')))
        res['files'][os.path.basename(f)] = len(rows)
        for row in rows:
            for col, v in row.items():
                if not v or col is None: continue
                if v in bu_names and ('bu' in col.lower() or 'business' in col.lower() or 'org' in col.lower()): res['BU'][(os.path.basename(f), col)] += 1; res.setdefault('ABD', 0); res['ABD'] += (v == 'ABD')
                if v in sets and 'set' in col.lower(): res['SET'][(os.path.basename(f), col)] += 1
                if v in curs and 'currenc' in col.lower(): res['CUR'][(os.path.basename(f), col)] += 1; res.setdefault('USD', 0); res['USD'] += (v == 'USD')
    out[t] = {k: ({' | '.join(a): b for a, b in v.items()} if isinstance(v, collections.Counter) else v) for k, v in res.items()}
json.dump(out, open(E + 'cross_scan.json', 'w'), indent=1)
for t, v in out.items():
    print('##', t); print('  ', v if isinstance(v, str) else {k: v[k] for k in v if k != 'files'}); print('   files', v['files'] if isinstance(v, dict) else '')
