"""Run 22 steps 3-5: level-by-level impact from the EDITED workbook + fresh live reads; adds ImpactMap and WhoDidWhat
sheets, logs Change 2 as not made, writes impact_map.csv and evidence/impact_facts.json. Local only."""
import sys, json, csv, collections
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
R = sys.argv[1]; F = R + '/calendar_chain_workbook_ETIA-TEST_EDITED.xlsx'
wb = load_workbook(F)

def rows(s):
    it = wb[s].iter_rows(values_only=True); h = next(it)
    return [dict(zip(h, r)) for r in it if r and r[0] not in (None, '(no rows)')]

P, S, L, B = rows('Periods'), rows('PeriodStatus'), rows('Ledgers'), rows('BusinessUnits')
AO, AT, OM = rows('ReceivablesOptions'), rows('ReceivablesTxnTypes'), rows('OtherModules')
ar_inv = json.load(open(R + '/evidence/rest/ar_all_visible.json', encoding='utf-8'))['items']
ap_tot = json.load(open(R + '/evidence/rest/ap_total.json', encoding='utf-8')).get('totalResults')
ap_rng = len(json.load(open(R + '/evidence/rest/ap_invdate.json', encoding='utf-8'))['items']) + len(json.load(open(R + '/evidence/rest/ap_acctdate.json', encoding='utf-8'))['items'])
rc_rng = len(json.load(open(R + '/evidence/rest/receipts_dec.json', encoding='utf-8'))['items'])
APPN = {'101': 'General Ledger', '200': 'Payables', '222': 'Receivables', '10037': 'application 10037 (name not read)', '10455': 'application 10455 (name not read)'}
FSCR_CAL = 'fscr-main/pillars/erp/financials/financial-reporting-structures/manage-accounting-calendars/SKILL.md:179-229'
FSCR_COST = 'fscr-main/pillars/scm/manufacturing-and-supply-chain-materials-management/cost-accounting/cost-organization-relationships/ora-resource/ora_dependency_readiness.md:28-29'
FSCR_BU = 'fscr-main/pillars/erp/financials/organization-structures/manage-business-unit.md:59'
DOC_VAL = 'https://docs.oracle.com/en/cloud/saas/applications-common/25d/facia/how-accounting-calendars-are-validated.html'
DOC_AR = 'https://docs.oracle.com/en/cloud/saas/financials/24d/faofc/what-happens-to-accounting-periods-during-reconciliation.html'
WB = 'workbook EDITED (Run 21 data)'
facts = {}; M = []

def add(ch, lvl, mod, typ, name, frm, link, cnt, tag, src):
    M.append(dict(Change=ch, Level=lvl, Module=mod, ObjectType=typ, ObjectName=name, ReachedFrom=frm, LinkType=link, Count=cnt, Tag=tag, Source=src))

for ch, cal in (('1', 'GoSaaS MFG'), ('2', 'GS Account')):
    led = [l for l in L if l['CalendarName'] == cal]; bus = [b for b in B if b['CalendarName'] == cal]
    dec = [p for p in P if p['CalendarName'] == cal and p['PeriodName'] == 'Dec-26']
    adj = [p for p in P if p['CalendarName'] == cal and p['PeriodName'] == '13_Dec-26']
    st = [s for s in S if s['CalendarName'] == cal and s['PeriodName'] == 'Dec-26']
    f = facts[cal] = {'ledgers': len(led), 'bus': len(bus), 'dec26_rows': len(dec), 'status_rows': len(st),
                      'status_by_app': {a: dict(collections.Counter(s['ClosingStatus'] for s in st if str(s['ApplicationId']) == a)) for a in APPN},
                      'ar_options': [a['BusinessUnitName'] for a in AO if a['CalendarName'] == cal],
                      'ar_txn_rows': len([t for t in AT if t['CalendarName'] == cal]),
                      'om_bus': {m: sorted({o['BusinessUnitName'] for o in OM if o['CalendarName'] == cal and o['Module'] == m}) for m in ('Payables', 'Payables and Procurement', 'Procurement')},
                      'periods_total': len([p for p in P if p['CalendarName'] == cal]),
                      'last_period': [(p['PeriodName'], p['EndDate']) for p in P if p['CalendarName'] == cal][-1]}
    if not dec:  # control change cannot be made
        add(ch, 0, 'General Ledger', 'Calendar period', f'{cal} / Dec-26 (does not exist)', '-', 'requested edit', 0, 'VERIFIED IN ENVIRONMENT',
            'workbook Periods + REST accountingPeriodsLOV (Run 22): calendar has %d periods, last %s' % (f['periods_total'], f['last_period'][0]))
    else:
        add(ch, 0, 'General Ledger', 'Calendar period EndDate', f'{cal} / Dec-26: 2026/12/31 -> 2026/12/24', '-', 'edited cell', 1, 'VERIFIED IN ENVIRONMENT', WB + ', sheet Periods + Changes')
        add(ch, 1, 'General Ledger', 'Adjacent period', f'{cal} / 13_Dec-26 (adjusting, 2026/12/31)', 'Dec-26 EndDate', 'next period in the same calendar', len(adj), 'VERIFIED IN ENVIRONMENT', WB + ', sheet Periods')
        add(ch, 1, 'General Ledger', 'Date gap', '2026/12/25 to 2026/12/30 belong to no period', 'Dec-26 EndDate', 'calendar continuity', 6, 'VERIFIED IN ENVIRONMENT', WB + ' (dates); gap rule: ' + DOC_VAL)
        add(ch, 1, 'General Ledger', 'Calendar validation', 'Save would fail: date gap', 'Date gap', 'Oracle calendar validation', 1, 'FROM ORACLE DOCUMENTATION', DOC_VAL)
        add(ch, 1, 'General Ledger', 'FSCR eligibility rule', 'FSCR stops: continuity broken; adjacent period becomes affected', 'Date gap', 'FSCR calendar skill rule', 1, 'FROM FSCR', FSCR_CAL)
    add(ch, 1, 'General Ledger', 'Ledger', f'Ledgers using {cal}', cal, 'ledger PeriodSetName = calendar', len(led), 'VERIFIED IN ENVIRONMENT', WB + ', sheet Ledgers')
    for a, cnt in sorted(f['status_by_app'].items()):
        if cnt or dec:
            n = sum(cnt.values())
            st_txt = ', '.join(f'{k}={v}' for k, v in cnt.items()) or 'no rows'
            add(ch, 2, APPN[a].split(' (')[0] if a in ('101', '200', '222') else 'Other', 'Period status (Dec-26)', f'{APPN[a]}: Dec-26 status per ledger ({st_txt})',
                'Ledgers', 'status row per ledger and application', n, 'VERIFIED IN ENVIRONMENT', 'REST accountingPeriodStatusLOV (Run 22 re-read) = workbook PeriodStatus')
    add(ch, 2, 'Enterprise structure', 'Business unit', f'Business units on those ledgers', 'Ledgers', 'BU primary ledger', len(bus), 'VERIFIED IN ENVIRONMENT', WB + ', sheet BusinessUnits')
    add(ch, 3, 'Receivables', 'Receivables system options', ', '.join(f['ar_options']) or '(none)', 'Business units', 'options row per BU; its ledger uses the calendar', len(f['ar_options']), 'VERIFIED IN ENVIRONMENT', WB + ', sheet ReceivablesOptions')
    add(ch, 3, 'Receivables', 'Receivables transaction-type BU rows', 'transaction types with a row for these BUs', 'Business units', 'BU row on transaction type', f['ar_txn_rows'], 'VERIFIED IN ENVIRONMENT', WB + ', sheet ReceivablesTxnTypes')
    add(ch, 3, 'Receivables', 'Receivables accounting period', 'Receivables Dec-26 would follow the new GL dates', 'Receivables period status', 'subledger periods follow GL periods', len(f['ar_options']), 'FROM ORACLE DOCUMENTATION', DOC_AR)
    for m in ('Payables and Procurement', 'Payables', 'Procurement'):
        add(ch, 3, m, f'{m} options', ', '.join(f['om_bus'][m]) or '(none)', 'Business units', 'options row per BU', len(f['om_bus'][m]), 'VERIFIED IN ENVIRONMENT', WB + ', sheet OtherModules')
    add(ch, 3, 'Costing', 'Cost books', 'cost books on these ledgers (not read)', 'Ledgers', 'cost book uses ledger calendar', '', 'FROM FSCR', FSCR_COST)
    add(ch, 3, 'Many modules', 'Business-unit impact checklist', 'FSCR advises checking Expenses, Projects, Time and Labor, Requisitioning', 'Business units', 'FSCR assess-impacts guide', '', 'FROM FSCR', FSCR_BU)
    if ch == '1':
        bu_set = {b['BusinessUnitName'] for b in bus}
        real = [x for x in ar_inv if x['BusinessUnit'] in bu_set]
        inrng = [x for x in real if '2026-12-25' <= (x['TransactionDate'] or '') <= '2026-12-31']
        facts[cal]['ar_invoices_visible_in_bus'] = [(x['TransactionNumber'], x['TransactionDate'], x['BusinessUnit']) for x in real]
        add(ch, 4, 'Receivables', 'Receivables invoices dated 25-31 Dec 2026', 'none found (3 visible invoices, all BUU1, dated Mar 2025)', 'Receivables accounting period', 'invoice date falls in a period', len(inrng), 'VERIFIED IN ENVIRONMENT', 'REST receivablesInvoices (all 3 visible, filtered locally)')
        add(ch, 4, 'Receivables', 'Receipts dated 25-31 Dec 2026', 'none found', 'Receivables accounting period', 'receipt date falls in a period', rc_rng, 'VERIFIED IN ENVIRONMENT', 'REST standardReceipts (date filter)')
        add(ch, 4, 'Payables', 'Payables invoices dated 25-31 Dec 2026', f'none found ({ap_tot} invoices visible in total)', 'Payables period status', 'invoice/accounting date falls in a period', ap_rng, 'VERIFIED IN ENVIRONMENT', 'REST invoices (InvoiceDate and AccountingDate filters)')
        add(ch, 4, 'Receivables', 'Future invoice dated 25-30 Dec 2026', 'would have no period to land in (ILLUSTRATIVE)', 'Date gap', 'GL date must be in a period', '', 'GUESS', 'reasoning from the gap; no such document exists')

# Changes sheet: log Change 2 as not made
ch = wb['Changes']; ch.append(['Periods', 'Change 2: GS Account | Dec-26', 'EndDate', '(period does not exist)', 'NOT MADE: GS Account has 13 periods, Jul21 to 13_Jul22 (2022/07/25); no Dec-26 in workbook or live'])
# ImpactMap sheet + CSV
HDR = Font(bold=True, color='FFFFFF'); FILL = PatternFill('solid', fgColor='1F4E78')
cols = ['Change', 'Level', 'Module', 'ObjectType', 'ObjectName', 'ReachedFrom', 'LinkType', 'Count', 'Tag', 'Source']
for name in ('ImpactMap', 'WhoDidWhat'):
    if name in wb.sheetnames:
        del wb[name]
ws = wb.create_sheet('ImpactMap'); ws.append(cols)
for m in M:
    ws.append([m[c] for c in cols])
ws.append([]); ws.append(['Counts per level (rows in this map)'])
lv = collections.Counter((m['Change'], m['Level']) for m in M)
for (c, l), n in sorted(lv.items()):
    ws.append([c, l, f'{n} map rows'])
for c in ws[1]:
    c.font = HDR; c.fill = FILL
for i, w in zip('ABCDEFGHIJ', (8, 6, 22, 30, 60, 26, 34, 8, 26, 70)):
    ws.column_dimensions[i].width = w
with open(R + '/impact_map.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(M)
WHO = [('Verify BASELINE MD5 and copy EDIT workbook', 'Claude', 'md5sum + copy'),
       ('Make the edits in the copy and log them in Changes', 'Claude', 'scripts/make_edits.py'),
       ('Find that GS Account has no Dec-26', 'Claude', 'workbook + REST accountingPeriodsLOV'),
       ('Read live periods and period status', 'Claude, using FSCR sign-in', 'FSCR token cache via rget.py; REST accountingPeriodsLOV, accountingPeriodStatusLOV'),
       ('Detect changed cells (edited vs baseline)', 'Claude', 'scripts/detect.py'),
       ('Confirm live = baseline', 'Claude', 'scripts/detect.py'),
       ('Rule: edit allowed only if Never opened in every ledger and application', 'FSCR (skill file)', FSCR_CAL),
       ('Rule: continuity must hold; adjacent period becomes affected', 'FSCR (skill file)', FSCR_CAL),
       ('Ledger uses calendar (Costing view)', 'FSCR (readiness file)', FSCR_COST),
       ('Assess-impacts checklist for business units', 'FSCR (guide)', FSCR_BU),
       ('Calendar, ledger, BU, Receivables, Payables, Procurement data', 'FSCR exports (Runs 18, 20, 21)', 'task-level FSM CSV exports'),
       ('Join calendar -> ledger -> BU -> modules and count each level', 'Claude', 'scripts/impact.py'),
       ('Search for documents dated 25-31 Dec 2026', 'Claude', 'REST receivablesInvoices, standardReceipts, invoices'),
       ('Oracle documentation lookup (gaps, edit lock, subledger periods)', 'Claude', 'docs.oracle.com'),
       ('Examples, ImpactMap, report', 'Claude', 'scripts/impact.py, RUN_REPORT.md')]
ws = wb.create_sheet('WhoDidWhat'); ws.append(['Step', 'Done by', 'File, guide, export or script'])
for w_ in WHO:
    ws.append(list(w_))
for c in ws[1]:
    c.font = HDR; c.fill = FILL
ws.column_dimensions['A'].width = 62; ws.column_dimensions['B'].width = 30; ws.column_dimensions['C'].width = 90
wb.save(F)
json.dump(facts, open(R + '/evidence/impact_facts.json', 'w'), indent=1, default=str)
print(json.dumps(facts, default=str)[:2500]); print('map rows', len(M), dict(lv))
