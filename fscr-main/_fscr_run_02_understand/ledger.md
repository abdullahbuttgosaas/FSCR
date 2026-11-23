# Run 02 ledger: can FSCR understand an existing Oracle environment? (ETIA-TEST, read-only)

Start 2026-11-03 07:10:16 +05:00. All times are local (+05:00). Times per question are approximate (±3 min) where a command printed no timestamp.

## Decisions
- **D1: FSCR is run from a fresh copy, `_fscr_run_02_understand/fscr-work2`, not from `_fscr_run_01/fscr-work`.** Rule 3 forbids changing Run 01 files, and FSCR scripts write into their working copy; Run 01 finding F3 was an export script appending to a project log. The copy includes the Run 01 project `fscrt-run01-om-setup` (no new FSCR project, because a new project creates an Oracle Run Book, which is a write). End check: `diff -rq` of the copy against Run 01's copy shows no file changed.
- **D2: My own REST helper, `rget.py`, refuses any method other than GET.** `fr2.sh` refuses `--method`, and `soap_read.py` refuses any body that isn't a get/find operation. This enforces rule 1 in code.
- **D3: FSCR's compare (`task-level-compare`) was run with `--dry-run` only.** The dry run shows it would create file blobs, upload both ZIPs and create a COMPARE_REQUEST in Oracle. That is not an export, so under rule 1 it was stopped. A local diff (`diff_exports.py`) was used instead.
- **D4: Three setup exports were run.** Payment terms and business units have Run 01 artifacts to compare against. Order lookups covers areas 4 and 5. No export exists for price lists or customers (catalog CSV flag N).
- **D5: Pre-existing records chosen:**
  - BUs: 0012, 01PRC Exam BU, TESTBU4.
  - Price lists: Collector Retail USD D01, TESTPRICELIST4, and zz_test_pl_8034_all (picked because it is IN_PROGRESS with no access set).
  - Payment terms: ORA_HES, ABC, 30 Net.
  - Lookups: ORA_DOO_LINE_TYPES, TEST LINE TYPES, TEST LINE TYPES 1.
  - Order types: teest, Subscription, AMNA_STANDARD_ORDERS.
  - Org customers: accounts 1002 (OM_Test_Customer) and 20008 (Apex Wireless).
  - Person customers: accounts 21264 (party 130534) and 21040 (party 130309). These are the only non-FSCRT person parties with accounts; the third, 130796, was not read.
- **D6: No live reads for the 10 extra tasks in question F.** Their coverage comes from the FSCR catalog and skill folders only (static). An export for each would have added 10 Oracle export processes; I judged the catalog flag sufficient for "does a read route exist" and labelled it not verified.

## Question log (rows in ledger.csv)
- **07:10–07:13 Setup.** Folder created; Run 01 file hashes saved (`run01_hashes_start.md5`, 6,384 files); the original repo matches Run 01's start hashes; token valid (1,947 s left); port 8765 not listening.
- **07:13–07:30 A (8 areas), live reads.** DNS failures (`getaddrinfo failed`, Errno 11001/11002) happened in 5 bursts. Each failed before any request was sent; I retried at most twice per step. `findPersonProfile` failed 3 times, so it was stopped and the prefix is marked not verified.
- **07:16–07:24 D.** Exports 100004733440719 (payment terms), 100004734412462 (business units) and 100004733440757 (order lookups). The first launch at ~07:15 never started because my log folder didn't exist; it sent no Oracle call. My `--output-dir` given as a POSIX path landed the ZIPs in `E:\e\GoSaaS\...`. I moved them into run 02 and deleted the empty `E:\e` tree, which contained only these 3 files (created 07:17–07:18 by this run).
- **07:22–07:31 E, F (offline).**
- **07:26–07:33 B, C (offline analysis).** Two parsing bugs in my own `analyze.py` were fixed: site tags carry attributes, and DisplaySequence is a number in one file and a string in the other.
- **07:29–07:30 Final read-only checks** (`evidence/final/`): no price list or order type updated after 02:10Z (07:10 local); every FSCRT record's LastUpdateDate is before the run.

## Findings (new in Run 02)
- F1: FSCR's BU export **does** show the Default Set (ENTERPRISE for both FSCRT BUs). Run 01 said it was "not readable by REST"; it is readable through FSCR's export route.
- F2: The 4 FSCRT customer accounts have **no customer profile**. Oracle says "The record for Account ID … doesn't exist." So they have no profile class, credit settings or collector, and no payment terms. The 4 pre-existing accounts read all have a DEFAULT profile. FSCR's reader reported only `CUSTOMER_SOAP_HTTP_500`.
- F3: The FSCRT BUs have no primary ledger, no legal entity and no business functions. 94 of 183 BUs have no ledger and 97 have no business functions, so this is common in this pod. FSCR's own BU guidance says to "Align the BU to one primary ledger".
- F4: All 55 price lists in the pod return 0 items through REST, including pre-existing ones. Whether they are really empty or the items child isn't visible to this user is **unclear**.
- F5: FSCR has no executable router. A read question such as "what is set up for X?" has no entry point. The repo's AGENTS.md says read-only requests "must also be selected by the active workflow" and are "not permissible as exploratory shortcuts".
- F6: FSCR's readers return raw data (CSV ZIPs, SOAP XML). Apart from payment-term reconcile, FSCR does no explanation, cross-area joining or comparison against a request.

## Usage readings
| When | Source | Reading |
|---|---|---|
| 07:10 start | app usage tool `get_usage` | context 210,862 tokens (21% of 1,000,000); 5-hour window 10% (resets 07:20); weekly 26% |
| 07:34 end | app usage tool `get_usage` | context 396,367 (40%); 5-hour 11% of a new window (resets 12:20); weekly 28% |

Context size is the running size of this session's context window, not billed tokens. The 5-hour window reset during the run, so its percentages before and after the reset can't be subtracted.

- Finish 2026-11-03 07:34:37 +05:00, 24 min total. Ledger rows were written in one batch after the live reads, not after every question as rule 5 asks; the times per question are reconstructed from command timestamps.
