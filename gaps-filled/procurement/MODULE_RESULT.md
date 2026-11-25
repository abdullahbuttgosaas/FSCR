# Procurement: module result

## Cumulative counts (all sittings)
| Status | Count |
|---|---|
| tested | 14 |
| written (fresh test pending) | 0 |
| written (unsafe to test) | 4 |
| failed | 0 |
| screen-only | 2 |
| open (1 of them reserved for the live demo: Freight Terms) | 6 |
| **Total missing tasks** | **26** |

---

## Sitting 3: 2026-11-25 night (AB with Claude, PC): demo task Manage FOB Lookup

Only task: **Manage FOB Lookup** (`PO_MANAGE_FOB_LOOKUP`), released from the demo reserve and filled for the demo (batch 05, size 1, sitting limit 1). Freight Terms stays reserved.

### Counts this sitting
tested 1 · written-unsafe 0 · failed 0 · screen-only 0 · left 6 (incl. 1 demo reserve)

### Per task
| Task | Status | Write / test / wait min | Records (new) |
|---|---|---|---|
| Manage FOB Lookup | tested | 4 / 12 / 5 | GAPFILL_AB_B5_FOB1 (100004744393796); fresh F GAPFILL_AB_B5_FOB2F not created (network drop, no ProcessId); re-test GAPFILL_AB_B5_FOB3R (100004744397138) |

Total this sitting: working 16 minutes, waiting 5 minutes (incl. sign-in). Details: `BATCH_05_RESULT.md`.

### Failed tasks
None.

### Next sitting
1. Approval tasks (4) and task configurations: read approval participants (read-only), then decide disabled-rule test vs unsafe.
2. Freight Terms lookup stays reserved for the demo.

### Test records created
GAPFILL_AB_B5_FOB1, GAPFILL_AB_B5_FOB3R (FOB codes, new; nothing existing changed).

---|---|
| tested | 13 |
| written (fresh test pending) | 0 |
| written (unsafe to test) | 4 |
| failed | 0 |
| screen-only | 2 |
| open (2 of them reserved for the live demo) | 7 |
| **Total missing tasks** | **26** |

---

## Sitting 2: 2026-11-25 evening (AB with Claude, PC)

8 tasks moved: 4 **tested**, 3 **written (unsafe to test)**, 0 failed, plus 2 proven **screen-only**. The sitting limit (10) was not reached: the other open tasks are the 2 demo-reserve lookups and the 5 approval / task-configuration tasks, which need a careful read-only look at approval participants first (see `BATCH_04_RESULT.md`).

### Counts this sitting
tested 4 · written-unsafe 3 · failed 0 · screen-only 2 · left 7 (incl. 2 demo reserve)

### Per task
| Task | Status | Records (new, GAPFILL_AB_) |
|---|---|---|
| Manage Compliance Checklist Sections | tested | B3_CS1, B3_CS3; fresh B3_CS4F |
| Manage Compliance Checklist Questions | tested | B3_CQ1, B3_CQ2; fresh B3_CQ3F |
| Manage Compliance Checklist Templates | tested | B3_CT5 (+ invisible CT2, CT4); fresh B3_CT6F |
| Manage B2B Configuration | tested (REST) | B4_SP1 + B4_TP2; fresh B4_SP2F + B4_TP3F |
| Configure Procurement Business Function | written (unsafe) | none |
| Specify Supplier Contract Management Business Function Properties | written (unsafe) | none |
| Manage Contract Terms Descriptive Flexfields | written (unsafe) | none |
| Manage Collaboration Messaging Domain Value Map | screen-only | none |
| Manage Self Service Procurement Messages | screen-only | none |

Every fresh test passed on the first round with no wrong sentence. Suggestions not applied are listed in each STATUS.md.

### Time (minutes)
| Step | Start | Finish | Minutes |
|---|---|---|---|
| Sign-in, exports, business-function tries (blocked) | 18:17 | 18:24 | 7 |
| Checklist sections, questions, templates: tries and read-backs | 18:24 | 18:33 | 9 |
| 5 batch-03 skills written; 3 fresh tests | 18:33 | 18:40 | 7 |
| B2B REST tries, skill, fresh test; DFF skill; screen-only checks | 18:36 | 18:44 | 8 |
| Cards, tracker, results, index | 18:44 | 18:48 | 4 |

### Next sitting
1. Approval tasks (4) and task configurations: read approval participants (read-only), then decide disabled-rule test vs unsafe.
2. Demo reserve stays: FOB and Freight Terms lookups.

---

## Sitting 1, continuation: 2026-11-25 after the spend-limit reset (AB with Claude, PC)

10 tasks moved this sitting (the sitting limit): 9 **tested**, 1 **written (unsafe to test)**, 0 failed.

### Counts this sitting
tested 9 · written-unsafe 1 · failed 0 · screen-only 0 · left 16 (incl. 2 demo reserve)

### Per task
| Task | Status | Fresh test records (new, GAPFILL_AB_) |
|---|---|---|
| Manage Special Handling Types | tested | SH3F, SH4R, SH5R |
| Manage Contract Line Types | tested | LT4F, LT5R, LT6R |
| Manage Contract Clause Types | tested | CT3F, CT4R, CT5R (codes on OKC_SUBJECT) |
| Manage Contract Terms Value Sets | tested | VS3F, VS4R, VS5R (+GAPFILL_G1/G2, H1/H2, I1/I2) |
| Manage Contract and Procurement System Integrations | tested | TS6F, TS7R, TS8R (path A, internal) |
| Manage Purchasing Profile Options | tested | PO2F, PO3R, PO4R |
| Specify Contract Clause Import XML File Location | tested | none (test-and-restore, restored) |
| Manage Collaboration Messaging Configuration | tested | none (test-and-restore, restored) |
| Manage Channel Settings | tested | none (test-and-restore, restored) |
| Configure Electronic Signature for Procurement Documents | written (unsafe) | none (needs provider credentials) |

The 6 sitting-1 skills needed 3 fresh rounds (F, R, R2): rounds F and R found real faults (no safe log reader, a wrong sentence, a recovery path the reader could not find, missing export line); round R2 found no wrong sentence. The records the first, stopped testers loaded (LT3F, CT2F, VS2F) were not re-imported. Tester suggestions that would change wording again are listed in each STATUS.md as "not applied".

### Time (minutes, this continuation)
| Step | Start | Finish | Minutes |
|---|---|---|---|
| Fresh rounds F and R for 6 skills, fixes | 17:05 | 17:50 | 45 |
| Batch 02 tests (own test-and-restore) and 3 new skills | 17:20 | 17:58 | 38 |
| Round R2 (6) + batch 02 fresh tests (3) + collab re-test | 17:52 | 18:11 | 19 |
| Cards, tracker, results | 18:08 | 18:15 | 7 |

### Next sitting
1. Harder tasks: compliance checklist sections, questions and templates; Contract Terms DFF; the two business function tasks (judge against the unsafe rule).
2. The 8 "neither" tasks (SSP messages, B2B configuration, domain value map, 5 approval / task-configuration tasks).
3. Demo reserve stays: FOB and Freight Terms lookups.

### Test records created this continuation (all new; nothing existing was left changed)
GAPFILL_AB_B1_SH3F, SH4R, SH5R · LT4F, LT5R, LT6R · CT3F, CT4R, CT5R · VS3F, VS4R, VS5R (+GAPFILL_G1, G2, H1, H2, I1, I2) · TS6F, TS7R, TS8R · GAPFILL_AB_B2_PO2F, PO3R, PO4R. Three shared settings were changed and restored (XML location, collab messaging parameter, two channel setting values).

---

## Sitting 1: 2026-11-25 (AB with Claude, PC)

**Stopped early.** At about 17:30 the org reached its monthly Claude spend limit (API 429; resets 2026-11-28 20:00 PKT). All 5 fresh testers stopped mid-run. 6 tasks reached "written": skill done and AB's own live test passed. None is **tested**, because no fresh test finished.

### Counts this sitting
tested 0 · written (fresh test pending) 6 · written-unsafe 0 · failed 0 · screen-only 0 · left 20 (incl. 2 demo reserve)

### Demo reserve (never filled in a sitting)
- `PO_MANAGE_FOB_LOOKUP`, Manage FOB Lookup
- `PO_MANAGE_FREIGHT_TERM_LOOKUP`, Manage Freight Terms Lookup

See `DEMO_RESERVE.md`.

### Per task
| Task | Status | Write | Test | Wait | Test records |
|---|---|---|---|---|---|
| Manage Special Handling Types | written (fresh pending) | 4 | 3 | 3 | GAPFILL_AB_B1_SH1 |
| Manage Contract Line Types | written (fresh pending) | 4 | 4 | 3 | GAPFILL_AB_B1_LT2, fresh LT3F |
| Manage Contract Clause Types | written (fresh pending) | 5 | 3 | 2 | GAPFILL_AB_B1_CT1, fresh CT2F |
| Manage Contract Terms Value Sets | written (fresh pending) | 4 | 3 | 3 | GAPFILL_AB_B1_VS1, fresh VS2F |
| Manage Contract and Procurement System Integrations | written (fresh pending) | 5 | 6 | 6 | GAPFILL_AB_B1_TS4R (round trip) |
| Manage Purchasing Profile Options | written (fresh pending) | 4 | 2 | 2 | GAPFILL_AB_B2_PO1 |
| **Total** | | **26** | **21** | **19** | |

Plus about 13 minutes of read-only exports and REST checks for all 19 CSV tasks, and 2 sign-ins (waiting).

### Failed tasks
None.

### Next sitting
1. After 2026-11-28 20:00 PKT: fresh-test the 6 written skills with new names (SH3F, LT4F, CT3F, VS3F, TS6F, PO2F). Mark each tested when it passes.
2. Finish batch 02: Clause Import XML File Location, Collaboration Messaging Configuration, Channel Settings, Electronic Signature. See `BATCH_02_RESULT.md` for what the exports showed.
3. Harder tasks: compliance checklist sections, questions and templates (sections need a procurement BU), Contract Terms DFF, both business function tasks.
4. The 8 "neither" tasks: SSP messages (export gives no ZIP), B2B configuration (REST `b2bTradingPartners` answers), domain value map, and 5 approval / task-configuration tasks (approval REST gave HTTP 500 without a finder).

### Test records created (all GAPFILL_AB_, new; nothing existing was changed)
GAPFILL_AB_B1_SH1 · GAPFILL_AB_B1_LT2 · GAPFILL_AB_B1_LT3F · GAPFILL_AB_B1_CT1 · GAPFILL_AB_B1_CT2F · GAPFILL_AB_B1_VS1 (+GAPFILL_V1, GAPFILL_V2) · GAPFILL_AB_B1_VS2F (+GAPFILL_F1, GAPFILL_F2) · GAPFILL_AB_B1_TS4R · GAPFILL_AB_B2_PO1. Refused, not created: GAPFILL_AB_B1_LT1, TS1, TS2, TS3.
