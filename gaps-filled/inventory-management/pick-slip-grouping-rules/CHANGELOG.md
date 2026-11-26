# CHANGELOG: Manage Pick Slip Grouping Rules

## 26/11/2026 (sitting 1, batch 02)
- Read-only export: INV_PICK_GROUPING_RULE.csv, INV_PICK_GROUPING_RULE_TRANSLATION.csv; 27 rules before.
- First try succeeded.
- Own test record FSCRT_HF_GF_PSG1: ProcessId 100004744433919, 0 failed objects; after-export 28 rules, only prefix rows added, existing changed 0.
- Skill written (VERIFIED parts from the live test).
- Fresh test F (FSCRT_HF_GF_PSG1F, ProcessId 100004744436942): PASS. Wrong/unclear wording reported across this batch and fixed: a REST-resource sentence contradicted the Rules (pick slip grouping; REST resources pickSlipGroupingRules and inventoryMaterialStatuses were then found and added); the privacy note did not warn that the scripts print "Wrote <path>" lines with the environment name; a value set / lookup code with spaces breaks the ModuleId query.
- Fresh test R (FSCRT_HF_GF_PSG1R, ProcessId 100004743460112): PASS, no wrong sentence reported.
- Tester suggestions not applied (not errors): package builder output also holds a path (lower-case "wrote"); say silence/"wrote" is normal and check load.zip with inspect_export.py; ModuleId is also visible in the export (REST read kept because ids must be read live); compare lists the parent code next to the child code; "copies" grammar slip in picking rules; worked-example 40 vs 41 control rows wording.
