---
skill_id: "gosaas.gap-fills.common-features.manage-indirect-tax-automation-with-thomson-reut"
name: "Manage Indirect Tax Automation with Thomson Reuters: register the tax partner by REST taxPartnerRegistrations (GoSaaS gap fill, written, unsafe to test)"
description: "Registers Thomson Reuters as the tax calculation partner of an environment through the REST resource taxPartnerRegistrations (create only). Not run: it needs the customer's real Thomson Reuters account and connects every transaction's tax calculation of the environment to it. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 22, 2026-11-26. Resource describe VERIFIED; create not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_MANAGE_INDIRECT_TAX_AUTOMATION_WITH_THOMSON_REUTERS"
task_name: "Manage Indirect Tax Automation with Thomson Reuters"
dataloader_import_mode: "REST"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "an Thomson Reuters account for this environment (endpoint address, connection user and password), owned by the customer"
side_effects:
  - "Step 3 (not run) registers the tax partner for the whole environment: Oracle then sends transactions' tax calculation to it. The resource has no delete."
---

# Manage Indirect Tax Automation with Thomson Reuters (GoSaaS gap fill, written: unsafe to test)

> **Added by GoSaaS, not part of official FSCR.** No FSM CSV: the task export is refused (task flag `CSVExportImportSupportedFlag N`, VERIFIED 2026-11-26). Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.
> **Status: written, unsafe to test.** Run Step 3 only on an environment the customer owns, with their own Thomson Reuters account and their written approval. A person types the connection password; a script or agent never does.

## What it is and when to use
The task connects Oracle's tax engine to Thomson Reuters ONESOURCE Indirect Tax (a tax partner) so the partner calculates transaction taxes. The REST resource `taxPartnerRegistrations` (fscm, VERIFIED by describe: actions **create** and get; attributes `OperationName`, `TaxPartnerName`, `EndpointURL`, `ConnectionUserName`, `ConnectionPassword`, `DocumentId`, `ReqstId`, `Status`) starts the "register tax partner" operation. Oracle's docs (REST API for Fusion Cloud Financials, "Create a tax partner for tax calculation integration") show `OperationName` `registerTaxPartner`.
Use it when a customer moves tax calculation to Thomson Reuters and has the account details. Oracle's REST docs (Financials 26D/25D, "Create a tax partner") give no list of partner names and no example naming a partner (VERIFIED by reading the docs 2026-11-26), so the partner name is GUESS.

## Why it is unsafe to test here
1. It needs a real Thomson Reuters account (endpoint, user, password) that we do not have and must not type.
2. A registration applies to the whole environment: other people's transactions would be sent to the partner.
3. The resource has no delete and no update (VERIFIED: create, get), so it cannot be put back by REST.
What would make it safe: an environment the customer owns, with their Thomson Reuters sandbox account and their approval.

## Placeholders
```text
FSCR     = the FSCR root folder (holds core\ and the filled-in core\auth\fusionEnv.properties). Read only.
W        = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's REST client; never prints the server)
RUN      = a NEW empty work folder OUTSIDE FSCR and outside any git repo
PARTNER  = the tax partner name Oracle expects for Thomson Reuters (GUESS: read it from Oracle's docs for your release)
ENDPOINT = the Thomson Reuters endpoint address of the customer's account
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. Never print tokens, the server address or user names.

## Prerequisites
1. The customer's Thomson Reuters account for this environment (sandbox for a test).
2. The tax regimes and taxes that Thomson Reuters will calculate are set up for the partner (Oracle's tax partner setup; GUESS: done on the Manage Indirect Tax Automation page or the tax regime's partner options).

## Step 1. Check the resource (read only, VERIFIED)
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/taxPartnerRegistrations/describe --no-open-browser --output describe.json > describe.log 2>&1
python -I -c "import json; v=list(json.load(open('describe.json',encoding='utf-8'))['Resources'].values())[0]; print(sorted({a['name'] for a in v['collection'].get('actions',[])+v['item'].get('actions',[])}), [a['name'] for a in v['attributes']])"
```
Expect `['create', 'get']` and the 8 attributes above. A plain GET of the collection gives HTTP 500 (VERIFIED): Oracle's docs say GET is not supported; do not read it as an error of yours.

## Step 2. Build the request (GUESS)
```json
{"OperationName": "registerTaxPartner", "TaxPartnerName": "<PARTNER>", "EndpointURL": "<ENDPOINT>", "ConnectionUserName": "<typed by the person>", "ConnectionPassword": "<typed by the person>"}
```
Keep the file outside git and delete it after Step 3; it holds a password.

## Step 3. Create ONCE (GUESS, owned environment only)
POST it with FSCR's REST client (`fusion_rest_client.py ... --method POST --data-file <file>`; see FSCR `core/fusion-api/rest-api-client`). Write down `ReqstId` and `Status` from the answer; never print the request.

## Step 4. Read back (GUESS)
The answer's `Status` is the registration's state; `ReqstId` is a scheduled process: check it in Scheduled Processes until it succeeds. Then open the task's page and see the partner registered.

## Rules and limits
1. Never run Step 3 on a shared environment or with an account that is not the customer's.
2. Never let a script or agent type or print the connection password.
3. No delete or update by REST.

## Same route as Manage Indirect Tax Automation with Avalara
Both tasks use the one resource `taxPartnerRegistrations` (VERIFIED describe 2026-11-26: create, get). The Avalara skill (common-features/manage-avalara-onboarding) was judged the same way in batch 19.

## Worked example (2026-11-26)
| Step | Result |
|---|---|
| Task export | refused, task flag `CSVExportImportSupportedFlag N` |
| REST | `taxPartnerRegistrations` describe: create, get (VERIFIED); collection GET: HTTP 500 (GET not supported) |
| Create | not run (unsafe) |
