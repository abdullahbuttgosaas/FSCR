# Batch 02: Inventory Management gap fill (sitting 1)

| Start | Finish | Working minutes | Waiting minutes |
|---|---|---:|---:|
| 26/11/2026 17:58 | 26/11/2026 18:13 | 68 (sum over 5 tasks) | 41 (sum over 5 tasks; tasks ran in parallel) |

Sign-in: 26/11/2026 17:36 still valid for the whole batch (no 401/403); no re-sign-in needed.

| Task | Status | Working min | Waiting min | Own test record (ProcessId) | Fresh tests (ProcessId) |
|---|---|---:|---:|---|---|
| INV_MANAGE_MATERIAL_STATUSES | tested | 16 | 9 | FSCRT_HF_GF_MS1 (try 1 100004744436442 failed; try 2 100004744435347) | MS1F 100004743458194, MS1R 100004744435568 |
| INV_MANAGE_PICKING_RULES | tested | 12 | 7 | FSCRT_HF_GF_PR1 (100004743457097) | PR1F 100004743459117, PR1R 100004743458585 |
| INV_MANAGE_PICK_SLIP_GROUPING_RULES | tested | 12 | 7 | FSCRT_HF_GF_PSG1 (100004744433919) | PSG1F 100004744436942, PSG1R 100004743460112 |
| INV_MANAGE_INVENTORY_LOOKUPS | tested | 14 | 9 | FSCRT_HF_GF_LK1 + code C1 (try 1 100004744436456 failed; try 2 100004744436620) | LK1F 100004744435460, LK1R 100004744435537 |
| ORA_INV_MANAGE_INVENTORY_VALUE_SETS | tested | 14 | 9 | FSCRT_HF_GF_VS1 + value V1 (try 1 100004744435316 failed; try 2 100004743458011) | VS1F 100004744436929, VS1R 100004744435554 |

Every record was read back by an after-export compared with the before-export (only FSCRT_HF_GF_ rows added,
existing changed 0) and by REST (inventoryMaterialStatuses, pickSlipGroupingRules, standardLookups, valueSets);
picking rules have no REST resource (404).

## Problems and findings
- Material statuses: a transaction-control row for a type that is not status-controlled (MaterialStatusEnabled N)
  fails the whole status with INV_INT_TRXTYPCODE. The skill reads the allowed types live by REST
  (inventoryTransactionTypes?q=MaterialStatusEnabled='Y'). Oracle adds a missing allowed type itself.
- Lookups and value sets: ModuleId is required (JBO-27014 for lookups; ORA-01400 NULL insert for value sets).
  The skills read it live by REST (standardLookups / valueSets) from an object of the same module, never from
  another environment.
- REST resources found for material statuses and pick slip grouping rules after the first fresh test; added to
  the skills and re-tested.
- New helper scripts/template_row.py (copy a working record of your own export under a new code).
- A privacy sentence was added to the shared skill template, so batch 01 skills were re-tested too (R3, all pass).

## What is left
63 of 73 missing tasks. Sitting limit reached (10 tasks tested this sitting). Next sitting starts with
the easy group: Release/ship rules (WSH_MANAGE_SHIP_CONFIRM_RULES, WSH_MANAGE_SHIPPING_EXCEPTIONS), Carriers and
SCM common lookups, receiving and shipping value sets, Regulatory Authority for Product Recall.
