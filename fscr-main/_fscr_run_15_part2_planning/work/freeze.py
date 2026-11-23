import datetime, hashlib, os, sys
run = sys.argv[1]
files = ["01_OFFERING_TASK_MAP.md", "01_OFFERING_TASK_MAP_tasks.csv", "01_identified-task-mapping.json",
         "02_WAVE_PLAN.xlsx", "03_TASK_DEPENDENCIES.md", "04_READINESS_CHECKLIST.md"]
now = datetime.datetime.now().astimezone()
lines = [f"FREEZE RECORD – FSCR Run 15 (Part 2 planning)",
         f"Frozen at: {now:%Y-%m-%d %H:%M:%S %Z (UTC%z)}",
         "Rule: outputs below are not edited after this time. Comparison with the manual baseline starts after this record.", ""]
for f in files:
    p = os.path.join(run, f)
    h = hashlib.md5(open(p, "rb").read()).hexdigest()
    lines.append(f"{h}  {os.path.getsize(p):>9} bytes  {f}")
open(os.path.join(run, "work", "freeze_record.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
