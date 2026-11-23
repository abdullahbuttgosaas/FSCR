# Batch 1, part 2: Financials generic lookups (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-20. Tested on ETIA-TEST only (release 11.13.26.10.0). No FSCR file was changed; nothing was written outside `gaps-filled`.

| Start | Finish | Note |
|---|---|---|
| 16:13:08 | 16:31:17 | Reading docs, sign-in check, 2 tasks, 2 fresh tests, wording fixes, index, report, cleanup. Sign-in check 16:15:12 to 16:15:39: the cached token was still valid, so no browser sign-in and no address paste were needed (not counted in any task). |

## Results

| # | Task | Status | Working min (write + own live test) | Waiting min (Oracle) | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 1 | Manage Tax Lookup Codes (`ORA_ZX_MANAGE_TAX_LOOKUP_CODES`) | tested | 4 | 3 | PASS (yes) | 3 |
| 2 | Manage Legal Entity Configurator Lookups (`XLE_MANAGE_APPLICATION_LOOKUP`) | tested | 2 | 2 | PASS (yes) | 3 |
| | **Total** | 2 of 2 tested | **6** | **5** | 2 of 2 | **6** |

These minutes come from the run's time log (16:15:39 to 16:22:33 for task 1, 16:22:51 to 16:26:25 for task 2), with Oracle export, import and REST times taken out as waiting time. Task 1 includes one failed import attempt (about 40 seconds of waiting). The fresh tests ran in the background while the next step went on (task 1's ran 16:22:48 to 16:25:46, task 2's ran 16:26:40 to 16:29:11).

**Task 1 compared with task 2:** task 1 took 4 working minutes and task 2 took 2. Reusing the recipe halved the writing time. In part 1 the cut was about 90% (11 minutes down to 1). The cut was smaller here because task 2 was not a copy: it needed its own way to get the ModuleId and the view, and its export check did not work. Oracle waiting was about the same for both (2 to 3 minutes), so for the card, waiting was as large as working time.

Plan estimate (GAPS_PLAN.md section 3): write 20 + 10, test 15 + 10. Actual: 6 working minutes and 6 testing minutes.

## What was reused
- **From FSCR, in place:** the export and import scripts (`shared/setup-export`, `shared/setup-import`), the REST client, and the generic lookups skill (`core/fusion-api/apps-common/lookups`, set-enabled, standard and common references) for every read-back.
- **From part 1 (`manage-standard-lookups`):** the skill structure, rules, log-reading one-liner, the REST wrapper pattern and the evidence renderer. Its scripts could not be reused unchanged, because this is a different package (4 CSVs plus translations, set codes, two views). Four new scripts are in `common-features/manage-tax-lookup-codes/scripts/`.
- **Task 2** uses task 1's 4 scripts unchanged. Its card only covers the view (standard), how to get the ModuleId and module key, and that the export compare does not apply.

## Test records created (all new; none edited or deleted; may not be deletable)
| Task | Live test (main session) | Fresh test (sub-agent) |
|---|---|---|
| 1 | `GAPFILL_TAX_T1` (set-enabled, set COMMON) + `GAPFILL_TAX_A` | `GAPFILL_TAXF1_TYPE` + `GAPFILL_TAXF1_A`, `GAPFILL_TAXF1_B` |
| 2 | `GAPFILL_LE_T2` (standard) + `GAPFILL_LE_A` | `GAPFILL_LEF2_TYPE` + `GAPFILL_LEF2_A`, `GAPFILL_LEF2_B` |

At the end, the main session read all 4 types back from Oracle: READBACK PASS for each. No code was added to a seeded tax or legal entity type. Each task's CHANGELOG.md lists its records.

**Risk (task 1):** the two tax types are set-enabled, user-level types in the tax module. They may be listed in Manage Tax Lookup Codes and in lookup searches for every user of ETIA-TEST. They are not used by any tax list of values unless someone configures them (this is a guess, not tested).

Evidence: `evidence/batch-01/<task-folder>/01_before_readback.png`, `02_after_readback.png`, `03_fresh_test_readback.png`. These are rendered REST read-backs with no secrets.

## Problems and findings
1. **`ChangeSinceLastRefresh` is required.** Task 1's first import failed with `JBO-27014` on all 4 files. The fix was `N`, the value the export shows, and the builder now always writes it.
2. **One package, two views.** `ViewApplicationId` 2 means set-enabled (the codes carry a set, and the type needs a reference group). 0 means standard. Most tax lookups are set-enabled; the legal entity lookups are all standard. The read-back has to use the matching REST resource (`setEnabledLookups` or `standardLookups`).
3. **The export check differs by task.** The tax export showed the new user-defined type and code, so the compare passed. The legal entity export still had 0 rows after the import, so REST is the only check for task 2. This confirms the GAPS_PLAN rule: an empty export proves nothing.
4. **ModuleId when the export is empty.** It comes from a REST search for seeded types named after the scope's moduleKey (`q=LookupType LIKE '<moduleKey>%'`), followed by `--info-of`. Tax and legal entity ModuleIds look alike (same first characters) but are different values.
5. **Git Bash trap (new).** Git Bash rewrites a `/fscmRestApi/...` argument into a Windows path, and the REST client then fails with `REST URL must have a valid HTTPS authority`. The fix is `MSYS_NO_PATHCONV=1`, which is now in the skill.
6. **Fresh testers' notes were applied as wording after the tests and were not re-tested.** The notes covered: how to pass several codes, row counts growing between runs, the misleading export messages, non-ASCII characters in codes, defining `<FSCR>` in the card, the step order for the replaced Step 3a, `set -` on standard codes, and the approval rule.
7. **Cleanup.** The work folder `gaps-filled/_work_b1p2` (exports, logs, read-back JSON) was deleted at the end. No server or background process was left running.

## What should change in GAPS_PLAN.md
1. **Lower the estimates for a new package:** about 5 working minutes for the first skill (plus 3 minutes of Oracle waiting), about 2 for each card, and about 3 for a fresh test. The pattern holds: one full skill per FSM package, then cards.
2. **Group P1 is done.** All 5 lookup tasks are tested (3 standard-package tasks, 2 Financials generic-package tasks). Mark P1 as done in sections 3 and 5, and update the counts in section 1.
3. **Add a rule:** before writing a card, run the after-export once. If the new record does not appear, the card must say that REST is the only check (as for Geography Lookups and LE lookups).
4. **Add a rule for set-enabled lookups:** read the reference group from a seeded type by REST, and never guess it.
5. **Seeded-type use is still untested** for all 5 lookup tasks (adding codes to a seeded type). It needs your decision on a safe test (for example, a disabled code in a low-use seeded type) before any of them counts as fully covered.
6. **Test names:** this part used `GAPFILL_` again, while README rule 5 still says `ZZ_TEST_` or `FSCRT_`. Please pick one so the README can be updated.
7. **The tax chain (P9) can reuse this package knowledge:** tax lookup codes feed tax classifications. Test codes there would affect real tax screens, so P9 tests need the same "new record, clearly named" rule.
