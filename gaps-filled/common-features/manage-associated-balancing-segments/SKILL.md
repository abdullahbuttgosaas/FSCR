---
skill_id: "gosaas.gap-fills.common-features.manage-associated-balancing-segments"
name: "Manage Associated Balancing Segments: assign balancing segment values to a legal entity through the rapid implementation spreadsheet (GoSaaS gap fill, written, unsafe to test)"
description: "Documents how balancing segment values are assigned to a legal entity in a ledger by file: the rapid implementation workbook Create Chart of Accounts, Ledger, Legal Entities, and Business Units in Spreadsheet, uploaded once. Not run: the upload creates or changes ledgers, legal entities and their balancing segment links, which cannot be deleted. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 24, 2026-11-27. Route from Oracle docs and live checks; not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_MANAGE_ASSOCIATED_BALANCING_SEGMENTS"
task_name: "Manage Associated Balancing Segments"
dataloader_import_mode: "spreadsheet upload (rapid implementation)"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "a ledger and a legal entity assigned to it (primary ledger configuration)"
side_effects:
  - "The upload (not run) assigns balancing segment values to a legal entity in a ledger. From then on, journals and subledger accounting of that ledger use the link for intercompany balancing and legal entity reports. No delete by file or REST."
---

# Manage Associated Balancing Segments (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live 2026-11-26 · **DOCS** = read in Oracle's docs · **GUESS** = not run live.
> **Status: written, unsafe to test.**

## What it is and when to use
In a ledger's configuration, each legal entity gets the primary balancing segment values it owns. GL uses this link for intercompany balancing, legal entity reports and the default legal entity on journals.
- **FSM CSV (VERIFIED 2026-11-26, twice):** the task's export is the legal entity package (7 files); no balancing segment file or column.
- **REST (VERIFIED):** `legalEntitiesLOV` is get only; `legalEntityBalancingSegmentValues` 404.
- **File route (DOCS, rapid implementation):** the workbook *Create Chart of Accounts, Ledger, Legal Entities, and Business Units in Spreadsheet* has a legal entity sheet where each legal entity lists its balancing segment values; uploading the generated file creates the chart, ledger, legal entities and these links in one go.

## Why it is unsafe to test here
1. The only file route builds or changes a whole ledger setup (chart of accounts, calendar, ledger, legal entities). These cannot be deleted.
2. Adding a link to an existing real ledger and legal entity changes how that ledger balances journals.
3. A new prefix legal entity alone is not enough: the link needs a ledger, and a new ledger is permanent and shared (balances cube, period statuses).
What would make it safe: a new environment set up only for tests, with written approval.

## Steps (GUESS, owned environment only)
1. Setup and Maintenance > Financials > Define Financials Configuration for Rapid Implementation > *Create Chart of Accounts, Ledger, Legal Entities, and Business Units in Spreadsheet*: download the workbook.
2. Fill the chart, ledger and legal entity sheets; on the legal entity sheet give each legal entity its balancing segment values.
3. Generate the data file and upload it with *Upload Chart of Accounts* and then *Upload Ledger, Legal Entities, and Business Units* (two uploads, in that order).
4. Read back: Manage Primary Ledger > Specify Ledger Options > Assign Balancing Segment Values to Legal Entities, or this task's page.

## Rules and limits
1. Never upload against a real ledger.
2. A balancing segment value belongs to one legal entity per ledger.
