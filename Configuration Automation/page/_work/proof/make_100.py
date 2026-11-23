"""4b: a 100-customer sheet from the page's own generator (other tabs empty): unique meaningful names with a run tag,
only the two proven places (Dallas TX 75201, Seattle WA 98101), each with Bill to and Ship to."""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "page"), str(ROOT)]
import workbook  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

TAG = sys.argv[1]
FIRST = ["Harbor", "Summit", "Prairie", "Cedar", "Granite", "Lakeside", "Pioneer", "Redwood", "Silver", "Northgate"]
SECOND = ["Freight", "Outfitters", "Medical", "Logistics", "Hardware", "Foods", "Textiles", "Robotics", "Printing", "Energy"]
PLACES = [("1500 Marilla St", "Dallas", "TX", "75201"), ("600 4th Ave", "Seattle", "WA", "98101")]
wb = load_workbook(io.BytesIO(workbook.make_template()))
org, pur = wb["Organization Customers"], wb["Address Purposes"]
col = {str(c.value).replace(" *", ""): c.column for c in org[2] if c.value}
pcol = {str(c.value).replace(" *", ""): c.column for c in pur[2] if c.value}
names = []
for i in range(int(sys.argv[2]) if len(sys.argv) > 2 else 100):
    name = f"ZZ_TEST_CU_{TAG} {FIRST[i // 10]} {SECOND[i % 10]} {i + 1:03d}"
    line, city, state, postal = PLACES[i % 2]
    for label, v in (("Name", name), ("Account Address Set", "Enterprise Set"), ("Supplier Site ID", str(7000 + i)),
                     ("Account Type", "External"), ("Country", "United States"), ("Address Line 1", line),
                     ("City", city), ("State", state), ("Postal Code", postal)):
        org.cell(4 + i, col[label], v)
    for k, purpose in enumerate(("Bill to", "Ship to")):
        pur.cell(4 + 2 * i + k, pcol["Customer Name"], name)
        pur.cell(4 + 2 * i + k, pcol["Purpose"], purpose)
    names.append(name)
out = Path(__file__).parent / f"Customers_{len(names) if False else (int(sys.argv[2]) if len(sys.argv) > 2 else 100)}_{TAG}.xlsx"
wb.save(out)
print(out, len(names), names[0], names[-1])
