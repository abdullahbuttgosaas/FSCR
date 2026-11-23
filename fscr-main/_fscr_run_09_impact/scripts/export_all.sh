#!/usr/bin/env bash
# Run 08: data export of setup tasks through FSCR's task-level export (read-only; each creates one Oracle export
# process). Output under the Run 08 FSCR project exports folder (AGENTS.md), sub-folder = label (baseline/drift/...).
# Copied from Run 06 export_all.sh; changes: --data only, project exports destination, label argument.
# Usage: export_all.sh <label> <TASKCODE ...>
R8W='E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_09_impact\fscr-work9\project\draft_impl_project_20261104_r09\exports'
R8="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_09_impact"
cd "$R8/fscr-work9" || exit 1
export PYTHONIOENCODING=utf-8
L="$1"; shift
for t in "$@"; do
  echo "== $t $L start $(date '+%H:%M:%S')"
  python shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code "$t" --data \
    --output-dir "$R8W/$L/$t" --token-cache auto --no-open-browser --wait-seconds 900 2>&1 \
    | grep -E "process:|Wrote|rror|Status|Exception" | cut -c1-260
  echo "== $t $L end $(date '+%H:%M:%S')"
done
