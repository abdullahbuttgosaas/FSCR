"""FSCR live chain for one Run 04 skill, one stage per call, using FSCR's own scripts unchanged.
Stages:
  preflight  core/data-loader upload_and_initiate.py <candidate> --task-routed (no upload; approval gate)
  plan       core/data-loader/task-hook task_hook.py data-load (rule plan; prints registry nodes compactly)
  hook       Task Hook build-data-load-preview -> approve-data-load-preview -> verify-approved-data-load-archive
             (needs runs/<short>/rule-results.json and final-data.json written beforehand, with real evidence)
  upload     upload_and_initiate.py --approved-preflight-envelope --approve-upload --task-validation-envelope
  status     get_data_load_info.py <request id> until terminal; copies the FSM log into evidence
  verify     fresh FSCR data export + the skill's own adapter reconcile against the candidate
Usage: live_run.py <stage> <skill_dir_rel> <TASK_CODE> <short> <task name> <sequence> [request_id]"""
import glob, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

R4 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_04_create16")
W = R4 / "fscr-work4"
PROJ = W / "project/fscrt-run04-create16"
stage, skill_rel, task, short, task_name, seq = sys.argv[1:7]
RUN = PROJ / "artifacts/core/data-loader/task-hook/runs" / short
EV = R4 / "evidence/skills" / short
cand = PROJ / "exports" / short / f"fscrt-{short}-candidate.zip"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "MSYS_NO_PATHCONV": "1"}
RUN.mkdir(parents=True, exist_ok=True)
EV.mkdir(parents=True, exist_ok=True)


def sh(args, cwd, stdin=None, log=None):
    p = subprocess.run(args, cwd=str(cwd), input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if log:
        (EV / log).write_text(p.stdout + "\n--stderr--\n" + p.stderr, encoding="utf-8")
    return p


def tail(p, n=700):
    t = (p.stdout + p.stderr).strip()
    return t[-n:]


if stage == "preflight":
    p = sh([sys.executable, "upload_and_initiate.py", str(cand), "--task-routed", "--project-root", str(PROJ),
            "--preflight-envelope-output", str(RUN / "preflight.json")], W / "core/data-loader/scripts", log="preflight.log")
    print("preflight rc", p.returncode, "|", tail(p, 400).replace("\n", " ")[-400:])
elif stage == "plan":
    p = sh([sys.executable, "core/data-loader/task-hook/scripts/task_hook.py", "data-load", "--task-context",
            "project/fscrt-run04-create16/artifacts/shared/runbook/current/task-context.json", "--task-name", task_name,
            "--sequence", seq], W, log="plan.json")
    try:
        d = json.loads(p.stdout)
    except Exception:
        print("plan rc", p.returncode, tail(p)); sys.exit(1)
    def find(o, k):
        if isinstance(o, dict):
            if k in o: return o[k]
            for v in o.values():
                r = find(v, k)
                if r is not None: return r
        if isinstance(o, list):
            for v in o:
                r = find(v, k)
                if r is not None: return r
    print("status", find(d, "taskValidationStatus"), "| resources", [r.get("file") for r in (find(d, "ruleResources") or [])])
    reg = W / skill_rel / "ora-resource/ora_rule_registry.json"
    rd = json.loads(reg.read_text(encoding="utf-8"))
    t = rd["tasks"][0] if "tasks" in rd else rd
    print("start", t.get("start_node"), "| readiness", t.get("readiness", {}).get("status"))
    for n in t.get("nodes", []):
        print(f" {n['id']} [{n.get('action_type')}] {n.get('source', {}).get('file')} :: {str(n.get('applies_when'))[:90]} -> {n.get('transitions')}")
elif stage == "hook":
    fd = json.loads((RUN / "final-data.json").read_text(encoding="utf-8"))
    fd["archiveSha256"] = hashlib.sha256(cand.read_bytes()).hexdigest()
    pin = {"taskContextPath": "project/fscrt-run04-create16/artifacts/shared/runbook/current/task-context.json",
           "taskName": task_name, "sequence": int(seq), "finalData": fd,
           "ruleResults": json.loads((RUN / "rule-results.json").read_text(encoding="utf-8"))}
    hook = [sys.executable, "core/data-loader/task-hook/scripts/task_hook.py"]
    p = sh(hook + ["build-data-load-preview", "--input-stdin"], W, json.dumps(pin), log="hook_preview.log")
    if p.returncode != 0:
        print("preview refused rc", p.returncode, tail(p, 500)); sys.exit(1)
    (RUN / "preview.json").open("x").write(p.stdout)
    pv = json.loads(p.stdout); pv = pv.get("preview", pv)
    p = sh(hook + ["approve-data-load-preview", "--input-stdin"], W, json.dumps({"preview": pv}), log="hook_approve.log")
    if p.returncode != 0:
        print("approve refused", tail(p, 500)); sys.exit(1)
    (RUN / "approval.json").open("x").write(p.stdout)
    ap = json.loads(p.stdout); ap = ap.get("approval", ap)
    p = sh(hook + ["verify-approved-data-load-archive", "--input-stdin", "--archive", str(cand)], W,
           json.dumps({"preview": pv, "approval": ap}), log="hook_verify.log")
    if p.returncode != 0:
        print("verify refused", tail(p, 500)); sys.exit(1)
    v = json.loads(p.stdout)
    (RUN / "task-validation-envelope.json").open("x").write(json.dumps(v["taskValidationEnvelope"]))
    print("hook OK sha256", fd["archiveSha256"][:16])
elif stage == "upload":
    p = sh([sys.executable, "upload_and_initiate.py", "--approved-preflight-envelope", str(RUN / "preflight.json"), "--approve-upload",
            "--task-validation-envelope", str(RUN / "task-validation-envelope.json")], W / "core/data-loader/scripts", log="upload.log")
    m = re.search(r"Content ID\(Request ID\)\s*\|\s*([^|]+)\|", p.stdout)
    print("upload rc", p.returncode, "|", m.group(1).strip() if m else tail(p, 500).replace("\n", " "))
elif stage == "status":
    rid = sys.argv[7]
    for _ in range(40):
        p = sh([sys.executable, "get_data_load_info.py", rid], W / "core/data-loader/scripts", log="status.log")
        if not re.search(r"In progress|Not available yet", p.stdout):
            break
        time.sleep(15)
    rows = [l for l in p.stdout.splitlines() if l.startswith("| fscrt") or "Succeeded" in l or "Failed" in l or "Error" in l]
    print("\n".join(rows[:6]) or tail(p, 600))
    for f in glob.glob(rf"C:\Users\PC\.codex\data-loader-status-logs\requestid-{rid}\*"):
        shutil.copy(f, EV)
        t = Path(f).read_text(encoding="utf-8", errors="replace")
        print(" | ".join(l.strip()[:230] for l in t.splitlines() if re.search(r"rows were processed|Status:|rror|ORA-|JBO", l))[:1500])
elif stage == "verify":
    out = R4 / "evidence/skills" / short / "after_export"
    p = sh([sys.executable, "shared/setup-export/task-level-export/scripts/export_setup_task_csv.py", "--task-code", task, "--data",
            "--output-dir", str(out), "--token-cache", "auto", "--no-open-browser", "--wait-seconds", "900"], W, log="after_export.log")
    z = sorted(glob.glob(str(out / "*.zip")))
    pids = re.findall(r"process: (\d+)", p.stdout)
    if not z and pids:  # FSCR lost the download (seen with DNS errors): fetch the started process with FSCR's engine
        target = out / f"ETIA-TEST_setup_task_csv_export_{task.lower()}_{pids[-1]}.zip"
        f = sh([sys.executable, str(R4 / "scripts/fetch_export_result.py"), task, pids[-1], str(target)], R4, log="after_export_fetch.log")
        print("fetched via FSCR engine:", f.stdout.strip()[:160])
        z = sorted(glob.glob(str(out / "*.zip")))
    print("export:", pids, z[-1].split("\\")[-1] if z else "NO ZIP")
    if z:
        base = next(x for x in sorted(glob.glob(str(R4 / "evidence/exports" / task / "*.zip"))) if "template_export" not in x)
        p = sh([sys.executable, str(W / skill_rel / "scripts/fsm_task_adapter.py"), "reconcile", "--contract", str(W / skill_rel / "e2e-adapter.json"),
                "--report", str(EV / "reconcile.json"), "--baseline", base, "--candidate", str(cand), "--blueprint", str(EV / "blueprint.json"),
                "--requirements", str(EV / "requirements.json"), "--export", z[-1]], W, log="reconcile.log")
        try:
            r = json.loads((EV / "reconcile.json").read_text(encoding="utf-8"))
            print("reconcile rc", p.returncode, "status", r.get("status"), "| errors", json.dumps(r.get("errors"))[:500], "| mismatches", json.dumps(r.get("mismatches"))[:300])
        except Exception:
            print("reconcile rc", p.returncode, tail(p, 500))
