# Price Lists: fields for an upload sheet

Every field of Oracle's **Create Price List** screen (Order Management > Pricing Administration >
Manage Price Lists > +) as the Price Lists folder takes it (scope A, 2026-10-26). "Key" is the request
key (`pricelists.json`, `--run`, `--plan`, `--run-batch`). "Proven" = created by a real run, read back
through REST and, for the dates, on the screen (price lists ZZ_TEST_PL_8034_*, see CLAUDE.md > Scope A).
Check a request read-only with `python "Price Lists/run.py" --plan '<JSON>'`.

Not in scope (never built): items, charges, tiers, matrices, rate plans, component / covered items,
flexfields, Returns price lists.

In the upload sheet (2026-10-26) these are two tabs: **Price Lists** (one row per price list, the
columns below) and **Price List Access Sets** (Price List Name *, Set Code *), joined by Price List
Name written exactly. A Business Unit that is a Name on the sheet's Business Units tab is sent with
`business_unit_pending: true`: business units are created first and the price list waits for it (root
CLAUDE.md > Price Lists module). The preview runs `--plan` for all rows in one call; Create runs
`--run-batch` once; a value Oracle refuses makes the page ask the user.

## Price list header

| Screen label | Key | Required | Allowed values | If empty | Rules and Oracle's messages | Status |
|---|---|---|---|---|---|---|
| Name | `name` | yes | text, 1-80 characters; no single quote ('); no space at the start or end | - | Unique in **all of Oracle**, not per business unit: "A price list with the name X already exists. (QP-2715100)" (same and other business unit). Capitals count: a capitals-only twin is accepted by Oracle (the plan notes it). 81 characters: "Value ... for field PriceListName exceeds the maximum length allowed." An existing name is skipped and never changed (a half-made one with the same header is completed). | proven: 80 accepted, 81 refused, duplicates refused, capitals twin accepted |
| Item Description | `description` | no | text, up to 1000; no single quote | none | 1001: "Value ... for field PriceListDescription exceeds the maximum length allowed." | proven: 1000 accepted, 1001 refused |
| Type | `type` | no | Segment price list, Floor price list, GSA price list, Ceiling price list (code or name; "Floor" works) | Segment price list | Unknown value: "'X' is not a Type Oracle offers here." + the four | proven: all four |
| Currency | `currency` | yes | Oracle's enabled currencies (268 by REST, 267 on the screen), code or name | - | Unknown: "'X' is not one of Oracle's 268 enabled currencies." + close codes | proven: USD, PKR, AFN, EUR |
| Business Unit | `business_unit` | yes | a business unit where the user (Configuration.TEST) has active **Pricing Administrator** data access - the screen's list (43 on 2026-10-26) - and that is active | - | Not in the list: "Configuration.TEST has no Pricing Administrator access on the business unit 'X', so Oracle doesn't offer it for price lists." / "Oracle has no business unit 'X' that can be used for price lists." + closest names in the list. Inactive: "The business unit 'X' is inactive, so no price list is made for it." | proven: ABD, US1, ABC Procurement BU, ZZ_TEST_BU_8034_PL |
| (pending business unit) | `business_unit_pending` | no | true / false | false | true = made earlier in the same upload: the price list waits (list read every 15 s, up to 5 min); not there -> "Oracle doesn't show the business unit X for pricing yet (waited ...), so the price list wasn't made." Never created on a guess. | proven offline (made-up name, 30 s); a real new business unit was in the list at once |
| Start Date | `start_date` | yes | YYYY-MM-DD, or "today" (today in the user's time zone) | - | Sent as 12:00 AM of that date in the Oracle user's time zone ((UTC-05:00) New York - Eastern Time, daylight saving included), so the screen shows that date at 12:00 AM | proven on the screen (10/26/26, 10/27/26, 10/28/26, 11/2/26) |
| End Date | `end_date` | no | YYYY-MM-DD, on or after Start Date | none | Before Start Date: "You must enter a start date that's on or before the end date." (Oracle; the folder refuses it first) | proven: 12/31/27, 3/15/27, 12/31/26; the refusal proven |

## Price list line default values

| Screen label | Key | Required | Allowed values | If empty | Status |
|---|---|---|---|---|---|
| Pricing Charge Definition | `charge_definition` | no | Sale Price, Recurring Sale Price (code or name; chargeDefinitionsLOV) | none | proven: both |
| Line Type | `line_type` | no | Buy | Buy | proven |
| Calculation Method | `calculation_method` | no | Price, Cost, Covered item price percent, Source document cost (code or name) | Price | proven: all four |

## Access sets and approval

| What | Key | Required | Rules and Oracle's messages | Status |
|---|---|---|---|---|
| Access sets | `access_sets` | yes, one or more | Oracle's 37 reference data sets, code or name; each once. Without one Oracle refuses the approval: "StatusCode: You cannot approve this price list because it is not associated with an access set. (QP-2715317)" | proven: one and two sets; 001 CUSTOMER SITE, ENTERPRISE, COMMON, SET0001 |
| Approval | - | always | PATCH StatusCode APPROVED after the access sets; works at once on this pod (no approval flow) | proven |

## Before Create and at Create

- **No Oracle needed:** name and description length, quote, outer spaces, listed twice, dates and
  their order, at least one access set, a set listed twice.
- **Read-only (`--plan`, REST; the screen once a week for the time zone):** the name exists (and its
  state: approved / half-made / other values), a capitals-only twin, currency, the business unit in
  the user's pricing access list and active, type / line type / method / charge definition, access
  sets, what Oracle will get with the dates as the screen will show them.
- **Only at Create:** anything else Oracle refuses, given per price list in Oracle's words with
  suggested values; one price list's refusal never stops the others (proven: the bad one of three).

## Not proven

A real wait for a pending business unit that appears late (the new one was available at once);
Oracle refusing a combination of type, method and charge definition (none refused in the five tried;
not every combination tried); a price list on a business unit whose name has a quote; names with
characters other than letters, digits, spaces, _ and -; another user's time zone; Oracle's own message
for a business unit without access (the folder never sends one); the approval flow with Oracle's
approval opt-in on (off on this pod).

## Checked again 2026-10-26

Currency: only codes of 3 characters (`priceLists/describe` CurrencyCode precision 3); the enabled currency
1214 was refused at Create on 2026-10-21 ("Value 1214 for field CurrencyCode exceeds the maximum length
allowed.") and is now red in the preview with three-letter suggestions. Oracle's "The value of the attribute
BusinessUnit isn't valid." is the business unit outside the user's pricing access (checked).
