---
skill_id: "gosaas.gap-fills.common-features.manage-partner-organizations"
name: "Manage Partner Organizations: new partner organization by CRM REST (GoSaaS gap fill, written, not load-tested)"
description: "Find partner organizations and create a new one through FSCR's REST client (GET/POST /crmRestApi/resources/11.13.18.05/partners). Read steps VERIFIED; the create step is GUESS because a partner needs an owner resource (a real person) on a shared environment. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 09, 2026-11-25. Read steps and one refused POST seen live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "HZ_MANAGE_PARTNER_ORGANIZATIONS"
task_name: "Manage Partner Organizations"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
status: "written (unsafe to test on a shared environment)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (fusion_rest_client.py, run in place through the GoSaaS wrapper rest_call.py)"
side_effects:
  - "Read steps: none. Create step: one new partner organization (a party with a partner profile), owned by a resource; partner assignment may run for it."
---

# Manage Partner Organizations (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill or guide for this task, and no FSM CSV route (the read-only task export is refused). The REST resource `partners` (CRM) has `create`, `upsert` and a `runAssignment` action (VERIFIED by `/describe`).
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not tested live.
> **Status: written, not load-tested.** Why: Oracle refuses a partner without an owner (`HTTP 400: Provide a valid value for ResourceId.`, VERIFIED, nothing created). The owner must be an existing CRM **resource** (a person set up as a resource). Our sign-in user is not a resource (VERIFIED: `resources` by user name returned 0 rows), so a test partner would have to be owned by a real colleague, who would then see it in their partner lists and get its assignment work. That changes what another person sees on a shared environment. Load-test only on an environment you own, or with a test resource that is yours, and with written approval.

## What it is and when to use
A partner organization is a company that sells or services with you (partner relationship management). Use this skill to look up partners and, where allowed, create a new one.

## Placeholders
```text
FSCR    = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
W       = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's fusion_rest_client.py unchanged; also shows Oracle's error text)
RUN     = a NEW empty work folder, OUTSIDE FSCR and outside any git repo
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
NAME    = new partner OrganizationName, starting with PREFIX (max 360)
COUNTRY = two-letter country code, e.g. US
OWNER   = the PartyId of the resource that will own the partner (Prerequisite 2)
```

## Step 1. Safe run and sign-in
- Run every call as `cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" <endpoint> [options] --no-open-browser --output <file>.json > <file>.log 2>&1`. On a failure the `.log` ends with Oracle's own message (`HTTP 400: ...`), without the server address. Do not use `-I`.
- Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; paths as `E:/...`. Join filter conditions in `q=` with `;`.
- Always pass `fields=` on reads: full partner and resource rows hold names, e-mail addresses and user names. Never print tokens, the server address or user names.
- Sign-in: FSCR `core/auth/fusion-oauth-authentication` (`fusion_login.py --token-cache auto`), a person completes the browser page; never type credentials.

## Step 2. Look up partners (read only, VERIFIED)
```bash
... /crmRestApi/resources/11.13.18.05/partners --query "q=OrganizationName LIKE '<text>%'" --query onlyData=true \
    --query fields=PartyNumber,OrganizationName,Country,PartnerStatus --output partners.json
```
VERIFIED: the call works (our environment had 0 partners, so partner management is likely not in use there). `LIKE` is case-sensitive.

## Prerequisites (for the create step)
1. NAME is free: Step 2 with `q=OrganizationName='<NAME>'` → `count 0` (VERIFIED).
2. **OWNER:** a resource that may own the partner, preferably your own. Find your resource without printing your user name: read your user name at run time from any FSCR export's `ASM_SETUP_CSV_METADATA.xml` (`SubmittedBy`), keep it in a variable, then
   `... /crmRestApi/resources/11.13.18.05/resources --query "q=Username='<value>'" --query onlyData=true --query fields=PartyId,ResourceType`. OWNER = `PartyId` (VERIFIED: the resource has `Username` and `PartyId`; for our sign-in user it returned 0 rows, so we stopped here). If you get 0 rows, **stop**: do not borrow another person's resource on a shared environment.

## Step 3. Create (GUESS)
`<RUN>/post.json`:
```json
{"OrganizationName":"<NAME>","Country":"<COUNTRY>","ResourceId":<OWNER>}
```
```bash
... /crmRestApi/resources/11.13.18.05/partners --method POST --body-file "<RUN>/post.json" \
    --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" --output post_resp.json
grep -o "HTTP [0-9]*.*" post_resp.json.log | head -1
```
- VERIFIED: without `ResourceId` Oracle answers `HTTP 400: Provide a valid value for ResourceId.` and creates nothing (GET afterwards: 0 rows).
- GUESS: with a valid owner, `HTTP 201` and a new `PartyNumber`. Oracle may ask for more fields (for example a partner type or level); read each `HTTP 400` message, add one field, retry, at most 3 tries. Dropped connection after the POST: do not POST again; GET by NAME first.
- Never send `Upsert-Mode=true` (it can update an existing partner).

## Step 4. Read back (GUESS for a created row; the GET itself is VERIFIED)
Step 2 with `q=OrganizationName='<NAME>'` and `fields=PartyNumber,OrganizationName,Country` → `count 1`.

## Rules and limits
1. New partners only; never PATCH, DELETE or upsert an existing partner.
2. Do not run `runAssignment` on a shared environment.
3. Not tested: partner types, levels, tiers, contacts, addresses, account team members (`accountTeamMembers` child).
4. Seen on one environment (release 11.13.26.10.0).

## Worked example (2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | POST `GAPFILL_AB_B9_PRT1`, country US, no owner | refused: `HTTP 400 Provide a valid value for ResourceId`; GET: 0 rows, nothing created (VERIFIED) |
| owner check | the sign-in user's own resource | 0 rows: the user is not a resource; create step stopped (unsafe to borrow another person's resource) |
| 2 (2026-11-26) | POST `GAPFILL_AB_B21_PRT1`, US, `"ResourceId": <own test resource PartyId>` | refused: `HTTP 400 Invalid attribute "ResourceId" in the payload` (VERIFIED: `ResourceId` is not a partners attribute; describe lists `OwnerPartyNumber`) |
| 3 (2026-11-26) | same, `"OwnerPartyNumber": <own test resource party number>` (resource `GAPFILL_AB_B20_RM1`, made by manage-resource-org-members, active, no user account) | refused: `HTTP 400 Provide a valid value for ResourceId.`; GET afterwards 0 rows, nothing created (VERIFIED) |

**Result 2026-11-26: failed.** Oracle does not accept a CRM resource without a user account as the partner owner through REST (GUESS for the cause: the owner is taken from, or checked against, a resource with a sign-in user, or it needs a channel role). Next try: an owner resource that has a user account (for example the Import Worker Users test worker made a resource), with the person's approval.

