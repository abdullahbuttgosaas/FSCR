"""Build an FSM CSV ZIP that adds ONE new context (with ONE context-sensitive segment) to an existing
descriptive flexfield. GoSaaS helper, not official FSCR. Standard library only. Offline.

The flexfield's parent row is copied UNCHANGED from the task export (a child row is processed only
when its parent is in the same ZIP). Every other file of the package is written header only.
Refuses a context or segment code that does not start with --prefix, a context that already exists,
and a column already used by a global segment of the flexfield.

python -I dff_context_package.py --export-dir EXP/unz --dff FND_ATTACHED_DOCUMENTS --prefix GAPFILL_XX_ \
   --context GAPFILL_XX_CTX1 --segment GAPFILL_XX_SEG1 --column ATTRIBUTE3 --value-set "Text 150" \
   --enabled N --out-dir pay --zip-name dff.zip
"""
import argparse, csv, glob, io, os, re, sys, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('--export-dir', required=True)
ap.add_argument('--dff', required=True)
ap.add_argument('--prefix', required=True)
ap.add_argument('--context', required=True)
ap.add_argument('--segment', required=True)
ap.add_argument('--column', required=True)
ap.add_argument('--value-set', required=True)
ap.add_argument('--enabled', default='N', choices=['Y', 'N'])
ap.add_argument('--out-dir', required=True)
ap.add_argument('--zip-name', required=True)
ap.add_argument('--parent-json', help='REST descriptiveFlexfields JSON with the parent row, used only when '
                'the export has no row for --dff')
a = ap.parse_args()

for v in (a.context, a.segment):
    if not v.startswith(a.prefix):
        sys.exit(f'refused: {v} does not start with {a.prefix}')
if len(a.segment) > 30:
    sys.exit('refused: segment code longer than 30 characters')


def ident(code):  # API-style identifier: letters and digits, first word lower case
    parts = [p for p in re.split(r'[^A-Za-z0-9]+', code) if p]
    return (parts[0].lower() + ''.join(p.capitalize() for p in parts[1:]))[:30]


def read(name):
    p = os.path.join(a.export_dir, name)
    with open(p, encoding='utf-8-sig', newline='') as f:
        r = csv.reader(f)
        rows = list(r)
    return rows[0], [dict(zip(rows[0], x)) for x in rows[1:]]


files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(a.export_dir, '*.csv')))
need = ['FND_APP_DESCRIPTIVE_FLEXFIELD.csv', 'ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv',
        'ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv', 'ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv']
for n in need:
    if n not in files:
        sys.exit(f'refused: {n} missing in the export')
hdr = {n: read(n)[0] for n in files}
data = {n: read(n)[1] for n in files}
P = 'FND_APP_DESCRIPTIVE_FLEXFIELD.'
parents = [r for r in data['FND_APP_DESCRIPTIVE_FLEXFIELD.csv'] if r['DescriptiveFlexfieldCode'] == a.dff]
if not parents and a.parent_json:  # flexfield with no user context yet: parent row read live by REST
    import json
    items = [i for i in json.load(open(a.parent_json, encoding='utf-8')).get('items', [])
             if i.get('DescriptiveFlexfieldCode') == a.dff]
    if len(items) != 1:
        sys.exit(f'refused: {a.parent_json} holds {len(items)} rows for {a.dff}')
    parents = [{k: ('' if items[0].get(k) is None else str(items[0][k]))
                for k in ('DescriptiveFlexfieldCode', 'ApplicationId', 'Name', 'Description', 'Delimiter')}]
    print(f'parent row of {a.dff} taken from {os.path.basename(a.parent_json)} (REST read)')
if len(parents) != 1:
    sys.exit(f'refused: flexfield {a.dff} found {len(parents)} times in FND_APP_DESCRIPTIVE_FLEXFIELD.csv '
             '(the export holds only flexfields that already have user contexts or segments)')
parent = parents[0]
if any(r[P + 'DescriptiveFlexfieldCode'] == a.dff and r['ContextCode'] == a.context
       for r in data['ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv']):
    sys.exit(f'refused: context {a.context} already exists')
used = [r['ColumnName'] for r in data['ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv']
        if r[P + 'DescriptiveFlexfieldCode'] == a.dff]
if a.column in used:
    sys.exit(f'refused: column {a.column} is used by a global segment of {a.dff}')

key = {P + 'DescriptiveFlexfieldCode': a.dff, P + 'ApplicationId': parent['ApplicationId']}
out = {n: [] for n in files}
out['FND_APP_DESCRIPTIVE_FLEXFIELD.csv'] = [parent]  # unchanged
out['ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv'] = [dict(key, ContextCode=a.context,
    ContextIdentifier=ident(a.context), Name=a.context, Description='Test context ' + a.context, EnabledFlag=a.enabled)]
out['ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv'] = [dict(key, **{
    'ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.ContextCode': a.context,
    'SegmentCode': a.segment, 'SegmentIdentifier': ident(a.segment), 'ColumnName': a.column,
    'Name': a.segment, 'Prompt': a.segment, 'ShortPrompt': a.segment[:30], 'SequenceNumber': '10',
    'EnabledFlag': 'Y', 'DisplayType': 'TEXT_BOX', 'RequiredFlag': 'N', 'ReadOnlyFlag': 'N',
    'BIEnabledFlag': 'N', 'IndexedFlag': 'N', 'ShowValueDescription': 'N', 'ValueSetCode': a.value_set})]

os.makedirs(a.out_dir, exist_ok=True)
zp = os.path.join(a.out_dir, a.zip_name)
meta = os.path.join(a.export_dir, 'ASM_SETUP_CSV_METADATA.xml')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in files:
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=hdr[n], quoting=csv.QUOTE_ALL, lineterminator='\r\n', extrasaction='raise')
        w.writeheader()
        for r in out[n]:
            w.writerow({k: r.get(k, '') for k in hdr[n]})
        z.writestr(n, buf.getvalue().encode('utf-8'))
        if out[n]:
            print(f'{n}: {len(out[n])} rows' + (' (parent, unchanged)' if n == 'FND_APP_DESCRIPTIVE_FLEXFIELD.csv' else ''))
    if os.path.isfile(meta):
        z.write(meta, 'ASM_SETUP_CSV_METADATA.xml')
print('wrote ' + zp)
