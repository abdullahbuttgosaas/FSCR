---
skill_id: "gosaas.gap-fills.common-features.manage-tax-registrations"
name: "Manage Tax Registrations: new tax registration on a test customer's third-party tax profile (GoSaaS gap fill)"
description: "Create one new tax registration for a TEST customer (third-party tax profile) under a TEST tax regime through FSCR's REST client (POST /fscmRestApi/resources/11.13.18.05/taxRegistrations), then read it back by REST. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 09, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_TAX_REGISTRATIONS"
task_name: "Manage Tax Registrations"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (fusion_rest_client.py, run in place through the GoSaaS wrapper rest_call.py)"
  - "gosaas common-features/manage-tax-exemptions Step 1 (a test customer with a THIRD_PARTY party tax profile)"
  - "gosaas common-features/manage-tax-regimes (a TEST tax regime)"
side_effects:
  - "One REST POST that creates one tax registration on the test customer's tax profile. It may not be deletable; plan as if it stays."
---

# Manage Tax Registrations (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. This skill runs FSCR's REST client in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A tax registration records that a party is registered for a tax regime (with a registration number, from a date). Tax determination uses it, for example to decide whether a customer is registered. Use this skill to add **one new** registration to a **test customer** for a **test regime**.

**Why REST and not the CSV route:** the task's FSM CSV package (VERIFIED, read-only export) holds first-party files only (legal reporting unit registrations, VAT reporting, default tax accounts) plus `ZX_TAX_EXEMPTION.csv`. First-party registrations belong to real legal reporting units: changing them changes tax on real transactions, so they are **out of scope** for a shared environment. Third-party (customer/supplier) registrations are not in the package; the REST resource `taxRegistrations` has `create` (VERIFIED by `/describe`).

**Safety:** only a test customer that you made (its name starts with your prefix) and only a test regime that you made (not subscribed by any business unit). Never add a registration to a real customer, supplier or legal reporting unit; never change or end-date an existing registration.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
W       = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's fusion_rest_client.py unchanged; also shows Oracle's error text)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
CUST    = the test customer's organization name (starts with PREFIX); PNUM = its party number (read live, Prerequisite 1)
REGIME  = a TEST tax regime code (starts with PREFIX) (Prerequisite 2)
REGNUM  = the new registration number, starting with PREFIX (VERIFIED with 18 characters; the field takes 50)
FROM    = start date YYYY-MM-DD, on or after the regime's EffectiveFrom (if the brief gives none: the regime's EffectiveFrom)
```

## Step 1. Safe run and sign-in
- Run every call as `cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" <endpoint> [options] --no-open-browser --output <file>.json > <file>.log 2>&1`, then look at the JSON. If the command fails, the last line of the `.log` is Oracle's own message (`HTTP 400: ...`), without the server address. Do **not** use `-I` (FSCR sign-in needs `pywin32` from the user site-packages on Windows).
- Git Bash on Windows: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; paths as `E:/...`. A query with spaces or quotes goes in `--query "q=..."` (one `--query` per parameter).
- Never print tokens, headers, the sign-in URL, the server address or user names. Always pass `fields=` on reads (full rows hold user names).
- If a call reports HTTP 401/403, an expired token, or hangs: sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
1. **A test customer with a THIRD_PARTY party tax profile.** Read PNUM live:
   `... "/crmRestApi/resources/11.13.18.05/accounts" --query "q=OrganizationName='<CUST>'" --query onlyData=true --query fields=PartyNumber,OrganizationName` → want `count 1`; PNUM = `PartyNumber` (VERIFIED).
   Then the profile: `... /fscmRestApi/resources/11.13.18.05/partyTaxProfiles --query "q=PartyNumber='<PNUM>'" --query onlyData=true --query fields=PartyNumber,PartyTypeCode` → want a row with `PartyTypeCode THIRD_PARTY`.
   If the customer or the profile is missing, make them first with Step 1 of the gap skill `manage-tax-exemptions` (CRM REST `accounts` POST, then `partyTaxProfiles` POST; GET first, POST once).
2. **A test regime REGIME:** `... /fscmRestApi/resources/11.13.18.05/taxRegimesLOV --query "q=TaxRegimeCode='<REGIME>'" --query onlyData=true --query fields=TaxRegimeCode,CountryCode,EffectiveFrom,EffectiveTo` → want `count 1`, no `EffectiveTo` (VERIFIED). If you have none, make one with the gap skill `manage-tax-regimes` (Steps 1 to 6; Step 7 is not needed here).
   **Look at `CountryCode`.** Oracle checks the registration number against the regime's country: for a `GB` regime it refused `REGNUM` with `ZX-885657 You must enter a tax registration number with country code GB as the first two digits` (VERIFIED, nothing created). A `US` regime took a free-text number (VERIFIED). Prefer a test regime whose country has no number format (US worked). For a country with a format, REGNUM must follow it (GUESS).
3. **No registration yet** for PNUM under REGIME:
   `... /fscmRestApi/resources/11.13.18.05/taxRegistrations --query "q=PartyNumber='<PNUM>';TaxRegimeCode='<REGIME>'" --query onlyData=true --query fields=PartyNumber,TaxRegimeCode,RegistrationNumber` → want `count 0` (VERIFIED).
   **Join conditions with `;`, never with ` and `:** on this resource `q=A and B` returns `count 0` even when the row exists (VERIFIED in our fresh test), so a duplicate check with `and` always looks clean. If there is one, take another test customer or test regime; never change the existing one. (Whether Oracle allows two registrations for one party and regime with different dates was not tried: GUESS that it refuses overlaps.)

## Step 2. Create (POST)
**Approval.** The person must approve the environment, CUST, REGIME and REGNUM before the POST. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.

Write `<RUN>/post.json`:
```json
{"PartyTypeCode":"THIRD_PARTY","PartyNumber":"<PNUM>","TaxRegimeCode":"<REGIME>","RegistrationNumber":"<REGNUM>","EffectiveFrom":"<FROM>"}
```
```bash
cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/taxRegistrations --method POST \
  --body-file "<RUN>/post.json" --header "Content-Type=application/vnd.oracle.adf.resourceitem+json" \
  --no-open-browser --output post_resp.json > post.log 2>&1; echo rc=$?; grep -o "HTTP [0-9]*.*" post.log | head -1
```
- Want `rc=0` and `HTTP 201` (the log's last line is then `Wrote ...post_resp.json`; on a failure the last line is Oracle's `HTTP 400: ...`). `post_resp.json` shows your PNUM, REGIME, REGNUM and FROM (VERIFIED). It is the full row: keep it in RUN only, and never copy its `...By` columns into a report. These 5 fields are enough (VERIFIED); Oracle fills the profile id and the defaults (for example rounding) itself.
- `HTTP 400` creates nothing (VERIFIED for ZX-885657): read the message, change one thing, check Prerequisite 3 again, retry; at most 3 tries.
- **Dropped connection or time-out after the POST was sent:** do **not** POST again. Wait 2 minutes, then Step 3: if the registration is there, it worked.

## Step 3. Read back (the proof)
```bash
cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/taxRegistrations \
  --query "q=PartyNumber='<PNUM>';TaxRegimeCode='<REGIME>'" --query onlyData=true \
  --query fields=PartyTypeCode,PartyNumber,TaxRegimeCode,RegistrationNumber,EffectiveFrom \
  --no-open-browser --output readback.json > readback.log 2>&1
python -I -c "import json,sys; d=json.load(open(sys.argv[1])); ok=d['count']==1 and d['items'][0]['RegistrationNumber']==sys.argv[2] and d['items'][0]['PartyTypeCode']=='THIRD_PARTY'; print('READBACK:', 'PASS' if ok else 'FAIL', d['items'])" readback.json "<REGNUM>"
```
`READBACK: PASS` = exactly one registration for PNUM under REGIME, with your number, on the third-party profile (VERIFIED).

## Rules and limits
1. New registrations only, only on your own test customer and test regime. Never edit, end-date or delete an existing registration (this skill sends no PATCH or DELETE).
2. First-party (legal reporting unit) registrations are out of scope: they are real company setup.
3. Not tested: `Tax`, `TaxJurisdictionCode`, registration status/type/reason codes, party sites, suppliers, `DefaultRegistrationFlag=true`.
4. Test records may stay for good.
5. Tested on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B9_TRG1` on test customer `GAPFILL_AB_B4FIX_CUST1`, regime `GAPFILL_AB_TR1` (country GB) | refused: HTTP 400 `ZX-885657` (number must start with GB); GET: 0 registrations, nothing created |
| 2 | `GAPFILL_AB_B9_TRG2`, same customer, regime `GAPFILL_AB_TR3R` (country US), from 2026-01-01 | created (HTTP 201); read-back 1 row, THIRD_PARTY, PASS |
| fresh test | `GAPFILL_AB_B9_TRG3F` on test customer `GAPFILL_AB_B4FIX_CUST2F`, regime `GAPFILL_AB_TR3R` | created (HTTP 201); the read-back as then written (`q=... and ...`) returned 0 rows; with `;` 1 row, PASS. Led to the `;` rule |
