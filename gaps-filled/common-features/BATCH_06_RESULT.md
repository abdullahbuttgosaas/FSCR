# Batch 06 result: Common Features (AB), daily rates and 4 shared-setting tasks

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (same sitting as batch 05). Tested on ETIA-TEST only (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file was edited. Work folder `E:\GoSaaS\gw\cf5\b06` (outside the repo). Record names `GAPFILL_AB_B6_<name>`.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 02:39 | 02:44 | 5 | Daily rates: export, try 1 (rules dropped), diagnosis, try 2, compare PASS |
| 02:44 | 02:45 | 1 | REST reads of the 3 seeded profile options (read only) |
| 02:44 | 02:47 | 3 | Daily rates skill; fresh test (02:45 to 02:47) |
| 02:45 | 02:48 | 3 | 4 "unsafe to test" skills written from the exports, REST reads and docs |
| 02:48 | 02:52 | 4 | Cards, changelogs, evidence, tracker, index, reports |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records / ProcessIds |
|---|---|---|---:|---:|---|---|
| 1 | Manage Daily Rates (`GL_MANAGE_DAILY_RATES`) | tested (try 2) | 7 + 2 | 3 | PASS | `GAPFILL_AB_B6_DRT1` (100004743401986: type created, rules dropped); `GAPFILL_AB_B6_DRT2` + rules EUR, GBP (100004742421461); `GAPFILL_AB_B6_DRT3F` + rules CAD, EUR (100004743401997) |
| 2 | Manage Search Profile Options (`ZCA_MANAGE_SEARCH_PROFILE_OPTIONS`) | written (unsafe to test) | 4 + 0 | 1 | not run | none |
| 3 | Manage Common CRM Business Unit Profile Options (`ORA_ZCA_MANAGE_COMMON_CRM_BUSINESS_UNIT_PROFILE_OPTIONS`) | written (unsafe to test) | 3 + 0 | 1 | not run | none |
| 4 | Map Reports to Work Areas (`ATK_DEFINE_REPORT_MAPPING`) | written (unsafe to test) | 4 + 0 | 1 | not run | none |
| 5 | Manage Country Default Controls (`ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS`) | written (unsafe to test) | 4 + 0 | 1 | not run | none |
| | **Total** | **1 tested, 4 written** | **24** | **7** | 1 of 1 | |

## Why 4 tasks are "written", not tested (decision by the prompt's rule: shared settings are not loaded)
- **Search profile options:** the export scope is 2 named **seeded** options in `edit` mode. Any load changes the SITE value every user gets.
- **CRM BU profile options:** the scope is the seeded `HZ_ENABLE_MULTIPLE_BU_CRM`; a load switches multiple-BU behaviour for all CRM users.
- **Map reports to work areas:** a mapping shows the report in that work area to every user.
- **Country default controls:** one row per country; a row changes tax defaulting for every transaction in that country, and there is no test country.
Each SKILL.md is written in full: the read steps (REST and export) are VERIFIED live; the build/import/read-back steps are labelled GUESS. Evidence 01 to 03 only. They do not count as filled.

## Problems and findings
1. **Daily rates: the CSV package holds no rate values.** It carries rate types and cross-rate rules. The import log itself says `Conversion Rate: Data Load Pending. You must load the data for this business object` (rates are an external load: spreadsheet or file-based import, not tested). The skill says so in its first lines.
2. **Rule rows with `EnabledFlag=Y` are dropped without an error.** Try 1: "Completed successfully", the type was created, 0 rules (export compare FAIL on the rule file). All 10 working rule rows have `EnabledFlag=N`; try 2 changed only that: 2 rules added, compare PASS. The fresh tester's rules (CAD, EUR) also came in. The log counts only the type, so the export compare is the only proof.
3. **`ZCA_SEARCH_HIDE_SENSITIVE_ATTR` is in the task scope but not in `profileOptions`** (0 rows) in this release.
4. **REST:** `profileOptions` rejects unknown `fields` (HTTP 400); `conversionRateTypesLOV` 404; `currencyRates` with a rate type filter 400. Reads without `--fields` print seeded user names (`SEED_DATA_FROM_APPLICATION`): skills always pass `--fields`.
5. **Records left by try 1:** `GAPFILL_AB_B6_DRT1` (a rate type with cross rates on, no rules). Nothing uses it.

## What is left
Sitting limit reached (10 tasks: 6 tested, 4 written). 96 Common Features gaps open, 49 of them "neither" (check CSV and REST before calling screen-only). Next candidates (from `my_gaps.csv`): Intercompany Exceptions (LE package; likely unsafe), Cross-Validation Rules (no rule file in the export: check FBDI/REST), tree structures and labels, document sequence assignments (unsafe), descriptive flexfields (deploy), the "neither" checks.
