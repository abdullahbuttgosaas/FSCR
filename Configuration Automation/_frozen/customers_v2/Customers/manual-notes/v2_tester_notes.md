# Customers: what changed for testers (v1 -> v2, 2026-10-26)

| Situation | v1 (before) | v2 (now) |
|---|---|---|
| City that starts other city names (ABSECON, Dallas, Seattle) | Preview OK, then refused at Create: "does not exist in Oracle's geography ... Nothing was saved." | Found in the preview ("Found in Oracle: DALLAS, TX (DALLAS county)") and created. |
| Misspelt city / postal code of another state / unknown state | Sometimes only at Create | Red in the preview, with suggestions (e.g. "Dalas" -> DALLAS). |
| City in several counties, no postal code | First row Oracle offered | The county named like the city (else the first); the preview says which. |
| Oracle's places lookup fails during the preview | The whole preview stopped: "upload the sheet again" | Tried 3 times, then once more; still failing = that customer is **held** (yellow note), the rest is checked; Create checks it again. |
| Site Language not in Oracle's list / any Customer Category Code | Refused at Create | Red in the preview. |
| Oracle refuses a value at Create (place or list) | Failed card, re-upload | The run pauses: "Needs your decision" panel with suggestions, another value or Skip; only that customer runs again. |
| Oracle shows a message after Save and Close | Card said "Nothing was saved" even if the customer was saved | Oracle is searched first: saved -> the run verifies it and says so; not saved -> "Oracle did not save X ... (checked in Oracle: no new customer named X)". |
| A stop after Save was pressed | "Nothing was saved" | "may have been saved (Registry ID N if it was)"; a rerun never makes it twice. |

Everything else (columns, purposes, Bill-to Site, same-name customers, the run summary,
the failed-only sheet) is unchanged; the regression check compares the v1 and v2 preview
of the working sheet field by field.

How to see each change (test switches, only on a test page started by Claude):
`CUSTOMERS_TEST_REFUSE_CITY=<city>` (a forced refusal at Create),
`CUSTOMERS_TEST_FAIL_AFTER_SAVE=1` (a stop right after Save),
`CUSTOMERS_TEST_GEO_FAILS=<n>` (the places lookup fails n times in the preview).
Test sheets: `CU_TEST_10.xlsx` (5 valid, 5 wrong), `CU_TEST_valid5.xlsx`, `CU_TEST_ask.xlsx` in this folder.
