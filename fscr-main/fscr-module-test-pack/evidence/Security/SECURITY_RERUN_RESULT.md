# Security re-check with boss_scope set (2026-11-24)

Read-only re-check of the 6 Security tasks after `boss_scope` was set. Nothing was created, changed or loaded in Oracle. No token, user name or sign-in value is shown here.

## What changed

- `core/auth/fusionEnv.properties` (pack working copy, git-ignored): `boss_scope=urn:opc:resource:fusion:etia-test:boss/`. Nothing else changed; `rmc_scope` stays empty. The file was not copied anywhere.
- Format: FSCR takes the exact scope string registered on the sign-in app (auth skill `SKILL.md`: "Use the exact scope registered…"). Oracle accepted the value as given.
- Sign-in on port 8765 (`fusion_login.py --service boss`, then standard): both **Login complete**.
- BOSS token claims (names only): `aud` = `urn:opc:resource:fusion:etia-test:boss`, `scope` = `/`. **BOSS present, Risk Cloud absent.**
- Standard token: `scope` = `urn:opc:resource:consumer::all` (Fusion). No Risk scope.

## Results

| # | Task | Read check (this run) | Result | Verdict |
|---|---|---|---|---|
| 1 | Activate Audit Policies | 8 of 8 `check-auditstatus` reads: HTTP 200, SUCCESS (2 ON, 6 NONE) | Works (read) | Blocked by safety: enabling changes an environment-wide audit setting |
| 2 | Activate Algorithms | BOSS GET `referenceDataValues` 200 (items, hasMore), GET with `attributeCode='PROCESSES.ORA'` 200, GET `availableOfferings` 200, GET `featureSelectedChoices` 204 (no content) | Works (read) | Blocked by missing Fusion role (Risk Administrator) and by safety: live publish changes existing algorithms. Likely runnable with approval once the role is added |
| 3 | Add EPM Data Sources | BOSS GET `connectorDefinitions` 200, 0 records. Risk Cloud GET: `Error: Missing required OAuth scope property: rmc_scope` | BOSS read works, Risk read blocked | Blocked by Risk scope (create is a Risk Cloud POST); also needs real EPM connector details |
| 4 | Add Other Data Sources | Same two reads as task 3: BOSS 200 / 0 records; Risk Cloud blocked by `rmc_scope` | BOSS read works, Risk read blocked | Blocked by Risk scope |
| 5 | Assign Default Process Owners | BOSS GET `referenceDataValueProperties/$views/detailed` 200, 0 records (no owners set yet); HCM GET `publicWorkers` 200 | Works (read) | Blocked by missing Fusion role (Risk Administrator) and by safety: assigns existing workers as owners (BOSS `$bulk` POST) |
| 6 | Assign Risk Power User Role | HCM GET `selfDetails` 200; SCIM GET Roles `ORA_GTG_RISK_POWER_USER_JOB` 200, 1 found; GET `advancedAccessRequests` 200, 0 | Works (read) | Blocked by safety: submits an access request that changes an existing user's roles. Needs Risk Administrator first (skill precondition) |

Note: the first `selfDetails` read used `fields=PersonId` and returned HTTP 400; repeated with `fields=Username` (as the skill says) it returned 200.

Not run (by rule): the BOSS `connectorDefinitions/$query` read is an HTTP POST, so a plain GET was used instead. No publish, create, `$bulk`, access request or `update-auditstatus` was run. The 8 audit reads use Oracle's read-only `check-auditstatus` action (same as on 19 Nov).

## Signed-in user's roles (read-only SCIM check)

Has `ORA_FND_IT_SECURITY_MANAGER_JOB` and Application Implementation Consultant. Has **no Risk Management role**: not `ORA_GTG_RISK_ADMINISTRATOR_JOB`, not `ORA_GTG_RISK_POWER_USER_JOB`. The assign-initial-users skills stop when the user lacks Risk Administrator (`assign-initial-users/scripts/risk_administrator_precondition.py`).

## What we need from the admin

1. Add the **Risk Cloud** resource scope to the sign-in app "ETIA TEST - FSCR" (Token issuance policy > Add scope), and send us the exact registered value for `rmc_scope`. Needed for tasks 3 and 4.
2. Give the test user **Risk Administrator** (`ORA_GTG_RISK_ADMINISTRATOR_JOB`) on ETIA-TEST. Needed for tasks 2, 5 and 6.
3. A written OK before any load that changes existing settings or users (tasks 1, 2, 5, 6), and real EPM connector details for task 3.

## Suggested tracker wording (Security row)

> boss_scope now set; BOSS sign-in works. Read checks: 6 of 6 tasks read OK on Fusion/BOSS (audit 8/8 status reads 200; algorithms, process owners, power-user reads 200). Loads not run: tasks 3-4 need the Risk Cloud scope (rmc_scope missing, admin request open); tasks 2, 5, 6 need the Risk Administrator role; tasks 1, 2, 5, 6 change existing settings or users and need approval. Execution: blank (blocked by access and safety).

Execution stays **blank**: no load was approved or done.

## Clean-up

Sign-in listener on 8765 closed after each login; no server, headless browser or Python process left running (checked at the end).

## Time log

| Part | Start | Finish | Minutes |
|---|---|---|---:|
| Working | 24/11/2026 16:45 | 24/11/2026 17:05 | 14 |
| Waiting (sign-in, Oracle reads) | 24/11/2026 16:45 | 24/11/2026 17:05 | 6 |

| Start | Finish | Minutes |
|---|---|---:|
| 24/11/2026 16:45 | 24/11/2026 17:05 | 20 |
