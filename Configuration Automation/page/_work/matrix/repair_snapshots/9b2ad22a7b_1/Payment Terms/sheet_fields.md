# Payment Terms: fields for an upload-sheet tab

Every field of Oracle's **Create Payment Terms** screen, as the Payment Terms folder takes it
(2026-10-25). Labels are Oracle's screen labels; "key" is the folder's request key (`--run`
and `terms.json`). "Proven" = created in a real import and read back by the folder's verify
step (terms ZZ_TEST_PT_8505_*, see CLAUDE.md > Material). Check a request read-only with
`python "Payment Terms/browser_flow.py" --plan '<JSON>'`.

In the upload sheet (2026-10-25) these are three tabs: **Payment Terms** (the header, one row
per term), **Payment Term Lines** (one row per installment, in order, with its three discounts)
and **Payment Term Sets** (one row per set). Lines and sets name their term in **Payment Term
Name**, written exactly as the Name (capitals and spaces count). Empty From Date in the sheet =
Oracle's today minus one day, shown in the preview and sent as that date. See CLAUDE.md >
Upload sheet.

## Header (one per term)

| Oracle label | Key | Required | Allowed values | If empty | Rules and Oracle's messages | Status |
|---|---|---|---|---|---|---|
| Name * | `name` | yes | text, max 50 | - | Exact match: capitals and spaces count ("Net 30" and "net 30" are two terms). An existing name is skipped, nothing changed. No spaces at the start or end (folder). Same name twice in one request refused. Screen: "A record with the value Net 30 already exists. Enter a unique value." Import of 60 characters: "Value ... for field Name exceeds the maximum length allowed". | proven: exact match, capitals-only variant created, special characters `!@#&*()/é` created; 60 characters refused |
| From Date * | `from_date` | yes | date YYYY-MM-DD, or "today" (Oracle's today minus one day) | screen: Oracle's today | Screen: "The date or time entered is not valid." | proven |
| To Date | `to_date` | no | date | none | not before From Date (folder; no screen message, not proven at save) | proven (2027-12-31) |
| Item Description | `description` | no | text, max 240 | empty | Import of 241: "Value ... for field Description exceeds the maximum length allowed" | proven: 240 saved, 241 refused |
| Cutoff Day | `cutoff_day` | no | whole number 1-31 | empty | "The value of the Cutoff Day attribute must be between 1 and 31. (AP-810443)"; "The number is not a whole number." Meant for Day of Month terms (Oracle's help), but also accepted on a Days term (ZZ_TEST_PT_6142_CUTOFF_DAYS) | proven (15, 20) |
| Rank | `rank` | no | whole number, 0 or more | empty | "The number is not a whole number." Used to pick the more favorable term of invoice and purchase order. **Unique across all payment terms:** "A record with the value 5 already exists. Enter a unique value." (checked in the preview against Oracle's terms and the sheet, 2026-10-26) | proven (2, 5); duplicate refused ZZ_TEST_PT_6142_RANK5; negative not proven |

## Installments (one row each, at least one)

Each installment: **Due (%) or Amount Due**, and **one** way to set the due date: Days, Fixed
Date, Day of Month (+ Months Ahead), or Calendar.

| Oracle label | Key | Allowed values | Rules and Oracle's messages | Status |
|---|---|---|---|---|
| Due (%) | `due_percent` | number 0-100, decimals allowed | "The value of the Due attribute must be between 0 and 100. (AP-810443)". All lines together: "The total percentage for all payment terms lines must equal 100%. (AP-810270)" | proven (100, 60/40, 50/50, 25×4, 1×100, 0.1×1000) |
| Amount Due | `due_amount` | number, 0 or more | Not with percent in the same term: "You must either enter a percentage due or an amount due, not both. (AP-810315)". Last line must be 0: "To define an amount due payment term, the last terms line must be defined with zero amount due. (AP-810272)" | proven (500 then 0, with and without a discount) |
| Days | `days` | whole number, 0 or more | "You must enter either 0 or a positive number." | proven |
| Fixed Date | `fixed_date` | date | "The date is not in the correct format" | proven (2026-12-31; beside a Days line in one term) |
| Day of Month | `day_of_month` | whole number 1-31 (31 = last day) | "The value of the Day of Month attribute must be between 1 and 31. (AP-810443)" | proven (20, 25, 15) |
| Months Ahead | `months_ahead` | whole number, 0 or more | only with Day of Month (screen greys it out without). **Required with Day of Month** (0 = the same month): without it Oracle refuses the term at save, "You must enter months ahead because you entered a due day of the month or discount day of the month." (the screen says nothing on Tab; checked in the preview since 2026-10-26) | proven (1, 2, 0); refusal proven ZZ_TEST_PT_6142_DOM_NOMA |
| Calendar | `calendar` | AKPmt Calendar, AMN Calendar, DSS Calendar, N24 Calendar (Oracle's drop-down, read live) | unknown calendar refused with Oracle's list | proven (AKPmt Calendar) |

- One due-date way per installment: folder rule; a mix inside one line is **not proven**.
- Number of installments: 1000 accepted (proven); no maximum found.

## Discounts (per installment: First, Second, Third)

Keys in a page row: `discount_` (first), `discount2_`, `discount3_` + `percent`, `days`,
`day_of_month`, `months_ahead`. In `terms.json`: `"discounts": [{"percent", "days" |
"day_of_month" (+ "months_ahead")}, ...]`.

| Oracle label | Allowed values | Rules and Oracle's messages | Status |
|---|---|---|---|
| Discount (%) | number more than 0, up to 100 (0 refused: "You must enter a positive number.", ZZ_TEST_PT_6142_DISC0, 2026-10-26) | "The value of the Discount attribute must be between 0 and 100. (AP-810443)". Required with its days or day of month: "You must enter the discount percentage if you've already entered either the discount days, or the discount day of month and the months ahead. (AP-810447)". Second lower than first: "...second discount percentage that's less than the first... (AP-810459)"; third lower than second: "...third discount percentage that's less than the second... (AP-810454)" (equal refused) | proven (3/2/1; 2 on an amount term) |
| Days | whole number, 0 or more | first before second: "You must enter a first discount day that's before the second discount day. (AP-810418)"; second before third: folder rule (not proven) | proven (10/20/30) |
| Day of Month | whole number 1-31 | Days or Day of Month on one discount, not both (folder rule; not proven) | proven (day 10 and 5) |
| Months Ahead | whole number, 0 or more | only with that discount's Day of Month (screen greys it out); **required with that discount's Day of Month** (0 = the same month), same Oracle refusal as the due Day of Month (checked in the preview since 2026-10-26) | proven (1, 0); refusal proven ZZ_TEST_PT_6142_DISC_NOMA |

- A second discount needs the first, a third needs the second (folder rule).
- Only due dates can use a calendar, not discounts (Oracle's documentation; the screen has no
  calendar field for discounts).

## Set Assignments (0 or more per term)

| Oracle label | Key | Allowed values | Rules | Status |
|---|---|---|---|---|
| Set Code | `set_assignments` (page: rows with `set`) | one of Oracle's 37 set codes (Set Code drop-down / REST setIdSetsLOV): 001 CUSTOMER SITE, 1111, 21, 221, 23, 25010094, 25010114, 28REFDATA, 7382, A1_DATA_SET, AHSAN RDS, AKREFDATA, ASAD123, ASCEND_001, ASH-25010114, COMMON, CUSTOMER_RDS, DSSREFDATA, ENTERPRISE, HAHAREFDATA, ITBU, MA_CUST_SET, MGREF-AP, MGREFST, MNC_CUST_OM_RDS, MOMINA12, MWBKBU1, MWBKBU2, N24REFDATA, NMT, ORA25010114, PPREFDATA, PRC100R, S-31, SET0001, S_DATA_SET, TEST | not twice; unknown code refused with the list; none needed to save (a term needs a set to be used in a business unit, Oracle's docs) | proven: ENTERPRISE (no term used it before), COMMON + ENTERPRISE, COMMON + S_DATA_SET |
| Set Name, Item Description | - | filled by Oracle from the code | - | - |

## Before Create (read-only) and at Create

- **No Oracle needed:** every rule above except the lists: required fields, lengths, ranges,
  whole numbers, dates, To Date not before From Date, one due-date way, percent or amount,
  total 100, last amount 0, discount order and percents, Months Ahead with Day of Month and Day of
  Month with Months Ahead (due and each discount), the
  same name twice in the sheet.
- **With Oracle, read-only (`--plan`, about 65 s for a whole request):** Oracle's today, the
  Calendar and Set Code lists, and whether each name exists (exact).
- **Only at Create:** anything Oracle's import refuses that no rule above catches. The folder
  then reads the import log, says per term "saved" or "not saved: <Oracle's reason>", and a
  rerun skips the saved ones.

## Not proven

A mix of due-date ways inside one installment; Days and Day of Month on one discount; a To Date
before the From Date; a third discount with fewer days than the second; a negative Rank or
Amount Due; Cutoff Day on a Days or Fixed Date term; the highest number of installments
(1000 worked). The folder refuses the first five; it allows Cutoff Day on any term.

## Checked again 2026-10-26 (real imports ZZ_TEST_PT_6142_*)

Accepted by Oracle: Cutoff Day on a Days term; discounts by Day of Month in any order; a discount later than
the due date; discounts on Calendar and Fixed Date lines; due Days with a discount by Day of Month; a 0%
installment; one amount line of 0; 99999 days; 6 decimals in Due (%). Refused and now red in the preview:
Day of Month without Months Ahead (due and discount), a Rank another term has, a 0% discount. Also red:
"nan" / "inf" as numbers, and a To Date before a From Date written "today".
