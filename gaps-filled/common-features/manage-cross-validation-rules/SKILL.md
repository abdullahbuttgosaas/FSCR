---
skill_id: "gosaas.gap-fills.common-features.manage-cross-validation-rules"
name: "Manage Cross-Validation Rules: create rules with the Cross-Validation Rules Import (FBDI zip + Load Interface File for Import) (GoSaaS gap fill, written, unsafe to test)"
description: "Creates, changes or deletes chart of accounts cross-validation rules from the FBDI template Cross-Validation Rules Import (interface GL_CROSS_VALIDATION_RULES_INT), uploaded with Upload Rules on the task page or with erpintegrations importBulkData. Not run: a rule on a shared chart of accounts blocks account combinations for every ledger on it, and Replace mode deletes every rule that is not in the file. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 24, 2026-11-27. Route from Oracle docs; not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_CROSS-VALIDATION_RULES"
task_name: "Manage Cross-Validation Rules"
dataloader_import_mode: "FBDI"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "the FBDI template Cross-Validation Rules Import (File-Based Data Import for Financials guide)"
side_effects:
  - "Step 3 (not run) adds or changes rules on the chart of accounts structure instance. An enabled rule stops new account combinations that break it, for every ledger and user on that chart. Replace mode deletes every rule missing from the file."
---

# Manage Cross-Validation Rules (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live 2026-11-25/26 · **DOCS** = read in Oracle's docs 2026-11-27 · **GUESS** = not run live.
> **Status: written, unsafe to test.**

## What it is and when to use
Cross-validation rules stop bad account combinations (for example a company with a cost center it does not own). They belong to a chart of accounts structure instance.
- **FSM CSV (VERIFIED 2026-11-26):** the task's export works but is the chart of accounts key flexfield package (7 files: flexfield, structures, instances, segments, labels); it holds no rule file. Loading it would only touch the chart's structures.
- **REST (VERIFIED 404, 2026-11-25):** `crossValidationRules`, `glCrossValidationRules`, `accountCombinationsCrossValidationRules`.
- **FBDI (DOCS):** Oracle's *Cross-Validation Rules Import* template loads the interface `GL_CROSS_VALIDATION_RULES_INT`. It creates, updates and deletes rules. Two modes: **Increment** (changes only the rules in the file) and **Replace** (the file is the full set; rules not in the file are deleted). On the page: Manage Cross-Validation Rules > Actions > **Upload Rules**, which runs *Load Interface File for Import*.

## Why it is unsafe to test here
1. A rule is attached to a shared chart of accounts instance. Once enabled it blocks combinations for all ledgers and users on that chart; no own test chart exists here.
2. One wrong mode (Replace) deletes all existing rules of the chart.
3. A disabled prefix rule would block nothing, but it still changes the shared chart's rule list and was not needed to prove anything the docs do not already say.
What would make it safe: an environment with its own test chart of accounts (own value sets, own structure instance), with written approval; always Increment mode.

## Placeholders
```text
COA  = the chart of accounts structure instance code
RULE = new rule name = PREFIX + short name
```

## Steps (GUESS, owned environment only)
1. Download the template *CrossValidationRulesImport* (File-Based Data Import for Financials guide, or Manage Cross-Validation Rules > Actions > Download Template).
2. Fill one row: `<COA>`, `<RULE>`, description, **enabled N**, condition filter and validation filter, error message. Generate the zip on the template's Instructions and CSV Generation tab.
3. Upload with **Increment** mode: on the page, Actions > Upload Rules; or by REST `erpintegrations` `importBulkData` with the zip and the *Load Interface File for Import* job (job name and parameters not read live).
4. Read back on the page (no REST read exists). Errors stay in the interface table: correct the spreadsheet and load again.

## Rules and limits
1. Never use Replace mode on a shared chart.
2. Load a new rule disabled first; enable only after review.
3. Never change a rule you did not create.

## Sources (DOCS)
Oracle Help Center, Implementing General Ledger: "How Cross-Validation Rules Import Data Is Processed", "Manage Cross-Validation Rules Import".
