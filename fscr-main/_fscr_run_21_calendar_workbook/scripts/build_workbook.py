"""Run 21: build calendar_chain_workbook_ETIA-TEST.xlsx (local only; read-only data, real values only).
Chain: calendar -> ledger -> business unit -> Receivables (+ Payables/Procurement in OtherModules).
Sources: Run 20 calendar export; Run 18 GL, BU, AR exports and REST reads; Run 21 period-status REST reads and
Payables/Procurement exports."""
import csv, glob, json, os, sys, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
csv.field_size_limit(10**9)
R = sys.argv[1]; E21 = R + '/evidence/'
E20 = R + '/../_fscr_run_20_cross_module_subject/evidence/exports/'
E18 = R + '/../_fscr_run_18_best_subject/evidence/'
CALS = ['GoSaaS MFG', 'N24Ledger', 'GS Account']
WHY = {'GoSaaS MFG': 'Main subject (Run 20): widest reach.',
       'N24Ledger': 'Contrast 1: few ledgers, but 3 Receivables option rows.',
       'GS Account': 'Contrast 2: many business units, but no Receivables option rows.'}

def C(base, task, name):
    f = glob.glob(base + f'{task}/csv/**/{name}', recursive=True)
    return list(csv.DictReader(open(f[0], encoding='utf-8-sig'))) if f else None

def J(path):
    return json.load(open(path, encoding='utf-8'))['items']

S_CAL = 'FSM export GL_MANAGE_ACCOUNTING_CALENDARS (Run 20)'
S_LED = 'FSM export GL_MANAGE_PRIMARY_LEDGERS (Run 18), file GL_PRIMARY_LEDGER.csv; IDs from REST ledgersLOV (Run 18)'
S_BU = 'FSM export FUN_MANAGE_BUSINESS_UNIT (Run 18), file FUN_BUSINESS_UNIT.csv; IDs from REST finBusinessUnitsLOV (Run 18)'
APPS = {'101': 'General Ledger', '200': 'Payables', '222': 'Receivables'}
STAT = {'O': 'Open', 'C': 'Closed', 'F': 'Future entry', 'N': 'Never opened', 'P': 'Permanently closed', 'W': 'Close pending'}

ps = [p for p in C(E20, 'GL_MANAGE_ACCOUNTING_CALENDARS', 'GL_PERIOD_SET.csv') if p['PeriodSetName'] in CALS]
pd = [p for p in C(E20, 'GL_MANAGE_ACCOUNTING_CALENDARS', 'GL_PERIOD_DEF.csv') if p['PeriodSetName'] in CALS]
led = [l for l in C(E18 + 'exports/', 'GL_MANAGE_PRIMARY_LEDGERS', 'GL_PRIMARY_LEDGER.csv') if l['PeriodSetName'] in CALS]
lov = {l['Name']: l for l in J(E18 + 'rest/ledgers.json')}
cal_of = {l['Name']: l['PeriodSetName'] for l in led}
lid = {l['Name']: str(lov.get(l['Name'], {}).get('LedgerId', '')) for l in led}
bu = [b for b in C(E18 + 'exports/', 'FUN_MANAGE_BUSINESS_UNIT', 'FUN_BUSINESS_UNIT.csv') if b['PrimaryLedgerName'] in cal_of]
bulov = {b['BusinessUnitName']: b for b in J(E18 + 'rest/bu_lov.json')}
bid = {b['Name']: str(bulov.get(b['Name'], {}).get('BusinessUnitId', '')) for b in bu}
bu_led = {b['Name']: b['PrimaryLedgerName'] for b in bu}

def keys(bu_name=None, ledger=None, cal=None):
    ledger = ledger or bu_led.get(bu_name, '')
    cal = cal or cal_of.get(ledger, '')
    k = {'CalendarName': cal, 'LedgerName': ledger, 'LedgerId': lid.get(ledger, '')}
    if bu_name is not None:
        k.update({'BusinessUnitName': bu_name, 'BusinessUnitId': bid.get(bu_name, '')})
    return k

SHEETS = collections.OrderedDict()
# 2 Calendars
SHEETS['Calendars'] = [dict({'CalendarName': p['PeriodSetName'], 'WhyIncluded': WHY[p['PeriodSetName']]},
                            **{k: v for k, v in p.items() if k != 'PeriodSetName'}, Source=S_CAL + ', file GL_PERIOD_SET.csv')
                       for p in sorted(ps, key=lambda p: CALS.index(p['PeriodSetName']))]
# 3 Periods (calendar definition; status is per ledger, see PeriodStatus)
first = ['PeriodYear', 'PeriodName', 'PeriodNum', 'StartDate', 'EndDate', 'AdjustmentPeriodFlag']
SHEETS['Periods'] = [dict({'CalendarName': p['PeriodSetName']}, **{k: p[k] for k in first},
                          Status='per ledger and application: see sheet PeriodStatus',
                          **{k: v for k, v in p.items() if k not in first + ['PeriodSetName']}, Source=S_CAL + ', file GL_PERIOD_DEF.csv')
                     for p in sorted(pd, key=lambda p: (CALS.index(p['PeriodSetName']), p['StartDate'], p['PeriodNum']))]
# 3b PeriodStatus
rows = []
for l in sorted(led, key=lambda l: (CALS.index(l['PeriodSetName']), l['Name'])):
    f = E21 + f"rest/period_status/{lid[l['Name']]}.json"
    if not os.path.exists(f):
        continue
    for x in J(f):
        rows.append(dict(keys(ledger=l['Name']), ApplicationId=x['ApplicationId'],
                         ApplicationName=APPS.get(x['ApplicationId'], 'not read (ID only)'), PeriodName=x['PeriodNameId'],
                         PeriodYear=x['PeriodYear'], PeriodNumber=x['PeriodNumber'], StartDate=x['StartDate'], EndDate=x['EndDate'],
                         ClosingStatus=x['ClosingStatus'], StatusMeaning=STAT.get(x['ClosingStatus'], 'unknown code'),
                         AdjustmentPeriodFlag=x['AdjustmentPeriodFlag'], Source='REST accountingPeriodStatusLOV (Run 21), filtered by LedgerId'))
rows.sort(key=lambda r: (CALS.index(r['CalendarName']), r['LedgerName'], r['ApplicationId'], r['StartDate'], int(r['PeriodNumber'])))
SHEETS['PeriodStatus'] = rows
# 4 Ledgers
lfirst = ['CurrencyCode', 'StructureInstanceCode', 'AccountedPeriodType', 'LedgerCategoryCode']
SHEETS['Ledgers'] = [dict(keys(ledger=l['Name']), CurrencyCode=l['CurrencyCode'], ChartOfAccounts=l['StructureInstanceCode'],
                          ChartOfAccountsId=lov.get(l['Name'], {}).get('ChartOfAccountsId', ''),
                          LedgerCategory=lov.get(l['Name'], {}).get('LedgerCategoryCode', ''),
                          **{('Src_' + k if k in ('CalendarName', 'LedgerName', 'LedgerId', 'ChartOfAccounts', 'ChartOfAccountsId', 'LedgerCategory') else k): v
                             for k, v in l.items() if k not in ('Name', 'PeriodSetName', 'CurrencyCode', 'StructureInstanceCode')},
                          Source=S_LED)
                     for l in sorted(led, key=lambda l: (CALS.index(l['PeriodSetName']), l['Name']))]
# 5 BusinessUnits
SHEETS['BusinessUnits'] = [dict(keys(bu_name=b['Name']), Status=b['Status'],
                                **{k: v for k, v in b.items() if k not in ('Name', 'PrimaryLedgerName', 'Status')}, Source=S_BU)
                           for b in sorted(bu, key=lambda b: (CALS.index(cal_of[b['PrimaryLedgerName']]), b['PrimaryLedgerName'], b['Name']))]
bus = set(bid)

def module_rows(rows, bukey, source):
    out = []
    for x in rows or []:
        if x.get(bukey) in bus:
            k0 = keys(bu_name=x[bukey])
            keep = {('Src_' + k if k in k0 else k): v for k, v in x.items() if v and k != bukey}
            out.append(dict(k0, **keep, Source=source))
    return sorted(out, key=lambda r: (CALS.index(r['CalendarName']), r['LedgerName'], r['BusinessUnitName']))

# 6 ReceivablesOptions, 7 ReceivablesTxnTypes
so = C(E18 + 'exports/', 'AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS', 'AR_SYSTEM_OPTIONS.csv')
SHEETS['ReceivablesOptions'] = module_rows(so, 'BUName', 'FSM export AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS (Run 18), file AR_SYSTEM_OPTIONS.csv (empty fields left out)')
for r in SHEETS['ReceivablesOptions']:
    r['ReceivablesLedgerSameAsBULedger'] = 'yes' if r.get('Src_LedgerName') == r['LedgerName'] else 'no'
tt = C(E18 + 'exports/', 'AR_MANAGE_TRANSACTION_TYPES', 'AR_REF_ACCT_TRX_TYPE.csv')
SHEETS['ReceivablesTxnTypes'] = module_rows(tt, 'BuName', 'FSM export AR_MANAGE_TRANSACTION_TYPES (Run 18), file AR_REF_ACCT_TRX_TYPE.csv (empty fields left out)')
# 8 OtherModules (long format: one row per BU, setup and field)
other = []
SRC = [('Payables and Procurement', 'Common options for Payables and Procurement', E21 + 'exports/', 'AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT', 'AP_FINANCIAL_SYS_PARAM.csv', 'BuName'),
       ('Payables', 'Invoice options', E21 + 'exports/', 'AP_MANAGE_INVOICE_OPTIONS', 'AP_SYSTEM_PARAMETER.csv', 'BuName'),
       ('Payables', 'Payment options', E21 + 'exports/', 'AP_MANAGE_PAYMENT_OPTIONS', 'AP_SYSTEM_PARAMETER.csv', 'BuName'),
       ('Procurement', 'Procurement business function options', E21 + 'exports/', 'PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION', 'PO_SYSTEM_PARAMETER.csv', 'ShortCode')]
status = []
for mod, setup, base, task, fname, bukey in SRC:
    files = glob.glob(base + f'{task}/csv/**/{fname}', recursive=True)
    if not files:
        status.append((mod, setup, task, 'not readable: export did not return a file')); continue
    n = 0
    for f in files:
        rows = list(csv.DictReader(open(f, encoding='utf-8-sig')))
        k = bukey or next((c for c in (rows[0].keys() if rows else []) if c.lower() in ('buname', 'businessunitname', 'procurementbuname', 'prcbuname', 'bu_name')), None)
        if not k:
            status.append((mod, setup, task + '/' + os.path.basename(f), f'no business unit column ({len(rows)} rows)')); continue
        for x in rows:
            if x.get(k) in bus:
                n += 1
                for fld, v in x.items():
                    if v and fld != k and not fld.startswith(('Last', 'Created', 'Creation', 'GlobalAttribute', 'Attribute')):
                        other.append(dict(keys(bu_name=x[k]), Module=mod, Setup=setup, Field=fld, Value=v,
                                          Source=f'FSM export {task} (Run 21), file {os.path.basename(f)}'))
    status.append((mod, setup, task, f'{n} BU rows for these business units'))
other.sort(key=lambda r: (CALS.index(r['CalendarName']), r['LedgerName'], r['BusinessUnitName'], r['Module'], r['Setup'], r['Field']))
SHEETS['OtherModules'] = other

# workbook
wb = Workbook(); HDR = Font(bold=True, color='FFFFFF'); FILL = PatternFill('solid', fgColor='1F4E78')
ws = wb.active; ws.title = 'README'
counts = {s: {c: sum(1 for r in v if r.get('CalendarName') == c) for c in CALS} for s, v in SHEETS.items()}
lines = [['Accounting calendar chain workbook (ETIA-TEST)'],
         ['What it is: the current setup of one chain in Oracle pod ETIA-TEST, read on 2026-11-09. Read only: nothing was changed in Oracle.'],
         ['The chain: an accounting calendar (General Ledger) -> ledgers that use it -> business units on those ledgers -> Receivables options and transaction types of those business units (and Payables/Procurement options in OtherModules).'],
         ['In plain words: Receivables never names the calendar. It uses a ledger, and the ledger uses the calendar, so a calendar change reaches Receivables quietly.'],
         ['How sheets connect: every sheet starts with CalendarName, then LedgerName and LedgerId, then BusinessUnitName and BusinessUnitId where they apply. Filter by the same value on each sheet.'],
         ['Safe to change for the test (Periods sheet, GoSaaS MFG): StartDate, EndDate, AdjustmentPeriodFlag of a future period such as Dec-26. Calendars sheet: NonAdjPeriodsNum, AdjPeriodsNum. Do not change key columns (CalendarName, LedgerName, LedgerId, BusinessUnitName, BusinessUnitId, PeriodName). Log every edit in the Changes sheet.'],
         ['Period status lives per ledger and per application (General Ledger 101, Payables 200, Receivables 222), so it is in sheet PeriodStatus, not in Periods.'],
         [''], ['Calendar', 'Why included'] + list(SHEETS.keys())]
for c in CALS:
    lines.append([c, WHY[c]] + [counts[s][c] for s in SHEETS])
lines += [[''], ['OtherModules sources', 'Result']] + [[f'{m}: {s} ({t})', r] for m, s, t, r in status]
for l in lines:
    ws.append(l)
ws['A1'].font = Font(bold=True, size=14)
for c in ws[9]:
    c.font = HDR; c.fill = FILL
ws.column_dimensions['A'].width = 60; ws.column_dimensions['B'].width = 55
for name, rows in SHEETS.items():
    sh = wb.create_sheet(name)
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    if 'Source' in cols:
        cols.remove('Source'); cols.append('Source')
    if not cols:
        cols = ['CalendarName', 'Note']
    sh.append(cols)
    for r in rows:
        sh.append([r.get(c, '') for c in cols])
    if not rows:
        sh.append(['(no rows)', 'Nothing in the exports or REST reads for these business units.'])
    for c in sh[1]:
        c.font = HDR; c.fill = FILL
    sh.freeze_panes = 'B2'
    for i, c in enumerate(cols, 1):
        sh.column_dimensions[sh.cell(1, i).column_letter].width = max(12, min(40, len(c) + 3))
    if rows:
        t = Table(displayName='T_' + name, ref=f'A1:{sh.cell(1, len(cols)).column_letter}{len(rows) + 1}')
        t.tableStyleInfo = TableStyleInfo(name='TableStyleLight9', showRowStripes=True); sh.add_table(t)
ch = wb.create_sheet('Changes'); ch.append(['Sheet', 'Row key', 'Column', 'Old value', 'New value'])
for c in ch[1]:
    c.font = HDR; c.fill = FILL
for i in 'ABCDE':
    ch.column_dimensions[i].width = 26
wb.save(R + '/calendar_chain_workbook_ETIA-TEST.xlsx')
json.dump({'counts': counts, 'other_status': status, 'sheets': wb.sheetnames}, open(E21 + 'workbook_counts.json', 'w'), indent=1)
print('sheets', wb.sheetnames)
for s in SHEETS:
    print(s.ljust(20), counts[s], 'total', len(SHEETS[s]))
for x in status:
    print('OTHER', x)
