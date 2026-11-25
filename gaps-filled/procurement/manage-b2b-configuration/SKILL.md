---
skill_id: "gosaas.gap-fills.procurement.manage-b2b-configuration"
name: "Manage B2B Configuration (GoSaaS gap fill)"
description: "Create a new B2B service provider and a new B2B trading partner under it with Oracle REST (b2bServiceProviders, b2bTradingPartners), then read both back. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 04, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_CMK_MANAGE_B2B_CONFIG"
task_name: "Manage B2B Configuration"
offering: "Procurement"
dataloader_import_mode: "REST"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
side_effects:
  - "Creates one service provider and one trading partner (no connection, no documents, no supplier site). Plan as if they stay (this skill never deletes)."
---

# Manage B2B Configuration (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no CSV route (catalog flag N) and no skill for this task. This skill uses FSCR's REST client in place (through the GoSaaS wrapper `rest_call.py`) and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
B2B configuration sets up who exchanges purchasing messages (orders, acknowledgments) with Oracle: **service providers** (a B2B network or a direct link) and **trading partners** (an identifier used on that link). Use this skill to create a **new** service provider and a **new** trading partner. Do not use it to change existing ones.
Out of scope (not tested): delivery methods, documents, inbound/outbound collaboration messages and supplier site associations. A partner without those exchanges no messages. GUESS

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
SP     = new service provider name and partner id, PREFIX + short name (e.g. GAPFILL_AB_SP1)
TP     = new trading partner id, PREFIX + short name (e.g. GAPFILL_AB_TP1)
```

## Shell and safety (read first)
- Start every Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Keep values in files under `RUN` (shell variables do not survive between tool calls).
- Run `rest_call.py` with `python -B` (not `-I`) and always with `--output <file>`; print only the fields you need (never whole JSON: audit fields hold user names). It never prints tokens or the server address.
- In a `q=` filter write spaces as `%20` (a raw space gives `Invalid REST endpoint`). VERIFIED

## Sign-in
If a call says HTTP 401/403, or hangs with no output, stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab).

## Step 1. Read (check the names are free)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/b2bServiceProviders?limit=500&onlyData=true" --no-open-browser --output "<RUN>/sp_before.json"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/b2bTradingPartners?limit=500&onlyData=true" --no-open-browser --output "<RUN>/tp_before.json"
python -I -c "import json,sys; a=json.load(open(sys.argv[1],encoding='utf-8'))['items']; b=json.load(open(sys.argv[2],encoding='utf-8'))['items']; print(len(a),'providers',len(b),'partners'); print('SP taken:', any(x['ServiceProviderName']==sys.argv[3] for x in a), '| TP taken:', any(x['TradingPartner']==sys.argv[4] for x in b))" "<RUN>/sp_before.json" "<RUN>/tp_before.json" "<SP>" "<TP>"
```
Both must say `False`. VERIFIED (our environment: 5+ providers, 0 partners at first).

## Step 2. Create the service provider
Approval: the person must approve the environment, the task, SP and TP before this step.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -I -c "import json,sys; json.dump({'ServiceProviderName':sys.argv[2],'PartnerId':sys.argv[2],'PartnerIdType':'ORA_Name'}, open(sys.argv[1],'w'))" "<RUN>/sp_body.json" "<SP>"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/b2bServiceProviders" --method POST --body-file "<RUN>/sp_body.json" --no-open-browser --output "<RUN>/sp_new.json"
python -I -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d['ServiceProviderId'], d['ServiceProviderName'], d['PartnerIdType']); open(sys.argv[2],'w').write(str(d['ServiceProviderId']))" "<RUN>/sp_new.json" "<RUN>/sp_id.txt"
```
VERIFIED: HTTP 201, Oracle returns the new `ServiceProviderId` (saved to `sp_id.txt`). `PartnerIdType` codes seen: `ORA_Name`, `ORA_PHONE`, `ORA_Generic`, `ORA_Direct`.

## Step 3. Create the trading partner under it
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -I -c "import json,sys; json.dump({'TradingPartner':sys.argv[2],'TradingPartnerIdType':'ORA_Name','ServiceProviderId':int(open(sys.argv[3]).read())}, open(sys.argv[1],'w'))" "<RUN>/tp_body.json" "<TP>" "<RUN>/sp_id.txt"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/b2bTradingPartners" --method POST --body-file "<RUN>/tp_body.json" --no-open-browser --output "<RUN>/tp_new.json"
python -I -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d['TradingPartnerId'], d['TradingPartner'], d['ServiceProviderName']); open(sys.argv[2],'w').write(str(d['TradingPartnerId']))" "<RUN>/tp_new.json" "<RUN>/tp_id.txt"
```
- `ServiceProviderId` is **required** (an id, not the name). VERIFIED: a body with only `ServiceProviderName` was refused with `HTTP 400: null`, nothing created.
- Oracle sets `ManualEntryIndicator` = `Yes`. VERIFIED

## Step 4. Read back
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/b2bServiceProviders/$(cat "<RUN>/sp_id.txt")?onlyData=true" --no-open-browser --output "<RUN>/sp_after.json"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/b2bTradingPartners/$(cat "<RUN>/tp_id.txt")?onlyData=true" --no-open-browser --output "<RUN>/tp_after.json"
python -I -c "import json,sys; s=json.load(open(sys.argv[1],encoding='utf-8')); t=json.load(open(sys.argv[2],encoding='utf-8')); ok=s['ServiceProviderName']==sys.argv[3] and t['TradingPartner']==sys.argv[4] and t['ServiceProviderName']==sys.argv[3]; print('READBACK:', 'PASS' if ok else 'FAIL')" "<RUN>/sp_after.json" "<RUN>/tp_after.json" "<SP>" "<TP>"
```
`READBACK: PASS` = both records exist and the partner points to your provider. VERIFIED

## Rules and limits
1. New records only; this skill never sends PATCH or DELETE.
2. Never link a test partner to a real network provider (they route real messages); create your own test provider as in Step 2.
3. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Partner with provider name only (`GAPFILL_AB_B4_TP1`) | refused HTTP 400, not created |
| Provider `GAPFILL_AB_B4_SP1` | created (new id), ORA_Name |
| Partner `GAPFILL_AB_B4_TP2` under it | created, ManualEntryIndicator Yes |
| Read back both by id | PASS |
