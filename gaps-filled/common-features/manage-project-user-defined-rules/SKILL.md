---
skill_id: "gosaas.gap-fills.common-features.manage-project-user-defined-rules"
name: "Manage User-Defined Rules for Project Management: load approval rules by the FSM CSV package (GoSaaS gap fill, written, unsafe to test)"
description: "Loads user-defined (BPM approval) rules for project management workflows through the task's FSM CSV package. Not run: an upload replaces a workflow's whole rule set, which changes approvals for everyone. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 21, 2026-11-26. Package export VERIFIED (11 files, 0 rows); import not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "PPM"
offering: "Common Features"
task_code: "ORA_PJF_MANAGE_USER_DEFINED_RULES"
task_name: "Manage User-Defined Rules for Project Management"
dataloader_import_mode: "FSM CSV"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "FSCR shared/setup-import (task-level export and import)"
side_effects:
  - "Step 3 (not run) uploads a rule set for a project workflow (for example project or budget approval); Oracle's BPM rule upload replaces the rules of that workflow. No undo."
---

# Manage User-Defined Rules for Project Management (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.
> **Status: written, unsafe to test.** The rules decide who approves projects, budgets and change orders. A rule upload replaces a workflow's rule set (GUESS from Oracle's BPM rule upload behaviour); one wrong file changes approvals for every project user. The export has 0 rows, so there is no existing rule to copy and no own test workflow.

## What it is and when to use
Project workflows (approval of projects, budgets, forecasts, change documents) use BPM rules. The task's FSM CSV package (VERIFIED 2026-11-26: read-only export works, 11 files, all 0 rows) carries the rule sets. Use it to move tested approval rules from a test environment to production.

## Why it is unsafe to test here
1. A rule set is per workflow, not per record: a new rule cannot be added without loading the workflow's whole set.
2. Approvals of other people's projects would change at once.
What would make it safe: an environment the customer owns, the rule set exported from their test environment, their written approval.

## Placeholders
```text
FSCR, RUN = as in the other gap skills; never inside git
TASK      = ORA_PJF_MANAGE_USER_DEFINED_RULES
```

## Step 1. Read-only export (VERIFIED)
`cd "<FSCR>"; python -B shared/setup-import/task-level-export/scripts/export_setup_task_csv.py --task-code <TASK> --token-cache auto --no-open-browser --output-dir "<RUN>/export_before"` (see FSCR's task-level export skill for the exact options). Expect 11 files.

## Step 2. Build the package (GUESS)
Take the package exported from the source environment (same release). Never edit the metadata XML.

## Step 3. Import ONCE (GUESS, owned environment only)
FSCR's task-level import with `--task-code <TASK>`. Write down the ProcessId.

## Step 4. Read back (GUESS)
Export again and compare; then submit a test project for approval and check the approver.

## Rules and limits
1. Never import on a shared environment.
2. Never import twice; if the connection drops, export read-only first.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Export | works: 11 files, 0 rows (VERIFIED) |
| REST | `projectUserDefinedRules` 404; `approvalRules` 400 (not a project rules resource) |
| Import | not run (unsafe) |
