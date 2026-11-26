"""Build an FSM CSV ZIP that creates ONE new HCM data role as a copy of an existing one
(same inherited job role, same security profiles), under a new name. GoSaaS helper, not official FSCR.
Offline, standard library only. Nothing of the source role is sent: only the new rows.

python -I copy_data_role.py --export-dir EXP/unz --source HCM_DATA_ROLE_TEST_DATA \
    --new GAPFILL_XX_DR1 --prefix GAPFILL_XX_ --out-dir pay --zip-name dr.zip

Rules: --new must start with --prefix, must not exist yet, at most 30 characters (GUESS limit kept short).
Copies the source parent row with DataRoleName, GroupingKey, AppRoleName, DataRoleIdResolverName = --new,
display name and descriptions = --new text; id columns (GeneratedDataRoleId, DataRoleId, BaseRoleId,
GenDataRoleProfileId, SecurityProfileId) are emptied. Profile rows: parent key and GroupingKey
'<new>,<securing object>'. Prints counts only.
"""
import argparse, csv, io, os, sys, zipfile

ap = argparse.ArgumentParser()
for a in ('--export-dir', '--source', '--new', '--prefix', '--out-dir', '--zip-name'):
    ap.add_argument(a, required=True)
a = ap.parse_args()
if not a.new.startswith(a.prefix):
    sys.exit(f'refused: {a.new} does not start with {a.prefix}')
if len(a.new) > 30:
    sys.exit('refused: new name longer than 30 characters')
PF, CF = 'PER_HCM_DATA_ROLE.csv', 'ORA_PER_HCM_DATA_ROLE_PROFILE.csv'
IDS = ('GeneratedDataRoleId', 'DataRoleId', 'BaseRoleId', 'GenDataRoleProfileId', 'SecurityProfileId')


def read(n):
    with open(os.path.join(a.export_dir, n), encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    return rows[0], [dict(zip(rows[0], r)) for r in rows[1:]]


ph, pr = read(PF)
ch, cr = read(CF)
if any(r['DataRoleName'] == a.new for r in pr):
    sys.exit(f'refused: {a.new} already exists')
src = [r for r in pr if r['DataRoleName'] == a.source]
if len(src) != 1:
    sys.exit(f'refused: source {a.source} found {len(src)} times')
p = dict(src[0])
text = a.new.replace('_', ' ')
p.update(DataRoleName=a.new, GroupingKey=a.new, AppRoleName=a.new, DataRoleIdResolverName=a.new,
         DataRoleDisplayName=text, DataRoleDescription='Test data role ' + text, AppRoleDisplayName=text,
         AppRoleDescription='')
for k in IDS:
    if k in p:
        p[k] = ''
kids = []
for r in cr:
    if r['DataRoleName'] == a.source:
        c = dict(r)
        c['PER_HCM_DATA_ROLE.DataRoleName'] = a.new
        c['DataRoleName'] = a.new
        c['GroupingKey'] = a.new + ',' + r['HrSecuringObject']
        for k in IDS:
            if k in c:
                c[k] = ''
        kids.append(c)
if not kids:
    sys.exit('refused: source has no security profile rows')
os.makedirs(a.out_dir, exist_ok=True)
zp = os.path.join(a.out_dir, a.zip_name)
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, h, rows in ((PF, ph, [p]), (CF, ch, kids)):
        buf = io.StringIO()
        w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator='\n')
        w.writerow(h)
        for r in rows:
            w.writerow([r.get(k, '') for k in h])
        z.writestr(n, buf.getvalue().encode('utf-8'))
    z.write(os.path.join(a.export_dir, 'ASM_SETUP_CSV_METADATA.xml'), 'ASM_SETUP_CSV_METADATA.xml')
print(f'{PF}: 1 new row ({a.new}, job role {p["InheritedJobRoleCommonName"]})')
print(f'{CF}: {len(kids)} new rows (securing objects: {", ".join(sorted(k["HrSecuringObject"] for k in kids))})')
print('wrote ' + zp)
