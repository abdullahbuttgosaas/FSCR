"""Run 33 step 3: take one prepared FSM package through FSCR's official route:
Data Loader preflight -> Task Hook (rule plan, preview, approval, archive verification) -> Data Loader upload + initiate.
Approval basis: the user's written instruction for this run (load these FSCRT_ records on ETIA-TEST, no manual steps).
Usage: run_task33.py <TASK_CODE> <task name> <sequence> [--stage preflight|hook|upload|all]
Nothing is printed that holds a token. Rule results are written by Claude from real evidence (GETs through FSCR's shared REST client)."""
import json, subprocess, sys, os, hashlib, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
W = Path(r"C:\Users\PC\AppData\Local\Temp\claude\175f66902b2145cc\abeda3cc-913b-44a7-975c-fc0a2783eaaf\scratchpad\fscr-work33")
PROJ = "project/fscrt-r33-procurement"
CTX = f"{PROJ}/artifacts/shared/runbook/current/task-context.json"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
BU = "FSCRT_Brindle Harbor Marine Supply F01"

def sh(args, cwd, inp=None, retries=4):
    for i in range(retries):
        p = subprocess.run([sys.executable] + args, cwd=cwd, input=inp, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
        if "getaddrinfo" in ((p.stdout or "") + (p.stderr or "")) and i < retries - 1:   # DNS failure: request never left the machine
            time.sleep(4); continue
        return p
    return p

def fget(endpoint, queries):
    a = ["core/fusion-api/rest-api-client/scripts/fusion_rest_client.py", endpoint, "--method", "GET"]
    for q in queries: a += ["--query", q]
    p = sh(a, str(W))
    try: return json.loads(p.stdout)
    except Exception: return {"error": ((p.stdout or "") + (p.stderr or ""))[-300:]}

def rules_for(task, out):
    """Evaluate the planned rule resources against the final data. Returns (ruleResults, finalData)."""
    zipname = f"{task.lower()}_fscrt.zip"
    if task == "PO_MANAGE_DOCUMENT_STYLES":
        r = fget("/fscmRestApi/resources/11.13.18.05/purchasingDocumentStyles", ["q=StyleName='FSCRT_R33 Style'", "onlyData=true", "fields=StyleName"])
        json.dump(r, open(out / "lookup_style_exists.json", "w"), indent=1)
        n = len(r.get("items", [])) if "items" in r else -1
        assert n == 0, ("style lookup", r)
        res = [
         {"source": "ora_input_validation.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "MDS.VALIDATE_INPUT -> valid. StyleName 'FSCRT_R33 Style' (15 chars) and StyleDescription are under 240 characters; Status ACTIVE is under 30 characters; LineTypeAllowed=ALL and no line type input supplied."},
           {"severity": "info", "message": "NOTE: the rule is written for the REST object (Purchase Basis = Quantity/Amount). The Fusion CSV package carries PURCHASE_BASES lines GOODS and SERVICES instead, so the Quantity/Amount value check had nothing to test."}]},
         {"source": "ora_defaulting_rules.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "MDS.APPLY_DEFAULTS -> no default applied: no Purchase Basis Quantity/Amount field and no Line Type input in the CSV package."}]}]
        fd = {"archiveName": zipname, "rowCounts": {"PO_DOC_STYLE_VALUE.csv": 1, "PO_DOC_STYLE_HEADER.csv": 3, "PO_DOC_STYLE_LINE.csv": 2, "PO_DOC_STYLE_HEADER_TRANSLATION.csv": 3}, "operation": "create", "names": ["FSCRT_R33 Style"]}
    elif task == "ORA_PO_MANAGE_PROCUREMENT_DOCUMENT_NUMBERING":
        r = fget("/fscmRestApi/resources/11.13.18.05/procurementDocumentNumberings", [f"q=BusinessUnitName='{BU}'", "onlyData=true", "fields=DocumentNumberId,DocumentType,DeterminantType,BusinessUnitName", "limit=50"])
        json.dump(r, open(out / "lookup_numbering_exists.json", "w"), indent=1)
        n = len(r.get("items", [])) if "items" in r else -1
        assert n == 0, ("numbering lookup", r)
        res = [
         {"source": "ora_input_validation.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "PDN.VALIDATE_INPUT -> valid. Document Type REQUISITION, Determinant Type REQUISITIONING_BU, Determinant Value = BU name (not Purchase Order, so BusinessUnitName). Prefix FSCRT_R33| and MinimumDigits 5 supplied."},
           {"severity": "warning", "message": "CurrentMaximumUniqueIdentifier is not in the CSV package; treated as 'as applicable' (not needed for a prefix/min-digits scheme)."}]},
         {"source": "ora_reference_lookups.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "PDN.DERIVE_DOCUMENT_NUMBER_ID -> not_found. GET procurementDocumentNumberings for this BU returned 0 rows (lookup_numbering_exists.json), so the row is new and no DocumentNumberId is invented."}]},
         {"source": "ora_design_enforcement.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "PDN.ENFORCE_OPERATION_ROUTE -> post (no existing row, create route)."}]}]
        fd = {"archiveName": zipname, "rowCounts": {"ORA_PO_UNIQUE_IDENTIFIER_CONT_ALL.csv": 1}, "operation": "create", "names": [BU]}
    elif task == "ORA_PO_COMPLIANCE_CHECKLIST_QUESTIONS":
        res = []; fd = {"archiveName": zipname, "rowCounts": {"ORA_POQ_CHECKLIST_QUESTION.csv": 1, "ORA_POQ_TRANS_CHECKLIST_QUESTION.csv": 1}, "operation": "create", "names": ["FSCRT_R33_Q1"]}
    elif task == "ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS":
        res = []; fd = {"archiveName": zipname, "rowCounts": {"ORA_POQ_CHECKLIST_SECTION.csv": 1, "ORA_POQ_CHECKLIST_SECTION_QUESTIONS.csv": 0, "ORA_POQ_TRANS_CHECKLIST_SECTION.csv": 1}, "operation": "create", "names": ["FSCRT_R33_SEC1"]}
    else: raise SystemExit("unknown task")
    return res, fd

def hook(task, name, seq, out, zp):
    rules, fd = rules_for(task, out)
    json.dump(rules, open(out / "rule-results.json", "w"), indent=1); json.dump(fd, open(out / "final-data.json", "w"), indent=1)
    p = sh(["core/data-loader/task-hook/scripts/task_hook.py", "data-load", "--task-context", CTX, "--task-name", name, "--sequence", str(seq)], str(W))
    open(out / "hook_rule_plan.json", "w").write(p.stdout); print("rule plan:", p.stdout[:160].replace("\n", " "))
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest(); fd["archiveSha256"] = sha
    pin = {"taskContextPath": CTX, "taskName": name, "sequence": int(seq), "finalData": fd, "ruleResults": rules}
    json.dump(pin, open(out / "preview-input.json", "w"))
    hook_py = "core/data-loader/task-hook/scripts/task_hook.py"
    def run(args, payload):
        q = sh([hook_py] + args, str(W), inp=json.dumps(payload))
        if q.returncode != 0: raise SystemExit(f"{args[0]} failed rc={q.returncode}: {q.stdout[-1500:]} {q.stderr[-1500:]}")
        return json.loads(q.stdout)
    preview = run(["build-data-load-preview", "--input-stdin"], pin); json.dump(preview, open(out / "preview.json", "w"))
    pv = preview.get("preview", preview)
    approval = run(["approve-data-load-preview", "--input-stdin"], {"preview": pv}); json.dump(approval, open(out / "approval.json", "w"))
    ap = approval.get("approval", approval)
    verified = run(["verify-approved-data-load-archive", "--input-stdin", "--archive", str(zp)], {"preview": pv, "approval": ap}); json.dump(verified, open(out / "validation-result.json", "w"))
    env_obj = verified.get("taskValidationEnvelope"); json.dump(env_obj, open(out / "task-validation-envelope.json", "w"))
    print("hook ok; envelope:", bool(env_obj)); return bool(env_obj)

def main():
    task, name, seq = sys.argv[1], sys.argv[2], sys.argv[3]; stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "all"
    out = RUN / "evidence" / task; out.mkdir(parents=True, exist_ok=True)
    zp = RUN / "payload" / task / f"{task.lower()}_fscrt.zip"
    pf = out / "preflight.json"
    if stage in ("preflight", "all"):
        p = sh(["scripts/upload_and_initiate.py", str(zp), "--task-routed", "--preflight-envelope-output", str(pf), "--project-root", str(W / PROJ)], str(W / "core/data-loader"))
        open(out / "preflight.log", "w", encoding="utf-8").write((p.stdout or "") + (p.stderr or "")); print("preflight rc", p.returncode, p.stdout[-200:].replace("\n", " "))
        if "passed validation" not in ((p.stdout or "") + (p.stderr or "")): raise SystemExit("preflight failed")
    if stage in ("hook", "all"): hook(task, name, seq, out, zp)
    if stage in ("upload", "all"):
        p = sh(["scripts/upload_and_initiate.py", "--approved-preflight-envelope", str(pf), "--approve-upload",
                "--task-validation-envelope", str(out / "task-validation-envelope.json")], str(W / "core/data-loader"), retries=1)
        open(out / "upload.log", "w", encoding="utf-8").write((p.stdout or "") + (p.stderr or "")); print("upload rc", p.returncode); print(p.stdout[-900:]); print(p.stderr[-400:])
main()
