---
skill_id: "gosaas.gap-fills.procurement.configure-electronic-signature"
name: "Configure Electronic Signature for Procurement Documents (GoSaaS gap fill)"
description: "Route and limits for setting up the DocuSign or Adobe Sign connection for procurement documents through FSCR's setup-task CSV export and import. Written, not import-tested: the row needs provider credentials that an agent must not enter. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 02, 2026-11-25. Export checked live on one test environment; import NOT tested. NOT official FSCR."
task_code: "ORA_PO_CONFIGURE_ELECTRONIC_SIGNATURE"
task_name: "Configure Electronic Signature for Procurement Documents"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
side_effects:
  - "The export is read-only. Any import stores provider credentials and changes how all procurement documents are signed; only a person may do it."
---

# Configure Electronic Signature for Procurement Documents (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live check (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
This task connects Oracle procurement to an e-signature provider (DocuSign or Adobe Sign) so suppliers can sign contracts and documents. It has one CSV, `ORA_ZCA_ESIGNATURE_SETUP.csv`. VERIFIED
Its columns include the provider (`SolutionProviderCode`), **`UserName`, `Password`, `ConfirmPassword`, `AccountId`, `AdobeSignRefreshToken`, `APIKey`, `AdminGuid`**, `EndpointUrl`, `OauthUrl`, `ValidationStatus` and `CsfKeyName` (where Oracle keeps the secret). VERIFIED

**An agent must not do the import.** A working row needs real provider credentials (password, API key or refresh token). An agent must never type, copy or store these. Use this skill only to:
1. export and look at the current setup (read only, secrets masked), and
2. hand the person the steps to enter the credentials themselves on the screen.

## Placeholders
```text
FSCR = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
RUN  = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
```

## Shell and safety (read first)
- Start every Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.
- **Never print the CSV with cat, head or a plain reader.** If the setup exists, it holds user names, account ids, tokens and URLs. Use only the masked reader in Step 1.
- FSCR's file names start with the environment name: do not copy them into reports.
- Delete nothing from RUN until the person has checked it is not needed; keep RUN outside any git repo (the export may hold secrets).

## Sign-in
If a call says HTTP 401/403, or hangs with no output, stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Step 1. Read-only export and masked look
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_PO_CONFIGURE_ELECTRONIC_SIGNATURE --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "
import csv,sys
S=('pass','secret','user','key','token','url','account','guid','created','updated','login')
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig')))
print(len(rows),'row(s)')
for r in rows: print({k:('<set>' if v and any(s in k.lower() for s in S) else v) for k,v in r.items()})
" "<RUN>/export_before/unz/ORA_ZCA_ESIGNATURE_SETUP.csv"
```
Expect 2 files: `ASM_SETUP_CSV_METADATA.xml` and `ORA_ZCA_ESIGNATURE_SETUP.csv` (23 columns). VERIFIED. On our environment it had **0 rows** (no provider set up). VERIFIED

## Step 2. Hand over to a person
Tell the person:
- The setup needs a DocuSign or Adobe Sign account and its credentials. These must be entered **by a person** on the screen: Setup and Maintenance > Procurement > task **Configure Electronic Signature for Procurement Documents** (GUESS: screen path from the task name; not opened by us).
- After saving, the screen validates the connection (`ValidationStatus`). GUESS
- After they save, the agent may repeat Step 1 to confirm a row exists (masked).

## Why there is no import step
- The import would need the credentials in a CSV file on disk: that is storing a secret, which the agent must not do.
- A test value cannot be made safe: the setup is one shared row that all procurement documents use, and fake credentials would fail validation or break signing. GUESS (not tried, on purpose)

## Rules and limits
1. Read-only for agents. Never type, copy, print or store provider credentials.
2. Mask every credential column when you look at the export.
3. Tested (export only) on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25)
| Step | Result |
|---|---|
| Export | 2 files; `ORA_ZCA_ESIGNATURE_SETUP.csv` 23 columns, 0 rows |
| Import | not done: needs provider credentials an agent must not enter |
