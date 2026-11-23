"""Offline analysis of the Run 02 evidence (no Oracle calls).
Builds evidence/area_facts.json: per area, the FSCRT records and the chosen pre-existing records as read
from Oracle, plus the comparison with Run 01 input_records.md / payloads (question C).
Why: FSCR's readers return raw exports/XML and no explanation or comparison against a request."""
import csv, io, json, re, zipfile
from pathlib import Path

R2 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_02_understand")
R1 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01")
EV = R2 / "evidence"
J = lambda p: json.loads((EV / p).read_text(encoding="utf-8"))
facts = {}


def zrows(zipname, csvname):
    z = zipfile.ZipFile(EV / "D/exports" / zipname)
    return list(csv.DictReader(io.StringIO(z.read(csvname).decode("utf-8-sig"))))


def x(s, tag, allm=False):
    pat = r"<(?:\w+:)?%s>([^<]*)</(?:\w+:)?%s>" % (tag, tag)
    return re.findall(pat, s) if allm else (re.search(pat, s) or [None, None])[1]


# A1 business units: REST LOV + FSCR export
bu_exp = zrows("ETIA-TEST_setup_task_csv_export_fun_manage_business_unit_100004734412462.zip", "FUN_BUSINESS_UNIT.csv")
usage = zrows("ETIA-TEST_setup_task_csv_export_fun_manage_business_unit_100004734412462.zip", "FUN_BU_USAGE.csv")
lov = {b["BusinessUnitName"]: b for b in J("A1/finBusinessUnitsLOV.json")["items"]}
pick = ["FSCRT_Quillon Ridge Outfitters West F01", "FSCRT_Brindle Harbor Marine Supply F01", "0012", "01PRC Exam BU", "TESTBU4"]
keep = ["Name", "Status", "DefaultSetCode", "PrimaryLedgerName", "LegalEntityName", "InternalLocationCode", "LocationSetCode", "ManagerListName", "ProfitCenterFlag", "CreationDate", "CreatedBy"]
facts["A1"] = {b: {"export": {k: r.get(k) for k in keep}, "rest_lov": {k: v for k, v in lov.get(b, {}).items() if k != "@context"},
                   "business_functions": sum(1 for u in usage if u["FUN_BUSINESS_UNIT.Name"] == b)}
               for b in pick for r in bu_exp if r["Name"] == b}
facts["A1_stats"] = {"bus_total": len(bu_exp), "bus_without_functions": len(bu_exp) - len({u["FUN_BUSINESS_UNIT.Name"] for u in usage}),
                     "bus_without_ledger": sum(1 for r in bu_exp if not r.get("PrimaryLedgerName")),
                     "set_assignment_rows_for_fscrt": 0,
                     "data_access_rows_fscrt": [(d["UserName"], d["RoleNameCr"], d["SecurityContextValue"], d["CreationDate"]) for d in J("A1/dataSecurities_fscrt.json")["items"]]}

# A2 price lists
pls = J("A2/priceLists_all.json")["items"]
pick = ["FSCRT_Quillon Ridge Wholesale Tents USD F01", "FSCRT_Brindle Harbor Dock Equipment EUR F01", "Collector Retail USD D01", "TESTPRICELIST4", "zz_test_pl_8034_all"]
sets = lambda p: [a["AccessSetCode"] for a in (p["accessSets"].get("items", []) if isinstance(p["accessSets"], dict) else p["accessSets"]) if isinstance(a, dict)]
keep = ["PriceListId", "PriceListName", "PriceListDescription", "PriceListTypeCode", "BusinessUnit", "CurrencyCode", "StatusCode", "StartDate", "EndDate", "PricingChargeDefinition", "LineTypeCode", "CalculationMethodCode", "CreatedBy", "CreationDate"]
items_all = J("A2/items_all_summary.json")
facts["A2"] = {p["PriceListName"]: dict({k: p.get(k) for k in keep}, access_sets=sets(p), items_read=items_all.get(p["PriceListName"])) for p in pls if p["PriceListName"] in pick}
facts["A2_stats"] = {"price_lists_total": len(pls), "with_items_via_rest": sum(1 for v in items_all.values() if "rows=0" not in v),
                     "in_progress": [p["PriceListName"] for p in pls if p["StatusCode"] != "APPROVED"],
                     "no_access_set": [p["PriceListName"] for p in pls if not sets(p)]}

# A3 payment terms (FSCR export)
pz = "ETIA-TEST_setup_task_csv_export_ar_manage_receivables_payment_terms_100004733440719.zip"
terms, lines, disc = zrows(pz, "AR_PAYMENT_TERM.csv"), zrows(pz, "AR_PAYMENT_TERM_LINE.csv"), zrows(pz, "AR_PAYMENT_TERM_DISCOUNT.csv")
pick = ["FSCRT_2P10N30F1", "FSCRT_D25B75AF1"] + [t["Name"] for t in terms if not t["Name"].startswith("FSCRT")][:3]
tk = ["Name", "Description", "SetCode", "StartDateActive", "EndDateActive", "BaseAmount", "FirstInstallmentCode", "InstallmentOption", "PrintingLeadDays", "DiscountBasis", "CalcDiscountOnLinesFlag", "PartialDiscountFlag", "CreditCheckFlag", "PrepaymentFlag", "BillingCycleId"]
facts["A3"] = {n: {"term": {k: t.get(k) for k in tk if k in t},
                   "lines": [{k: l.get(k) for k in ("SequenceNum", "RelativeAmount", "DueDays", "DueDate", "DueDayOfMonth")} for l in lines if l["AR_PAYMENT_TERM.Name"] == n],
                   "discounts": [{k: v for k, v in d.items() if v and k not in ("CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin")} for d in disc if d.get("AR_PAYMENT_TERM.Name") == n]}
               for n in pick for t in terms if t["Name"] == n}
facts["A3_stats"] = {"terms_total": len(terms), "terms_ended": [t["Name"] for t in terms if t.get("EndDateActive")],
                     "fscr_reconcile": J("D/fscr_pt_reconcile_fresh.json")["status"]}

# A4/A5 lookups and order types (FSCR export + REST)
lz = "ETIA-TEST_setup_task_csv_export_doo_manage_orchestration_lookups_100004733440757.zip"
ltypes, lcodes = zrows(lz, "FND_APP_STANDARD_LOOKUP.csv"), zrows(lz, "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv")
ck = ["LookupCode", "Meaning", "Description", "EnabledFlag", "DisplaySequence", "Tag", "StartDateActive", "EndDateActive"]
rest_types = {t["LookupType"]: t for t in J("A4/standardLookups_fscrt.json")["items"]}
facts["A4"] = {t["LookupType"]: {"type": {k: t.get(k) for k in ("Meaning", "Description", "ModuleId", "CustomizationLevel", "RestAccessSecured")},
                                 "codes": [{k: c.get(k) for k in ck if k in c} for c in lcodes if c["FND_APP_STANDARD_LOOKUP.LookupType"] == t["LookupType"]],
                                 "rest_tag": {c["LookupCode"]: c.get("Tag") for c in (rest_types[t["LookupType"]]["lookupCodes"].get("items", []))} if t["LookupType"] in rest_types else None}
               for t in ltypes}
ot = J("A5/ora_doo_order_types_codes.json")["items"]
pick = [o for o in ot if o["LookupCode"].startswith("FSCRT")] + [o for o in ot if not o["LookupCode"].startswith("FSCRT")][:3]
facts["A5"] = {o["LookupCode"]: {k: o.get(k) for k in ck + ["CreatedBy", "CreationDate"]} for o in pick}
before = json.loads((R1 / "evidence/ora_doo_order_types_before.json").read_text(encoding="utf-8"))
bitems = before.get("items", before) if isinstance(before, dict) else before
bmap = {o["LookupCode"]: o for o in bitems}
facts["A5_stats"] = {"codes_now": len(ot), "codes_before_run01": len(bmap),
                     "changed_preexisting": [o["LookupCode"] for o in ot if o["LookupCode"] in bmap and any(str(o.get(k)) != str(bmap[o["LookupCode"]].get(k)) for k in ("Meaning", "Description", "EnabledFlag", "DisplaySequence", "Tag", "EndDateActive"))],
                     "new_since_run01": [o["LookupCode"] for o in ot if o["LookupCode"] not in bmap],
                     "disabled_now": [o["LookupCode"] for o in ot if o.get("EnabledFlag") != "Y"]}

# A6/A7/A8 customers: FSCR SOAP reader XML + own profile reads + hub REST
def acct(path):
    s = json.loads(Path(path).read_text(encoding="utf-8"))[0]
    m = re.search(r"<(?:\w+:)?CustomerAccountSite[ >]", s)
    site = s[m.start():] if m else ""
    uses = re.findall(r"<(?:\w+:)?CustomerAccountSiteUse[ >](.*?)</(?:\w+:)?CustomerAccountSiteUse>", s, re.S)
    return {"AccountNumber": x(s, "AccountNumber"), "AccountName": x(s, "AccountName"), "PartyId": x(s, "PartyId"),
            "CustomerType": x(s, "CustomerType"), "CustomerClassCode": x(s, "CustomerClassCode"), "Status": x(s, "Status"),
            "AccountEstablishedDate": x(s, "AccountEstablishedDate"), "AccountTerminationDate": x(s, "AccountTerminationDate"),
            "site_SetId": x(site, "SetId"), "site_StartDate": x(site, "StartDate"), "site_EndDate": x(site, "EndDate"),
            "KeyAccountFlag": x(site, "KeyAccountFlag"), "TpHeaderId": x(site, "TpHeaderId"), "EceTpLocationCode": x(site, "EceTpLocationCode"),
            "site_uses": [{"SiteUseCode": x(u, "SiteUseCode"), "PrimaryFlag": x(u, "PrimaryFlag"), "StartDate": x(u, "StartDate"), "Status": x(u, "Status")} for u in uses],
            "account_DFF": {k: x(s, k) for k in ("accountNotesOther", "shippingInstrustions", "customerAgreement")}}


def prof(path):
    p = Path(path)
    if not p.exists():
        return "not read"
    s = p.read_text(encoding="utf-8")
    m = re.search(r"<TEXT>(.*?)</TEXT>", s.replace("&lt;", "<").replace("&gt;", ">"))
    if m:
        return "NO PROFILE: " + m.group(1).strip()
    return {k: x(s, k) for k in ("ProfileClassName", "CreditChecking", "CollectorName", "OverrideTerms", "StandardTerms", "PaymentTerms", "EffectiveStartDate")}


cust = {"22050": ("A6", "evidence/A6/soap/prof_resp_22050.xml"), "22051": ("A6", "evidence/A6/soap/prof_resp_22051.xml"),
        "1002": ("A6", "evidence/A6/soap/prof_resp_1002.xml"), "20008": ("A6", "evidence/A6/profile_20008.json"),
        "22052": ("A7", "evidence/A6/soap/prof_resp_22052.xml"), "22053": ("A7", "evidence/A6/soap/prof_resp_22053.xml"),
        "21264": ("A7", "evidence/A7/prof_resp_21264.xml"), "21040": ("A7", "evidence/A7/prof_resp_21040.xml")}
for n, (area, pf) in cust.items():
    ap = next(p for p in (EV / "A6" / f"acct_{n}.json", EV / "A7" / f"acct_{n}.json") if p.exists())
    a = acct(ap)
    if pf.endswith(".json"):
        raw = json.loads((R2 / pf).read_text(encoding="utf-8"))[0]
        a["profile"] = {k: x(raw, k) for k in ("ProfileClassName", "CreditChecking", "CollectorName", "OverrideTerms")}
    else:
        a["profile"] = prof(R2 / pf)
    facts.setdefault(area, {})[n] = a
facts["A8"] = {n: facts[a][n]["site_uses"] for n, (a, _) in cust.items()}
orgs = {o["PartyId"]: o for o in J("A6/hubOrganizations_fscrt.json")["items"]}
facts["A6_party"] = {o["OrganizationName"]: {k: o.get(k) for k in ("PartyNumber", "DUNSNumberC", "JgzzFiscalCode", "Type", "Status")} for o in orgs.values()}
facts["A7_party"] = J("A7/hubPersons_compare.json")["items"]
facts["A7_party"] = [{k: p.get(k) for k in ("PartyNumber", "PersonName", "FirstName", "MiddleName", "LastName", "NameSuffix", "Title", "Salutation", "JgzzFiscalCode")} for p in facts["A7_party"]]

# C: compare with Run 01 request payloads
pay = json.loads((R1 / "payloads/customers.json").read_text(encoding="utf-8"))
nums = {"orgA": "22050", "orgB": "22051", "perA": "22052", "perB": "22053"}
diffs = []
for key, n in nums.items():
    area = "A6" if key.startswith("org") else "A7"
    got = facts[area][n]
    for f, v in pay[key]["account"].items():
        if f in got and str(got[f]) != str(v):
            diffs.append((n, "account." + f, v, got[f]))
    for f, v in pay[key]["account_site"].items():
        g = got.get("site_" + f, got.get(f))
        if f in ("SetId", "StartDate", "EndDate", "KeyAccountFlag", "TpHeaderId", "EceTpLocationCode") and str(g) != str(v):
            diffs.append((n, "site." + f, v, g))
    want = sorted(u["SiteUseCode"] for u in pay[key]["site_uses"])
    if sorted(u["SiteUseCode"] for u in got["site_uses"]) != want:
        diffs.append((n, "site_uses", want, got["site_uses"]))
facts["C_customer_diffs_vs_run01_payload"] = diffs
(EV / "area_facts.json").write_text(json.dumps(facts, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: (v if k.endswith("stats") or k.startswith("C_") else "...") for k, v in facts.items()}, indent=1, default=str)[:4000])
