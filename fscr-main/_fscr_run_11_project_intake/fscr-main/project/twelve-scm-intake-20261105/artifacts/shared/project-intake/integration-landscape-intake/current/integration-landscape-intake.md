# Output 3 — Integration landscape intake (from the SOW only)

FSCR skills: `shared.project-intake.integration-landscape-intake` (generic stub — no questions, fields or template). Checked but not applicable: `shared.integrations.integration-strategy-advisor` (generic stub), `oic-design-advisor`, `api-led-integration-guidance`, `event-driven-integration-guidance`, `legacy-system-integration-patterns` (all five are 2.1 KB generic stubs with the same text apart from the name [V]).
Who produced it: **Claude alone** for the content. FSCR gave only the output names and artifact location.
Tags: [V] = stated in the SOW. [NV] = interpretation.

## 1. In-scope integrations
**None.** The SOW says: "No extensions and integrations are part of the target scope." [V]
No integration was created in this intake. [V]

## 2. Systems the SOW names (context only — not integrations)
| System | SOW mention | Role in this project | Tag |
|---|---|---|---|
| Oracle Fusion Financials (production) | "updates to the production Financials modules natively integrated with the new SCM modules" | Native (same pod), not an integration | V |
| Coupa | "utilize configuration values and concepts from Coupa, where applicable" | Configuration source / possible legacy procurement system; no interface stated | V (named); NV (legacy role) |
| MES (external Manufacturing Execution System) | "longer term vision to integrate … Integrating with an MES is not scope" | Future, out of scope | V |
| EPM (Planning & Budgeting) | Reporting approach to consider EPM; "EPM enabled sustainability reporting is not in scope" | Reporting-approach topic, not an interface | V |
| Fusion Data Intelligence, OTBI, BIP | Reporting approach | Reporting tools, not integrations | V |
| Supplier data (conversion) | Conversions: Suppliers | One-time conversion, not an interface | V |

## 3. Open questions (not stated in the SOW)
| # | Question |
|---|---|
| I1 | What integrations already run against the production Financials pod (banks, HCM, payroll, expenses cards) that the new SCM modules could affect? |
| I2 | Coupa: is it being retired? If it stays during transition, is a coexistence interface (POs, suppliers, invoices) needed and who owns it? |
| I3 | Supplier conversion source system and format (Coupa, AP supplier master, spreadsheet)? |
| I4 | Any carrier, EDI, punch-out catalog or supplier network expected for Self-Service Procurement / Supplier Portal? |
| I5 | Sustainability "manual file uploads" — source and frequency (manual, so not an interface) |
| I6 | Is a middleware platform (OIC) licensed, for the future MES phase? |
| I7 | Any scanners or mobile devices for receiving/putaway or maintenance? |

## 4. Note on scope risk [NV]
These are review points, not scope. Supplier Portal invoice creation, Coupa reuse and the future MES vision often produce interface requests during design. Under the SOW's "Any out of scope items … may result in addendums", such requests would need an addendum.
