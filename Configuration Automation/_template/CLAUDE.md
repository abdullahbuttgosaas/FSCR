# <Configuration name>

TEMPLATE. New configuration folders are made by copying `_template/` (root CLAUDE.md >
New folder template). Replace every <...> and TODO.

Task: **<task name>** (Setup and Maintenance > offering **<offering>** > functional
area **<area>**). Status summary: <one line: route and PROVEN / PARTIAL / UNTESTED>.

## Input rules

REQUIRED (the fields the screen marks required plus what saving needs). If missing, ask
the user in one plain message; never ask for codes or IDs:
- <field>: <rule>

OPTIONAL - if missing, the UI default:

| Request key | Screen field | UI default | Kind / valid values |
|---|---|---|---|
| <key> | <label> | <default> | <text / drop-down: values> |

Dates: `YYYY-MM-DD`. "today" = Oracle's today (read from <where on screen>, never the
PC clock) minus one day; the script prints a NOTE when it does this.

Drop-down values seen on the screen (add new ones when seen; never rename):
- <field>: <values>

## Route status

- <route>: PROVEN | PARTIAL | UNTESTED | NOT SUPPORTED - <date, what was run, result>

PROVEN only when the root checklist is complete (Input rules, --check, verification,
timeouts, Route status, Configuration index row, a clean --check run of its own, and
the Page interface below tried once).

## How to do it

```
python "<Folder>/browser_flow.py" --check     # read-only, nothing created
python "<Folder>/browser_flow.py"             # full run
```
(The page commands are under Page interface.)

Request file `<Folder>/request.json`: <format>.

What `--check` does: <screens opened, values checked; nothing created>.
What the full run does: <steps>. Verification: <how every value is read back>.

## Page interface

The contract is in root CLAUDE.md > Page interface (helper `common/page.py`). The
form is `SPEC` in `browser_flow.py`: one field per Input rules key, same defaults.

```
python "<Folder>/browser_flow.py" --spec
python "<Folder>/browser_flow.py" --options <pick field>
python "<Folder>/browser_flow.py" --run '{"name": "ZZ_TEST_1234", ...}'
```

| Key | Label | Required | Type | Placeholder | Default |
|---|---|---|---|---|---|
| name | Name | yes | text | ZZ_TEST_1234 | - |
| <key> | <plain label> | <yes/no> | <text / number / date / yes-no / pick / rows> | <example> | <UI default> |

Rows fields (if any): <key>: row label "<Installment>", button "<Add an installment>",
at least <n> rows; sub-fields: <key> (<label>, <required>, <type>, <example>), ...

Pick lists (`--options`) and where each is read live: <field or rows.sub>: <REST list or screen>.
Result "where": <plain navigation to see the record in Oracle>.
Tried: <date, --spec / --options / --run result, and a --run with a missing value>.

## Sample requests

- "<plain-language request>"

## Related folders

None. (If this configuration needs another folder's object, note it here, tell the
user and wait for their go-ahead before any code. No code links between folders.)

## Known gotchas

- <date: what changed / what to watch>

## Discovery steps

1. Find the task, its offering and functional area.
2. Check Actions for Export/Import to CSV File (CSV route) or use the form.
3. Learn every field, required markers, defaults, drop-down values.
4. Prove with a dummy (ZZ_TEST_<4 digits>); verify every value; record findings here.
