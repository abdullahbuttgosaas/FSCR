"""Build the FSM CSV update ZIP for FUN_MANAGE_BUSINESS_UNIT (C4: Brindle manager -> Smith, Aron).
Why: FSCR's BU task guide states the update rules (ora_bulk_intake.md: "Existing no-op or update ... preserve
untouched values and require explicit update intent") but ships no builder. Adapted from Run 01's
build_bu_package.py. Per FSCR rule BU.NO_FULL_DATA_EXPORT the row is built from the fresh template plus declared
reads, not copied from a full data export:
- Name, DefaultSetCode ENTERPRISE, Status A, InternalLocationCode LHR_WH, LocationSetCode COMMON: Run 01
  current-workflow facts (Run 01 builder; finBusinessUnitsLOV LocationId 300000389039489), unchanged.
- Manager: publicWorkers PersonNumber 4 = Aron Smith (evidence/C4/publicWorkers_4.json).
Audit columns, OrganizationCode and effective dates are left blank, as in Run 01. Child CSVs are header-only."""
import csv, io, json, sys, zipfile

tpl, out = sys.argv[1], sys.argv[2]
row = {"Name": "FSCRT_Brindle Harbor Marine Supply F01", "DefaultSetCode": "ENTERPRISE", "Status": "A",
       "InternalLocationCode": "LHR_WH", "LocationSetCode": "COMMON",
       "ManagerListName": "Smith, Aron", "PersonNumber": "4", "FirstName": "Aron", "LastName": "Smith",
       "Classification": "FUN_BUSINESS_UNIT", "ClassificationCode": "FUN_BUSINESS_UNIT", "OrgInformationContext": "FUN_BUSINESS_UNIT"}
zin = zipfile.ZipFile(tpl)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename == "FUN_BUSINESS_UNIT.csv":
            header = next(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
            unknown = set(row) - set(header)
            if unknown:
                sys.exit(f"field not in template: {unknown}")
            buf = io.StringIO()
            w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writerow(header)
            w.writerow([row.get(h, "") for h in header])
            data = buf.getvalue().encode("utf-8")
        zo.writestr(info.filename, data)
print(json.dumps({"output": out, "rows": 1, "changed_vs_current": {"ManagerListName": ["Yaqub, Younas", "Smith, Aron"],
      "PersonNumber": ["300000002688269", "4"], "FirstName": ["Younas", "Aron"], "LastName": ["Yaqub", "Smith"]}}))
