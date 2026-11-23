# Check: what is boss_scope for the 6 Security tasks?

Read-only check from the pack files. Nothing was changed and nothing was created in Oracle. No sign-in values are shown here.
Paths are inside `fscr-main/fscr-module-test-pack/` unless noted. Skill folder: `pillars/erp/risk-and-security/`.

## 1. Which of the 6 skills say they need boss_scope or a BOSS / Risk Cloud scope?

| Task | Needs | File and line |
|---|---|---|
| Activate Audit Policies | Neither. It names only `core.fusion-api.audit-setup`. The text "boss" does not appear in its SKILL.md. | `activate-algorithms/activate-audit-policies/SKILL.md` (no match) |
| Activate Algorithms | BOSS, but it does not name `boss_scope`. | `activate-algorithms/activate-algorithms/SKILL.md:79` "BOSS read access to provided algorithms and algorithm contexts"; `:112` "through the Core BOSS client" |
| Add EPM Data Sources | `boss_scope` and `rmc_scope` (Risk Cloud) | `add-other-data-sources/add-epm-data-sources/SKILL.md:208` "This POST is a read-only BOSS query. It uses `boss_scope`"; `:289` "configured Risk Cloud OAuth `rmc_scope`"; `:160-161` "approved BOSS or Risk Cloud client, required OAuth scope" |
| Add Other Data Sources | `boss_scope` and `rmc_scope` | `add-other-data-sources/add-other-data-sources/SKILL.md:286` "read-only BOSS query using `boss_scope`"; `:152` "approved Risk Cloud client, `rmc_scope`, and create/read privileges" |
| Assign Default Process Owners | BOSS, not named `boss_scope` | `assign-initial-users/assign-default-process-owners/SKILL.md:98` "BOSS read access to BusinessUnit, workerAssignmentExtracts, managerHierarchy, User, Worker …" |
| Assign Risk Power User Role | BOSS plus SCIM, not named `boss_scope` | `assign-initial-users/assign-risk-power-user-role/SKILL.md:50-51` "BOSS read access to Risk Management reference data and owner properties." / "Fusion SCIM read access and Advanced Access Request submit privilege" |

The link from "BOSS" to `boss_scope` is made by the auth skill: `core/auth/fusion-oauth-authentication/SKILL.md:90` (the `boss` service uses `boss_scope`). The BOSS client refuses to run without it (`core/fusion-api/rest-api-client/SKILL.md:59` sends `/api/boss` endpoints to `boss-rest_client.py`).

## 2. Where is boss_scope set? Is it in the sign-in file?

- It is set in `core/auth/fusionEnv.properties`, field `boss_scope` (line 7). In this pack the field is **empty**. The other scope fields `ai_scope`, `fusion_common_scope` and all optional ones, including `rmc_scope` (line 13), are also **empty**. Only `scope` is **filled**.
- The sign-in file (`fscr-signin-values.txt`, in the folder above the pack) has no `boss_scope` field at all: **missing**. Its copy block (lines 20-26) has five fields: environment, restBaseUrl, clientId, redirectUrl and `scope` (filled). Line 16 says "the other scope lines stay empty; the playbook steps do not use them".
- The file header says it was "Shared by Abdullah"; the name Younas does not appear in it, so who prepared it is **not stated**.
- The auth skill says a blank service scope blocks that service (`core/auth/fusion-oauth-authentication/SKILL.md:104` "Missing or blank service scopes block authentication; never substitute `scope` or `boss_scope`…").

## 3. Where does the value come from?

- Oracle side. The onboarding guide says to add resource scopes to the sign-in app in the Identity Domain, under "Token issuance policy > Add scope". It lists "Oracle Boss Cloud (Spectra)" as the resource that gives `boss_scope`, and "Risk Cloud" as the optional one for `rmc_scope` (`core/getting-started/onboarding/references/iam-client-application-setup.md:77` and `:85`).
- It says to use the exact registered value and not to build it from the pod name (`iam-client-application-setup.md:92`; also `core/getting-started/onboarding/references/fusion-environment-configuration.md:35` "Exact approved BOSS service scope").
- The exact value for ETIA-TEST: **not stated**.
- Whether the ETIA-TEST sign-in app already has the Boss and Risk Cloud scopes added: **not stated**. `fscr-access-requirements.md:29` only says the other three scopes are blank on this machine and that Run 38 worked with `scope` alone.

## 4. If boss_scope were set, what could be read and loaded?

Assumes Oracle has the scope registered on the app (not stated, see 3). "Loaded" means a live change.

- **Activate Audit Policies:** does not need it. Read already worked with `scope` (8 of 8 status reads). Loading stays blocked: it changes an existing environment-wide audit setting.
- **Activate Algorithms:** read (published inventory and preview) would work. Loading stays blocked: live publish changes existing algorithms in approval-gated BOSS posts (`SKILL.md:77`, `:140`), and the skill recommends audit policies first.
- **Add EPM Data Sources:** the BOSS read check would work. Loading stays blocked: the create needs `rmc_scope` (also empty) and real EPM connector details, and the skill stops if connector type or name is missing.
- **Add Other Data Sources:** the BOSS read check would work. Loading stays blocked: the create needs `rmc_scope` (empty) and a Risk Cloud client with create rights.
- **Assign Default Process Owners:** reads of users, hierarchy and owners would work. Loading stays blocked: it needs existing users and changes existing owners (`SKILL.md:95`).
- **Assign Risk Power User Role:** reads would work. Loading stays blocked: it submits access requests for existing users (`SKILL.md:47`), which is a change to existing accounts.

So setting `boss_scope` alone would unlock reads for 5 of the 6 tasks (Activate Algorithms, the two Assign tasks, and the BOSS check of the two data source tasks, which still need `rmc_scope` to create). The 6th, Activate Audit Policies, can already be read. It would unlock no safe load, because none of the 6 creates a stand-alone FSCRT_ record that the skills describe. That last point is my reading of the skills, not a line in a file.

## 5. Was anything I told you earlier wrong or unclear?

- "boss_scope is blank" was correct for `fusionEnv.properties`. I confirmed it with the client's own error "Missing required OAuth scope property: boss_scope".
- "Not in the sign-in values" was correct, but unclear: it is missing from the file on purpose (line 16), not lost or mistyped.
- Unclear: I wrote "BOSS scope and a Risk Cloud client" for the two data source tasks. More exactly they need `boss_scope` and `rmc_scope`, and both are empty.
- Unclear: I never checked whether Oracle itself allows these scopes for the sign-in app. The block I saw is local configuration. Whether Oracle would also refuse is **not stated** in any file.
- Not wrong, but worth knowing: Activate Audit Policies does not need boss_scope at all. I marked it Not done because enabling changes an existing setting, not because of the scope.
- The tracker row and RESULT.md say "BOSS scope missing" for 5 of 6 tasks. That is right for 5, but the reasons are mixed with existing-user and existing-setting risks, as listed in section 4.
