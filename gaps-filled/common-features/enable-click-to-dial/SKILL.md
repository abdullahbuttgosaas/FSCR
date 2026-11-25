---
skill_id: "gosaas.gap-fills.common-features.enable-click-to-dial"
name: "Enable Click to Dial: read and set the SITE profile option HZ_ENABLE_CLICK_TO_DIAL by REST (GoSaaS gap fill)"
description: "Reads the profile option Click to Dial Enabled (HZ_ENABLE_CLICK_TO_DIAL), its levels and its SITE value, and sets the SITE value through the REST child siteProfileOptionValues (run with FSCR's REST client), with a read-back. Tested on a shared environment as test-and-restore (old value written down, changed, read back, set back, read back). Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 13, 2026-11-25. Tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "MCT_ENABLE_CLICK_TO_DIAL"
task_name: "Enable Click to Dial"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "tested (batch 13, test-and-restore)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
  - "shared.setup-export.task-level-export (read only, optional)"
side_effects:
  - "Steps 2 and 5 are read only."
  - "Step 3 changes the SITE value: click to dial turns on or off for every user."
  - "Step 4 (test only) sets the old value back."
---

# Enable Click to Dial (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
The task holds one profile option (VERIFIED, from the scope in the export's `ASM_SETUP_CSV_METADATA.xml`): `HZ_ENABLE_CLICK_TO_DIAL`, user name **Click to Dial Enabled**, application `HZ`, values `Y`/`N` (lookup `YES_NO`). Only the **SITE** level is enabled and updatable; PRODUCT and USER are not (VERIFIED, REST `profileOptionLevels`). With `Y`, users can start a call by clicking a phone number (it also needs the telephony tasks of the same offering; GUESS). Use the skill to read the value, or to switch it on or off when the environment owner asks.

## Placeholders
```text
FSCR   = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS   = the gaps-filled folder (the one that holds common-features\)
W      = <GAPS>/common-features/scripts/rest_call.py   (runs FSCR's fusion_rest_client.py unchanged; shows Oracle's error text)
RUN    = a NEW empty work folder, OUTSIDE FSCR and outside any git repo
OPTION = HZ_ENABLE_CLICK_TO_DIAL
P      = /fscmRestApi/resources/11.13.18.05/profileOptions/<OPTION>
OLD    = the SITE value read in Step 2
NEW    = the value you set (Y or N, not OLD)
```
Call pattern (Git Bash): `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<RUN>"; timeout 120 python -B "<W>" "<FSCR>" <endpoint> [--method PATCH --body-file f.json --header "Content-Type=application/vnd.oracle.adf.resourceitem+json"] [--query k=v ...] --no-open-browser --output x.json > x.log 2>&1; echo rc=$?`. On `rc=1` the last lines of `x.log` hold Oracle's message.

## Prerequisites
1. Read access to `profileOptions`; for Step 3 the right to change profile values.
2. For a real change: the environment owner's approval, because SITE affects every user. For a **test** on a shared environment, only the test-and-restore of Steps 3 to 4, done within a minute.

## Step 1. Safe run and sign-in
Paths as `E:/...` (never `$PWD` or `/e/...`). On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens, headers or the server address: the JSON answers hold the address in `links`, so print only the fields you need (`--query onlyData=true` drops the links).

## Step 2. Read the option, levels and SITE value (read only, VERIFIED)
- `<P> --query onlyData=true` → `UserProfileOptionName` "Click to Dial Enabled", `SqlValidation` on lookup `YES_NO`.
- `<P>/child/profileOptionLevels --query onlyData=true` → SITE `EnabledFlag Y`, `UpdateableFlag Y`; PRODUCT and USER `N` (so no own-user route exists).
- `<P>/child/siteProfileOptionValues/SITE --query onlyData=true` → `{"LevelValue":"SITE","ProfileOptionValue":"<OLD>"}`. **Write OLD down** (VERIFIED: `N` on our environment). If this read gives HTTP 404 (no SITE row) or OLD is empty, **stop** and ask the environment owner (this skill only changes an existing SITE row).
- `<P>/child/userProfileOptionValues --query onlyData=true` → 0 rows.
- The two letters of a level are `EnabledFlag`/`UpdateableFlag`.

## Step 3. Set the SITE value (VERIFIED)
Write **both** body files before the first PATCH, so a test can set the value back at once. Every PATCH answer holds the server address in `links`: print only `ProfileOptionValue` and `LastUpdateDate`.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<RUN>"
echo '{"ProfileOptionValue":"<NEW>"}' > new.json; echo '{"ProfileOptionValue":"<OLD>"}' > old.json
S=<P>/child/siteProfileOptionValues/SITE; HD="Content-Type=application/vnd.oracle.adf.resourceitem+json"
show() { python -I -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d['ProfileOptionValue'], d['LastUpdateDate'])" "$1"; }
timeout 120 python -B "<W>" "<FSCR>" $S --method PATCH --body-file new.json --header "$HD" --no-open-browser --output p_new.json > p_new.log 2>&1; echo rc=$?; show p_new.json
timeout 120 python -B "<W>" "<FSCR>" $S --query onlyData=true --no-open-browser --output r_new.json > r_new.log 2>&1; echo rc=$?; show r_new.json
```
VERIFIED: `rc=0`, both lines show NEW and a new `LastUpdateDate`; each call takes about 1 to 3 s. For a real change (not a test), stop here.
- Use PATCH on the existing `SITE` row; never POST a second SITE row and never DELETE it.
- Dropped connection: do not PATCH again blindly; read the value first, then decide.

## Step 4. Set it back (test only, VERIFIED)
Right after Step 3, in the same shell:
```bash
timeout 120 python -B "<W>" "<FSCR>" $S --method PATCH --body-file old.json --header "$HD" --no-open-browser --output p_old.json > p_old.log 2>&1; echo rc=$?; show p_old.json
timeout 120 python -B "<W>" "<FSCR>" $S --query onlyData=true --no-open-browser --output r_old.json > r_old.log 2>&1; echo rc=$?; show r_old.json
```
PASS = both lines show OLD. On our runs the value was NEW for 3 to 7 seconds (Steps 3 and 4 pasted as one block; compare the `LastUpdateDate` of Step 3 and Step 4).

## Step 5. CSV export (read only, optional, VERIFIED)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code MCT_ENABLE_CLICK_TO_DIAL --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/export"
```
VERIFIED (about 60 s): 3 profile CSVs (`FND_APP_PROFILE_OPTION`, `ORA_FND_APP_PROFILE_OPTION_LEVEL`, `FND_APP_PROFILE_VALUE`), all with **0 rows**: the export leaves the seeded option and its seeded SITE value out, so it cannot be the read-back. Use REST (Step 2). The CSV import route was not run (it would need the seeded parent option row written in full; see `manage-search-profile-options` Step 6).

## Rules and limits
1. Steps 2 and 5 are safe anywhere. Step 3 changes the setting for every user: only with approval, or as the test-and-restore of Steps 3 to 4.
2. Always write OLD down before Step 3; a test is finished only when Step 4's read-back shows OLD.
3. Seen on one environment (release 11.13.26.10.0).

## Worked example (2026-11-25)
| Step | Value | Result |
|---|---|---|
| levels | SITE only | PRODUCT and USER not enabled |
| read | SITE `N` (OLD) | 0 USER values |
| PATCH `Y` | `Y` | read back `Y` |
| PATCH `N` (back) | `N` | read back `N`, 3 s after the change |
| fresh test (F) | N -> Y -> N | PASS, value Y for 4 s |
| re-test (R) after wording fix | N -> Y -> N | PASS, value Y for 5 s |
