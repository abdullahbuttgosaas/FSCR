# Batch 09 result: Common Features (AB), tax registrations, legal and BU document sequences, partners, implementation users

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (third Common Features sitting, one-paste PEOPLE_PROMPT run). Tested on one test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file was edited. Work folder outside the repo. Record names `GAPFILL_AB_B9_<name>`; fresh tests end in F, re-tests in R. No existing record was edited or deleted.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 15:14 | 15:17 | 3 | Reading context, batch 08 result, helpers (sitting set-up, not in any task) |
| 15:17:19 | 15:17:35 | 0.3 | Sign-in (browser page completed). Waiting |
| 15:17 | 15:24 | 7 | REST probes: messages (read-only), partners (create needs an owner), new helper `scripts/rest_call.py` (shows Oracle's gzip error text); 2 network blips (DNS, time-out) retried |
| 15:24 | 15:28 | 4 | 4 read-only exports in parallel (waiting); cross-validation rules package checked |
| 15:28 | 15:33 | 5 | Tax registration tries 1 and 2, skill written |
| 15:33 | 15:44 | 11 | Legal sequence: test category, try 1, skill; tax registration fresh test (bug found), fix, re-test; BU category + try 1 |
| 15:44 | 15:58 | 14 | BU skill; legal and BU fresh tests and re-tests (waiting, in parallel); partner and implementation users skills |
| 15:58 | 16:10 | 12 | Cards, evidence, tracker, reports (shared with batch 10) |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records / ProcessIds |
|---|---|---|---:|---:|---|---|
| 1 | Manage Tax Registrations (`ORA_ZX_MANAGE_TAX_REGISTRATIONS`) | tested (try 2) | 7 + 7 | 3 | read-back FAIL as written, fixed; re-test R PASS | `GAPFILL_AB_B9_TRG1` (refused ZX-885657); `TRG2`; fresh `TRG3F`; re-test `TRG4R` on new test customer `GAPFILL_AB_B9_CUST3R` (REST, no ProcessId) |
| 2 | Manage Legal Document Sequences (`ORA_FND_MANAGE_DOCUMENT_SEQUENCES_LEGAL`) | tested | 6 + 5 | 6 | PASS; re-test R PASS | category `GAPFILL_AB_B9_LC1` (100004743405664); `GSQ1` (100004743402677); fresh `GSQ2F` (100004743402841); re-test `GSQ3R` (100004743406350) |
| 3 | Manage Business Unit Document Sequences (`ORA_FND_MANAGE_DOCUMENT_SEQUENCES_BU`) | tested | 5 + 5 | 5 | PASS (wrong sentence found); re-test R PASS | category `GAPFILL_AB_B9_BC1` (100004742441924); `BSQ1` (100004742423977); fresh `BSQ2F` (100004743405852); re-test `BSQ3R` (100004744392361) |
| 4 | Manage Partner Organizations (`HZ_MANAGE_PARTNER_ORGANIZATIONS`) | written (unsafe to test) | 6 + 0 | 2 | not run | none (`GAPFILL_AB_B9_PRT1` refused, not created) |
| 5 | Create Implementation Users (`FND_CREATE_IMPLEMENTATION_USERS`) | written (unsafe to test) | 4 + 0 | 0 | not run | none |
| | **Total** | **3 tested, 2 written** | **45** | **16** | 3 of 3 | |

Screen-only (proven, not counted in the sitting limit): Manage Applications Core Messages, Manage Messages, Manage Messages for General Ledger, Manage Cross-Validation Rules (see `screen-only.csv`).

## Problems and findings
1. **FSCR's REST client hides Oracle's error text:** it decodes gzip error bodies as plain text, so every `HTTP 400` came out as garbage. New helper `common-features/scripts/rest_call.py` runs FSCR's own `fusion_rest_client.py` unchanged but swaps, at run time, the request function for one that un-gzips the error and leaves the server address out. With it Oracle's messages were readable (for example `The action "create" is not enabled`, `Provide a valid value for ResourceId`).
2. **Messages are read-only by REST:** `messages` describe lists only `get`; a test POST was refused (`create is not enabled`), GET after: 0 rows. With no FSM CSV, the 3 message tasks are screen-only.
3. **Cross-validation rules have no CSV route:** the task's package is the chart-of-accounts flexfield package with no rule object, although rules exist. REST names tried: 404. Screen-only (or the General Ledger spreadsheet task).
4. **Tax registrations:** the CSV package holds only first-party (legal reporting unit) files, which are real company setup; the REST resource `taxRegistrations` takes third-party registrations. A GB regime checks the number format (ZX-885657); a US test regime does not. **`q=A and B` returns 0 rows on this resource**; `q=A;B` works. The fresh tester found this. As first written, the skill's duplicate check would always have looked clean. Fixed and re-tested.
5. **Legal sequences** on this environment are all on the shipping deliveries table (bill of lading). **BU sequences** did not exist; Oracle accepted one on the work-order table with determinant BU. Both use a new test category, so no real document is numbered by them.
6. **After-export with no ZIP gives a false compare FAIL** ("removed" rows). The BU tester hit it; both sequence skills now say to check the ZIP first. The legal skill was re-tested after this change.
7. **Partner organizations need an owner resource**; the sign-in user is not a CRM resource, so a test partner would belong to a real colleague. Written, not loaded.
8. **FSCR already has a skill for implementation users** (`core/getting-started/implementation-users`, SCIM) that its catalog does not map to `FND_CREATE_IMPLEMENTATION_USERS`. Our tool permissions blocked even its read-only preflight (account-related), so the gap skill points to FSCR's skill and marks live steps GUESS.
9. Network: one DNS failure and two time-outs (REST and one export) during the sitting. A plain retry worked each time; nothing was sent twice.

## What is left
Batch 10 ran in the same sitting (`BATCH_10_RESULT.md`). See `MODULE_RESULT.md` for the counts.
