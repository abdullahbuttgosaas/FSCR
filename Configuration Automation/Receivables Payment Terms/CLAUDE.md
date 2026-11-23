# Receivables Payment Terms

Task: **Manage Receivables Payment Terms**, code `AR_MANAGE_RECEIVABLES_PAYMENT_TERMS` (Setup and Maintenance >
offering **Financials** > functional area **Customer Billing**). Status summary: built 2026-10-30 and tested
**offline only** (page matrix, Oracle replaced by the pod's saved files); **no live run yet** (route UNTESTED on
Oracle). The page shows it under the **Receivables** side of the Order Management | Receivables switch.

This is NOT the Payables folder `Payment Terms/` (`AP_MANAGE_PAYMENT_TERMS`, shown on the page as "Payment Terms
(Payables)"). The two never share code or files.

Built from the spec `RECEIVABLES_PAYMENT_TERMS_SPEC.md` (moved 2026-10-30 to `E:\GoSaaS\Configuration Automation
v2.1\fscr-main\_fscr_spec\`), which takes its Oracle knowledge from the FSCR repo skill
`pillars/erp/financials/customer-billing/manage-receivables-payment-terms` (read-only).

## Input rules

REQUIRED (ask in one plain message if missing; never ask for codes or IDs):
- Name: 1-15 characters (Oracle's limit for Receivables terms), no space at the start or end. Capitals and spaces
  count. An existing **Name + Set Code** is skipped and never changed.
- Set Code: one of Oracle's reference data sets (exact code). **Never defaulted** (not COMMON, not ENTERPRISE).
- At least one installment: Relative Amount (its share of the Base Amount, above 0, not money) and ONE due date:
  Days, Fixed Date, or Day of Month + Months Ahead.
- With **2 or more installments**: Print Lead Days (whole number above 0) and Tax and Freight ("Include in the first
  installment" / "Allocate across all installments"). **Never defaulted.**
- With **any discount**: Discount Basis. **Never defaulted.** Only "Invoice amount" (I) and "Lines only" (L) are
  offered (see Open items).
- Base language: taken from Oracle (the one language its terms' names use, US on ETIA-TEST). Zero or several -> the
  preview says so in red and nothing is created (no sheet column yet). **Never defaulted.**

OPTIONAL - if missing, the create default (FSCR `ora_defaulting_rules.md:20-27`):

| Request key | Sheet column | Default | Rule |
|---|---|---|---|
| description | Item Description | none | max 240; also the base-language name row's description |
| from_date | From Date | Oracle's today minus one day (the page sends the date it showed) | YYYY-MM-DD |
| to_date | To Date | none | strictly after From Date (and after Oracle's today on the sheet) |
| base_amount | Base Amount | 100 (installments are percentages) | above 0; installments add up to it exactly |
| print_lead_days | Print Lead Days | none (1 installment: may stay empty) | whole number, 0 or more; above 0 with 2+ |
| tax_freight | Tax and Freight | Include in the first installment, **1 installment only** | the two labels above |
| discount_basis | Discount Basis | Invoice amount, **only when no discount** | Invoice amount / Lines only |
| discount_date_basis | Discount Date Basis | Application date | Application / Receipt / Deposit date |
| cutoff_day | Cutoff Day | none | whole number 1-31 |
| credit_check / prepayment | Credit Check / Prepayment | No | Yes / No |
| installments[].sequence | Sequence | row order 1, 2, 3 | whole, positive, unique in the term |
| installments[].discount*_ | First / Second / Third Discount | none | percent 0-100, each percent once per installment, one date each (Days / Fixed Date / Day of Month + Months Ahead), filled in order, at most 3 |

Always the create default, not on the sheet (v1): In Use N, Allow Discount on Partial Payments N, no billing cycle,
no flexfields, no extra languages. Update, end-dating and deleting are not supported (Oracle has no hard delete).

## Route status

- **Create: setup task process without a browser** (`setupTaskCSVImports/AR_MANAGE_RECEIVABLES_PAYMENT_TERMS`, Basic
  auth, the call Business Units proved for `FUN_MANAGE_BUSINESS_UNIT`): **UNTESTED on Oracle**. Offline: PASS
  (matrix 2026-10-30). FSCR's live proof (`ZZFSCR N45 4203`, 2026-10-28) went through its Core Data Loader + UCM +
  Run Book, not this route. **If Oracle refuses the call** (HTTP error on the POST), the run stops with "Oracle refused
  the setup task process for Receivables payment terms ... no other way was tried" (code SETUP_NEEDED, or
  NO_PERMISSION on 401/403: plain card, no repair, no question). There is **no browser fallback yet**; adding one is a
  decision for the user.
- **Layout: the task's own empty template** (`setupTaskCSVTemplateExports/<task>/child/SetupTaskCSVTemplateExportProcess`,
  result `SetupTaskCSVTemplateExportProcessResult/{id}`, `enclosure/FileContent`; names from FSCR
  `fsm_csv_export_engine.py:22,71,83`): **UNTESTED on Oracle**. If Oracle refuses it, the layout of the data file
  (`setupTaskCSVExports`, PROVEN for other tasks) is used and the preview says so (the saved ETIA-TEST files show
  both identical).
- **Read-back: a fresh data file, field by field**: offline PASS, including FSCR's real ETIA-TEST before/after files
  (its accepted term reads back "every value as sent", the 10 other terms unchanged).
- **Lists**: reference data sets `setIdSetsLOV` (GET, PROVEN in Price Lists / Payment Terms).
- Page interface (`--spec`, `--options`, `--run`, `--plan`, `--run-batch`): offline PASS 2026-10-30.

Not PROVEN until the live test (prompt 3): `--check`, one `--plan`, one ZZ_TEST_ create through the page, the
read-back, a rerun that skips.

## How to do it

```
python "Receivables Payment Terms/run.py" --check                  # read-only: template, data file, sets, language
python "Receivables Payment Terms/run.py" --plan '<JSON list>'     # read-only: the page's preview check
python "Receivables Payment Terms/run.py" --run-batch '<JSON list>'   # every term of an upload in one go
python "Receivables Payment Terms/run.py"                          # the terms in request.json
```

Order (`run.py` docstring): rules without Oracle (`rpt_rules.py`), then read-only reads (sets + Oracle's today, the
data file "before", the template), then for Create: the names read again from a fresh data file (a term made
meanwhile is skipped, never sent twice), ONE file for every new term built from the template (`rpt_package.py`),
sent once, polled every 10 s (30-minute limit), Oracle's log and reports saved in `_work/`, then a fresh data file
compared field by field. **Never resubmitted** after a timeout or unknown result; the read-back decides.

Results per term: created and checked ("every value as sent") / skipped (already there) / refused with Oracle's
reason ("Nothing was saved in Oracle", INVALID_REQUEST, saved "no", with a structured problem for pause-and-ask when
the reason names a field) / "saved in Oracle, but not as sent: ..." (VERIFY_FAILED, saved "yes") / "may have been
saved" (read-back couldn't finish, saved "maybe").

## File layout (read from the pod on every run)

Only the four entity names are fixed in code (`rpt_package.ENTITIES`): `AR_PAYMENT_TERM` (header, key Name +
SetCode), `AR_PAYMENT_TERM_LINE` (installment, + SequenceNum), `AR_PAYMENT_TERM_TRANSLATION` (name per language),
`AR_PAYMENT_TERM_DISCOUNT` (+ line SequenceNum + DiscountPercent). Everything else comes from the template:
- entity order = the order of `MigrationProcessBusinessObjectCSVMetadataVORow` in `ASM_SETUP_CSV_METADATA.xml`
  (ETIA-TEST: LINE, TERM, TRANSLATION, DISCOUNT - not the hierarchy order; FSCR's fixed order failed on it);
- the file's members in the template's own order; the metadata copied **byte for byte**;
- each CSV's header = its own first line as written (the CSV column order is NOT the metadata attribute order);
  field types from the metadata, matched by name; extra columns only as parent links `<ENTITY>.<Field>`;
- quoting and line ending as the template's header line (ETIA-TEST: every value quoted, `\n`).
Stops (plain, nothing built): wrong task, status not COMPLETED, an entity or member missing, an unknown column, the
template's release differing from the data file's, the template's ProcessEnv not in ORACLE_HOST.
Dates: **YYYY-MM-DD** in the file (Oracle's exports write 2026/10/28 and its loader refuses that, JBO-25009 /
JBO-25027; the Payables folder writes YYYY/MM/DD - different task, different loader). Audit columns always empty.
Saved ETIA-TEST template (headers and metadata only): `manual-notes/pod_layout_etia_test/` (test fixture).

## Receivables sheet test (2026-11-02)

Ran together with the other three Receivables modules from one upload (workbook A in `Transaction Types/manual-notes/receivables_sheet_test/`) through the page's server code on ETIA-TEST: ZZ_TEST_PT_311 (net 30, COMMON) created first, read back "every value as sent"; the type ZZ_TEST_TT_3113 named it and ran after it; rerun skipped, nothing sent. Since then (2026-11-02) its registry group has `"uses_browser": false`: a sheet with only Receivables modules is checked and created without the Oracle browser sign-in. Details: root CLAUDE.md > The upload sheet > Receivables sheet test.

## Page interface

Upload sheet tabs **Receivables Payment Terms** and **Receivables Term Lines** (registry group "Receivables Payment
Terms", area Receivables; root CLAUDE.md > Receivables Payment Terms module). `--plan` is the group's
`oracle_check` (every rule, sets, existing names, language, layout) and its `answer_check`; `--run-batch` is the
`batch_run`. `--spec` fields: name, set_code (pick), installments (rows: sequence, relative_amount, days,
fixed_date, day_of_month, months_ahead, discount{,2,3}_percent/_days/_fixed_date/_day_of_month/_months_ahead),
description, from_date, to_date, base_amount, print_lead_days, tax_freight (pick), discount_basis (pick),
discount_date_basis (pick), cutoff_day, credit_check, prepayment. `--options set_code` = setIdSetsLOV; the three
choice lists are fixed. `--run '<JSON>'` = one term through `--run-batch`'s flow.

Pause-and-ask (`ask_on_refusal`): a refusal whose log names a field (Set Code via LOV_SetCode, Name length, Print
Lead Days, Base Amount, a discount percent, To Date, ... `rpt_package.MESSAGES` / `ATTRS`) becomes a question with
suggestions (sets used by Receivables terms first); an unknown refusal goes to Claude for a proposal; a script
failure goes to the automatic repair; a refused route is a plain card.

Preview wording (examples): "Name is longer than 15 characters (Oracle's limit for Receivables payment terms).
Shorten it." / "A Receivables payment term 'X' already exists in set COMMON. It will be skipped; nothing is changed."
(yellow) / "Oracle has 'x' in set COMMON, which differs only in capitals or spaces. This one will be a new term."
(yellow) / "The installments add up to 90, but Base Amount is 100. They must add up to exactly 100." /
"Installment 2: Day of Month needs Months Ahead (0 = same month)." / "This term has 2 installments, so Print Lead
Days is needed (a whole number above 0)." / "A discount is given, so choose the Discount Basis."

Offline tests: `python page/matrix/test_matrix.py` (generic behaviours with the stub folder, plus 18 cases with this
folder's real code through `page/matrix/stub_receivables.py`). Test workbooks:
`manual-notes/Receivables_Payment_Terms_TEST_good.xlsx` / `..._bad.xlsx` (made by the page's generator).

## Open items (for the live test, prompt 3)

1. **Route proof**: does `setupTaskCSVImports` accept this task with Basic auth? And the template export?
2. **Discount Basis labels**: FSCR contradicts itself on `F` and `T` (`payment_terms_fsm_package.py:80-85` says F =
   "Lines and tax, excluding freight", T = "Lines, freight items, and tax"; `e2e-adapter.json:808,823` says F =
   "Freight", T = "Tax"). Read Oracle's own Discount Basis list on Create Receivables Payment Term once (read-only),
   then add the two labels to `rpt_rules.DISCOUNT_BASIS` and the sheet's drop-down.
3. **How Oracle's log names a failed row** for this task (Business Units' log uses internal keys). Until seen, a log
   block is tied to a term only when it quotes the term's exact name, or when exactly one term was refused; the
   read-back decides which terms were saved.
4. **Name uniqueness**: is `AR_SU_UNIQUE_PAY_TERMS` per set and case-sensitive? The preview warns in yellow.
5. **Which sets can hold a term**: ETIA-TEST terms use only COMMON. Another set gets a yellow note; a refusal at Create
   asks the user (suggestions: sets that hold terms first).
6. The test term `ZZ_TEST_AR_4821` can't be deleted afterwards (no hard delete); it stays as test material.

Observed in the live test, 2026-10-30 (ETIA-TEST, ORACLE_ENV test; one term `ZZRPT 9721` in COMMON created through
the page, Receivables side; facts only):
- (1) Route: Oracle **accepted** the setup task process for this task with Basic auth (`setupTaskCSVImports`,
  process 100004733414498, ESS request 4,422,374, StatusCode COMPLETED, about 22 s). The template call was **accepted**
  too (`setupTaskCSVTemplateExports`, COMPLETED in about 22 s, in `--check` and in the run). Template layout = the data
  file's: release 11.13.26.10.0, ProcessEnv etia-test, entity order LINE, TERM, TRANSLATION, DISCOUNT.
- (3) Log naming: on a fully successful run the ProcessLog names **no term and no row**: only counts ("Business
  object: Receivables Payment Terms ... Detail Object: PaymentTerm ... A total of 1 rows were processed. 0 rows of
  them failed"); Discount and Payment Schedule say "already processed ... listed under the Receivables Payment Terms
  business object". The ProcessResultsReport has a "Message Details" table (Row Key, Type, Message Code, Message),
  empty here. How a FAILED row is named: not observed.
- (4) Name uniqueness (per set, case): not observed (nothing was tested; the 12 terms now in Oracle have no
  capitals-only twins).
- (5) Sets: `setIdSetsLOV` lists 37 reference data sets (one code, `MGREFST `, ends with a space in Oracle's list).
  All 12 Receivables terms on the pod use COMMON only; whether other sets can hold a term: not observed.
- (2) Discount Basis labels: not observed (no discount in this test; no screen opened).
- Read-back: the module's fresh data file matched every value as sent; an independent read-only data file after the
  run showed 12 terms (11 before), `ZZRPT 9721` with 1 header, 2 lines (50/30 days, 50/45 days), 1 US name row, no
  discount, StartDateActive 2026/10/30, and the other 11 terms' rows identical to FSCR's ETIA-TEST data file of
  2026-10-28. Check before Create 73 s, Create 149 s (the folder's own part 139 s). `ZZRPT 9721` stays on the pod
  (no hard delete; it can be end-dated later).

## Sample requests

- "Create a Receivables payment term ZZ_TEST_AR_4821 in COMMON: 60% in 30 days with 2% off within 10 days, 40% in
  60 days, print lead days 1, tax and freight in the first installment, discount on the invoice amount."
- "New receivables term Net 45 AR in COMMON, all due in 45 days."

## Related folders

- `Payment Terms/` (Payables, `AP_MANAGE_PAYMENT_TERMS`): a different Oracle object; no shared code or files.
- `Business Units/`: the setup task process pattern (send, unpack, log reading) was copied from `bu_batch.py`; no
  dependency.

## Known gotchas

- 2026-10-30 (offline, from FSCR's ETIA-TEST evidence): the metadata lists LINE before TERM; a fixed order breaks
  (FSCR `20261028-payment-term-create-blocked.json:11`). Never hardcode the order.
- 2026-10-30: the TERM CSV starts `Name,SetCode` while its metadata attribute list has Name near the end: headers
  come from the CSV's first line only.
- 2026-10-30: FSCR's accepted term had 2 installments and `FirstInstallmentCode` INCLUDE: "Include in the first
  installment" is valid for split terms too (only its default is limited to one installment).

## Discovery steps (live, prompt 3)

`--check` (read-only) -> `--plan` with `ZZ_TEST_AR_4821` (proves the template call) -> Create through the page ->
read-back "every value as sent" -> by hand from the after data file: 1 header, 2 lines, 1 name row, 1 discount for
`ZZ_TEST_AR_4821` / COMMON, every other term unchanged -> the same sheet again: skipped. Record every finding here
and mark the routes PROVEN only after that clean run.

## Material (test records in Oracle)

None yet from this folder. FSCR's `ZZFSCR N45 4203` (COMMON) exists on ETIA-TEST from 2026-10-28.
