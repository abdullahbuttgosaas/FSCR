"""Read-only FSM setup-data export of one setup task through FSCR, saved under a neutral name.

Runs FSCR's shared/setup-export/task-level-export (--data) into a run folder, then renames the downloaded
ZIP to <run>/<label>.zip (FSCR's own file names contain the environment name; they are never kept or printed).
Prints only the ProcessId, status and the inner CSV row counts.

Usage (from the FSCR root):
  python3 <this> --task-code AP_MANAGE_AGING_PERIODS --run <WORK>/runs/aging --label before
  [--criteria-file criteria.json]   (optional SetupTaskCSVExportCriteria scope)
Standard library only. Read only on Oracle.
"""
import argparse, csv, glob, io, os, re, shutil, subprocess, sys, zipfile

MAIL = re.compile(r"[^@\s]+@[^@\s]+|(?<=Submitted By: )[^.\s]+(\.[A-Za-z0-9_]+)?|(?<=SubmittedBy\W{3})[^\"\s,]+")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-code", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--criteria-file")
    ap.add_argument("--wait-seconds", default="900")
    a = ap.parse_args()
    tmp = os.path.join(a.run, "_raw_" + a.label)
    os.makedirs(tmp, exist_ok=True)
    cmd = [sys.executable, "shared/setup-export/task-level-export/scripts/export_setup_task_csv.py",
           "--task-code", a.task_code, "--data", "--output-dir", tmp, "--token-cache", "auto",
           "--no-open-browser", "--wait-seconds", a.wait_seconds, "--poll-interval", "15"]
    if a.criteria_file:
        cmd += ["--export-criteria-file", a.criteria_file]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    with open(os.path.join(a.run, a.label + "_export_console.log"), "w", encoding="utf-8") as fh:
        fh.write(out)  # stays in WORK (outside the pack)
    pid = re.findall(r"(?:ProcessId\W+|process: )(\d{6,})", out)
    st = re.findall(r"StatusCode: ([A-Za-z_()]{4,}[^;\n]*)", out)
    print("exit", p.returncode, "ProcessId", pid[-1] if pid else "?", "status", st[-1] if st else "?")
    zips = glob.glob(os.path.join(tmp, "**", "*.zip"), recursive=True)
    if not zips:
        tail = re.sub(r"https?://\S+", "<url>", out[-1200:])
        print("no ZIP downloaded. Console tail (redacted):\n", MAIL.sub("<hidden>", tail))
        return 1
    dest = os.path.join(a.run, a.label + ".zip")
    shutil.move(max(zips, key=os.path.getmtime), dest)
    logs = glob.glob(os.path.join(tmp, "**", "*"), recursive=True)
    for f in logs:
        if os.path.isfile(f) and not f.endswith(".zip"):
            shutil.move(f, os.path.join(a.run, a.label + "_" + ("log" if "log" in f.lower() else "meta")
                                        + os.path.splitext(f)[1]))
    shutil.rmtree(tmp, ignore_errors=True)
    with open(os.path.join(a.run, a.label + "_processid.txt"), "w") as fh:
        fh.write(pid[-1] if pid else "?")
    zf = zipfile.ZipFile(dest)
    for n in zf.namelist():
        if n.endswith(".csv"):
            rows = list(csv.reader(io.StringIO(zf.read(n).decode("utf-8-sig"))))
            print(f"  {n}: {max(len(rows) - 1, 0)} rows")
    print("saved", a.label + ".zip in the run folder")
    return 0


if __name__ == "__main__":
    sys.exit(main())
