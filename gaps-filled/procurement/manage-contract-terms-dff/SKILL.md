---
skill_id: "gosaas.gap-fills.procurement.manage-contract-terms-dff"
name: "Manage Contract Terms Descriptive Flexfields (GoSaaS gap fill)"
description: "Route and limits for adding a context or segment to a contract terms (OKC) descriptive flexfield through FSCR's setup-task CSV export and import. Written, not import-tested: any change needs a flexfield deployment that changes a shared flexfield for every user, so an agent test is unsafe. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 04, 2026-11-25. Export checked live on one test environment; import NOT tested (unsafe). NOT official FSCR."
task_code: "ORA_OKC_MANAGE_CONTRACT_TERMS_DESCRIPTIVE_FLEXFIELDS"
task_name: "Manage Contract Terms Descriptive Flexfields"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
side_effects:
  - "The export is read-only. Any import changes a shared flexfield and must be followed by a flexfield deployment; only with the owner's approval."
---

# Manage Contract Terms Descriptive Flexfields (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live check (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
Descriptive flexfields (DFFs) add extra fields to contract terms pages (clauses, templates, deliverables). The task export is the standard flexfield package for module OKC (scope `moduleType=APPLICATION`, `moduleKey=OKC`, `mode=search`). VERIFIED. It has 14 files: `ASM_SETUP_CSV_METADATA.xml`, `FND_APP_DESCRIPTIVE_FLEXFIELD.csv` and the `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_*` files for contexts, segments, global segments, usages, pages and validators. On our environment it had **0 rows** (no OKC DFF configured). VERIFIED

**An agent must not test this by import.** A new context or segment only appears after a **flexfield deployment**, which regenerates the flexfield for every user of the environment; a deployed context or segment code cannot simply be removed, and a wrong one can break the pages that use the flexfield. GUESS (standard Oracle flexfield behaviour; not tried, on purpose). Use this skill to look at the current setup and to hand a person an approved change.

## Placeholders
```text
FSCR = the FSCR root folder. Read only.
RUN  = a NEW empty work folder OUTSIDE FSCR and outside any git repo
```

## Shell and safety (read first)
- Start every Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Save FSCR output to a file; error lines can hold the server address.
- If the export makes no ZIP (`Error: Failed calling ...`), run it again into a new folder (read-only).
- FSCR's file names start with the environment name: do not copy them into reports. Do not print audit columns (user names).

## Sign-in
If a call says HTTP 401/403, or hangs with no output, stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab).

## Step 1. Read-only export and row counts
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_OKC_MANAGE_CONTRACT_TERMS_DESCRIPTIVE_FLEXFIELDS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run the export again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,glob,sys,os; [print(os.path.basename(f), sum(1 for _ in csv.reader(open(f,encoding='utf-8-sig')))-1, 'rows') for f in sorted(glob.glob(sys.argv[1]+'/*.csv'))]" "<RUN>/export_before/unz"
```
Expect 14 files (VERIFIED). Rows show which OKC DFFs already have contexts and segments.

## Step 2. Hand over to a person
Tell the person (with the flexfield owner's approval):
- The change is made either on the screen (Setup and Maintenance > task **Manage Contract Terms Descriptive Flexfields** > edit the flexfield > add a context or segment), or by importing a package built from this export (new context row + its segment rows, metadata XML unchanged).
- After either, the flexfield must be **deployed** (Deploy Flexfield on the same page). GUESS: the CSV import does not deploy by itself.
- After that, the agent may repeat Step 1 and compare the exports to confirm the new rows.

## Why there is no agent import step
- A test context cannot be kept to the tester: after deployment it is part of the shared flexfield for everyone.
- Rolling back means changing and redeploying the shared flexfield again.

## Rules and limits
1. Read-only for agents.
2. Export checked on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25)
| Step | Result |
|---|---|
| Export | 14 files, all 0 rows (scope module OKC) |
| Import | not done: needs a shared flexfield deployment |
