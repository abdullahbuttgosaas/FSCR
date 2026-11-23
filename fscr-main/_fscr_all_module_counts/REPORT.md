# All-module counts for the FSCR Module Test Tracker (working numbers)

Paper only. No Oracle calls, no sign-in, no server. Only new files in this folder.

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 2026-11-19 14:37 | 2026-11-19 14:37 | see note | Start stamped when the folder was made, after reading the Run 36 files. Minutes not computed to the second. |

**Source:** Run 36 `module_scope_map.csv` (2,616 tasks, one row each). I re-counted every row from that file and compared with Run 36 `module_counts.csv`: **0 differences** (totals, a, b, c, skill-but-no-route, label).

## Table (tracker order)
Missing = b + c. Labels are **proposed**; testers set the final value. Rule: 0 skills = None, 1-74% = Partial, 75% or more = Full.

| Pillar | Module | Total | a | b | c | Skill, no route | Missing | Coverage | Proposed label |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| ERP | Common Features | 227 | 79 | 99 | 49 | 10 | **148** | 34.8% | Partial |
| ERP | Security | 6 | 6 | 0 | 0 | 0 | **0** | 100.0% | Full |
| ERP | General Ledger | 158 | 3 | 117 | 38 | 0 | **155** | 1.9% | Partial |
| ERP | Payables | 46 | 6 | 33 | 7 | 0 | **40** | 13.0% | Partial |
| ERP | Receivables | 142 | 68 | 66 | 8 | 3 | **74** | 47.9% | Partial |
| ERP | Cash Management | 19 | 0 | 17 | 2 | 0 | **19** | 0.0% | None |
| ERP | Fixed Assets | 28 | 10 | 18 | 0 | 0 | **18** | 35.7% | Partial |
| ERP | Expenses | 39 | 6 | 28 | 5 | 0 | **33** | 15.4% | Partial |
| ERP | Revenue Management | 22 | 0 | 21 | 1 | 0 | **22** | 0.0% | None |
| ERP | Project Financial Management | 214 | 15 | 171 | 28 | 1 | **199** | 7.0% | Partial |
| ERP | Purchasing | 14 | 3 | 9 | 2 | 0 | **11** | 21.4% | Partial |
| HCM | Global HR | 167 | 82 | 50 | 35 | 2 | **85** | 49.1% | Partial |
| HCM | Absence Management | 10 | 8 | 2 | 0 | 0 | **2** | 80.0% | Full |
| HCM | Time and Labor | 37 | 27 | 7 | 3 | 0 | **10** | 73.0% | Partial |
| HCM | Global Payroll | 47 | 42 | 5 | 0 | 3 | **5** | 89.4% | Full |
| HCM | Benefits | 36 | 16 | 6 | 14 | 2 | **20** | 44.4% | Partial |
| HCM | Workforce Compensation | 17 | 17 | 0 | 0 | 0 | **0** | 100.0% | Full |
| HCM | Performance and Goal Management | 23 | 14 | 8 | 1 | 0 | **9** | 60.9% | Partial |
| HCM | Talent Review and Succession | 9 | 0 | 9 | 0 | 0 | **9** | 0.0% | None |
| HCM | Recruiting | 50 | 41 | 5 | 4 | 1 | **9** | 82.0% | Full |
| HCM | Learning | 20 | 15 | 0 | 5 | 0 | **5** | 75.0% | Full |
| SCM | Procurement | 41 | 15 | 18 | 8 | 0 | **26** | 36.6% | Partial |
| SCM | Sourcing and Supplier Management | 58 | 32 | 16 | 10 | 9 | **26** | 55.2% | Partial |
| SCM | Inventory Management | 134 | 61 | 68 | 5 | 0 | **73** | 45.5% | Partial |
| SCM | Order Management | 68 | 33 | 26 | 9 | 1 | **35** | 48.5% | Partial |
| SCM | Manufacturing | 18 | 13 | 3 | 2 | 0 | **5** | 72.2% | Partial |
| SCM | Cost Management | 62 | 32 | 27 | 3 | 1 | **30** | 51.6% | Partial |
| SCM | Supply Planning | 17 | 11 | 2 | 4 | 3 | **6** | 64.7% | Partial |
| SCM | Maintenance | 19 | 4 | 10 | 5 | 0 | **15** | 21.1% | Partial |
| SCM | Logistics - Transportation Management | 1 | 0 | 1 | 0 | 0 | **1** | 0.0% | None |
| SCM | Logistics - Global Trade Management | 7 | 1 | 6 | 0 | 0 | **6** | 14.3% | Partial |
| SCM | PLM - Product Hub | 44 | 29 | 10 | 5 | 0 | **15** | 65.9% | Partial |
| SCM | PLM - Product Development | 37 | 15 | 19 | 3 | 0 | **22** | 40.5% | Partial |
| SCM | PLM - Quality Management | 5 | 0 | 5 | 0 | 0 | **5** | 0.0% | None |
| | **All 34 tracker rows** | **1842** | 704 | 882 | 256 | 36 | **1138** | 38.2% | |

## Checks
**(a) Filled rows.** All five match.
- Common Features 227 / 148: same.
- Procurement 41 / 26: same.
- Sourcing and Supplier Management 58 / 26: same.
- Purchasing 14 / 11: same.
- Supply Planning 17 / 6: same.

**(b) Sum vs catalog.** The 34 rows add up to **1842**. The catalog has 2,616. **774 tasks belong to no row**: they are in offerings the tracker does not have (421 CX/Service Logistics/Sustainability/EHS, 190 Public Sector, 82 Student Management) or in no offering (81, family rules could not place them). Run 36 calls this group Unmapped; it is not a tracker row. Check: 1842 + 774 = 2,616.

**(c) No double counting.** 2,616 task codes, 2,616 unique, no duplicates. Each task has one row.

**(d) Small rows.**
- Logistics - Transportation Management: **1 task** (Missing 1). Almost nothing in the catalog; the row may be too small to test on its own.
- Security: 6 tasks (all covered). Most security tasks (52 in Users and Security / Initial Users) were kept in Common Features.
- Quality Management 5, Talent Review and Succession 9, Absence Management 10, Purchasing 14: small, so one task changes the percent a lot.
- No row has zero tasks.
- Rows with None (0 skills): Cash Management 19, Revenue Management 22, Talent Review and Succession 9, Transportation 1, Quality Management 5. Here Missing equals Total.

## Assumptions
- Run 36 is the authority. Rows with no skill have Missing = Total only when every task lacks a skill (the None rows).
- The 43 skill-but-no-route tasks sit inside a, so they are not in Missing.
- Tasks with no CSV or API in Oracle stay in Missing (c).
- Percent = a / Total, rounded to one decimal; labels use the exact value.

## For you to decide
1. **Borderline labels:** Time and Labor 73.0% and Manufacturing 72.2% are Partial but close to 75%; Learning is exactly 75.0%, so Full. Moving the line changes them.
2. **Border choices** in Run 36 `sensitivity.csv` (for example Users and Security 52 tasks to Security instead of Common Features; HZ 59 tasks; Transaction Tax 35) change several totals. I kept Run 36's choices.
3. **Row count:** the list you gave has 34 rows (11 ERP + 10 HCM + 13 SCM). Run 36 said "35 modules" (34 rows + Unmapped). No tracker definition file exists, so please confirm no row is missing.
4. Numbers are working numbers: REST support for tasks without a skill was not scanned and skill quality was not tested.

Files: `module_totals.csv`, `paste_total_missing.tsv` (two columns, 34 lines, no header).
Clean-up: only a short Python script ran and finished. No server or background process was started.
