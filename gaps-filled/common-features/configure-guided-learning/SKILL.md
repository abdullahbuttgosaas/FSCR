---
skill_id: "gosaas.gap-fills.common-features.configure-guided-learning"
name: "Configure Guided Learning: read and set the SITE profile option FND_GUIDED_LEARNING_ENABLED by REST (GoSaaS gap fill)"
description: "Reads the profile option Guided Learning Enabled (FND_GUIDED_LEARNING_ENABLED), its levels and its SITE value, and sets the SITE value through the REST child siteProfileOptionValues (FSCR's REST client), with a read-back. The task has no CSV package. Tested as test-and-restore on a shared environment. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 13, 2026-11-25. Tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FND_GUIDED_LEARNING_ENABLED"
task_name: "Configure Guided Learning"
type: "rest"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
status: "tested (batch 13, test-and-restore)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client (through the GoSaaS wrapper rest_call.py)"
  - "gap skill enable-click-to-dial (the same steps, for another option)"
side_effects:
  - "Step 2 is read only."
  - "Step 3 changes the SITE value: guided learning turns on or off for every user."
  - "Step 4 (test only) sets the old value back."
---

# Configure Guided Learning (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.

## What it is and when to use
Guided learning (Oracle Guided Learning, in-app guidance) is switched on or off by one profile option: `FND_GUIDED_LEARNING_ENABLED`, user name **Guided Learning Enabled**, application `FND`, values `Y`/`N` (its `SqlValidation` uses lookup `FND_SANDBOX_YESNO_TYPE`, not `YES_NO` as for click to dial; VERIFIED). It is the only option whose code or user name holds "Guided Learning" (VERIFIED, REST search); that it is the option behind this task is a **GUESS** from its name and description (the task has no CSV package that would name it). Only the **SITE** level is enabled and updatable (VERIFIED). The guided-learning service itself (application id, content) is set up in Oracle Guided Learning, not here (GUESS).

There is **no CSV route**: FSCR's export says `CSVExportImportSupportedFlag is N for ORA_FND_GUIDED_LEARNING_ENABLED` and makes no file (VERIFIED).

## Placeholders and steps
Use the skill `<GAPS>/common-features/enable-click-to-dial/SKILL.md` (placeholders, Step 1 sign-in, call pattern, Steps 2 to 4) with these values:
```text
OPTION = FND_GUIDED_LEARNING_ENABLED
P      = /fscmRestApi/resources/11.13.18.05/profileOptions/FND_GUIDED_LEARNING_ENABLED
```
- **Step 2 (read, VERIFIED):** the option read shows `UserProfileOptionName` "Guided Learning Enabled" and lookup `FND_SANDBOX_YESNO_TYPE`; levels (EnabledFlag/UpdateableFlag) SITE `Y/Y`, PRODUCT and USER `N/N`; SITE value OLD = `Y` on our environment; 0 USER values. Write OLD down.
- **Step 3 (VERIFIED):** PATCH `<P>/child/siteProfileOptionValues/SITE` with `{"ProfileOptionValue":"<NEW>"}` (NEW = the other of Y/N) → `rc=0`, read back NEW.
- **Step 4 (test only, VERIFIED):** PATCH back to OLD → read back OLD. Paste Steps 3 and 4 of the click-to-dial skill as one block (both body files written first): on the tests the value was `N` for 3 to 5 seconds. Take OLD from your own read, not from this example.
- Skip the click-to-dial skill's Step 5 (no CSV package for this task).

## Rules and limits
1. Turning guided learning **off** hides in-app guidance from every user; on a shared environment only test-and-restore, within a minute, and only when OLD is known.
2. Never POST a second SITE row and never DELETE it; never set a USER or PRODUCT value (not enabled).
3. Seen on one environment (release 11.13.26.10.0).

## Worked example (2026-11-25)
| Step | Value | Result |
|---|---|---|
| CSV export | - | refused by FSCR (flag N), no file |
| read | SITE `Y` (OLD) | SITE only level |
| PATCH `N` | `N` | read back `N` |
| PATCH `Y` (back) | `Y` | read back `Y` |
| fresh test (F) | Y -> N -> Y | PASS, value N for 4 s |
| re-test (R) after wording fix | Y -> N -> Y | PASS, value N for 3 s |
