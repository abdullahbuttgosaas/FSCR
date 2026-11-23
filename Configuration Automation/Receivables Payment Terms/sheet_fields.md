# Receivables Payment Terms: sheet columns, request keys and Oracle's columns

Tabs in `page/sheet_definition.json` (2026-10-30). Every rule is checked by `run.py --plan` (`rpt_rules.py`); the
page only reads types (number, date, digits, yes-no) and required columns.

## Tab "Receivables Payment Terms" (one row per term) -> `AR_PAYMENT_TERM` (+ the base `AR_PAYMENT_TERM_TRANSLATION` row)

| Column | Key | Oracle column | Rule / default |
|---|---|---|---|
| Name * | name | Name (and the translation's Name) | 1-15 characters, no outer spaces; exact Name + Set Code in Oracle = skipped |
| Set Code * | set_code | SetCode (and every child's parent link + SetCode) | Oracle's set code; never defaulted |
| Item Description | description | Description (and the translation's Description) | max 240 |
| From Date | from_date | StartDateActive | YYYY-MM-DD; empty = Oracle's today minus one day |
| To Date | to_date | EndDateActive | after From Date |
| Base Amount | base_amount | BaseAmount | above 0; empty = 100 |
| Print Lead Days | print_lead_days | PrintingLeadDays | whole; above 0 and required with 2+ installments |
| Tax and Freight | tax_freight | FirstInstallmentCode | Include in the first installment = INCLUDE, Allocate across all installments = ALLOCATE; required with 2+; empty with 1 = INCLUDE |
| Discount Basis | discount_basis | CalcDiscountOnLinesFlag | Invoice amount = I, Lines only = L; required with a discount; empty without = I |
| Discount Date Basis | discount_date_basis | DiscountBasisDateType | Application / Receipt / Deposit date; empty = APPLICATION_DATE |
| Cutoff Day | cutoff_day | DueCutoffDay | whole 1-31 |
| Credit Check | credit_check | CreditCheckFlag | Y/N, empty = N |
| Prepayment | prepayment | PrepaymentFlag | Y/N, empty = N |
| (none) | | InUse, PartialDiscountFlag | always N |
| (none) | | CycleName, AttributeCategory, Attribute1-15 | always empty |
| (none) | | translation Language = SourceLang | Oracle's one base language (ETIA-TEST: US) |

## Tab "Receivables Term Lines" (one row per installment) -> `AR_PAYMENT_TERM_LINE` and `AR_PAYMENT_TERM_DISCOUNT`

| Column | Key | Oracle column | Rule |
|---|---|---|---|
| Payment Term Name * | (join only) | | the term's Name, exactly |
| Sequence | sequence | SequenceNum | digits; empty = row order |
| Relative Amount * | relative_amount | RelativeAmount | above 0; all add up to Base Amount |
| Days / Fixed Date / Day of Month | days / fixed_date / day_of_month | DueDays / DueDate / DueDayOfMonth | exactly one |
| Months Ahead | months_ahead | DueMonthsForward | required with (and only with) Day of Month |
| First / Second / Third Discount (%) | discount_percent / discount2_ / discount3_ | DiscountPercent (one discount row each, SequenceNum = the installment's) | 0-100, each percent once per installment, filled in order |
| ... Discount Days / Fixed Date / Day of Month / Months Ahead | discount*_days / _fixed_date / _day_of_month / _months_ahead | DiscountDays / DiscountDate / DiscountDayOfMonth / DiscountMonthsForward | one date each; Months Ahead with Day of Month |

Oracle's messages the folder turns into plain words: `rpt_package.MESSAGES` (FSCR `ora_error_handling.md:53-67`).
