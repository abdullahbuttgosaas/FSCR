#!/usr/bin/env bash
# Run 17: read-only FSM data export of setup tasks through FSCR's task-level export, unmodified.
# Each export creates one Oracle export-process record (a read route, as in Run 09). No import, no write.
# Copied from Run 09 export_all.sh; changes: Run 17 paths only.
# Usage: export_all.sh <TASKCODE ...>
R="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_21_calendar_workbook"
OUTW='E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_21_calendar_workbook\evidence\exports'
cd "$R/fscr-work21" || exit 1
export PYTHONIOENCODING=utf-8
for t in "$@"; do
  echo "== $t start $(date '+%H:%M:%S')"
  python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code "$t" --data \
    --output-dir "$OUTW\\$t" --token-cache auto --no-open-browser --wait-seconds 900 2>&1 \
    | grep -E "process:|Wrote|rror|Status|Exception" | cut -c1-260
  echo "== $t end $(date '+%H:%M:%S')"
done
