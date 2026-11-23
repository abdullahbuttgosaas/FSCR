# FSCR access requirements: ETIA-TEST

What a new person's Oracle account needs so that every FSCR step in the module test pack's playbook works on
ETIA-TEST: sign-in, setup data export, Data Loader import, Task Hook and Run Book.

This file sits outside the pack and holds no sign-in values. The values are in `fscr-signin-values.txt`, which
Abdullah shares with one person at a time.

**Confirmed** means it was seen in one of our runs or is written in the FSCR docs or code in the pack.
**Assumed** means it is a reasonable reading but has not been shown. Nothing here was tested by changing users,
roles or clients, because this work was read-only in Oracle.

Sources (all inside the pack unless noted):
- [A] `core/getting-started/onboarding/references/iam-client-application-setup.md`, from Oracle's "OAuth Setup for FSCR 26D" document
- [B] `core/auth/fusion-oauth-authentication/SKILL.md` and `scripts/fusion_auth.py`
- [C] `core/getting-started/implementation-users/SKILL.md` and `references/oracle-26b-hcm-implementation-users.md` (FSCR's role policy, grounded in Oracle 26B "Roles and the Allowed Activities")
- [D] the `required_privileges` sections of `core/data-loader/SKILL.md`, `core/runbook/SKILL.md` and `shared/setup-export/fsm-csv-export/SKILL.md`; the Data Loader code
- [R] our run logs: Run 38 (cold test) and earlier runs (`_fscr_run_*`, outside the pack)

## 1. The sign-in app (OAuth client)

| # | Statement | Status |
|---|---|---|
| 1.1 | FSCR signs in through one public OAuth client of type **Mobile Application**, using PKCE with no client secret. | Confirmed [A][B][R] |
| 1.2 | **One Client ID serves every person.** The Client ID identifies the app, not the user, and each person signs in with their own Oracle user name and password in the browser. Nobody needs their own client. | Confirmed by design [A][B]; Assumed for ETIA-TEST, because only one user has signed in with it in our runs [R] |
| 1.3 | An administrator only needs to enable a person if the app has **"Enforce grants as authorization"** turned on. Then each user or group must be added on the app's Users or Groups tab, and "without those assignments, their FSCR login will not work". | Confirmed [A] |
| 1.4 | Whether ETIA-TEST's FSCR app has "Enforce grants" turned on. | **Assumed off** (not checked: that needs the Identity Domain console, and this work was read-only) |
| 1.5 | The app must be **Active**, allow the Authorization code grant, allow the non-HTTPS loopback redirect, and register exactly `http://127.0.0.1:8765/oauth/callback`. | Confirmed [A]; working on ETIA-TEST [R] |
| 1.6 | The scope in `scope` (Oracle Applications Cloud / Fusion) is the only scope the playbook needs. FSCR also lists `ai_scope`, `boss_scope` and `fusion_common_scope` as "required" in its template, but every playbook step in Run 38 worked with `scope` alone, and the other three are blank on this machine. | Confirmed [R] |
| 1.7 | Each person's computer enrolls the same three values (Fusion URL, environment name, Client ID) once, in its own `~/.fusionaim/oauth-trust.json`. Nothing is shared between computers. | Confirmed [B] |
| 1.8 | Signing in with the IAM client does not give any Oracle rights. "IAM application assignments do not replace Fusion roles or data access." | Confirmed [A] |

## 2. Roles in the person's Oracle account

| # | Statement | Status |
|---|---|---|
| 2.1 | A user of their own in ETIA-TEST. Records, Run Books and loads are made in that user's name. | Confirmed [R] |
| 2.2 | **Application Implementation Consultant** (`ORA_ASM_APPLICATION_IMPLEMENTATION_CONSULTANT_JOB`) is FSCR's minimum role for setup work: "performing all setup tasks, managing setup data … export/import … export/import process submission and monitoring, implementation project management". | Confirmed as FSCR's policy [C] |
| 2.3 | That role is enough for the playbook's **setup data export** (`setupTaskCSVExports`) and **FSM import** (`setupTaskCSVImports`). | Assumed (it matches Oracle's role description [C]; our runs used one user and did not list its roles) |
| 2.4 | **Data Loader**: the user needs to "view the selected Data Loader business object and data-set status" and to "upload loader content to UCM and initiate the selected Data Loader operation". For FSM packages the UCM account is `setup$/functionalSetupManager$/import$`. | Confirmed [D] |
| 2.5 | Application Implementation Consultant includes the UCM upload right for that FSM import account and the Data Loader data-set REST access (`hcmRestApi/.../dataLoaderDataSets`). | Assumed |
| 2.6 | **Run Book**: the user needs to "view Oracle Fusion Run Book journeys, tasks …" and to "create or merge Run Books, add or update Run Book tasks". Run Books are journeys of type `RBK` and are listed per user (`findSelfJourneys`), so each person sees only their own. | Confirmed [D] |
| 2.7 | The role that grants Run Book creation on ETIA-TEST. | Assumed: covered by Application Implementation Consultant (not documented by FSCR) |
| 2.8 | **Task Hook** needs no Oracle rights. It runs locally on the person's computer. | Confirmed [D: `required_privileges: []`][R] |
| 2.9 | FSCR's planning, project setup and the kit's scripts need no Oracle rights. | Confirmed [D][R] |
| 2.10 | Some modules' setup tasks need their own task privileges (FSCR: "task-specific setup data privileges"). | Confirmed [C]; which ones depends on the module |
| 2.10a | **Data access** to the business units a task uses (for example Pricing Administrator data access on a test BU). Without it Oracle rejects the record as an invalid business unit, not as "forbidden". | Confirmed [R: Run 01 price lists] |
| 2.11 | IT Security Manager, Application Diagnostic Administrator, HCM data roles and AI Agent Studio roles are in FSCR's full implementation-user policy but **not** needed for the playbook. | Assumed (no playbook step uses them) |

## 3. What a person sees if something is missing, and what to do

| Missing | What they see | What to do | Status |
|---|---|---|---|
| Values in `fusionEnv.properties` differ from the trust answers | `Environment name and OAuth client ID must match the selected Fusion configuration` | Copy the values file again exactly. | Confirmed [B] |
| Trust file made with other values | `OAuth client is not enrolled for this environment` or `Fusion URL differs from the enrolled environment` | Re-enroll for ETIA-TEST only, with `fusion_auth_setup.py trust ... --replace`. | Confirmed [B] |
| A scope line is blank | `Missing required OAuth scope property: scope` | Copy `scope` from the values file. | Confirmed [B] |
| Fusion URL cannot be reached | `Cannot reach the Fusion login page over verified HTTPS; no trust policy was created` (or "timed out") | Check the network or VPN and try once more. | Confirmed [B]; a timeout was seen once in Run 30 [R] |
| Person not assigned to the app ("Enforce grants" on) | An Oracle sign-in page error saying the user is not authorized for the application. The exact wording comes from Oracle Identity Domains, not from FSCR. | The admin adds the user or their group to the FSCR app. | Wording Assumed; cause Confirmed [A] |
| Redirect or scope wrong in the app | An Oracle sign-in page error about the redirect URI or `invalid_scope`. | Fix the value; never change the registered redirect for one person. | Assumed |
| No UCM upload right | `The authenticated Fusion user does not have permission to upload files to the UCM account <account>. No data load was initiated.` | Ask a Fusion security administrator for the upload right. Do not sign in again or retry. | Confirmed [D] |
| A role is missing for export, import or Run Book | HTTP **403** from the REST call after a good sign-in. FSCR refreshes the sign-in and retries once for reads only, then stops. | Ask the admin for the role (section 2). A new sign-in does not help. "A repeated 403 may require role or data-access diagnosis rather than another login." | Confirmed [B][D]; exact text Assumed |
| Data access on a business unit missing | HTTP 400: `Attribute set with value … for BusinessUnitId … failed` and `The value of the attribute BusinessUnit isn't valid.` | The admin grants the person data access for that role on that BU (Run 01: Pricing Administrator on the FSCRT test BUs). FSCR does not check this in advance. | Confirmed [R] |
| Signed-in session expired | HTTP 401 | Sign in again (`fusion_login.py`). | Confirmed [B] |

## 4. Run log findings

Searched by a helper agent: 20 login logs and the reports of every `_fscr_run_*` folder, `_gap_fills`, `_fscr_evidence_pack` and the cold test.

| Step | What our runs show | Status |
|---|---|---|
| Sign-in | No scope, client or authorization error, ever. Network timeouts (`WinError 10060`) in Runs 06, 08 and 30, and a callback timeout twice in Run 27b; each worked on the next try. Run 03: an expired token was renewed without a password because the browser was still signed in. | Confirmed |
| Export | No access error. The 404s and 500s seen (Run 02) were missing records, not rights. | Confirmed |
| Create / load | The only access problem in all runs: Run 01 price lists, missing BU data access (section 3). Data Loader and FSM imports never failed for rights; failures were data rules (Run 04, `JBO-27014`). | Confirmed |
| Task Hook | No Oracle access error (Run 03's block came from the local permission setting, not Oracle). | Confirmed |
| Run Book | No access error. Two large creates timed out on our side, but Oracle created both (Runs 30, 33). | Confirmed |
| Other users | Every run used the same single test account and Client ID, so no second person has yet signed in with it. That is why 1.2 and 1.4 stay Assumed for ETIA-TEST until a second person signs in. | Confirmed (one user only) |
| The test user's roles | No log lists them, so the role statements in section 2 rest on FSCR's docs, not on a role list we saw. | Confirmed (gap) |

**Simplest proof for a new person:** sign in, then run one read-only export from the playbook (Step 4, recipe step 1). If it works, sign-in, scope and export rights are fine. Upload rights show only at the first load.

## Time log

| Start | Finish | Minutes |
|---|---|---:|
| 17/11/2026 17:26 | 17/11/2026 17:35 | 9 |
