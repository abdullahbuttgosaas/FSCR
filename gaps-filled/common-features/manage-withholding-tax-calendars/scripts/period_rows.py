"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 2 part 2 (2026-11-23). Offline: no Oracle call.

Write the --row arguments for the period file (AP_OTHER_PERIOD_PERIOD.csv) of a new Payables-style
"other period" calendar (Manage Withholding Tax Calendars / special calendars): one row per month of one
year, in the shape the export uses. Feed the output file to build_fsm_package.py as "@<file>".

Usage:
  python -I period_rows.py --name GAPFILL_X --type GENERAL --year 2027 --app-id 200 --out <RUN>/period_rows.txt
  [--first-month 1] [--months 12]

Row columns written (all others stay empty):
  AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_TYPE.CalendarType, CalendarName, CalendarType,
  ApplicationId, PeriodYear, PeriodNum, EnteredPeriodName (Jan..Dec), PeriodName (Jan-27),
  StartDate, EndDate (yyyy/mm/dd)
PeriodYear is the year of the first period; PeriodNum counts 1, 2, ... from --first-month.
"""
import argparse, calendar, sys
from pathlib import Path

MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--type", required=True, help="CalendarType, as in the header row (e.g. GENERAL)")
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--app-id", required=True, help="ApplicationId of the period rows, copied from the export")
    ap.add_argument("--first-month", type=int, default=1)
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not 1 <= a.first_month <= 12 or not 1 <= a.months <= 24:
        sys.exit("STOP: --first-month 1..12 and --months 1..24")
    lines = []
    y, m = a.year, a.first_month
    for n in range(1, a.months + 1):
        last = calendar.monthrange(y, m)[1]
        cols = {
            "AP_OTHER_PERIOD_TYPE.CalendarName": a.name, "AP_OTHER_PERIOD_TYPE.CalendarType": a.type,
            "CalendarName": a.name, "CalendarType": a.type, "ApplicationId": a.app_id,
            "PeriodYear": str(a.year), "PeriodNum": str(n), "EnteredPeriodName": MON[m - 1],
            "PeriodName": f"{MON[m - 1]}-{y % 100:02d}",
            "StartDate": f"{y:04d}/{m:02d}/01", "EndDate": f"{y:04d}/{m:02d}/{last:02d}",
        }
        lines.append("--row")
        lines.append("AP_OTHER_PERIOD_PERIOD.csv|" + "|".join(f"{k}={v}" for k, v in cols.items()))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {a.months} period rows to {a.out}")


if __name__ == "__main__":
    main()
