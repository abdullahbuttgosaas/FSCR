---
skill_id: "gosaas.gap-fills.common-features.view-service-clients"
name: "View Service Clients (GoSaaS gap fill)"
description: "Show which client business units a service-provider business unit serves, and for which business function pair, without a screen: FSCR's read-only setup-task CSV export of FUN_VIEW_SERVICE_CLIENTS plus the finBusinessUnitsLOV REST resource. Read only: creates and changes nothing. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 05, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FUN_VIEW_SERVICE_CLIENTS"
task_name: "View Service Clients"
dataloader_import_mode: "FSM"
type: "export"
execution_mode: "read-only"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "gosaas common-features/manage-docseq-categories/scripts/rest_read.py (generic REST read)"
  - "gosaas common-features/search-legal-entities/scripts/view_record.py (export viewer, hides person columns)"
side_effects:
  - "Starts one setup-task CSV export process (read-only for Fusion data). Nothing is created or changed."
---

# View Service Clients (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
In shared-service setups one business unit (the **provider**) does work, such as payables invoice processing or procurement, for other business units (the **clients**). "View Service Clients" only **shows** these provider-client relationships. There is nothing to create. Use this skill when someone asks "which business units does BU X serve", "who provides services to BU Y", or wants a read-only check before a procurement or payables setup step.
- Do **not** use it to add or change service provider relationships (that is a separate "Manage Service Provider Relationships" task and changes how documents are routed).

## Placeholders
```text
FSCR   = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS   = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H      = <GAPS>/common-features/manage-docseq-categories/scripts   (rest_read.py)
V      = <GAPS>/common-features/search-legal-entities/scripts/view_record.py
RUN    = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
BU     = the business unit name the person asks about
```

## Sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; `timeout 120` before REST reads. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens, headers, the server address or user names.

## Prerequisites
None (read access to business units).

## Step 1. Check the business unit name by REST
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource finBusinessUnitsLOV \
  --q "BusinessUnitName='<BU>'" --fields BusinessUnitName,ActiveFlag,ProfitCenterFlag \
  --out "<RUN>/bu.json" --expect-count 1
```
`READBACK: PASS` = the name is exact and the unit exists (VERIFIED). For a search use `--q "BusinessUnitName LIKE '%<part>%'"` without `--expect-count` (REST `LIKE` is case-sensitive, VERIFIED).

## Step 2. Read-only export (about 2 minutes)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FUN_VIEW_SERVICE_CLIENTS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export"
```
Expect 5 files (VERIFIED, about 125 s): `FUN_BU_SERVICE_PROVIDERS.csv` (the relationships: `ClientBuName`, `ProviderBuName`, `UpstreamFunctionId`, `DownstreamFunctionId`, `ActiveFlag`), `FUN_BU_USAGE.csv` (which business functions each BU uses), `FUN_BUSINESS_UNIT.csv` (the units; it also holds **manager person names**), an `LE_<number>.csv` reference-data-set assignment file, and `ASM_SETUP_CSV_METADATA.xml`. If the export drops, retry into a new folder, one at a time, up to 3 tries.

## Step 3. Show the clients of one provider (and the providers of one client)
```bash
python -I "<V>" "<RUN>/export/unz" --value "<BU>" --file FUN_BU_SERVICE_PROVIDERS.csv \
  --cols ClientBuName,ProviderBuName,UpstreamFunctionId,DownstreamFunctionId,ActiveFlag --out "<RUN>/clients.txt"
```
- A row with `ProviderBuName=<BU>` = BU serves `ClientBuName` for that function pair. A row with `ClientBuName=<BU>` = BU is served by `ProviderBuName`. A row where both are the same BU = the unit serves itself (normal). VERIFIED
- `ActiveFlag=N` rows are ended relationships. VERIFIED (a few exist)
- The function ids are seeded business function numbers; the pairs seen were 10/20, 10/110, 120/110 and 30/40 (VERIFIED). Their names are not in the export (GUESS: they are the business functions of the "Manage Service Provider Relationships" screen). Report the numbers as they are.
- Leave out `--cols` to see the organization codes too. Never print `FUN_BUSINESS_UNIT.csv` with another tool than `view_record.py`: that file holds person names, which the viewer hides.

## Build rows / import
None. Read-only task; never import anything for it.

## Read back
Step 1 (the BU exists) and Step 3 (its relationship rows) are the read-back.

## Rules and limits
1. Read only. Never re-import this export.
2. Keep RUN outside git (person names, organization codes and audit user names are in the files).
3. Tested on one environment (release 11.13.26.10.0): 276 relationship rows, 186 business units.

## Worked example (VERIFIED, 2026-11-25)
| Step | Result |
|---|---|
| REST `finBusinessUnitsLOV` | the named BU, active |
| Export | 5 files, 276 relationships, about 125 s |
| View | 3 rows for the BU: it serves one other BU (2 function pairs) and itself (1 pair), all active |
