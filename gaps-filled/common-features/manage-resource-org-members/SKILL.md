---
skill_id: "gosaas.gap-fills.common-features.manage-resource-org-members"
name: "Manage Resource Organization Members: add a resource (manager or member) to a resource organization by REST crm resourceUsers (GoSaaS gap fill)"
description: "Creates sales resources in a resource organization through the REST resource resourceUsers: a manager that starts a new organization, then members under it. No sign-in account is made (CreateUserAccountFlag false). Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 20, 2026-11-26. Tested live (own test, fresh test). NOT official FSCR."
layer: "pillar"
pillar: "CX"
offering: "Common Features"
task_code: "HZ_MANAGE_RESOURCE_ORGANIZATION_MEMBERS"
task_name: "Manage Resource Organization Members"
dataloader_import_mode: "REST"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "a legal entity and a business unit that existing resources already use (read live)"
side_effects:
  - "Each POST creates a person (worker, type EMP) and a CRM resource. A manager POST with a new organization name also creates that resource organization. No sign-in account is created. There is no delete: end-date the resource on the page if it must go."
---

# Manage Resource Organization Members (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: the task export is refused (task flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-25). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.

## What it is and when to use
A resource organization (for example a sales team) has one manager and members. The REST resource `resourceUsers` (crm, VERIFIED: actions create, get, update) creates a resource and places it in an organization in one call:
- a **manager** (a role with ManagerFlag Y, such as `SALES_MANAGER`) with a new `ResourceOrganizationName` creates that organization (VERIFIED);
- a **member** (a role with MemberFlag Y, such as `SALES_REPRESENTATIVE`) needs `ResourceParentOrganizationName` = the organization (VERIFIED).
Use it to load sales teams from a list.

## Placeholders
```text
FSCR = the FSCR root folder (holds core\ and the filled-in core\auth\fusionEnv.properties). Read only.
W    = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's REST client; never prints the server)
RUN  = a NEW empty work folder OUTSIDE FSCR and outside any git repo
C    = /crmRestApi/resources/11.13.18.05
ORG  = the organization name (test: starts with your prefix, e.g. GAPFILL_AB_...)
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. Never print tokens, the server address or user names.

## Step 1. Read the values you need (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceRoles --query onlyData=true --query limit=200 --query fields=RoleCode,RoleName,ManagerFlag,MemberFlag --no-open-browser --output roles.json > roles.log 2>&1
python -B "<W>" "<FSCR>" <C>/resourceUsers --query onlyData=true --query limit=50 --query fields=LegalEntity,BusinessUnit --no-open-browser --output ru.json > ru.log 2>&1
```
Pick a manager role (`ManagerFlag` true) and a member role (`MemberFlag` true); the API gives true/false. Pick the LegalEntity and BusinessUnit pair that most existing resources use (2026-11-26: `GS Legal Entity` / `GoSaaS`, 4 of 7 rows). Check every new name gives 0 rows:
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --query "q=LastName='<name>' or ResourceOrganizationName='<ORG>'" --query onlyData=true --query fields=LastName --no-open-browser --output pre.json > pre.log 2>&1
```
Pass absolute paths to `--body-file` and `--output` if your shell may change folder (VERIFIED with absolute Windows paths).

## Step 2. Create the manager (makes the organization, VERIFIED)
`mgr.json`:
```json
{"FirstName": "GAPFILL", "LastName": "<PREFIX>_RM1", "ResourceEmail": "<prefix>.rm1@example.invalid", "PersonType": "EMP",
 "LegalEntity": "<LE>", "BusinessUnit": "<BU>", "CreateUserAccountFlag": false,
 "ResourceOrganizationName": "<ORG>", "ResourceOrgRoleCode": "SALES_MANAGER", "ResourceStartDate": "<today>"}
```
```bash
python -B "<W>" "<FSCR>" <C>/resourceUsers --method POST --body-file mgr.json --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" --no-open-browser --output mgr_out.json > mgr.log 2>&1
```
POST ONCE. If the connection drops, run the Step 4 GET before trying again. The answer has `ResourceProfileId`.
Note (VERIFIED in the fresh test): a manager sent with no `ResourceParentOrganizationName` showed `null` in the POST answer, but a parent organization later in the read-back. Always send the parent you want (Step 2 of manage-resource-org-hierarchies); check it in Step 4.

## Step 3. Add a member (VERIFIED)
`mem.json`: copy `mgr.json` (keep FirstName, PersonType, LegalEntity, BusinessUnit, CreateUserAccountFlag, ResourceStartDate, `ResourceOrganizationName` = `<ORG>`), then change LastName and email, set `"ResourceOrgRoleCode": "SALES_REPRESENTATIVE"` and add `"ResourceParentOrganizationName": "<ORG>"`.
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --method POST --body-file mem.json --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" --no-open-browser --output mem_out.json > mem.log 2>&1
```
POST once.

## Step 4. Read back (VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --query "q=ResourceOrganizationName='<ORG>'" --query onlyData=true --query fields=LastName,ResourceOrganizationName,ResourceParentOrganizationName,ResourceOrgRoleCode,UserStatus --no-open-browser --output rb.json > rb.log 2>&1
```
Expect the manager and each member, with their role codes; `UserStatus` empty (no sign-in account).

## Errors seen (VERIFIED, nothing was created by any of them)
| Message | Cause | Fix |
|---|---|---|
| HZ-120845 (ResourceOrgRoleCode required) | no role in the body | add `ResourceOrgRoleCode` |
| HZ-120896 (manager email or parent organization required for a nonmanager) | member role, no organization link | add `ResourceParentOrganizationName` |
| HZ-120839 (manager not active or not in the hierarchy) | `ResourceOrgManagerEmail` pointed at a new manager without a user | use `ResourceParentOrganizationName` instead |

## Rules and limits
1. Always `CreateUserAccountFlag: false` for a test, and `example.invalid` emails: no sign-in account, no mail sent.
2. Never add people to an organization you did not create.
3. No delete by REST. Test records stay; end-date them on the page if needed.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused, task flag `CSVExportImportSupportedFlag N` |
| Own test | manager `GAPFILL_AB_B20_RM1` (SALES_MANAGER) made organization `GAPFILL_AB_B20_ORG1`; member `GAPFILL_AB_B20_RM2` (SALES_REPRESENTATIVE) added; read back 2 rows, no user accounts; resources 4 -> 6 |
| Fresh test | see STATUS.md (`fresh_claude_pass`) |
