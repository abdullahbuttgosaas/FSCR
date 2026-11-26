"""Import one FSM setup CSV package through FSCR's task-level import and keep the ProcessId.

Runs shared/setup-import/task-level-import/scripts/import_setup_task_csv.py with the output folder in the run
folder (outside the pack), saves the ProcessId to <run>/<label>_processid.txt and prints a redacted summary of
the process log (counts, errors, JBO messages). Never prints user names, tokens or server addresses.

If the connection drops after the import started, DO NOT import again: wait 2 minutes and check whether the
record exists (new export or REST), or fetch the log with --process-id.

Usage (from the FSCR root):
  python3 <this> --task-code AP_MANAGE_INVOICE_HOLDS_AND_RELEASES --zip load.zip --run <WORK>/runs/x --label imp1
  python3 <this> --task-code ... --run ... --label imp1 --process-id 1000...   (only fetch the log again)
Standard library only.
"""
import argparse, glob, os, re, subprocess, sys

MAIL = re.compile(r"[^@\s]+@[^@\s]+|(?<=Submitted By: )[^.\s]+(\.[A-Za-z0-9_]+)?|(?<=SubmittedBy\W{3})[^\"\s,]+")


def redact(t):
    t = re.sub(r"https?://\S+", "<url>", t)
    t = MAIL.sub("<hidden>", t)
    t = re.sub(r"/\S*(gwpayables|fscr-module-test-pack)\S*", "<path>", t)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-code", required=True)
    ap.add_argument("--zip")
    ap.add_argument("--run", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--process-id")
    ap.add_argument("--wait-seconds", default="600")
    a = ap.parse_args()
    out_dir = os.path.join(a.run, a.label + "_import")
    os.makedirs(out_dir, exist_ok=True)
    if a.process_id:
        cmd = [sys.executable, "shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py",
               "--task-code", a.task_code, "--process-id", a.process_id, "--token-cache", "auto",
               "--wait-seconds", a.wait_seconds, "--poll-interval", "15",
               "--output", os.path.join(out_dir, "import_process_log.txt")]
    else:
        cmd = [sys.executable, "shared/setup-import/task-level-import/scripts/import_setup_task_csv.py",
               "--task-code", a.task_code, "--zip-file", a.zip, "--token-cache", "auto", "--no-open-browser",
               "--wait-seconds", a.wait_seconds, "--poll-interval", "15", "--output-dir", out_dir]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    with open(os.path.join(out_dir, "console.log"), "w", encoding="utf-8") as fh:
        fh.write(out)
    pid = re.findall(r"(?:ProcessId\W+|process: |process )(\d{6,})", out)
    pid = a.process_id or (pid[0] if pid else "?")
    with open(os.path.join(a.run, a.label + "_processid.txt"), "w") as fh:
        fh.write(pid)
    print("exit", p.returncode, "ProcessId", pid)
    for line in out.splitlines():
        if re.search(r"Status|Completed|rror|Wrote|Retrieved", line):
            print("  ", redact(line)[:220])
    logs = [f for f in glob.glob(os.path.join(out_dir, "**", "*"), recursive=True)
            if os.path.isfile(f) and f != os.path.join(out_dir, "console.log")]
    for f in logs:
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        txt = txt.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", " ")
        keep = [l for l in txt.splitlines() if not re.search(r"nvironment|generated using", l)]
        keep = [l for l in keep
                if re.search(r"rows|processed|fail|error|JBO-|ORA-|required|invalid|success|warning|Status", l, re.I)]
        if keep:
            print("== log", os.path.basename(f)[-40:].split("_")[-1], "(redacted):")
            for l in keep[:80]:
                print("  ", redact(l)[:300])
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
