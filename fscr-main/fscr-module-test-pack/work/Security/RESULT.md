# Module test: Security

Verdict: **Partly**. FSCR + Claude planned all 6 Security tasks and created the Run Book in one pass, but 0 of 6 tasks were loaded: the BOSS sign-in scope is missing and the rest change existing users or settings.

**Coverage:** 6 tasks: a 6 skill/guide, b 0 route only, c 0 neither. Missing 0/6. Proposed coverage: Full (`coverage.csv`). All 6 are Risk and Security tasks (REST mode, CSV flag UNKNOWN). 52 other security tasks are counted under Common Features, not in this row.

**Plan:** 6 tasks planned (main offering Risk and Security). The 6 tasks are only in the pre-release catalog supplement, so the plan used the effective catalog (copy in the scratch area, kit and pack files unchanged).
- (a) 0 of 0 Oracle-sourced links in order. Oracle's 26B pages (audit setup, EPM data sources) were saved, but none states an order between these 6 tasks. FSCR's skills state 0 of 0.
- (b) 0 of 2 unverified links out of order (audit policies before algorithms; default process owners before Risk Power User role). These are not verified.
- (c) 2 of 5 FSCR-stated prerequisites out of order, as the script reports. On reading the skills, both are the script matching a functional-area name (Activate Algorithms, Add Other Data Sources), not a real prerequisite; the 2 real FSCR prerequisites are in order.

**Run Book:** FSCRT_AB_Security: 6 steps, 6 with a route, 0 manual (0 have a CSV), 0 with a prerequisite. 0 of 0 sourced links in order. Created on the first try, no timeout, read back from Oracle (6 tasks, all Not Started). The order is area-interleaved (position 1 to 6), so Activate Algorithms sits after Add EPM Data Sources.

| # | Task | Group | Result | Record / reason |
|---|---|---|---|---|
| 1 | Activate Audit Policies | Skill + route | **Not done** | Read back only: 8 of 8 audit-status reads returned 200 (2 ON, 6 not on). Enabling changes an existing environment-wide setting. |
| 2 | Activate Algorithms | Skill + route | **Not done** | boss_scope is blank (read stopped: Missing required OAuth scope). Live publish changes existing algorithms. |
| 3 | Add EPM Data Sources | Skill + route | **Not done** | Needs BOSS scope, Risk Cloud client, a seeded EPM connector and real EPM details. |
| 4 | Add Other Data Sources | Skill + route | **Not done** | Needs BOSS scope and Risk Cloud REST access; neither is set up. |
| 5 | Assign Default Process Owners | Skill + route | **Not done** | Needs existing users and BOSS scope; changes existing owners. |
| 6 | Assign Risk Power User Role | Skill + route | **Not done** | Needs existing users and access requests; BOSS scope missing. |

Group note: all 6 tasks are Skill + route, so there are no Route only or Neither tasks to sample.

**Scores (tracker Guide wording)**
- Plan accuracy **3**: all 6 tasks listed (0/6 missing), 0 sourced links so dependencies are not confirmed against Oracle.
- Runbook quality **3**: 6 steps in order with 0 prerequisites; same as Procurement, Sourcing, Purchasing, Supply Planning and Receivables.
- Execution & validation **3**: nothing needed manual fixes and 8 of 8 read-only checks worked, but 0 of 6 tasks were loaded. This score is a judgement for Abdullah to confirm, because no task was loaded and the Guide gives no anchor for that case.
- Fit rating **Medium**: FSCR planned and built the Run Book; GoSaaS must add dependency links, prerequisites and the BOSS access.

**What is missing (GoSaaS gap):**
- BOSS sign-in scope (boss_scope) is not in the sign-in values, so 5 of 6 tasks cannot read or load.
- No Oracle-sourced dependency links for Risk and Security.
- Run Book has 0 prerequisites.
- The plan builder cannot see tasks that are only in the pre-release catalog.

**Records created (all FSCRT_AB_):** Run Book FSCRT_AB_Security (journey ID 300000395228749) and local project fscrt-ab-security. Nothing existing was edited or deleted. The sign-in values were copied into the pack's fusionEnv.properties without being shown (4 of 5 lines differed before).

**Clean-up:** no listener or server was left running; port 8765 free (checked: 0 listeners, no python or headless browser left).

**Time log (working and waiting, minutes are approximate for the split)**

| Part | Start | Finish | Minutes |
|---|---|---|---:|
| Working | 19/11/2026 15:11 | 19/11/2026 15:21 | 6 |
| Waiting (sign-in, Run Book create, Oracle reads, docs retries, images) | 19/11/2026 15:11 | 19/11/2026 15:21 | 4 |

| Start | Finish | Minutes |
|---|---|---:|
| 19/11/2026 15:11 | 19/11/2026 15:21 | 10 |
