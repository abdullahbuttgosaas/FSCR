# Procurement batch 04: result (2026-11-25, sitting 2, AB with Claude)

| Task | Status | Write / test / wait min | Test records |
|---|---|---|---|
| Manage B2B Configuration | **tested** (REST) | 6 / 5 / 3 | service provider GAPFILL_AB_B4_SP1 + partner GAPFILL_AB_B4_TP2; fresh SP2F + TP3F, READBACK PASS |
| Manage Contract Terms Descriptive Flexfields | **written (unsafe to test)** | 4 / 1 / 1 | none: needs a shared flexfield deployment |
| Manage Collaboration Messaging Domain Value Map | **screen-only** | - | no CSV, no REST resource found |
| Manage Self Service Procurement Messages | **screen-only** | - | CSV flag N, export gives no ZIP, no REST resource found |

## Still open (next sitting)
Intake request, purchasing document, requisition and work confirmation approvals, and task configurations. REST `approvalRules` exists (get, create, upsert, duplicate) but needs a `ParticipantId` and changes who approves live documents. Next: read the participants (read-only) and judge whether a disabled new rule (EnabledFlag N) is a safe test, or mark them unsafe.

## Refused / not created
GAPFILL_AB_B4_TP1 (no ServiceProviderId, HTTP 400).
