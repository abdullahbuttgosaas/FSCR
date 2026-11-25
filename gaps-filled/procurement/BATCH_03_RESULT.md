# Procurement batch 03: result (2026-11-25, sitting 2, AB with Claude)

| Task | Status | Write / test / wait min | Test records (ProcessId) |
|---|---|---|---|
| Manage Compliance Checklist Sections | **tested** | 6 / 6 / 4 | GAPFILL_AB_B3_CS1 draft (100004744391888), CS3 active with question (100004744391914); fresh CS4F (100004744395994) PASS |
| Manage Compliance Checklist Questions | **tested** | 5 / 4 / 3 | GAPFILL_AB_B3_CQ1 draft, CQ2 active; fresh CQ3F (100004744391947) PASS |
| Manage Compliance Checklist Templates | **tested** | 6 / 10 / 7 | GAPFILL_AB_B3_CT5 with section CS3 (100004744396588); fresh CT6F (100004744393751) PASS |
| Configure Procurement Business Function | **written (unsafe to test)** | 5 / 2 / 2 | none: import blocked (changes a live BU) |
| Specify Supplier Contract Management Business Function Properties | **written (unsafe to test)** | 4 / 2 / 2 | none: import blocked (changes a live BU) |

## Findings
- Checklist sections, questions and templates are supplier-qualification objects: section and question usage `ORA_CHECKLIST`, but template usage **`CHECKLIST`**.
- A template with usage `ORA_CHECKLIST` imports with "success" but is invisible (CT2, CT4 left in Oracle, not visible). A template section row needs `ObjectVersionNumber1=1` (else JBO-26048).
- An active section needs at least 1 active question (`POQ_AREA_QUES_REQD_ERROR`). Oracle sets the owner when the owner columns are empty.
- Both business-function tasks hold one row per live business unit. The agent's permission check blocked the test-and-restore import, so both are written-unsafe with an offline package step.

## Refused / not created
GAPFILL_AB_B3_CS2 (no question), GAPFILL_AB_B3_CT1 and CT3 (SQL error).
