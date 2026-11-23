"""Run 18: count live links in ETIA-TEST from the REST reads (local, read-only)."""
import json,collections,sys
B=sys.argv[1]+'/evidence/rest/'; L=lambda n: json.load(open(B+n+'.json',encoding='utf-8'))['items']
bu,sa,pl,da,led,cur,rs,le=[L(n) for n in ('bu_lov','set_assign_bu','price_lists','data_access','ledgers','currencies','ref_sets','legal_entities')]
o={}
act=[b for b in bu if b['ActiveFlag']]
o['BU']={'business_units':len(bu),'active':len(act),'with_primary_ledger':sum(1 for b in bu if b['PrimaryLedgerId']),
 'with_default_legal_entity':sum(1 for b in bu if b['LegalEntityId']),
 'set_assignment_rows':len(sa),'bus_with_set_assignments':len({s['DeterminantValue'] for s in sa}),
 'price_lists_pointing_to_a_BU':sum(1 for p in pl if p.get('BusinessUnitId')),'distinct_BUs_with_price_lists':len({p['BusinessUnitId'] for p in pl if p.get('BusinessUnitId')}),
 'data_access_grants_by_BU':sum(1 for d in da if (d.get('SecurityContext') or '').lower().startswith('business unit')),
 'data_access_security_contexts':dict(collections.Counter(d.get('SecurityContext') for d in da))}
# top BUs by number of links
cnt=collections.Counter()
for s in sa: cnt[str(s['DeterminantValue'])]+=1
for p in pl: cnt[str(p.get('BusinessUnitId'))]+=1
name={str(b['BusinessUnitId']):b['BusinessUnitName'] for b in bu}
for d in da:
    if (d.get('SecurityContext') or '').lower().startswith('business unit'):
        for k,v in name.items():
            if v==d.get('SecurityContextValue'): cnt[k]+=1
o['BU']['top_BUs_by_links']=[(name.get(k,k),c) for k,c in cnt.most_common(8)]
o['BU']['price_lists_per_BU']=dict(collections.Counter(p.get('BusinessUnit') for p in pl).most_common(6))
by=collections.Counter(s['SetCode'] for s in sa); grp=collections.Counter(s['ReferenceGroupName'] for s in sa)
o['SETS']={'sets':len(rs),'reference_groups_(set-enabled setup types)':len(grp),'set_assignment_rows':len(sa),
 'sets_in_use':len(by),'top_sets_by_rows':by.most_common(6),
 'COMMON_rows':by.get('COMMON',0),'ENTERPRISE_rows':by.get('ENTERPRISE',0),
 'BUs_using_COMMON':len({s['DeterminantValue'] for s in sa if s['SetCode']=='COMMON'}),
 'groups_using_COMMON':len({s['ReferenceGroupName'] for s in sa if s['SetCode']=='COMMON'}),
 'reference_groups_sample':sorted(grp)[:60]}
en=[c for c in cur if c['EnabledFlag']=='Y']
o['CUR']={'currencies':len(cur),'enabled':len(en),'ledgers':len(led),'ledger_currency_counts':collections.Counter(l.get('CurrencyCode') for l in led).most_common(6),
 'price_list_currency_counts':collections.Counter(p.get('CurrencyCode') for p in pl).most_common(6),
 'USD_links':{'ledgers':sum(1 for l in led if l.get('CurrencyCode')=='USD'),'price_lists':sum(1 for p in pl if p.get('CurrencyCode')=='USD')}}
json.dump(o,open(sys.argv[1]+'/evidence/live_links.json','w'),indent=1,default=str)
for k,v in o.items():
    print('##',k)
    for a,b in v.items(): print('  ',a,':',str(b)[:400])
