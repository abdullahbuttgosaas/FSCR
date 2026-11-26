---
skill_id: "gosaas.gap-fills.common-features.run-geography-loader"
name: "Run Geography Loader: load master geography data by file import (crm importActivities) (GoSaaS gap fill, written, unsafe to test)"
description: "Loads countries' geography data (states, cities, postal codes) into the master geography through a file import activity (REST crm importActivities). Not run: master geography is shared reference data used by every address and tax, and has no delete. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 21, 2026-11-26. Route from Oracle docs and REST describe; not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "CX"
offering: "Common Features"
task_code: "HZ_RUN_GEOGRAPHY_LOADER"
task_name: "Run Geography Loader"
dataloader_import_mode: "REST"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "HZ_LOAD_GEOGRAPHY_INTERFACE_DATA (the country's geography structure)"
side_effects:
  - "Step 3 (not run) adds geographies to the master geography of the environment; every address entry, address validation and tax jurisdiction sees them. No delete."
---

# Run Geography Loader (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: task export refused (flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-26). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.
> **Status: written, unsafe to test.** Even a test geography with our prefix would show in every user's address lists (country, state, city) and could be picked on real addresses; geographies cannot be deleted.

## What it is and when to use
The geography loader fills the master geography from a file (Oracle docs: file-based import of the Geography object into the interface `HZ_IMP_GEOGRAPHIES_T`, then the loader). REST `crm importActivities` (VERIFIED: create, get, update, upsert; collection GET 200) creates and runs a file import activity. Use it at go-live for countries whose geography Oracle does not deliver.

## Why it is unsafe to test here
1. Master geography is shared reference data: everyone's address entry and validation uses it.
2. No delete: a wrong row stays.
What would make it safe: an environment the customer owns, their country file, their written approval.

## Placeholders
```text
FSCR, W, RUN = as in import-worker-users
C    = /crmRestApi/resources/11.13.18.05
FILE = the geography CSV (country code, level, name, parent; GUESS for the columns: take them from the Geography import object's mapping)
```

## Step 1. Check the route (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/importActivities --query limit=1 --query onlyData=true --query fields=Name,ObjectCode,Status --no-open-browser --output ia.json > ia.log 2>&1
```

## Step 2. Build the file (GUESS)
One row per geography, parents before children; country structure must exist (task Manage Geographies).

## Step 3. Create and run the import activity ONCE (GUESS, owned environment only)
POST `<C>/importActivities` with `Name`, `ObjectCode` for Geography, the file as an attachment, and `ActivateFlag`; write down the activity id.

## Step 4. Read back (GUESS)
GET the activity until its `Status` is completed; check the new geographies in Manage Geographies.

## Rules and limits
1. Never load geography on a shared environment.
2. One run per file; never load the same file twice.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused, flag N |
| REST | `importActivities` GET 200, describe create/get/update/upsert (VERIFIED); `geographyImportActivities` 404 |
| Load | not run (unsafe) |
