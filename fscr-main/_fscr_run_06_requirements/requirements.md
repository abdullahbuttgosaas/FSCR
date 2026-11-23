# Run 06 new business requirements (drafted by Claude; user said "just complete the test, idc how")

Scope: ETIA-TEST, FSCRT test records only. No deletes. Nothing pre-existing outside FSCRT records may change.

| # | Area | Requirement (business wording) |
|---|---|---|
| R1 | SCM: Order Management | We are launching dealer consignment. Add a new order type "Dealer Consignment F06" (code FSCRT_SO_CONSIGN_F06), enabled, description "Stock placed at dealers on consignment". |
| R2 | SCM: lookups | The outdoor-activity list must include climbing: code FSCRT_CLIMBING, meaning "FSCRT_Climbing", display sequence 3, enabled. |
| R3 | SCM: lookups | The paddling activity's description must read "Kayak, canoe and paddleboard gear". |
| R4 | SCM: lookups | The hiking activity must be named "FSCRT_Hiking and trekking". |
| R5 | SCM: Order Management | The warranty swap order type (FSCRT_SO_WARRANTY_SWAP_F01) must be available (enabled). |
| R6 | ERP: Receivables | Consignment invoices need their own AutoInvoice grouping rule FSCRT_GRP6, set up like FSCRT_GRP1, starting 2026-11-03. |

The run must first read what is already set up, decide for each requirement whether anything needs to change, apply only what is missing, and prove that nothing else changed.
