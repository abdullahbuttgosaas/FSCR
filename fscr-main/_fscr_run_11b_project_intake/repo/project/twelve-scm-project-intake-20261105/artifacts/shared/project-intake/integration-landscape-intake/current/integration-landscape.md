# Output 3 — Integration Landscape Intake (Twelve)

Source: SOW 50513scm only.
FSCR skills used:
- `shared.project-intake.integration-landscape-intake` and `shared.integrations.integration-strategy-advisor` are both generic stubs with no questions and no template. They provided only the output headings (recommendations, work products, review points).

FSCR had nothing to fill in. Claude filled all content from the SOW.

Legend: **V** = verified against the SOW text. **NV** = not verified. "not recorded" = the SOW does not say.

## 1. In-scope integrations

**None.** The SOW says "No extensions and integrations are part of the target scope" (RICE 3). — V

No integration objects were created.

## 2. Systems the SOW names (context only, not integrations)

| System | How the SOW uses it | Integration in scope? | Status |
|---|---|---|---|
| Oracle Cloud Financials (production): GL, AR, PM, Grants, AP, CM, FA | Native, built-in connection to the new SCM modules. Remediated, not integrated. | No (native) | V (A; Fin intro) |
| Coupa | Source of configuration values and concepts for Self-Service Procurement (3.5) | No. Configuration reuse only. | V |
| External Manufacturing Execution System (MES) | Long-term vision only. "Integrating with an MES is not scope." | No (excluded) | V (6.4) |
| EPM (Planning & Budgeting) | Included in the reporting approach (6.1, 6.2). EPM-enabled sustainability reporting is out of scope (4.3). | No | V |
| OTBI, BI Publisher, Fusion Data Intelligence | Included in the reporting approach (6.1) | No (reporting tools) | V |
| Payables supplier invoices and manual file upload → Sustainability | Data source for Sustainability (4.1). Inside Oracle plus manual upload. | No (native plus manual) | V |
| Legacy source of supplier data | Supplier conversion (RICE 2). Source system not named. | No. This is a conversion. | V (conversion); source not recorded |
| "Other systems" | Twelve provides data from other systems in a mutually agreed format (E.1). The systems are not named. | not recorded | V (clause); systems not recorded |

## 3. Integration counts

| Measure | Value | Status |
|---|---|---|
| Inbound integrations | 0 | V (RICE 3) |
| Outbound integrations | 0 | V (RICE 3) |
| Middleware / OIC | not recorded (no integrations in scope) | — |
| Conversions (not integrations) | 1: Suppliers | V (RICE 2) |

## 4. Review points (NV)

- The MES vision (6.4) and future location rollouts (C.3) will probably bring integrations later. Raise them as a change request or phase-2 item, not in this scope.
- If Coupa stays live after go-live, a Coupa↔Oracle integration question will come up. The SOW does not say whether Coupa is retired.
- Bank or payment integrations for AP are not mentioned. Production Financials already exists, so any existing integrations are assumed unaffected. This is not verified.

## 5. Open questions

| # | Question |
|---|---|
| I1 | What integrations exist today for the production Financials modules (banks, payroll, HR, tax, cards)? Does the SCM implementation affect any of them? |
| I2 | Is Coupa retired at go-live? If not, what is the coexistence approach? |
| I3 | What is the source system for the supplier conversion, and what file format is used? |
| I4 | Which "other systems" does E.1 refer to? |
| I5 | MES: which product, and when? This is for the long-term vision only. |
| I6 | Will EPM or FDI reporting need data extracts that count as integrations later? |
