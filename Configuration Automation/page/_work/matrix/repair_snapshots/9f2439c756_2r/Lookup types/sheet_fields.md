# Standard Lookups: fields for an upload sheet

Every field of Oracle's **Manage Standard Lookups** screen as the Lookup types folder takes it
(2026-10-25). Labels are Oracle's screen labels; "key" is the request key (`lookups.json` and the
page's `--run`). "Proven" = created by a real run and read back through REST (types
ZZ_TEST_LK_8806_*, see CLAUDE.md > History). Check a request read-only with
`python "Lookup types/run.py" --plan '<JSON>'`.

In the upload sheet (2026-10-25) these are two tabs: **Lookup Types** (one row per NEW type) and
**Lookup Codes** (one row per code), joined by Lookup Type written exactly (capitals and spaces
count). A code row whose type isn't on the Lookup Types tab adds that code to a type Oracle already
has (User or Extensible; System refused). A type row that already exists is skipped and its codes
are added to it. Nothing existing is changed.

## Lookup type (Search Results grid)

| Oracle label | Key | Required | Allowed values | If empty | Rules and Oracle's messages | Status |
|---|---|---|---|---|---|---|
| Lookup Type | `lookup_type` | yes | text, max 30 | - | New type: no small letters, not starting with ORA (both refused: "JBO-25017: New entity row ... cannot be created"); spaces, "-" and "." allowed. An existing type: any name, it only gets new codes. | proven (accepted: spaces, "-", "."; refused: small letters, ORA) |
| Meaning | `meaning` | new type: yes | text, max 80 | - | Unique among lookup types: "Another lookup type already has the same meaning. (FND-7104)" | proven |
| Item Description | `description` | no | text, max 240 | empty | - | proven |
| Module | `module` | new type: yes | an Oracle module NAME (Module dialog; 500+ modules) | - | Unknown name -> "Oracle has no module called 'X'. Close matches: ..."; a name Oracle has twice -> not supported yet; a module no lookup uses -> can't be resolved | proven: Order Management, Concepts, Oracle Middleware Extensions for Applications |
| Lookup Configuration Level | - | set by Oracle | User for a new type | User | can't be chosen | proven (U) |
| REST Access Secured | `rest_access_secured` | no | Secure, Authenticated, Anonymous | Secure | - | proven: all three |

## Lookup codes (Standard Lookup Type: Lookup Codes grid)

| Oracle label | Key | Required | Allowed values | If empty | Rules and Oracle's messages | Status |
|---|---|---|---|---|---|---|
| Lookup Code | `code` | yes | text, max 30; small letters and spaces allowed | - | Once per type (Oracle silently keeps the last row of an import; REST: "Too many objects match the primary key"). On an existing type an existing code is skipped, never changed. | proven ("my code x", "p 2") |
| Display Sequence | `display_sequence` | no | whole number, 0 or more | empty | "abc" refused ("Cannot create an object of type:java.lang.Long ... value:abc"); Oracle accepted -1 (the folder keeps 0 or more) | proven: 0, 1, 5, 7, 10 |
| Enabled | `enabled` | no | yes / no | yes | - | proven: yes and no |
| Start Date | `start_date` | no | YYYY-MM-DD or "today" (Oracle's today minus one day) | empty | - | proven |
| End Date | `end_date` | no | YYYY-MM-DD | empty | After Start Date: "Start Date must be before End Date" | proven (refusal and valid dates) |
| Meaning | `meaning` | yes | text, max 80 | - | Once per type, capitals count, also against existing codes: "Lookup Type X already has lookup code meaning Open. (FND-7103)" | proven |
| Item Description | `description` | no | text, max 240 | empty | - | proven |
| Tag | `tag` | no | text, max 150 | empty | meaning depends on the type | proven |

A new type may have no codes ("0 codes"): allowed, not proven by an import yet.

## Which types take new codes

| Level | New codes | Status |
|---|---|---|
| User | yes; existing codes untouched | proven (H1 added to ZZ_TEST_LK_8806_ALL) |
| Extensible | yes; Oracle's codes untouched | proven (ZZ_TEST_LK_8806 added to ORA_DGV_SERVICE_TYPE) |
| System | no: refused before anything is sent | folder rule (Oracle's own answer not tried on purpose) |

## Before Create and at Create

- **No Oracle needed:** required fields, lengths, code twice, code meaning twice, dates, Display
  Sequence, access value.
- **Read-only (`--plan`, REST; the screen only for a module looked up the first time):** does the
  type exist, its level and codes (which codes will be added / skipped), type meaning used, code
  meaning used in the existing type, new-type name rules, module name -> ID.
- **Only at Create:** anything else the import refuses; the folder then reads Oracle's log and
  says per type and code "Saved" / "Not saved (reason)". One refused row drops its whole type
  (the other types of the run are saved); a rerun skips what is saved.

## Not proven

Screen Save behaviour (the import was tested); a System type through REST; an existing type
re-sent with different values in the import; a module no lookup uses; module names Oracle has
twice; the highest number of codes (1000 worked); translations and the code flexfield.

## Checked again 2026-10-26

Oracle's meaning and code checks are exact (capitals count), proven by real creates: type
ZZ_TEST_LK_6142_TMEAN with another type's meaning in other capitals, codes A2 "ALPHA" (next to "Alpha") and
"a1" (next to "A1") in ZZ_TEST_LK_8806_ALL. New in the preview: two new lookup types of one upload with the
same meaning (FND-7104), and End Date after Start Date when one of them is "today".
