import zipfile, csv, io, base64, time, getpass, requests
from datetime import datetime

HOST = "https://fa-etia-test-saasfaprod1.fa.ocs.oraclecloud.com"
BASE = f"{HOST}/fscmRestApi/resources/11.13.18.05/setupTaskCSVImports/FND_MANAGE_STANDARD_LOOKUPS"
SRC, TEMPLATE = "response.bin", "ZZ_POC_TEST"
NEW = {"type": "ZZ_POC_TEST3", "meaning": "ZZ POC Test 3",
       "description": "POC CSV generated lookup type",
       "codes": [("CODE1", "Code 1"), ("CODE2", "Code 2")]}

user = input("Oracle username: ")
auth = (user, getpass.getpass("Oracle password: "))

z = zipfile.ZipFile(SRC)
print("Files in the export zip:", z.namelist())
type_name = next(n for n in z.namelist() if n.endswith("FND_APP_STANDARD_LOOKUP.csv"))
code_name = next(n for n in z.namelist() if n.endswith("ORA_FND_APP_STANDARD_LOOKUP_CODE.csv"))
stamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S.0")
raw_type = z.read(type_name)
print("Type CSV starts with:", raw_type[:60])

def read(name):
    rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
    return rows[0], rows[1:]

def write(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()

def setcol(h, row, col, val):
    row[h.index(col)] = val

th, trows = read(type_name)
t = list(next(r for r in trows if r[0] == TEMPLATE))
for col, val in (("LookupType", NEW["type"]), ("Meaning", NEW["meaning"]),
                 ("Description", NEW["description"]),
                 ("CreationDate", stamp), ("LastUpdateDate", stamp)):
    setcol(th, t, col, val)

ch, crows = read(code_name)
ctpl = next(r for r in crows if r[0] == TEMPLATE)
codes = []
for i, (code, meaning) in enumerate(NEW["codes"], 1):
    c = list(ctpl)
    c[0] = NEW["type"]
    for col, val in (("LookupCode", code), ("Meaning", meaning),
                     ("DisplaySequence", str(i)),
                     ("CreationDate", stamp), ("LastUpdateDate", stamp)):
        setcol(ch, c, col, val)
    codes.append(c)

new_type_csv = write(th, [t]).encode("utf-8")
new_code_csv = write(ch, codes).encode("utf-8")

def build(compression, keep_other_files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression) as zo:
        for n in z.namelist():
            if n == type_name:
                zo.writestr(n, new_type_csv)
            elif n == code_name:
                zo.writestr(n, new_code_csv)
            elif keep_other_files:
                zo.writestr(n, z.read(n))
        if not keep_other_files:
            zo.writestr(type_name, new_type_csv)
            zo.writestr(code_name, new_code_csv)
    return buf.getvalue()

variants = [
    ("A: stored, keep other files", build(zipfile.ZIP_STORED, True), {}),
    ("B: deflated, keep other files", build(zipfile.ZIP_DEFLATED, True), {}),
    ("C: stored, keep other files, with FileName", build(zipfile.ZIP_STORED, True), {"FileName": "import.zip"}),
    ("D: stored, only 2 CSVs", build(zipfile.ZIP_STORED, False), {}),
]

for label, data, extra in variants:
    body = {"TaskCode": "FND_MANAGE_STANDARD_LOOKUPS",
            "FileContent": base64.b64encode(data).decode(),
            "SourceTargetDiffOkFlag": True}
    body.update(extra)
    r = requests.post(f"{BASE}/child/SetupTaskCSVImportProcess", json=body, auth=auth)
    print(f"\n[{label}] status {r.status_code}")
    print(r.text[:400])
    if r.status_code in (200, 201):
        pid = r.json()["ProcessId"]
        res = f"{BASE}/child/SetupTaskCSVImportProcess/{pid}/child/SetupTaskCSVImportProcessResult/{pid}"
        for _ in range(12):
            time.sleep(10)
            rr = requests.get(res, auth=auth)
            status = rr.json().get("StatusCode") if rr.status_code == 200 else f"GET {rr.status_code}"
            print("StatusCode:", status)
            if status in ("COMPLETED", "COMPLETED_WARNINGS", "COMPLETED_ERRORS"):
                break
        print("Result URL:", res)
        break