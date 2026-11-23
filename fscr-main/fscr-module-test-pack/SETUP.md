# Setup (one page)

You will test how well Oracle's FSCR sets up one module, the same way we tested Common Features, Procurement and
Sourcing and Supplier Management. Claude does the work; you sign in and check.

## 1. What you need

| Item | Detail |
|---|---|
| **Claude Desktop** | Installed and signed in to your GoSaaS Claude account. You will use its **Code** tab. |
| **Model** | **Opus 5.5**. Pick it in the model menu before you start. |
| **Python** | **3.10 or newer** (3.11 or 3.12 recommended). Check with `python --version` (Mac: `python3 --version`). If it is missing, install it from python.org and tick "Add Python to PATH". No extra packages are needed. |
| **Browser** | Microsoft Edge or Google Chrome (used for the sign-in page and to draw the 4 table images). |
| **Oracle access** | Your **own** login to the Oracle Fusion **test** environment (release 26D or later), with setup rights for your module (Functional Setup Manager export/import, Run Books). Never production. |
| **Oracle sign-in app** | FSCR signs in through a public OAuth client ("Mobile Application") in the test environment. Ask your Oracle admin for its **Client ID** and scopes, or follow FSCR's onboarding to create one. |
| **Node.js / git** | Not needed. |

## 2. Unzip and open

1. Download `fscr-module-test-pack.zip` from Drive. If it comes in parts, put all parts in one folder and unzip the first part.
2. Unzip it to a short path, for example `C:\fscr-module-test-pack` (Mac: your Documents folder).
3. Open Claude Desktop → **Code** tab → choose the folder `fscr-module-test-pack`.

## 3. Sign in with your own login

Say to Claude: **"Help me set up my Oracle sign-in."** Claude follows FSCR's onboarding. It puts your environment,
Client ID and scopes into `core/auth/fusionEnv.properties` without showing them, then starts the sign-in. A browser
window opens. **You** type your Oracle user name and password there. Never paste them into the chat.

## 4. Start the test

Say exactly (with your module and initials):

> **Test the module Procurement, my initials are AB**

Module names are the tracker rows, for example `General Ledger`, `Payables`, `Global HR` or `Inventory Management`.
Claude can list them all.

## 5. What Claude produces

In `evidence/<Module>/` (about 30–90 minutes):
- `RESULT.md`: verdict, plan, Run Book, 6-task table, scores with reasons, time taken
- `tracker_row.md`: your tracker values, ready to paste
- `plan.csv`, `oracle_links.csv`, `data/`, `INDEX.md`
- `images/`: 4 table pictures (coverage, plan result, 6 tasks, tracker row)

In Oracle: only records named `FSCRT_<your initials>_...`. Nothing existing is changed.

## 6. Hand it in

1. Upload the whole `evidence/<Module>` folder to Google Drive.
2. Share it with Abdullah (Viewer) and **send him the folder link**.
3. Do **not** edit the tracker. It is view only, and Abdullah pastes your `tracker_row.md`.

Optional: open a **new** Claude chat on the same folder and say "verify the module <name>" for an independent check.

## If something goes wrong

| Problem | What to do |
|---|---|
| Sign-in fails with a network timeout | Try once more. It usually works the second time. |
| Run Book "create" timed out or says "unknown" | Do **not** create it again. Claude checks later by name and links it by hand. |
| "Payment terms object order mismatch" (Receivables only) | Use the optional patch in `module-test-kit/patches/`. Read its README first. |
| Import fails: the CSV needs an internal ID | Expected for some tasks. Claude stops after 2 tries and marks it Not done. |
| A task needs a Procurement (or other) business unit | Claude may create a new `FSCRT_` test BU, never change an existing one. Otherwise it is marked Not done. |
| Oracle has no CSV or API for a task | Normal. It is screen-only work and is not counted against FSCR. |
| Oracle rejects a value (for example INDEPENDENT) | Claude uses Oracle's code instead (INDEP). |
| `python` not found | Install Python 3.12 from python.org with "Add Python to PATH", then restart Claude Desktop. |
| No images made / "No Edge or Chrome found" | Install Edge or Chrome. |
| A check says FAIL | Ask Claude to fix the listed problem and run the check again. |
