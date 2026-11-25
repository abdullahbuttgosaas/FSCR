# Gap level count (19 owned modules)

Made 2026-11-25 from files only (no sign-in, no Oracle, no network). Read-only count; no other file was changed.

| Module | Total missing | Route only | Neither | Already tested | Known screen-only | Route-only with a named CSV route (catalog CSV flag Y) | Route-only with a specific object or route named in our files |
|---|---:|---:|---:|---:|---:|---:|---:|
| Common Features | 148 | 99 | 49 | 42 | 0 | 99 | 42 |
| Security | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| General Ledger | 155 | 117 | 38 | 1 | 0 | 117 | 1 |
| Payables | 40 | 33 | 7 | 0 | 0 | 33 | 0 |
| Receivables | 74 | 66 | 8 | 1 | 0 | 66 | 0 |
| Cash Management | 19 | 17 | 2 | 0 | 0 | 17 | 0 |
| Fixed Assets | 18 | 18 | 0 | 0 | 0 | 18 | 0 |
| Expenses | 33 | 28 | 5 | 0 | 0 | 28 | 0 |
| Revenue Management | 22 | 21 | 1 | 0 | 0 | 21 | 0 |
| Project Financial Management | 199 | 171 | 28 | 0 | 0 | 171 | 0 |
| Purchasing | 11 | 9 | 2 | 0 | 0 | 9 | 0 |
| Procurement | 26 | 18 | 8 | 0 | 0 | 18 | 0 |
| Sourcing and Supplier Management | 26 | 16 | 10 | 0 | 0 | 16 | 0 |
| Inventory Management | 73 | 68 | 5 | 0 | 0 | 68 | 0 |
| Order Management | 35 | 26 | 9 | 0 | 0 | 26 | 0 |
| Manufacturing | 5 | 3 | 2 | 0 | 0 | 3 | 0 |
| Cost Management | 30 | 27 | 3 | 0 | 0 | 27 | 0 |
| Supply Planning | 6 | 2 | 4 | 0 | 0 | 2 | 0 |
| Maintenance | 15 | 10 | 5 | 0 | 0 | 10 | 0 |
| **Total** | 935 | 749 | 186 | 44 | 0 | 749 | 43 |

1. How: levels come from the `level` column of `gap_index.csv` (route only = b, neither = c) and were cross-checked against `fscr-main\_fscr_run_36_scope_map\module_scope_map.csv` and the FSCR catalog `setupTasksAll.json` (0 differences). "Already tested" = `STATUS.md` cards under `gaps-filled\` with `status: tested` (44 cards, all in the index; 43 are route only and 1 is neither: Receivables alternate name mapping rules, filled by REST).
2. No coverage file needed: `gap_index.csv` holds the level for all 935 rows. Security is one of the 19 modules but has 0 gap rows (it has no missing tasks in the index), so its row is all zeros.
3. Named route: the FSCR catalog (`setupTasksAll.json`) only gives a CSV export/import flag; it names no business object and no REST resource for any of the 935 tasks. So all 749 route-only tasks have a CSV route by the catalog (that is what "route only" means), and only 43 name a specific object or route in our own files (`STATUS.md` `route:` key, `batch1_export_check.csv`, or an `EXPORT` note in the index). No export or REST call was made to check this.
4. Known screen-only is 0 everywhere: there is no `screen-only.csv` under `gaps-filled\` yet, and the index `screen_only` column is "unknown" for every open gap ("no" for the 44 tested).
5. What the table cannot tell: which tasks are screen-only (even with a CSV flag) or unsafe to test on the shared pod is only known after a live export and test; "neither" is likely screen-only but not proven.

Self-check: per-module totals add up to 935 (expected 935); route only + neither = total missing in every module: yes.
