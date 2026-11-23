#!/usr/bin/env bash
# Template + data export for each of the 15 Run 05 sampled skills through FSCR's task-level export (read-only exports;
# each creates one Oracle export process, recorded from this log). Output outside the project folder, so FSCR
# does not append to the project token-usage log. Usage: export_all.sh <TASKCODE ...>
R4W='E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_05_breadth'
R4="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_05_breadth"
cd "$R4/fscr-work5" || exit 1
export PYTHONIOENCODING=utf-8
for t in "$@"; do
  for mode in --template-only --data; do
    echo "== $t $mode start $(date '+%H:%M:%S')"
    python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code "$t" $mode \
      --output-dir "$R4W\\evidence\\exports\\$t" --token-cache auto --no-open-browser --wait-seconds 900 2>&1 \
      | grep -E "process:|Wrote|rror|Status|Exception" | cut -c1-260
    echo "== $t $mode end $(date '+%H:%M:%S')"
  done
done
