"""Drive FSCR Task Hook preview -> approve -> verify for one archive, using FSCR's own task_hook.py commands.
Why: FSCR documents the three commands but ships no wrapper; this only pipes JSON between them and saves outputs.
Approval basis: the user's written standing approval for this run (recorded in the ledger as gate G1/G2).
Usage: taskhook_lifecycle.py <work_root> <project_rel> <task_name> <sequence> <archive> <rule_results.json> <final_data.json> <out_dir>"""
import json, subprocess, sys, hashlib, os
work, proj, task, seq, archive, rules, final, out = sys.argv[1:9]
env = dict(os.environ, PYTHONIOENCODING="utf-8", MSYS_NO_PATHCONV="1")
hook = os.path.join(work, "core/data-loader/task-hook/scripts/task_hook.py")
def run(args, payload):
    p = subprocess.run([sys.executable, hook] + args, input=json.dumps(payload), capture_output=True, text=True, cwd=work, env=env)
    if p.returncode != 0:
        sys.exit(f"{args[0]} failed rc={p.returncode}: {p.stdout[-2000:]} {p.stderr[-2000:]}")
    return json.loads(p.stdout)
sha = hashlib.sha256(open(archive, "rb").read()).hexdigest()
fd = json.load(open(final)); fd["archiveSha256"] = sha
pin = {"taskContextPath": f"{proj}/artifacts/shared/runbook/current/task-context.json", "taskName": task, "sequence": int(seq),
       "finalData": fd, "ruleResults": json.load(open(rules))}
os.makedirs(out, exist_ok=True)
json.dump(pin, open(os.path.join(out, "preview-input.json"), "w"))
preview = run(["build-data-load-preview", "--input-stdin"], pin)
json.dump(preview, open(os.path.join(out, "preview.json"), "w"))
pv = preview.get("preview", preview)
approval = run(["approve-data-load-preview", "--input-stdin"], {"preview": pv})
json.dump(approval, open(os.path.join(out, "approval.json"), "w"))
ap = approval.get("approval", approval)
verified = run(["verify-approved-data-load-archive", "--input-stdin", "--archive", archive], {"preview": pv, "approval": ap})
json.dump(verified, open(os.path.join(out, "validation-result.json"), "w"))
env_obj = verified.get("taskValidationEnvelope")
json.dump(env_obj, open(os.path.join(out, "task-validation-envelope.json"), "w"))
print(json.dumps({"sha256": sha, "envelope": bool(env_obj), "keys": list(verified)}))
