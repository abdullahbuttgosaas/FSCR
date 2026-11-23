"""The REAL Transaction Types folder (run.py, its rules, its file builder, its log reader and read-back) with Oracle
replaced, for the offline matrix (2026-11-02). Same command line as the folder: --plan / --run-batch / --spec /
--options / --run. Nothing reaches Oracle: the host is a dummy, every network call fails, and the folder's Pod is
swapped for StubPod.

StubPod's "Oracle": the empty template = "Transaction Types/manual-notes/<LAYOUT_DIR>/" (header lines and metadata;
LAYOUT_DIR is pod_layout_etia_test once the read-only check saved it, else the STAND-IN); the data file = those headers
plus the stub's types (MATRIX_WORK/tt_pod.json, kept between calls; a created type is written to AR_TRANSACTION_TYPE with
slash dates and audit values). Like ETIA-TEST's transaction sources, the data file may list only some types; Oracle's
type list (transactionTypesLOV) lists them all ("lov_only" in the state); the Receivables payment terms = the terms in
the payment terms stub's state (MATRIX_WORK/rpt_pod.json, so a term that stub created earlier in the same test is there)
or its standing terms; and a setup task process that loads a file the way Oracle would:
- a type in set ZZ_NOT_FOR_TT is refused (LOV_SetCode, naming the type);
- a DefaultTermName that isn't a payment term in DefaultTermSetCode refuses its type (LOV_DefaultTermName);
- a type whose description holds "(stub: unknown refusal)" is refused with a message no rule knows (not naming it);
- a slash date or a filled audit column refuses its type (JBO-25009);
- any row in AR_REF_ACCT_TRX_TYPE refuses the whole file (the module must never send accounts).
MATRIX_WORK/tt_stub.json switches the pod: {"order": "pod" | "reversed", "template": "ok" | "refused" |
"no_accounts" | "other_release", "route": "ok" | "refused", "check": "ok" | "fails", "export_hides_new": false |
true (a created type shows only in the type list, not in the data file)}.
"""
import csv
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "Transaction Types"
LAYOUT = next(p for p in (FOLDER / "manual-notes" / "pod_layout_etia_test",
                          FOLDER / "manual-notes" / "standin_layout_NOT_FROM_ORACLE") if (p / "members.txt").exists())
WORK = Path(os.environ.get("MATRIX_WORK") or (ROOT / "page" / "_work" / "matrix"))
os.environ["ORACLE_HOST"] = "https://fa-etia-test-stub.invalid"      # never a real pod (real env vars win over .env)
os.environ["ORACLE_ENV"] = "test"
os.environ.pop("ALLOW_PROD", None)
sys.path[:0] = [str(FOLDER), str(ROOT)]
sys.dont_write_bytecode = True
from common import oracle  # noqa: E402

import tt_package as pkg  # noqa: E402
import run  # noqa: E402


def _no_network(*a, **k):
    raise RuntimeError("the offline matrix never calls Oracle")


oracle.session = _no_network


def _work_dir(config_dir):
    oracle.WORK_DIR = WORK / "tt_work"
    oracle.WORK_DIR.mkdir(parents=True, exist_ok=True)
    return oracle.WORK_DIR


oracle.init_work_dir = _work_dir
oracle.cleanup_work_dir = lambda: None

SETS = [("COMMON", "Common Set"), ("ENTERPRISE", "Enterprise Set"), ("ZZ_NOT_FOR_TT", "Stub set Oracle refuses")]
AUDIT = {"LastUpdateDate": "2026/11/02 10:03:24.51", "LastUpdatedBy": "Configuration.TEST",
         "CreationDate": "2026/11/02 10:03:24.237", "CreatedBy": "Configuration.TEST",
         "LastUpdateLogin": "5EE3760FAC71DB4CE0631B65310A50F9"}
T, A = pkg.ENTITIES["type"], pkg.ENTITIES["accounts"]
STANDING_TERMS = [("30 Net", "COMMON"), ("IMMEDIATE", "COMMON"), ("Net 45 AR", "COMMON"), ("test", "COMMON")]


def control():
    f = WORK / "tt_stub.json"
    c = {"order": "pod", "template": "ok", "route": "ok", "check": "ok", "export_hides_new": False}
    if f.exists():
        c.update(json.loads(f.read_text(encoding="utf-8")))
    return c


def trx_type(name, set_code, cls, desc, start="2010/01/01", term=""):
    return dict(AUDIT, Name=name, SetCode=set_code, Description=desc, Type=cls, Status="A", StartDate=start,
                PostToGl="Y", AccountingAffectFlag="Y", AllowFreightFlag="N", TaxCalculationFlag="Y",
                NaturalApplicationOnlyFlag="N", AllowOverapplicationFlag="N", CreationSign="P" if cls != "CM" else "N",
                DefaultStatus="OP", DefaultPrintingOption="PRI", DefaultTermName=term,
                DefaultTermSetCode="COMMON" if term else "")


def state():
    """A subset of a pod's types: the data file has two, the type list has more."""
    f = WORK / "tt_pod.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return {T: [trx_type("Invoice", "COMMON", "INV", "Standard invoice", term="30 Net"),
                trx_type("Credit Memo", "COMMON", "CM", "Standard credit memo")],
            A: [{"AR_TRANSACTION_TYPE.SetCode": "COMMON", "AR_TRANSACTION_TYPE.Name": "Invoice", "BuName": "Vision BU",
                 "SourceRefTable": "RA_CUST_TRX_TYPES_ALL", "LedgerName": "Vision Ledger", "Name": "Invoice"}],
            "lov_only": [["Debit Memo", "COMMON", "Standard debit memo"], ["Chargeback", "COMMON", ""],
                         ["ORA_Lease Invoice", "COMMON", ""]]}


def save(rows):
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "tt_pod.json").write_text(json.dumps(rows), encoding="utf-8")


def term_keys():
    f = WORK / "rpt_pod.json"
    if f.exists():
        return sorted({(r["Name"], r["SetCode"]) for r in json.loads(f.read_text(encoding="utf-8")).get("AR_PAYMENT_TERM", [])})
    return list(STANDING_TERMS)


def metadata(order, template):
    xml = (LAYOUT / pkg.METADATA).read_text(encoding="utf-8")
    m = re.search(r"(<MigrationProcessBusinessObjectCSVMetadata1>\n)(.*?)(\s*</MigrationProcessBusinessObjectCSVMetadata1>)",
                  xml, re.S)
    blocks = re.findall(r"\s*<MigrationProcessBusinessObjectCSVMetadataVORow>.*?</MigrationProcessBusinessObjectCSVMetadataVORow>\n?",
                        m.group(2), re.S)
    if template == "no_accounts":
        blocks = [b for b in blocks if f">{A}<" not in b]
    if order == "reversed":
        blocks = blocks[::-1]
    xml = xml[:m.start(2)] + "".join(blocks) + xml[m.end(2):]
    if template == "other_release":
        xml = xml.replace("<ProcessRelease>11.13.26.10.0<", "<ProcessRelease>11.13.27.01.0<")
    names = [re.search(r"<BusinessObjectShortName>(\w+)<", b).group(1) for b in blocks]
    return xml.encode("utf-8"), names


def pod_zip(rows, template="ok"):
    """A file as Oracle gives it: the members in the pod's zip order (members.txt), the metadata in its own order."""
    meta, names = metadata(control()["order"], template)
    members = (LAYOUT / "members.txt").read_text(encoding="utf-8").split()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in [m[:-4] for m in members if m.endswith(".csv") and m[:-4] in names]:
            head = (LAYOUT / f"{n}.csv").read_bytes()
            cols = next(csv.reader([head.decode("utf-8-sig").splitlines()[0]]))
            body = "".join(",".join('"' + str(r.get(c_, "")).replace('"', '""') + '"' for c_ in cols) + "\n"
                           for r in (rows or {}).get(n, []))
            z.writestr(f"{n}.csv", head + body.encode("utf-8"))
        z.writestr(pkg.METADATA, meta)
    return buf.getvalue()


class StubPod(run.Pod):
    def host(self):
        return oracle.HOST

    def sets(self):
        if control()["check"] == "fails":
            oracle.fail("GET setIdSetsLOV\nHTTP 503 Service Unavailable (stub)")
        return list(SETS)

    def template(self):
        t = control()["template"]
        if t == "refused":
            print("  template not available: HTTP 404 (stub)")
            return None
        return pod_zip(None, t)

    def export(self, tag):
        return pod_zip(state())

    def lov_types(self):
        st = state()
        return [(r["Name"], r["SetCode"], r.get("Description", "")) for r in st.get(T, [])] + \
            [tuple(x) for x in st.get("lov_only", [])]

    def terms_export(self, tag):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("AR_PAYMENT_TERM.csv", '"Name","SetCode","StartDateActive"\n'
                       + "".join(f'"{n}","{s}","2025/12/30"\n' for n, s in term_keys()))
        return buf.getvalue()

    def send(self, zip_bytes):
        if control()["route"] == "refused":
            raise run.RouteRefused("POST setupTaskCSVImports/AR_MANAGE_TRANSACTION_TYPES\nHTTP 404 Not Found (stub)", 404)
        (WORK / "tt_sent.zip").write_bytes(zip_bytes)
        self.sent = zip_bytes
        return 6565

    def wait(self, pid):
        lay, got = pkg.read_rows(self.sent)
        rows, log, errors, terms = state(), [], 0, term_keys()
        if got.get(A):
            text = "Row Identifier: (file). Status: Error. Message Text: reference account rows were sent (stub)."
            return "COMPLETED_ERRORS", [text]
        for h in got[T]:
            name = h["Name"]
            dates = [v for c, v in h.items() if lay.entities[T]["types"].get(c) == "date" and "/" in v]
            audit = [v for c, v in h.items() if c in pkg.AUDIT and v]
            if h["SetCode"] == "ZZ_NOT_FOR_TT":
                log.append(f"Row Identifier: {h['SetCode']}, {name}. Status: Error. Message Text: JBO-25072: Applying "
                           "List binding LOV_SetCode with given set of values leads to no matching row.")
            elif h.get("DefaultTermName") and (h["DefaultTermName"], h.get("DefaultTermSetCode")) not in \
                    [tuple(x) for x in terms]:
                log.append(f"Row Identifier: {h['SetCode']}, {name}. Status: Error. Message Text: JBO-25072: Applying "
                           "List binding LOV_DefaultTermName with given set of values leads to no matching row.")
            elif "(stub: unknown refusal)" in h.get("Description", ""):
                log.append("Row Identifier: 300000999002. Status: Error. Message Text: AR-99998: a rule nobody has "
                           "written down yet refused this (stub).")
            elif dates or audit:
                log.append(f"Row Identifier: {name}. Status: Error. Message Text: JBO-25009: Cannot create an object "
                           "of type:java.sql.Date from type:java.lang.String.")
            else:
                r = {c: (v.replace("-", "/") if lay.entities[T]["types"].get(c) == "date" and v else v)
                     for c, v in h.items()}
                if control()["export_hides_new"]:
                    rows.setdefault("lov_only", []).append([name, h["SetCode"], h.get("Description", "")])
                else:
                    rows[T].append(dict(r, **AUDIT))
                log.append(f"Row Identifier: {h['SetCode']}, {name}. Status: Success.")
                continue
            errors += 1
        save(rows)
        text = "\n".join(log) + f"\nTotal Objects: {len(got[T])}"
        return ("COMPLETED_ERRORS" if errors else "COMPLETED"), [text]


run.POD = StubPod

if __name__ == "__main__":
    run.main()
