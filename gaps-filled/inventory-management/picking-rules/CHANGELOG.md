# CHANGELOG: Manage Picking Rules

## 26/11/2026 (sitting 1, batch 02)
- Read-only export: ORA_INV_RULE.csv, ORA_INV_RULE_TRANSLATION.csv, INV_RULE_SELECTION_CRITERION.csv; 24 rules before.
- First try succeeded.
- Own test record FSCRT_HF_GF_PR1: ProcessId 100004743457097, 0 failed objects; after-export 25 rules, only prefix rows added, existing changed 0.
- Skill written (VERIFIED parts from the live test).
- Fresh test F (FSCRT_HF_GF_PR1F, ProcessId 100004743459117): PASS. Wrong/unclear wording reported across this batch and fixed: a REST-resource sentence contradicted the Rules (pick slip grouping; REST resources pickSlipGroupingRules and inventoryMaterialStatuses were then found and added); the privacy note did not warn that the scripts print "Wrote <path>" lines with the environment name; a value set / lookup code with spaces breaks the ModuleId query.
- Fresh test R (FSCRT_HF_GF_PR1R, ProcessId 100004743458585): PASS, no wrong sentence reported.
- Tester suggestions not applied (not errors): package builder output also holds a path (lower-case "wrote"); say silence/"wrote" is normal and check load.zip with inspect_export.py; ModuleId is also visible in the export (REST read kept because ids must be read live); compare lists the parent code next to the child code; "copies" grammar slip in picking rules; worked-example 40 vs 41 control rows wording.
