---
skill_id: "gosaas.gap-fills.common-features.manage-internal-resource-organizations"
name: "Manage Internal Resource Organizations: create a new resource organization by REST crm resourceUsers (GoSaaS gap fill)"
description: "Creates a new internal resource organization (for example a sales team) through the REST resource resourceUsers: one POST of a manager resource with a new ResourceOrganizationName creates the organization with that manager. No sign-in account is made. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 22, 2026-11-26. Tested live (own test, fresh test). NOT official FSCR."
layer: "pillar"
pillar: "CX"
offering: "Common Features"
task_code: "HZ_MANAGE_RESOURCE_ORGANIZATIONS"
task_name: "Manage Internal Resource Organizations"
dataloader_import_mode: "REST"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.2"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "a legal entity and a business unit that existing resources already use (read live, Step 1)"
side_effects:
  - "The POST creates a person (worker, type EMP), a CRM resource and the new resource organization. No sign-in account. There is no delete by REST: end-date the resource on the page if it must go."
---

# Manage Internal Resource Organizations (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: the task export is refused (task flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-26). No resource-organization REST resource (`resourceOrganizations` 404, VERIFIED). Labels: **VERIFIED** = seen live 2026-11-26 · **GUESS** = not run live.

## What it is and when to use
An internal resource organization groups sales resources (a team with a manager). Oracle creates it when a **manager** resource is created with a new organization name: the REST resource `resourceUsers` (crm, actions create, get, update; VERIFIED) does that in one POST. Members and child organizations: see the gap skills manage-resource-org-members and manage-resource-org-hierarchies.

## Placeholders
```text
FSCR = the FSCR root folder (holds core\ and the filled-in core\auth\fusionEnv.properties). Read only.
W    = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's REST client unchanged; never prints the server)
RUN  = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
C    = /crmRestApi/resources/11.13.18.05
ORG  = the new organization name (test: your prefix + short name, e.g. GAPFILL_XX_ORG1)
MGR  = the manager's last name (test: your prefix + short name, e.g. GAPFILL_XX_RM1)
LE, BU = legal entity and business unit names read in Step 1
ROLE = the manager role code (Step 1; normally SALES_MANAGER)
TODAY = today's date, YYYY-MM-DD
```
Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; pass absolute `E:/...` paths to `--body-file` and `--output`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page; a valid cached sign-in returns at once). About one hour; on HTTP 401/403 sign in again. Never print tokens, the server address or user names.

## Prerequisites
1. A manager role: read in Step 1 (a role with `ManagerFlag` true, for example `SALES_MANAGER`).
2. A legal entity and business unit pair already used by resources (Step 1). Nothing else.

## Step 1. Read the values (read only, VERIFIED)
Run every command of Steps 1 to 3 in one shell that stays in `<RUN>` (`cd "<RUN>"` once, then the other lines; the one-liners read relative file names). If a command gives no output file, read the end of its `.log`.
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceRoles --query onlyData=true --query limit=200 --query fields=RoleCode,ManagerFlag,MemberFlag --no-open-browser --output "<RUN>/roles.json" > roles.log 2>&1
python -B "<W>" "<FSCR>" <C>/resourceUsers --query onlyData=true --query limit=100 --query fields=LegalEntity,BusinessUnit --no-open-browser --output "<RUN>/ru.json" > ru.log 2>&1
python -I -c "import json,collections; m=[r['RoleCode'] for r in json.load(open('roles.json',encoding='utf-8'))['items'] if r['ManagerFlag']]; print('SALES_MANAGER is a manager role:', 'SALES_MANAGER' in m, '| manager roles:', len(m)); print(collections.Counter((r['LegalEntity'],r['BusinessUnit']) for r in json.load(open('ru.json',encoding='utf-8'))['items']).most_common(3))"
```
`<ROLE>` = `SALES_MANAGER` when the first line says `True` (VERIFIED); otherwise any code from `m` (print `m` to see them). `<LE>`, `<BU>` = the first (most common) pair. Check the new names are free:
```bash
python -B "<W>" "<FSCR>" <C>/resourceUsers --query "q=ResourceOrganizationName='<ORG>' or LastName='<MGR>'" --query onlyData=true --query fields=LastName --no-open-browser --output "<RUN>/pre.json" > pre.log 2>&1
python -I -c "import json; print('existing rows:', len(json.load(open('pre.json',encoding='utf-8'))['items']))"
```
Expect `existing rows: 0`; otherwise choose other names.

## Step 2. Create the organization with its manager (POST ONCE, VERIFIED)
`<RUN>/org.json`:
```json
{"FirstName": "GAPFILL", "LastName": "<MGR>", "ResourceEmail": "<mgr in lower case>@example.invalid", "PersonType": "EMP",
 "LegalEntity": "<LE>", "BusinessUnit": "<BU>", "CreateUserAccountFlag": false,
 "ResourceOrganizationName": "<ORG>", "ResourceOrgRoleCode": "<ROLE>", "ResourceStartDate": "<TODAY>"}
```
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --method POST --body-file "<RUN>/org.json" --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" --no-open-browser --output "<RUN>/org_out.json" > org.log 2>&1
```
Success: `org_out.json` written, with `ResourceProfileId`. If the connection drops, run Step 3 before any new try; never POST twice.

## Step 3. Read back (VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" <C>/resourceUsers --query "q=ResourceOrganizationName='<ORG>'" --query onlyData=true --query fields=LastName,ResourceOrganizationName,ResourceParentOrganizationName,ResourceOrgRoleCode,UserStatus --no-open-browser --output "<RUN>/rb.json" > rb.log 2>&1
python -I -c "import json; print(json.load(open('rb.json',encoding='utf-8'))['items'])"
```
Expect 1 row: `<MGR>`, `ResourceOrganizationName` = `<ORG>`, `<ROLE>`, `UserStatus` None (no account).
`ResourceParentOrganizationName` may be filled by Oracle even if you sent none (VERIFIED 3 times: Oracle placed each new organization under an earlier own test organization of the hierarchy). This is Oracle's choice, not an error. To choose the parent, send `ResourceParentOrganizationName` = an organization you own (see manage-resource-org-hierarchies).

## Errors seen (VERIFIED in batch 20, nothing created)
| Message | Cause | Fix |
|---|---|---|
| HZ-120845 ResourceOrgRoleCode required | no role | add `ResourceOrgRoleCode` |
| HZ-120839 manager not active or not in the hierarchy | `ResourceOrgManagerEmail` of a new manager without user | do not send it |

## Rules and limits
1. Always `CreateUserAccountFlag: false` and `example.invalid` emails for a test: no account, no mail.
2. New organizations only; never add a resource to an organization you did not create.
3. No delete by REST; test records stay.

## Worked example (2026-11-26, codes only)
| Step | Result |
|---|---|
| Task export | refused (task flag N) |
| Own test | manager `GAPFILL_AB_B22_RM1` created organization `GAPFILL_AB_B22_ORG1`; read back 1 row, role SALES_MANAGER, no account; parent filled by Oracle with an own earlier test organization |
| Fresh test | see STATUS.md |
