# FSCR creation tokens: Run 01 and Run 04

Read-only lookup, 2026-11-03. No Oracle call was made and no server was started.

**Sources:**
- The session transcript, `C:\Users\PC\.claude\projects\E--GoSaaS-fscr-main-fscr-main\fdb8d1e2-ed83-470f-bab1-2a37235221e5.jsonl`. It holds the usage the API returned for each response; each response is counted once by message ID.
- The run ledgers: `_fscr_run_01\ledger.csv` and `_fscr_run_04_create16\ledger.csv`.

**The per-call list:** every call in Run 01 and Run 04 is in `FSCR_Creation_Tokens_calls.csv`, in this folder (415 calls). Each row has the call's time, its label, its token counts and what it did.

Times are +05:00 on 2026-11-03.

## The rule used

1. **Every call was labelled by what its own tool commands did**, read from the transcript:
   - **Object label:** the call read pod data for one object, built or sent its data, ran FSCR's create chain for it, fixed its own create code, or read it back.
   - **Shared or excluded label:** anything else (see the separate lines below).
2. **Shared work is never spread across objects:**
   - **A call acting on several objects:** for example, the lookup discovery and read-back covering types, codes and order types. It goes on its own shared line.
   - **A call that wrote a script used by several objects:** for example, `fr.sh`, `taskhook_lifecycle.py`, `adapter_run.py` and `live_run.py`. It also goes on its own line.
3. **Calls only reading FSCR skill, rule or adapter files are excluded,** even during an object's creation. This includes reading adapter code to find a bug.
4. **Calls where I wrote or changed code, or a patch, for one object are included** in that object.
5. **Segment start** is the first call labelled with the object. **Segment end** is the first call after its last labelled call. That is when the last result, normally the read-back, came back.
6. **Minutes:** for each call of the object, the time until the next call in the session (its tool run plus the next response), added up.
   - Five calls (08:55:30, 08:56:06, 08:56:42, 08:57:27 for S2, and 09:06:20 for S8) both wrote shared driver code and ran a step for the object. Their tokens are on the shared-code line; their time is counted in the object's minutes.
   - Sign-in calls are labelled separately, so no sign-in waiting is inside any object's minutes.
   - Report and ledger calls between an object's calls are not counted in its minutes.
7. **New input** = input tokens + cache-write tokens.

**Run 04 ledger times differ from the transcript.** For example, the ledger says Remit-to (S9) ran 09:12–09:17, but the transcript shows its calls at 09:09:05–09:10:05. The transcript times are used.

## Run 01

| Object | Records | Route | Script written for it | Output | New input | Cache read | Calls | Minutes | Segment |
|---|---:|---|---|---:|---:|---:|---:|---:|---|
| Business units | 2 | Code I wrote (FSCR route, my file builder) | `build_bu_package.py` | 10,183 | 24,442 | 4,671,736 | 18 | 4.4 | 00:44:34–00:56:30 |
| Payment terms | 2 | FSCR end to end (script patched locally on 28 Oct; no code written in this run) | none | 8,664 | 14,773 | 3,597,689 | 11 | 2.7 | 00:56:30–01:02:37 |
| Lookup types | 2 | FSCR with request bodies I wrote | none | 1,165 | 748 | 292,019 | 1 | 0.2 | 00:53:30–00:53:42 |
| Lookup codes | 4 | FSCR with request bodies I wrote | none | 708 | 1,601 | 292,765 | 1 | 0.3 | 00:53:42–00:54:02 |
| Order types | 2 | FSCR with request bodies I wrote | none | 778 | 1,042 | 294,364 | 1 | 0.3 | 00:54:02–00:54:18 |
| *Shared: types, codes and order types (discovery and read-back)* | – | FSCR with request bodies I wrote | `verify_lookups.py` | 3,546 | 4,729 | 1,453,247 | 5 | 1.1 | 00:52:46–00:54:37 |
| Price lists (2 segments) | 2 | Code I wrote (my REST) | `rest_diag.py` | 14,383 | 26,210 | 6,556,954 | 23 | 4.0 | 00:58:03–01:01:23 (rejected attempts) and 06:42:50–06:43:34 (created) |
| Organization customers, person customers and address purposes | 2 + 2 + 6 | Code I wrote (my SOAP) | `customers_soap.py`, `xsd_dump.py`, `fscr_customer_read.py`, `verify_customers.py` | 44,341 | 78,034 | 24,402,378 | 62 | 17.8 | 01:03:22–01:21:42 |

**Customers, persons and address purposes have one combined row.** They cannot be split by call:
- Address purposes were created inside the customer-account calls.
- One call created organization B and both persons together (01:16:58).

The price-list approval (06:58:42–06:59:34) changed existing records, so it is not in this table. It is on the separate lines.

## Run 04

| Skill | Records | Route | Script or code written for it | Output | New input | Cache read | Calls | Minutes | Segment |
|---|---:|---|---|---:|---:|---:|---:|---:|---|
| S2 Payables Calendars | 1 calendar (+12 periods) | FSCR end to end | none | 4,310 | 11,258 | 4,187,586 | 6 | 4.3 | 08:55:13–08:59:39 |
| S3 Payables Payment Terms | 1 | FSCR end to end + my 1-line patch | patched copy `patches\ap-payment-terms\fsm_task_adapter.py` | 11,348 | 21,882 | 10,117,978 | 14 | 4.1 | 08:59:55–09:04:19 |
| S4 Bank Charges | 0 (blocked) | FSCR offline steps only | none | 1,787 | 3,698 | 1,478,930 | 2 | 0.5 | 09:04:43–09:05:10 |
| S8 AutoInvoice Grouping Rules | 1 | FSCR end to end | none | 3,636 | 7,427 | 2,992,609 | 4 | 2.9 | 09:05:35–09:08:29 |
| S9 Remit-to Addresses | 0 (blocked) | FSCR offline + my 1-line patch | patched copy `patches\remit-to\fsm_task_adapter.py` | 4,181 | 8,184 | 3,800,623 | 5 | 0.6 | 09:09:05–09:10:05 |
| S10 Receipt Classes and Methods | 0 (failed) | FSCR offline + my patch | patched copy `patches\receipt-classes\e2e-adapter.json` | 4,033 | 6,297 | 2,312,638 | 3 | 0.7 | 09:10:18–09:11:07 |
| S11 Conversion Rates and Policies | 0 (blocked) | FSCR offline steps only | none | 1,110 | 2,030 | 808,670 | 1 | 0.2 | 09:22:12–09:22:22 |
| S12 Transaction Types | 1 | FSCR end to end (input corrected, no code) | none | 7,612 | 13,833 | 7,895,148 | 10 | 6.2 | 09:11:57–09:18:10 |
| S14 Transaction Sources | 1 | FSCR end to end (input corrected, no code) | none | 6,706 | 10,620 | 5,611,734 | 7 | 3.5 | 09:18:26–09:21:58 |

**Skills not run:**
- **S1 Receivables Payment Terms:** not run in Run 04. Run 04 used the Run 01 result; see "Payment terms" in the Run 01 table.
- **S5 Common Options, S6 Invoice Options, S7 Payment Options, S13 AutoAccounting Rules, S15 Receipt Sources and S16 Receivables System Options:** not run (no safe target), so they have 0 creation tokens.
  - One shared call checked their exports for a usable business unit (09:11:22): output 1,146, new input 1,998, cache read 777,843.
  - That call is on the separate lines, not spread across them.

## Totals for creation work

| Group | Objects | Output | New input | Cache read | Total | Calls |
|---|---|---:|---:|---:|---:|---:|
| **A. Through FSCR, no code written** | Run 01: payment terms, lookup types, lookup codes, order types (+ their shared line). Run 04: S2, S8, S12, S14 | 37,125 | 66,031 | 26,617,161 | 26,720,317 | 46 |
| **B. I had to write a script, code or patch, and records were created** | Run 01: business units, price lists, customers / persons / address purposes. Run 04: S3 | 80,255 | 150,568 | 45,749,046 | 45,979,869 | 117 |
| **C. Tried, nothing created** | Run 04: S4, S9 (patch written), S10 (patch written), S11 | 11,111 | 20,209 | 8,400,861 | 8,432,181 | 11 |
| **Grand total, creation work (A + B + C)** | | **128,491** | **236,808** | **80,767,068** | **81,132,367** | **174** |

**Notes on the groups:**
- In group A, lookup types, codes and order types used request bodies I wrote, but no script; they are in group A for that reason.
- Payment terms ran on a script patched locally on 28 October, before Run 01.

## Separate lines: work not assigned to a single object (not in the totals above)

| Line | Output | New input | Cache read | Total | Calls |
|---|---:|---:|---:|---:|---:|
| Run 01 sign-in (00:43:12–00:43:26; follow-up 06:42:33–06:42:46) | 2,403 | 4,151 | 1,271,805 | 1,278,359 | 8 |
| Run 01 project initialization, Run Book, task-context gate, repo copy (00:47:31–00:51:04) | 11,615 | 27,347 | 6,122,288 | 6,161,250 | 23 |
| Run 01 scripts used by several objects (`fr.sh`, `taskhook_lifecycle.py`) | 2,568 | 5,701 | 508,190 | 516,459 | 2 |
| Run 01 exploring FSCR (core REST client, export, validator, Data Loader options; FSCR customer packager check after creation) | 5,161 | 10,330 | 3,636,306 | 3,651,797 | 12 |
| Run 01 reading an object's FSCR skill or script files | 2,452 | 8,520 | 2,156,122 | 2,167,094 | 6 |
| Run 01 final check of all objects (01:22:57–01:23:38) | 1,614 | 7,146 | 884,567 | 893,327 | 2 |
| Run 01 price-list approval, a change after creation (06:58:42–06:59:21) | 3,165 | 6,298 | 725,401 | 734,864 | 6 |
| Run 01 ledger and report writing (incl. the 06:59–07:06 correction pass) | 71,151 | 117,888 | 10,921,458 | 11,110,497 | 58 |
| Run 01 rest of the run (23:49–00:43 setup, mapping, sign-in wait period; time between the main run and the follow-ups) | 50,240 | 211,825 | 10,601,326 | 10,863,391 | 60 |
| Run 04 project initialization and Run Book (incl. final Run Book check) | 4,070 | 8,045 | 4,900,086 | 4,912,201 | 7 |
| Run 04 scripts used by several skills (`build_task_mapping.py`, `adapter_run.py`, `live_run.py`, `inspect_candidate.py`) | 14,446 | 17,942 | 5,567,812 | 5,600,200 | 8 |
| Run 04 template and data export for all 15 skills (one batch) | 3,404 | 2,111 | 657,420 | 662,935 | 1 |
| Run 04 survey and exploring FSCR | 10,639 | 30,636 | 9,171,455 | 9,212,730 | 14 |
| Run 04 reading a skill's FSCR skill, rule or adapter files | 6,875 | 15,040 | 9,763,891 | 9,785,806 | 13 |
| Run 04 target check for the 6 skills not run | 1,146 | 1,998 | 777,843 | 780,987 | 1 |
| Run 04 discount-basis "F" check, a side question (09:22:48–09:23:05; corrected 2026-11-03: first labelled S11 by mistake) | 2,832 | 3,992 | 2,442,829 | 2,449,653 | 3 |
| Run 04 ledger and report writing | 32,903 | 28,468 | 12,502,776 | 12,564,147 | 16 |
| Between Run 04 and Run 05 (first call of Run 05, 09:40:07) | 1,626 | 3,770 | 832,383 | 837,779 | 1 |
| **All separate lines** | **228,310** | **511,208** | **83,443,958** | **84,183,476** | **241** |

**Check:** creation work (81,132,367) + separate lines (84,183,476) = 165,315,843. That equals all calls from Run 01's start to Run 05's start: Run 01 79,173,537 + Run 04 86,142,306.

**Not recorded:**
- Token usage for the session's automatic summarizing calls; the transcript holds none.
- Token usage per tool command inside one response: the API reports usage per response only, so a response that did two things cannot be split.
