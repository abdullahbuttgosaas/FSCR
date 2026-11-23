---
skill_id: "gosaas.gap-fills.common-features.manage-tax-rules"
name: "Manage Tax Rules (GoSaaS gap fill, NOT WORKING YET)"
description: "Attempted recipe to create a new, disabled tax rule on a test tax through FSCR's setup-task CSV export and import (ZX_TAX_RULE_SUPERTYPE + rule result). The import was REJECTED 3 times on 2026-11-24 (ZX_RECRATE_DATE_INVALID, the tax's dates not found). Kept so the next attempt starts from what is known. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 2, 2026-11-24. Status FAILED: no rule was created."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_RULES"
task_name: "Manage Tax Rules"
dataloader_import_mode: "FSM"
type: "import"
owner_team: "GoSaaS"
version: "0.0.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
  - "gosaas common-features/manage-tax-regimes/scripts/template_row.py"
  - "ZX_MANAGE_TAXES (the tax must exist)"
  - "ZX_MANAGE_TAX_CONDITION_SETS (the condition set must exist)"
side_effects:
  - "Export: read-only. Import: all 3 attempts failed and created nothing (checked by a second export)."
---

# Manage Tax Rules (GoSaaS gap fill, NOT WORKING YET)

> **Added by GoSaaS, not part of official FSCR.** **Status: failed.** This recipe did **not** create a rule in our test. Do not use it to do the task yet; use it as the starting point for the next attempt.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax rule decides one step of tax determination (for example "is this tax applicable") for one tax. It is built on a determining factor set; each **rule result** row points to a condition set and gives the result (for example `NOT_APPLICABLE`). Rules are evaluated by priority. A **disabled** rule (`EnabledFlag=N`) is never evaluated.

## What is known (VERIFIED)
1. **Export works** (75 to 121 s): `--task-code ZX_MANAGE_TAX_RULES --data`, same commands as `../manage-tax-condition-sets/SKILL.md` Step 2. 15 files, the **same files as the condition sets package**: `ZX_TAX_RULE_SUPERTYPE.csv` (rule header: `TaxRegimeCode, Tax, TaxRuleCode, ServiceTypeCode, RecoveryTypeCode, Priority, EffectiveFrom, ContentOwnerPartyTypeCode, ContentOwnerPartyNumber, BuName, LegalEntityIdentifier, DetFactorTemplCode, SystemDefaultFlag, EffectiveTo, EnabledFlag, ..., TaxRuleName, ...`), `ZX_TAX_RULE_SUPERTYPE_TRANSLATION.csv`, `ORA_ZX_TAX_RULE_RESULT.csv` (result rows, with the condition repeated in `...1` columns), condition set and factor set files, `ASM_SETUP_CSV_METADATA.xml`. No tax file: the rule refers to its tax by code.
2. **Rows tried** (template row from the one existing rule, an applicability rule owned by a business unit; `template_row.py` then `build_fsm_package.py`, 1 + 1 + 1 rows, other files header only):
   - Header: `TaxRegimeCode=<REGIME>`, `Tax=<TAX>`, `TaxRuleCode=<CODE>`, `ServiceTypeCode=DET_APPLICABLE_TAXES`, `Priority=10`, `EffectiveFrom=<date>`, `ContentOwnerPartyTypeCode=GCO` (BuName cleared), `DetFactorTemplCode=<factor set>`, `SystemDefaultFlag=N`, `EnabledFlag=N`, `RecordTypeCode=USER_DEFINED`, `TaxRuleName=<NAME>`, `EnterpriseId=1`, `RegimeTypeFlag=I`.
   - Translation: the header key columns (prefixed `ZX_TAX_RULE_SUPERTYPE.`), `Language=US`, `SourceLang=US`, `TaxRuleName`.
   - Result: `ConditionGroupCode=<condition set>`, `Priority=1`, `EnabledFlag=Y`, the header keys, `Priority1=10`, `ResultTypeCode=APPLICABILITY`, `AlphanumericResult=NOT_APPLICABLE`, `AllowExemptionsFlag=N`, `AllowExceptionsFlag=N`, `DetFactorTemplCode` and `DetFactorTemplCode1` = factor set, `ConditionGroupCode1` = condition set, `EnabledFlag1=Y`, and the condition (`AlphanumericValue1`, class, qualifier, factor, operator) copied from the condition set; `NumericValue1` (internal geography ID) cleared.
   - Key for the builder: `ZX_TAX_RULE_SUPERTYPE.csv=TaxRuleCode,TaxRegimeCode,Tax`, `ORA_ZX_TAX_RULE_RESULT.csv=TaxRuleCode,TaxRegimeCode,Tax,ConditionGroupCode`, translation by the prefixed key + `Language`.
3. **Every import was rejected** with the same message on the header (the result row then fails too):
   `ZX_RECRATE_DATE_INVALID: Enter a date range that's within the date range of the parent tax of {TAX_START_DATE} to {TAX_END_DATE}.`
   The placeholders are **not filled**, so Oracle did not find the parent tax at all (it is not a real date clash).

| Attempt | Change | ProcessId | Result |
|---|---|---|---|
| 1 | rule from 2026/01/01 (= the tax's start), owner GCO | 100004741398794 | rejected |
| 2 | rule from 2026/02/01 (inside the tax's dates) | 100004741399835 | rejected, same |
| 3 | owner `OU` + `BuName` of the test business unit that subscribes the test regime | 100004742403274 | rejected, same |

4. A second rules export after attempt 3 shows **no change** in any of the 15 files (compare PASS on "nothing added").

## Most likely cause (GUESS)
The test tax `GAPFILL_AB_P1_TX1` is **not live** on a regime whose only subscription is a business-unit one made for the test. Tax statuses on the same tax are refused in the same way (`manage-tax-statuses`: "valid value for the Tax attribute"), while formulas and jurisdictions on it import fine. Statuses, rates and rules seem to look the tax up only among taxes that are **live (or in simulation) on a regime subscribed by the global configuration owner**. Making that true changes real tax setup, so it was not done.

## How to finish it (needs a person's decision)
1. A person makes one test tax usable for rules (for example a GCO subscription of the test regime on the screen and a simulation tax), or names an existing live test tax where a **disabled** rule is acceptable.
2. Rebuild the three rows above for that tax, import once, then read back with a second rules export and `compare_fsm_exports.py` (expect the 3 rows added).
3. Then write the full skill and run a fresh test.

## Rules and limits
- New records only; never import a full export. Keep the rule **disabled** (`EnabledFlag=N`) in any test.
- Never take IDs from an export (`NumericValue1` holds an internal geography ID; leave it empty).
- Never import twice while one may still be running; at most 3 attempts.
- Tested on one environment (release 11.13.26.10.0).
