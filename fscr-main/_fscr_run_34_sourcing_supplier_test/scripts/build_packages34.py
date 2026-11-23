"""Run 34: build FSM CSV packages holding ONLY new FSCRT_ rows (reuses Run 33's build_packages33.py method).
Headers + metadata XML are copied unchanged from the ETIA-TEST export (export_before/<TASK>/unz).
Usage: build_packages34.py <TASK_CODE> [...]"""
import csv, zipfile, shutil, sys
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
def build(task, files):
    src = RUN / "export_before" / task / "unz"; out = RUN / "payload" / task; out.mkdir(parents=True, exist_ok=True)
    for n in list(out.glob("*")):
        if n.is_file(): n.unlink()
    for name, rows in files.items():
        h = next(csv.reader(open(src / name, encoding="utf-8-sig", newline="")))
        for r in rows: assert set(r) <= set(h), (name, set(r) - set(h))
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(h)
            for r in rows: w.writerow([r.get(c, "") for c in h])
    shutil.copy(src / "ASM_SETUP_CSV_METADATA.xml", out / "ASM_SETUP_CSV_METADATA.xml")
    z = out / f"{task.lower()}_fscrt.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in ["ASM_SETUP_CSV_METADATA.xml", *files]: zf.write(out / n, n)
    print("wrote", z); return z
CF, CFN = "FSCRT_R34_CF", "FSCRT_R34 Freight"
AG = "FSCRT_R34 Agency"
SPEC = {
 "PON_MANAGE_COST_FACTORS": {
  "PON_PRICE_ELEMENT_TYPES.csv": [dict(PriceElementCode=CF, Name=CFN, Description="FSCR Run 34 test cost factor", PricingBasis="FIXED_AMOUNT", EnabledFlag="Y", SystemFlag="N", CostFactorType="EXTERNAL")],
  "PON_PRICE_ELEMENT_TYPES_TRANSLATION.csv": [{"PON_PRICE_ELEMENT_TYPES.PriceElementCode": CF, "Name": CFN, "Description": "FSCR Run 34 test cost factor", "Language": "US", "SourceLang": "US"}]},
 "ORA_POZ_MANAGE_CERTIFYING_AGENCIES": {
  "ORA_POZ_CERTIFYING_AGENCY.csv": [dict(Name=AG, Description="FSCR Run 34 test certifying agency")],
  "ORA_POZ_CERT_AGENCY_BUS_CLASS.csv": [{"ORA_POZ_CERTIFYING_AGENCY.Name": AG, "ClassificationCode": "SMALL_BUSINESS"}]},
}
AUDIT = {"CreationDate", "CreatedBy", "LastUpdateDate", "LastUpdatedBy", "LastUpdateLogin"}
def rows(task, name): return list(csv.DictReader(open(RUN / "export_before" / task / "unz" / name, encoding="utf-8-sig")))
def copy_of(r, **kw): return {**{k: v for k, v in r.items() if k not in AUDIT}, **kw}
# Negotiation style: flags copied from the seeded Standard_Negotiation row (read only), new code and name.
NS, NST, NSN = "PON_MANAGE_NEGOTIATION_STYLES", "FSCRT_R34_STYLE", "FSCRT_R34 Style"
if (RUN / "export_before" / NS / "unz").exists():
    base = next(r for r in rows(NS, "PON_NEGOTIATION_STYLES.csv") if r["StyleCode"] == "Standard_Negotiation")
    dts = [r for r in rows(NS, "PON_DOCTYPE_STYLES.csv") if r["PON_NEGOTIATION_STYLES.StyleCode"] == "Standard_Negotiation"]
    dtt = [r for r in rows(NS, "PON_DOCTYPE_STYLES_TRANSLATION.csv") if r["PON_NEGOTIATION_STYLES.StyleCode"] == "Standard_Negotiation" and r["Language"] == "US"]
    SPEC[NS] = {
     "PON_NEGOTIATION_STYLES.csv": [copy_of(base, StyleCode=NST, StyleName=NSN, Description="FSCR Run 34 test negotiation style", SystemFlag="N", Status="ACTIVE")],
     "PON_NEGOTIATION_STYLES_TRANSLATION.csv": [{"PON_NEGOTIATION_STYLES.StyleCode": NST, "StyleName": NSN, "Description": "FSCR Run 34 test negotiation style", "Language": "US", "SourceLang": "US"}],
     "PON_DOCTYPE_STYLES.csv": [copy_of(r, **{"PON_NEGOTIATION_STYLES.StyleCode": NST}) for r in dts],
     "PON_DOCTYPE_STYLES_TRANSLATION.csv": [copy_of(r, **{"PON_NEGOTIATION_STYLES.StyleCode": NST}) for r in dtt]}
# Supplier qualification value set: independent, 2 values. ModuleId = Supplier Qualification (PrcPoqCommon), read from Oracle messages REST.
VS = "FSCRT_R34_VS"
SPEC["ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_VALUE_SETS"] = {
 "FND_APP_FLEX_VALUE_SET.csv": [dict(ValueSetCode=VS, ModuleId="AFBED13209D2FBA6E0401490D3C538E3", Description="FSCR Run 34 test value set", ValidationType="INDEP",
        ValueDataType="VARCHAR2", ValueSubtype="TEXT", MaximumLength="30", UppercaseOnlyFlag="N", ZeroFillFlag="N", SecurityEnabledFlag="N")],
 "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv": [{"FND_APP_FLEX_VALUE_SET.ValueSetCode": VS, "Value": v, "Description": f"FSCR Run 34 value {v}", "EnabledFlag": "Y", "SummaryFlag": "N"} for v in ("FSCRT_A", "FSCRT_B")]}
# Attempt 2 for the agency: Oracle failed on the blank AgencyId ('For input string: ""', a number column). Drop AgencyId from the
# CSV header and from the metadata attribute list so Oracle assigns the ID (no ID is invented).
def drop_agency_id(z):
    import re
    out = z.parent; csvp = out / "ORA_POZ_CERTIFYING_AGENCY.csv"
    rr = list(csv.reader(open(csvp, encoding="utf-8", newline=""))); i = rr[0].index("AgencyId")
    with open(csvp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); [w.writerow(r[:i] + r[i + 1:]) for r in rr]
    mp = out / "ASM_SETUP_CSV_METADATA.xml"; m = mp.read_text(encoding="utf-8")
    m2 = m.replace("<XmlAttributeList>AgencyId,Name,Description,EndDate</XmlAttributeList>", "<XmlAttributeList>Name,Description,EndDate</XmlAttributeList>")
    m2 = m2.replace("<XmlAttributeTypeList>long,string,string,date</XmlAttributeTypeList>", "<XmlAttributeTypeList>string,string,date</XmlAttributeTypeList>", 1)
    assert m2 != m; mp.write_text(m2, encoding="utf-8")
    import re as _r
    for k in _r.findall(r"<CSVFileHeader[^>]*>[^<]*AgencyId[^<]*", m2): print("header still names AgencyId:", k[:120])
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in ["ASM_SETUP_CSV_METADATA.xml", "ORA_POZ_CERTIFYING_AGENCY.csv", "ORA_POZ_CERT_AGENCY_BUS_CLASS.csv"]: zf.write(out / n, n)
if __name__ == "__main__":
    for t in sys.argv[1:]:
        z = build(t, SPEC[t])
        if t == "ORA_POZ_MANAGE_CERTIFYING_AGENCIES": drop_agency_id(z)
