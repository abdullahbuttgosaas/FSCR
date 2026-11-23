---
skill_id: "gosaas.gap-fills.erp.financials.customer-payments.manage-alternate-name-mapping-rules"
name: "Manage Alternate Name Mapping Rules Setup Task Guidance (GoSaaS gap fill)"
description: "Create new Receivables alternate name mapping rules (test-prefixed names, new rows only) with Oracle's documented REST POST through FSCR's generic REST client, then prove the rows exist. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill. Run 25, one test environment, 2026-11-15. Skill written in Run 27a, cold-tested in Run 27b, wording fixed in Run 27c, 2026-11-16. NOT official FSCR."
tested_by_fresh_chat: "Yes, Run 27b (2026-11-16); made generic and re-tested by a fresh chat 2026-11-24 (PASS). See CHANGELOG.md"
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Customer Payments"
functional_area_code: "ORA_FIN_CUSTOMER_PAYMENTS"
task_code: "ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES"
task_name: "Manage Alternate Name Mapping Rules"
parent_skill_id: "erp.financials.customer-payments"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
rest_resource: "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.3.0"
inputs:
  - "fusion_environment_context"
  - "new_alternate_payer_names"
  - "existing_customer_account_number"
outputs:
  - "post_responses"
  - "before_and_after_collection_reads"
  - "verification_rows"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
side_effects:
  - "GET calls are read-only."
  - "Each POST creates one active alternate name mapping rule. This skill never updates or deletes, so test rows stay in the environment."
required_privileges:
  - "GUESS: a Receivables setup role that can manage alternate name mapping rules. Runs 25 and 27b worked with a test setup user; the exact privilege was not checked."
---

# Manage Alternate Name Mapping Rules (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR. Origin: Run 25, one test environment.** Skill written in Run 27a. Cold-tested by a fresh chat in Run 27b; fixed in Run 27c (see `CHANGELOG.md`).
> FSCR has no skill and no route for this task. This file does not edit any FSCR file.
> Labels: **VERIFIED** = seen in our test runs (Run 25, Run 27b, re-test 2026-11-24) or a check we ran · **FROM FSCR** = FSCR file and line · **FROM ORACLE DOCS** = link · **GUESS** = my judgment, not tested.

## What this setup is
An alternate name mapping rule is a "nickname" for a customer: when a bank payment arrives under a different payer name (in Japan, often a Kana spelling in a Zengin lockbox file), the rule tells Oracle which customer account the money belongs to. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/financials/26a/farfa/api-alternate-name-mapping-rules.html

## When to use
- A user asks to create new alternate name mapping rules (task `ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES`, "Manage Alternate Name Mapping Rules").
- Do **not** use it to change or remove existing rules. This skill adds new rows only.
- Test environments only until a person says otherwise. Every payer name must start with your test prefix (`PREFIX` below).

## What FSCR has (and does not have)
| FSCR file | What it says |
|---|---|
| `knowledge/setup-task-catalog/effective/setupTasksAll.json:9226` | Task exists; ExportImportSupportedFlag N, CSVExportImportSupportedFlag N. FROM FSCR |
| `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json:9864-9870` | Name, one-line description, both flags false. FROM FSCR |
| `pillars/erp/financials/customer-payments/SKILL.md:107-109` | Lists only Receipt Sources and Receipt Classes; not this task. FROM FSCR |
| `core/fusion-api/rest-api-client/SKILL.md:50-52` | Generic client for any `/fscmRestApi` path; no task fields. FROM FSCR |

No FSCR file names `alternateNameMappingRules`. VERIFIED (Run 25 search)

## Placeholders used below
Replace these in every command (write paths with forward slashes, e.g. `C:/...`, see Step 0):
```text
FSCR    = the FSCR root folder: the one that directly holds core/, shared/ and core/auth/fusionEnv.properties
          (in a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main). Read only, never edit.
GAP     = the folder that holds this SKILL.md (its helper is GAP/scripts/verify_rules.py)
RUN     = a NEW empty folder you create for this run, OUTSIDE FSCR (keep every output here; never write inside FSCR)
PREFIX  = your test prefix, e.g. GAPFILL_ or whatever your test environment requires. Every new payer name starts with it.
NAME1, NAME2 = your new payer names, e.g. "<PREFIX>Payer A". Create only as many rules as the brief approves (one is fine: then skip everything about rule 2).
ACCOUNT = an existing test customer account number (Step 3)
```
The REST client is `<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`.

Do **not** reuse the names in the worked examples; they already exist and the precheck will refuse them.

## Step 0. Shell, paths and Python flags (read first)
**The commands are written for Git Bash on Windows** and were run in this exact form in Run 27b (VERIFIED). Two things make them work:
1. **`MSYS_NO_PATHCONV=1` in front of every `python` command that has a `/fscmRestApi/...` path.** Without it, Git Bash rewrites any argument that starts with `/` into a Windows file path, and the client stops with:
   `REST URL must have a valid HTTPS authority without credentials`
   VERIFIED (Run 27b, try 1 failed with this text; the same command with `MSYS_NO_PATHCONV=1` worked). If you see that error, this is the cause.
2. **File paths written as `E:/...` (drive letter + forward slashes), never `/e/...`.** With `MSYS_NO_PATHCONV=1` set, a `/e/folder/...` path reaches Python unchanged and becomes `E:\e\GoSaaS\...`, which does not exist. VERIFIED (Run 27b, try 2)

Other shells:
- **PowerShell or cmd:** they do not rewrite paths, so drop the `MSYS_NO_PATHCONV=1 ` prefix, keep the drive-letter paths, and put each command on one line (or end lines with a backtick in PowerShell instead of `\`). GUESS (not run in PowerShell for this skill).
- **Linux or macOS bash:** no path rewriting; `MSYS_NO_PATHCONV=1` is harmless there. GUESS
- **Any shell, other option:** the client adds the leading `/` itself if you leave it out (FROM FSCR `rest_client_common.py:70-74`), so `fscmRestApi/resources/...` without the first `/` is never rewritten. GUESS that it works end to end (not run).

Also:
- Run FSCR scripts with their full path and add `-B`, so Python does not write `__pycache__` into FSCR. (VERIFIED in the journal-categories skill, Run 26b, and used in Run 27b.)
- Do **not** use `-I` with FSCR scripts. FSCR's Windows token storage needs `pywin32`, which lives in the user site-packages folder, and `-I` hides it ("Windows Fusion OAuth storage requires pywin32"). VERIFIED (journal-categories `CHANGELOG.md`, Run 26b; seen again in Run 25)
- Send every response to `RUN` with `--output`. With `--output` the client prints `HTTP <status>` and writes the file. FROM FSCR `rest_client_common.py:159-164, 306-307`; VERIFIED (Run 27b)
- Never print tokens, Authorization headers or token cache contents. FROM FSCR `core/fusion-api/rest-api-client/SKILL.md:124-125`
- Python launcher: Runs 25 and 27b used `python`. Use `python3` if that is your launcher.

## Step 1. Sign in (only if the saved token does not work)
1. **First, find out if you need to sign in.** Run the `describe` command from Step 2. If it prints `HTTP 200`, the saved token works: skip the rest of Step 1. If it prints `Opening Oracle Identity Cloud login in your browser.`, the token has expired and the client is now **waiting for sign-in** (it signs in by itself, FROM FSCR `rest-api-client/SKILL.md:82-85`). Treat that wait exactly like point 3 below.
2. **Why the token matters for POSTs:** the client retries a **GET** once on HTTP 401/403 but **not a POST** (FROM FSCR `rest_client_common.py:292`). So always run a fresh GET right before each POST (Step 5). Run 25's token expired in the middle of the run. VERIFIED
3. **To sign in on purpose** (Git Bash; no `MSYS_NO_PATHCONV` needed, there is no `/fscmRestApi` path):
   ```bash
   python -u -B "<FSCR>/core/auth/fusion-oauth-authentication/scripts/fusion_login.py" --service standard --callback-timeout 280 > "<RUN>/login.log" 2>&1
   ```
   - **Run it in the background** (or in a second terminal), because it blocks until sign-in finishes or times out.
   - **`-u`** makes Python write its output straight away. Without it, output sent to a file stays empty until the script ends, so you cannot see the sign-in link or progress. VERIFIED (Run 27b: empty log mid-run)
   - **`--open-browser` is not needed.** Opening the browser is already the default; the flag changes nothing. Use `--no-open-browser` only if you want the link printed and not opened. FROM FSCR `fusion_login.py:61-72`. The line `Opening Oracle Identity Cloud login in your browser.` is printed either way (FROM FSCR `fusion_auth.py:1090`; VERIFIED, Run 27b printed it without the flag).
   - It uses `http://127.0.0.1:8765/oauth/callback` and listens on port 8765 until sign-in completes or the timeout ends. VERIFIED (Runs 25, 27b)
4. **How long to wait:** up to `--callback-timeout` seconds (280 above; the default is 300, FROM FSCR `fusion_auth.py:32`). Check the log every 30 to 60 seconds. In Run 27b the successful try finished well inside the 280 s. VERIFIED
5. **How to tell it finished:**
   - Success: the log ends with `Login complete for standard.` (just before it: `Saved access token cache in ...`) and the exit code is 0. VERIFIED (Run 27b `login_27b_try2.log`)
   - Timeout: the log shows `Error: Timed out waiting for authorization callback` and the exit code is 1. VERIFIED (Run 27b `login_27b.log`)
   - Either way the listener on port 8765 closes by itself when the script ends. VERIFIED (Run 27b, netstat). If you stop the script yourself, check that nothing listens on 8765 any more.
6. **If it times out, retry.** Start the same command again, at most **2 more times (3 tries in total)**. Run 27b needed 3 tries: the client's own sign-in timed out at 300 s, the first `fusion_login.py` at 280 s, and the next one completed. VERIFIED. Why the first two timed out is a **GUESS** (probably the browser's sign-in state, e.g. a page not yet signed in or not in front). Before each retry, make sure the previous try has ended (exit code printed, nothing on port 8765).
   After 3 timeouts, stop and report "sign-in needs a person". Do not read or type credentials.
7. `<FSCR>/core/auth/fusionEnv.properties` must name the environment the person approved; check it before any POST. The token is cached under the user's home `.fusionaim` folder, outside FSCR. VERIFIED (Run 27b log)

## Step 2. Check read-only that the resource exists and count the rules
```bash
cd "<FSCR>"
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules/describe" --output "<RUN>/describe.json"
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules" --query onlyData=true --query totalResults=true --query limit=500 --output "<RUN>/before_all.json"
```
- Both print `HTTP 200`. VERIFIED (Run 27b)
- `describe.json` must list `create` with method `POST`. VERIFIED (Runs 25 and 27b: get, update:PATCH, delete:DELETE, create:POST, upsert:POST)
- `before_all.json` holds every rule. Note `totalResults`. The count depends on your environment (in our test environment it was 0, then 2, then 4, then 5). VERIFIED
- If `hasMore` is `true`, raise `limit` and read again (the helper refuses a cut-off file).

## Step 3. Find an existing test customer account to point at (read-only)
A rule must point at an existing customer account. `CustomerAccountNumber` is required and comes from a choice list of accounts. VERIFIED (describe)
```bash
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/receivablesCustomerAccountActivities" --query onlyData=true --query limit=100 --output "<RUN>/accounts.json"
```
- **Check `hasMore`.** It can be `true` here, and that is fine: you only need one test account. Run 27b got `hasMore: true` and found 30 test accounts in the first 100. VERIFIED. If none is in the first page, read the next page with `--query offset=100` (FROM ORACLE DOCS: standard REST `offset` parameter, not tried here), or try `--query "q=CustomerName LIKE '<your environment's test-customer prefix>%'"` (GUESS, not tried).
- The account number field is **`AccountNumber`** and the name is `CustomerName`. VERIFIED (Runs 25, 27b). Do not ask for a field called `CustomerAccountNumber` with `fields=`; Run 25 got HTTP 400 "URL request parameter fields ... is not valid". VERIFIED
- Pick an account whose `CustomerName` clearly marks it as test data (for example your environment's test-customer prefix). Never copy an account number from another environment. VERIFIED (our tests used a test customer)
- Do not point test rules at real-looking customers.
- **If no test account exists:** stop and report it. Do not create a customer in this skill. Creating one needs its own approval and its own route.
- This step only reads. The customer account is not changed by the POST either. VERIFIED (Run 25)

## Step 4. Write the POST body
One JSON file per rule. All fields are documented by Oracle; `required` comes from the pod's describe. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/financials/26a/farfa/op-alternatenamemappingrules-post.html

| Field | Send? | Notes |
|---|---|---|
| `AlternatePayerName` | **Required** | The nickname. Max 320 characters (FROM ORACLE DOCS). Start with `<PREFIX>`. |
| `CustomerAccountNumber` | **Required** | From Step 3, as a string, e.g. `"12345"`. |
| `Active` | Useful | `"Y"` (1 character). Runs 25 and 27b sent `"Y"`. VERIFIED |
| `ZenginCustomerBankName` | Optional | Payer's bank name as it appears in the Zengin file (max 360). Used in rule 2 in Runs 25 and 27b. VERIFIED |
| `ZenginCustomerBankBranchName` | Optional | Payer's bank branch name (max 360). Used in rule 2 in Runs 25 and 27b. VERIFIED |
| `BillToSite` | Optional | Bill-to site of the account. Not tried. |
| `RemittanceBankNumber`, `RemittanceBankBranchNumber`, `VirtualAccountNumber` | Optional | Virtual account details. Not tried. |
| `AlternateNameId` | **Do not send** | Describe marks it mandatory, but Oracle fills it in. Left out in Runs 25 and 27b, and an ID came back. VERIFIED |
| `CustomerName`, `RemittanceBankName`, `Created*`, `LastUpdate*`, `ObjectVersionNumber` | **Do not send** | Read only. |

Minimal body (`<RUN>/payload/rule1.json`):
```json
{"AlternatePayerName": "NAME1", "CustomerAccountNumber": "ACCOUNT", "Active": "Y"}
```
Body with the bank-name fields (`<RUN>/payload/rule2.json`):
```json
{"AlternatePayerName": "NAME2", "CustomerAccountNumber": "ACCOUNT", "ZenginCustomerBankName": "<PREFIX>Test Bank", "ZenginCustomerBankBranchName": "<PREFIX>Test Branch", "Active": "Y"}
```
Save files as UTF-8 without a BOM. VERIFIED (Run 27b)

## Step 5. Fresh GET, precheck, POST (repeat for each rule)
**Confirmation rule.** Before any POST, the environment, the task and the exact names must be approved. If the person's brief already names the environment, the task and the names (or how many test rows to make) and says to proceed, that is the approval: write one line in your run log, "POST approved by the brief: <environment>, <task>, <names>" (one name or several). Otherwise stop and ask. (Same rule as the journal-categories skill; VERIFIED, Run 27b did this.)

**Order: GET → precheck → POST rule 1 → GET → precheck → POST rule 2.** A fresh GET right before each POST catches a name someone else used in the meantime and refreshes an expired token (a GET retries sign-in; a POST does not). VERIFIED (Run 27b did this order)

a. Before rule 1: fresh read of the whole collection, then the offline precheck of **all** your names (standard library only, so `-I` is fine for the helper). This file is your **before** file for Step 7; it replaces the Step 2 copy, which is expected. Always pass `--prefix "<PREFIX>"`: without it the helper assumes `FSCRT_` and fails other names.
```bash
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules" --query onlyData=true --query totalResults=true --query limit=500 --output "<RUN>/before_all.json"
python -I -B "<GAP>/scripts/verify_rules.py" precheck --before "<RUN>/before_all.json" --prefix "<PREFIX>" --name "NAME1" --name "NAME2"
```
`PRECHECK: PASS` means: every name starts with `<PREFIX>`, is at most 320 characters, is not repeated, and is not already used. Stop on `FAIL`.

b. POST rule 1:
```bash
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules" --method POST --body-file "<RUN>/payload/rule1.json" --output "<RUN>/post_rule1.json"
```

c. Before rule 2: a **new** fresh read into a **different** file (keep `before_all.json` untouched), precheck only NAME2 against it, then POST rule 2:
```bash
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules" --query onlyData=true --query totalResults=true --query limit=500 --output "<RUN>/fresh_get_before_post2.json"
python -I -B "<GAP>/scripts/verify_rules.py" precheck --before "<RUN>/fresh_get_before_post2.json" --prefix "<PREFIX>" --name "NAME2"
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules" --method POST --body-file "<RUN>/payload/rule2.json" --output "<RUN>/post_rule2.json"
```
For more rules, repeat c with the next number.

- Use `--body-file`, not `--body`, to avoid shell quoting problems.
- **Never** add the header `Upsert-Mode: true`; it would update a matching rule instead of failing. FROM ORACLE DOCS (POST page, request headers)
- Wait for each POST to finish before sending the next.

## Step 6. Read the response
- **Success:** the client prints `HTTP 201` and writes the new row to `post_ruleN.json`. Look for a new `AlternateNameId`, your `AlternatePayerName`, `CustomerAccountNumber`, `Active: "Y"`, `ObjectVersionNumber: 1`. VERIFIED (Run 25 with its own script; Run 27b with FSCR's client: both POSTs HTTP 201 on the first try)
- `CustomerName` is **null** in the POST response; that is normal. A later GET shows the name. VERIFIED (Runs 25, 27b)
- **Failure:** the client prints `Error: HTTP <code> calling <url>: <Oracle's message>` and exits 1; no file is written. FROM FSCR `fusion_auth.py:58-63`, `fusion_rest_client.py:22-26`. Copy the exact message into your report, change one thing, and retry at most 3 times.
- On HTTP 401/403 for a POST: sign in again (Step 1), check with a GET that the rule was not created after all, then do Step 5c again (fresh GET, precheck, POST).
- Not seen yet (no POST has failed in Runs 25 or 27b): the error text for a wrong account number or a duplicate name. GUESS: Oracle returns HTTP 400 with a message.

## Step 7. Verify (read-only, then offline)
```bash
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules" --query onlyData=true --query totalResults=true --query limit=500 --output "<RUN>/after_all.json"
python -I -B "<GAP>/scripts/verify_rules.py" verify --before "<RUN>/before_all.json" --after "<RUN>/after_all.json" --prefix "<PREFIX>" --expect "NAME1" --expect "NAME2" --account ACCOUNT --rows-out "<RUN>/verify_rows.csv"
```
Use the `before_all.json` from Step 5a (taken before any POST), not the Step 5c file.

`RESULT: PASS` means:
1. every new name is in the after file and was not in the before file;
2. total rules after = before + number created (exactly);
3. rules named `<PREFIX>*` after = before + number created;
4. no rule that existed before is missing;
5. **no rule that existed before has changed**: same payer name, account, bank names, `Active`, `ObjectVersionNumber` and `LastUpdateDate` (prints `earlier rules unchanged: True`; added in Run 27c);
6. each new rule points at `ACCOUNT` and is active.

Optional extra proof, a read by ID (the ID is in `post_ruleN.json`):
```bash
MSYS_NO_PATHCONV=1 python -B "<FSCR>/core/fusion-api/rest-api-client/scripts/fusion_rest_client.py" "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules/<AlternateNameId>" --query onlyData=true --output "<RUN>/verify_by_id_1.json"
```
Run 27b ran the after read, the helper (`RESULT: PASS`, 2 + 2 = 4) and both reads by ID (HTTP 200, `CustomerName` filled in). VERIFIED. The updated helper passed on the Run 27b files, including the unchanged check, and fails when an earlier rule's `ObjectVersionNumber` is changed. VERIFIED (Run 27c, offline)

Save `before_all.json`, `post_rule*.json`, `after_all.json` and `verify_rows.csv` as the proof.

## Rules and limits
1. **Names.** Every test payer name starts with your test prefix, passed to the helper as `--prefix`. The payer name is how you find the row again, so never reuse one.
2. **Create only what the brief approves.** Runs 25 and 27b allowed at most 2 rows. That was a brief rule, not an Oracle limit.
3. **No updates, no deletes.** This skill never sends PATCH or DELETE, and never sends `Upsert-Mode`. Test rows stay in the environment. They are **active**, so a real Zengin lockbox payment with that payer name would match the test account. GUESS: no such payment happens in a test environment.
4. **Delete is a GUESS.** Oracle documents a DELETE, and the pod's describe lists `delete:DELETE` (VERIFIED in the describe). Nobody has tried it, so whether it works, or is blocked once a rule has been used, is unknown.
5. **Why not CSV import.** The pod says `ImportSupportedFlag = false` for this task (VERIFIED in Run 25 by a CSV support probe). The FSCR catalog flags agree (FROM FSCR `setupTasksAll.json:9226`).
6. **Why the other routes were dropped.**
   - Zengin bulk upload ("Zengin Format for Japan REST API"): it is made for the Japan Bank Association file and can also update and delete rules. Too broad for a few test rows. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/readiness/erp/24a/fins24a/24A-fin-wn-f31497.htm
   - FBDI, SOAP, ESS: none found for this object. GUESS (web search only).
   - HDL: loads HCM data, not Receivables setup. GUESS
   - The setup screen: not allowed in our runs (no clicking through Oracle screens).
7. **One environment tested.** One test environment, on 2026-11-15, 2026-11-16 and 2026-11-24. Other environments and releases are untested.
8. **Sign-in needs a person** if the browser page asks for credentials. Do not read or type credentials. In Runs 25 and 27b the page completed by itself (in 27b on the third try). VERIFIED
9. **Python flags.** `-B` for FSCR scripts, never `-I` with them. `-I -B` is fine for `verify_rules.py` (standard library only). `-u` for `fusion_login.py` when its output goes to a file.
10. **What a fresh chat has tested (Run 27b, skill only, Git Bash).** VERIFIED: FSCR's client for describe, collection GET, account GET, POST and read by ID on this resource; `fusion_login.py` sign-in on port 8765 (after 2 timeouts); the precheck and verify helper; the confirmation rule. Still **not tested** (GUESS): the commands in PowerShell, the path without the leading `/`, `offset` and the `q` filter on accounts, a failed POST and its error text, DELETE, the required privilege.

## Worked examples (VERIFIED)
Use them to see what good output looks like. **Do not reuse these names**; they now exist in our test environment. Account numbers and IDs are from that environment: never copy them.

| Item | Run 25 (own script) | Run 27b (fresh chat, skill only, FSCR client) |
|---|---|---|
| Environment | one test environment, test setup user | same |
| Rules before | 0 | 2 (FSCRT_R25 Payer A and B) |
| Account used | one test customer account | same |
| Names | `FSCRT_R25 Payer A`, `FSCRT_R25 Payer B` | `FSCRT_R27 Payer A`, `FSCRT_R27 Payer B` |
| POST 1 result | HTTP 201, `AlternateNameId` 300000395050002 | HTTP 201, `AlternateNameId` 300000395049051 |
| POST 2 (with bank names) | HTTP 201, `AlternateNameId` 300000395048006 | HTTP 201, `AlternateNameId` 300000395044061 |
| Rules after | 2 (0 + 2) | 4 (2 + 2); earlier 2 unchanged |
| Attempts / fixes | 2 POSTs, both first try, 0 fixes | 2 POSTs, both first try, 0 fixes; 3 sign-in tries; 3 tries for the first command (shell paths) |
| Time | about 9 minutes, including choosing the task and a sign-in | about 12 minutes, about 8 of them waiting on sign-in timeouts |

Full evidence is kept in the GoSaaS run folders of Runs 25 and 27b (not needed to use this skill).
