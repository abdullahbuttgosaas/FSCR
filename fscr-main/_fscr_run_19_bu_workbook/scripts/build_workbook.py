"""Run 19: build bu_change_impact_workbook_ETIA-TEST.xlsx for 6 business units (local only, read-only data).
Sources: Run 18 FSM exports and REST reads (reused), plus one fresh REST read of price lists (Run 19).
Every data sheet starts with BusinessUnitName, BusinessUnitId and ends with Source. Real values only."""
import csv, glob, json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
csv.field_size_limit(10**9)
R = sys.argv[1]
R18 = R + '/../_fscr_run_18_best_subject/evidence/'
BUS = ['ABD', 'ABC Procurement BU', 'GoSaaS', 'AMNA BU', 'AKBusiness Unit Domestic', 'ZZ_TEST_7669']
WHY = {
    'ABD': 'Most kinds of links: ledger, legal entity, 19 functions, service providers, 68 set assignments, 21 price lists, user access.',
    'ABC Procurement BU': 'Also has all 7 kinds of links, including 3 price lists, on a different ledger (GoSaaS Labs Ledger).',
    'GoSaaS': 'Most user access grants (25 in Run 18); its ledger GoSaaS MFG US is shared with other BUs.',
    'AMNA BU': 'Has Receivables system options and a Receivables transaction-type row; ledger EBS-Testing-AI.',
    'AKBusiness Unit Domestic': 'Has Receivables system options, a default currency (USD) and the most service-provider links (11 in Run 18).',
    'ZZ_TEST_7669': 'Contrast: active, but no ledger, legal entity, functions, set assignments, price lists or user access.',
}

def csvrows(task, name):
    f = glob.glob(R18 + f'exports/{task}/csv/**/{name}', recursive=True)[0]
    return list(csv.DictReader(open(f, encoding='utf-8-sig')))

def rest(name, base=R18):
    return json.load(open(base + f'rest/{name}.json', encoding='utf-8'))['items']

lov = {b['BusinessUnitName']: b for b in rest('bu_lov')}
BID = {n: str(lov[n]['BusinessUnitId']) for n in BUS}
bu = [b for b in csvrows('FUN_MANAGE_BUSINESS_UNIT', 'FUN_BUSINESS_UNIT.csv') if b['Name'] in BUS]
ORG = {b['Name']: b['OrganizationCode'] for b in bu}
S_BU = 'FSM export FUN_MANAGE_BUSINESS_UNIT (Run 18), file FUN_BUSINESS_UNIT.csv'
S_LOV = 'REST finBusinessUnitsLOV (Run 18)'

wb = Workbook()
HDR = Font(bold=True, color='FFFFFF'); FILL = PatternFill('solid', fgColor='1F4E78')
tcount = [0]

def sheet(title, cols, rows, note=None):
    ws = wb.create_sheet(title)
    cols = ['BusinessUnitName', 'BusinessUnitId'] + [c for c in cols if c not in ('BusinessUnitName', 'BusinessUnitId', 'Source')] + ['Source']
    ws.append(cols)
    for r in rows:
        ws.append([('' if r.get(c) is None else (json.dumps(r[c]) if isinstance(r.get(c), (dict, list)) else r.get(c))) for c in cols])
    if not rows:
        ws.append(['(no rows for any of the 6 BUs)'] + [''] * (len(cols) - 1))
    for c in ws[1]:
        c.font = HDR; c.fill = FILL
    ws.freeze_panes = 'C2'
    for i, c in enumerate(cols, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = max(12, min(42, len(c) + 3))
    if rows:
        tcount[0] += 1
        ref = f"A1:{ws.cell(1, len(cols)).column_letter}{len(rows) + 1}"
        t = Table(displayName=f"T_{title}", ref=ref); t.tableStyleInfo = TableStyleInfo(name='TableStyleLight9', showRowStripes=True)
        ws.add_table(t)
    if note:
        ws.cell(len(rows) + 3 if rows else 4, 1, note).font = Font(italic=True)
    return ws

# 2 BusinessUnits: every export column + LOV IDs
rows = []
for b in bu:
    r = {'BusinessUnitName': b['Name'], 'BusinessUnitId': BID[b['Name']]}
    r.update({k: v for k, v in b.items() if k != 'Name'})
    l = lov[b['Name']]
    r.update({'LOV_ActiveFlag': l['ActiveFlag'], 'LOV_PrimaryLedgerId': l['PrimaryLedgerId'], 'LOV_LegalEntityId': l['LegalEntityId'],
              'LOV_LocationId': l['LocationId'], 'LOV_ProfitCenterFlag': l['ProfitCenterFlag']})
    r['Source'] = S_BU + '; IDs from ' + S_LOV
    rows.append(r)
rows.sort(key=lambda r: BUS.index(r['BusinessUnitName']))
bu_cols = list(rows[0].keys())
SHEETS = {}
SHEETS['BusinessUnits'] = rows

# 3 BusinessFunctions
use = csvrows('FUN_MANAGE_BUSINESS_UNIT', 'FUN_BU_USAGE.csv')
rows = [{'BusinessUnitName': u['FUN_BUSINESS_UNIT.Name'], 'BusinessUnitId': BID[u['FUN_BUSINESS_UNIT.Name']], 'FunctionModuleId': u['ModuleId'],
         'FunctionName': 'not in export (FSCR says the ID-to-name list is developer-provided seed data)',
         'Enabled (ConfigurationStatus)': u['ConfigurationStatus'], 'CreatedBy': u['CreatedBy'], 'CreationDate': u['CreationDate'],
         'Source': S_BU.replace('FUN_BUSINESS_UNIT.csv', 'FUN_BU_USAGE.csv')} for u in use if u['FUN_BUSINESS_UNIT.Name'] in BUS]
rows.sort(key=lambda r: (BUS.index(r['BusinessUnitName']), int(r['FunctionModuleId'])))
SHEETS['BusinessFunctions'] = rows

# 4 LedgerAndLegalEntity
led = {str(l['LedgerId']): l for l in rest('ledgers')}
les = {str(l['LegalEntityId']): l for l in rest('legal_entities')}
gl = {g['Name']: g for g in csvrows('GL_MANAGE_PRIMARY_LEDGERS', 'GL_PRIMARY_LEDGER.csv')} if glob.glob(R18 + 'exports/GL_MANAGE_PRIMARY_LEDGERS/csv/**/GL_PRIMARY_LEDGER.csv', recursive=True) else {}
rows = []
for b in sorted(bu, key=lambda b: BUS.index(b['Name'])):
    l = lov[b['Name']]; L = led.get(str(l['PrimaryLedgerId'] or ''), {}); E = les.get(str(l['LegalEntityId'] or ''), {})
    g = gl.get(b['PrimaryLedgerName'], {})
    rows.append({'BusinessUnitName': b['Name'], 'BusinessUnitId': BID[b['Name']],
                 'PrimaryLedgerName': b['PrimaryLedgerName'], 'PrimaryLedgerId': l['PrimaryLedgerId'] or '',
                 'LedgerCurrency': L.get('CurrencyCode', ''), 'LedgerCategory': L.get('LedgerCategoryCode', ''),
                 'ChartOfAccountsId': L.get('ChartOfAccountsId', ''), 'AccountingCalendar (PeriodSetName)': L.get('PeriodSetName', ''),
                 'LedgerInGLExport': 'yes' if g else ('no' if b['PrimaryLedgerName'] else ''),
                 'LegalEntityName': b['LegalEntityName'], 'LegalEntityId': l['LegalEntityId'] or '',
                 'LegalEntityIdentifier': E.get('LegalEntityIdentifier', ''), 'LegalEntityPartyId': E.get('PartyId', ''),
                 'Source': S_BU + ' (names); ' + S_LOV + ' (IDs); REST ledgersLOV and legalEntitiesLOV (Run 18); FSM export GL_MANAGE_PRIMARY_LEDGERS (Run 18)'})
SHEETS['LedgerAndLegalEntity'] = rows

# 5 ServiceProviders (one row per relationship row; a BU can be client, provider, or both)
sp = csvrows('FUN_MANAGE_BUSINESS_UNIT', 'FUN_BU_SERVICE_PROVIDERS.csv')
rows = []
for x in sp:
    for role, name in (('client', x['ClientBuName']), ('provider', x['ProviderBuName'])):
        if name in BUS:
            if role == 'provider' and x['ClientBuName'] == name:
                continue  # self-relationship: list once, as client
            r = {'BusinessUnitName': name, 'BusinessUnitId': BID[name], 'ThisBURole': role if x['ClientBuName'] != x['ProviderBuName'] else 'client and provider (itself)'}
            r.update({k: v for k, v in x.items() if not k.startswith('Last')})
            r['Source'] = S_BU.replace('FUN_BUSINESS_UNIT.csv', 'FUN_BU_SERVICE_PROVIDERS.csv')
            rows.append(r)
rows.sort(key=lambda r: BUS.index(r['BusinessUnitName']))
SHEETS['ServiceProviders'] = rows

# 6 SetAssignments (BU export file) + REST cross-check column
sa = csvrows('FUN_MANAGE_BUSINESS_UNIT', 'LE_1214416713655.csv')
code2bu = {v: k for k, v in ORG.items()}
rest_sa = {}
for s in rest('set_assign_bu'):
    rest_sa.setdefault(str(s['DeterminantValue']), {})[s['ReferenceGroupName']] = s['SetCode']
rows = []
for s in sa:
    n = code2bu.get(s['OrganizationCode'])
    if not n:
        continue
    rows.append({'BusinessUnitName': n, 'BusinessUnitId': BID[n], 'ReferenceGroupName': s['ReferenceGroupName'], 'SetCode': s['SetCode'],
                 'DeterminantType': s['DeterminantType'], 'OrganizationCode': s['OrganizationCode'],
                 'SameInREST': 'yes' if rest_sa.get(BID[n], {}).get(s['ReferenceGroupName']) == s['SetCode'] else 'no',
                 'CreationDate': s['CreationDate'], 'Source': S_BU.replace('FUN_BUSINESS_UNIT.csv', 'LE_1214416713655.csv (set assignments)') + '; checked against REST setIdAssignmentsBusinessUnit (Run 18)'})
rows.sort(key=lambda r: (BUS.index(r['BusinessUnitName']), r['ReferenceGroupName']))
SHEETS['SetAssignments'] = rows

# 7 PriceLists (fresh Run 19 read)
pl = rest('price_lists_full', R + '/evidence/')
rows = []
for p in pl:
    if p.get('BusinessUnit') in BUS:
        r = {'BusinessUnitName': p['BusinessUnit'], 'BusinessUnitId': str(p['BusinessUnitId'])}
        r.update({k: v for k, v in p.items() if k not in ('@context', 'BusinessUnit', 'BusinessUnitId')})
        r['Source'] = 'REST priceLists (Run 19, read 2026-11-09)'
        rows.append(r)
rows.sort(key=lambda r: (BUS.index(r['BusinessUnitName']), r['PriceListName']))
SHEETS['PriceLists'] = rows

# 8 UserAccess
da = rest('data_access')
rows = []
for d in da:
    if d.get('SecurityContext') == 'Business unit' and d.get('SecurityContextValue') in BUS:
        n = d['SecurityContextValue']
        rows.append({'BusinessUnitName': n, 'BusinessUnitId': BID[n], 'UserName': d.get('UserName'), 'Role': d.get('RoleNameCr'),
                     'RoleCode': d.get('RoleCommonName'), 'ActiveFlag': d.get('ActiveFlag'), 'SecurityContext': d.get('SecurityContext'),
                     'CreationDate': d.get('CreationDate'), 'Source': 'REST dataSecurities (Run 18)'})
rows.sort(key=lambda r: (BUS.index(r['BusinessUnitName']), str(r['UserName'])))
SHEETS['UserAccess'] = rows

# 9 ReceivablesOptions (all non-empty columns) + 9b ReceivablesTxnTypeBU
so = [x for x in csvrows('AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS', 'AR_SYSTEM_OPTIONS.csv') if x['BUName'] in BUS]
keep = [k for k in (so[0].keys() if so else []) if k != 'BUName' and any(x[k] for x in so)]
rows = []
for x in so:
    r = {'BusinessUnitName': x['BUName'], 'BusinessUnitId': BID[x['BUName']]}
    r.update({k: x[k] for k in keep}); r['Source'] = 'FSM export AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS (Run 18), file AR_SYSTEM_OPTIONS.csv (empty columns left out)'
    rows.append(r)
rows.sort(key=lambda r: BUS.index(r['BusinessUnitName']))
SHEETS['ReceivablesOptions'] = rows
tt = [x for x in csvrows('AR_MANAGE_TRANSACTION_TYPES', 'AR_REF_ACCT_TRX_TYPE.csv') if x['BuName'] in BUS]
rows = []
for x in tt:
    r = {'BusinessUnitName': x['BuName'], 'BusinessUnitId': BID[x['BuName']]}
    r.update({k: v for k, v in x.items() if k != 'BuName' and v}); r['Source'] = 'FSM export AR_MANAGE_TRANSACTION_TYPES (Run 18), file AR_REF_ACCT_TRX_TYPE.csv'
    rows.append(r)
SHEETS['ReceivablesTxnTypeBU'] = rows

# README first
ws = wb.active; ws.title = 'README'
counts = {s: {n: sum(1 for r in v if r['BusinessUnitName'] == n) for n in BUS} for s, v in SHEETS.items()}
lines = [
    ['Business unit change-impact workbook (ETIA-TEST)'],
    ['What it is: 6 business units from Oracle pod ETIA-TEST and the setup that points to them, read on 2026-11-09. Read only: nothing was changed in Oracle.'],
    ['How sheets connect: every data sheet starts with BusinessUnitName and BusinessUnitId. Filter any sheet by one BU to see everything tied to it.'],
    ['How to read it: one row = one real record from Oracle. The Source column says which export or REST read it came from. No values were invented.'],
    ['How to use it later: change a value in BusinessUnits (for example Status A to I) and log it in the Changes sheet. Every other sheet, filtered by that BU, shows what the change would touch.'],
    [''],
    ['Business unit', 'BusinessUnitId', 'Why picked'] + list(SHEETS.keys()),
]
for n in BUS:
    lines.append([n, BID[n], WHY[n]] + [counts[s][n] for s in SHEETS])
lines += [[''], ['Sheet', 'What it holds'],
          ['BusinessUnits', 'All columns the BU export gives, plus IDs from the BU list (REST).'],
          ['BusinessFunctions', 'Functions turned on for each BU (module ID; Oracle export gives no name).'],
          ['LedgerAndLegalEntity', 'The primary ledger and default legal entity each BU points to, with IDs and ledger currency.'],
          ['ServiceProviders', 'BU-to-BU service-provider rows; a BU that serves itself is listed once.'],
          ['SetAssignments', 'Which reference data set each setup type (payment terms, transaction types and others) uses for this BU.'],
          ['PriceLists', 'Price lists owned by the BU.'],
          ['UserAccess', 'Users with data access to the BU, and the role.'],
          ['ReceivablesOptions', 'Receivables system options for the BU (only columns with a value).'],
          ['ReceivablesTxnTypeBU', 'Receivables transaction types with a row for the BU.'],
          ['Changes', 'Empty. Fill in later: Sheet, Row key, Column, Old value, New value.']]
for l in lines:
    ws.append(l)
ws['A1'].font = Font(bold=True, size=14)
for c in ws[7]:
    c.font = HDR; c.fill = FILL
ws.column_dimensions['A'].width = 26; ws.column_dimensions['B'].width = 18; ws.column_dimensions['C'].width = 70
for row in ws.iter_rows(min_row=2, max_row=5):
    row[0].alignment = Alignment(wrap_text=False)

for s, v in SHEETS.items():
    cols = list(v[0].keys()) if v else ['Note']
    note = None
    if s == 'UserAccess' and not v:
        note = 'No rows: REST dataSecurities returned no Business unit grants for these BUs.'
    sheet(s, cols, v, note)
ch = wb.create_sheet('Changes'); ch.append(['Sheet', 'Row key', 'Column', 'Old value', 'New value'])
for c in ch[1]:
    c.font = HDR; c.fill = FILL
for i in 'ABCDE':
    ch.column_dimensions[i].width = 24
out = R + '/bu_change_impact_workbook_ETIA-TEST.xlsx'
wb.save(out)
json.dump({'bu_ids': BID, 'counts': counts}, open(R + '/evidence/workbook_counts.json', 'w'), indent=1)
print('saved', out, 'sheets', wb.sheetnames)
for s in SHEETS:
    print(s.ljust(22), counts[s], 'cols', len(SHEETS[s][0]) if SHEETS[s] else 0)
