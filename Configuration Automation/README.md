# Configuration Automation

Scripts that create Oracle Fusion Cloud setup configuration from requirement files
using the setup-task CSV export/import REST API. Works on any Oracle Fusion
environment; you choose which one in `.env`.

## The page (easiest)

Double-click **`start.cmd`** in the project folder (macOS / Linux: `sh start.sh`). It
installs the minimum needed and opens the page in your browser at
http://127.0.0.1:8765. Keep the small window open while you use the page.

On a new computer (just unzipped), the page walks you through a short checklist. Most
steps run by themselves; you only:

1. press **Enter your Oracle details**: a small file opens in Notepad; fill in your own
   Oracle user name, password, Oracle address and an environment name (e.g. `test`),
   save and close it (the page never reads or shows these details);
2. **sign in to Oracle** in the window that opens by itself (it closes by itself);
3. press **Sign in to Claude** and sign in (used to fix problems automatically).

**No administrator rights?** Nothing on the checklist needs them, and nothing asks for an
admin password. The page installs Claude's helper for your user only, trying in order:
npm's usual install (as before), Anthropic's own per-user installer (no Node.js needed), a
portable Node.js in `%LOCALAPPDATA%\ConfigAutomation\tools` (macOS / Linux:
`~/.local/share/ConfigAutomation/tools`), then npm with a per-user folder. The page finds the
helper there by itself (no restart, no PATH change). Automatic fixes are optional: if every
way is blocked (company policy, blocked downloads), the step shows why and a **Continue
without automatic fixes** button, and the cards open anyway. A failed run then shows a plain
message to copy into Claude. **Try again** on that step sets it up later. To see what this PC
allows: `python common/claude_tool.py --diagnose`.

Every later start takes a few seconds: the page checks that your saved Oracle sign-in
still works and goes straight to the cards. Only when it has expired does the Oracle
sign-in window open again, before the cards. Then pick a card, fill in the short form,
and the page does the rest in Oracle, showing its progress and where to find the result.

The page runs only on this computer and refuses to change a production environment
unless you add `ALLOW_PROD=yes` yourself.

## Setup (once per PC)

Another way: unzip the project, open the folder in Claude and say "set up".
Claude installs what is needed and only asks you to do two things yourself:

1. Fill in your own Oracle details in the `.env` file it creates (it never reads them):

   ```
   ORACLE_USER=your.user@example.com
   ORACLE_PASS=your-password
   ORACLE_HOST=https://your-pod.fa.ocs.oraclecloud.com
   ORACLE_ENV=test
   ```

   - `ORACLE_ENV` is required: a label for the environment, e.g. `dev`, `test`,
     `uat`, `sit`, `prod` or your own. The scripts stop if it is missing.
   - For `prod` / `production` the scripts refuse to run unless you also add
     `ALLOW_PROD=yes`. Only add that line yourself, deliberately.
   - Every run prints the host and `ORACLE_ENV` first, so you can see where it is going.
   - Environment variables with the same names override the file.

2. Sign in to Oracle once in the browser window that opens (the session is kept on
   this PC in `.session/`).

Doing it by hand instead (Windows PowerShell, from the project folder):

```
winget install Python.Python.3.12
python -m pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
python common/check_setup.py
python common/login_once.py
python common/check_setup.py --final
```

Fill in `.env` after the copy step. `check_setup.py --final` creates `.setup_ok`
when everything passes. Before sharing the project, read `SHARING.md`.

## Usage

Each configuration type has its own folder at the root with a `run.py`, a
requirements file and a `CLAUDE.md` describing what is proven. Read that file first.

Lookups (`FND_MANAGE_STANDARD_LOOKUPS`): edit `Lookup types/lookups.json`
(format in `Lookup types/CLAUDE.md`), then

```
python "Lookup types/run.py" --dry-run
python "Lookup types/run.py"
```

Every lookup needs a module (the Module field in the UI). You only give its name;
Claude looks up the ID in the Module list in `Lookup types/CLAUDE.md`. To see the
module IDs already used by lookups in your environment:

```
python "Lookup types/run.py" --list-modules
```

Price lists: edit `Price Lists/pricelists.json`, then

```
python "Price Lists/run.py" --check
python "Price Lists/run.py"
```

Payment terms (through the Oracle screens, using your saved sign-in): edit
`Payment Terms/terms.json`, then

```
python "Payment Terms/browser_flow.py" --dry-run
python "Payment Terms/browser_flow.py"
```

Order types (new codes in the order-type lookup, through the Oracle screens): edit
`Order Types/ordertypes.json`, then

```
python "Order Types/browser_flow.py" --dry-run
python "Order Types/browser_flow.py"
```

Customers (filled in on Oracle's Create Customer form, using your saved sign-in): edit
`Customers/customers.json` (name, account address set and supplier site ID are
required; other fields in `Customers/CLAUDE.md`), then

```
python "Customers/browser_flow.py" --check
python "Customers/browser_flow.py"
```

`--check` fills the form and checks every value without saving. Customers that
already exist are skipped and their values shown; nothing is ever changed or deleted.

Every folder also has a read-only check that proves its Oracle screens or calls still
work without creating, changing or deleting anything, e.g.

```
python "Payment Terms/browser_flow.py" --check
```

New configuration folders start as a copy of `_template/`.

Temporary files go in each folder's `_work/` (e.g. `Lookup types/_work/`). The folder is deleted
automatically after a verified success and kept after a failure or dry run so you
can inspect it.
