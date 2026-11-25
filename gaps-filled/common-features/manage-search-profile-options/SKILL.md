---
skill_id: "gosaas.gap-fills.common-features.manage-search-profile-options"
name: "Manage Search Profile Options: set the search method for one user by REST; read the SITE value (GoSaaS gap fill)"
description: "Sets a USER-level value of the search profile option Search Method Default (ZCA_SEARCH_DEFAULT_OPTION) through the REST child userProfileOptionValues (run with FSCR's REST client), reads it back, and reads the SITE value and the task's CSV export. The SITE change (every user) is documented but not run. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 06 (written), batch 11 (USER level tested), 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZCA_MANAGE_SEARCH_PROFILE_OPTIONS"
task_name: "Manage Search Profile Options"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
status: "tested (batch 11, USER level)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
  - "gap skill create-implementation-users (a test user for the USER level)"
  - "shared.setup-export.task-level-export (read only)"
side_effects:
  - "Step 3 adds one USER-level value: only that user's default search method changes."
  - "Steps 6 to 8 (SITE, not run) would change the default for every user."
---

# Manage Search Profile Options (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.
> **Tested:** the USER-level value by REST (Steps 2 to 4, on a test user nobody signs in with). **Not run:** the SITE change (Steps 6 to 8): it changes search for every user of the environment; only with the owner's written approval.

## What it is and when to use
The task holds the profile options that control the global search in Fusion (application `ZCA`). Its export scope is two named, **seeded** options in `edit` mode (VERIFIED, from the export's `ASM_SETUP_CSV_METADATA.xml`):

| Option | User name | Levels (VERIFIED, REST `profileOptionLevels`) | Values |
|---|---|---|---|
| `ZCA_SEARCH_DEFAULT_OPTION` | Search Method Default | SITE and USER enabled and updatable; PRODUCT not | lookup `ZCA_SEARCH_OPTION`: `KEYWORD_SEARCH`, `REAL-TIME_SEARCH` (VERIFIED) |
| `ZCA_SEARCH_HIDE_SENSITIVE_ATTR` | hide sensitive attributes (GUESS from the code) | not found by REST in our release (HTTP 404 / 0 rows, VERIFIED) | - |

Use the USER route to give one user (for example a test or demo user) a different default search; use the read steps to report the current SITE value.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
W        = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's fusion_rest_client.py unchanged; shows Oracle's error text)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers, for the export)
RUN      = a NEW empty work folder, OUTSIDE FSCR and outside any git repo
OPTION   = ZCA_SEARCH_DEFAULT_OPTION
USER     = the user name that gets the value (for a test: your own test user, Prerequisite 2)
USERGUID = that user's 32-character id (SCIM id), read live in Prerequisite 2
VALUE    = KEYWORD_SEARCH or REAL-TIME_SEARCH (read live, Step 2)
P        = /fscmRestApi/resources/11.13.18.05/profileOptions/<OPTION>
```
Call pattern: `cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" <endpoint> [--scim-only] [--method POST --body-file f.json --header "Content-Type=application/vnd.oracle.adf.resourceitem+json"] [--query k=v ...] --no-open-browser --output x.json > x.log 2>&1; echo rc=$?`. On `rc=1` the last line of `x.log` is Oracle's message.

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens, headers, the server address (JSON answers hold it in `links`) or other people's user names; always pass `fields=` on reads of value rows.

## Prerequisites
1. Read access to `profileOptions`; for Step 3 the right to change profile values.
2. **USER exists and USERGUID is known.** For a test use your own test user made with the gap skill `create-implementation-users` (no roles needed). USERGUID = the `id` of `/hcmRestApi/scim/Users --scim-only --query 'filter=userName eq "<USER>"' --query attributes=id,userName,active` (VERIFIED).
3. **USER has no value yet:** `<P>/child/userProfileOptionValues --query "q=LevelValue='<USERGUID>'" --query onlyData=true --query fields=UserName,ProfileOptionValue` → `count 0` (VERIFIED filter: it found the row after Step 3). If there is a value, stop: changing it is an update of an existing record.

## Step 2. Read the option, its levels, values and SITE value (read only, VERIFIED)
- `<P>/child/profileOptionLevels --query onlyData=true` → USER `EnabledFlag Y`, `UpdateableFlag Y`. If USER is not enabled (for example `HZ_ENABLE_MULTIPLE_BU_CRM`), this route is closed.
- `/fscmRestApi/resources/11.13.18.05/standardLookups/ZCA_SEARCH_OPTION/child/lookupCodes --query onlyData=true --query fields=LookupCode,Meaning,EnabledFlag` → the allowed VALUEs.
- `<P>/child/siteProfileOptionValues --query onlyData=true --query fields=LevelValue,ProfileOptionValue` → SITE value (VERIFIED: `KEYWORD_SEARCH`). Write it down: Step 4 proves it did not change.
- The REST resource `profileOptions` itself is read only; its children `siteProfileOptionValues`, `userProfileOptionValues`, `productProfileOptionValues` allow get, create, upsert, update, delete (VERIFIED by `/describe`).

## Step 3. Create the USER value (VERIFIED)
`<RUN>/post.json`:
```json
{"LevelValue":"<USERGUID>","UserName":"<USER>","ProfileOptionValue":"<VALUE>"}
```
POST to `<P>/child/userProfileOptionValues` → `rc=0`; the answer shows LevelValue = USERGUID, your VALUE and USER (VERIFIED).
- `LevelValue` is the user's **GUID**, not the user name: with `LevelValue` = the user name Oracle refuses `Applying List binding LOV_UserName with given set of values leads to no matching row` (VERIFIED, nothing created).
- Never send `Upsert-Mode`. Dropped connection: do not POST again; wait 2 minutes and do Step 4.

## Step 4. Read back (VERIFIED)
Prerequisite 3's read again → `count 1` with VALUE; Step 2's SITE read again → unchanged.

## Step 5. Read-only export (optional)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZCA_MANAGE_SEARCH_PROFILE_OPTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 40 s): 4 files, `FND_APP_PROFILE_OPTION.csv` (13 columns), `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv` (10), `FND_APP_PROFILE_VALUE.csv` (10: `FND_APP_PROFILE_OPTION.ProfileOptionName`, `FND_APP_PROFILE_OPTION.ApplicationId`, `LevelName`, `LevelValue`, `ProfileOptionValue` + audit), all with **0 rows**, and the metadata. The export leaves seeded options out (as batch 4 saw for ZX options), so the export cannot be the read-back here: use REST (Steps 2 and 4).

## Step 6. SITE value: build the row (GUESS: not run; changes every user)
A value is a child row of its option (hierarchical package): the parent option row must be in the same ZIP, unchanged (lesson from `manage-admin-profile-values`, VERIFIED there for own options). Here the parent is seeded and the export has no row for it, so the parent row must be written from REST, with exactly the seeded values (`ProfileOptionName`, `ApplicationId`, `ModuleId`, `UserProfileOptionName`, `Description`, `SqlValidation`, dates). GUESS: if any parent value differs, the import updates the seeded option; a round trip (rule from batch 4) on an environment you own should be done first.
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name search_value.zip \
  --prefix ZCA_ --key "FND_APP_PROFILE_OPTION.csv=ProfileOptionName" \
  --row "FND_APP_PROFILE_OPTION.csv|ProfileOptionName=<OPTION>|ApplicationId=<from REST>|ModuleId=<from REST>|UserProfileOptionName=<from REST>|...all other columns exactly as REST shows them" \
  --row "FND_APP_PROFILE_VALUE.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<OPTION>|FND_APP_PROFILE_OPTION.ApplicationId=<from REST>|LevelName=SITE|LevelValue=SITE|ProfileOptionValue=<NEWVAL>"
```
NEWVAL must be one of the option's allowed values (read the option's `SQLValidation` through REST field names your release accepts, or the option's lookup) (GUESS).

## Step 7. SITE value: import (GUESS: not run; only with the environment owner's written approval)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZCA_MANAGE_SEARCH_PROFILE_OPTIONS --task-name "Manage Search Profile Options" \
  --zip-file "<RUN>/payload/search_value.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
Write down the `ProcessId`. If the connection drops after the process started, do not import again: wait 2 minutes and read back (Step 8). A generic database error at the insert (`JBO-26041`): fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it).

## Step 8. SITE value: other route and read back (GUESS)
The REST child `siteProfileOptionValues` also allows update (VERIFIED by `/describe`, not run). After any SITE change, Step 2's SITE read must show NEWVAL, and `profileOptions` must show the option unchanged. NEWVAL = the new SITE value the owner approved; note the old value first so it can be set back.

## Rules and limits
1. Steps 2, 4 and 5 are safe anywhere. Step 3 changes only USER's search default: use your own test user, or a real user only on that person's request.
2. Steps 6 to 8 change the default for every user: only on an environment you own, with written approval; never as a test on a shared environment.
3. Never update or delete an existing USER or SITE value (that is a change of someone else's setting).
4. Seen on one environment (release 11.13.26.10.0).

## Worked example (2026-11-25)
| Step | Record | Result |
|---|---|---|
| levels | `ZCA_SEARCH_DEFAULT_OPTION` | SITE and USER enabled; SITE value `KEYWORD_SEARCH`; 0 USER values |
| POST with LevelValue = user name | test user `GAPFILL_AB_B11_U1` | refused, LOV_UserName no matching row; nothing created |
| POST with LevelValue = GUID | `GAPFILL_AB_B11_U1`, `REAL-TIME_SEARCH` | created; read back `count 1`; SITE still `KEYWORD_SEARCH` |
| export (batch 06) | scope: the 2 named options | 4 files, 0 rows, about 40 s |
| fresh test | see CHANGELOG.md | |
