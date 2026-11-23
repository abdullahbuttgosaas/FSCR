"""Build the FSM CSV import ZIP for FUN_MANAGE_BUSINESS_UNIT from a fresh FSCR template export.
Why: FSCR's BU task guide gives the fill rules (ora_bulk_intake.md 'Template-Based New BU Preparation')
but ships no builder. Rules applied: Name, DefaultSetCode, user fields; Classification/ClassificationCode/
OrgInformationContext = FUN_BUSINESS_UNIT; Status A; OrganizationCode and effective dates blank; child CSVs header-only.
Template members and metadata XML are copied unchanged, in template order."""
import csv, io, sys, zipfile, json
tpl, out = sys.argv[1], sys.argv[2]
rows = [
 {"Name": "FSCRT_Quillon Ridge Outfitters West F01", "DefaultSetCode": "ENTERPRISE", "Status": "A",
  "ManagerListName": "Smith, Aron", "PersonNumber": "4", "FirstName": "Aron", "LastName": "Smith"},
 {"Name": "FSCRT_Brindle Harbor Marine Supply F01", "DefaultSetCode": "ENTERPRISE", "Status": "A",
  "InternalLocationCode": "LHR_WH", "LocationSetCode": "COMMON",
  "ManagerListName": "Yaqub, Younas", "PersonNumber": "300000002688269", "FirstName": "Younas", "LastName": "Yaqub"},
]
for r in rows:
    r.update({"Classification": "FUN_BUSINESS_UNIT", "ClassificationCode": "FUN_BUSINESS_UNIT", "OrgInformationContext": "FUN_BUSINESS_UNIT"})
zin = zipfile.ZipFile(tpl)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename == "FUN_BUSINESS_UNIT.csv":
            text = data.decode("utf-8-sig")
            header = next(csv.reader(io.StringIO(text)))
            buf = io.StringIO()
            w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writerow(header)
            for r in rows:
                unknown = set(r) - set(header)
                if unknown: sys.exit(f"field not in template: {unknown}")
                w.writerow([r.get(h, "") for h in header])
            data = buf.getvalue().encode("utf-8")
        zo.writestr(info.filename, data)
print(json.dumps({"output": out, "rows": len(rows)}))
