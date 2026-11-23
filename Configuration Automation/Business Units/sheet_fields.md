# Business Units: fields for an upload sheet

Every field of Oracle's **Create Business Unit** screen as the Business Units folder takes it
(2026-10-26). "Key" is the request key (`request.json`, `--run`, `--plan`, `--run-batch`).
"Proven" = created by a real run and read back through REST (finBusinessUnitsLOV) and a second
Manage Business Unit export (business units ZZ_TEST_BU_3138_*, see CLAUDE.md > Sheet route).
Check a request read-only with `python "Business Units/browser_flow.py" --plan '<JSON>'`.

Scope (the user's decision): only these screen fields, then the required access. Business
functions, ledger, legal entity, currency, profit center, service providers and set assignments
are never set (a business unit made this way has 0 set assignments; proven not to matter for
price lists).

In the upload sheet (2026-10-26) this is the tab **Business Units**: Name *, Active, Location
(drop-down of Oracle's active locations, read when the sheet is made), Manager (the two people),
Default Set * (drop-down of the 37 set codes). Empty Location or Manager = none (the sheet sends
`"location": "none"`); empty Active = Yes. The page's preview runs `--plan` for all rows in one
call; Create runs `--run-batch` once; a value Oracle refuses makes the page ask the user (root
CLAUDE.md > Business Units module).

## Business unit (Create Business Unit)

| Oracle label | Key | Required | Allowed values | If empty | Rules and Oracle's messages | Status |
|---|---|---|---|---|---|---|
| Name | `name` | yes | text, 1 to 240 characters; spaces, ' - _ . allowed | - | No space at the start or end: Oracle keeps it and makes a **separate** business unit ("ZZ_TEST_BU_3138_CAPS " next to "ZZ_TEST_BU_3138_CAPS"), so the folder refuses it. 241 characters: Oracle refuses "Value ... for field Name exceeds the maximum length allowed" (JBO-27040). Already in Oracle (exactly, or only capitals differ): treated as that business unit, never sent or changed, only missing access added. Oracle itself refuses a capitals-only duplicate with "Failed to validate all rows in a transaction" (JBO-27023) and then drops **everything** sent with it. Listed twice in one request (capitals don't count): refused. | proven: 240 accepted, 241 refused, trailing space, capitals-only |
| Location | `location` | no | an active location **name** (130 locations, 123 in the common set); "none" (or null) = no location | left out: the standing default "Go Saas Lahore Office"; "none": no location | Unknown: "Oracle has no location called 'X' (a location can't be made here)." with the closest names; inactive: refused. A location outside the common set: its reference set is read from one Manage Business Unit export (from business units that use it or another location of the same set); a set no business unit uses: refused. | proven: Go Saas Lahore Office (COMMON), GoSaaS Labs Location (SET0001), none |
| Manager | `manager` | no | **only** "Yaqub, Younas" (person number 300000002688269) or "Smith, Aron" (4); full name either way round, or the person number | none | Any other: "'X' can't be the manager: only Yaqub, Younas or Smith, Aron can be chosen." Checked live (publicWorkers: same ListName and PersonId) before use. Oracle stores ManagerListName, PersonNumber, First/Last name and the person's dates; REST shows ManagerId = PersonId. | proven: both |
| Default Set | `default_set` | yes | one of Oracle's 37 reference data sets, by code or name | the standing default "001 CUSTOMER SITE" | Unknown: "'X' is not one of Oracle's 37 reference data sets." with the closest codes. Oracle's own answer to an unknown code: "Applying List binding LOV_DefaultSetCode ... leads to no matching row" (JBO-25072); only that row is dropped. | proven: 001 CUSTOMER SITE, ENTERPRISE, COMMON |
| Active | `active` | no | yes / no (also true / false) | yes | Other values: "Active must be yes or no." | proven: yes and no (Status I) |

## Access (always, after the business unit)

| What | Rule | Status |
|---|---|---|
| Order Manager and Pricing Administrator data access for Configuration.TEST (fallback Configuration) on the business unit | Checked before anything is sent: the user is active and holds both roles; otherwise **nothing is created** ("... doesn't hold the role X, so that access can't be given on the business unit; nothing is made."). Each row added through REST and read back (exactly one active row). If a row fails after the business unit is saved: "Business unit X saved and checked, access missing: <role> (<Oracle's reason>). A rerun adds only the missing access." | proven (rerun added only the missing role; the refusal itself was simulated) |

## Before Create and at Create

- **No Oracle needed:** name present, length (240), outer spaces, listed twice, Active value,
  manager is one of the two, unknown request keys.
- **Read-only (`--plan`):** exists / only capitals differ (finBusinessUnitsLOV), location
  active and its set (HCM locations; one export for a set other than COMMON), default set
  (setIdSetsLOV), manager as expected (publicWorkers), access user and roles, access already
  on an existing business unit (dataSecurities).
- **Only at Create:** anything else Oracle refuses. One Setup task process for all new
  business units; a refused row is dropped and the others are saved (default set, name length);
  a refusal of the whole business object (JBO-27023, seen for a capitals-only duplicate) drops
  all of them. Oracle's log names a failed row only by internal keys, so the business unit
  missing afterwards is the failed one; with several failures every reason is given without
  saying which is which. A rerun skips what is saved.

## Not proven

A real access refusal by Oracle (simulated only); Oracle refusing a location or manager value at
Create (the folder never sends one it hasn't checked); a real refusal through the page's `--run`
(the code path is the batch's, proven there); more than 3 business units in one go; names with
characters other than letters, digits, spaces and ' - _ . ; whether Oracle checks Name on the
screen before Save (the screen was not used).

## Checked again 2026-10-26

Every refusal seen is checked in the preview. Unsaved Create Business Unit screen: the Name box holds 240
characters (no message on Tab). Not proven (only at Create): a name equal to another organization's name,
characters beyond those tried, location and default set pairs.
