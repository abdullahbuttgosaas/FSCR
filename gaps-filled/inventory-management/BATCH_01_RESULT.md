# Batch 01: Inventory Management gap fill (sitting 1)

| Start | Finish | Working minutes | Waiting minutes |
|---|---|---:|---:|
| 26/11/2026 17:37 | 26/11/2026 17:56 (R3 re-tests 18:10) | 56 (sum over 5 tasks) | 39 (sum over 5 tasks; tasks ran in parallel) |

Sign-in: 26/11/2026 17:36 (waiting time, not task time). No re-sign-in was needed.

| Task | Status | Working min | Waiting min | Own test record (ProcessId) | Fresh tests (ProcessId) |
|---|---|---:|---:|---|---|
| INV_MANAGE_INVENTORY_TRANSACTION_REASONS | tested | 11 | 7 | FSCRT_HF_GF_RSN1 (100004744433283) | RSN1F 100004744436023, RSN1R 100004744433588, RSN2R 100004743456909, RSN3R 100004743459255 |
| INV_MANAGE_LOT_EXPIRATION_ACTIONS | tested | 11 | 7 | FSCRT_HF_GF_LEA1 (100004743456540) | LEA1F 100004744433492, LEA1R 100004744436085, LEA2R 100004743456900, LEA3R 100004743457232 |
| INV_MANAGE_LOT_GRADES | tested | 11 | 7 | FSCRT_HF_GF_LG1 (100004744431804) | LG1F 100004744435059, LG1R 100004744435197, LG2R 100004744433685, LG3R 100004744435515 |
| WSH_MANAGE_RELEASE_SEQUENCE_RULES | tested | 13 | 9 | FSCRT_HF_GF_RSR1 (try 1 100004743455865 failed; try 2 100004744434147) | RSR1F 100004744434457, RSR1R 100004744433597, RSR2R 100004744436226, RSR3R 100004744435524 |
| WSH_MANAGE_SHIPPING_COST_TYPES | tested | 13 | 9 | FSCRT_HF_GF_SCT1 (try 1 100004744432773 failed; try 2 100004743455953) | SCT1F 100004744433483, SCT1R 100004744435209, SCT2R 100004744435268, SCT3R 100004743458601 |

Every record was read back: an after-export compared with the before-export (only FSCRT_HF_GF_ rows added, existing
rows changed 0) and, where a REST resource exists (inventoryTransactionReasons, inventoryLotGrades), a REST GET.

## Problems and findings
- Release sequence rules: an empty ObjectVersionNumber makes the import fail at the database insert (JBO-26041)
  while the row line still says "0 rows of them failed". Setting it to 1 (as on every existing row) fixed it.
  Lesson: check the business object line, not only the row count.
- Shipping cost types: the export package can be empty; Amount is required (JBO-27014). Cost type codes are read
  live from lookup WSH_FREIGHT_COST_TYPE.
- FSM process logs are one line with literal \r\n and name the environment and the submitter. New helper
  scripts/check_import_log.py prints only status lines and hides the submitter.
- Fresh testers found wording problems twice (F and R rounds); all fixed; the R2 round found no wrong sentence.
- A privacy sentence added during batch 02 also changed these skills, so all five were tested again (R3): all passed, no wrong sentence.
- Helpers written in scripts/: inspect_export.py, build_fsm_package.py, compare_fsm_exports.py, check_import_log.py.

## What is left
68 of 73 missing tasks. Next: batch 02 (Material Statuses, Picking Rules, Pick Slip Grouping Rules,
Inventory Lookups, Inventory Value Sets).
