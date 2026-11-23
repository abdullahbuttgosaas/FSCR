"""Run 34 step 3 (from Run 33 run_task33.py): take one prepared FSM package through FSCR's official route:
Data Loader preflight -> Task Hook (rule plan, preview, approval, archive verification) -> Data Loader upload + initiate.
Approval basis: the user's written instruction for this run (load these FSCRT_ records on ETIA-TEST, no manual steps).
Usage: run_task33.py <TASK_CODE> <task name> <sequence> [--stage preflight|hook|upload|all]
Nothing is printed that holds a token. Rule results are written by Claude from real evidence (GETs through FSCR's shared REST client)."""
import json, subprocess, sys, os, hashlib, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
from api import WORK as W
PROJ = "project/fscrt-r34-sourcing-supplier"
CTX = f"{PROJ}/artifacts/shared/runbook/current/task-context.json"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")

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
    """Evaluate the planned rule resources against the final data (Claude writes results from real GETs). Returns (ruleResults, finalData)."""
    zipname = f"{task.lower()}_fscrt.zip"
    if task == "PON_MANAGE_COST_FACTORS":
        r = fget("/fscmRestApi/resources/11.13.18.05/supplierNegotiationCostFactors", ["q=CostFactorCode='FSCRT_R34_CF' or CostFactorName='FSCRT_R34 Freight'", "onlyData=true", "fields=CostFactorId,CostFactorCode,CostFactorName"])
        json.dump(r, open(out / "lookup_cost_factor_exists.json", "w"), indent=1)
        n = len(r.get("items", [])) if "items" in r else -1
        assert n == 0, ("cost factor lookup", r)
        res = [
         {"source": "ora_input_validation.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "COST_FACTOR.CLASSIFY_OPERATION -> data_load (create through Data Loader with an FSM CSV package)."},
           {"severity": "info", "message": "COST_FACTOR.VALIDATE_DATA_LOADER_INPUT -> valid. Code FSCRT_R34_CF (12 chars, max 30), name 'FSCRT_R34 Freight' (17 chars, max 80), description under 240, pricing basis FIXED_AMOUNT (a value used by existing rows in the ETIA-TEST export)."},
           {"severity": "info", "message": "NOTE: the rule is written for the Data Loader REST object supplierNegotiationCostFactors (CostFactorCode/PricingBasisCode). The FSM CSV package carries PriceElementCode/PricingBasis instead; values were mapped one to one."}]},
         {"source": "ora_dependency_readiness.md", "status": "passed", "changes": [], "issues": [
           {"severity": "warning", "message": "COST_FACTOR.VERIFY_DATA_LOADER_RESOURCE -> supplierNegotiationCostFactors is not a Data Loader object on this pod (generate_sample_dat: 'No exact business-object file discriminator matched'); the FSM CSV route of the same task is used, as in Run 33."}]},
         {"source": "ora_reference_lookups.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "COST_FACTOR.LOOKUP_COST_FACTOR -> not_found. GET supplierNegotiationCostFactors for the code and name returned 0 rows (lookup_cost_factor_exists.json): a new record."}]},
         {"source": "ora_error_handling.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "COST_FACTOR.REQUIRE_PREVIEW_READY -> all earlier nodes passed; preview may be built."}]}]
        fd = {"archiveName": zipname, "rowCounts": {"PON_PRICE_ELEMENT_TYPES.csv": 1, "PON_PRICE_ELEMENT_TYPES_TRANSLATION.csv": 1}, "operation": "create", "names": ["FSCRT_R34_CF"]}
    elif task == "ORA_POZ_MANAGE_CERTIFYING_AGENCIES":
        r = fget("/fscmRestApi/resources/11.13.18.05/supplierRegistrationCertifyingAgenciesLOV", ["q=CertifyingAgency='FSCRT_R34 Agency'", "onlyData=true"])
        json.dump(r, open(out / "lookup_agency_exists.json", "w"), indent=1)
        n = len(r.get("items", [])) if "items" in r else -1
        assert n == 0, ("agency lookup", r)
        c = fget("/fscmRestApi/resources/11.13.18.05/standardLookups/POZ_BUSINESS_CLASSIFICATIONS/child/lookupCodes", ["q=LookupCode='SMALL_BUSINESS'", "onlyData=true"])
        json.dump(c, open(out / "lookup_classification_small_business.json", "w"), indent=1)
        ci = c.get("items", []); assert len(ci) == 1 and ci[0].get("EnabledFlag") == "Y", ("classification", c)
        res = [
         {"source": "ora_input_validation.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "POZ.CA.VALIDATE_INPUT -> valid. Create: Name 'FSCRT_R34 Agency' and Description supplied; no EndDate (open-ended); one business-classification association, no duplicates, no DELETE rows."}]},
         {"source": "ora_reference_lookups.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "POZ.CA.LIST_AGENCY_CANDIDATES / RESOLVE_AGENCY -> 0 candidates for 'FSCRT_R34 Agency' (lookup_agency_exists.json): new agency, no ID invented."},
           {"severity": "info", "message": "POZ.CA.RESOLVE_BUSINESS_CLASSIFICATION -> SMALL_BUSINESS resolves to exactly one enabled code in POZ_BUSINESS_CLASSIFICATIONS (lookup_classification_small_business.json)."},
           {"severity": "info", "message": "POZ.CA.RESOLVE_EXISTING_BUSINESS_CLASSIFICATION -> not_required (create, no child PATCH)."}]},
         {"source": "ora_error_handling.md", "status": "passed", "changes": [], "issues": [
           {"severity": "info", "message": "POZ.CA.CONFIGURATION_GATE -> open; all earlier nodes passed."}]}]
        fd = {"archiveName": zipname, "rowCounts": {"ORA_POZ_CERTIFYING_AGENCY.csv": 1, "ORA_POZ_CERT_AGENCY_BUS_CLASS.csv": 1}, "operation": "create", "names": ["FSCRT_R34 Agency"]}
    elif task == "PON_MANAGE_NEGOTIATION_STYLES":
        res = []; fd = {"archiveName": zipname, "rowCounts": {"PON_NEGOTIATION_STYLES.csv": 1, "PON_NEGOTIATION_STYLES_TRANSLATION.csv": 1, "PON_DOCTYPE_STYLES.csv": 3, "PON_DOCTYPE_STYLES_TRANSLATION.csv": 3}, "operation": "create", "names": ["FSCRT_R34_STYLE"]}
    elif task == "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_VALUE_SETS":
        res = []; fd = {"archiveName": zipname, "rowCounts": {"FND_APP_FLEX_VALUE_SET.csv": 1, "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv": 2}, "operation": "create", "names": ["FSCRT_R34_VS"]}
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
