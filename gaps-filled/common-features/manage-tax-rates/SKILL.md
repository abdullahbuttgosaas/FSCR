---
skill_id: "gosaas.gap-fills.common-features.manage-tax-rates"
name: "Manage Tax Rates and Tax Recovery Rates (GoSaaS gap fill, NOT WORKING YET)"
description: "Not built: a tax rate needs a tax status, and a tax status could not be created on a test tax (see manage-tax-statuses). Only the read-only export was checked (2026-11-24). Kept so the next attempt starts from what is known. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 2, 2026-11-24. Status FAILED: blocked by ZX_MANAGE_TAX_STATUSES; no import was made."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES"
task_name: "Manage Tax Rates and Tax Recovery Rates"
dataloader_import_mode: "FSM"
type: "import"
owner_team: "GoSaaS"
version: "0.0.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "ZX_MANAGE_TAX_STATUSES (the status must exist; that task failed)"
side_effects:
  - "Export only (read-only). No import was made."
---

# Manage Tax Rates and Tax Recovery Rates (GoSaaS gap fill, NOT WORKING YET)

> **Added by GoSaaS, not part of official FSCR.** **Status: failed (blocked).** No rate was created and no import was tried. Do not use this to do the task.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## Why it is blocked
A tax rate belongs to a **tax status** (`TaxStatusCode` of `TaxRegimeCode` + `Tax`). The status import on the test taxes was rejected 3 times in batch 3 part 1 (`ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute`, see `../manage-tax-statuses/SKILL.md`), so there is **no test status** to put a rate on. Putting a test rate on a real status would change real tax setup, so it was not done. The batch 3 plan says to mark this task failed "blocked by ZX_MANAGE_TAX_STATUSES".

## What is known (VERIFIED)
1. **Export works** (109 s, 2026-11-24; planning export 111 s on try 2): `--task-code ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES --data`, same commands as `../manage-tax-condition-sets/SKILL.md` Step 2. 32 files: `ZX_TAX_STATUS.csv` and its translation (the parent statuses), the percentage rate files `ORA_ZX_TAX_RATE_PERCENT_TYPE.csv` (+ `_TRANSLATION`, `_DEF_ACCOUNT`), and quantity, gross amount, recovery, schedule, withheld, line-amount and unit-price rate files, plus `ASM_SETUP_CSV_METADATA.xml`.
2. `ORA_ZX_TAX_RATE_PERCENT_TYPE.csv` starts with `TaxRateCode, EffectiveFrom, TaxJurisdictionCode, RecoveryTypeCode, ActiveFlag, TaxClass, PartyNumber, ContentOwnerPartyTypeCode, TaxAcctEntityCode, EffectiveTo, TaxRegimeCode, Tax, ...`. The environment had 5 percentage rates and 4 statuses, none on a `GAPFILL_` tax.
3. Because the status file is in this package, a rate's parent status row would be copied unchanged (`copy_parent_rows.py`), like the regime row for taxes. GUESS
4. REST `taxRatesLOV` answers (batch 3 part 1) and could be the read-back besides an export compare. GUESS

## How to finish it (needs a person's decision)
First make `manage-tax-statuses` work (it needs a tax that Oracle accepts for statuses; see that skill). Then: template row from an existing percentage rate, parent status row copied unchanged, one import, read back by a second export (and `taxRatesLOV`), then write the full skill and run a fresh test.
