---
skill_id: "gosaas.gap-fills.common-features.manage-coa-sync-with-drm"
name: "Manage Chart of Accounts Synchronization with DRM (GoSaaS gap fill, card)"
description: "Card over manage-profile-options: the CSV package of this task holds only General Ledger (GL) profile options. Creates a new GL profile option definition in the task's scope through FSCR's setup-task CSV export and import, with the application id and module id read live, then reads it back by REST and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 17, 2026-11-26. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_CHART_OF_ACCOUNTS_SYNCHRONIZATION_WITH_DRM"
task_name: "Manage Chart of Accounts Synchronization with DRM"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-profile-options/SKILL.md (the full skill this card changes)"
  - "gosaas common-features/manage-le-profile-options/SKILL.md (same card pattern, XLE)"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new GL profile option definition and its 3 level rows. It may not be deletable; plan as if it stays."
---

# Manage Chart of Accounts Synchronization with DRM (GoSaaS gap fill, card)

> **Added by GoSaaS, not part of official FSCR.** Card over `../manage-profile-options/SKILL.md` (the **full skill**). Follow the full skill; this card says only what is different. Labels: **VERIFIED** = seen in our live test (2026-11-26) · **GUESS** = not tested.

## What the CSV package holds (VERIFIED)
The task's export scope is `moduleType=APPLICATION`, `moduleKey=GL`, `mode=search`: 3 files, the standard profile option package. It holds the GL options of one GL module (VERIFIED: `GL_CURRENT_ACCESS_SET_ID` and `GL_CURRENT_LEDGER_ID`, 6 levels, 0 values). **The DRM (Data Relationship Management) connection itself is not in the package**: it is set up on the screen. This card covers what the CSV route can do: a **new** profile option owned by GL.

## When to use
- Someone asks to create a **new** profile option definition for task `GL_MANAGE_CHART_OF_ACCOUNTS_SYNCHRONIZATION_WITH_DRM`.
- Do **not** use it to change the two seeded options or to set their values: a SITE value of `GL_CURRENT_LEDGER_ID` or `GL_CURRENT_ACCESS_SET_ID` changes the default ledger or data access set for every user. New records only. A new user-defined option is read by no Oracle code, so it changes nothing for other users.

## Placeholders (in addition to the full skill's)
```text
TASK    = GL_MANAGE_CHART_OF_ACCOUNTS_SYNCHRONIZATION_WITH_DRM
TNAME   = Manage Chart of Accounts Synchronization with DRM
NAME    = new ProfileOptionName, upper case, starting with PREFIX, e.g. GAPFILL_<INITIALS>_GPO1
APPID   = the GL ApplicationId, read in Step 3 (a number; VERIFIED 101)
MODULE  = the GL ModuleId of the task's scope, read in Step 3 (32 characters)
```
Use the full skill's FSCR, GAPS, H, RUN, PREFIX and DISPLAY placeholders as they are.

## Changes to the full skill
| Full skill step | What to do instead |
|---|---|
| Step 0, Step 1 | as written |
| Step 2 export | `--task-code <TASK>`. Expect the same 4 files (3 CSVs + metadata; VERIFIED, about 1 minute). Row counts grow with earlier tests. The script may print `StatusCode: (unknown)` and `(no result yet)` while it waits: normal; success = the ZIP is there. |
| Step 3 module id | **Replaced.** Read APPID and MODULE as in the block below. Then do the full skill's NAME-is-free check (`--expect-absent`) as written. |
| Step 4 build | the full skill's command, with `ApplicationId=<APPID>` (in all 4 rows) and `ModuleId=<MODULE>` instead of `0` and the YES_NO module, and a `Description` such as `GoSaaS test option, read by no code`. Builder must print `FND_APP_PROFILE_OPTION.csv: 1 new rows` and `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv: 3 new rows`. |
| Step 5 import | `--task-code <TASK> --task-name "<TNAME>"`. Approval rule as in the full skill. **Write down the ProcessId** (`Started setup task CSV import process: <id>`). The script may print `StatusCode: (unknown)`: the real result is only in `<RUN>/import_result/*_process_log.txt` (read it as the full skill's Step 5 says). Success there: `A total of 4 rows were processed. 0 rows of them failed` and `Business object: Application Profile Value. Status: Completed successfully`. VERIFIED, under 1 minute. |
| Step 6A REST | as written (keep `--fields` and `--expect-count 1`), but `--expect "ProfileOptionName=<NAME>,ApplicationShortName=GL"` (this replaces the full skill's `--expect`; the display name is printed and should match). Want `READBACK: PASS`. VERIFIED |
| Step 6B compare | as written (`--task-code <TASK>` for the second export), with `<APPID>` instead of `0` in every `--expect`. Want `RESULT: PASS` (1 option + 3 levels added, nothing removed or changed). VERIFIED |

### Step 3 block (replaces the full skill's Step 3)
GL owns options in **two** modules (VERIFIED). Only one is in the task's scope: take MODULE from the export's own rows, and check REST knows it as GL:
```bash
python -I -c "import csv,sys; s=sorted({(r['ApplicationId'],r['ModuleId']) for r in csv.DictReader(open(sys.argv[1]+'/FND_APP_PROFILE_OPTION.csv',encoding='utf-8-sig'))}); print(s); sys.exit(0 if len(s)==1 else 2)" "<RUN>/export_before/unz"
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions \
  --q "ApplicationShortName='GL'" --fields ApplicationId,ModuleId --limit 500 --out "<RUN>/app_ids.json" > "<RUN>/app_ids.log" 2>&1
python -I -c "import json,sys;print(sorted({(i['ApplicationId'],i['ModuleId']) for i in json.load(open(sys.argv[1]))['items']}))" "<RUN>/app_ids.json"
```
- The first line must print exactly **one** pair `('APPID', 'MODULE')`; the same pair must also be in the REST list (the export prints APPID as text `'101'`, REST as a number `101`: compare the values, not the quotes). VERIFIED: export pair `101` + one module; REST lists 2 GL modules, the export's one among them. If the export has no rows or several pairs (exit 2), **stop** and ask the person which module the new option belongs to.
- Always pass `--fields` (the full rows hold user names).

## Rules and limits
1. New records only; never import a full export (a matching `ProfileOptionName` + `ApplicationId` would update that option).
2. Never send a value row for the seeded GL options (see When to use).
3. Keep all 4 files and the metadata XML in the package (the builder does this). Test records may stay for good. This card never deletes.
4. Not tested: values for the new option, SQL validation, USER level enabled, the DRM setup itself (screen only).
5. Tested on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED, 2026-11-26). Do not reuse these names; they now exist.
| Step | Result |
|---|---|
| Export before | 2 options, 6 levels, 0 values |
| Step 3 | export pair `101` + one module, among the 2 GL modules REST lists; `GAPFILL_AB_B17_GPO1` absent: PASS |
| New record | `GAPFILL_AB_B17_GPO1` ("GAPFILL AB B17 GL test option"), site level enabled, product and user disabled, from 2026/01/01 |
| Import | 1 attempt (ProcessId 100004743459537): 4 rows processed, 0 failed |
| REST read-back | 1 row, `ApplicationShortName=GL`: PASS |
| Export after + compare | 3 options, 9 levels; added 1 + 3, removed 0, changed 0: PASS |
| Fresh test (another tester, only this card + full skill) | `GAPFILL_AB_B17_GPO2F`: ProcessId 100004743459557; 4 processed, 0 failed; REST PASS; options 3 → 4, levels 9 → 12: PASS |
| Re-test after wording fix | `GAPFILL_AB_B17_GPO3R`: ProcessId 100004743460308; 4 processed, 0 failed; REST PASS; options 4 → 5, levels 12 → 15: PASS |
