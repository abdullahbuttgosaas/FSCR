---
skill_id: "gosaas.gap-fills.common-features.run-jurisdiction-rates-upload"
name: "Run Jurisdiction and Rates Upload Program: load partner tax content by the scheduled process Import Tax Configuration Content through REST erpintegrations (GoSaaS gap fill, written, unsafe to test)"
description: "Starts Oracle's tax content upload (US sales and use tax jurisdictions, rates and the geography hierarchy from a tax partner file) as a scheduled process through REST erpintegrations. Not run: it changes shared US tax content and geographies and cannot be put back. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 20, 2026-11-26. Route from Oracle docs and REST describe; not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_RUN_JURISDICTION_AND_RATES_UPLOAD_PROGRAM"
task_name: "Run Jurisdiction and Rates Upload Program"
dataloader_import_mode: "ESS"
type: "process"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "a tax partner content file (Vertex or ONESOURCE) from the customer's licence"
side_effects:
  - "Step 3 (not run) creates or updates tax jurisdictions, rates and geographies for the US regime of the whole environment. No undo."
---

# Run Jurisdiction and Rates Upload Program (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: task export refused (flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-26). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.
> **Status: written, unsafe to test.** The program loads a partner's full content file into the shared US tax setup and the master geography; it updates existing records and has no undo.

## What it is and when to use
In Oracle SaaS the task runs the scheduled process **Import Tax Configuration Content** (Oracle docs): it reads a partner file (Vertex or Thomson Reuters ONESOURCE), creates the US state, county and city geographies and the tax jurisdictions and rates for the partner's regime. Use it once at go-live and for each monthly content file. Route: REST `fscm erpintegrations` (VERIFIED by describe: create, get) with `OperationName` `importBulkData` (file upload + process) or `submitESSJobRequest`.

## Why it is unsafe to test here
1. It updates shared tax content and the master geography that every address and tax calculation uses.
2. It needs the customer's licensed partner file.
3. No undo and no delete.
What would make it safe: an environment the customer owns, their file, their written approval.

## Placeholders
```text
FSCR, W, RUN = as in import-worker-users
F    = /fscmRestApi/resources/11.13.18.05
FILE = the partner content zip (customer's)
```

## Step 1. Check the route (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <F>/erpintegrations/describe --no-open-browser --output d.json > d.log 2>&1
```
Expect actions create and get.

## Step 2. Find the job (GUESS)
In Scheduled Processes find "Import Tax Configuration Content"; read its job package and name and its parameters (content provider, file). Write them down.

## Step 3. Upload and run ONCE (GUESS, owned environment only)
POST `<F>/erpintegrations` with `OperationName` `importBulkData`, the file as Base64 `DocumentContent`, `ContentType` zip, and the job package, name and parameters of Step 2. Write down the `ReqstId`.

## Step 4. Read back (GUESS)
GET `<F>/erpintegrations?finder=ESSJobStatusRF;requestId=<ReqstId>` until SUCCEEDED; then check a jurisdiction of the new content in Manage Tax Jurisdictions.

## Rules and limits
1. Never run Step 3 on a shared environment.
2. One run at a time; never run the same file twice while one may still be running.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused, flag N |
| REST | `taxJurisdictions` exists but holds jurisdictions, not the upload program; `erpintegrations` describe: create, get (VERIFIED) |
| Run | not run (unsafe) |
