---
skill_id: "gosaas.gap-fills.common-features.manage-tax-profile-options"
name: "Manage Tax Profile Options (GoSaaS gap fill, card)"
description: "Card over manage-profile-options: create a new profile option definition owned by the Tax application (ZX) through FSCR's setup-task CSV export and import, with the application id and module id read live by REST, then read it back by REST (profileOptions) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 1, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_TAX_PROFILE_OPTIONS"
task_name: "Manage Tax Profile Options"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-profile-options/SKILL.md (the full skill this card changes)"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new profile option definition and its 3 level rows. It may not be deletable; plan as if it stays."
---

# Manage Tax Profile Options (GoSaaS gap fill, card)

> **Added by GoSaaS, not part of official FSCR.** Card over `../manage-profile-options/SKILL.md` (the **full skill**). Follow the full skill; this card says only what is different. Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = not tested.

## When to use
- Someone asks to create a **new** profile option definition for task `ORA_ZX_MANAGE_TAX_PROFILE_OPTIONS` (options owned by the Tax application, application short name `ZX`).
- Do **not** use it to change the seeded ZX (tax) options or their values. New records only. A new user-defined option is read by no Oracle code, so no tax calculation or other user changes.

## Placeholders (in addition to the full skill's)
```text
TASK    = ORA_ZX_MANAGE_TAX_PROFILE_OPTIONS
TNAME   = Manage Tax Profile Options
APP     = ZX         (the application short name of this task's export scope)
NAME    = new ProfileOptionName, upper case, starting with PREFIX, e.g. GAPFILL_<INITIALS>_ZPO1
APPID   = the ZX ApplicationId, read in Step 3 (a number)
MODULE  = the ZX ModuleId, read in Step 3 (32 characters)
```
Use the full skill's FSCR, GAPS, H, RUN, PREFIX and DISPLAY placeholders as they are.

## Changes to the full skill
| Full skill step | What to do instead |
|---|---|
| Step 0, Step 1 | as written |
| Step 2 export | `--task-code <TASK>`. Expect the same 4 files (VERIFIED, about 30 s). The metadata scope is `moduleType=APPLICATION`, `moduleKey=ZX`, `mode=search`. The export may be **empty** (VERIFIED: 0 rows; the seeded ZX options exist, REST shows them, but the export leaves seeded options out). That is normal: the rows are written in full, and your new option **does** appear in the second export (VERIFIED). |
| Step 3 module id | **Replaced.** Read APPID and MODULE live from the options this application already owns (never copy them from an export or another environment): see the block below. Then do the full skill's NAME-is-free check (`--expect-absent`) as written. |
| Step 4 build | the full skill's command, with `ApplicationId=<APPID>` (in all 4 rows) and `ModuleId=<MODULE>` instead of `0` and the YES_NO module, `--zip-name profile_option_new.zip`. Builder must print `FND_APP_PROFILE_OPTION.csv: 1 new rows` and `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv: 3 new rows`. |
| Step 5 import | `--task-code <TASK> --task-name "<TNAME>"`. Approval rule as in the full skill. **Write down the ProcessId** (`Started setup task CSV import process: <id>`). Success: `ProfileOptionSD.xml ... A total of 4 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`. VERIFIED, about 40 s. |
| Step 6A REST | as written, but `--expect "ProfileOptionName=<NAME>,ApplicationShortName=ZX"`. Want `READBACK: PASS`. VERIFIED |
| Step 6B compare | as written (`--task-code <TASK>` for the second export), with `<APPID>` instead of `0` in every `--expect`. Want `RESULT: PASS` (1 option + 3 levels added, nothing removed or changed). VERIFIED |

### Step 3 block (replaces the full skill's Step 3)
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions \
  --q "ApplicationShortName='ZX'" --fields ApplicationId,ModuleId --limit 500 --out "<RUN>/app_ids.json"
python -I -c "import json,sys;s=sorted({(i['ApplicationId'],i['ModuleId']) for i in json.load(open(sys.argv[1]))['items']});print(s);sys.exit(0 if len(s)==1 else 2)" "<RUN>/app_ids.json"
```
- Want exactly **one** pair `(APPID, 'MODULE')`. VERIFIED: one pair. If it prints no pair or several pairs (exit 2), **stop** and ask the person which module the new option belongs to.
- Always pass `--fields` (the full rows hold user names).

## Rules and limits
1. New records only; never import a full export (a matching `ProfileOptionName` + `ApplicationId` would update that option).
2. Keep all 4 files and the metadata XML in the package (the builder does this).
3. Test records may stay for good. This card never deletes.
4. Not tested: values for the new option (that is a values task), SQL validation, USER level enabled.
5. Tested on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED, 2026-11-24). Do not reuse this name; it now exists.
| Step | Result |
|---|---|
| Export before | 0 options, 0 levels, 0 values (seeded ZX options are left out of the export); 28 s |
| Step 3 | 1 pair (application id and module id of ZX; the same module id as the seeded ZX lookups); `GAPFILL_AB_P1_ZPO1` absent: PASS |
| New record | `GAPFILL_AB_P1_ZPO1`, site level enabled, product and user disabled, from 2026/01/01 |
| Import | 1 attempt (ProcessId 100004741416712), about 40 s: 4 rows processed, 0 failed |
| REST read-back | 1 row, `ApplicationShortName=ZX`: PASS |
| Export after + compare | 1 option, 3 levels (only ours); added 1 + 3, removed 0, changed 0: PASS |
