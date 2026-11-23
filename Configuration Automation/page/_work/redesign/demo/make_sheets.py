"""Two demo workbooks from the page's own empty sheet: Setup_Workbook.xlsx (2 problems the check finds) and
Setup_Workbook_fixed.xlsx (the same rows corrected)."""
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "page"))
import workbook  # noqa: E402
from openpyxl import load_workbook  # noqa: E402


def make(path, rank, location):
    wb = load_workbook(io.BytesIO(workbook.make_template()))

    def fill(tab, rows):
        ws = wb[tab]
        cols = {str(c.value).replace(" *", ""): c.column for c in ws[2] if c.value}
        for i, row in enumerate(rows, 4):
            for k, v in row.items():
                ws.cell(i, cols[k], v)
    fill("Order Types", [{"Lookup Code": "STANDARD_SALES", "Meaning": "Standard Sales Order"},
                         {"Lookup Code": "RETURN_ORDER", "Meaning": "Return Order"}])
    fill("Payment Terms", [{"Name": "NET30_ZZ", "From Date": "2026-10-25"},
                           {"Name": "2/10 NET 30", "From Date": "2026-10-25", "Rank": rank},
                           {"Name": "NET 60", "From Date": "2026-10-25"}])
    fill("Payment Term Lines", [{"Payment Term Name": "NET30_ZZ", "Due (%)": "100", "Day of Month": "15", "Months Ahead": "0"},
                                {"Payment Term Name": "2/10 NET 30", "Due (%)": "100", "Days": "30",
                                 "First Discount (%)": "2", "First Discount Days": "10"},
                                {"Payment Term Name": "NET 60", "Due (%)": "100", "Days": "60"}])
    fill("Lookup Types", [{"Lookup Type": "ZZ_ORDER_REASON", "Meaning": "ZZ order reason", "Module": "Order Management"}])
    fill("Lookup Codes", [{"Lookup Type": "ZZ_ORDER_REASON", "Lookup Code": "LATE", "Meaning": "Late delivery"}])
    fill("Business Units", [{"Name": "Lahore Retail BU", "Location": location, "Default Set": "COMMON"},
                            {"Name": "Karachi Wholesale BU", "Default Set": "COMMON"}])
    wb.save(path)
    print(path)


make(HERE / "Setup_Workbook.xlsx", "5", "Lahor")
make(HERE / "Setup_Workbook_fixed.xlsx", "6", "Go Saas Lahore Office")


def make_done(path, rich):
    wb = load_workbook(io.BytesIO(workbook.make_template()))

    def fill(tab, rows):
        ws = wb[tab]
        cols = {str(c.value).replace(" *", ""): c.column for c in ws[2] if c.value}
        for i, row in enumerate(rows, 4):
            for k, v in row.items():
                ws.cell(i, cols[k], v)
    fill("Order Types", [{"Lookup Code": "STANDARD_SALES", "Meaning": "Standard Sales Order"},
                         {"Lookup Code": "RUSH_FLAKY" if rich else "RUSH_ORDER", "Meaning": "Rush Order"},
                         {"Lookup Code": "RETURN_ORDER", "Meaning": "Return Order" if rich else "Return Order 2"}])
    fill("Payment Terms", [{"Name": "NET30_ZZ", "From Date": "2026-10-25"},
                           {"Name": "2/10 NET 30", "From Date": "2026-10-25",
                            "Item Description": "UNKNOWN_ME" if rich else "Two lines, 2% in 10 days"},
                           {"Name": "NET 60", "From Date": "2026-10-25"}])
    fill("Payment Term Lines", [{"Payment Term Name": "NET30_ZZ", "Due (%)": "100", "Day of Month": "15",
                                 "Months Ahead": "0" if rich else "1"},
                                {"Payment Term Name": "2/10 NET 30", "Due (%)": "100", "Days": "30",
                                 "First Discount (%)": "2", "First Discount Days": "10"},
                                {"Payment Term Name": "NET 60", "Due (%)": "100", "Days": "60"}])
    fill("Lookup Types", [{"Lookup Type": "ZZ_ORDER_REASON", "Meaning": "ZZ order reason", "Module": "Order Management"}])
    fill("Lookup Codes", [{"Lookup Type": "ZZ_ORDER_REASON", "Lookup Code": "LATE",
                           "Meaning": "Late delivery" if rich else "Late delivery (LATE)"}])
    fill("Business Units", [{"Name": "Lahore Retail BU", "Location": "Go Saas Lahore Office", "Default Set": "COMMON"},
                            {"Name": "Karachi Wholesale BU", "Default Set": "COMMON"},
                            {"Name": "Dallas BU" if rich else "Seattle BU", "Default Set": "COMMON"}])
    wb.save(path)
    print(path)


make_done(HERE / "Done_mixed.xlsx", True)
make_done(HERE / "Done_clean.xlsx", False)
