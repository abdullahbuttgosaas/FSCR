# Run 25: fill a "neither" gap (no FSCR skill, no standard route)

**Result: FILLED.** Task "Manage Alternate Name Mapping Rules" had no FSCR skill and no CSV route. I found a documented REST POST, created 2 FSCRT_ records in ETIA-TEST on the first try, and read them back. VERIFIED

**Tags:** VERIFIED = seen in files or the pod · FROM FSCR = FSCR file and line · FROM ORACLE DOCS = link · GUESS = my judgment.

## Numbers
| Item | Value |
|---|---|
| Start / end | 2026-11-15 16:43:34 / 16:52:29 (+05:00). VERIFIED (`start_time.txt`, `finish_time.txt`). The first line of `start_time.txt` says 16:44:05; that is when the folder was made, 31 s after the first command. |
| Total minutes | about 9 (8 min 55 s). VERIFIED |
| Create attempts | 2 POSTs, both 201 on the first try. Fixes needed: 0. VERIFIED |
| Records created | 2, both named FSCRT_. No updates, no deletes. VERIFIED |
| Sign-in | 1 sign-in on port 8765. The cached token ran out during the probe. The FSCR login script finished on its own. Token not printed (`login_25.log`, state and challenge redacted). VERIFIED |
| Tokens | My own token use is not visible to me. No FSCR script with a token log was run. |

## 1. The task I picked and why
- **Task:** Manage Alternate Name Mapping Rules (`ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES`), ERP, Customer Payments (Receivables).
- **Plain meaning:** a "nickname list" for customers. When a bank payment arrives under a different payer name (in Japan, often a Kana spelling), the rule tells Oracle which customer the money belongs to.
- **Why this one:**
  - Easy to explain: one name maps to one customer account.
  - Safe: it is a lookup rule, not a transaction. ETIA-TEST had 0 such rules before the run, so nothing existing could be touched. VERIFIED (`evidence/anmr_all.json`)
  - The new record has a free-text name, so it can start with FSCRT_.
  - It is not an inventory item or order type.
- **It is in the "neither" group:** no skill, CSV flag N, no route declared. VERIFIED (`_fscr_run_23_gap_pick/gaps_erp_scm.csv:53`)
- **How I chose:** 159 ERP and SCM tasks are in the "neither" group (`evidence/neither_erp_scm.csv`). I asked the pod about all 159 (GET only). 157 have CSV import and export turned off, 1 has both on (`ORA_PSC_TSK_GLOBAL_FEE_ATTRIBUTES`) and 1 returned 404. VERIFIED (`evidence/csv_support_probe.csv`). So the CSV route is closed for almost all of them. I then searched Oracle's documentation for a REST route on the easiest-to-explain tasks. "Manage Messages" had none; this task had one.

## 2. What FSCR has on it
| File | What it says | Tag |
|---|---|---|
| `fscr-main/knowledge/setup-task-catalog/effective/setupTasksAll.json:9226` | Task exists, ExportImportSupportedFlag N, CSVExportImportSupportedFlag N | FROM FSCR |
| `fscr-main/knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json:9864` | Name, a one-line description, csv and export flags false | FROM FSCR |
| `fscr-main/pillars/erp/financials/customer-payments/SKILL.md:107-109` | Customer Payments guide lists only Receipt Sources and Receipt Classes, not this task | FROM FSCR |
| `fscr-main/core/fusion-api/rest-api-client/SKILL.md:3` | Generic REST client, no task fields | FROM FSCR |
| `fscr-main/core/auth/` | Sign-in script (I used a copy) | FROM FSCR |

A search of all FSCR files for "alternateNameMapping", "alternate name mapping" and "zengin" found only the catalog files. No skill, guide, hint or REST name. VERIFIED

## 3. Routes I considered
| Route | Kept? | Why | Tag |
|---|---|---|---|
| FSM setup-task CSV import (`setupTaskCSVImports`) | Dropped | The pod says ImportSupportedFlag = false for this task (`evidence/csv_support_probe.csv`) | VERIFIED |
| **REST `POST /fscmRestApi/resources/11.13.18.05/alternateNameMappingRules`** | **Kept** | Oracle documents create, read, update and delete. The pod's describe lists `create:POST` (`evidence/anmr_describe.json`) | FROM ORACLE DOCS ([create](https://docs.oracle.com/en/cloud/saas/financials/26a/farfa/op-alternatenamemappingrules-post.html), [endpoints](https://docs.oracle.com/en/cloud/saas/financials/26a/farfa/api-alternate-name-mapping-rules.html)) + VERIFIED |
| Bulk upload ("Zengin Format for Japan REST API") | Dropped | Meant for a Japan Bank Association file, and it can also update and delete rules. Too broad for 2 test rows. | FROM ORACLE DOCS ([24A readiness](https://docs.oracle.com/en/cloud/saas/readiness/erp/24a/fins24a/24A-fin-wn-f31497.htm)) |
| FBDI | Dropped | No FBDI template for this object found in search | GUESS (search only) |
| SOAP | Dropped | No SOAP service found for this object | GUESS (search only) |
| HDL | Dropped | HDL loads HCM data; this is a Receivables setup | GUESS |
| ESS job | Dropped | No ESS job that creates these rules found | GUESS |
| Setup screen | Not used | Not allowed in this run | — |

## 4. Requests and outcomes
I made each rule point at test customer account 21541 (customer name `ZZ_TEST_CU_2589_14_OK`), which I found with a GET on `receivablesCustomerAccountActivities`. The customer account itself was not changed. Before each POST, the script checked that the name was unused.

| # | Request body | Result | Tag |
|---|---|---|---|
| 1a | `{"AlternatePayerName":"FSCRT_R25 Payer A","CustomerAccountNumber":"21541","Active":"Y"}` | 201, AlternateNameId 300000395050002 | VERIFIED (`evidence/attempt_1a.json`) |
| 2a | as above, plus `ZenginCustomerBankName` "FSCRT_R25 Test Bank" and `ZenginCustomerBankBranchName` "FSCRT_R25 Test Branch" | 201, AlternateNameId 300000395048006 | VERIFIED (`evidence/attempt_2a.json`) |

No errors, so no fixes.

## 5. Proof (GET only)
- A query for `AlternatePayerName LIKE 'FSCRT_%'` returns exactly these 2 rows (`evidence/verify_fscrt_query.json`).
- The pod now holds 2 rules in total: 0 before, 2 after (`evidence/anmr_all.json`, `evidence/verify_all_rules.json`).
- A GET by ID returns each row with CustomerName `ZZ_TEST_CU_2589_14_OK`, Active Y, created by Configuration.TEST at 11:51:43 and 11:51:54 UTC (`evidence/verify_by_id_*.json`, `verify_rows.csv`).

All VERIFIED.

**Left in the pod:** these 2 rules stay, because deletes were not allowed in this run. They are active, so a Zengin lockbox payment with payer name "FSCRT_R25 Payer A" or "FSCRT_R25 Payer B" would match account 21541. No such payment is likely in ETIA-TEST (GUESS).

## 6. What FSCR provided / what Claude found or built
| What FSCR provided | What Claude found or built |
|---|---|
| Task name, code and description in the catalog | Showed the pod has CSV turned off for 157 of the 159 "neither" tasks |
| Flags saying no CSV and no export | Found the documented REST resource that FSCR never names |
| Sign-in script (port 8765) | Read the field rules from the pod's describe: 2 required inputs |
| Generic REST client guidance | Found a test customer account to point at (GET) |
| No skill, no field list, no route | Wrote `scripts/create.py`, which checks the name is unused and then POSTs, and `scripts/api.py` |
| — | Created 2 records and proved them with 3 kinds of read |

## 7. What this means
- Some "neither" tasks are only gaps in FSCR's catalog, not in Oracle. Oracle has a REST route that FSCR's flags do not show. VERIFIED for this task.
- This is one task. I did not check the other 158 for REST routes, so I cannot say how many more are like it. GUESS: tasks named "Messages", "Approvals", "Data Access" or "Submit Process" are less likely to have a create route.

## Clean-up
- The FSCR login listener on port 8765 exited by itself after sign-in. At the end, nothing was listening on port 8765 and no Python process was running. VERIFIED (Get-NetTCPConnection, Win32_Process). I did not stop anything, because nothing I started was still running.
- No FSCR file was edited. My files are only in this folder (`work/auth` is a copy of FSCR `core/auth`).
