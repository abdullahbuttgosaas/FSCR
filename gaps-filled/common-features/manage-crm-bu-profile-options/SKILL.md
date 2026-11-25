---
skill_id: "gosaas.gap-fills.common-features.manage-crm-bu-profile-options"
name: "Manage Common CRM Business Unit Profile Options (GoSaaS gap fill, written, not load-tested)"
description: "Read, and when a person approves it, change the SITE value of the seeded option HZ_ENABLE_MULTIPLE_BU_CRM (Multiple Business Units Enabled) through FSCR's setup-task CSV export/import of ORA_ZCA_MANAGE_COMMON_CRM_BUSINESS_UNIT_PROFILE_OPTIONS. WRITTEN ONLY: the import was not run because it switches multiple-BU behaviour for all CRM users. Short card over manage-search-profile-options. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 06, 2026-11-25. Export and REST reads seen live on one test environment; the import was NOT run (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZCA_MANAGE_COMMON_CRM_BUSINESS_UNIT_PROFILE_OPTIONS"
task_name: "Manage Common CRM Business Unit Profile Options"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "gosaas common-features/manage-search-profile-options (the full steps this card follows)"
side_effects:
  - "Reads are safe. The import (not run) changes a seeded SITE value for every user; turning multiple business units on in CRM is hard to undo once data is created per BU (GUESS)."
---

# Manage Common CRM Business Unit Profile Options (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** Short card: follow `../manage-search-profile-options/SKILL.md` (placeholders, Step 1 sign-in, prerequisites, Steps 2 to 6 and rules) with the values below.
> **Status: written, not load-tested.** Export and REST reads VERIFIED (2026-11-25); the import was **not** run: it changes a seeded setting that every CRM user gets. Import steps are GUESS.

## What it is and when to use
The task has one seeded option in its export scope, mode `edit` (VERIFIED, from `ASM_SETUP_CSV_METADATA.xml`):
| Option | Application | User name | SITE value seen |
|---|---|---|---|
| `HZ_ENABLE_MULTIPLE_BU_CRM` | HZ | Multiple Business Units Enabled | `N` (VERIFIED) |
`Y` lets CRM objects (accounts, opportunities, and so on) be kept per business unit. Use the card to read the value (safe), or to set it on an environment you own with written approval. Oracle's guides treat switching it on as a one-way implementation decision (GUESS: data then gets BU values that turning it off does not remove).

## Differences from the full skill
| Full skill step | Here |
|---|---|
| OPTION | `HZ_ENABLE_MULTIPLE_BU_CRM` |
| Step 2 (REST) | same two calls; VERIFIED: 1 option row (HZ), SITE value `N` |
| Step 3 (export) | `--task-code ORA_ZCA_MANAGE_COMMON_CRM_BUSINESS_UNIT_PROFILE_OPTIONS`; VERIFIED (about 45 s): the same 4 files, 0 rows (seeded option left out) |
| Step 4 (rows) | parent row from REST unchanged + value row `LevelName=SITE`, `LevelValue=SITE`, `ProfileOptionValue=Y` or `N` (GUESS) |
| Step 5 (import) | `--task-code ORA_ZCA_MANAGE_COMMON_CRM_BUSINESS_UNIT_PROFILE_OPTIONS --task-name "Manage Common CRM Business Unit Profile Options"` (GUESS: not run) |
| Step 6 (read back) | REST site value = NEWVAL |

## Rules and limits
1. Never change this option on a shared environment for a test. Changing it on an environment you own needs written approval and a plan for existing CRM data.
2. Note the old value before any change.
3. Not tested: the import. Reads seen on one environment (release 11.13.26.10.0).
