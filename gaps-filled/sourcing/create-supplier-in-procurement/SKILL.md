---
skill_id: "gosaas.gap-fills.sourcing.create-supplier-in-procurement"
name: "Create Supplier in Procurement (GoSaaS gap fill, REST)"
description: "Create ONE new prospective supplier (no sites, no contacts, no addresses) through the Fusion REST resource suppliers, using FSCR's REST client, and read it back by REST. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing and Supplier Management batch 04, 2026-11-28. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_EGP_CREATE_SUPPLIER_IN_PRC"
task_name: "Create Supplier in Procurement"
offering: "Procurement / Product Management (Suppliers for Product Management)"
dataloader_import_mode: "REST"
owner_team: "GoSaaS"
version: "1.0.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
side_effects:
  - "One REST POST that creates one new supplier party with business relationship PROSPECTIVE. Suppliers cannot be deleted: plan as if it stays. A prospective supplier with no site cannot be used on purchase orders or invoices."
---

# Create Supplier in Procurement (GoSaaS gap fill, REST)

> **Added by GoSaaS, not part of official FSCR.** The task has no FSM CSV (`CSVExportImportSupportedFlag N`: the task export is refused, VERIFIED) and FSCR has no skill. The Fusion REST resource `suppliers` supports `create` (describe, VERIFIED). This skill runs FSCR's REST client in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-28) · **GUESS** = judgment, not tested.

## What it is and when to use
The setup task "Create Supplier in Procurement" opens the supplier creation page so a product manager can create a supplier. The same record is created by REST `POST suppliers`. This skill creates a NEW **prospective** supplier (business relationship `PROSPECTIVE`, tax organization type `CORPORATION`) with no address, site or contact, so it cannot be used to buy or pay. Use it for a test supplier or as the first step of a real supplier load (add addresses, sites and contacts with the resource's child endpoints: GUESS, not tested here).

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); create it first: mkdir -p "<RUN>"
SUP    = the new supplier name: your test prefix + short name, e.g. GAPFILL_AB_SUP1 (upper case, no spaces)
```
Every `<...>` below is a placeholder: put the real value in its place. Git Bash: paths as `E:/...`, start every call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; shell variables do not survive between calls.

## Sign-in
If a call says HTTP 401/403, or hangs with no output, stop it and sign in: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). Never print tokens, the server address or user names. Supplier records of other people may hold people's names: print only the fields shown below.

## Prerequisites
None. Codes used (VERIFIED accepted): `TaxOrganizationTypeCode CORPORATION`, `BusinessRelationshipCode PROSPECTIVE`.

## Step 1. Check SUP is new (and that the check works)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
cd "<RUN>"
python -B "$H" "<FSCR>" "$API/suppliers" --query limit=1 --query onlyData=true --query fields=Supplier --no-open-browser --output "<RUN>/any.json" > any.out 2>&1; echo "rc=$?"
K=$(python -I -c "import json,sys; print(json.load(open(sys.argv[1],encoding='utf-8'))['items'][0]['Supplier'])" "<RUN>/any.json")
python -B "$H" "<FSCR>" "$API/suppliers" --query "q=Supplier='$K'" --query onlyData=true --query fields=SupplierId --no-open-browser --output "<RUN>/control.json" > control.out 2>&1
python -B "$H" "<FSCR>" "$API/suppliers" --query "q=Supplier='<SUP>'" --query onlyData=true --query fields=SupplierId --no-open-browser --output "<RUN>/before.json" > before.out 2>&1
python -I -c "
import json,sys; c=json.load(open(sys.argv[1]))['count']; b=json.load(open(sys.argv[2]))['count']
print('check works' if c==1 else 'STOP: the name check does not find a known supplier', '| SUP is new' if b==0 else '| STOP: SUP exists')
" "<RUN>/control.json" "<RUN>/before.json"
```
Do not print `$K` (it is someone else's supplier name). Expect `check works | SUP is new`. VERIFIED

## Step 2. Create (POST once)
Approval: the person must approve the environment and the new supplier's name before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
cd "<RUN>"
python -I -c "import json,sys; json.dump({'Supplier':sys.argv[2],'TaxOrganizationTypeCode':'CORPORATION','BusinessRelationshipCode':'PROSPECTIVE'}, open(sys.argv[1],'w'))" "<RUN>/body.json" "<SUP>"
python -B "$H" "<FSCR>" "$API/suppliers" --method POST --body-file "<RUN>/body.json" --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" --no-open-browser --output "<RUN>/post.json" > post.out 2>&1; echo "rc=$?"; head -1 post.out
```
Success (VERIFIED): `rc=0`, `HTTP 201`. **Never POST again** after a timeout or error: run Step 3 first; a supplier name can exist only once. On `rc=1` the last lines of `post.out` hold Oracle's message (safe to print; check it holds no address first).

## Step 3. Read back
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
cd "<RUN>"
python -B "$H" "<FSCR>" "$API/suppliers" --query "q=Supplier='<SUP>'" --query onlyData=true --no-open-browser --output "<RUN>/after.json" > after.out 2>&1; echo "rc=$?"
python -I -c "
import json,sys; i=json.load(open(sys.argv[1],encoding='utf-8'))['items']
[print({k:x.get(k) for k in ('Supplier','SupplierNumber','BusinessRelationshipCode','TaxOrganizationTypeCode','Status','CreationSourceCode')}) for x in i]
print('READBACK:','PASS' if len(i)==1 and i[0]['BusinessRelationshipCode']=='PROSPECTIVE' else 'FAIL')
" "<RUN>/after.json"
```
`READBACK: PASS` = one supplier SUP, `PROSPECTIVE`, `Status ACTIVE`, `CreationSourceCode WEB_SERVICE`, with a new supplier number. VERIFIED

## Rules and limits
1. New suppliers only; never PATCH or upsert an existing supplier. Keep test suppliers PROSPECTIVE (no spend authorization, no sites).
2. A supplier cannot be deleted; record the name and number. Name a test supplier only with your prefix, never a real company name.
3. The POST needs no approval workflow on our environment (the supplier was created at once); an environment with supplier creation approval may answer differently (GUESS).
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-28). Do not reuse these names.
| Step | Result |
|---|---|
| Task export | refused: `CSVExportImportSupportedFlag is N` |
| Check | known supplier found (count 1); `GAPFILL_AB_S4_SUP1` new (count 0) |
| POST | HTTP 201: `GAPFILL_AB_S4_SUP1`, PROSPECTIVE, CORPORATION, Status ACTIVE, WEB_SERVICE |
| Read back | 1 supplier: PASS |
