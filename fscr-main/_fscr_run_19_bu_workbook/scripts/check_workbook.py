"""Run 19: re-open the workbook and compare its per-BU row counts with counts taken straight from the sources and
with Run 18's bu_links.json. Writes evidence/check_results.json (local, read-only)."""
import json,csv,glob,sys,collections
from openpyxl import load_workbook
csv.field_size_limit(10**9); R=sys.argv[1]; R18=R+'/../_fscr_run_18_best_subject/evidence/'
wb=load_workbook(R+'/bu_change_impact_workbook_ETIA-TEST.xlsx',read_only=True)
BUS=['ABD','ABC Procurement BU','GoSaaS','AMNA BU','AKBusiness Unit Domestic','ZZ_TEST_7669']
ids=json.load(open(R+'/evidence/workbook_counts.json'))['bu_ids']
def wbcount(s):
    rows=list(wb[s].iter_rows(min_row=2,values_only=True)); c=collections.Counter(r[0] for r in rows if r[0] in BUS)
    idok=all(str(r[1])==ids[r[0]] for r in rows if r[0] in BUS); return {n:c[n] for n in BUS},idok
C=lambda t,n: list(csv.DictReader(open(glob.glob(R18+f'exports/{t}/csv/**/{n}',recursive=True)[0],encoding='utf-8-sig')))
J=lambda p: json.load(open(p,encoding='utf-8'))['items']
bu=C('FUN_MANAGE_BUSINESS_UNIT','FUN_BUSINESS_UNIT.csv'); org={b['Name']:b['OrganizationCode'] for b in bu}
src={}
src['BusinessUnits']={n:sum(b['Name']==n for b in bu) for n in BUS}
u=C('FUN_MANAGE_BUSINESS_UNIT','FUN_BU_USAGE.csv'); src['BusinessFunctions']={n:sum(x['FUN_BUSINESS_UNIT.Name']==n for x in u) for n in BUS}
src['LedgerAndLegalEntity']={n:1 for n in BUS}
sp=C('FUN_MANAGE_BUSINESS_UNIT','FUN_BU_SERVICE_PROVIDERS.csv'); src['ServiceProviders']={n:sum(1 for x in sp if n in (x['ClientBuName'],x['ProviderBuName'])) for n in BUS}
sa=C('FUN_MANAGE_BUSINESS_UNIT','LE_1214416713655.csv'); src['SetAssignments']={n:sum(x['OrganizationCode']==org[n] for x in sa) for n in BUS}
pl=J(R+'/evidence/rest/price_lists_full.json'); src['PriceLists']={n:sum(p['BusinessUnit']==n for p in pl) for n in BUS}
da=J(R18+'rest/data_access.json'); src['UserAccess']={n:sum(1 for d in da if d.get('SecurityContext')=='Business unit' and d.get('SecurityContextValue')==n) for n in BUS}
so=C('AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS','AR_SYSTEM_OPTIONS.csv'); src['ReceivablesOptions']={n:sum(x['BUName']==n for x in so) for n in BUS}
tt=C('AR_MANAGE_TRANSACTION_TYPES','AR_REF_ACCT_TRX_TYPE.csv'); src['ReceivablesTxnTypeBU']={n:sum(x['BuName']==n for x in tt) for n in BUS}
# extra cross-checks
rest_sa=collections.Counter(str(s['DeterminantValue']) for s in J(R18+'rest/set_assign_bu.json'))
pl18=J(R18+'rest/price_lists.json')
r18={x['bu']:x for x in json.load(open(R18+'bu_links.json'))}
same_no=collections.Counter(r[0] for r in wb['SetAssignments'].iter_rows(min_row=2,values_only=True) if r[0] in BUS and r[6]=='no')
le=list(wb['LedgerAndLegalEntity'].iter_rows(min_row=1,values_only=True)); hdr=le[0]
out={'sheets':{},'mismatches':[],'empty':[],'id_columns_ok':{}}
for s in src:
    w,idok=wbcount(s); out['sheets'][s]={'workbook':w,'source':src[s]}; out['id_columns_ok'][s]=idok
    for n in BUS:
        if w[n]!=src[s][n]: out['mismatches'].append(f'{s} / {n}: workbook {w[n]} vs source {src[s][n]}')
        if w[n]==0: out['empty'].append(f'{s} / {n}')
for n in BUS:
    x=r18[n]
    pairs=[('BusinessFunctions','functions'),('SetAssignments','set_assignments'),('PriceLists','price_lists'),('UserAccess','data_access'),('ServiceProviders','service_provider_links')]
    for s,k in pairs:
        if out['sheets'][s]['workbook'][n]!=x[k]: out['mismatches'].append(f'{s} / {n}: workbook {out["sheets"][s]["workbook"][n]} vs Run 18 count {x[k]}')
    if src['SetAssignments'][n]!=rest_sa[ids[n]]: out['mismatches'].append(f'SetAssignments / {n}: FSM export {src["SetAssignments"][n]} vs REST setIdAssignmentsBusinessUnit {rest_sa[ids[n]]}')
    if same_no[n]: out['mismatches'].append(f'SetAssignments / {n}: {same_no[n]} rows have a different set code in REST (SameInREST = no)')
    if src['PriceLists'][n]!=sum(p['BusinessUnit']==n for p in pl18): out['mismatches'].append(f'PriceLists / {n}: Run 19 read {src["PriceLists"][n]} vs Run 18 read')
for row in le[1:]:
    d=dict(zip(hdr,row))
    if d['BusinessUnitName'] in BUS and d['PrimaryLedgerName'] and not d['LedgerCurrency']: out['mismatches'].append(f'LedgerAndLegalEntity / {d["BusinessUnitName"]}: ledger {d["PrimaryLedgerName"]} not found in REST ledgersLOV')
    if d['BusinessUnitName'] in BUS and not d['PrimaryLedgerName']: out['empty'].append(f'LedgerAndLegalEntity / {d["BusinessUnitName"]}: no ledger and no legal entity (row kept, values blank)')
json.dump(out,open(R+'/evidence/check_results.json','w'),indent=1)
print('ID columns ok:',out['id_columns_ok']); print('MISMATCHES:'); [print(' ',m) for m in out['mismatches']]; print('EMPTY:'); [print(' ',e) for e in out['empty']]
