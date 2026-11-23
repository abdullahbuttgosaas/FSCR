# PLAYBOOK: test one tracker module with FSCR

This is the method we used for Common Features, Procurement and Sourcing and Supplier Management. Follow it
step by step. Claude does the work; the person only signs in to Oracle with their own login.

## Rules (read first, never break)

1. **Only the test environment.** Never production. If you are not sure the environment is a test one, stop and ask.
2. **Create only records whose name starts with `FSCRT_` plus the person's own initials**, for example `FSCRT_AB_`.
   This includes Run Books, projects, lookups and business units. Use neutral test words after the prefix.
   Never use real customer or brand names.
3. **Never edit or delete existing data.** Read it, export it and compare it, but do not change it. A task that needs an
   existing record changed is "Not done", with the reason.
4. **Never print tokens, passwords or user names**: not in chat, files, logs or images.
5. **Each person signs in with their own Oracle login.** Claude never types a password. The person types it in the browser window.
6. **At the end, stop and delete every server or process you started**: the sign-in listener (port 8765),
   headless browsers and Python scripts. Then check nothing is left running.
7. **Screenshots are minimal**: at most 4 PNG table images at 2x resolution (coverage, plan result, the 6-task table,
   the final row values). Each has a title, a clean table and a footer with the source file. No tokens or user names
   are visible. `scripts/make_images.py` makes them from the CSV files, so no number is typed by hand.
8. **Never present an unsourced dependency as verified.** Every "A before B" link needs an Oracle URL and a quote that the
   checker finds in the saved page. Anything else is "unverified".

## Folders

| Folder | What goes there |
|---|---|
| `work/<Module>/` | everything a run makes (scripts write here) |
| `evidence/<Module>/` | the folder you upload to Drive (made by `build_evidence.py`) |
| `project/` | FSCR's own project workspace (FSCR writes here) |

All scripts are in `module-test-kit/scripts/`. Each has `--help`. Run them from that folder:
`cd module-test-kit/scripts`. They need Python 3.10 or newer, standard library only.

## Time log

Write the start time (date and clock time) the moment you begin. RESULT.md ends with:

| Start | Finish | Minutes |
|---|---|---:|
| dd/mm/yyyy hh:mm | dd/mm/yyyy hh:mm | n |

---

## Step 0: Start

1. Write the start time.
2. Ask for (or take from the request) the **module name** and the person's **initials**. Check the name with
   `python scope_filter.py --list`. Dashes and capitals do not matter.
3. Check `core/data-loader/config/env.properties`: `runID` must be **empty** or the person's **own** Run Book.
   If it holds anything else, empty it. *(Run 30: the config pointed at another team's Run Book.)*
4. Sign-in: follow FSCR's own `core/getting-started/onboarding/SKILL.md`. The person puts their environment, Client ID and
   scopes in `core/auth/fusionEnv.properties` (Claude can help, without printing the values), then runs FSCR's PKCE login
   (`core/auth/fusion-oauth-authentication`). A browser opens and the person signs in. If it times out once, try once more.
   *(Run 30: the first try hit a network timeout and the second worked.)*

## Step 1: Coverage (from the scope map)

```bash
python scope_filter.py --module "<Module>" --out ../../work/<Module>
```

This writes `scope_tasks.csv`, `coverage.csv`, `coverage_by_area.csv` and `sample_candidates.csv`.
It re-counts from `module_scope_map.csv` and must say **"match"** against `module_counts.csv`. The levels:

- **a**: FSCR has a skill or guide for the task
- **b**: no skill, but Oracle's catalog has a CSV route (flag Y)
- **c**: neither
- **Missing** = b + c, written **N/total** (for example 26/41)
- **Proposed coverage**: Full if 75% or more of tasks are level a, Partial for 1 to 74%, None for 0.
  Use this value in the tracker. If you change it, give the reason in RESULT.md.

## Step 2: Plan (task-dependency-resolver method)

**2a. FSCR's plan.** Start an FSCR project for the module with FSCR's router (`router/implementation-router`), using the
project name `FSCRT_<XX>_<Module>`. FSCR's `shared/implementation-planning/task-dependency-resolver` orders the tasks, and
`core/project-mgmt/project-workspace-initializer/scripts/create_project_runbook.py` writes the canonical
`project/<id>/artifacts/shared/runbook/current/runbook-plan.json`.

**2b. Same method, scored.** `plan_builder.py` repeats the resolver's method from the FSCR files in this pack:
catalog order with the main offering first, then displaySequence, plus the prerequisites FSCR's own skills name.
It then scores that order:

```bash
python plan_builder.py --module "<Module>" --scope ../../work/<Module>/scope_tasks.csv --out ../../work/<Module>
```

**2c. Oracle dependency links (sourced only).** Read Oracle's own documentation for the module (Oracle Help Center,
26D: the "Implementing ..." guide and the task pages). Save every page you use:

```bash
python fetch_oracle_page.py --out ../../work/<Module>/oracle_docs <https://docs.oracle.com/... page URL>
```

Write `work/<Module>/links_input.csv` (header in `templates/links_input.csv`), one row per link:

- `stated`: the page says B needs A, or "before you do B, do A". Copy the exact words.
- `list order`: the page lists the setup steps in order. Quote the two steps; join pieces with ` ... `.
- `unverified`: a link a senior consultant would expect, but no page you read states it. No URL, no quote.
  It is reported but **never counted as verified**.

Then run the plan builder again with the links. The checker opens each saved page and looks for the quote pieces in order.
A link that fails is `FAILED`; fix it or remove it, never keep it.

```bash
python plan_builder.py --module "<Module>" --scope ../../work/<Module>/scope_tasks.csv --out ../../work/<Module> --links ../../work/<Module>/links_input.csv --docs ../../work/<Module>/oracle_docs
```

**Report three numbers** (from `plan_summary.json`):

- (a) sourced links the plan respects: "X of Y in order", plus how many FSCR's own skills state
- (b) unverified links out of order: "X of Y" (said as unverified)
- (c) FSCR-stated prerequisites out of order: "X of Y"

*(Run 30 used links from memory and called some "GUESS". From Run 33 on, every link carries a URL and a checked quote.)*

## Step 3: Runbook check

Create the Run Book from FSCR's plan with FSCR's `core/runbook` (`runbook_rest.py create-runbook --project-root ...`),
named `FSCRT_<XX>_<Module>`. Then:

```bash
python runbook_check.py --runbook-plan <project>/artifacts/shared/runbook/current/runbook-plan.json --scope ../../work/<Module>/scope_tasks.csv --links ../../work/<Module>/oracle_links.csv --out ../../work/<Module>
```

If you read the Run Book's tasks back from Oracle, save them as JSON and add `--oracle-tasks <file>`. The script removes
performer names and Oracle self links (they hold your environment's address).
It counts steps, steps with a route, manual steps, manual steps that have a CSV route, steps with a prerequisite, and
sourced links in order. **Do not use owner or validation-step fields as criteria.** FSCR leaves them empty by design.
*(Run 30 scored 5 items including owner and validation and got 0 of 144, which said nothing about quality. Dropped from Run 33 on.)*

**If the create call times out or returns "unknown":** do not resend it (FSCR's own rule). Wait, list the Run Books by
name, and when it appears, bind it by hand: put its ID in the project's `runbook_control` binding and in `runID`.
If it never appears, say so and create one new Run Book. *(Run 30: the 144-task create timed out and appeared later.
Run 33: timed out, found later, bound by hand. Run 34: the first try failed on DNS with nothing in Oracle; the second
timed out and was found later.)*

## Step 4: Six-task sample test

Pick from `sample_candidates.csv`: **2 Skill + route, 2 Route only, 2 Neither**, as far as they exist. If a group
has fewer tasks, take what exists and say so; do not swap in tasks from another group. Prefer tasks that create a new,
stand-alone record. Write `work/<Module>/six_tasks.csv` (header in `templates/six_tasks.csv`).

For each task:

1. **Read first**: export the current setup (FSCR task-level export) and check that your `FSCRT_<XX>_` name is not already used.
2. **Load** through FSCR: Data Loader with Task Hook (`core/data-loader`), on the person's own Run Book.
3. **Task Hook rule results must come from real checks.** Write each rule result only from something you actually checked
   (the export, the CSV, Oracle's response). Never mark a rule passed without that. *(Runs 30 and 33.)*
4. **Read back** every record you created (an export after the load, or a REST GET), and write down the ID.
5. Result: `Done`, `Done with a fix` (say the fix), `Not done` (say why) or `Not counted`.

Known problems and what to do:

- **The skill names a REST object the Data Loader can't load:** use the FSM CSV package (task-level export,
  then import of the CSV files) through the Data Loader. Record it as a fix. *(Run 33 Document Styles, Run 34 Cost Factors.)*
- **The import CSV needs an internal ID column** that a new record cannot have (for example OriginalQuestionId, AgencyId):
  stop after 2 tries and mark it "Not done: Oracle's CSV needs an internal ID". Check the re-export to confirm 0 rows
  were created. *(Run 33 Compliance Checklist Questions, Run 34 Certifying Agencies.)*
- **The task needs a business unit function that no test BU has** (for example a Procurement BU): never add the function
  to an existing BU. Create a **new** test BU (`FSCRT_<XX>_BU`) only if that is possible without changing existing data.
  If it would need a new ledger, legal entity or other big setup, mark the task "Not done: missing prerequisite".
  *(Run 33 Compliance Checklist Sections, Run 35 Requisitioning BU Mapping.)*
- **Oracle has no CSV and no create API for the task** (catalog CSV flag N, and the REST resource is missing or read only):
  this is screen-only work in Oracle. Mark it "Not done: Oracle has no CSV or API" and **do not count it against FSCR**
  in the Execution score. *(Run 30 Resource Organizations and Data Roles, Run 33 Approval Groups and Corporate Cards,
  Runs 34 and 35 Messages.)* Check with a read only: the catalog flag and a REST describe or GET.
- **Oracle rejects a value:** use the code Oracle expects. *(Run 34: INDEPENDENT was rejected and INDEP worked.
  Run 35: lookups needed RestAccessSecured and a start date.)*
- **REST does not show a record you created** (for example lookups marked SECURE): read it back with an export instead. *(Run 30.)*

## Step 5: Scoring (tracker Guide wording)

Scores are 1 to 5; leave blank if that part was not run. Exact wording from the tracker's Guide sheet:

| Dimension | What it measures | 1 | 3 | 5 |
|---|---|---|---|---|
| **Plan accuracy** | How well FSCR maps the requirements and target configuration workbook to the right Fusion setup tasks and dependencies | Wrong or missing tasks; consultant rebuilds the plan | Mostly right; some tasks or dependencies missed | Matches what a senior GoSaaS consultant would plan |
| **Runbook quality** | Completeness, sequencing and usability of the runbook FSCR builds | Unusable without major rework | Usable after consultant edits | Usable as is in delivery |
| **Execution & validation** | Loads, imports/exports and validation against an authorized 26D+ environment | Failed or unreliable | Ran with manual fixes | Ran clean; validation caught real errors |

| Field | Value | Meaning |
|---|---|---|
| Fit rating | High | Usable as is |
| Fit rating | Medium | Usable with GoSaaS adaptation |
| Fit rating | Low | GoSaaS must build its own skills |
| Fit rating | None | Not covered |
| FSCR coverage | Full | FSCR ships skills/workflows for the module's core setup |
| FSCR coverage | Partial | Some setup areas covered |
| FSCR coverage | None | No FSCR content found for the module |
| FSCR coverage | Unknown | Not yet checked against the FSCR repo |
| Test status | Blocked | Stopped by environment, access or FSCR content issue — say why in Key findings |

How we applied it (2 and 4 sit between the anchors):

- **Plan accuracy**: all module tasks planned, and (a) is the main signal. 5 means every sourced link is in order and
  FSCR states the links. 4 means 90% or more in order. 3 means some links missed or FSCR states almost none.
  1 means tasks missing or wrong.
- **Runbook quality**: 3 when the steps are complete and in order but have no prerequisites, and some manual steps
  have a CSV route (needs consultant edits). 2 when most steps are manual or it needed heavy filling.
- **Execution & validation**: count only tasks Oracle lets you load (CSV or API). 5 means they ran clean and validation
  caught real errors. 3 means they ran with manual fixes, or some loadable tasks failed.
- **Fit rating**: Medium when FSCR does real work but GoSaaS must add dependency links, Run Book prerequisites or recipes.
- Write every score in RESULT.md with a one-line reason tied to a number from the CSV files.

## Step 6: Screenshots (4 images, made from the data)

Fill `work/<Module>/tracker_row.md` first (step 7), then:

```bash
python make_images.py --work ../../work/<Module> --env "test environment, <release>"
```

This makes `01_coverage.png`, `02_plan_result.png`, `03_six_task_table.png` and `04_tracker_row_values.png` in
`work/<Module>/images/`. It refuses to make them if a token, user name, e-mail or machine path is in the text.
Open each image and look at it before you upload.

## Step 7: Tracker row, RESULT.md and evidence folder

1. `python tracker_row.py template --module "<Module>" --coverage ../../work/<Module>/coverage.csv --initials <XX> --out ../../work/<Module>/tracker_row.md`,
   then fill every TODO following `SHEET_FILL_GUIDE.md`, and run `python tracker_row.py check ../../work/<Module>/tracker_row.md` until it says PASS.
2. Write `work/<Module>/RESULT.md` from `templates/RESULT.md`: verdict, plan, Run Book, six-task table, scores with
   reasons, what is missing, records created, and the time table.
3. Build and check the upload folder:

```bash
python build_evidence.py --module "<Module>" --work ../../work/<Module> --out ../../evidence --names "<person's name>,<sign-in name>"
```

Layout: `evidence/<Module>/RESULT.md, tracker_row.md, plan.csv, oracle_links.csv, images/, data/, INDEX.md`.
It must end with **PASS**. Then run `python secret_scan.py ../../evidence/<Module>` once more.

## Step 8: Hand-over and clean-up

1. The person uploads `evidence/<Module>/` to Drive and sends **Abdullah** the folder link. People do **not** edit the
   tracker; it is view only. Abdullah pastes `tracker_row.md` and adds the link as the Evidence link.
2. **Stop and delete** every server or process started: the sign-in listener on port 8765, headless browsers and
   Python scripts. Check that port 8765 is free and no `msedge`/`chrome` headless or `python` process from this run is
   left. Delete temporary files in `work/` that are not needed. Keep `evidence/`.
3. Write the finish time and the minutes in RESULT.md.

## Lessons from our runs (quick list)

| Lesson | Run |
|---|---|
| A Run Book create can time out: don't resend, check later by name, bind by hand | 30, 33, 34 |
| A skill can name a REST object the Data Loader can't load: use the FSM CSV package | 33, 34 |
| Some import CSVs need an internal ID column: stop after 2 tries, mark Not done | 33, 34 |
| Task Hook rule results must be written from real checks | 30, 33 |
| A task can need a business unit function that no test BU has: create a NEW test BU, never edit one | 33, 35 |
| A task with no CSV or API in Oracle is not counted against FSCR | 30, 33, 34, 35 |
| Don't use owner or validation-step fields as criteria | 30 |
| Never present an unsourced dependency as verified | 30 (fixed from 33 on) |
| Settings may point at someone else's Run Book: empty `runID` first | 30 |
| Use Oracle's codes, not meanings (INDEP, not INDEPENDENT) | 34 |
| REST may hide SECURE lookups: read back by export | 30 |

Finished examples: `examples/` (Common Features, Procurement, Sourcing and Supplier Management).
