---
skill_id: "gosaas.gap-fills.common-features.manage-tax-geographies"
name: "Manage Tax Geographies: set tax use on a country's geography structure; route through the shared master geography (GoSaaS gap fill, written, unsafe to test)"
description: "Documents how the tax side of the master geography is set (which geography types of a country are used for tax, tax zones). There is no own record to create: the task changes the structure of existing countries that all addresses and tax rules use. Not run. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 24, 2026-11-27. Route from REST describe and Oracle docs; not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_GEOGRAPHIES"
task_name: "Manage Tax Geographies"
dataloader_import_mode: "REST (Import Management)"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "gosaas.gap-fills.common-features.load-geography-interface-data (same import route)"
side_effects:
  - "Any change (not run) alters how an existing country's geography is used for tax: tax jurisdictions and tax rules of every legal entity and business unit in that country read it. No undo by CSV or REST."
---

# Manage Tax Geographies (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.
> **Status: written, unsafe to test.**

## What it is and when to use
Oracle docs ("Place Information"): tax uses the shared master geography. On *Manage Tax Geographies* you pick, for each country, which geography types (state, county, city, postal code) tax uses, and you keep tax zones. It is a view of the master geography, not a separate object.

## What was seen (2026-11-26)
1. FSM CSV: task export refused (flag `CSVExportImportSupportedFlag N`, VERIFIED).
2. REST: `crm geographies` is get only and lists countries only (attributes `GeographyId`, `GeographyCountry`, `GeographyCountryCode`; VERIFIED); `taxGeographies` 404 (VERIFIED).
3. The only write route is the master geography import (Import Management object `GeographyInterface`, see load-geography-interface-data), which has an open file-reference point and is itself unsafe.

## Why it is unsafe to test here
1. There is no new record to make with a prefix: the task changes existing countries' structure and tax use.
2. Tax jurisdictions, tax rules and address validation of all real business units in that country read it; there is no undo.
What would make it safe: an environment the customer owns, with written approval, and a country they do not trade in.

## Steps (GUESS, owned environment only)
1. Read the country: `GET /crmRestApi/resources/11.13.18.05/geographies?q=GeographyCountryCode='<CC>'` (VERIFIED read).
2. Load or change the country's geography rows with the GeographyInterface import (load-geography-interface-data, Steps 1 to 4).
3. Set the tax use of the geography types on the page (no REST field found).

## Rules and limits
1. Never change a country used by a real legal entity or business unit.
2. No delete.
