"""The REAL Receivables Payment Terms folder (run.py, its rules, its file builder, its log reader and read-back) with
Oracle replaced by the pod's saved files, for the offline matrix (2026-10-30). Same command line as the folder:
--plan / --run-batch / --spec / --options / --run. Nothing reaches Oracle: the host is a dummy, every network call
fails, and the folder's Pod is swapped for StubPod.

StubPod's "Oracle": the empty template = the ETIA-TEST template files in "Receivables Payment Terms/manual-notes/
pod_layout_etia_test/" (copied from FSCR's saved export, headers and metadata only); the data file = those headers
plus the stub's terms (MATRIX_WORK/rpt_pod.json, kept between calls so a rerun sees what was saved; written with
Oracle's slash dates and audit values); the reference data sets; and a setup task process that loads a file the way
Oracle does: a term in set ZZ_NOT_FOR_AR is refused (LOV_SetCode, naming the term), a term whose name holds
UNKNOWN is refused with a message no rule knows (not naming the term), a slash date refuses its term (JBO-25009).
MATRIX_WORK/rpt_stub.json switches the pod: {"order": "pod" | "reversed" | "shuffled", "template": "ok" |
"refused" | "no_discount" | "other_release", "route": "ok" | "refused", "langs": ["US"], "check": "ok" | "fails"}.
"""
import io
import json
import os
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "Receivables Payment Terms"
LAYOUT = FOLDER / "manual-notes" / "pod_layout_etia_test"
WORK = Path(os.environ.get("MATRIX_WORK") or (ROOT / "page" / "_work" / "matrix"))
os.environ["ORACLE_HOST"] = "https://fa-etia-test-stub.invalid"      # never a real pod (real env vars win over .env)
os.environ["ORACLE_ENV"] = "test"
os.environ.pop("ALLOW_PROD", None)
sys.path[:0] = [str(FOLDER), str(ROOT)]
sys.dont_write_bytecode = True
from common import oracle  # noqa: E402

import rpt_package as pkg  # noqa: E402
import run  # noqa: E402


def _no_network(*a, **k):
    raise RuntimeError("the offline matrix never calls Oracle")


oracle.session = _no_network


def _work_dir(config_dir):
    oracle.WORK_DIR = WORK / "rpt_work"
    oracle.WORK_DIR.mkdir(parents=True, exist_ok=True)
    return oracle.WORK_DIR


oracle.init_work_dir = _work_dir
oracle.cleanup_work_dir = lambda: None

SETS = [("COMMON", "Common Set"), ("ENTERPRISE", "Enterprise Set"), ("S1", "Set One"),
        ("ZZ_NOT_FOR_AR", "Stub set Oracle refuses for terms")]
AUDIT = {"LastUpdateDate": "2026/10/28 11:03:24.51", "LastUpdatedBy": "Configuration.TEST",
         "CreationDate": "2026/10/28 11:03:24.237", "CreatedBy": "Configuration.TEST",
         "LastUpdateLogin": "5EE3760FAC71DB4CE0631B65310A50F9"}
H, L, T, D = (pkg.ENTITIES[r] for r in ("header", "line", "translation", "discount"))


def control():
    f = WORK / "rpt_stub.json"
    c = {"order": "pod", "template": "ok", "route": "ok", "langs": ["US"], "check": "ok"}
    if f.exists():
        c.update(json.loads(f.read_text(encoding="utf-8")))
    return c


def term(name, set_code, lines, discounts=(), lang="US"):
    head = dict(AUDIT, Name=name, SetCode=set_code, CreditCheckFlag="N", PrintingLeadDays="" if len(lines) < 2 else "1",
                StartDateActive="2025/12/30", BaseAmount="100", CalcDiscountOnLinesFlag="I",
                DiscountBasisDateType="APPLICATION_DATE", FirstInstallmentCode="INCLUDE", InUse="N",
                PartialDiscountFlag="N", PrepaymentFlag="N")
    k = {"AR_PAYMENT_TERM.Name": name, "AR_PAYMENT_TERM.SetCode": set_code}
    ls = [dict(AUDIT, **k, SequenceNum=str(n), RelativeAmount=a, DueDays=d, SetCode=set_code)
          for n, (a, d) in enumerate(lines, 1)]
    ds = [dict(AUDIT, **k, **{"AR_PAYMENT_TERM_LINE.SequenceNum": s}, SequenceNum=s, DiscountPercent=p,
               DiscountDays=dd, SetCode=set_code) for s, p, dd in discounts]
    tr = [dict(AUDIT, **k, Name=name, Description="", Language=lang, SourceLang=lang)]
    return {H: [head], L: ls, T: tr, D: ds}


def state():
    f = WORK / "rpt_pod.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    rows = {H: [], L: [], T: [], D: []}
    langs = control()["langs"]
    for i, t in enumerate([term("30 Net", "COMMON", [("100", "30")]), term("IMMEDIATE", "COMMON", [("100", "0")]),
                           term("Net 45 AR", "COMMON", [("100", "45")]),
                           term("test", "COMMON", [("100", "60")], [("1", "2", "29")])]):
        for e, rs in t.items():
            if e == T:
                rs = [dict(r, Language=langs[i % len(langs)] if langs else "", SourceLang=langs[i % len(langs)]
                           if langs else "") for r in rs] if langs else []
            rows[e] += rs
    return rows


def save(rows):
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "rpt_pod.json").write_text(json.dumps(rows), encoding="utf-8")


def metadata(order, template):
    xml = (LAYOUT / pkg.METADATA).read_text(encoding="utf-8")
    m = re.search(r"(<MigrationProcessBusinessObjectCSVMetadata1>)(.*?)(\s*</MigrationProcessBusinessObjectCSVMetadata1>)",
                  xml, re.S)
    blocks = re.findall(r"\s*<MigrationProcessBusinessObjectCSVMetadataVORow>.*?</MigrationProcessBusinessObjectCSVMetadataVORow>",
                        m.group(2), re.S)
    if template == "no_discount":
        blocks = [b for b in blocks if f">{D}<" not in b]
    if order == "reversed":
        blocks = blocks[::-1]
    elif order == "shuffled":
        blocks = [blocks[i] for i in (2, 0, 3, 1) if i < len(blocks)]
    xml = xml[:m.start(2)] + "".join(blocks) + xml[m.end(2):]
    if template == "other_release":
        xml = xml.replace("<ProcessRelease>11.13.26.10.0<", "<ProcessRelease>11.13.27.01.0<")
    names = [re.search(r"<BusinessObjectShortName>(\w+)<", b).group(1) for b in blocks]
    return xml.encode("utf-8"), names


def pod_zip(rows, template="ok"):
    """A file as Oracle gives it: the entity CSVs in the metadata's order, then the metadata."""
    meta, names = metadata(control()["order"], template)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            head = (LAYOUT / f"{n}.csv").read_bytes()
            body = "".join(",".join('"' + str(r.get(c_, "")).replace('"', '""') + '"' for c_ in
                                    next(__import__("csv").reader([head.decode("utf-8-sig").splitlines()[0]])))
                           + "\n" for r in (rows or {}).get(n, []))
            z.writestr(f"{n}.csv", head + body.encode("utf-8"))
        z.writestr(pkg.METADATA, meta)
    return buf.getvalue()


class StubPod(run.Pod):
    def host(self):
        return oracle.HOST

    def sets(self):
        if control()["check"] == "fails":
            oracle.fail("GET setIdSetsLOV\nHTTP 503 Service Unavailable (stub)")
        self.today_value = date(2026, 10, 30)
        return list(SETS)

    def template(self):
        t = control()["template"]
        if t == "refused":
            print("  template not available: HTTP 404 (stub)")
            return None
        return pod_zip(None, t)            # "no_discount" / "other_release": only the template differs

    def export(self, tag):
        return pod_zip(state())

    def send(self, zip_bytes):
        if control()["route"] == "refused":
            raise run.RouteRefused("POST setupTaskCSVImports/AR_MANAGE_RECEIVABLES_PAYMENT_TERMS\nHTTP 404 Not Found "
                                   "(stub)", 404)
        (WORK / "rpt_sent.zip").write_bytes(zip_bytes)
        self.sent = zip_bytes
        return 4242

    def wait(self, pid):
        lay, got = pkg.read_rows(self.sent)
        rows, log, errors = state(), [], 0
        for h in got[H]:
            key = (h["Name"], h["SetCode"])
            mine = {e: [r for r in got[e] if pkg.key_of(r) == key] for e in got}
            dates = [v for e in mine for r in mine[e] for c, v in r.items()
                     if lay.entities[e]["types"].get(c) == "date" and "/" in v]
            audit = [v for e in mine for r in mine[e] for c, v in r.items() if c in pkg.AUDIT and v]
            if h["SetCode"] == "ZZ_NOT_FOR_AR":
                log.append(f"Row Identifier: {h['Name']}, {h['SetCode']}. Status: Error. Message Text: JBO-25072: "
                           "Applying List binding LOV_SetCode with given set of values leads to no matching row.")
            elif "UNKNOWN" in h["Name"]:
                log.append("Row Identifier: 300000777001. Status: Error. Message Text: AR-99999: a rule nobody has "
                           "written down yet refused this (stub).")
            elif dates or audit:
                log.append(f"Row Identifier: {h['Name']}, {h['SetCode']}. Status: Error. Message Text: JBO-25009: "
                           "Cannot create an object of type:java.sql.Date from type:java.lang.String.")
            else:
                for e, rs in mine.items():
                    for r in rs:
                        r = {c: (v.replace("-", "/") if lay.entities[e]["types"].get(c) == "date" and v else v)
                             for c, v in r.items()}
                        rows[e].append(dict(r, **AUDIT))
                log.append(f"Row Identifier: {h['Name']}, {h['SetCode']}. Status: Success.")
                continue
            errors += 1
        save(rows)
        text = "\n".join(log) + f"\nTotal Objects: {len(got[H])}"
        return ("COMPLETED_ERRORS" if errors else "COMPLETED"), [text]


run.POD = StubPod

if __name__ == "__main__":
    run.main()
