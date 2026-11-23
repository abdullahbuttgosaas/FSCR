"""The REAL AutoInvoice Grouping Rules folder (run.py, its rules, its file builder, its log reader and read-back) with
Oracle replaced, for the offline matrix (2026-11-01). Same command line as the folder: --plan / --run-batch / --spec /
--options / --run. Nothing reaches Oracle: the host is a dummy, every network call fails, and the folder's Pod is
swapped for StubPod.

StubPod's "Oracle": the empty template = ETIA-TEST's real template files in "AutoInvoice Grouping Rules/manual-notes/
pod_layout_etia_test/" (headers and metadata only, saved by the read-only check of 2026-11-01; members in the pod's
zip order, entities in its metadata order, which differ); the data file = those headers plus the stub's rules (ETIA-TEST's
real rules of 2026-11-01, a subset, plus one earlier Corsair rule) (MATRIX_WORK/agr_pod.json, kept between calls so a rerun sees what was saved; written with
slash dates and audit values); and a setup task process that loads a file the way FSCR says Oracle does:
- a characteristic in CONS_ONLY (stub only: which names need consolidated billing is not known) refuses its whole rule (AR_CONS_BILL_GROUP_NOT_ALLOW_U, the rule entity's own check,
  FSCR ora_input_validation.md:45), naming the rule;
- a rule whose description holds "(stub: unknown refusal)" is refused with a message no rule knows (not naming it);
- a slash date or a filled audit column refuses its rule (JBO-25009).
The characteristic names are the ones ETIA-TEST's rules use (L.INTERFACE_LINE_ATTRIBUTE1-7).
MATRIX_WORK/agr_stub.json switches the pod: {"order": "pod" | "reversed" | "shuffled", "template": "ok" | "refused" |
"no_request" | "other_release", "route": "ok" | "refused", "check": "ok" | "fails"}.
"""
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "AutoInvoice Grouping Rules"
LAYOUT = FOLDER / "manual-notes" / "pod_layout_etia_test"
WORK = Path(os.environ.get("MATRIX_WORK") or (ROOT / "page" / "_work" / "matrix"))
os.environ["ORACLE_HOST"] = "https://fa-etia-test-stub.invalid"      # never a real pod (real env vars win over .env)
os.environ["ORACLE_ENV"] = "test"
os.environ.pop("ALLOW_PROD", None)
sys.path[:0] = [str(FOLDER), str(ROOT)]
sys.dont_write_bytecode = True
from common import oracle  # noqa: E402

import agr_package as pkg  # noqa: E402
import run  # noqa: E402


def _no_network(*a, **k):
    raise RuntimeError("the offline matrix never calls Oracle")


oracle.session = _no_network


def _work_dir(config_dir):
    oracle.WORK_DIR = WORK / "agr_work"
    oracle.WORK_DIR.mkdir(parents=True, exist_ok=True)
    return oracle.WORK_DIR


oracle.init_work_dir = _work_dir
oracle.cleanup_work_dir = lambda: None

AUDIT = {"CreatedBy": "Configuration.TEST", "LastUpdatedBy": "Configuration.TEST"}
R, C, Q = (pkg.ENTITIES[k] for k in ("rule", "class", "request"))
CONS_ONLY = {"L.INTERFACE_LINE_ATTRIBUTE7"}    # stub only: a characteristic refused without consolidated billing


def control():
    f = WORK / "agr_stub.json"
    c = {"order": "pod", "template": "ok", "route": "ok", "check": "ok"}
    if f.exists():
        c.update(json.loads(f.read_text(encoding="utf-8")))
    return c


def rule(name, start, classes, description=""):
    """One standing rule as the data file shows it. classes: {code: [characteristics]}."""
    rows = {R: [dict(AUDIT, Name=name, StartDate=start, Description=description)], C: [], Q: []}
    for code, chars in classes.items():
        rows[C].append(dict(AUDIT, **{pkg.PARENT: name}, Class11=code))
        rows[Q] += [dict(AUDIT, **{pkg.PARENT: name, pkg.CLASS_LINK: code}, FromColumnName=ch) for ch in chars]
    return rows


def state():
    f = WORK / "agr_pod.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    rows = {R: [], C: [], Q: []}
    a = [f"L.INTERFACE_LINE_ATTRIBUTE{n}" for n in range(1, 8)]
    for r in (rule("DEFAULT", "1952/01/01", {}, "Default Grouping Rule"),
              rule("PROJECTS GROUPING RULE", "1952/01/01", {"C": a[:4], "I": a[:4]}, "Projects Grouping Rule"),
              rule("GLOBAL_INTERCOMPANY", "1950/01/01", {"I": a[:2]}, "Global Intercompany"),
              rule("ORA_PSCR", "1970/01/01", {"C": a[4:], "D": a[4:], "I": a[4:]}, "Public Sector Default Grouping"),
              rule("CORSAIR DISTRIBUTION BY SALES ORDER", "2026/01/01", {"I": a[:1]},
                   "Distributor invoices: one per sales order")):
        for e, rs in r.items():
            rows[e] += rs
    return rows


def save(rows):
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "agr_pod.json").write_text(json.dumps(rows), encoding="utf-8")


def metadata(order, template):
    xml = (LAYOUT / pkg.METADATA).read_text(encoding="utf-8")
    m = re.search(r"(<MigrationProcessBusinessObjectCSVMetadata1>\n)(.*?)(\s*</MigrationProcessBusinessObjectCSVMetadata1>)",
                  xml, re.S)
    blocks = re.findall(r"\s*<MigrationProcessBusinessObjectCSVMetadataVORow>.*?</MigrationProcessBusinessObjectCSVMetadataVORow>\n?",
                        m.group(2), re.S)
    if template == "no_request":
        blocks = [b for b in blocks if f">{Q}<" not in b]
    if order == "reversed":
        blocks = blocks[::-1]
    elif order == "shuffled":
        blocks = [blocks[i] for i in (1, 2, 0) if i < len(blocks)]
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
            cols = next(__import__("csv").reader([head.decode("utf-8-sig").splitlines()[0]]))
            body = "".join(",".join('"' + str(r.get(c_, "")).replace('"', '""') + '"' for c_ in cols) + "\n"
                           for r in (rows or {}).get(n, []))
            z.writestr(f"{n}.csv", head + body.encode("utf-8"))
        z.writestr(pkg.METADATA, meta)
    return buf.getvalue()


class StubPod(run.Pod):
    def host(self):
        return oracle.HOST

    def template(self):
        t = control()["template"]
        if t == "refused":
            print("  template not available: HTTP 404 (stub)")
            return None
        return pod_zip(None, t)            # "no_request" / "other_release": only the template differs

    def export(self, tag):
        if control()["check"] == "fails":
            oracle.fail("POST setupTaskCSVExports/AR_MANAGE_AUTOINVOICE_GROUPING_RULES\nHTTP 503 Service Unavailable (stub)")
        return pod_zip(state())

    def send(self, zip_bytes):
        if control()["route"] == "refused":
            raise run.RouteRefused("POST setupTaskCSVImports/AR_MANAGE_AUTOINVOICE_GROUPING_RULES\nHTTP 404 Not Found "
                                   "(stub)", 404)
        (WORK / "agr_sent.zip").write_bytes(zip_bytes)
        self.sent = zip_bytes
        return 4343

    def wait(self, pid):
        lay, got = pkg.read_rows(self.sent)
        rows, log, errors = state(), [], 0
        for h in got[R]:
            name = h["Name"]
            mine = {e: [r for r in got[e] if pkg.key_of(r) == name] for e in got}
            dates = [v for e in mine for r in mine[e] for c, v in r.items()
                     if lay.entities[e]["types"].get(c) == "date" and "/" in v]
            audit = [v for e in mine for r in mine[e] for c, v in r.items() if c in pkg.AUDIT and v]
            cons = [q["FromColumnName"] for q in mine[Q] if q["FromColumnName"] in CONS_ONLY]
            if cons:
                log.append(f"Row Identifier: {name}. Status: Error. Message Text: AR_CONS_BILL_GROUP_NOT_ALLOW_U: "
                           f"You can't group by {cons[0]} unless the rule is used for consolidated billing.")
            elif "(stub: unknown refusal)" in h.get("Description", ""):
                log.append("Row Identifier: 300000888001. Status: Error. Message Text: AR-99999: a rule nobody has "
                           "written down yet refused this (stub).")
            elif dates or audit:
                log.append(f"Row Identifier: {name}. Status: Error. Message Text: JBO-25009: Cannot create an object "
                           "of type:java.sql.Date from type:java.lang.String.")
            else:
                for e, rs in mine.items():
                    for r in rs:
                        r = {c: (v.replace("-", "/") if lay.entities[e]["types"].get(c) == "date" and v else v)
                             for c, v in r.items()}
                        rows[e].append(dict(r, **AUDIT))
                log.append(f"Row Identifier: {name}. Status: Success.")
                continue
            errors += 1
        save(rows)
        text = "\n".join(log) + f"\nTotal Objects: {len(got[R])}"
        return ("COMPLETED_ERRORS" if errors else "COMPLETED"), [text]


run.POD = StubPod

if __name__ == "__main__":
    run.main()
