---
skill_id: "gosaas.gap-fills.common-features.manage-custom-ess-lov-sources-crm"
name: "Manage Enterprise Scheduler Job Definitions and Job Sets for Customer Relationship Management and Related Applications: create a job-parameter list-of-values source by CSV (GoSaaS gap fill)"
description: "Creates one NEW Enterprise Scheduler list-of-values source through FSCR's setup-task CSV export/import of ORA_ATK_CUSTOM_ESS_CRM, following the FSCM gap skill with this task code. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 12, 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ATK_CUSTOM_ESS_CRM"
task_name: "Manage Enterprise Scheduler Job Definitions and Job Sets for Customer Relationship Management and Related Applications"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "tested (batch 12)"
depends_on:
  - "gap skill manage-custom-ess-lov-sources-fscm (all steps; same package)"
side_effects:
  - "Creates one new list-of-values source; nothing uses it until a job parameter picks it."
---

# Manage Enterprise Scheduler Job Definitions and Job Sets for Customer Relationship Management and Related Applications (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV); it has no skill or guide.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
This task's CSV package is the **same** one as the FSCM task `ORA_ATK_CUSTOM_ESS_FSCM`: one file, `ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv`, with the same rows (VERIFIED: the three task exports were identical, 98 rows each, before our tests). It holds the Enterprise Scheduler job-parameter list-of-values sources; job definitions and job sets are not in it.
**Read and follow the gap skill `manage-custom-ess-lov-sources-fscm` (same folder level as this skill), Steps 1 to 6, with only these values changed:**
```text
TASK     = ORA_ATK_CUSTOM_ESS_CRM
TASKNAME = Manage Enterprise Scheduler Job Definitions and Job Sets for Customer Relationship Management and Related Applications
```
Everything else (LOVNAME with your prefix, DSDEF from an existing row, the 5 values, the import, the log check, the export compare) is the same. **Safety:** NEW sources only; never re-import an existing source. Tests of the three ESS tasks share the package: run them one after the other.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B12_LOV2` (ProcessId 100004743426095) | 1 row processed, 0 failed; compare PASS (99 -> 100, 1 added) |
| fresh test | see CHANGELOG.md | |
