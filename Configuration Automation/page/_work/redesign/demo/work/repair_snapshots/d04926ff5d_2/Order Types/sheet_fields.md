# Order Types: fields for an upload-sheet tab

Read-only survey, 2026-10-25. Sources: `Order Types/CLAUDE.md`, `Order Types/browser_flow.py`,
`Order Types/ordertypes.json`, `common/page.py`, the output of `--spec` and
`--options lookup_type`. Nothing was created in Oracle, no Oracle screen was opened, and no code
was changed. `--options lookup_type --all` was tried, but Oracle could not be reached from this PC
(the host name did not resolve), so the live list was **not** read today.

There is no Order Types tab in `page/sheet_definition.json` or `page/sheet_registry.json` yet.

## 1. Fields, in the order the automation uses them (`--spec`)

One row = one order type (= one lookup code in the order type list).

| # | Key | Label (page form) | Oracle screen name / field | Required | Type | If empty | Who sets it | Example that worked in a real create |
|---|---|---|---|---|---|---|---|---|
| 1 | `code` | Order type code | Lookup Code / `LookupCode` | **yes** | text, max 30, case-sensitive | - | you | `ZZ_TEST_9464` (REST), `ABCABC1` (fallback) |
| 2 | `meaning` | Name shown to users | Meaning / `Meaning` | **yes** | text, max 80, must be unique in the list (case is ignored) | - | you | `ABC ABC Order Type 1` (fallback); `ZZ_TEST_9464` (REST, same as the code) |
| 3 | `description` | Description | Item Description / `Description` | no | text, max 240 | empty | you | `Page interface test` (REST); `Custom POC Order Type for Automation Testing` (fallback) |
| 4 | `display_sequence` | Position in the list | Display Sequence / `DisplaySequence` | no | number, whole, 0 or more | **the next number after the highest one already there** (printed as a NOTE) | the automation, unless you give one | `10` given by you (ABCABC1, fallback); `24` and `28` assigned automatically (REST) |
| 5 | `enabled` | Active | Enabled / `EnabledFlag` | no | yes/no | yes (`Y`) | you (default yes) | yes (every test so far) |
| 6 | `start_date` | Start date | Start Date / `StartDateActive` | no | date `YYYY-MM-DD` or `today` | empty (active right away) | you | `2026-10-19` (ABCABC1), `2026-10-17` (ZZ_TEST_4833), both by the fallback |
| 7 | `end_date` | End date | End Date / `EndDateActive` | no | date `YYYY-MM-DD` or `today` | empty | you | **none yet** |
| 8 | `tag` | Tag | Tag / `Tag` | no | text, max 150 | empty | you | **none yet** |
| 9 | `lookup_type` | Order type list | the lookup type (not a field of the code) | no | pick from a list | `ORA_DOO_ORDER_TYPES` (Type of Sales Order) | you (normally left at the default) | `ORA_DOO_ORDER_TYPES` (every create) |

- No field has "required when" or "shown when" set.
- Groups in `--spec`: Order type code and Name shown to users are under "main"; the rest are under "more options".
- Help lines: code "Up to 30 characters; capital and small letters count as different."; meaning
  "Up to 80 characters; no other order type may already use it."; position "Empty: the next
  number after the last order type."; start date "Empty: active right away. 'today' means
  Oracle's today minus one day."
- The page form trims outer spaces from text. A request file with outer spaces is refused instead.
- Unknown keys are refused, both on the page and in the request file.

## 2. Pick-from-a-list fields

Only one: **Order type list** (`lookup_type`). It belongs to the whole request, not to a code.
- Sample list (`--options lookup_type`, read today without Oracle): one value,
  `ORA_DOO_ORDER_TYPES` labelled "Type of Sales Order". It is **proven by real creates**
  (ABCABC1, ABCABC2, ZZ_DEMO_ORDER22, ZZ_TEST_6387, ZZ_TEST_4833, ZZ_TEST_2868, ZZ_TEST_9464).
- Full live list (`--options lookup_type --all`): it looks up `ORA_DOO_ORDER_TYPES`,
  `DOO_ORDER_TYPES` and any type with the meaning "Type of Sales Order". On 2026-10-21 it
  returned only the same one value. It could not be read today (no connection).
- If any other value is typed, `--run` checks it against the live list. For example, "Nope" gave NOT_IN_ORACLE.
- Active is yes/no rather than a list.

Suggestion for the sheet: leave this column out, or give it a fixed value of Type of Sales Order.
There is only one value, and every `--run` uses that value by default.

## 3. Behaviour

**Existing order type:** it is skipped and never changed. The check is **by code only, exact
and case-sensitive**: the code is compared with every code in the list, read through REST
(fallback: the fresh export). The page returns `skipped: true` with the existing values. The
meaning is not used to decide whether a code exists.

**Meaning already used** by another code (compared ignoring case): the run stops before
anything is created and names the code that uses it. For example, "abdabd" is used by
ABDTEST. The same meaning twice in one request file also stops.

**Code with spaces or lowercase:** there is no check, apart from the length (30) and outer
spaces. The code is sent exactly as typed. Because the existence check is case-sensitive,
`rush_order` and `RUSH_ORDER` count as two different codes. Oracle stores mixed case: the code
`Subscription` exists. **Not proven:** whether Oracle accepts a code with inner spaces or in
lowercase through REST. The automation has never tried either.

**Dates:**
- The format is `YYYY-MM-DD`. `today` means Oracle's today minus one day. On the REST route,
  Oracle's today is the date of the REST answer. On the fallback route, it is the calendar of
  a new, unsaved row on screen.
- Script rule: the end date may not be before the start date. Nothing else is checked: a past
  start or end is allowed.
- The page's date rules (`common/page.py`, used by the page server) are stricter. An end date
  must be **after** Oracle's today and after the start. A start later than today is allowed,
  with a note. So `today` as an end date passes the script but is refused by the page.
- The script prints no warning when a date is in the past. The page refuses a past end date
  (see above), but for a past start it shows neither a note nor a stop.
- If the new code is not active on Oracle's today (disabled, starting later or already
  ended), the Create Order check is skipped for it, with a NOTE.

**Position in the list:**
- If it is empty, the automation uses the highest existing number + 1. Within one request
  file, it counts up row by row.
- If you give a number, it is used as given. A number already in use is allowed and only gets
  a NOTE; it only affects the list order (ABCABC1 and ZZ_POC_STANDARD_ORDER both use 10).
- It must be a whole number of 0 or more.

## 4. Routes

| | REST (first) | Export/import (automatic fallback) |
|---|---|---|
| When | always tried first | only when the first REST call fails or is refused (e.g. 403), or with `--fallback` |
| Status | **PROVEN** 2026-10-21 (ZZ_TEST_2868, ZZ_TEST_9464) | Proven on the Redwood Set Up page 2026-10-20 (ZZ_TEST_4833); **not re-proven on the classic layout** Oracle is on now |
| Sets | all 8 code fields (`code`, `meaning`, `description`, `display_sequence`, `enabled`, `start_date`, `end_date`, `tag`) | the same 8 fields. It also copies the "who" columns from the most recent user-made code. |
| Checks | GET of each new code compared field by field; all other codes unchanged; Create Order > Order Type accepts the new name | second export compared field by field; existing rows unchanged; the row read on the Manage Order Lookups screen |
| Proven fields | code, meaning, description, enabled = yes, automatic position | code, meaning, description, position given by you (10), enabled = yes, start date |

No field can be set by one route but not by the other: both routes write the same 8 fields.
Proven only on the fallback route: start date and a position you give. Proven on neither route:
end date, tag, and Active = no.

## 5. Oracle fields the automation does not fill

The export's code file has these columns: LookupType, LookupCode, Meaning, Description,
EnabledFlag, StartDateActive, EndDateActive, DisplaySequence, Tag, plus the "who" columns.
**Every one of them is already covered.** The "who" columns are created by, created on, last
updated by and so on; Oracle or the template row fills them, not you. The list you gave
(Description, Tag, Enabled, Start Date, End Date, Display Sequence) is fully in the form.

The automation does not cover:
- the order type list itself (its meaning, description and module). This is on purpose: it is never changed.
- the further setup an order type may need before sales orders can really use it: transaction
  type and assignment rules, orchestration process assignment, document sequences. These are
  separate steps that don't exist yet.
- REST might have attributes on lookup codes beyond the export columns. **Not checked:** the
  notes only say LookupCode, Meaning and EnabledFlag are mandatory, and Oracle could not be
  reached today to look again.

## 6. Several order types per request

- **Request file (`ordertypes.json`): yes, several codes in one list.**
  - Every row is checked first. Any problem (a missing value, a length over the limit, a
    meaning used twice, a meaning already in Oracle) stops the whole request before anything is created.
  - Existing codes are skipped. Codes are created one after another.
  - If the **first** create fails, nothing is made and the whole request moves to the fallback.
  - If a **later** create fails, the run stops and names the codes already created. Those
    codes stay; nothing is deleted. A rerun skips them.
  - The fallback imports all new rows in one file. How a single bad row behaves there is **not proven**.
- **Page (`--run`): one order type per run.** There is no "rows" field. A sheet with several
  order types would need the page's batch run (one `--run` per row, as Customers does): a
  failed row does not stop the others.
- There is no Order Types group in `sheet_registry.json` yet, so `max_records`, a failed-only
  sheet, and the `error.detail` `saved` flag are not set up. Order Types' `--run` gives no
  `saved` flag, so the result card would say "may have been saved".

## 7. Sample requests and records

**ZZ_DEMO_ORDER** exists in Oracle, with meaning "ZZ Demo Sales Order" and position 20. The
notes only say it "also exists"; they do not record how it was created or what request created it.
Its sibling, **ZZ_DEMO_ORDER22**, was created by `browser_flow.py` on 2026-10-20 through the
fallback route. Its values were meaning "ZZ Demo Sales Order 22" and position 20. The rest of
its request was not recorded.

**Latest real test record: ZZ_TEST_9464**, created 2026-10-21 through the page's `--run` by
REST in 40 seconds. The request below is rebuilt from the notes; the exact text was not saved:

```json
{"code": "ZZ_TEST_9464", "meaning": "ZZ_TEST_9464", "description": "Page interface test"}
```

What Oracle returned: position 28 (assigned), enabled Y, no start or end date, no tag. The 22
other codes were unchanged, and Create Order offered it.

**Most complete record: ABCABC1**, created 2026-10-19 by the fallback route:
- code ABCABC1
- meaning "ABC ABC Order Type 1"
- description "Custom POC Order Type for Automation Testing"
- position 10
- enabled yes
- start date 2026-10-19

The current `ordertypes.json` holds `ABDTEST` / `abdabd` / "Quick test". ABDTEST already
exists, so a run would just skip it.

## Where the notes and the code disagree

1. **`--check`:** "How to do it" says `--check` is REST, GET only, which matches the code. A
   later paragraph ("`--check` (read-only, proven 2026-10-20) ... opens Actions > Export to
   CSV File ...") describes what is now `--check-ui`. The code only does those screen steps on
   `--check-ui`, or when REST is unavailable.
2. **Screen names in the fallback description:** "What `browser_flow.py` does" still names
   the old screens ("Export to CSV File > Create New", "Submit", "View All"). The shared
   helper is the Redwood "New Setup Export / Import" version, and Oracle is now back on classic.
3. **Dates:** the notes and the script allow any end date that isn't before the start, and
   `today` for either date. The page's own date rules refuse an end date on or before Oracle's today.
4. **Result of a fallback `--run`:** the notes say the result `created` holds "the code as
   the REST GET returned it". That is true for REST only. After the fallback, `created` holds
   just the code and meaning.
5. **Description label:** the Oracle screen calls it "Item Description"; the automation's label is "Description".
6. **"Several codes":** the sample requests show several codes in one request ("A1 (Alpha)
   and B1 (Beta)"). That works through the request file only, not through the page (one per `--run`).

## Not proven

- End date, tag and Active = no, on either route.
- Start date and a position you give, through REST.
- Codes with inner spaces or in lowercase.
- The fallback route on the current classic layout. Also how it handles one bad row among several.
- The full live list of order type lists today, and any extra REST fields (Oracle was unreachable).
- How ZZ_DEMO_ORDER was created.

## Checked again 2026-10-26

Lengths (code 30, meaning 80, description 240, tag 150) are now checked in the preview. Oracle compares
meanings and codes exactly (proven in the Lookup types folder); this sheet still treats meanings differing only
in capitals as the same (stricter on purpose). Small letters in a code are proven. A value Oracle refuses at
Create (HTTP 400) is now a plain refusal naming the field, not an automatic repair.
