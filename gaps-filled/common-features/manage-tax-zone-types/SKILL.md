---
skill_id: "gosaas.gap-fills.common-features.manage-tax-zone-types"
name: "Manage Tax Zone Types (GoSaaS gap fill, NOT WORKING YET)"
description: "Attempted recipe to create a new tax zone type (TCA geography type with use TAX) through FSCR's setup-task CSV export and import. The import FAILED 3 times on 2026-11-23 (database insert error). Kept so the next attempt starts from what is known. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 2, 2026-11-23. Status FAILED: no zone type was created."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_ZONE_TYPES"
task_name: "Manage Tax Zone Types"
dataloader_import_mode: "FSM"
type: "import"
owner_team: "GoSaaS"
version: "0.0.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Export: read-only. Import: none succeeded; failed imports created nothing (checked with a new export)."
---

# Manage Tax Zone Types (GoSaaS gap fill, NOT WORKING YET)

> **Added by GoSaaS, not part of official FSCR.** **Status: failed.** This recipe did **not** create a zone type in our test. Do not use it to do the task. Use it as the starting point for the next attempt: what the package looks like, what was tried, and what Oracle said.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A tax zone type is a Trading Community geography type with geography use `TAX` (for example "EU member states" or a county group). Tax zones of that type then list geographies or postal code ranges, and tax regimes or jurisdictions can use a zone. The task's package holds the zone types, zones, zone identifiers, geography ranges, hierarchy nodes, relationships and relationship types.

## When to use
- Only to retry this gap (see "Next attempt"). For real work, create the zone type on the screen until this recipe passes.

## Placeholders
```text
FSCR, GAPS, H, RUN, PREFIX: as in ../manage-document-sequences/SKILL.md
NAME = new GeographyType, starting with PREFIX
```

## What is known (VERIFIED)
1. **Export works** (60 to 165 s): `--task-code ZX_MANAGE_TAX_ZONE_TYPES --data`, same commands as the other gap skills. 9 files:
   `ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv` (23 columns: `GeographyType, GeographyUse, PostalCodeRangeFlag, LimitedByGeographyId, CreatedByModule, LastUpdatedBy, CreatedBy, RequestId, GeographyTypeName, GeographyName, BoundaryGeographyType, StartDate, EndDate, GeographyElement1..10`),
   `ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE_TRANSLATION.csv` (7: `ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.GeographyType, CreatedBy, GeographyType, GeographyTypeName, Language, LastUpdatedBy, SourceLang`),
   `HZ_GEOGRAPHIES_ZONE.csv`, `ORA_HZ_GEO_ZONE_IDENTIFIER.csv`, `ORA_HZ_GEOGRAPHY_RANGE.csv`, `ORA_HZ_GEO_HIERARCHY_NODE.csv`, `ORA_HZ_GEO_RELATIONSHIP.csv`, `ORA_HZ_GEO_RELATIONSHIP_TYPE.csv`, `ASM_SETUP_CSV_METADATA.xml`.
   An existing zone type row looks like: use `TAX`, `PostalCodeRangeFlag=N`, `CreatedByModule=HZ_GEO_HIERARCHY`, limited by one country (`LimitedByGeographyId`, `GeographyName`, `BoundaryGeographyType=COUNTRY`, `GeographyElement1`), dates `0001/01/01 00:00:00.0` to `4712/12/31 00:00:00.0`.
2. **No REST resource found** for geography types (`geographyTypes`, `taxZoneTypes`, `zoneTypes`: HTTP 404). The CRM `geographies` resource exists but rejected the filter tried (HTTP 400). The after-export is the only check so far.
3. **Builder call used** (new type row + one translation row; the 6 other files header only):
   ```bash
   python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name zone_type_new.zip --prefix <PREFIX> \
     --key "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv=GeographyType" \
     --key "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE_TRANSLATION.csv=ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.GeographyType,Language" \
     --prefix-col "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv=GeographyType" \
     --row "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv|GeographyType=<NAME>|GeographyUse=TAX|PostalCodeRangeFlag=N|CreatedByModule=HZ_GEO_HIERARCHY|GeographyTypeName=<display>|StartDate=0001/01/01 00:00:00.0|EndDate=4712/12/31 00:00:00.0" \
     --row "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE_TRANSLATION.csv|ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.GeographyType=<NAME>|GeographyType=<NAME>|GeographyTypeName=<display>|Language=US|SourceLang=US"
   ```
   Import with `--task-code ZX_MANAGE_TAX_ZONE_TYPES --task-name "Manage Tax Zone Types"` (about 24 s).

## Attempts (2026-11-23, all on `GAPFILL_AB_ZT1`)
| # | What changed | Oracle said | Created? |
|---|---|---|---|
| 1 | no `CreatedByModule`, no country limit | `JBO-27014: Attribute CreatedByModule in GeographyTypeEO is required` | no |
| 2 | + `CreatedByModule=HZ_GEO_HIERARCHY` | row validated (`1 rows processed, 0 failed`) but object `Completed with errors`: `JBO-26041: Failed to post data to database during "Insert"` into `HZ_GEOGRAPHY_TYPES_B`, no database reason given | no (after-export checked) |
| 3 | + country limit: the 4 limit columns copied from the export's existing zone type of the same country | same `JBO-26041` insert error | no (after-export checked) |

Stopped at 3 attempts (the gap rules allow at most 3).

## Batch 3 check (2026-11-23)
The detailed error could not be read by REST: the ESS logs of the 3 import requests are empty and the setup-import process is not reachable by the ESS request ID. Keep the FSCR `ProcessId` printed at import time; it is the only key to the full process log. Status: **cannot do by CSV (as tested)**.

## Next attempt (GUESS, not tested)
1. **Name format.** Existing zone types are mixed case with spaces (for example "<Country> Zone Type"), and geography types may be checked against a lookup or a pattern. Try a NAME with spaces and mixed case that still starts with the prefix text, e.g. `GAPFILL AB ZT2`.
2. **Missing child row.** The insert may need a hierarchy node or relationship type row for the new type (`ORA_HZ_GEO_HIERARCHY_NODE.csv`, `ORA_HZ_GEO_RELATIONSHIP_TYPE.csv`). Create one zone type on the screen in a test environment, export, and copy every row it adds in all 8 CSVs.
3. **Translation row.** Try the package without the translation row, or with `CreatedBy`/`LastUpdatedBy` left empty (they were empty in attempts 1 to 3).
4. Read the full ESS log of the import request (the process log only shows the JBO text) for the ORA- error under `JBO-26041`.

## Rules and limits
1. New records only; never import a full export.
2. This skill never deletes. Failed attempts created nothing (VERIFIED by new exports after attempts 2 and 3: 1 zone type before and after).
3. Tested on one environment (release 11.13.26.10.0). **Not working.**
