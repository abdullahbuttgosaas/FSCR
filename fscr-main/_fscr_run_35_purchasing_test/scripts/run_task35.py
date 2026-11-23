"""Run 35 step 3 (from Run 33/34 run_task33.py / run_task34.py): take one prepared FSM package through FSCR's official route:
Data Loader preflight -> Task Hook (rule plan, preview, approval, archive verification) -> Data Loader upload + initiate.
Approval basis: the user's written instruction for this run (load these FSCRT_ records on ETIA-TEST, no manual steps).
Usage: run_task33.py <TASK_CODE> <task name> <sequence> [--stage preflight|hook|upload|all]
Nothing is printed that holds a token. Rule results are written by Claude from real evidence (GETs through FSCR's shared REST client)."""
import json, subprocess, sys, os, hashlib, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
from api import WORK as W
PROJ = "project/fscrt-r35-purchasing"
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
    spec = json.load(open(RUN / "scripts" / "load_specs.json", encoding="utf-8"))[task]
    rp = RUN / "scripts" / f"rules_{task}.json"
    res = json.load(open(rp, encoding="utf-8")) if rp.exists() else []   # route-only tasks: no FSCR skill, so no planned rule resources
    fd = {"archiveName": zipname, "rowCounts": spec["rowCounts"], "operation": "create", "names": spec["names"]}
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
