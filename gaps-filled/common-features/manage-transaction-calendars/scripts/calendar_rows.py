"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 3 (2026-11-20). Offline: no Oracle call.

Write the date rows of one new transaction calendar as an argument file for build_fsm_package.py
(use it as @<file>). One row per day from --start to --end: TransactionDate (yyyy/mm/dd, the export's
format), DayOfWeek (MON..SUN, required by Oracle) and BusinessDayFlag (Y on the business weekdays,
N on the others and on each --holiday).

Usage:
  python -I calendar_rows.py --name GAPFILL_TC_X --start 2026-11-23 --end 2026-11-29 \
      --business MON,TUE,WED,THU,FRI [--holiday 2026-11-26] --out <run>/date_rows.txt
"""
import argparse, datetime as dt, sys

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
FILE = "ORA_GL_TRANSACTION_CALENDAR_DATE.csv"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--start", required=True, help="yyyy-mm-dd")
    ap.add_argument("--end", required=True, help="yyyy-mm-dd")
    ap.add_argument("--business", default="MON,TUE,WED,THU,FRI")
    ap.add_argument("--holiday", action="append", default=[], help="yyyy-mm-dd, not a business day")
    ap.add_argument("--max-days", type=int, default=31)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s, e = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    n = (e - s).days + 1
    if n < 1 or n > a.max_days:
        sys.exit(f"STOP: {n} days; keep 1..{a.max_days} (change --max-days only if allowed)")
    bus = {d.strip().upper() for d in a.business.split(",")}
    if not bus <= set(DAYS):
        sys.exit(f"STOP: --business must use {','.join(DAYS)}")
    hol = {dt.date.fromisoformat(h) for h in a.holiday}
    lines = []
    for i in range(n):
        d = s + dt.timedelta(days=i)
        dow = DAYS[d.weekday()]
        flag = "Y" if dow in bus and d not in hol else "N"
        lines += ["--row", f"{FILE}|GL_TRANSACTION_CALENDAR.Name={a.name}|TransactionDate={d:%Y/%m/%d}|DayOfWeek={dow}|BusinessDayFlag={flag}"]
    open(a.out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"wrote {n} date rows to {a.out}")


if __name__ == "__main__":
    main()
