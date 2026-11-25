# Batch 12 result: Common Features (AB), billing method extension assignments, custom ESS list-of-values sources

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (fourth Common Features sitting, after batch 11). One test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file edited. Work folder outside the repo. Record names `GAPFILL_AB_B12_<name>`. No existing record was edited or deleted.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 21:26 | 21:30 | 4 | 4 read-only exports in parallel (waiting); help settings export lost to network drops |
| 21:31 | 21:33 | 2 | Billing method columns (Oracle table docs by a helper; lookup read live) |
| 21:33 | 21:37 | 4 | Invoice method tries 1 (refused) and 2 (PASS); revenue method PASS; export compares |
| 21:40 | 21:47 | 7 | ESS LOV source FSCM, CRM, HCM: one after the other, each with before/after export compare |
| 21:38 | 21:46 | 8 | 5 skills written |
| 21:44 | 22:01 | 17 | Fresh tests: invoice F, wording fix, invoice R, revenue F (sequential); ESS FSCM F, CRM F, HCM F (sequential) |
| 22:01 | 22:10 | 9 | Own read-back, cards, evidence, reports |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records (ProcessId) |
|---|---|---|---:|---:|---|---|
| 1 | Manage Invoice Methods: Billing Extension Assignments | tested (try 2) | 7 + 9 | 4 | PASS, re-test R PASS | `IM1` refused (100004744403991); `IM2` (100004744404076); fresh `IM3F` (100004744396826); re-test `IM4R` (100004743426123) |
| 2 | Manage Revenue Methods: Billing Extension Assignments | tested | 3 + 4 | 3 | PASS | `RM1` (100004744396782); fresh `RM2F` (100004743428028) |
| 3 | Manage ESS Job Definitions and Job Sets (FSCM) | tested | 5 + 4 | 2 | PASS | `LOV1` (100004743427019); fresh `LOV4F` (100004743426141) |
| 4 | Manage ESS Job Definitions and Job Sets (CRM) | tested | 1 + 3 | 2 | PASS | `LOV2` (100004743426095); fresh `LOV5F` (100004743427169) |
| 5 | Manage ESS Job Definitions and Job Sets (HCM) | tested | 1 + 3 | 2 | PASS | `LOV3` (100004743427054); fresh `LOV6F` (100004744404522) |
| | **Total** | **5 tested** | **40** | **13** | 5 of 5 (+1 re-test) | |
All names start `GAPFILL_AB_B12_`.

## Problems and findings
1. **Safe way for assignments:** an assignment on an existing method changes how existing contracts bill, so each test made a NEW extension-based method with the prefix and assigned the batch 10 test extensions (`BX2` Invoice, `BX3F` Revenue). The environment had no extension-based methods before.
2. **`ProcessingOrder` must be blank** on the assignment row (Oracle: "You must leave the Processing Order attribute blank"); Oracle fills `MethodCfgType=EXTENSION_BASED` and `TransactionCode=BILLING_EVENT`, and shows `AsmFlag` empty.
3. **The three custom ESS tasks export the same file** (`ATK_ESSMETA_USER_JOB_LOV_SOURCE.csv`, job-parameter LOV sources) with the same rows; job definitions and job sets are not in the CSV package. A new source on an existing view object imports first try.
4. **Network drops (DNS `getaddrinfo failed`, one WinError 10060)** hit 2 imports and 2 exports. Rule kept: no second import; the log was fetched by ProcessId with FSCR's `get_setup_task_csv_import_result.py`, and failed exports were re-run into new folders.
5. The HCM tester reported "see CHANGELOG.md" as wrong because the CHANGELOG files were not written yet; they are now (no skill wording change).
6. Not counted (sitting limit reached): Country Default Controls re-judged as safe (0 rows exist; a row for an unused country is a new record) and is the first task for the next sitting; help settings export not read (network).

## What is left
Sitting limit reached (10 tasks: 10 tested, 0 written, 0 failed; plus 3 screen-only). See `MODULE_RESULT.md`.
