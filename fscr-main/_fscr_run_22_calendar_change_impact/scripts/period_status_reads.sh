#!/usr/bin/env bash
# Run 21: read-only period statuses (all applications) for the 25 ledgers of the 3 calendars. GET only via rget.py.
R="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_22_calendar_change_impact"; cd "$R" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8; F=/fscmRestApi/resources/11.13.18.05; mkdir -p evidence/rest/period_status
while IFS=$'\t' read -r cal name id; do
  echo -n "$cal | $name | "; python scripts/rget.py $F/accountingPeriodStatusLOV --all --query onlyData=true --query limit=500 --query "q=LedgerId=$id" --out "evidence/rest/period_status/$id.json" | head -1
done < scripts/ledger_ids.tsv
