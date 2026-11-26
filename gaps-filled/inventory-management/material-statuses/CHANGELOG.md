# CHANGELOG: Manage Material Statuses

## 26/11/2026 (sitting 1, batch 02)
- Read-only export: INV_INVENTORY_STATUS.csv, INV_INVENTORY_STATUS_TRANSACTION_CONTROL.csv, INV_INVENTORY_STATUS_TRANSLATION.csv; 51 statuses before.
- Try 1 ProcessId 100004744436442: INV_INT_TRXTYPCODE "You must provide a value for the TransactionTypeId attribute": a control row named a transaction type whose MaterialStatusEnabled is N (Cycle Count Transfer, proven by REST inventoryTransactionTypes); nothing created. Fix: control rows only for types with MaterialStatusEnabled Y.
- Own test record FSCRT_HF_GF_MS1: ProcessId 100004744435347, 0 failed objects; after-export 52 statuses, 41 control rows for the new status, only prefix rows added, existing changed 0.
- Skill written (VERIFIED parts from the live test).
- Fresh test F (FSCRT_HF_GF_MS1F, ProcessId 100004743458194): PASS. Wrong/unclear wording reported across this batch and fixed: a REST-resource sentence contradicted the Rules (pick slip grouping; REST resources pickSlipGroupingRules and inventoryMaterialStatuses were then found and added); the privacy note did not warn that the scripts print "Wrote <path>" lines with the environment name; a value set / lookup code with spaces breaks the ModuleId query.
- Fresh test R (FSCRT_HF_GF_MS1R, ProcessId 100004744435568): PASS, no wrong sentence reported.
- Tester suggestions not applied (not errors): package builder output also holds a path (lower-case "wrote"); say silence/"wrote" is normal and check load.zip with inspect_export.py; ModuleId is also visible in the export (REST read kept because ids must be read live); compare lists the parent code next to the child code; "copies" grammar slip in picking rules; worked-example 40 vs 41 control rows wording.
