"""Create Receivables customers (organization or person) on Fusion through Oracle's TCA SOAP services.

Why: FSCR has no working create route for customers in this pod. Its only customer skill
(manage-customer-uploads) is FBDI-only, organization-only, self-blocking, and ETIA-TEST's Data Loader
has no FBDI business objects. FSCR's own customer reads use these same SOAP services
(customer_soap_contract.py), so this script uses them for create.

Steps per customer (each step persisted to state JSON so nothing is re-sent after a success):
  1 FoundationPartiesLocationService.createLocation (address + Location DFF)
  2 FoundationPartiesOrganizationService.createOrganization / FoundationPartiesPersonService.createPerson
    (party + party site on that location)
  3 CustomerAccountService.createCustomerAccount (account + account DFF + account site in the set
    + site uses = address purposes)
Token: FSCR fusion_auth cache (never printed). No automatic retry of any create.
Usage: customers_soap.py <customers.json> <key> [--step location|party|account|all]
"""
import gzip, json, re, sys, os, urllib.request, urllib.error
from pathlib import Path
from xml.sax.saxutils import escape

E = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01")
R = E / "fscr-work"
SOAPD = E / "evidence" / "soap"
sys.path.insert(0, str(R / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa

NS = {
    "loc_t": "http://xmlns.oracle.com/apps/cdm/foundation/parties/locationService/applicationModule/types/",
    "loc": "http://xmlns.oracle.com/apps/cdm/foundation/parties/locationService/",
    "locdff": "http://xmlns.oracle.com/apps/cdm/foundation/parties/flex/location/",
    "org_t": "http://xmlns.oracle.com/apps/cdm/foundation/parties/organizationService/applicationModule/types/",
    "org": "http://xmlns.oracle.com/apps/cdm/foundation/parties/organizationService/",
    "per_t": "http://xmlns.oracle.com/apps/cdm/foundation/parties/personService/applicationModule/types/",
    "per": "http://xmlns.oracle.com/apps/cdm/foundation/parties/personService/",
    "par": "http://xmlns.oracle.com/apps/cdm/foundation/parties/partyService/",
    "acc_t": "http://xmlns.oracle.com/apps/cdm/foundation/parties/customerAccountService/applicationModule/types/",
    "acc": "http://xmlns.oracle.com/apps/cdm/foundation/parties/customerAccountService/",
    "accdff": "http://xmlns.oracle.com/apps/cdm/foundation/parties/flex/custAccount/",
}


def order_of(xsd_glob, type_name):
    for f in sorted(SOAPD.glob(xsd_glob)):
        s = f.read_text(encoding="utf-8")
        m = re.search(r'<xsd:complexType name="%s"(.*?)</xsd:complexType>' % type_name, s, re.S)
        if m:
            return re.findall(r'<xsd:element[^>]*name="([^"]+)"', m.group(1))
    raise SystemExit(f"type {type_name} not found in {xsd_glob}")


def el(prefix, fields, order, children=None):
    """Serialize scalar fields (and nested child XML strings) in XSD sequence order."""
    children = children or {}
    unknown = (set(fields) | set(children)) - set(order)
    if unknown:
        raise SystemExit(f"fields not in schema: {unknown}")
    out = []
    for name in order:
        if name in fields and fields[name] not in (None, ""):
            out.append(f"<{prefix}:{name}>{escape(str(fields[name]))}</{prefix}:{name}>")
        for c in children.get(name, []):
            out.append(c)
    return "".join(out)


def call(service, body):
    props = fa.oauth_service_properties(fa.read_properties(R / "core/auth/fusionEnv.properties"), "standard")
    token = fa.load_cached_access_token(props)
    if not token:
        raise SystemExit("TOKEN_EXPIRED")
    nsdecl = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items())
    env = f'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" {nsdecl}><soapenv:Header/><soapenv:Body>{body}</soapenv:Body></soapenv:Envelope>'
    req = urllib.request.Request(props["restBaseUrl"].rstrip("/") + f"/crmService/{service}", data=env.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Content-Type", "text/xml; charset=utf-8")
    req.add_header("Accept-Encoding", "identity")
    def dec(raw):
        return (gzip.decompress(raw) if raw[:2] == bytes([0x1F, 0x8B]) else raw).decode("utf-8", "replace")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, dec(r.read()), env
    except urllib.error.HTTPError as e:
        return e.code, dec(e.read()), env


def first(tag, text):
    m = re.search(r"<(?:\w+:)?%s>([^<]*)</(?:\w+:)?%s>" % (tag, tag), text)
    return m.group(1) if m else None


def fault(text):
    m = re.search(r"<faultstring>(.*?)</faultstring>", text, re.S)
    return m.group(1).strip() if m else None


def save(state_path, state):
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main():
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    key = sys.argv[2]
    step = sys.argv[sys.argv.index("--step") + 1] if "--step" in sys.argv else "all"
    c = data[key]
    state_path = E / "evidence" / "customers" / f"{key}_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    logdir = state_path.parent

    if step in ("location", "all") and "LocationId" not in state:
        dff = el("locdff", c["location_dff"], order_of("*LocationInformation.xsd", "LocationInformation"))
        loc = el("loc", c["location"], order_of("FoundationPartiesLocationService_Location.xsd", "Location"),
                 {"LocationInformation": [f"<loc:LocationInformation>{dff}</loc:LocationInformation>"]})
        st, txt, env = call("FoundationPartiesLocationService", f"<loc_t:createLocation><loc_t:location>{loc}</loc_t:location></loc_t:createLocation>")
        (logdir / f"{key}_1_location_request.xml").write_text(env, encoding="utf-8")
        (logdir / f"{key}_1_location_response.xml").write_text(txt, encoding="utf-8")
        lid = first("LocationId", txt) if st == 200 else None
        print("createLocation HTTP", st, "LocationId", lid, "fault", fault(txt))
        if not lid:
            return 1
        state["LocationId"] = lid; save(state_path, state)

    if step in ("party", "all") and "PartyId" not in state:
        is_org = c["party_type"] == "ORGANIZATION"
        site = dict(c["party_site"], LocationId=state["LocationId"])
        site_xml = el("par", site, order_of("FoundationPartiesOrganizationService_PartySite.xsd", "PartySite"))
        usage_xml = el("par", {"PartyUsageCode": "CUSTOMER", "CreatedByModule": "HZ_WS"},
                       order_of("FoundationPartiesOrganizationService_PartyUsageAssignment.xsd", "PartyUsageAssignment"))
        if is_org:
            prof = el("org", c["party_profile"], order_of("FoundationPartiesOrganizationService_OrganizationProfile.xsd", "OrganizationProfile"))
            party = el("org", c["party"], order_of("FoundationPartiesOrganizationService_OrganizationParty.xsd", "OrganizationParty"),
                       {"PartySite": [f"<org:PartySite>{site_xml}</org:PartySite>"],
                        "PartyUsageAssignment": [f"<org:PartyUsageAssignment>{usage_xml}</org:PartyUsageAssignment>"],
                        "OrganizationProfile": [f"<org:OrganizationProfile>{prof}</org:OrganizationProfile>"]})
            svc, body = "FoundationPartiesOrganizationService", f"<org_t:createOrganization><org_t:organizationParty>{party}</org_t:organizationParty></org_t:createOrganization>"
        else:
            pprof = el("per", c["party_profile"], order_of("FoundationPartiesPersonService_PersonProfile.xsd", "PersonProfile")) if c.get("party_profile") else ""
            party = el("per", c["party"], order_of("FoundationPartiesPersonService_Person.xsd", "Person"),
                       {"PartySite": [f"<per:PartySite>{site_xml}</per:PartySite>"],
                        "PersonProfile": [f"<per:PersonProfile>{pprof}</per:PersonProfile>"] if pprof else [],
                        "PartyUsageAssignment": [f"<per:PartyUsageAssignment>{usage_xml}</per:PartyUsageAssignment>"]})
            svc, body = "FoundationPartiesPersonService", f"<per_t:createPerson><per_t:personParty>{party}</per_t:personParty></per_t:createPerson>"
        st, txt, env = call(svc, body)
        (logdir / f"{key}_2_party_request.xml").write_text(env, encoding="utf-8")
        (logdir / f"{key}_2_party_response.xml").write_text(txt, encoding="utf-8")
        pid, sid = (first("PartyId", txt), first("PartySiteId", txt)) if st == 200 else (None, None)
        print("create party HTTP", st, "PartyId", pid, "PartySiteId", sid, "PartyNumber", first("PartyNumber", txt), "fault", fault(txt))
        if not (pid and sid):
            return 1
        state.update(PartyId=pid, PartySiteId=sid); save(state_path, state)

    if step in ("account", "all") and "CustomerAccountId" not in state:
        su_order = order_of("CustomerAccountSiteUse.xsd", "CustomerAccountSiteUse")
        uses = [f"<acc:CustomerAccountSiteUse>{el('acc', u, su_order)}</acc:CustomerAccountSiteUse>" for u in c["site_uses"]]
        site = dict(c["account_site"], PartySiteId=state["PartySiteId"])
        site_xml = el("acc", site, order_of("CustomerAccountSite.xsd", "CustomerAccountSite"), {"CustomerAccountSiteUse": uses})
        dff = el("accdff", c["account_dff"], order_of("CustAcctInformation.xsd", "CustAcctInformation"))
        acct = dict(c["account"], PartyId=state["PartyId"])
        acct_xml = el("acc", acct, order_of("CustomerAccount.xsd", "CustomerAccount"),
                      {"CustomerAccountSite": [f"<acc:CustomerAccountSite>{site_xml}</acc:CustomerAccountSite>"],
                       "CustAcctInformation": [f"<acc:CustAcctInformation>{dff}</acc:CustAcctInformation>"]})
        st, txt, env = call("CustomerAccountService", f"<acc_t:createCustomerAccount><acc_t:customerAccount>{acct_xml}</acc_t:customerAccount></acc_t:createCustomerAccount>")
        (logdir / f"{key}_3_account_request.xml").write_text(env, encoding="utf-8")
        (logdir / f"{key}_3_account_response.xml").write_text(txt, encoding="utf-8")
        aid = first("CustomerAccountId", txt) if st == 200 else None
        print("createCustomerAccount HTTP", st, "CustomerAccountId", aid, "AccountNumber", first("AccountNumber", txt),
              "SiteUseIds", re.findall(r"<(?:\w+:)?SiteUseId>(\d+)<", txt), "fault", fault(txt))
        if not aid:
            return 1
        state.update(CustomerAccountId=aid, AccountNumber=first("AccountNumber", txt),
                     CustomerAccountSiteId=first("CustomerAccountSiteId", txt),
                     SiteUseIds=re.findall(r"<(?:\w+:)?SiteUseId>(\d+)<", txt)); save(state_path, state)
    print(json.dumps(state))
    return 0


if __name__ == "__main__":
    sys.exit(main())
