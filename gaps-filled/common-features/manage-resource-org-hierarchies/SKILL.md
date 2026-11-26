---
skill_id: "gosaas.gap-fills.common-features.manage-resource-org-hierarchies"
name: "Manage Resource Organization Hierarchies: put a resource organization under a parent organization by REST crm resourceUsers (GoSaaS gap fill)"
description: "Builds the resource organization hierarchy through the REST resource resourceUsers: a manager POST with a new organization name and ResourceParentOrganizationName creates the child organization under the parent. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 20, 2026-11-26. Tested live (own test, fresh test). NOT official FSCR."
layer: "pillar"
pillar: "CX"
offering: "Common Features"
task_code: "HZ_MANAGE_RESOURCE_ORGANIZATION_HIERARCHIES"
task_name: "Manage Resource Organization Hierarchies"
dataloader_import_mode: "REST"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "gosaas.gap-fills.common-features.manage-resource-org-members (a parent organization with a manager)"
side_effects:
  - "The POST creates a person (worker, EMP), a CRM resource, and the child resource organization under the parent. No sign-in account. No delete by REST."
---

# Manage Resource Organization Hierarchies (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: the task export is refused (task flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-25). No hierarchy resource exists: crm `resourceOrganizationHierarchies` and `resourceHierarchies` give 404 (VERIFIED 2026-11-26). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.

## What it is and when to use
Resource organizations form a tree (a sales region over its teams). Oracle builds the tree from the managers: a manager placed with `ResourceParentOrganizationName` = the parent makes its own organization a child of the parent. The REST resource `resourceUsers` (crm, create, get, update) does it in one POST (VERIFIED).
Use it to load a sales organization tree, top level first.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\ and core\auth\fusionEnv.properties). Read only.
W      = <GAPS>/common-features/scripts/rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo
C      = /crmRestApi/resources/11.13.18.05
PARENT = an existing resource organization with a manager (made with manage-resource-org-members)
CHILD  = the new organization name
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. Never print tokens, the server address or user names.

## Step 1. Check (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --query "q=ResourceOrganizationName='<PARENT>'" --query onlyData=true --query fields=LastName,ResourceOrgRoleCode --no-open-browser --output parent.json > parent.log 2>&1
python -B "<W>" "<FSCR>" <C>/resourceUsers --query "q=ResourceOrganizationName='<CHILD>' or LastName='<new name>'" --query onlyData=true --query fields=LastName --no-open-browser --output pre.json > pre.log 2>&1
```
The parent must have a row with a manager role; `pre.json` must have 0 items. Take the manager role, LegalEntity and BusinessUnit as in manage-resource-org-members Step 1. Pass absolute paths to `--body-file` and `--output` if your shell may change folder.

## Step 2. Create the child organization under the parent (VERIFIED)
`child.json`:
```json
{"FirstName": "GAPFILL", "LastName": "<PREFIX>_RM3", "ResourceEmail": "<prefix>.rm3@example.invalid", "PersonType": "EMP",
 "LegalEntity": "<LE>", "BusinessUnit": "<BU>", "CreateUserAccountFlag": false,
 "ResourceOrganizationName": "<CHILD>", "ResourceParentOrganizationName": "<PARENT>",
 "ResourceOrgRoleCode": "SALES_MANAGER", "ResourceStartDate": "<today>"}
```
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --method POST --body-file child.json --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" --no-open-browser --output child_out.json > child.log 2>&1
```
POST ONCE; if the connection drops, read back first.

## Step 3. Read back (VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --query "q=ResourceOrganizationName='<CHILD>'" --query onlyData=true --query fields=LastName,ResourceOrganizationName,ResourceParentOrganizationName,ResourceOrgRoleCode,UserStatus --no-open-browser --output rb.json > rb.log 2>&1
```
Expect the new manager with `ResourceOrganizationName` = CHILD, `ResourceParentOrganizationName` = PARENT and `UserStatus` empty.

## Rules and limits
1. Only build under a parent you created; never move or re-parent someone else's organization (that would be an edit).
2. `CreateUserAccountFlag: false` and `example.invalid` emails for tests.
3. No delete by REST.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused, task flag `CSVExportImportSupportedFlag N` |
| REST names | `resourceOrganizationHierarchies`, `resourceHierarchies` 404 |
| Own test | manager `GAPFILL_AB_B20_RM3` made `GAPFILL_AB_B20_ORG2` under parent `GAPFILL_AB_B20_ORG1`; read back: parent `GAPFILL_AB_B20_ORG1` |
| Fresh test | see STATUS.md (`fresh_claude_pass`) |
