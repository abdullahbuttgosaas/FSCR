# Payment Terms

Task: **Manage Payment Terms** (Setup and Maintenance > Payables functional area).
Task code (from the export metadata `ObjectShortName`): `AP_MANAGE_PAYMENT_TERMS`.
Status summary: UI-only route automated with Playwright (`browser_flow.py`): export, add
rows, import, export again and compare. **Every field of Oracle's Create Payment Terms
screen PROVEN by real creates on 2026-10-25** (ZZ_TEST_PT_8505_*, see Field rules and
Material). The only manual step is the one-time sign-in (`common/login_once.py`). REST route
out of scope (UNTESTED). Field-by-field reference for the upload sheet: `sheet_fields.md`.

## Input rules

Check every request against this before doing any work (root CLAUDE.md > Input rules).
`python "Payment Terms/browser_flow.py" --plan <file or JSON>` checks a request read-only
(every rule below, Oracle's lists, and whether each name exists).

REQUIRED - if missing or unclear, stop and ask in plain words, all missing items in one message:
- Name (max 50 characters). **Exact match: capitals and spaces count** ("Net 30" and
  "net 30" are two terms; this pod has "PP payment term" and "PP Payment Term"). An existing
  name is skipped, never changed. Outer spaces are refused by the folder (Oracle would keep
  them: "AZ " exists here).
- From Date (`YYYY-MM-DD` or `"today"`).
- At least one installment, each with **Due (%) or Amount Due** and **one way to set its
  due date**: Days, Fixed Date, Day of Month (+ Months Ahead), or Calendar.

OPTIONAL - if missing, Oracle's default (empty) is used:

| Field | Rule |
|---|---|
| To Date | not before From Date |
| Item Description | at most 240 characters (Oracle's limit, proven) |
| Cutoff Day | whole number 1-31 (Oracle AP-810443); meant for Day of Month terms |
| Rank | whole number, 0 or more (the folder's rule; Oracle's screen also took -1, not proven at save) |
| Discounts per installment | up to 3 (First, Second, Third), each: percent + Days, or percent + Day of Month (+ Months Ahead) |
| Set assignments | any of Oracle's set codes (37 on 2026-10-25), several per term, none needed |

Dates: `YYYY-MM-DD`, or `"today"` = **Oracle's today minus one day**. Oracle's today is
read from the screen, never the PC clock: the From Date that Create Payment Terms fills
in by itself (Manage Payment Terms > Create, left with Cancel). The script prints a NOTE
with the date it used.

## Field rules (all checked before the import, all problems at once)

Proven on Oracle's screen or by a real import on 2026-10-25 unless marked otherwise.

| Rule | Source / Oracle's message |
|---|---|
| Name required, max 50 | screen (box holds 50); import: "Value ... for field Name exceeds the maximum length allowed" |
| Name exists (exact) -> skipped | screen: "A record with the value Net 30 already exists. Enter a unique value." ("net 30" accepted) |
| Same name twice in one request | folder rule |
| From Date required, To Date not before From Date | folder rule (To Date before From Date gave no screen message; not proven at save) |
| Item Description max 240 | import of 241: "Value ... for field Description exceeds the maximum length allowed" |
| Cutoff Day 1-31, whole | "The value of the Cutoff Day attribute must be between 1 and 31. (AP-810443)" |
| Rank whole number | "The number is not a whole number. Enter a whole number." |
| Due (%) 0-100, decimals allowed | "The value of the Due attribute must be between 0 and 100. (AP-810443)" |
| Percent term: total exactly 100 | "The total percentage for all payment terms lines must equal 100%. (AP-810270)" (user, screen) |
| All percent or all amount | "You must either enter a percentage due or an amount due, not both. (AP-810315)" (user, screen) |
| Amount term: last line amount 0 | "To define an amount due payment term, the last terms line must be defined with zero amount due. (AP-810272)" (user, screen) |
| Amount Due 0 or more | folder rule (negative not tried) |
| One due-date way per installment | folder rule (a mix inside one line is **not proven**; lines with different ways in one term are proven) |
| Days whole, 0 or more | "You must enter either 0 or a positive number" / "not a whole number" |
| Day of Month 1-31 | "The value of the Day of Month attribute must be between 1 and 31. (AP-810443)" |
| Months Ahead 0 or more, only with Day of Month | screen greys Months Ahead out until Day of Month is filled |
| Day of Month needs Months Ahead (due and each discount; 0 = same month) | import: "You must enter months ahead because you entered a due day of the month or discount day of the month." Nothing on screen at Tab (probed 2026-10-26: Months Ahead becomes editable and stays empty). Proven 2026-10-26: ZZ_TEST_PT_6142_DOM_NOMA and _DISC_NOMA refused, _DOM_MA0 (0 for both) created. Seen first on another PC for "Pre-order Standard Payment" / "... Return". Checked by `--plan` since 2026-10-26. |
| Fixed Date a real date | "The date is not in the correct format" / "The date or time entered is not valid" |
| Calendar one of Oracle's list | drop-down: AKPmt Calendar, AMN Calendar, DSS Calendar, N24 Calendar (2026-10-25) |
| Discount (%) 0-100 | "The value of the Discount attribute must be between 0 and 100. (AP-810443)" |
| Discount % required with its days / day of month | "You must enter the discount percentage if you've already entered either the discount days, or the discount day of month and the months ahead. (AP-810447)" (user, screen) |
| A discount: Days or Day of Month, not both; one of them given | folder rule (both together were accepted on screen; not proven at save) |
| Discount Months Ahead only with its Day of Month | screen greys it out |
| Second discount needs the first, third needs the second | folder rule |
| Second % lower than first | "You must enter a second discount percentage that's less than the first discount percentage. (AP-810459)" (equal refused too) |
| Third % lower than second | "You must enter a third discount percentage that's less than the second discount percentage. (AP-810454)" (proven on screen 2026-10-25; equal refused too) |
| First discount days before second | "You must enter a first discount day that's before the second discount day. (AP-810418)" (user, screen) |
| Second discount days before third | folder rule (no screen message on a lower third; not proven at save) |
| Set code one of Oracle's list, not twice | Set Code drop-down (37 codes) |

## Route status

- **2026-10-25: every field PROVEN** (classic layout), terms ZZ_TEST_PT_8505_*: Days,
  Fixed Date, Day of Month + Months Ahead + Cutoff Day, Calendar, To Date + Rank, Amount Due
  500 then 0 (with and without a first discount 2% / 10 days), three discounts (3/10, 2/20,
  1/30), a discount by Day of Month + Months Ahead, a set no term used before (ENTERPRISE),
  two sets, 4 / 100 / **1000** installments (no maximum found), a Fixed Date line beside a
  Days line, a name differing only in capitals from an existing one, special characters
  (`!@#&*()/é`), a 240-character description, and one term through the page's `--run` with
  every kind of field. Each read back by the second export: every column as built, all
  existing rows unchanged. A run takes about 2.5 minutes for 1 to 13 terms.
- **Several terms in one import: PROVEN.** Oracle saves the good terms and drops only a bad
  one (batch B: two good + a 60-character name -> the two saved, the bad one not). The results
  page then says "Completed with errors" for all 3 business objects and names nothing; the
  **log file** ("Download Log File") names the row and the field, e.g. "Row Identifier:
  ZZ_TEST_PT_8505_BAD_XXX... Status: Error ... JBO-27040: Value ... for field Name exceeds the
  maximum length allowed." The folder downloads the log, reads which terms Oracle refused and
  why, reads the after-export for which terms got in, verifies those, and stops with "Saved and
  checked: ... Not saved: X (reason)". A rerun skips the saved ones (exact name), so nothing is
  made twice.
- 2026-10-21: Oracle is back on the classic Setup and Maintenance page; this folder's
  `classic_setup.py` (`Setup(ui)`) detects the layout and runs the classic Export/Import to
  CSV File steps, or delegates to `common/browser.py` on Redwood. ImportNotClean (an import
  that ends with errors) is raised on classic only; on Redwood the shared helper still stops
  the run (not re-proven since 2026-10-20).
- Earlier proofs: ttttttttt (classic, 2026-10-21), ZZ_TEST_3593 (Redwood, 2026-10-20),
  ZZ_POC_TERM5/6/7 (2026-10-19), ZZ_TEST_7166 (first page `--run`, 2026-10-21).
- **REST / API route: UNTESTED, out of scope** for this folder.

## How to do it

From the project root (sign-in must be saved on this PC; see root First-run setup):

```
python "Payment Terms/browser_flow.py" --plan [terms.json | '<JSON>']   # read-only, see below
python "Payment Terms/browser_flow.py" --check     # read-only: screens + Oracle's today
python "Payment Terms/browser_flow.py" --dry-run   # export + build import zip, no import
python "Payment Terms/browser_flow.py"             # full run (headless)
python "Payment Terms/browser_flow.py" --headed    # same, browser visible
```

Requirements file `Payment Terms/terms.json` (several terms go in one import):

```json
{"terms": [{
  "name": "Net 30 Example",              // required, max 50, exact (capitals and spaces count)
  "from_date": "2026-10-18",             // required, YYYY-MM-DD or "today"
  "to_date": "2027-12-31",               // optional
  "description": "...",                  // optional, max 240
  "cutoff_day": 15,                      // optional, 1-31
  "rank": 1,                             // optional, whole number
  "installments": [                      // required, at least one
    {"due_percent": 60,                  // or "due_amount": 500 (all lines the same kind)
     "days": 30,                         // or "fixed_date" / "day_of_month" (+ "months_ahead") / "calendar"
     "discounts": [                      // optional, up to 3, percents going down, days going up
       {"percent": 2, "days": 10},
       {"percent": 1, "day_of_month": 5, "months_ahead": 1}]},
    {"due_percent": 40, "calendar": "AKPmt Calendar"}
  ],
  "set_assignments": ["COMMON", "ENTERPRISE"]   // optional, any of Oracle's set codes
}]}
```

(Comments are documentation only; the real file is plain JSON. Unknown keys are refused.)

What `browser_flow.py` does (all through the UI, via `common/browser.py` OracleUI):
1. Prints host and ORACLE_ENV, refuses production, checks every rule (Field rules),
   listing all problems at once.
2. When a term uses "today", a calendar or sets: Create Payment Terms is opened read-only
   (`screen_lists()`): Oracle's today from From Date; the Calendar and Set Code drop-downs
   after adding an installment row and a set row to the unsaved form (rows need a name, so a
   random ZZ_TEST_PT_LISTS_ name is typed); Cancel, Yes. Unknown calendar or set code stops.
3. Fresh export; terms whose exact name exists are skipped.
4. Rows built from the export's columns (layout of the newest user-made term): header (Name,
   EnabledFlag/Type from that term, StartDateActive, EndDateActive, DueCutoffDay, Rank,
   Description), one line per installment (SequenceNum, DuePercent or DueAmount, DueDays /
   FixedDate `YYYY/MM/DD` / DueDayOfMonth + DueMonthsForward / Calendar by name,
   DiscountPercent/Days/DayOfMonth/MonthsForward and the same with 2 and 3), translation
   (Name, Description, US), one subscription per set code. Attribute* and GlobalAttribute*
   columns stay empty; who columns are copied and replaced by Oracle.
5. Import. If Oracle ends it "Completed with errors", the log file is downloaded into
   `_work/` and read (which rows failed and why), and the run carries on to step 6.
6. Second fresh export: which terms are there (saved) and which not; every saved term's rows
   are compared column by column (numbers by value), all existing rows unchanged.
7. Deletes `_work/` only if everything passed; on failure keeps the zips, the import log
   and `fail_*.png` / `fail_*.txt`.

`--plan` (read-only, 2026-10-25): every rule that needs no Oracle first, then one browser
visit: Oracle's today, Calendar and Set Code lists (Create Payment Terms, Cancel) and one
export for the names. Prints one JSON line: `{"ok", "lists": {"today", "calendars", "sets"},
"results": [{"name", "status": "new" | "exists" | "problems", "problems": [{"key", "row",
"text"}], "skipped", "existing"}]}`. Takes a request file, one page request or a list.
About 65 seconds. Tried 2026-10-25: exact name -> exists; same name with other capitals ->
new; unknown calendar / set code -> listed with Oracle's values; To Date before From Date,
second discount not lower, second discount days before first, Months Ahead without Day of
Month, a line without a due-date way, percent and amount mixed, a name twice -> all listed.

`--check` (read-only): opens Actions > Export to CSV File > Create New and Import from CSV
File > Create New, confirms their fields and Submit, leaves each with Cancel; reads Oracle's
today from Create Payment Terms (Cancel). Re-proven 2026-10-25 (35 s).

## Business objects and file layout

The export screen names 3 business objects (Payment Term Header 320, Payment Term
Line 330, Payment Term Subscription 340); the results page shows "Total Objects 3". The zip
holds 4 CSVs + metadata (translation belongs to the header):

| File | Key column(s) | Columns |
|---|---|---|
| `AP_TERM_HEADER.csv` | `Name` | who columns, `EnabledFlag` (Y), `DueCutoffDay`, `Type` (STD), `StartDateActive`, `EndDateActive`, `Rank`, `AttributeCategory`, `Attribute1-15`, `Description`, `GlobalAttributeCategory`, `GlobalAttribute1-20`, `GlobalAttributeDate1-5`, `GlobalAttributeNumber1-5` |
| `AP_TERM_LINE.csv` | `AP_TERM_HEADER.Name`, `SequenceNum` | who columns, `DuePercent`, `DueAmount`, `DueDays`, `DueDayOfMonth`, `DueMonthsForward`, `DiscountPercent`, `DiscountDays`, `DiscountDayOfMonth`, `DiscountMonthsForward` (and the same with 2 and 3), `AttributeCategory`, `Attribute1-15`, `FixedDate`, `Calendar` |
| `AP_TERM_SUBSCRIPTION.csv` | `AP_TERM_HEADER.Name`, `SetCode` | who columns |
| `AP_TERM_HEADER_TRANSLATION.csv` | `AP_TERM_HEADER.Name`, `Language` | who columns, `Name`, `Description`, `Language` US, `SourceLang` US |
| `ASM_SETUP_CSV_METADATA.xml` | | `ObjectShortName` AP_MANAGE_PAYMENT_TERMS; keep unchanged |

Format: UTF-8, no BOM, every field quoted, `\n` line endings, zip deflated. Dates `YYYY/MM/DD`.

## Page interface

Contract: root CLAUDE.md > Page interface (helper `common/page.py`). One payment term per
`--run`; `terms.json` and the normal commands are unchanged.

```
python "Payment Terms/browser_flow.py" --spec
python "Payment Terms/browser_flow.py" --options set_assignments.set      # REST setIdSetsLOV, 37
python "Payment Terms/browser_flow.py" --options installments.calendar    # screen drop-down, about 40 s
python "Payment Terms/browser_flow.py" --run '{"name": "Net 30", "from_date": "today", "installments": [{"due_percent": 100, "days": 30}]}'
```

| Key | Label | Required | Type |
|---|---|---|---|
| name | Payment term name | yes | text |
| from_date | From date | yes | date |
| installments | Installments | yes | rows (at least 1) |
| description | Description | no | text |
| to_date | To date | no | date |
| cutoff_day | Cutoff day of the month | no | number |
| rank | Rank | no | number |
| set_assignments | Reference data sets | no | rows (set: pick) |

Installment row (2026-10-25): due_percent, due_amount, days, fixed_date (date),
day_of_month, months_ahead, calendar (pick), and for each discount `discount_`, `discount2_`,
`discount3_` + `percent`, `days`, `day_of_month`, `months_ahead` (all optional in the
contract; the rules above decide). Result `created` = the term as the after-export shows it
(every filled column). A stop says in `error.detail` `{"message", "saved": "no" | "yes" |
"maybe", "registry_id": null}`; a term Oracle's import refused gives INVALID_REQUEST with
Oracle's reason ("Oracle refused the payment term: Value ... for field Description exceeds the
maximum length allowed. Nothing was saved in Oracle."). Steps: reading 5, checking 20,
creating 50, verifying 85, done 100.
Tried 2026-10-25: `--spec` OK; `--run` ZZ_TEST_PT_8505_PAGE (60% in 30 days with discounts
3%/10 and 1.5%/20, 40% on day 15 two months ahead with discount 2% on day 5 one month ahead,
To Date 2028-06-30, Rank 2, Cutoff 20, sets COMMON and S_DATA_SET): created and every column
read back, 157 s; the same name again -> skipped with its values, 60 s.

## Upload sheet (2026-10-25)

The page's upload sheet has three tabs for this folder (root CLAUDE.md > The upload sheet >
Payment Terms module): Payment Terms, Payment Term Lines, Payment Term Sets, joined by
Payment Term Name exactly (capitals and spaces count). Field reference: `sheet_fields.md`.
- Preview: the page sends every term (page request shape) to `--plan` in one call. Besides the
  rules and lists it gives per term `"summary"` ("2 installments: 50% in 30 days; 50% in 60
  days. 1 set: COMMON. From 2026-10-24."), `"found": {"name": ...}` when Oracle has a name that
  differs only in capitals or spaces (yellow: Oracle treats it as a new term), `"skipped"` for an
  exact existing name, and a `"fix"` per problem. Calendar and Set Code are checked here against
  Oracle's live lists (the page doesn't check them a second time). Empty From Date: the preview
  shows Oracle's today minus one day and sends that date.
- Create: `--run-batch '<JSON list>'` makes all new terms of the upload in ONE import (the
  folder's normal flow), then answers one result per term: created and verified / already there
  (skipped) / "Oracle refused the payment term X: <reason from the import log>. Nothing was saved
  in Oracle." (INVALID_REQUEST, no repair) / saved but not matching (VERIFY_FAILED, saved yes). A
  stop before Oracle answers (screen, sign-in) also gives a top-level error for the page's repair
  rules; the rerun skips what was saved. Per-term verify results (`verify(..., per)`) feed this.
- Tested 2026-10-25 through the page, previews only (no term created): `manual-notes/
  Payment_Terms_TEST_good.xlsx` (ZZ_SHEET_PT_4766_NET45, _TWO, _EOM, _AMT, _DISC, _FIXED): ready,
  6 summaries; `..._bad.xlsx`: 12 red problems (percent total 99, amount not ending in 0, percent
  and amount mixed, Months Ahead without Day of Month, second discount not lower, unknown
  calendar, unknown set code, name over 50, a name twice, two terms without lines, a line whose
  term is missing) and the yellow note for "net 30"; an exact "Net 30" -> skipped. `--run-batch`
  and the page's one-call run were tested offline only (Oracle replaced).

## Preview versus Create (2026-10-26)

Everything Oracle refused at Create is now found by `--plan` (the preview). Proven by real imports
on 2026-10-26 (ZZ_TEST_PT_6142_*), each term testing one rule the preview did not check:

| Rule | Oracle | Preview now |
|---|---|---|
| Day of Month (due or a discount) needs Months Ahead, 0 allowed | refused: "You must enter months ahead because you entered a due day of the month or discount day of the month." (DOM_NOMA, DISC_NOMA; DOM_MA0 with 0 created). The screen says nothing at Tab. First seen on another PC: "Pre-order Standard Payment" / "... Return" | red, "add Months Ahead (0 means the same month, 1 the next month)" |
| Rank unique across ALL payment terms | refused: "A record with the value 5 already exists. Enter a unique value." (RANK5) | red against the export's ranks and earlier rows of the upload, with a free rank as the fix |
| Discount % more than 0 | refused: "You must enter a positive number." (DISC0) | red |
| "nan" / "inf" as a number | would reach the import as text | red ("must be a number") |
| To Date before a From Date written "today" | (folder rule) not compared before | red once Oracle's today is known |

Accepted by Oracle (no rule needed; created and checked): Cutoff Day on a Days term (CUTOFF_DAYS); two
discounts by Day of Month in any order (DISC_DOM_ORDER, 20 then 10); a discount later than the due date
(DISC_AFTER_DUE, due 10 days, discount 20 days); a discount on a Calendar line (DISC_CAL) and on a Fixed
Date line (DISC_FIXED); due by Days with a discount by Day of Month (DAYS_DISC_DOM); a 0% installment
(ZERO_LINE); a single amount line of 0 (AMT0); 99999 days (DAYS_BIG); 6 decimals (PCT_DEC 33.333333 /
66.666667). The name box on Create Payment Terms holds 50 characters.

**Still only at Create** (not provable without saving, or never seen): anything else the import log
refuses. The card quotes Oracle's reason per term, the others are saved, a rerun skips what was saved.
**Pause and ask (on since 2026-10-26):** `--run-batch` turns Oracle's import reason into `detail.problems`
(`refusal_problems()`): Months Ahead (the installment / discount without it; suggestions 0, 1; the answer goes into
that installment), Rank already used (free ranks from the pre-import export), a 0% discount, Name / Description
too long (shortened). Other reasons stay a plain card. Proven 2026-10-26 through the page: ZZ_TEST_PT_6142_ASK3
(rank 883 taken after the preview by ZZ_TEST_PT_6142_RANKTAKER2) -> asked with 885/886/887; "881" refused in the
panel (used by ASK1); 885 -> created. ASK5 (884, taken by RANKTAKER3) -> skipped, only it in the failed-only sheet
with Oracle's reason on its Rank cell.

## Related folders

None noted. (If this configuration needs another folder's object, note it here, tell
the user and wait for their go-ahead before writing any code.)

## Known gotchas

- 2026-10-26: **Lost clicks on Oracle's busy pages: every browser step checked and done again** with the shared
  retry helper `ui.retry()` (`common/browser.py`: up to 3 tries, a short pause and a fresh wait each time, then one
  clear failure "Oracle's <step> after 3 tries", which `--plan` passes to the page). `classic_setup.py` (same steps
  as Business Units' copy, which this copy lacked: the result row clicked again): Offering, Search Tasks, the result
  row, the Actions menu, submenu and entry, the history's results link, the task link, Cancel in the check.
  `screen_lists()`: Create (the form counts as open only when a From Date shows Oracle's default: Manage Payment
  Terms' own filter row has an empty "From Date" box too, which a first version of this fix took for the form),
  the Name typed in, each Add Row of the unsaved form only while its row hasn't shown, the Calendar and Set Code
  lists read again while empty, Cancel / Yes until the form has closed. **Never retried:** the import Submit.
- 2026-10-25: Oracle's name check is exact (capitals and spaces count); the folder compared
  names ignoring capitals before and would have skipped "net 30" when "Net 30" exists. Fixed.
- 2026-10-25: an import with one bad term ends "Completed with errors" for every business
  object, but the good terms ARE saved. Never treat such an import as "nothing saved": the
  after-export decides (see Route status).
- 2026-10-25: Create Payment Terms fills its From Date a moment after the field appears;
  reading it at once gave an empty value. `screen_lists()` waits up to 20 s.
- 2026-10-25: installment and set rows can't be added on Create Payment Terms before the
  header has a name ("You can't enter detail records without entering data for the master
  record."); the list reading types a random ZZ_TEST_PT_LISTS_ name and never saves.
- 2026-10-21: Oracle switched back to the classic Setup and Maintenance page; fixed inside
  this folder with `classic_setup.py` (copied from the classic steps proven in Business
  Units, owned here); all export/import/check/open_task calls go through `ui.setup`.
- 2026-10-20: Redwood Set Up page. Export = Actions > Export ("New Setup Export"); status on
  Export History. Import = Actions > Import (a file drop area).

Playwright route (handled in `common/browser.py`):
- The "Oracle Guided Learning" pop-up is blocked (route aborted).
- Task Actions button: `button[title="Manage Payment Terms : Actions"]`; menu items exist
  hidden once per task row; only the visible one may be clicked.
- Follow processes by NAME on the View All history page. Statuses seen: Not started, In
  progress, Completed successfully, Completed with errors (stage "Ready for error review").
- Use the page's Done button, never browser Back. Downloads go straight into `_work/`.
- Session expiry shows Oracle's sign-in page: the script stops and says to run
  `common/login_once.py` again.

Data:
- Re-importing all existing rows unchanged does NOT modify them (checked by re-export).
- Process dates in the UI are shown in a different time zone.

## Not proven

- Whether Oracle refuses a mix of due-date ways inside ONE installment, Days and Day of Month
  together on one discount, a To Date before the From Date, or a third discount with fewer days
  than the second (the folder refuses all of these).
- A negative Rank or Amount Due at save (the folder refuses them).
- Cutoff Day on a Days or Fixed Date term (allowed by the folder; Oracle's older docs say not to).
- The highest number of installments (1000 were accepted).
- The Redwood layout with the new import-error handling.

## Material

- `manual-notes/` - nothing yet.
- Test terms in this TEST pod (not deletable by scripts): ZZ_POC_TERM1 (by hand),
  ZZ_POC_TERM2 (manual CSV import), ZZ_POC_TERM5, ZZ_POC_TERM6, ZZ_POC_TERM7 and
  ZZ_POC_TERM8, ZZ_DEMO_TERM (2026-10-19), ZZ_TEST_8751, ZZ_TEST_3593 (2026-10-20), ttttttttt,
  ZZ_TEST_7166 (2026-10-21).
- 2026-10-25 (from 2026-10-24 = Oracle's today minus one day): ZZ_TEST_PT_8505_DAYS (100% in
  30 days), _FIXED (fixed 2026-12-31), _DOM (cutoff 15, day 20, 1 month ahead), _CAL (AKPmt
  Calendar), _TODATE (45 days, to 2027-12-31, rank 5), _AMT (500 in 30 days, 0 in 60), _AMTDISC
  (same + 2%/10 days), _DISC3 (60 days, 3%/10, 2%/20, 1%/30), _DISCDOM (cutoff 15, day 25 one
  month ahead, discount 2% day 10 one month ahead), _SET1 (ENTERPRISE), _SET2 (COMMON +
  ENTERPRISE), _LINES4, _LINES100, _LINES1000, _MIXLINES (50% in 30 days + 50% fixed
  2027-01-31), zz_test_pt_8505_days (capitals only differ from _DAYS), "ZZ_TEST_PT_8505
  !@#&*()/é", _DESC240, _PAGE (the page `--run`). Refused on purpose, not in Oracle:
  ZZ_TEST_PT_8505_BAD_XXX... (60-character name), ZZ_TEST_PT_8505_DESC241.
