"""The REAL Transaction Sources folder (run.py, its rules, its file builder, its log reader and read-back) with Oracle
replaced, for the offline matrix (2026-11-01). Same command line as the folder: --plan / --run-batch / --spec /
--options / --run. Nothing reaches Oracle: the host is a dummy, every network call fails, and the folder's Pod is
swapped for StubPod.

StubPod's "Oracle": the empty template = "Transaction Sources/manual-notes/<LAYOUT_DIR>/" (header lines and metadata;
LAYOUT_DIR is pod_layout_etia_test once the read-only check saved it, else the STAND-IN); the data file = those headers
plus the stub's sources (MATRIX_WORK/ts_pod.json, kept between calls; a created source is written to AR_BATCH_SOURCE, as
FSCR says it persists, with slash dates and audit values). As on ETIA-TEST (2026-11-01: 1 of 22), the data file lists
only some sources; Oracle's source list (transactionSourcesLOV) lists them all ("lov_only" in the state); the grouping
rules = the names in the grouping rules stub's
state (MATRIX_WORK/agr_pod.json, so a rule that stub created earlier in the same test is there) or its standing rules;
and a setup task process that loads a file the way Oracle would:
- a source in set ZZ_NOT_FOR_TS is refused (LOV_SetCode, naming the source);
- a GroupName that isn't a grouping rule refuses its source (LOV_GroupName);
- a source whose description holds "(stub: unknown refusal)" is refused with a message no rule knows (not naming it);
- a slash date or a filled audit column refuses its source (JBO-25009).
MATRIX_WORK/ts_stub.json switches the pod: {"order": "pod" | "reversed", "template": "ok" | "refused" |
"no_persisted" | "other_release", "route": "ok" | "refused", "check": "ok" | "fails", "export_hides_new": false |
true (a created source shows only in the source list, not in the data file)}.
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
FOLDER = ROOT / "Transaction Sources"
LAYOUT = next(p for p in (FOLDER / "manual-notes" / "pod_layout_etia_test",
                          FOLDER / "manual-notes" / "standin_layout_NOT_FROM_ORACLE") if (p / "members.txt").exists())
WORK = Path(os.environ.get("MATRIX_WORK") or (ROOT / "page" / "_work" / "matrix"))
os.environ["ORACLE_HOST"] = "https://fa-etia-test-stub.invalid"      # never a real pod (real env vars win over .env)
os.environ["ORACLE_ENV"] = "test"
os.environ.pop("ALLOW_PROD", None)
sys.path[:0] = [str(FOLDER), str(ROOT)]
sys.dont_write_bytecode = True
from common import oracle  # noqa: E402

import ts_package as pkg  # noqa: E402
import run  # noqa: E402


def _no_network(*a, **k):
    raise RuntimeError("the offline matrix never calls Oracle")


oracle.session = _no_network


def _work_dir(config_dir):
    oracle.WORK_DIR = WORK / "ts_work"
    oracle.WORK_DIR.mkdir(parents=True, exist_ok=True)
    return oracle.WORK_DIR


oracle.init_work_dir = _work_dir
oracle.cleanup_work_dir = lambda: None

SETS = [("COMMON", "Common Set"), ("ENTERPRISE", "Enterprise Set"), ("ZZ_NOT_FOR_TS", "Stub set Oracle refuses")]
AUDIT = {"LastUpdateDate": "2026/11/01 11:03:24.51", "LastUpdatedBy": "Configuration.TEST",
         "CreationDate": "2026/11/01 11:03:24.237", "CreatedBy": "Configuration.TEST",
         "LastUpdateLogin": "5EE3760FAC71DB4CE0631B65310A50F9"}
S, P = pkg.ENTITIES["source"], pkg.ENTITIES["persisted"]
STANDING_RULES = ["DEFAULT", "GLOBAL_INTERCOMPANY", "PROJECTS GROUPING RULE", "PN GROUPING RULE"]


def control():
    f = WORK / "ts_stub.json"
    c = {"order": "pod", "template": "ok", "route": "ok", "check": "ok", "export_hides_new": False}
    if f.exists():
        c.update(json.loads(f.read_text(encoding="utf-8")))
    return c


def state():
    """ETIA-TEST's sources of 2026-11-01 (a subset): the data file has only the Imported one."""
    f = WORK / "ts_pod.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    doo = dict(AUDIT, Name="Distributed Order Orchestration", SetCode="COMMON", Description="Import Invoices from DOO",
               BatchSourceType="FOREIGN", StartDate="2009/04/28", Status="A", AutoTrxNumberingFlag="Y",
               InvalidLinesRule="Create", GroupName="DEFAULT")
    return {S: [], P: [doo], "lov_only": [["Manual", "Common Set", "Manual"], ["Intercompany", "Common Set", ""],
                                          ["Global Intercompany", "Common Set", ""], ["ORA_PSCR", "Common Set", ""]]}


def save(rows):
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "ts_pod.json").write_text(json.dumps(rows), encoding="utf-8")


def rule_names():
    f = WORK / "agr_pod.json"
    if f.exists():
        return sorted({r["Name"] for r in json.loads(f.read_text(encoding="utf-8")).get("AR_AI_GROUPING_RULE", [])})
    return list(STANDING_RULES)


def metadata(order, template):
    xml = (LAYOUT / pkg.METADATA).read_text(encoding="utf-8")
    m = re.search(r"(<MigrationProcessBusinessObjectCSVMetadata1>\n)(.*?)(\s*</MigrationProcessBusinessObjectCSVMetadata1>)",
                  xml, re.S)
    blocks = re.findall(r"\s*<MigrationProcessBusinessObjectCSVMetadataVORow>.*?</MigrationProcessBusinessObjectCSVMetadataVORow>\n?",
                        m.group(2), re.S)
    if template == "no_persisted":
        blocks = [b for b in blocks if f">{P}<" not in b]
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

    def lov_sources(self):
        names = dict(SETS)
        st = state()
        return [(r["Name"], names.get(r["SetCode"], r["SetCode"]), r.get("Description", ""))
                for e in (S, P) for r in st.get(e, [])] + [tuple(x) for x in st.get("lov_only", [])]

    def rules_export(self, tag):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("AR_AI_GROUPING_RULE.csv", '"Name","StartDate","Description"\n'
                       + "".join(f'"{n}","1952/01/01",""\n' for n in rule_names()))
        return buf.getvalue()

    def send(self, zip_bytes):
        if control()["route"] == "refused":
            raise run.RouteRefused("POST setupTaskCSVImports/AR_MANAGE_TRANSACTION_SOURCES\nHTTP 404 Not Found (stub)", 404)
        (WORK / "ts_sent.zip").write_bytes(zip_bytes)
        self.sent = zip_bytes
        return 4545

    def wait(self, pid):
        lay, got = pkg.read_rows(self.sent)
        rows, log, errors, known = state(), [], 0, rule_names()
        for h in got[S]:
            name = h["Name"]
            dates = [v for c, v in h.items() if lay.entities[S]["types"].get(c) == "date" and "/" in v]
            audit = [v for c, v in h.items() if c in pkg.AUDIT and v]
            if h["SetCode"] == "ZZ_NOT_FOR_TS":
                log.append(f"Row Identifier: {name}, {h['SetCode']}. Status: Error. Message Text: JBO-25072: Applying "
                           "List binding LOV_SetCode with given set of values leads to no matching row.")
            elif h.get("GroupName") and h["GroupName"] not in known:
                log.append(f"Row Identifier: {name}, {h['SetCode']}. Status: Error. Message Text: JBO-25072: Applying "
                           "List binding LOV_GroupName with given set of values leads to no matching row.")
            elif "(stub: unknown refusal)" in h.get("Description", ""):
                log.append("Row Identifier: 300000999001. Status: Error. Message Text: AR-99999: a rule nobody has "
                           "written down yet refused this (stub).")
            elif dates or audit:
                log.append(f"Row Identifier: {name}. Status: Error. Message Text: JBO-25009: Cannot create an object "
                           "of type:java.sql.Date from type:java.lang.String.")
            else:
                r = {c: (v.replace("-", "/") if lay.entities[S]["types"].get(c) == "date" and v else v)
                     for c, v in h.items() if c in lay.entities[P]["header"]}
                if control()["export_hides_new"]:
                    rows.setdefault("lov_only", []).append([name, dict(SETS).get(h["SetCode"], h["SetCode"]),
                                                            h.get("Description", "")])
                else:
                    rows[P].append(dict(r, **AUDIT))
                log.append(f"Row Identifier: {name}, {h['SetCode']}. Status: Success.")
                continue
            errors += 1
        save(rows)
        text = "\n".join(log) + f"\nTotal Objects: {len(got[S])}"
        return ("COMPLETED_ERRORS" if errors else "COMPLETED"), [text]


run.POD = StubPod

if __name__ == "__main__":
    run.main()
