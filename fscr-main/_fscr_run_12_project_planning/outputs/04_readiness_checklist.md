# Output 4: Readiness Checklist (Twelve, SOW 50513scm)

**Who produced it: Claude alone, using FSCR headings.** `shared.implementation-planning.readiness-checklist-generator` is a generic stub. Its SKILL.md has inputs and outputs (recommendations, work products, review points) but no checklist, no gates and no template. Claude built the gates from the SOW, the intake outputs and our practice cycle rules (CRP1 / CRP2 / UAT / go-live).

Legend: **Source**: SOW section, Intake (run 11b outputs), Practice (rules in the run prompt), FSCR (file), Claude. **Status**: V = the item is stated in the cited source. NV = Claude's recommendation. Every item is open; nothing has been checked against Twelve.

## Gate 0: Project start / design

| # | Check | Owner | Source | Status |
|---|---|---|---|---|
| R0.1 | Signed SOW received (work starts on receipt) | GoSaaS PMO | SOW preamble | V |
| R0.2 | Twelve project lead named, with decision authority | Twelve | SOW E.9 | V |
| R0.3 | Start date, go-live date and phase dates agreed | Both | Intake S1, wave plan W1 | V (gap) |
| R0.4 | Environment list confirmed (DEV, PROD, any TEST pod) and access given to GoSaaS | Twelve | SOW E.6, E.7; wave plan W2 | V |
| R0.5 | Oracle quarterly update dates for each pod obtained | Twelve / Oracle | Wave plan W3; not in FSCR | NV |
| R0.6 | Expenses in/out decision session scheduled | Both | SOW Fin 5.1 | V |
| R0.7 | Enterprise structure confirmation workshop (LE, ledger, BU, 2 plants, item master) | Both | Intake output 2 (E1–E7) | NV |
| R0.8 | Coupa configuration values and concepts extracted for reuse | Twelve | SOW 3.5 | V |
| R0.9 | Offerings opted in (Manufacturing and Supply Chain Materials Management, Procurement, Product Management) | GoSaaS | Output 1; FSCR purchasing-line-types dependency seq 1 | V (FSCR rule) |
| R0.10 | Implementation user with an Application Implementation Consultant-based role | Twelve IT | FSCR `manage-purchasing-line-types/ora_dependency_readiness.md` seq 2 | V |

## Gate 1: Ready for CRP1 (2 weeks, partial data, no security, no customizations)

| # | Check | Owner | Source | Status |
|---|---|---|---|---|
| R1.1 | Key design decisions signed off for all new modules | Twelve | SOW B (KDDs), E.1 | V |
| R1.2 | Base configuration in DEV: locations, inventory orgs (2 plants), item master, cost org, cost books | GoSaaS | Output 3 D1–D6 | V (FSCR deps) |
| R1.3 | Partial data loaded: sample items, sample suppliers | GoSaaS | Practice (CRP1 partial data) | V |
| R1.4 | Manufacturing ready-to-use: work areas, work centers, resources defined (no structures migrated) | GoSaaS | SOW 6.1; Output 3 D10–D12 | V |
| R1.5 | Maintenance ready-to-use: maintenance org, a sample asset, a work definition | GoSaaS | SOW 7.1 | V |
| R1.6 | CRP1 scripts: P2P (req → PO → receipt → RTV → invoice), process WO, maintenance WO | GoSaaS | SOW 2.1, 4.1, 6.4, 7.4 | NV (script list) |
| R1.7 | Testers use broad implementation roles (security excluded in CRP1) | Twelve | Practice | V |

## Gate 2: Ready for CRP2 (2 weeks, full data, full security, customizations)

| # | Check | Owner | Source | Status |
|---|---|---|---|---|
| R2.1 | CRP1 defects fixed and retested (≈7-week fix/load/validate window used) | GoSaaS | Practice | V |
| R2.2 | Full supplier conversion loaded and reconciled | GoSaaS | SOW RICE 2; practice (full data) | V |
| R2.3 | Full item load (equipment, spares, bulk, manufactured) | GoSaaS / Twelve data | SOW 1.1–1.2, 2.1 | V |
| R2.4 | Security roles and data access built and assigned to CRP users | GoSaaS | SOW Config 12; practice (full security) | V |
| R2.5 | DOA approval rules for requisitions, POs (and expenses if in scope) configured | GoSaaS | SOW 3.3, 4.2, 5.3; Output 3 D20 | V |
| R2.6 | Printable PO report built and unit tested | GoSaaS DEV | SOW RICE 1; practice (customizations) | V |
| R2.7 | Project and non-project accounting rules for POs and receipts | GoSaaS | SOW 3.4, Fin 1 | V |
| R2.8 | Requisitioning and Purchasing BU functions configured in the existing BU structure | GoSaaS | SOW Fin 3.1 | V |
| R2.9 | Supplier Portal registration and self-service configured | GoSaaS | SOW 5.1–5.4 | V |
| R2.10 | Sustainability configured; AP invoice data available | GoSaaS | SOW Fin 4.1 | V |
| R2.11 | Financials remediation list (GL, AR, PM, Grants, AP, CM, FA) decided and built | Both | SOW Fin intro; Intake S5 | V (gap) |

## Gate 3: Ready for UAT (2 weeks, full data + delta)

| # | Check | Owner | Source | Status |
|---|---|---|---|---|
| R3.1 | CRP2 defects closed; regression passed | GoSaaS | Practice | V |
| R3.2 | Delta data load completed and reconciled | GoSaaS | Practice (UAT full + delta) | V |
| R3.3 | Train-the-trainer delivered; training material ready | GoSaaS | SOW Change Mgmt, C.6 | V |
| R3.4 | UAT testers from Twelve named and available | Twelve | SOW E.1, E.3 | V |
| R3.5 | UAT window checked against the Oracle quarterly update calendar | Both | Wave plan W3 | NV (no calendar in FSCR) |
| R3.6 | Configuration documentation (templates) complete for every in-scope module | GoSaaS | SOW Configurations Scope | V |

## Gate 4: Go-live (1 week)

| # | Check | Owner | Source | Status |
|---|---|---|---|---|
| R4.1 | UAT sign-off | Twelve | SOW preamble (timely sign-offs) | V |
| R4.2 | Approved configuration migrated to Production **by Twelve** | Twelve | SOW C.10 | V |
| R4.3 | Supplier conversion loaded to PROD | GoSaaS / Twelve | SOW RICE 2 | NV (who loads) |
| R4.4 | Required employees present in PROD (or onboarded after go-live) | Twelve | SOW C.5.1 | V |
| R4.5 | Go-live and "ready to use" criteria refined and met | Both | SOW C.2.1 | V |
| R4.6 | Cutover / hypercare plan agreed | Both | Intake S7 | V (gap) |
| R4.7 | Go-live week is not in an Oracle update window | Both | Wave plan W3 | NV |

## FSCR coverage

| Item | FSCR | Status |
|---|---|---|
| Checklist content | none (stub) | V |
| Cycle or gate model (CRP/UAT) | none: no CRP/UAT planning rules in shared or knowledge | V |
| Task-level readiness | yes: per-task `ora_dependency_readiness.md` (used for R1.2, R1.4, R0.9, R0.10) | V |
