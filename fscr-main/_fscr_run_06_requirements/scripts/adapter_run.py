"""Drive one FSCR skill's own fsm_task_adapter.py through its offline steps, unchanged (Run 04).
Steps: manifest(template) -> manifest(baseline) -> normalize(request, design) -> build -> validate.
Each step's report goes to evidence/skills/<short>/; prints only the step, exit code and a short status/error line.
The adapter itself never connects to Fusion (its own docstring). Usage:
  adapter_run.py <skill_dir_rel> <TASK_CODE> <short> <request.txt> <design.json> [--adapter <patched adapter.py>]"""
import json, subprocess, sys, glob
from pathlib import Path

R4 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_06_requirements")
W = R4 / "fscr-work6"
skill_rel, task, short, request, design = sys.argv[1:6]
adapter = Path(sys.argv[sys.argv.index("--adapter") + 1]) if "--adapter" in sys.argv else W / skill_rel / "scripts/fsm_task_adapter.py"
contract = Path(sys.argv[sys.argv.index("--contract") + 1]) if "--contract" in sys.argv else W / skill_rel / "e2e-adapter.json"
ex = R4 / "evidence/exports" / task
tpl = next(iter(sorted(glob.glob(str(ex / "*template_export*.zip")))))
base = next(iter(sorted(z for z in glob.glob(str(ex / "*.zip")) if "template_export" not in z)))
out = R4 / "evidence/skills" / short
out.mkdir(parents=True, exist_ok=True)
cand_dir = W / "project/fscrt-run04-create16/exports" / short
cand_dir.mkdir(parents=True, exist_ok=True)
cand = cand_dir / f"fscrt-{short}-candidate.zip"
props = dict(l.split("=", 1) for l in (W / "core/auth/fusionEnv.properties").read_text(encoding="utf-8").splitlines() if "=" in l and not l.startswith("#"))
base_url = props.get("restBaseUrl", "").strip()
env_name = props.get("environment", "etia-test").strip()


def run(step, args):
    p = subprocess.run([sys.executable, str(adapter), step, "--contract", str(contract), "--report", str(out / f"{step}{args[0] if args and args[0].startswith('_') else ''}.json")] + [a for a in args if not a.startswith("_")],
                       capture_output=True, text=True, cwd=str(W), env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    (out / f"{step}{args[0] if args and args[0].startswith('_') else ''}.log").write_text(p.stdout + "\n--stderr--\n" + p.stderr, encoding="utf-8")
    msg = (p.stdout + p.stderr).strip().splitlines()
    tail = " | ".join(m for m in msg if any(k in m.lower() for k in ("error", "status", "blocked", "fail", "invalid", "ready", "pass", "sha256")))[:600]
    print(f"{step}{args[0] if args and args[0].startswith('_') else ''}: rc={p.returncode} {tail or (msg[-1][:300] if msg else '')}")
    return p.returncode


if run("manifest", ["_tpl", "--package", tpl, "--environment", env_name, "--base-url", base_url, "--template-only", "true"]) != 0:
    sys.exit(1)
if run("manifest", ["_base", "--package", base, "--environment", env_name, "--base-url", base_url, "--template-only", "false"]) != 0:
    sys.exit(1)
if run("normalize", ["--baseline", base, "--request", request, "--design", design, "--blueprint-output", str(out / "blueprint.json"),
                     "--preview-output", str(out / "preview.json"), "--requirements-output", str(out / "requirements.json")]) != 0:
    sys.exit(1)
if run("build", ["--template", tpl, "--baseline", base, "--blueprint", str(out / "blueprint.json"),
                 "--requirements", str(out / "requirements.json"), "--output", str(cand)]) != 0:
    sys.exit(1)
rc = run("validate", ["--template", tpl, "--baseline", base, "--blueprint", str(out / "blueprint.json"),
                      "--requirements", str(out / "requirements.json"), "--package", str(cand)])
print("candidate:", cand if cand.exists() else "none", "| template:", Path(tpl).name, "| baseline:", Path(base).name)
sys.exit(rc)
