"""Run 08: best-start vs pod comparison (offline; makes no Oracle call).

  bestart_compare.py expected            -> expected/best_start.json
  bestart_compare.py actual  <label>     -> actual/<label>/normalized.json   (from FSCR export ZIPs + raw reads)
  bestart_compare.py compare <label>     -> results/<label>.json and results/<label>.md

Expected state = Run 01 input records (input_records.md / request payloads) with the later deliberate changes
of Run 03 (payloads c1-c6) and Run 06 (r1-r3, grp6) applied; Run 04 GRP1 is included because Run 06 R6 defined
GRP6 "like GRP1". Every value below cites its source.  Same normalisation on both sides (norm()).
Fingerprint = MD5 of the canonical JSON of the fields the best start defines for that record; the actual side is
hashed over exactly the same field list.  Status: match / different / missing / extra (extra = FSCRT_ record on
the pod in a compared area that the best start does not define)."""
import csv, hashlib, io, json, re, sys, zipfile
from pathlib import Path

R8 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_08_compare")
RUNS = R8.parent
EXPORTS = R8 / r"fscr-work8\project\draft_impl_project_20261104\exports"


def norm(v):
    """Same rule on both sides: None->'', trim; booleans->Y/N; dates->YYYY-MM-DD; integral numbers without .0."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Y" if v else "N"
    s = str(v).strip()
    if s.lower() in ("true", "false"):
        return "Y" if s.lower() == "true" else "N"
    m = re.match(r"^(\d{4})[/-](\d{2})[/-](\d{2})([ T].*)?$", s)
    if m:
        return f"{m[1]}-{m[2]}-{m[3]}"
    if re.match(r"^-?\d+\.0+$", s):
        return s.split(".")[0]
    return s


def fp(rec, fields):
    canon = json.dumps({f: norm(rec.get(f)) for f in sorted(fields)}, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(canon.encode("utf-8")).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ expected
def build_expected():
    p1, p3, p6 = RUNS / "_fscr_run_01/payloads", RUNS / "_fscr_run_03_change/payloads", RUNS / "_fscr_run_06_requirements/payloads"
    E = {}

    def add(area, key, src, **f):
        E[f"{area}|{key}"] = {"area": area, "key": key, "source": src, "fields": f}

    # Payment terms: input_records.md [3]; names shortened in Run 01 (15-char limit); D25 start = Run 01 'today'
    # (ledger_rows/m1_m2_m3.json); D25 end date set by Run 03 C1 (c1_blueprint_confirmed.json).
    c1 = load(p3 / "c1_blueprint_confirmed.json")["operations"][0]["header"]
    add("payment_term", "FSCRT_2P10N30F1", "Run01 input [3]", SetCode="ENTERPRISE",
        Description="2 percent off if paid in 10 days, otherwise due in 30", StartDateActive="2026-11-03",
        EndDateActive="2028-12-31", Lines="1:100:30", Discounts="1:2:10")
    add("payment_term", "FSCRT_D25B75AF1", "Run01 input [3] + Run03 C1", SetCode="ENTERPRISE",
        Description="25 percent deposit at 15 days, balance at 60 days", StartDateActive="2026-11-02",
        EndDateActive=c1["EndDateActive"], Lines="1:25:15;2:75:60", Discounts="")
    # Lookup types: Run 01 payloads lt1/lt2 (lt1 REST access 'default' -> not specified, not compared)
    for f in ("lt1", "lt2"):
        d = load(p1 / f"{f}.json")
        flds = {k: d[k] for k in ("Meaning", "Description", "ModuleId", "CustomizationLevel", "RestAccessSecured") if k in d}
        add("lookup_type", d["LookupType"], f"Run01 payload {f}.json", **flds)
    # Lookup codes: Run 01 payloads, then Run 03 C2 and Run 06 R2/R3 changes applied in order.
    codes = {"FSCRT_HIKING": ("FSCRT_OUTDOOR_ACTIVITY_F01", ["lc_hiking", "c2_hiking"]),
             "FSCRT_PADDLING": ("FSCRT_OUTDOOR_ACTIVITY_F01", ["lc_paddling", "r3_paddling"]),
             "FSCRT_STANDARD": ("FSCRT_CARRIER_SERVICE_TIER_F01", ["lc_standard", "c2_standard"]),
             "FSCRT_FREIGHT": ("FSCRT_CARRIER_SERVICE_TIER_F01", ["lc_freight", "c2_freight"]),
             "FSCRT_CLIMBING": ("FSCRT_OUTDOOR_ACTIVITY_F01", ["r2_climbing"])}
    for code, (lt, files) in codes.items():
        rec = {"Description": "", "Tag": "", "EndDateActive": ""}  # blank in the input row = expected blank
        for f in files:
            src = p1 if f.startswith("lc_") else (p3 if f.startswith("c2") else p6)
            rec.update({k: v for k, v in load(src / f"{f}.json").items() if k != "LookupCode"})
        add("lookup_code", f"{lt}/{code}", " + ".join(files), **rec)  # DisplaySequence only where given
    # Order types (ORA_DOO_ORDER_TYPES): Run 01 ot_*, Run 03 C3, Run 06 R1
    for code, files in {"FSCRT_SO_TRAIL_DEALER_F01": ["ot_trail", "c3_trail"],
                        "FSCRT_SO_WARRANTY_SWAP_F01": ["ot_warranty", "c3_warranty"],
                        "FSCRT_SO_CONSIGN_F06": ["r1_consign"]}.items():
        rec = {"EndDateActive": ""}
        for f in files:
            src = p1 if f.startswith("ot_") else (p3 if f.startswith("c3") else p6)
            rec.update({k: v for k, v in load(src / f"{f}.json").items() if k != "LookupCode"})
        add("order_type", code, " + ".join(files), **rec)
    # Grouping rules: Run 04 GRP1 design, Run 06 GRP6 design
    for src in (RUNS / "_fscr_run_04_create16/payloads/grp/design.json", p6 / "grp6/design.json"):
        ops = load(src)["operations"]
        g = [o for o in ops if o["entity"] == "AR_AI_GROUPING_RULE"][0]
        cls = sorted(o["targetKey"]["Class11"] for o in ops if o["entity"] == "ORA_AR_AI_GRP_TXN_TYPE")
        add("grouping_rule", g["targetKey"]["Name"], str(src.relative_to(RUNS)), Description=g["values"]["Description"],
            StartDate=g["values"]["StartDate"], EndDate="", Classes=",".join(cls))
    # Business units: input_records.md [1] (Run 03 C4 manager change was refused by FSCR -> unchanged)
    add("business_unit", "FSCRT_Quillon Ridge Outfitters West F01", "Run01 input [1]", DefaultSetCode="ENTERPRISE",
        Status="A", ManagerListName="Smith, Aron", InternalLocationCode="")
    add("business_unit", "FSCRT_Brindle Harbor Marine Supply F01", "Run01 input [1]", DefaultSetCode="ENTERPRISE",
        Status="A", ManagerListName="Yaqub, Younas", InternalLocationCode="LHR_WH")
    # Price lists: Run 01 pl1/pl2 (+ approved), Run 03 C5 for Brindle. Brindle line type/calc method 'default'.
    bu = {"300000394664006": "FSCRT_Quillon Ridge Outfitters West F01", "300000394664009": "FSCRT_Brindle Harbor Marine Supply F01"}
    for files in (["pl1"], ["pl2", "c5_pl"]):
        rec = {}
        for f in files:
            rec.update(load((p1 if f.startswith("pl") else p3) / f"{f}.json"))
        out = {"PriceListDescription": rec["PriceListDescription"], "PriceListTypeCode": rec["PriceListTypeCode"],
               "BusinessUnit": bu[str(rec["BusinessUnitId"])], "CurrencyCode": rec["CurrencyCode"],
               "StatusCode": "APPROVED", "StartDate": rec["StartDate"], "EndDate": rec.get("EndDate", ""),
               "PricingChargeDefinitionId": rec["PricingChargeDefinitionId"],
               "AccessSets": ",".join(sorted(a["AccessSetCode"] for a in rec["accessSets"]))}
        for k in ("LineTypeCode", "CalculationMethodCode"):
            if k in rec:
                out[k] = rec[k]
        add("price_list", rec["PriceListName"], " + ".join(files), **out)
    # Organization customers: Run 01 customers.json (orgA/orgB) + Run 03 C6 (Kestrel account description)
    cust = load(p1 / "customers.json")
    c6 = load(p3 / "c6_kestrel.json")["account"]
    for k, extra in (("orgA", c6), ("orgB", {})):
        c = cust[k]
        acct = dict(c["account"], **extra)
        site = c["account_site"]
        out = {"DUNSNumber": c["party_profile"]["DUNSNumberC"], "TaxpayerIdentificationNumber": c["party_profile"]["JgzzFiscalCode"],
               "AccountName": acct["AccountName"], "CustomerType": acct["CustomerType"],
               "CustomerClassCode": acct["CustomerClassCode"], "AccountEstablishedDate": acct["AccountEstablishedDate"],
               "AccountTerminationDate": acct["AccountTerminationDate"],
               "DFF_accountNotesOther": c["account_dff"]["accountNotesOther"],
               "DFF_shippingInstrustions": c["account_dff"]["shippingInstrustions"],
               "DFF_customerAgreement": c["account_dff"]["customerAgreement"],
               "SiteSetId": site["SetId"], "SiteStartDate": site["StartDate"], "SiteEndDate": site["EndDate"],
               "KeyAccountFlag": site["KeyAccountFlag"], "TpHeaderId": site["TpHeaderId"],
               "EceTpLocationCode": site["EceTpLocationCode"], "TranslatedCustomerName": site["TranslatedCustomerName"],
               "SiteUses": ",".join(sorted(f"{u['SiteUseCode']}:{norm(u['PrimaryFlag'])}" for u in c["site_uses"])),
               "Address1": c["location"]["Address1"], "Address2": c["location"]["Address2"], "City": c["location"]["City"],
               "State": c["location"]["State"], "PostalCode": c["location"]["PostalCode"], "Country": c["location"]["Country"],
               "Mailstop": c["party_site"]["Mailstop"]}
        add("org_customer", c["party_profile"]["OrganizationName"], "Run01 customers.json" + (" + Run03 C6" if extra else ""), **out)
    o = R8 / "expected/best_start.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    for r in E.values():
        r["fields"] = {k: norm(v) for k, v in r["fields"].items()}
        r["fingerprint"] = fp(r["fields"], r["fields"].keys())
    o.write_text(json.dumps(E, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"expected records: {len(E)} -> {o}")


# ------------------------------------------------------------------ actual
def zip_csv(label, task, member):
    z = sorted((EXPORTS / label / task).glob("*.zip"))
    if len(z) != 1:
        sys.exit(f"INPUT_VALIDATION: expected 1 ZIP in {EXPORTS / label / task}, found {len(z)}")
    with zipfile.ZipFile(z[0]) as zf:
        return list(csv.DictReader(io.TextIOWrapper(zf.open(member), encoding="utf-8-sig"))), z[0].name


def build_actual(label):
    A, src = {}, {}

    def add(area, key, **f):
        A[f"{area}|{key}"] = {"area": area, "key": key, "fields": {k: norm(v) for k, v in f.items()}}

    pt, src["payment_term"] = zip_csv(label, "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS", "AR_PAYMENT_TERM.csv")
    ln, _ = zip_csv(label, "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS", "AR_PAYMENT_TERM_LINE.csv")
    dc, _ = zip_csv(label, "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS", "AR_PAYMENT_TERM_DISCOUNT.csv")
    for r in pt:
        if r["Name"].startswith("FSCRT_"):
            k = (r["Name"], r["SetCode"])
            lines = sorted((int(x["SequenceNum"]), norm(x["RelativeAmount"]), norm(x["DueDays"])) for x in ln
                           if (x["AR_PAYMENT_TERM.Name"], x["AR_PAYMENT_TERM.SetCode"]) == k)
            disc = sorted((int(x["AR_PAYMENT_TERM_LINE.SequenceNum"]), norm(x["DiscountPercent"]), norm(x["DiscountDays"]))
                          for x in dc if (x["AR_PAYMENT_TERM.Name"], x["AR_PAYMENT_TERM.SetCode"]) == k)
            add("payment_term", r["Name"], SetCode=r["SetCode"], Description=r["Description"],
                StartDateActive=r["StartDateActive"], EndDateActive=r["EndDateActive"],
                Lines=";".join(":".join(map(str, t)) for t in lines), Discounts=";".join(":".join(map(str, t)) for t in disc))
    lt, src["lookups"] = zip_csv(label, "DOO_MANAGE_ORCHESTRATION_LOOKUPS", "FND_APP_STANDARD_LOOKUP.csv")
    lc, _ = zip_csv(label, "DOO_MANAGE_ORCHESTRATION_LOOKUPS", "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv")
    for r in lt:
        if r["LookupType"].startswith("FSCRT_"):
            add("lookup_type", r["LookupType"], **{k: r[k] for k in ("Meaning", "Description", "ModuleId", "CustomizationLevel", "RestAccessSecured")})
    for r in lc:
        t = r["FND_APP_STANDARD_LOOKUP.LookupType"]
        f = {k: r[k] for k in ("Meaning", "Description", "EnabledFlag", "EndDateActive", "DisplaySequence", "Tag")}
        if t.startswith("FSCRT_"):
            add("lookup_code", f"{t}/{r['LookupCode']}", **f)
        elif t == "ORA_DOO_ORDER_TYPES" and r["LookupCode"].startswith("FSCRT_"):
            add("order_type", r["LookupCode"], **f)
    gr, src["grouping_rule"] = zip_csv(label, "AR_MANAGE_AUTOINVOICE_GROUPING_RULES", "AR_AI_GROUPING_RULE.csv")
    gc, _ = zip_csv(label, "AR_MANAGE_AUTOINVOICE_GROUPING_RULES", "ORA_AR_AI_GRP_TXN_TYPE.csv")
    for r in gr:
        if r["Name"].startswith("FSCRT_"):
            add("grouping_rule", r["Name"], Description=r["Description"], StartDate=r["StartDate"], EndDate=r["EndDate"],
                Classes=",".join(sorted(x["Class11"] for x in gc if x["AR_AI_GROUPING_RULE.Name"] == r["Name"])))
    bu, src["business_unit"] = zip_csv(label, "FUN_MANAGE_BUSINESS_UNIT", "FUN_BUSINESS_UNIT.csv")
    for r in bu:
        if r["Name"].startswith("FSCRT_"):
            add("business_unit", r["Name"], **{k: r[k] for k in ("DefaultSetCode", "Status", "ManagerListName", "InternalLocationCode")})
    raw = R8 / "actual" / label / "raw"
    for r in load(raw / "priceLists_fscrt.json")["items"]:
        f = {k: r.get(k) for k in ("PriceListDescription", "PriceListTypeCode", "BusinessUnit", "CurrencyCode", "StatusCode",
                                   "StartDate", "EndDate", "PricingChargeDefinitionId", "LineTypeCode", "CalculationMethodCode")}
        f["AccessSets"] = ",".join(sorted(a["AccessSetCode"] for a in r.get("accessSets", {}).get("items", [])))
        add("price_list", r["PriceListName"], **f)
    src["price_list"] = "rget.py priceLists (Claude's GET reader)"
    accts = {}
    for p in raw.glob("acct_*.json"):
        d = load(p)
        x = d[0] if isinstance(d, list) else ""
        if "FSCR_READ_ERROR" in json.dumps(d)[:200]:
            continue
        accts[re.search(r"<ns2:PartyId>(\d+)<", x)[1]] = x
    for o in load(raw / "hubOrganizations_fscrt.json")["items"]:
        a = o.get("Address", {})
        a = a.get("items", []) if isinstance(a, dict) else (a or [])
        a = ([x for x in a if x.get("PrimaryFlag")] or a or [{}])[0]
        f = {"DUNSNumber": o.get("DUNSNumber"), "TaxpayerIdentificationNumber": o.get("TaxpayerIdentificationNumber"),
             **{k: a.get(k) for k in ("Address1", "Address2", "City", "State", "PostalCode", "Country", "Mailstop")}}
        x = accts.get(str(o["PartyId"]))
        if x:  # FSCR customer_soap_read getCustomerAccount response
            first = lambda tag, s=x: (re.search(rf"<ns\d+:{tag}>([^<]*)</", s) or [None, None])[1]
            site = x.split("<ns2:CustomerAccountSite", 1)[1]
            f.update({k: first(k) for k in ("AccountName", "CustomerType", "CustomerClassCode", "AccountEstablishedDate", "AccountTerminationDate")})
            f.update({"DFF_" + k: first(k) for k in ("accountNotesOther", "shippingInstrustions", "customerAgreement")})
            f.update({"SiteSetId": first("SetId", site), "SiteStartDate": first("StartDate", site), "SiteEndDate": first("EndDate", site),
                      **{k: first(k, site) for k in ("KeyAccountFlag", "TpHeaderId", "EceTpLocationCode", "TranslatedCustomerName")}})
            uses = re.findall(r"<ns2:SiteUseCode>(\w+)</ns2:SiteUseCode><ns2:PrimaryFlag>(\w+)<", x)
            f["SiteUses"] = ",".join(sorted(f"{c}:{norm(p)}" for c, p in uses))
        add("org_customer", o["OrganizationName"], **f)
    src["org_customer"] = "rget.py hubOrganizations (party, address) + FSCR customer_soap_read (account, site, uses, DFF)"
    o = R8 / "actual" / label / "normalized.json"
    o.write_text(json.dumps({"sources": src, "records": A}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"actual records ({label}): {len(A)} -> {o}")


# ------------------------------------------------------------------ compare
DEFAULT_FIELDS = {}  # for extra records: hash over all normalised fields read


def compare(label):
    E = load(R8 / "expected/best_start.json")
    A = load(R8 / "actual" / label / "normalized.json")["records"]
    rows = []
    for k in sorted(set(E) | set(A), key=lambda s: (s.split("|")[0], s)):
        e, a = E.get(k), A.get(k)
        if e and a:
            fe, fa = e["fingerprint"], fp(a["fields"], e["fields"].keys())
            diff = [f for f in sorted(e["fields"]) if norm(a["fields"].get(f)) != e["fields"][f]]
            st = "match" if fe == fa else "different"
            rows.append(dict(area=e["area"], key=e["key"], status=st, expected_md5=fe, actual_md5=fa,
                             fields=len(e["fields"]), diff=[{"field": f, "expected": e["fields"][f], "actual": norm(a["fields"].get(f))} for f in diff]))
        elif e:
            rows.append(dict(area=e["area"], key=e["key"], status="missing", expected_md5=e["fingerprint"], actual_md5="", fields=len(e["fields"]), diff=[]))
        else:
            rows.append(dict(area=a["area"], key=a["key"], status="extra", expected_md5="",
                             actual_md5=fp(a["fields"], a["fields"].keys()), fields=len(a["fields"]), diff=[]))
    out = R8 / "results" / f"{label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    cnt = {s: sum(r["status"] == s for r in rows) for s in ("match", "different", "missing", "extra")}
    md = [f"# Comparison `{label}`", "", f"Totals: {cnt}", "", "| Area | Record | Status | Expected MD5 | Actual MD5 | Differing fields |", "|---|---|---|---|---|---|"]
    for r in rows:
        d = "; ".join(f"{x['field']}: '{x['expected']}' -> '{x['actual']}'" for x in r["diff"])
        md.append(f"| {r['area']} | {r['key']} | **{r['status']}** | {r['expected_md5'][:12]} | {r['actual_md5'][:12]} | {d} |")
    (R8 / "results" / f"{label}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{label}: {cnt}")
    for r in rows:
        if r["status"] != "match":
            print(" ", r["status"], r["area"], r["key"], [(x["field"], x["expected"], x["actual"]) for x in r["diff"]])


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"expected": lambda: build_expected(), "actual": lambda: build_actual(sys.argv[2]), "compare": lambda: compare(sys.argv[2])}[cmd]()
