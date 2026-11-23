---
skill_id: "gosaas.gap-fills.common-features.manage-tax-statuses"
name: "Manage Tax Statuses (GoSaaS gap fill, NOT WORKING YET)"
description: "Attempted recipe to create a new tax status under a test tax through FSCR's setup-task CSV export and import (ZX_TAX_STATUS). The import was REJECTED 3 times on 2026-11-23 (ZX_INVALID_VALUE for the Tax attribute): for a tax that is not live, for a tax enabled for simulation, and again after the regime was subscribed by a test business unit. Kept so the next attempt starts from what is known. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 1, 2026-11-23. Status FAILED: no status was created."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_STATUSES"
task_name: "Manage Tax Statuses"
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
side_effects:
  - "Export: read-only. Import: the one attempt failed and created nothing."
---

# Manage Tax Statuses (GoSaaS gap fill, NOT WORKING YET)

> **Added by GoSaaS, not part of official FSCR.** **Status: failed.** This recipe did **not** create a status in our test. Do not use it to do the task yet; use it as the starting point for the next attempt.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A tax status (for example STANDARD, EXEMPT, ZERO) sits under one tax. Tax rates hang below a status. One status per tax can be the default.

## What is known (VERIFIED)
1. **Export works** (170 to 227 s): `--task-code ZX_MANAGE_TAX_STATUSES --data`, same commands as `../manage-taxes/SKILL.md` Step 2. 33 files: `ZX_TAX_STATUS.csv` (44 columns: `TaxStatusCode, Tax, TaxRegimeCode, PartyNumber, ContentOwnerPartyTypeCode, EffectiveFrom, EffectiveTo, RuleBasedRateFlag, AllowRateOverrideFlag, AllowExemptionsFlag, AllowExceptionsFlag, DefaultStatusFlag, DefaultFlgEffectiveFrom, ..., TaxStatusName, ..., RegimeTypeFlag`), `ZX_TAX_STATUS_TRANSLATION.csv` (`ZX_TAX_STATUS.TaxStatusCode, ZX_TAX_STATUS.Tax, ZX_TAX_STATUS.TaxRegimeCode, ZX_TAX_STATUS.PartyNumber, ZX_TAX_STATUS.ContentOwnerPartyTypeCode, ..., Language, SourceLang, TaxStatusName`), 30 rate files, `ASM_SETUP_CSV_METADATA.xml`. **No tax or regime file**: the status refers to its tax by code; no parent row can be added.
2. **No REST resource** for statuses (`taxStatusesLOV`: HTTP 404). `taxRatesLOV` answers (for the rates task).
3. **Builder call used** (template row from an existing GCO status, then the generic builder; rate files header only):
   ```bash
   python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_STATUS.csv --match "TaxStatusCode=<TEMPLATE>" \
     --set "TaxStatusCode=<CODE>" --set "Tax=<TAX>" --set "TaxRegimeCode=<REGIME>" --set "TaxStatusName=<NAME>" \
     --set "EffectiveFrom=<yyyy/mm/dd>" --set "DefaultFlgEffectiveFrom=<yyyy/mm/dd>" --clear EffectiveTo --clear DefaultFlgEffectiveTo --out "<RUN>/rows.txt"
   python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ZX_TAX_STATUS_TRANSLATION.csv \
     --match "ZX_TAX_STATUS.TaxStatusCode=<TEMPLATE>" --match "Language=US" --set "ZX_TAX_STATUS.TaxStatusCode=<CODE>" \
     --set "ZX_TAX_STATUS.Tax=<TAX>" --set "ZX_TAX_STATUS.TaxRegimeCode=<REGIME>" --set "TaxStatusName=<NAME>" --out "<RUN>/rows.txt" --append
   python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name status_new.zip --prefix <PREFIX> \
     --key "ZX_TAX_STATUS.csv=TaxStatusCode,Tax,TaxRegimeCode" \
     --key "ZX_TAX_STATUS_TRANSLATION.csv=ZX_TAX_STATUS.TaxStatusCode,ZX_TAX_STATUS.Tax,ZX_TAX_STATUS.TaxRegimeCode,Language" \
     --prefix-col "ZX_TAX_STATUS.csv=TaxStatusCode" --max-len "TaxStatusCode=30" @"<RUN>/rows.txt"
   ```
   Import with `--task-code ZX_MANAGE_TAX_STATUSES --task-name "Manage Tax Statuses"` (about 80 s).

## Attempt (2026-11-23, `GAPFILL_AB_P1_ST1` on tax `GAPFILL_AB_P1_TX1`, regime `GAPFILL_AB_TR1`)
| # | What | Oracle said | Created? |
|---|---|---|---|
| 1 | status copied from an existing GCO status; tax not live (`N`), regime with no subscription | `Detail Object: TaxStatus ... 1 rows ... 1 failed`; `Row Identifier: <REGIME>, <TAX>, <CODE>, -99 ... ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute.` (-99 = global configuration owner, resolved correctly) | no |
| 2 (approved by AB) | same, `GAPFILL_AB_P1_ST2` on a **new simulation tax** `GAPFILL_AB_P1_TX4S` (`LiveForProcessingFlag=S`, created and read back fine), same unsubscribed regime | the same `ZX_INVALID_VALUE ... Tax attribute` (ProcessId 100004741402182) | no |
| 3 (approved by AB) | regime first subscribed by one test business unit (`ZX_MANAGE_TAX_REGIMES` import: usage + subscription `GCO_ONLY` + detail rows, read back by export); then `GAPFILL_AB_P1_ST3` on the original tax `GAPFILL_AB_P1_TX1` | the same `ZX_INVALID_VALUE ... Tax attribute` (ProcessId 100004741398375) | no |

Why we stopped after attempt 1 (attempt 2 was added with AB's approval): in the same test environment, a **tax formula** on the very same tax imported fine, so the tax exists. In the export, every tax that has a status is **live for processing (`Y`) or enabled for simulation (`S`) and its regime is subscribed**; our test tax is neither, on purpose. The fixes (make the tax live or simulated, or subscribe the regime) **change existing records and real tax behaviour**, which the gap rules do not allow without the person's decision. Attempt 2 ruled out "not live" and attempt 3 ruled out "no business-unit subscription". The one difference left: every regime whose taxes have statuses also has a **global configuration owner subscription** row (`ORA_ZX_BU_GCO_TAX_SUB.csv`), and that row can only be written with internal IDs (`FirstPtyOrgId=-99`, `SubscriptionOptionId`), which the gap rules forbid. GUESS: statuses for a GCO-owned tax need that GCO subscription. Stopped at the 3-attempt limit.

## Next attempt (needs the person's decision)
1. (tried, attempt 3: a business-unit subscription does **not** help), and (tried, attempt 2: a simulation tax does **not** help).
2. Subscribe the global configuration owner to the test regime on the screen (Manage Tax Regimes, configuration options), then retry once, or
3. Create one status on the screen for a test tax, then export and compare the rows.

## Rules and limits
1. New records only; never import a full export. Never change a real tax.
2. This skill never deletes. The failed attempt created nothing (checked by the import log: 1 failed, 0 succeeded).
3. Tested on one environment (release 11.13.26.10.0). **Not working.**
