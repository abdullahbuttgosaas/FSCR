---
skill_id: "gosaas.gap-fills.common-features.manage-atk-admin-profile-values"
name: "Manage Application Toolkit Administrator Profile Values (GoSaaS gap fill, card)"
description: "Card over manage-profile-options and manage-admin-profile-values: in one FSM CSV import, create your own new Application Toolkit (ATK) profile option (the prerequisite) and set its SITE value, with the application id and module id read live by REST, then read both back by REST and a second export. Seeded ATK values are never touched. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 1, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ATK_ADMIN_PROFILE_OPTION_VALUES"
task_name: "Manage Application Toolkit Administrator Profile Values"
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
  - "gosaas common-features/manage-admin-profile-values/SKILL.md (value row and read-back)"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new ATK profile option, its 3 level rows and one SITE value on it. They may not be deletable; plan as if they stay."
---

# Manage Application Toolkit Administrator Profile Values (GoSaaS gap fill, card)

> **Added by GoSaaS, not part of official FSCR.** Card over `../manage-profile-options/SKILL.md` (the **full skill**). Follow the full skill; this card says only what is different. Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = not tested.

## What this task is and the test rule
The task sets **values** of profile options owned by the Application Toolkit (application short name `ATK`). Its export holds ATK options, their levels and their values.
- **Test rule:** set a value only on **your own new option**, which no code reads. Setting a value on a seeded ATK option changes the environment for every user: that is the real business use, but it is **not tested** here and needs the person's explicit approval of option, level and value.
- **Prerequisite (Step 1 of this card, same import):** your own ATK option. This card creates it in the **same package** as its value, so there is no separate task to run first.

## Placeholders (in addition to the full skill's)
```text
TASK    = ORA_ATK_ADMIN_PROFILE_OPTION_VALUES
TNAME   = Manage Application Toolkit Administrator Profile Values
NAME    = your new ATK option, upper case, starting with PREFIX, e.g. GAPFILL_<INITIALS>_APO1
VALUE   = the value text, e.g. GAPFILL_<INITIALS>_AV1
APPID   = the ATK ApplicationId, read in Step 3 (a number)
MODULE  = the ATK ModuleId, read in Step 3 (32 characters)
```

## Steps
| Full skill step | What to do instead |
|---|---|
| Step 0, Step 1 | as written |
| Step 2 export | `--task-code <TASK>`. Expect the same 4 files (VERIFIED, about 40 s); scope `moduleType=APPLICATION`, `moduleKey=ATK`, `mode=search`. It holds some seeded ATK options and values: **do not copy or change them**. |
| Step 3 module id | **Replaced** by the block below. Then the full skill's NAME-is-free check (`--expect-absent`) as written. |
| Step 4 build | the block below: option + 3 levels + **1 SITE value** in one package. |
| Step 5 import | `--task-code <TASK> --task-name "<TNAME>" --zip-file "<RUN>/payload/atk_option_value_new.zip"`. Approval rule as in the full skill (environment, task, NAME and VALUE). **Write down the ProcessId.** Success: `ProfileOptionSD.xml ... A total of 5 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`. VERIFIED, about 80 s. |
| Step 6 read back | the block below (REST option, REST value, export compare). |

### Step 3 block: application id and module id, live by REST
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions \
  --q "ApplicationShortName='ATK'" --fields ApplicationId,ModuleId --limit 500 --out "<RUN>/app_ids.json"
python -I -c "import json,sys;s=sorted({(i['ApplicationId'],i['ModuleId']) for i in json.load(open(sys.argv[1]))['items']});print(s);sys.exit(0 if len(s)==1 else 2)" "<RUN>/app_ids.json"
```
Want exactly **one** pair `(APPID, 'MODULE')` (VERIFIED). Otherwise (exit 2) **stop** and ask the person. Never copy the ids from an export or another environment.

### Step 4 block: one package, option + levels + value
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name atk_option_value_new.zip --prefix <PREFIX> \
  --key "FND_APP_PROFILE_OPTION.csv=ProfileOptionName,ApplicationId" \
  --key "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName" \
  --key "FND_APP_PROFILE_VALUE.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName,LevelValue" \
  --prefix-col "FND_APP_PROFILE_OPTION.csv=ProfileOptionName" --max-len "ProfileOptionName=80" \
  --row "FND_APP_PROFILE_OPTION.csv|ProfileOptionName=<NAME>|ApplicationId=<APPID>|ModuleId=<MODULE>|Description=<text>|StartDateActive=<yyyy/mm/dd>|UserProfileOptionName=<DISPLAY>" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=<APPID>|LevelName=PRODUCT|UpdateableFlag=N|EnabledFlag=N" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=<APPID>|LevelName=SITE|UpdateableFlag=Y|EnabledFlag=Y" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=<APPID>|LevelName=USER|UpdateableFlag=N|EnabledFlag=N" \
  --row "FND_APP_PROFILE_VALUE.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=<APPID>|LevelName=SITE|LevelValue=SITE|ProfileOptionValue=<VALUE>"
```
The builder must print `FND_APP_PROFILE_OPTION.csv: 1 new rows`, `FND_APP_PROFILE_VALUE.csv: 1 new rows`, `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv: 3 new rows`. It stops if NAME exists, lacks PREFIX or is too long.
- **Option already made earlier** (only the value is new): build only the value row and add the parent option row unchanged with `../manage-profile-options/scripts/copy_parent_rows.py`, exactly as `../manage-admin-profile-values/SKILL.md` step 3 (without the parent, `0 rows were processed`). GUESS for ATK (VERIFIED for application 0).

### Step 6 block: read back
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions --q "ProfileOptionName='<NAME>'" \
  --fields ProfileOptionName,ApplicationShortName,UserProfileOptionName --out "<RUN>/readback_after.json" \
  --expect "ProfileOptionName=<NAME>,ApplicationShortName=ATK" --expect-count 1
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions/<NAME>/child/siteProfileOptionValues \
  --fields LevelValue,ProfileOptionValue --out "<RUN>/readback_value.json" \
  --expect "LevelValue=SITE,ProfileOptionValue=<VALUE>" --expect-count 1
```
Both must say `READBACK: PASS`. VERIFIED. Then the second export (full skill Step 2 with `--task-code <TASK>`, `--output-dir "<RUN>/export_after"`) and the full skill's Step 6B compare with `<APPID>` instead of `0` and one more expect: `--expect "FND_APP_PROFILE_VALUE.csv=<NAME>,<APPID>,SITE,SITE"`. Want `RESULT: PASS` (added 1 option + 3 levels + 1 value, removed 0, changed 0). VERIFIED

## Rules and limits
1. Values only on your own `PREFIX` option. Seeded ATK values are not touched (see the test rule).
2. Create only; never change or remove an existing value. This card never deletes.
3. Not tested: PRODUCT and USER level values, options with SQL validation, a value on an option made in an earlier run (GUESS above).
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED, 2026-11-24). Do not reuse these names; they now exist.
| Step | Result |
|---|---|
| Export before | 3 ATK options, 9 levels, 2 values; 42 s |
| Step 3 | 1 pair (ATK application id and module id); `GAPFILL_AB_P1_APO1` absent: PASS |
| New records | option `GAPFILL_AB_P1_APO1` (site level enabled) + SITE value `GAPFILL_AB_P1_AV1` |
| Import | 1 attempt (ProcessId 100004741419235), about 80 s: 5 rows processed, 0 failed |
| REST read-back | option 1 row `ApplicationShortName=ATK`: PASS; site value 1 row `GAPFILL_AB_P1_AV1`: PASS |
| Export after + compare | 4 options, 12 levels, 3 values; added 1 + 3 + 1, removed 0, changed 0: PASS |
