
## Part 4, 08:45–08:55: second compare and amendments

### Setup
- **Start:** 08:45:00. The token had expired (-75 s) and port 8765 was free.
- **Login:** FSCR `fusion_login.py --token-cache auto` ran in the background from `fscr-work3`. Browser single sign-on was still active, so no password was needed. Token valid by 08:45:26; the process exited.
- **Baselines:**
  - Run 01 hashed at start: 6,394 files (`evidence/run01_hashes_part4_start.md5`).
  - `fscr-work3` hashed before the compare (`evidence/fscr-work3_hashes_before_compare2.md5`).
- **Usage at start** (`get_usage`): context 599,395 (60%); 5-hour 40%; weekly 33%. Context size is not billed tokens.
- **Backups:** RUN_REPORT.md, ledger.md and ledger.csv were copied to `evidence/corrections_backup/` before any change (md5 identical).

### FSCR compare, second and final run (08:45:35–08:46:40)
- **Pair:**
  - zip1 `evidence/after/exports/…payment_terms_100004733440780.zip` (07:59, before C1).
  - zip2 `evidence/gate/after_c1/…payment_terms_100004734412650.zip` (08:28, after C1).
  - **Decision:** I used 100004733440780 rather than the 07:52 export 100004733446385 as "before". It is the last export before C1, and both are identical (first compare: 0 mismatches).
- **Oracle records created:**
  - file blobs 100004733440833 and 100004734412655
  - upload processes 100004733440842 and 100004733446491
  - compare process **162143105**, COMPLETED
- **Result:** Receivables Payment Terms 1 mismatch / 16 match; Discount 0/2; Payment Schedule 0/20; Translation 0/17.
  - Field detail, extracted from Oracle's nested `AR_PAYMENT_TERM_Discrepancy.xml`: `FSCRT_D25B75AF1,ENTERPRISE` EndDateActive blank → 2028-12-31; all other attributes null.
  - **Verified:** the real change was detected and reported correctly, with no false differences.
  - FSCR's own standard report shows counts only.
- **Local change:** one row appended to the existing `fscr-work3/…/token-usage-log.md`. No other `fscr-work3` file changed or was added.
- **Errors:** none. Retries: 0. Tool calls for the compare and its inspection: about 6.

### Amendments to RUN_REPORT.md, ledger.md and ledger.csv (Amended; history kept)
- **A1:** the Task Hook gate is self-attested by the AI.
  - The `rule-results.json` files were written by the AI. FSCR's Task Hook validates their structure (one result per planned rule file, an allowed status, issue and change shapes), refuses a preview if any result is `blocked`, and does not re-run the rules.
  - The first draft (main run, 07:55) marked as `passed` some rule files that were only judged not applicable. The **permission system** caught it, not FSCR.
- **A2:** C1 = "through FSCR's route with two deviations":
  - (1) a separate config `run-config-blank.properties` with the Run Book ID blank, passed via `--run-config`, so Oracle would not update the Run Book;
  - (2) the payment-terms script is the locally patched copy of 28 October (md5 1508355745c2…; the unpatched original is 1bf32fce4044…, verified by hash at 08:50).
- **A3:** the first compare (162140984) ran on identical data, so its "56 rows matched" proved nothing about detection. It is superseded by the second compare above. Added the report section 7b "Changes outside the named FSCRT records":
  - both compares' blobs, uploads and processes;
  - 9 export processes and the C1 import records;
  - 2 token-usage-log rows appended in `fscr-work3`;
  - Run 01 project: 10 new files, plus 2 single-use files created and deleted by FSCR's upload step;
  - the status log outside the repo; the Run Book unchanged.
- **A4:** FSCR's Data Loader status check writes logs to `C:\Users\PC\.codex\data-loader-status-logs\` (outside the repo and project). Added to the report's "docs wrong or silent" section.
- **A5:** customer DFF hazard. A SOAP update of one segment can blank the other segments, so all three were sent with the untouched ones at their current values. Recorded as a risk for any partial update; whether Oracle would actually blank them was **not tested**.
- **A6:** C4: it is not known whether Oracle's BU import would replace the manager or add a second one, because the import never ran.
- **A7:** capability matrix, "change":
  - payment terms via FSCR (patched, with the A2 deviations);
  - lookups and order types via FSCR's REST client with my own request bodies;
  - business units blocked by FSCR's own rule;
  - price lists and customers via my own calls (no FSCR route on this pod).
- **Amendment ledger entries for earlier sections:**
  - "C1 … CHANGED AND VERIFIED" (follow-up): read as *through FSCR's route with the two deviations in A2*.
  - "FSCR compare tool (run once) … 0 mismatches": superseded by the second compare above (A3).
  - "C6 … other two DFF segments were sent with their current values": see the A5 risk note.
  - "C4 … Not verified: replace or add": see A6.
