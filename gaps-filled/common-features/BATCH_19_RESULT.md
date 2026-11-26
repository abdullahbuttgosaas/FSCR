# Batch 19 result: Common Features (AB), tablet, digital assistant, Avalara, China account attributes

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (eighth Common Features sitting, second batch). Read only on Oracle: task exports and REST GET / describe; nothing was created.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 19:16 | 19:18 | 2 | Read-only exports (all refused, task flag N); REST names tried by GET |
| 19:18 | 19:22 | 4 | `taxPartnerRegistrations` answered HTTP 500 (not 404): describe = create, get; Oracle docs: tax calculation partner registration |
| 19:22 | 19:45 | 23 | Avalara onboarding skill (written, unsafe), cards, evidence, reports |

## Results
| # | Task | Status | Working min | Waiting min | Proof / reason (on the card) |
|---|---|---|---:|---:|---|
| 1 | Manage Tablet Application Configuration | screen-only | 4 | 2 | export refused; fscm tabletApplicationConfigurations, crm mobileApplicationConfigurations 404 |
| 2 | Manage Digital Assistant | screen-only | 4 | 2 | export refused; fscm digitalAssistants, crm digitalAssistantConfigurations 404 |
| 3 | Manage Avalara E-invoicing | screen-only | 4 | 2 | export refused; taxPartners, eInvoicingPartners 404; taxPartnerRegistrations is for tax calculation (Oracle docs), not e-invoicing |
| 4 | Manage Indirect Tax Automation with Avalara | **written (unsafe)** | 10 | 3 | REST route exists: taxPartnerRegistrations (create only). Needs the customer's Avalara account and password; registers the partner for the whole environment; no delete |
| 5 | Create Enterprise Additional Account Attributes for China | screen-only | 4 | 2 | export refused; chinaAdditionalAccountAttributes, additionalAccountAttributes 404 |
| | **Total** | **4 screen-only, 1 written** | **26** | **11** | |

## Problems and findings
1. **Avalara onboarding is not screen-only:** `taxPartnerRegistrations` has create (VERIFIED by describe). A plain GET gives HTTP 500 (Oracle docs: GET not supported). Unsafe: needs a real partner account and its password (never typed by an agent) and changes tax calculation for everyone, with no delete.
2. **Finding outside this sitting's 10 (not changed):** Manage Indirect Tax Automation with Thomson Reuters is screen-only in `screen-only.csv`, but the same resource registers tax calculation partners; re-judge it in a later sitting.

## What is left
See `MODULE_RESULT.md`.
