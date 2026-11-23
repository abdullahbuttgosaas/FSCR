# FSCR inventory: one page (Run 07)

**Built 2026-11-04.** Read-only: no Oracle call, no sign-in, original repo unchanged. Full lists are in `FSCR_Inventory.xlsx`.
**Method:** a join of files and outputs that already existed:
- the FSCR catalogs;
- the route audit of 2026-11-02 (`_fscr_spec/ROUTE_AUDIT`);
- the Run 04 and Run 05 ledgers;
- the Run 01–06 reports.

**Source tags:** **[Rnn]** / **[audit]** = an earlier result; **[now]** = computed now by joining. **Labels:** verified / not verified / unclear.

## 1. Tasks (sheet 1_Tasks: all 2,616)
| | Count | Source |
|---|---:|---|
| Catalog tasks | 2,616 | [audit] verified |
| CSV export/import flag Y / N / UNKNOWN | 2,076 / 520 / 20 | [audit] verified |
| Tasks with an FSCR skill or task guide | 848 | [audit] verified |
| Tasks whose skill folder has its own script | 99 | [now] verified |
| Tasks with an adapter (`e2e-adapter.json`) | 16 | [audit] [R04] verified |
| Tasks by area: ERP / SCM / HCM / CX / Common | 730 / 518 / 337 / 490 / 7 | [now] verified (by the rule) |
| Tasks by area: Multiple / Unmapped offering / No offering | 233 / 81 / 220 | [now] verified (by the rule) |

**Area rule:** a task takes the pillar of its skill. Without a skill, it takes the pillar of the catalog offerings that contain it.

## 2. What can be automated today (sheet 2)
| Status | ERP | SCM | HCM | CX | Other¹ | Total | Source |
|---|---:|---:|---:|---:|---:|---:|---|
| Adapter: created a record in our tests | 6 | 0 | 0 | 0 | 0 | **6** | [R04] verified |
| Adapter: failed or blocked in our tests | 4 | 0 | 0 | 0 | 0 | 4 | [R04] verified |
| Adapter: untested (no safe business unit) | 6 | 0 | 0 | 0 | 0 | 6 | [R04] |
| Skill: route named, no create recipe | 63 | 237 | 285 | 212 | 10 | **807** | [now]; recipe finding [R05] |
| Skill: manual steps or no route | 0 | 12 | 4 | 6 | 3 | 25 | [now] |
| No skill; read only through FSCR export (CSV Y) | 539 | 222 | 14 | 209 | 389 | **1,373** | [now]; read not verified per task |
| No skill, no FSCR route | 112 | 47 | 34 | 63 | 139 | 395 | [now] |

¹ Other = Common + Multiple + Unmapped offering + No offering.

## 3. Other options for the rest (sheet 3)
A task can declare several routes, so the rows overlap.

| Route | Skill files [audit] | Tasks [now] |
|---|---:|---:|
| FSM CSV | 739 | 672 |
| REST | 473 | 461 |
| HDL | 43 | 42 |
| ESS | 27 | 27 |
| FBDI | 9 | 9 |
| CX import | 5 | 5 |
| Manual only | 12 | 12 |
| None declared | 17 | 17 |
| SOAP | not an audit category | not already known |

**About REST:** 201 of the 473 files count as REST only because of a `depends_on` link, and only 2 of 10 sampled files name a POST [audit].

**Tasks with no skill:** 1,768 [now]. Of those, 1,373 have CSV flag Y, so Oracle's own FSM CSV route is still open to them.

## 4. Skills (sheet 4: the 934 leaf skills)
| | Count | Source |
|---|---:|---|
| Leaf skills | 934 | [now], matches the earlier verified count |
| By area: HCM / SCM / CX / ERP | 359 / 202 / 166 / 84 | [now] |
| By layer: Shared / Core / Common / Router | 81 / 31 / 8 / 3 | [now] |
| With a task code | 795 | [now] |
| With their own script | 124 | [now] (ERP 35, HCM 27, CX 26, Shared 18, Core 13, SCM 5) |
| Type: planning / orchestration / import / advisory / other | 701 / 102 / 60 / 32 / 39 | [now] |
| Mode: assisted / hybrid / advisory / automated | 718 / 181 / 28 / 7 | [now] |

## 5. What FSCR does today (sheet 5)
- **Supports (create through its own chain):** 6 tasks [R04]. It also has a working REST route for Order Management lookups, used with our request bodies [R01, R03, R06].
- **Can only read:** up to 2,076 CSV-flag tasks through its export; 20 of 20 sampled worked [R05]. 1,373 of them have no skill at all [now].
- **Only advises:**
  - 807 tasks name a route but give no create recipe [now]. In the Run 05 sample, 0 of 40 skills had a full recipe and the median template-field coverage was 0% [R05].
  - 25 more give manual steps or no route [now].
- **Cannot do:**
  - 395 tasks with no skill and no CSV route [now];
  - 42 HDL tasks, because there is no HDL builder [now, R05];
  - 9 FBDI tasks on this pod, which has 0 FBDI objects [now, R01];
  - price lists [R01, R02];
  - customers and person customers [audit, R01];
  - business-unit updates [R03];
  - 4 adapters failed or blocked [R04].

## 6. Effort to build the rest (sheets 6 and 6b)
| Missing piece | Tasks | Measured time per task (run) | Total |
|---|---:|---|---|
| FSM CSV file builder (FSM route, no adapter) | 656 | 2–12 min (business-unit builders R01, R03) | **estimate** 22–131 h, extrapolated from 2 single-object builders |
| REST request bodies (REST route, no adapter) | 459 | 1–5 min (lookups R01/R03/R06) | **estimate** 8–38 h; endpoint discovery time unclear |
| Builders for no-skill CSV-Y tasks | 1,373 | 2–12 min (same basis) | **estimate** 46–275 h; field discovery unclear |
| Patch release-drift adapters | 6 | 0.6–4.1 min per patch (R04) | measured; S10 could not be fixed safely |
| Price-list REST code (create, approve, update) | 1 | ~6 min (R01, R03) | measured |
| Customer SOAP code (organization + person + purposes) | 3 | ~18 min create, ~1 min update (R01, R03) | measured |
| Gap analysis for new requirements | per request | ~8 min for 6 requirements (R06) | measured |
| HDL builder / FBDI route / ESS routes | 42 / 9 / 27 | never built | not already known |
| Unblock 3 FSCR guards; ledgered test BU for 6 adapters | 3 / 6 | never built | not already known |

**Other measured times:** Runs 01–04 took 51, 24, 24 and 33 active minutes; the route audit took 29 min; Run 05 took 28 min.

## Not already known (sheet 7)
- **Export on every CSV task:** whether it works for all of them; only 39 tasks were ever used.
- **Reusable adapter, and HDL/FBDI/ESS routes:** their build time; none was ever built.
- **REST endpoints:** whether the REST skills' endpoints work; only 10 were sampled.
- **Field coverage:** whether skills name the template's fields, outside the 20 tasks measured.
- **Area of 301 tasks:** 81 are in offerings that FSCR's mapping leaves without a pillar, and 220 are in no enabled offering.
- **SOAP routes per task:** this would need a new scan.
- **The 6 untested adapters:** whether they work.
- **FBDI on another pod:** whether it works on a pod with FBDI objects registered.
