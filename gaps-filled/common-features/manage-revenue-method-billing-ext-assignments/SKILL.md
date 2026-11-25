---
skill_id: "gosaas.gap-fills.common-features.manage-revenue-method-billing-ext-assignments"
name: "Manage Revenue Methods: Billing Extension Assignments: create a new extension-based revenue method with one billing extension assigned (GoSaaS gap fill)"
description: "Creates one NEW revenue method (BillMethodFlag R) with its translation row and one billing extension assignment through FSCR's setup-task CSV export/import of PJB_MANAGE_REVENUE_METHOD_BILLING_EXTENSION_ASSIGNMENTS, following the invoice-method gap skill with R values. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 12, 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "PJB_MANAGE_REVENUE_METHOD_BILLING_EXTENSION_ASSIGNMENTS"
task_name: "Manage Revenue Methods: Billing Extension Assignments"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "tested (batch 12)"
depends_on:
  - "gap skill manage-invoice-method-billing-ext-assignments (all steps; same package)"
  - "PJB_MANAGE_BILLING_EXTENSIONS (gap skill manage-billing-extensions: an extension with CallingProcess R)"
side_effects:
  - "Creates one new revenue method (active) and one assignment of an extension to it. Nothing uses a new method until a contract or bill plan names it."
---

# Manage Revenue Methods: Billing Extension Assignments (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV); it has no skill or guide.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
A **revenue method** says how revenue amounts are found; an extension-based one calls billing extensions. This task's CSV package is the **same 3 files** as the invoice-method task (method, translation, assignments), filtered to revenue methods (VERIFIED: the revenue export lists only `R` methods, the invoice export only `I` methods).
**Read and follow the gap skill `manage-invoice-method-billing-ext-assignments` (same folder level as this skill), Steps 1 to 6, with these values instead:**

```text
TASK     = PJB_MANAGE_REVENUE_METHOD_BILLING_EXTENSION_ASSIGNMENTS
TASKNAME = Manage Revenue Methods: Billing Extension Assignments
FLAG     = R
EXT      = an existing billing extension with CallingProcess R (Revenue)   (its Prerequisite 1 with R)
METHOD   = a new revenue method name starting with your PREFIX
```
Use the same build command (with `BillMethodFlag=R` in all 3 rows), the same rule **leave `ProcessingOrder` empty**, the same import, log check and 3-file export compare. **Safety:** NEW methods only; never add an assignment to an existing revenue method.

## Differences seen (VERIFIED)
- None in columns or rules. Oracle again set `MethodCfgType=EXTENSION_BASED` and `TransactionCode=BILLING_EVENT`.
- Fresh tests of the invoice and revenue tasks share the package: run them one after the other, not at the same time.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B12_RM1` + extension `GAPFILL_AB_B10_BX3F` (Revenue), no ProcessingOrder (ProcessId 100004744396782) | 1 row processed, 0 failed; compare PASS (3 files, 1 added each; the first after-export failed on a network drop, re-run into a new folder) |
| fresh test | see CHANGELOG.md | |
