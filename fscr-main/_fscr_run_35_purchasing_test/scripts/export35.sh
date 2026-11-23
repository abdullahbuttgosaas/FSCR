#!/usr/bin/env bash
# Run 35: FSCR task-level CSV export (read-only) for each task; output under export_before/<TASK> or export_after/<TASK>.
# Usage: export35.sh before|after TASK [TASK ...]
W="C:/Users/PC/AppData/Local/Temp/claude/537d324d8fa4a5c1/7ac3c756-7f84-4cc1-8a73-06733818bf7d/scratchpad/fscr-work35"
R="E:/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_35_purchasing_test"
when=$1; shift
cd "$W"
for t in "$@"; do
  out="$R/export_$when/$t"; mkdir -p "$out"
  python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code "$t" --data --wait-seconds 400 --output-dir "$out" --no-open-browser > "$R/evidence/export_${when}_$t.log" 2>&1
  z=$(ls "$out"/*.zip 2>/dev/null | tail -1)
  if [ -n "$z" ]; then rm -rf "$out/unz"; mkdir -p "$out/unz"; (cd "$out/unz" && unzip -o -q "$z"); echo "$t OK $(ls "$out/unz" | tr '\n' ' ')"; else echo "$t NOZIP: $(tail -2 "$R/evidence/export_${when}_$t.log" | tr '\n' ' ')"; fi
done
