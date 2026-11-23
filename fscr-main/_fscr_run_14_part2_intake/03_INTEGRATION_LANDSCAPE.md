# Output 3: Integration Landscape (Project Intake, high-level)

**Project:** Twelve: Oracle Cloud SCM Implementation (SOW dated Jan 24, 2025, Doc 50513scm)
**Produced by:** Claude alone, using the GoSaaS checklist as the question structure. FSCR `shared/project-intake/integration-landscape-intake` and `shared/integrations/*` (integration-strategy-advisor etc.) are empty stubs; they contributed no content. FSCR's offering catalog was used only to note that the in-scope modules are native Oracle Cloud offerings (pre-integrated, not custom integrations).
**Labels:** **[SOW]** verified; **SUGGESTED (checklist)** not verified, with a matching open question; **not stated**.

---

## 1. Integrations in scope

**None.** The SOW states: "No extensions and integrations are part of the target scope" [SOW B, RICE 3]. Verified.
Per the run rules, no integration has been created or proposed.

| # | Integration | Endpoint | Middleware | Direction | Objects | Status |
|---|---|---|---|---|---|---|
| – | (none) | – | – | – | – | 0 integrations in scope [SOW] verified |

## 2. External systems mentioned in the SOW (context only, not integrations)

| System | What the SOW says | Integration in scope? | Basis |
|---|---|---|---|
| Coupa | Source of "configuration values and concepts", where applicable, for Self-Service Procurement | No. Configuration reference only. | [SOW B 3.5] verified |
| External Manufacturing Execution System (MES) | "position a longer term vision to integrate Manufacturing with an external MES. Integrating with an MES is not scope." | **No, explicitly excluded.** Future. | [SOW B 6.4] verified |
| Oracle EPM (Planning & Budgeting) | Reporting approach to consider EPM. EPM-enabled sustainability reporting not in scope. | No. Reporting strategy only. | [SOW B Fin 6.1–6.2, 4.3] verified |
| Fusion Data Intelligence | Option in the reporting approach | No. Reporting strategy only. | [SOW B Fin 6.1] verified |
| Supplier source data | Supplier conversion (one-time load, FDD/TDD) | No. A conversion, not an integration. Source system not stated. | [SOW B RICE 2] verified |
| Sustainability manual file uploads | Data "sourced from Payables Supplier Invoices and manual file uploads" | No. Manual upload, a native Oracle feature. | [SOW B Fin 4.1] verified |

## 3. Native (in-pod) flows, not integrations
The SOW says the production Financials modules are "natively integrated with the new SCM modules" [SOW A]. Verified. These are standard Oracle Cloud flows inside one pod (e.g. Purchasing → Receipt Accounting → GL via SLA; Cost Accounting → GL; Procurement ↔ Projects; AP invoices → Sustainability). They need configuration, not integration build. Listed for completeness; no integration objects are created.

## 4. Checklist questions (Scoping Checklist › Integration; Pre-sales › Integrations)

| Checklist question | Answer |
|---|---|
| Integration type (ECAD / MCAD / ERP / Other) | not applicable: none in scope [SOW] |
| End-point system name | not applicable |
| Middleware (OIC / GoSaaS Integrator / Other) | not applicable. Whether Twelve owns OIC is not stated. |
| One-way or two-way | not applicable |
| Object types pushed; item classes | not applicable |
| Integration use cases (new item, item maintenance, change order completion) | not applicable |
| Number of environments | **SUGGESTED (checklist):** 3 (Dev/Test/Prod) "recommended". SOW mentions development and production only [E.6]. → Q-I3 |
| Integration workshops (1 wk per integration) | 0 weeks: no integrations |
| Pre-implementation: "access to each integrated application" | not applicable |
| PM: "integration access requirements document" | not applicable |

## 5. Open questions (each needs a person to confirm)
| ID | Question | Suggested answer |
|---|---|---|
| Q-I1 | Will Coupa run in parallel or be retired at go-live? If it runs in parallel, is an interim interface needed? (That would be a change request; the SOW excludes integrations.) | none |
| Q-I2 | Are there existing integrations into production Financials (bank, payroll, HCM, legacy) that the new SCM configuration could affect, e.g. new accounts or BU changes? | not stated, none suggested |
| Q-I3 | How many environments, and is OIC licensed? | SUGGESTED (checklist): 3 environments; OIC not needed for this SOW |
| Q-I4 | Timeline for the future MES integration (positioning only)? | none |
| Q-I5 | What is the source system for the supplier conversion? | none |
