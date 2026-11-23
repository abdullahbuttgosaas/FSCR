"""Run 09: offline reference scan (no Oracle call). For each case, find every CSV cell in the fresh FSCR exports
(and the saved REST/SOAP reads) that contains the target value, and say which file, row and column.
Rows are labelled 'self' when they are the target record's own rows (its own task export), else 'reference'.
Also counts how many rows each export holds, so "0 references" can be read against what was searched.
Usage: ref_scan.py  -> evidence/ref_scan.json + printed summary"""
import csv, io, json, zipfile
from pathlib import Path

R9 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_09_impact")
EXP = R9 / r"fscr-work9\project\draft_impl_project_20261104_r09\exports\now"
CASES = {
    "1_payment_term": {"targets": ["FSCRT_2P10N30F1"], "self_task": "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS"},
    "2_lookup_code": {"targets": ["FSCRT_SO_TRAIL_DEALER_F01"], "self_task": "DOO_MANAGE_ORCHESTRATION_LOOKUPS"},
    "3_business_unit": {"targets": ["FSCRT_Brindle Harbor Marine Supply F01", "300000394664009"], "self_task": ("FUN_MANAGE_BUSINESS_UNIT", "FUN_MANAGE_BUSINESS_UNIT_SET_ASSIGNMENT")},
}
out, sizes = {c: [] for c in CASES}, {}
for z in sorted(EXP.glob("*/*.zip")):
    task = z.parent.name
    with zipfile.ZipFile(z) as zf:
        for m in zf.namelist():
            if not m.endswith(".csv"):
                continue
            rows = list(csv.DictReader(io.TextIOWrapper(zf.open(m), encoding="utf-8-sig")))
            sizes[f"{task}/{m}"] = len(rows)
            for i, r in enumerate(rows):
                for c, spec in CASES.items():
                    for col, val in r.items():
                        if val and any(t in val for t in spec["targets"]):
                            key = {k: r[k] for k in list(r)[:3]}
                            st = spec["self_task"]; st = st if isinstance(st, tuple) else (st,)
                            role = "self" if task in st and m in ("FUN_BUSINESS_UNIT.csv", "AR_PAYMENT_TERM.csv", "AR_PAYMENT_TERM_LINE.csv", "AR_PAYMENT_TERM_TRANSLATION.csv", "AR_PAYMENT_TERM_DISCOUNT.csv", "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv") else "reference"
                            out[c].append({"source": f"{task}/{m}", "row": i + 1, "column": col, "value": val[:120],
                                           "row_key": key, "role": role})
# saved REST/SOAP reads of this run
for p in sorted((R9 / "evidence").rglob("*.json")) + sorted((R9 / "evidence").rglob("*.xml")):
    if p.name in ("ref_scan.json",) or p.name.startswith("describe_"):
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    if '"Bad Request"' in text[:200]:
        continue  # 400 error bodies only echo the filter
    for c, spec in CASES.items():
        hits = sum(text.count(t) for t in spec["targets"])
        if hits:
            out[c].append({"source": str(p.relative_to(R9)), "occurrences": hits, "role": "rest/soap read"})
(R9 / "evidence/ref_scan.json").write_text(json.dumps({"rows_searched": sizes, "hits": out}, indent=1, ensure_ascii=False), encoding="utf-8")
print("CSV files searched:", len(sizes), "rows:", sum(sizes.values()))
for c, hs in out.items():
    print(f"== {c}: {len(hs)} hits")
    for h in hs:
        print("  ", h.get("role"), h["source"], h.get("column", ""), h.get("row_key", h.get("occurrences", "")))
