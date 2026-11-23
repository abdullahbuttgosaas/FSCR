# Batch 1 re-test after wording fixes (result)

GoSaaS work, not official FSCR. Done by AB with Claude on 2026-11-24. The only environment used was the test pod (release 11.13.26.10.0). FSCR scripts ran in place and no FSCR file was edited. Nothing was deleted, committed or pushed.

| Start | Finish | Note |
|---|---|---|
| about 01:40 | 02:12 | Read the cards, 1 sign-in, 10 fresh tests in parallel, 2 wording fixes, 3 extra re-tests, main-session read-backs, evidence, cards, index, this report |

- **Sign-in (not counted):** one sign-in on port 8765, 01:45:23 to 01:45:28. The browser was still signed in. No second sign-in was needed, and no tester saw a 401/403 or a hang.
- **API interruption:** at about 01:52 an account usage limit stopped 4 testers: rate types, tax lookups, calendars and value sets. Each had already finished its single import. After the limit reset (02:01) they were resumed with "do not import again". They finished their checks with no second import.

## Scope
The 10 cards that had `retest_after_wording_fix: pending`:
- 8 are in `common-features`.
- 2 are batch-1-era skills in other modules: `general-ledger/manage-journal-categories` and `receivables/manage-alternate-name-mapping-rules`.

Each tester was a fresh sub-agent. It was given only the task name, the path to the current SKILL.md, a record name `GAPFILL_AB_RT_<name>`, a work folder, and the rules (no deletes, no secrets printed, import at most once). The main session then read every record back from Oracle itself.

## Results

| # | Task | Result | Wording fixed | Test records (new) | Fresh test min |
|---|---|---|---|---|---:|
| 1 | Manage Conversion Rate Types (`GL_MANAGE_CONVERSION_RATE_TYPES`) | PASS, 1st test | none | `GAPFILL_AB_RT_CRT` | 5 |
| 2 | Manage Geography Lookups (`HZ_MANAGE_GEOGRAPHY_LOOKUPS`) | PASS, 1st test | none | `GAPFILL_AB_RT_GEO` + code `_A` | 4 |
| 3 | Manage LE Configurator Lookups (`XLE_MANAGE_APPLICATION_LOOKUP`) | PASS, 1st test | none | `GAPFILL_AB_RT_LE` + code `_A` | 4 |
| 4 | Manage Resource Note Type (`HZ_MANAGE_RESOURCE_NOTE_TYPE`) | PASS, 1st test | none | `GAPFILL_AB_RT_NOTE` + code `_A` | 4 |
| 5 | Manage Standard Lookups (`FND_MANAGE_APPLCORE_STANDARD_LOOKUPS`) | PASS, 1st test | none | `GAPFILL_AB_RT_SL` + codes `_A`, `_B` | 4 |
| 6 | Manage Tax Lookup Codes (`ORA_ZX_MANAGE_TAX_LOOKUP_CODES`) | PASS, 1st test | none | `GAPFILL_AB_RT_TAX` + code `GAPFILL_AB_RT_A` | 6 |
| 7 | Manage Transaction Calendars (`GL_MANAGE_TRANSACTION_CALENDARS`) | PASS, 1st test | none | `GAPFILL_AB_RT_TC` (7 dates, 2026-12-07..13) | 6 |
| 8 | Manage Applications Core Value Sets (`FND_MANAGE_APPLCORE_VALUE_SETS`) | PASS, 1st test | none | `GAPFILL_AB_RT_VS` + values `_V1`, `_V2` | 6 |
| 9 | Manage Journal Categories (`GL_MANAGE_JOURNAL_CATEGORIES`) | **PASS on the 3rd test** (tests 1 and 2 failed) | yes, twice (below) | `GAPFILL_AB_RT_JC`, `_JC2`, `_JC3` | 5 + 4 + 3 = 12 |
| 10 | Manage Alternate Name Mapping Rules (`ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES`) | **PASS on the 2nd test** (test 1 failed) | yes (below) | `GAPFILL_AB_RT_ANM`, `_ANM2` | 1.5 + 1 = 2.5 |
| | **Total** | **10 of 10 pass; 0 still pending** | 2 skills | | **about 54** |

- Fresh test minutes are the testers' own start and finish clock times, rounded. They run in parallel, so the wall clock for all of them was about 25 minutes.
- Every create took **1 import (or 1 POST) per test**. Nothing was imported twice.
- **"Fail" here means a skill-test fail.** In every failed test the record was still created correctly, but the tester had to deviate from the skill to finish its checks.

### Wording fixed

**Journal categories, version 0.2.0 to 0.3.0** (scripts unchanged):

- Test 1 failed. The tester had to deviate because:
  - `FSCR` and `GAP` were hard-coded `E:\...` paths to the old `fscr-main\_gap_fills` folder;
  - `FSCRT_` and ETIA-TEST were written into the rules;
  - the build and compare commands had no `--prefix`, so the compare printed a false `RESULT: FAIL`.
- Fix 1:
  - generic `FSCR`/`GAP`/`GAPS`/`RUN`/`PREFIX` placeholders, where FSCR is the copy whose `fusionEnv.properties` is filled in, not a template;
  - `--prefix "<PREFIX>"` in Steps 4, 7A and 7B;
  - 1 to 3 rows allowed;
  - environment names, row counts and run folders removed from the instructions. They are kept only as history in the worked example.
- Test 2 failed. Step 7A's `rest_read_categories.py` finds FSCR only from its old folder and stopped with `No module named 'fusion_auth'`.
- Fix 2: Step 7A now uses the generic gaps-filled helper `common-features/manage-docseq-categories/scripts/rest_read.py --fscr <FSCR>`. The old script is marked "history only".
- Test 3: PASS with no deviation.

**Alternate name mapping rules, version 0.2.0 to 0.3.0** (script unchanged):

- Test 1 failed. The precheck and verify helpers default to `FSCRT_` and printed FAIL. Every command also had the PC's `E:/...` FSCR/GAP paths, and the account and user (`ZZ_TEST_...`, `21541`, a user name) were ETIA-TEST-specific.
- Fix:
  - generic `FSCR`/`GAP`/`RUN`/`PREFIX` placeholders;
  - `--prefix "<PREFIX>"` on every `verify_rules.py` call;
  - environment-specific account numbers, user names, paths and counts removed;
  - one-rule runs allowed.
- Test 2: PASS with no deviation (`PRECHECK: PASS`, `RESULT: PASS`, earlier rules unchanged).

## Main-session read-back (all match)
- **REST:**
  - `currencyConversionTypesLOV` (CRT);
  - `standardLookups/<type>?expand=lookupCodes` (GEO, LE, NOTE, SL);
  - `setEnabledLookups/<type>` (TAX);
  - `valueSets` + `valueSets/<code>/child/values` (VS);
  - `journalCategoriesLOV` (JC, JC2, JC3);
  - `alternateNameMappingRules` with a `q` filter (ANM, ANM2).
- **Transaction calendars:** there is no REST resource. The rows were read from the tester's after-export: the calendar with Mon to Fri as business days, plus its 7 dates. Thursday 2026-12-10 is a holiday.
- **Evidence:** `gaps-filled/evidence/batch-01-retest/<TASK_CODE>/` holds `retest_readback.txt` and `01_retest_readback.png`. They show the import-log result lines and the read-back rows. There are no tokens, server addresses or headers.

## Cards and index
- **All 10 cards:**
  - `retest_after_wording_fix` line removed;
  - `fresh_claude_pass: yes`;
  - new records added to `test_records`;
  - a note "Re-tested 2026-11-24 after the wording fix: PASS".
- **Each CHANGELOG.md** has a dated "Re-test after wording fix, 2026-11-24" section.
- `python rebuild_index.py`: 32 cards applied, **No problems**. Common Features: 26 tested of 148. All 19 modules: 28 tested of 935.

## Notes not applied (wording unchanged after the passing tests)
1. **Which FSCR folder (raised by most testers).** On this PC about 26 folders hold `core\auth\fusionEnv.properties`. The value-sets tester first picked an unconfigured copy, and its export was refused. The tester then switched to the configured copy and passed.
   - Suggestion: add the journal-categories sentence ("whose fusionEnv.properties is filled in for the approved environment") to the other 8 skills' FSCR placeholder.
   - That is a wording change, so it needs another fresh test.
2. **The log one-liner** leaves literal `\t` and `\/`, and the first log lines say "In progress" before "Completed successfully". This is cosmetic.
3. **Worked-example counts** are out of date (expected; the skills say counts grow).
4. **One tester's own console output** showed the server address once: it ran `cat` on a raw POST response. That was in the tester's transcript only. No file in `gaps-filled` contains it.

## Cleanup
- **Sign-in:** the listener exited after sign-in (exit 0) and nothing listens on port 8765.
- **Agents and processes:** all 14 sub-agents have finished. No server or Python process started by this session is running.
- **Scratch files:** the scratchpad work folders were deleted after the evidence was written.
