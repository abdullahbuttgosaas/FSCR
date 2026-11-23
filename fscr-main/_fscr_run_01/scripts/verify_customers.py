"""Read back each created customer and compare with what was sent. Read-only.
Account/site/site-use/account DFF and location (+DFF) come from FSCR's own SOAP reader
(customer_soap_read.read, operations 'customer-account' and 'location'); party name, DUNS and
taxpayer id come from the CRM hub REST resources via rest_diag-style GETs."""
import json, re, sys, subprocess
from pathlib import Path
E = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01")
W = E / "fscr-work"
sys.path.insert(0, str(W / "pillars/erp/financials/customers/manage-customer-uploads/scripts"))
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
import customer_soap_read as csr

props_path = W / "core/auth/fusionEnv.properties"
props = fa.oauth_service_properties(fa.read_properties(props_path), "standard")
core = csr.load_core(W)
data = json.loads((E / "payloads/customers.json").read_text(encoding="utf-8"))


def fscr_xml(op, **sel):
    out = csr.read(core, props_path, fa.token_cache_path(props), props["restBaseUrl"], op, sel)
    return json.dumps(out, default=lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else str(b))


def val(xml, tag, after=None):
    s = xml if after is None else xml[xml.find(after):]
    m = re.search(r"<(?:\w+:)?%s>([^<]*)</(?:\w+:)?%s>" % (tag, tag), s)
    return m.group(1) if m else None


def rest(path, *q):
    args = [sys.executable, str(E / "scripts/rest_diag.py"), "GET", path]
    for x in q: args += ["--query", x]
    out = E / "evidence/customers/_rest_tmp.json"
    subprocess.run(args + ["--out", str(out)], capture_output=True, text=True)
    return json.loads(out.read_text(encoding="utf-8"))


report = {}
for key, c in data.items():
    st = json.loads((E / f"evidence/customers/{key}_state.json").read_text())
    res = {"ids": st, "checks": [], "mismatches": []}
    def chk(label, sent, got):
        sent, got = str(sent), "" if got is None else str(got)
        ok = sent == got
        res["checks"].append((label, sent, got, ok))
        if not ok: res["mismatches"].append(label)
    acc = fscr_xml("customer-account", account_id=st["CustomerAccountId"])
    (E / f"evidence/customers/{key}_readback_account.json").write_text(acc, encoding="utf-8")
    for f, v in c["account"].items(): chk("account." + f, v, val(acc, f))
    for f, v in c["account_dff"].items(): chk("accountDFF." + f, v, val(acc, f))
    site_part = acc[acc.find("CustomerAccountSiteId>"):]
    for f, v in c["account_site"].items(): chk("site." + f, v, val(site_part, f))
    uses = re.findall(r"<(?:\w+:)?SiteUseCode>([^<]*)<", acc)
    prim = re.findall(r"<(?:\w+:)?PrimaryFlag>([^<]*)<", acc)
    chk("siteUses", sorted(u["SiteUseCode"] for u in c["site_uses"]), sorted(uses))
    chk("siteUses.primary", ["true"] * len(c["site_uses"]), prim)
    for u in c["site_uses"]:
        seg = acc[acc.find(u["SiteUseCode"]):]
        chk(f"siteUse.{u['SiteUseCode']}.StartDate", u["StartDate"], val(seg, "StartDate"))
    try:
        loc = fscr_xml("location", location_id=st["LocationId"]); res["location_source"] = "FSCR customer_soap_read"
    except Exception as e:
        sys.path.insert(0, str(E / "scripts")); import customers_soap as cs
        _, loc, _ = cs.call("FoundationPartiesLocationService", f"<loc_t:getLocation><loc_t:locationId>{st['LocationId']}</loc_t:locationId></loc_t:getLocation>")
        res["location_source"] = f"own getLocation (FSCR read failed: {e})"
    (E / f"evidence/customers/{key}_readback_location.json").write_text(loc, encoding="utf-8")
    for f, v in c["location"].items():
        if f != "CreatedByModule": chk("location." + f, v, val(loc, f))
    for f, v in c["location_dff"].items(): chk("locationDFF." + f, v, val(loc, f))
    if c["party_type"] == "ORGANIZATION":
        p = rest("/crmRestApi/resources/11.13.18.05/hubOrganizations", f"q=PartyId={st['PartyId']}", "onlyData=true", "expand=Address")["items"][0]
        chk("party.OrganizationName", c["party_profile"]["OrganizationName"], p.get("OrganizationName"))
        chk("party.DUNS", c["party_profile"]["DUNSNumberC"], p.get("DUNSNumberC") or p.get("DUNSNumber"))
        chk("party.TaxpayerId", c["party_profile"]["JgzzFiscalCode"], p.get("JgzzFiscalCode") or p.get("TaxpayerIdentificationNumber"))
    else:
        p = rest("/crmRestApi/resources/11.13.18.05/hubPersons", f"q=PartyId={st['PartyId']}", "onlyData=true", "expand=Address")["items"][0]
        pp = c["party_profile"]
        chk("party.FirstName", pp["PersonFirstName"], p.get("FirstName"))
        chk("party.LastName", pp["PersonLastName"], p.get("LastName"))
        if "PersonMiddleName" in pp: chk("party.MiddleName", pp["PersonMiddleName"], p.get("MiddleName"))
        if "PersonNameSuffix" in pp: chk("party.Suffix", pp["PersonNameSuffix"], p.get("NameSuffix"))
        chk("party.Prefix", pp["PersonPreNameAdjunct"], p.get("Title") or p.get("Salutation"))
        chk("party.TaxpayerId", pp["JgzzFiscalCode"], p.get("JgzzFiscalCode") or p.get("TaxpayerIdentificationNumber"))
        res["party_name"] = p.get("PersonName") or p.get("PartyName")
    for f in ("PartySiteName", "Mailstop"):
        if f in c["party_site"]:
            items = p.get("Address", [])
            items = items.get("items", items) if isinstance(items, dict) else items
            got = items[0].get("PartySiteName" if f == "PartySiteName" else "Mailstop") if items else None
            chk("partySite." + f, c["party_site"][f], got)
    res["party_raw_keys"] = sorted(k for k in p if any(x in k for x in ("DUNS", "Taxpayer", "Jgzz", "Title", "Salutation", "Suffix", "Name")))
    report[key] = res
    print(key, "checks", len(res["checks"]), "mismatches", res["mismatches"])
(E / "evidence/customers/verify_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
