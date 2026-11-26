---
skill_id: "gosaas.gap-fills.common-features.publish-account-hierarchies"
name: "Publish Account Hierarchies (Select Aggregation Options for Account Hierarchies): read the account hierarchy trees by FSM CSV; publish by scheduled process (GoSaaS gap fill, written, unsafe to test)"
description: "Reads the account hierarchy trees and tree versions that the task publishes, through the task's FSM CSV export (the trees package), and documents how the publish step (balances cube hierarchy) is run. The publish was not run: it writes the hierarchy into the shared GL balances cubes and cannot be undone. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 23, 2026-11-26. Export VERIFIED; publish not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_SELECT_AGGREGATION_OPTIONS_FOR_ACCOUNT_HIERARCHIES"
task_name: "Publish Account Hierarchies"
dataloader_import_mode: "FSM CSV (read) + scheduled process (publish)"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "gosaas.gap-fills.common-features.manage-trees-and-tree-versions (the tree and an ACTIVE tree version to publish)"
  - "gosaas.gap-fills.common-features.manage-account-hierarchies"
side_effects:
  - "Step 4 (not run) publishes the tree version as a hierarchy of the account dimension in every balances cube whose chart of accounts uses the tree's value set. Reports and Financial Reporting of all ledgers on that chart see it. There is no unpublish by CSV or REST."
---

# Publish Account Hierarchies (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.
> **Status: written, unsafe to test.** The publish changes the shared GL balances cubes of a chart of accounts and cannot be put back.

## What it is and when to use
After an account hierarchy (a tree on the chart of accounts value set) has an active version, *Publish Account Hierarchies* (task code `GL_SELECT_AGGREGATION_OPTIONS_FOR_ACCOUNT_HIERARCHIES`) sends it to the GL balances cubes so balances roll up by the hierarchy; the aggregation option chooses whether the tree version is published to the cube and kept up to date.
- **FSM CSV (VERIFIED 2026-11-26):** the task's export works and is the **trees package** (5 files: `FND_APP_TREE`, `ORA_FND_APP_TREE_VERSION`, `ORA_FND_APP_TREE_VERSION_NODE`, `ORA_FND_APP_TREE_DATA_SOURCE_LABEL`, `ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER`; scope module GL, `moduleType APPLICATION`). It has **no** publish or aggregation column: it creates trees, which the tested gap skill manage-trees-and-tree-versions already does.
- **REST (VERIFIED 404):** `accountHierarchies`, `publishAccountHierarchies`, `treeVersions`, `accountHierarchyPublications`. `erpintegrations` exists (it can submit scheduled processes).

## Why it is unsafe to test here
1. Publishing writes the hierarchy into the balances cube of every chart of accounts that uses the tree's value set; on a shared environment these are real ledgers' cubes.
2. There is no unpublish or delete route by CSV or REST, so it cannot be put back by test-and-restore.
3. A new prefix tree nobody uses does not help: the cube is shared, not the tree.
What would make it safe: an environment with its own test chart of accounts (own value set, own ledger and cube), with written approval.

## Placeholders
```text
FSCR = the FSCR root folder. Read only.
RUN  = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
TREE = the account hierarchy tree code; VER = its active tree version name
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. Never print tokens, the server address or user names; never print `ASM_SETUP_CSV_METADATA.xml`.

## Prerequisites
1. The tree and an ACTIVE version (manage-trees-and-tree-versions; status shows in `ORA_FND_APP_TREE_VERSION.csv`, column `Status`).
2. The chart of accounts that uses the tree's value set has a balances cube (created with the ledger).

## Step 1. Read-only export (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code GL_SELECT_AGGREGATION_OPTIONS_FOR_ACCOUNT_HIERARCHIES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/e1" > "<RUN>/e1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/e1"
python -I -c "import csv,sys; [print(r['TreeStructureCode'],r['TreeCode'],r['TreeVersionName'],r['Status']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_FND_APP_TREE_VERSION.csv',encoding='utf-8-sig')) if r['TreeStructureCode']=='GL_ACCT_FLEX']" "<RUN>/e1/unz"
```
Lists the account hierarchy tree versions and their status (2026-11-26: 49 trees in the package).

## Step 2. Make or change the tree (VERIFIED, other skill)
Use manage-trees-and-tree-versions; this task's package is the same.

## Step 3. Publish (GUESS, owned environment only)
Run the scheduled process **Publish Account Hierarchies** for `<TREE>` / `<VER>` (on the page: Publish Account Hierarchies, select the version, Publish). By script: REST `erpintegrations` `submitESSJobRequest` with the process's job package and definition (not published; read them once on the Scheduled Processes page) and the tree and version as parameters. Keep the request id; check it with `erpintegrations?finder=ESSJobStatusRF;requestId=<id>`.

## Step 4. Read back (GUESS)
The process ends Succeeded; the hierarchy appears in Financial Reporting / Smart View for the chart's cube.

## Rules and limits
1. Never publish on a shared environment.
2. Never change a tree you did not create.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Export | works: 5 files, trees package, no publish column (VERIFIED) |
| REST | 4 names 404; `erpintegrations` 200 |
| Publish | not run (unsafe) |
