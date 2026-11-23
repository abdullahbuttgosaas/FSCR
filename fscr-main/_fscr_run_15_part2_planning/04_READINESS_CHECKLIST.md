# Output 4: Readiness Checklist (Project Planning, high-level)

**Project:** Twelve Benefit Corporation: Oracle Cloud SCM Implementation (SOW dated Jan 24, 2025, Doc 50513scm)
**Produced by:** Claude alone, structured on the GoSaaS method (Scoping Checklist, Project Implementation Methodology, PM Check List, Pre-Implementation Checklist: `_fscr_run_10_drive_reference/downloads/01_checklists_capture.txt`). FSCR's `shared/implementation-planning/readiness-checklist-generator` is an empty placeholder (2,994-byte generic manifest, no method) and contributed nothing. A few checks reference FSCR dependency files (Output 3) where noted.
**Status:** Planning only. No check has been performed; every check is **open**. Week numbers refer to the 12-week plan in `02_WAVE_PLAN.xlsx` (W1 = week of Mon 17-Feb-2025, given input).

**Source labels:** **SOW x** = stated in the SOW (verified against `work/sow_text.txt`). **Method** = GoSaaS checklist/methodology capture (verified the item is in the capture). **Rule** = cycle rule given in the run instructions. **FSCR Dn** = dependency in Output 3 from an FSCR file. **Claude** = not verified, suggestion only.
**Owner:** GS = GoSaaS, TW = Twelve, OR = Oracle.

---

## G0. Project start gate (before kickoff, W1)

| # | Check | Owner | Source | Evidence |
|---|---|---|---|---|
| G0.1 | SOW signed by both parties (Twelve 28-Jan-2025, GoSaaS 28-Jan-2025) | GS | SOW signature block (verified) | signed SOW |
| G0.2 | Twelve project lead with decision authority named | TW | SOW E.9 | name in contact list |
| G0.3 | GoSaaS PM and team assigned per SOW roles (10 roles, 3,820 h) | GS | SOW D; Method (PM checklist: offshore leads assign team) | staffing plan |
| G0.4 | High-level project plan and instance plan drafted from the SOW | GS | Method (PM checklist) | this wave plan, reviewed |
| G0.5 | Kickoff deck, client contact list, weekly client and internal meetings, minutes template, budget tracker set up | GS | Method (PM checklist) | meeting series |
| G0.6 | Remote access to development and production platforms granted to GoSaaS; administrator plus backup | TW | SOW E.6, E.7; Method (Pre-implementation checklist) | user accounts work |
| G0.7 | Number of environments confirmed (Dev / Test / Prod recommended); Test pod exists or is ordered | TW / OR | Method (Scoping: 3 recommended); SOW E.6 names only dev and prod | environment list |
| G0.8 | Oracle Support identifier and admin access confirmed; SR opened for the update schedule and cohort | TW / GS | Method (PM checklist, Pre-implementation checklist) | SR number, cohort letter |
| G0.9 | Workshop plan with names and dates (8am–noon PST blocks) | GS / TW | Method (Scoping › Planning) | calendar invites |
| G0.10 | Reference information shared: Coupa configuration values, approval rules, existing ES (ledger, LE, BU names), plant list | TW | SOW E.2, B 3.5; Claude | files received |
| G0.11 | Quarter-end / month-end close and freeze periods known (live Financials) | TW | Method (Pre-sales: quarter-end freeze) | close calendar |
| G0.12 | Start date: 17-Feb-2025 is Presidents' Day; kickoff date agreed | GS / TW | Claude (calendar verified) | kickoff invite |

## G1. Design sign-off / build start gate (end W3)

| # | Check | Owner | Source | Evidence |
|---|---|---|---|---|
| G1.1 | Per-module Business Scenarios, Requirements, Process Flows, Key Design Decisions and Configuration Templates documented and approved (11 modules + Security) | GS / TW | SOW B; Method step 5 | signed design docs |
| G1.2 | Enterprise structure decisions: BU option (A or B), item master org, 2 plant inventory orgs, cost org and cost books | TW | Output 2 Q-E1…Q-E8; FSCR D1–D7 | KDD log |
| G1.3 | Approval (Delegation of Authority) hierarchy basis decided | TW | SOW B 3.3, 4.2; Claude | KDD |
| G1.4 | Expenses in/out decision recorded after the design session | TW | SOW Fin 5.1 | decision record |
| G1.5 | Financials remediation scope listed (GL, AP, PPM, FA; AR, CE, Grants TBD) | GS / TW | SOW Fin intro, "determined during the project" | scope addendum |
| G1.6 | New COA natural accounts identified (inventory, WIP, variance, receipt accrual) | TW | Claude (Output 3 D27) | COA change list |
| G1.7 | Supplier conversion source and volume decided; FDD approved | TW / GS | SOW RICE 2; Run 14 Q-D1, Q-D2 | FDD sign-off |
| G1.8 | Printable PO report FDD approved | TW | SOW RICE 1 | FDD sign-off |
| G1.9 | Reporting approach workshop scheduled (OTBI/BIP/FDI/EPM) | GS | SOW Fin 6 | agenda |

## G2. CRP1 entry gate (start W4) — partial data, no security, no customizations

| # | Check | Owner | Source | Evidence |
|---|---|---|---|---|
| G2.1 | CRP1 configuration built in Dev per approved design (offerings opted in, catalog task order followed) | GS | Method step 7; FSCR D13, D17 | config workbook / task map status |
| G2.2 | Partial supplier data loaded and validated (checklist: "Partial should be 50% target") | GS / TW | Rule; Method (Pre-sales) | load log |
| G2.3 | Minimum items, plant inventory orgs, cost org, work areas/centers needed for scripts created | GS | FSCR D1, D2, D8, D9 | setup list |
| G2.4 | CRP scripts written for each module and approved; CRP attendees and users named | GS / TW | Method step 7 | script list |
| G2.5 | Defect tracker ready | GS | Method step 8 | tracker link |
| G2.6 | Security and customizations explicitly out of CRP1 (testers use implementation roles) | GS | Rule | CRP1 charter |
| G2.7 | No Oracle non-prod update during CRP1 weeks, or plan adjusted (cohort B: update Fri 07-Mar, smoke test before CRP1) | GS | Template cohort key; wave plan 'Update conflicts' | smoke-test result |
| G2.8 | System tested by GoSaaS before handover (smoke test) | GS | Method step 7 "test system" | smoke-test log |

## G3. CRP1 exit / CRP2 entry gate (end W6 / start W7) — full data, full security, customizations

| # | Check | Owner | Source | Evidence |
|---|---|---|---|---|
| G3.1 | CRP1 scripts executed by Twelve; sign-off received | TW | Method step 8 | sign-off |
| G3.2 | CRP1 defects reviewed; design (Best Start / config templates) updated | GS | Method step 8 | defect log, doc versions |
| G3.3 | Fix config done (checklist 2–4 weeks; plan allows 1 — risk accepted) | GS | Method (between cycles); wave plan WP-6 | change log |
| G3.4 | Test environment available; P2T refresh done if chosen; configuration migrated to Test | GS / TW / OR | Method (configure new env 1 wk); Claude (refresh) | env check |
| G3.5 | Full supplier data loaded, validated and smoke tested | GS / TW | Rule; Method (load 2, validate 1, smoke 1) | reconciliation report |
| G3.6 | Security roles and data access built (Security and Roles, Cfg 12); test users provisioned with target roles | GS / TW | Rule; SOW Cfg 12; FSCR D10 | role matrix |
| G3.7 | Printable PO report deployed (code + unit test) | GS | Rule; SOW RICE 1.3.2 | unit-test evidence |
| G3.8 | Expenses configured if in scope | GS | SOW Fin 5 | config doc |
| G3.9 | Receipt/cost accounting and SLA rules configured; new accounts exist in live COA | GS / TW | FSCR D3, D14; Claude D27 | accounting test |
| G3.10 | CRP2 scripts cover end-to-end: requisition → PO (project/non-project) → receipt → putaway → AP invoice → accounting; process work order; maintenance work order and program; supplier portal; sustainability | GS / TW | SOW B 2–7, Fin 1–7 | script list |
| G3.11 | Oracle update check for CRP2 weeks (cohort C: non-prod Fri 04-Apr in CRP2 week 1) | GS | Template cohort key | plan adjustment |

## G4. CRP2 exit / UAT entry gate (end W9 / start W10) — full data plus delta

| # | Check | Owner | Source | Evidence |
|---|---|---|---|---|
| G4.1 | CRP2 sign-off; defects closed or accepted | TW | Method step 8 | sign-off |
| G4.2 | Configuration documents (all 12 Configurations Scope items) updated | GS | SOW Configurations Scope | doc versions |
| G4.3 | Delta supplier load done and validated | GS / TW | Rule | reconciliation |
| G4.4 | UAT scripts and UAT users (business testers, real roles) ready | TW / GS | Method step 9 | script list |
| G4.5 | Data validation reports / OTBI reports for UAT available | GS | Method step 9 | report list |
| G4.6 | Cutover plan drafted for rehearsal in UAT | GS / TW | Method (UAT = go-live rehearsal, cutover plan) | cutover plan |
| G4.7 | Train-the-Trainer material ready; trainers trained during UAT | GS / TW | SOW Change Mgmt, C.6 | training sessions |
| G4.8 | Twelve has started migrating approved configuration to Production | TW | SOW C.10 | migration log |
| G4.9 | Oracle update check for UAT weeks (cohort A: non-prod Fri 02-May = UAT last day) | GS | Template cohort key | plan adjustment |

## G5. Go-live go/no-go gate (end W11, before cutover W12)

| # | Check | Owner | Source | Evidence |
|---|---|---|---|---|
| G5.1 | UAT sign-off by Twelve | TW | Method step 10 | sign-off |
| G5.2 | Go-Live and "Ready to Use" criteria (refined during the project) met | TW / GS | SOW C.2.1 | criteria checklist |
| G5.3 | Production configuration complete and reviewed against signed configuration documents | TW / GS | SOW C.10; Method step 11 | comparison report |
| G5.4 | Full supplier load to Production and delta plan ready; freeze period or delta approach agreed | GS / TW | Method step 11; Rule | load plan |
| G5.5 | Security: Production user accounts and roles provisioned; required employees in Production | TW | SOW C.5.1; Method step 11 | user list |
| G5.6 | Printable PO report deployed to Production | GS / TW | SOW RICE 1 | deployment log |
| G5.7 | Cutover window avoids month-end close in live Financials (April close falls in W12) | TW | Claude (WP-10) | close calendar |
| G5.8 | No Oracle Prod update in the go-live week; Test/Prod release levels known (cohort A: Prod 25B on 16-May, week after go-live) | GS / OR | Template cohort key | SR confirmation |
| G5.9 | Coupa transition decided (run in parallel or retire) | TW | Run 14 Q-S6, Q-I1 | decision |
| G5.10 | End-user training delivered by Twelve trainers | TW | SOW C.4, C.6 | attendance |
| G5.11 | Hypercare / support model agreed (not in SOW) | GS / TW | Method (Post Go-Live); Run 14 Q-P8 | support plan |

## G6. Go-live complete / hypercare exit (W12 → W14, SUGGESTED)

| # | Check | Owner | Source | Evidence |
|---|---|---|---|---|
| G6.1 | Twelve declares live; immediate fixes done | TW / GS | Method step 12 | go-live note |
| G6.2 | First requisition, PO, receipt, AP invoice and accounting run in Production | TW | Claude | transaction list |
| G6.3 | First process and maintenance work orders created, released, completed | TW | SOW B 6.1, 7.1 | transaction list |
| G6.4 | First month-end close with the new subledgers (Receipt/Cost Accounting) passed | TW | SOW Fin 7; Claude | close checklist |
| G6.5 | Oracle Prod update after go-live regression-tested (cohort A: 16-May) | GS / TW | Template cohort key | regression log |
| G6.6 | Lessons learnt; next phases (future locations, MES) noted | GS | Method step 14; SOW C.3, B 6.4 | lessons-learnt doc |

## Counts
- Gates: **7** (G0–G6). Checks: **66** (G0 12, G1 9, G2 8, G3 11, G4 9, G5 11, G6 6). Verified by grep count.
- Checks citing the SOW: **28**. Checks whose only source is Claude: **3** (G0.12, G5.7, G6.2). Verified by grep on the Source column. The rest cite the GoSaaS method, the cycle rules, the cohort key, FSCR dependencies or Run 14 open questions.
- Status of all checks: **open** (nothing has been executed).
