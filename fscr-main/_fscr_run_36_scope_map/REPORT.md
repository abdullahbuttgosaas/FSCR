# Run 36: one FSCR scope map for the Module Test Tracker

Paper only: files were read, nothing was signed in to, and nothing outside this folder changed.

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 2026-11-17 15:38 | 2026-11-17 15:51 | 13 | Start was stamped when the folder was created. Reading Runs 07/29/32/34 came first and was not timed. |

**Source and method.** The task list is the official FSCR catalog (`fscr-main/knowledge/setup-task-catalog/effective`, 2,616 tasks), which is the list Run 07 used. Skill and route links come from Run 07's route-audit script, which I re-ran on the repo (`scripts/02_route_audit.py`). Its output was byte-identical to the 2026-11-02 audit, and a/b/c, the CSV flag and the routes match Run 07 `tasks.csv` for all 2,616 tasks (0 mismatches).

Levels are the Run 29/32 levels:
- **a** = has an FSCR skill or guide
- **b** = no skill or guide, catalog CSV flag Y
- **c** = neither
- **Skill but no route** = has a skill that names no FSM_CSV or REST route (43 tasks)

**Rule order** (`scripts/rules.py`, with a reason in every CSV row):
1. Named task overrides (37).
2. Run 29 rule: any ORA_ASK_ area in an ERP offering goes to Common Features.
3. An ORA_ASK_ area that appears only in non-ERP offerings also goes to Common Features.
4. Task-code product family (for example POZ → Sourcing and Supplier Management, RCS/INV → Inventory Management, CST → Cost Management, HZ → Receivables, XLA → General Ledger).
5. Area vote using `area_to_row.csv` (410 areas).

Each task code is counted once.

## Totals
- **2,616 tasks mapped**: 1,842 to tracker rows and **774 Unmapped**. Unmapped tasks are in offerings with no tracker row: 421 CX and other (Service Logistics, Sustainability, EHS), 190 Public Sector, 82 Student Management, and 81 tasks in no offering. The 81 are what is left of the 222 no-offering tasks after family rules placed the others.
- All rows: a 848, b 1,373, c 395, Missing 1,768/2,616. These equal the Run 07 totals.
- Per-row counts and proposed coverage are in `module_counts.csv`:
  - **Full**: Security, Absence, Global Payroll, Workforce Compensation, Recruiting, Learning.
  - **None**: Cash Management 0/19, Revenue Management 0/22, Talent Review and Succession 0/9 (FSCR has only offering router files there), Transportation 0/1, Quality Management 0/5.
  - **Partial**: all other rows.

## Comparison with the filled rows (`work/comparison_detail.csv` lists every task)

| Row | Filled | New | Left | Joined | Why |
|---|---|---|---:|---:|---|
| Common Features | 144 (79 missing) | **227 (148/227)** | 6 | 89 | **Left:** 6 inventory-organization and facility-calendar tasks moved to Inventory Management (Run 34 lesson). **Joined:** 32 Transaction Tax (ZX/JE; Run 29 did not count tax), 24 ORA_ASK_ tasks that appear only in SCM/CX/HCM offerings, 23 generic FND tasks (lookups, value sets, flexfields) that the catalog lists only under HCM/CX "Common" areas, 4 tax-partner tasks, 3 telephony, 2 overrides, 1 ATK. |
| Procurement | 60 (39/60) | **41 (26/41)** | 28 | 9 | **Left:** 9 subledger accounting rules (XLA, to General Ledger), 7 supplier/sourcing approvals (POZ/PON, to S&SM), 3 EXM to Expenses, 3 to Inventory, 2 AP (payment terms, common options) to Payables, 2 CX task configurations to Unmapped, 1 approval groups to Common Features, 1 external-price approvals to Purchasing. **Joined:** 5 B2B messaging (CMK) from the Suppliers area, 2 no-offering PO tasks, 2 others. |
| Sourcing and Supplier Management | 91 (46/91) | **58 (26/58)** | 41 | 8 | **Left:** all 41 were in the "Suppliers" area. They are Inventory 12, Receivables (TCA) 9, Procurement (CMK) 5, Cost 4, Manufacturing 3, Common Features 3, Projects 2, Unmapped 2, Product Hub 1. **Joined:** 8 supplier/sourcing tasks (POZ/PON/EGP) that Run 32 had tagged Procurement or Shared. |

The **29 tasks Run 34 flagged** are the plan.csv rows from other offerings (23 Manufacturing/SCM Materials + 6 Order Management). **All 29 left S&SM** and went to Inventory 12, Receivables 6, Cost 4, Manufacturing 3, Common Features 2 and Projects 2. A further 12 Suppliers-area tasks from the Procurement offering also left S&SM (TCA, CMK, data quality, item organizations).

## What I could not determine
- **Whether a row's core setup is covered.** The catalog does not say which tasks are core. I used a fixed proxy: Full if at least 75% of tasks have a skill or guide, Partial for 1–74%, None for 0. Learning sits exactly on the line (15/20).
- **Borderline choices** in `sensitivity.csv` (41 lines, each with tasks affected and the alternative row). The largest are:
  - Users and Security and Initial Users (52) → Security instead of Common Features
  - Transaction Tax (35) → Payables or Receivables instead of Common Features
  - HZ trading community (59) → Common Features instead of Receivables
  - Financial Reporting Structures (32) → General Ledger instead of Common Features
  - Joint Venture and Federal (49) → Unmapped instead of General Ledger
  - Grants and Project Execution/Resource (58) → Unmapped instead of Project Financial Management
- **No tracker definition file.** The row names come from your message only.
- **REST support** was not scanned for tasks without a skill, and **skill quality** was not tested (same caveats as Runs 29 and 32).
- **Run 34 has no RUN_REPORT.md.** I used `RESULT.md`, `plan.csv` and the scripts.

Files: `module_scope_map.csv`, `module_counts.csv`, `area_to_row.csv`, `sensitivity.csv`, `scripts/` (`build.py`, `rules.py`, `02_route_audit.py`), `work/` (audit output, comparison detail, console logs).
Clean-up: only Python scripts ran, and each one finished. No server, browser or background process was started.
