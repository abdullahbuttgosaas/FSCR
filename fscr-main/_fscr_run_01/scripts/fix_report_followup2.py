"""One-off: apply the follow-up 2 corrections to RUN_REPORT.md (exact-match replacements; fails if any anchor is missing)."""
from pathlib import Path

p = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01\RUN_REPORT.md")
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert s.count(a) == 1, ("anchor not found once", a[:90])
    s = s.replace(a, b)


# Part 1 summary
rep("""- **FSCR end to end, 10 records:** lookup types, lookup codes and order types (SCM), and payment terms (ERP).
  - I wrote only the data (JSON payloads or blueprint) and thin wrappers that call FSCR's own commands.
  - Payment terms are the strongest case. FSCR exported the current setup, previewed, built, validated, ran its approval gates, imported, re-exported and reconciled: "verified", 0 mismatches.""",
"""- **FSCR end to end, but only with an earlier local patch, 2 records: payment terms (ERP).**
  - FSCR exported the current setup, previewed, built, validated, ran its approval gates, imported, re-exported and reconciled: "verified", 0 mismatches.
  - This ran on the repo's `payment_terms_fsm_package.py`, which is the copy patched locally on 2026-10-28 (15:59). The original script failed on this pod on 2026-10-28 with `payment_terms_object_order_mismatch`: it has a hard-coded object order, and ETIA-TEST declares a different one. That failure is recorded in `project/draft-impl-project-20261028/state/runs/20261028-payment-term-create-blocked.json`. **This run did not re-test the unpatched original.**
- **FSCR route and client, but my own request bodies, 8 records: lookup types, lookup codes and order types (SCM).**
  - FSCR supplied the endpoint, the REST client, the lookup-view discovery order and the approval rule. It gave no body fields. The fields, ModuleId and enabled-flag handling came from Oracle's describe, a read of an existing lookup, and my own knowledge (detail in section 3a).""")
rep("- **As is:** Receivables payment terms (ERP), and lookups or order types through its REST route (SCM).",
    "- **With a patch:** Receivables payment terms (ERP). They need the local order-check patch of 2026-10-28; the unpatched original failed on this pod and was not re-tested in this run.\n"
    "- **Route only, with your own request body:** lookups and order types (SCM). FSCR's REST route and client work, but someone has to supply the body fields and ModuleId.")

# Follow-up block: approval
rep("- One difference to know: I sent StatusCode APPROVED, but Oracle stores both as **In progress** (IN_PROGRESS). Your records give no status, so I left them as they are. Approving them is a separate action in Oracle's pricing UI or REST.",
"""- Oracle stored both as **In progress** (IN_PROGRESS), even though I sent StatusCode APPROVED.

**Follow-up 2: approving the price lists (2026-11-03 06:59 +05:00).**
- FSCR route: none. `import-price-lists/SKILL.md` ("Approval-status decision") sets STATUS_CODE only inside the FBDI workbook before an import. It has no route for changing the status of an existing price list.
- Oracle route: the read-only `priceLists/describe` (`evidence/pricelists/describe.json`) shows StatusCode `updatable: true`, values from ORA_QP_APPROVAL_STATUSES, and item actions get/update/delete.
- Approach 1, used for both: `PATCH /fscmRestApi/resources/11.13.18.05/priceLists/{PriceListId}`, body `{"StatusCode":"APPROVED"}` (`payloads/pl_approve.json`), Content-Type application/json. No retry and no other approach were needed.

| Price list | PriceListId | Sent | Oracle response | Final status (read-back) | Error |
|---|---|---|---|---|---|
| FSCRT_Quillon Ridge Wholesale Tents USD F01 | 300000394622041 | 06:59:10 | HTTP 200, StatusCode APPROVED, Status "Approved" (`evidence/pricelists/pl1_approve_a1.json`) | **Approved** | none |
| FSCRT_Brindle Harbor Dock Equipment EUR F01 | 300000394623080 | 06:59:17 | HTTP 200, StatusCode APPROVED, Status "Approved" (`evidence/pricelists/pl2_approve_a1.json`) | **Approved** | none |

- Read-back (`evidence/pricelists/readback_after_approve.json`), compared with the earlier read-back: the only fields that changed are Status, StatusCode, LastUpdateDate and Oracle's version tag (ETag). Access sets are unchanged. EntityApprovalStatusCode is still null, so the approval-flow opt-in is not in use. No new records were created.""")
rep("**Limits:** one pod, one release, two records per module; one login (token valid 1 hour; the run fit inside it).",
    "**Limits:** one pod, one release, two records per module. The main run used one login (token valid 1 hour). Follow-up 1 needed a second login, which completed silently via browser single sign-on.")
rep("**Result (updated 2026-11-03 06:43):** all 24 input records are now created in ETIA-TEST and read back.",
    "**Result (updated 2026-11-03 07:05):** all 24 input records are now created in ETIA-TEST and read back, and both price lists are Approved.")

# Scorecard and totals
rep("| 3 Payment Terms | ERP | 2 | 2 | 0 | 0 | Yes, with own script | FSM CSV, FSCR end to end |",
    "| 3 Payment Terms | ERP | 2 | 2 | 0 | 0 | Yes, with own script (locally patched 2026-10-28) | FSM CSV, FSCR end to end on the patched script (original not re-tested) |")
rep("| 4 Lookup Types + Codes | SCM | 2 + 4 | 6 | 0 | 0 | Yes (routes to core REST) | REST via FSCR client |",
    "| 4 Lookup Types + Codes | SCM | 2 + 4 | 6 | 0 | 0 | Route only (endpoint + client, no body recipe) | REST via FSCR client, my request bodies |")
rep("| 5 Order Types | SCM | 2 | 2 | 0 | 0 | Yes | REST via FSCR client |",
    "| 5 Order Types | SCM | 2 | 2 | 0 | 0 | Route only (endpoint + client, no body recipe) | REST via FSCR client, my request bodies |")
rep("- **Created end to end with FSCR only: 10.** Definition: the create path ran only FSCR skills and scripts; I supplied data files and command wrappers. Items: 2 lookup types, 4 lookup codes, 2 order types, 2 payment terms.",
"""- **FSCR end to end on a locally patched script: 2** (payment terms). The create path ran only FSCR skills and scripts, plus my blueprint and wrappers. The script had been patched on 2026-10-28; the unpatched original was not re-tested.
- **FSCR route and client with my own request bodies: 8** (2 lookup types, 4 lookup codes, 2 order types). FSCR gave the endpoint, client, discovery order and gates. The body fields and ModuleId are mine (section 3a).
- *(The earlier figure, "10 created by FSCR alone", was wrong and is replaced by these two lines.)*""")

# Jobs table
rep("| REST creates | 10 POSTs (2 types, 4 codes, 2 order types; plus 2 rejected price-list POSTs, then 1 diagnostic re-send) | 10 / 0 (+ 3 rejected, nothing created) |",
"""| REST creates, main run | 8 POSTs succeeded (2 types, 4 codes, 2 order types; 8 `*_post_response.json` files) + 3 price-list POSTs rejected (00:59 FSCR client by id, 01:00 `rest_diag.py` diagnostic re-send by id, 01:01 by BU name; all HTTP 400) | 8 created / 3 rejected, nothing created |
| REST creates, follow-up 1 | 2 price-list POSTs (HTTP 201; `evidence/pricelists/pl1_create.json`, `pl2_create.json`) | 2 created / 0 rejected |
| REST status changes, follow-up 2 | 2 price-list PATCHes StatusCode→APPROVED (HTTP 200; `pl1_approve_a1.json`, `pl2_approve_a1.json`) | 2 changed / 0 failed |""")
rep("| SOAP creates | 4 createLocation, 4 createOrganization/createPerson, 4 createCustomerAccount succeeded; 7 faulted calls created nothing | – |",
    "| SOAP creates | 20 calls: 12 succeeded (4 createLocation, 4 createOrganization/createPerson, 4 createCustomerAccount) and 8 faulted, each creating nothing. The faults were 7 party creates (Kestrel 3, Caspian 2, Linnea 2) and 1 account create (Kestrel, SetCode). | 12 / 8 faulted |")
rep("| Run Book | WorkerJourneyId 300000394648040 | 5 tasks |",
"""| Run Book | WorkerJourneyId 300000394648040 | 5 tasks |

**Count method:** REST and SOAP calls were counted from the evidence files (`evidence/*_post_response.json`, `evidence/pricelists/*`, `evidence/customers/*_state.json`) and from the printed result lines of each call in this session's tool output. The tool output was needed because `customers_soap.py` overwrites its request/response files on each attempt, so faulted SOAP calls leave no separate file. The earlier figures "10 POSTs" and "7 faulted" were miscounts.""")

# Section 3a: provenance of the 8 lookup records
rep("### 4. Everything I wrote (all in `_fscr_run_01/scripts`)",
"""### 3a. Where each part of the 8 lookup and order-type records came from

FSCR files used (paths in `fscr-work/`):
- `core/fusion-api/apps-common/lookups/SKILL.md`: the discovery order Common → Standard → Generic → Set-enabled, the rule to approve before create, and no automatic retry.
- `core/fusion-api/apps-common/lookups/references/standard-lookups.md`: endpoints (lines 16 and 18) and client usage (`--method POST --body-file`). It says to "put the exact supported JSON body in a temporary file" but gives no fields.
- `core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`: the client that sent every POST.
- `pillars/scm/order-management/orders/manage-order-lookups/SKILL.md`: lists ORA_DOO_ORDER_TYPES as user-extensible, says to route to apps-common, and adds Oracle doc links. It has no write recipe and no fields.

| Records | Endpoint | Lookup view | ModuleId | Payload fields | Enabled flag |
|---|---|---|---|---|---|
| 2 lookup types (FSCRT_OUTDOOR_ACTIVITY_F01, FSCRT_CARRIER_SERVICE_TIER_F01) | FSCR: `standard-lookups.md:16` `POST /standardLookups` | **Mine.** FSCR's discovery order applies to existing lookups. For a new type I chose Standard because the OM lookup ORA_DOO_ORDER_TYPES was found there (read-only probes: commonLookups count 0, standardLookups count 1). | **Discovery**: copied `61ECAF4AAB00E990E040449821C61C97` from the existing ORA_DOO_ORDER_TYPES. That it means "Order Management" is *inferred*, not verified against a module table. | **Oracle describe** (`evidence/standardLookups_describe.json`: LookupType, ModuleId, Meaning, CustomizationLevel mandatory; Description, RestAccessSecured optional). The mappings CustomizationLevel U = "User" and "Authenticated" = `AUTH` are **mine**, with AUTH seen on the existing lookup. "Default" means the field was omitted, and Oracle stored SECURE. | n/a |
| 4 lookup codes (HIKING, PADDLING, STANDARD, FREIGHT) | FSCR: `standard-lookups.md:18` `POST /standardLookups/{LookupType}/child/lookupCodes` | follows the type | n/a | **Oracle describe** (child lookupCodes: LookupCode, Meaning, EnabledFlag mandatory with default Y; Description, Tag, DisplaySequence optional). STANDARD "(auto)" sequence was omitted: **my decision**. | **Mine**: Yes/No sent as `Y`/`N`. FSCR says nothing on it. Read back: FREIGHT = N. |
| 2 order types (FSCRT_SO_TRAIL_DEALER_F01, FSCRT_SO_WARRANTY_SWAP_F01) | FSCR: same `standard-lookups.md:18` with LookupType ORA_DOO_ORDER_TYPES | **FSCR procedure** (apps-common discovery order), run by me with read-only GETs | n/a (existing type) | **Oracle describe**, same fields as above | **Mine**: WARRANTY_SWAP sent `N`, read back N |

**Which FSCR skill gave a write recipe:** only `core/fusion-api/apps-common/lookups` (via `standard-lookups.md`), and only a partial one: method, endpoint, client command and gates, with no body schema. The Order Management pillar skill gave none. These 8 records are therefore labelled "FSCR route and client, my own request bodies", not "FSCR end to end".

### 4. Everything I wrote (all in `_fscr_run_01/scripts`)""")

# Payment-term name limit
rep("| Payment term name ≤ 15 characters | Not found in the skill text | Yes (existing data max 15; Oracle limit) |",
    "| Payment term name ≤ 15 characters | Yes, in `ora-resource/ora_input_validation.md:69` (\"Enforce Name 15\"). The earlier report missed it. | Confirmed in Oracle's describe: `paymentTermsLOV` Name maxLength 15 (`evidence/pt_limit/paymentTermsLOV_describe.json`). This LOV lists both FSCRT receivables terms. |")
rep("10. **Payment terms:** the 15-character name limit is not stated in the skill text I read. The prior patched order check worked unchanged on this pod.",
    "10. **Payment terms:** the original `payment_terms_fsm_package.py` hard-codes the business-object order [TERM, TRANSLATION, DISCOUNT, LINE]. ETIA-TEST declares [LINE, TERM, TRANSLATION, DISCOUNT], so the original failed here on 2026-10-28 (`payment_terms_object_order_mismatch`). This run used the locally patched copy and did not re-test the original. (Correction: the 15-character name limit *is* in the skill's `ora_input_validation.md:69`; the earlier report said it was not.)")

# Capability matrix
rep("| 1 | Create setup | BU (FSM), PT (FSM), lookups/order types (REST) | Works for 4 of 8 modules; 10 records pure FSCR, 2 with my builder |",
    "| 1 | Create setup | BU (FSM), PT (FSM), lookups/order types (REST) | 2 records FSCR end to end only **with a patch** (PT, local patch 2026-10-28; original not re-tested); 8 by FSCR route + client with my bodies; 2 BUs with my builder |")
rep("| 6 | Breadth and robustness | Errors, retries, recovery | Gates fail closed correctly; no unsafe auto-retries | Task Hook refusal, preflight approval stops | Tooling breaks on Windows; an export script edits an existing file silently |",
    "| 6 | Breadth and robustness | Errors, retries, recovery | Gates fail closed correctly; no unsafe auto-retries | Task Hook refusal, preflight approval stops | Tooling breaks on Windows; an export script edits an existing file silently |\n"
    "| – | **Not yet tested** | – | – | – | Changing existing setup; understanding and explaining the environment across areas; repeat runs; other areas (pillars and modules outside these 8) |")

# Honest assessment
rep("- Where a skill has its own script (Receivables payment terms), FSCR ran the whole chain without code changes on this pod: export, preview, confirmation, build, validation, approval gates, import, re-export, reconcile. It proved the result with a field-level reconcile.",
    "- Where a skill has its own script (Receivables payment terms), FSCR ran the whole chain on this pod: export, preview, confirmation, build, validation, approval gates, import, re-export, reconcile. It proved the result with a field-level reconcile. **But this only worked with a patch:** the repo's script is the copy patched locally on 2026-10-28, because the original failed on this pod's object order. This run did not re-test the unpatched original.")
rep("- Its generic REST route for lookups worked first time.",
    "- Its generic REST route and client for lookups worked first time, but it supplies no request-body fields. I built those from Oracle's describe and an existing lookup.")
rep("- By record: 10 of 24 records were created by FSCR alone and 14 needed my code (12 in the main run, plus the 2 price lists in the follow-up once BU data access was granted).",
    "- By record: 2 of 24 were FSCR end to end, and only on a locally patched script. 8 used FSCR's route and client with my request bodies. 14 needed my code (12 in the main run, plus the 2 price lists in follow-up 1 after you granted BU data access). Follow-up 2 approved the 2 price lists with my REST PATCH.")

# Section B
rep("| Payment terms | ERP | **As is** |",
    "| Payment terms | ERP | **With a patch** (local order-check patch of 2026-10-28; the original failed on this pod and was not re-tested) |")
rep("| Lookup types / codes / order types | SCM | **As is** (REST route) |",
    "| Lookup types / codes / order types | SCM | **Route only** (FSCR endpoint and client; you supply the body) |")
rep("| Price lists | SCM | **Not yet with FSCR** | Done in this run by my REST call, after Pricing Administrator data access was granted on the BU.",
    "| Price lists | SCM | **Not yet with FSCR** | Done in this run by my REST call, after Pricing Administrator data access was granted on the BU; approved by REST PATCH of StatusCode (FSCR has no route for it).")

# Tokens
rep("""| After modules 6–8 (01:23) | same | 448,119 | 48% | 24% |

The context figure is the running size of this session's context window, not a billed-token count. No per-request token or dollar figure was visible to me.""",
"""| After modules 6–8 (01:23) | same | 448,119 | 48% | 24% |
| Now, after follow-ups 1 and 2 (2026-11-03 ~07:05) | same | 166,294 | 6% (a new 5-hour window, resets 07:19 +05:00) | 25% |

- **Start reading:** the first reading (100,881) was taken at the start, before any run work. It is the session's baseline (system prompt, tools, your brief), not run work.
- **Main run:** context grew from 100,881 to 448,119, so **347,238 were added during the run**. That is context-window size, not billed tokens. The plan 5-hour window went from 13% to 48% (**+35 points**) and weekly from 18% to 24% (**+6 points**). Those are plan-window percentages, not billed tokens.
- **Follow-up work (price-list creates, approvals and this correction pass):** its own line. The session was automatically summarized after the main run, so the context dropped. The present 166,294 is the size of the summarized context plus the follow-ups, and cannot be subtracted from 448,119. *Not verified* as a follow-up-only amount. The 5-hour window shows 6% of a new window that started after the main run (plan-window percentage); weekly rose from 24% to 25% (**+1 point**). Both are *inferred* to be mostly this follow-up, because other use on the account in the same window would also count.
- None of these figures is a billed-token or dollar count; no per-request figure was visible to me.""")

# New section: pod changes outside the run's own records
rep("### Files", """### E. Changes on the pod outside the run's own records

| Change | Made by | When | Detail |
|---|---|---|---|
| FSCR Run Book "FSCRT Run01 OM Setup" (WorkerJourneyId 300000394648040) | **FSCR** (`core/runbook/runbook_rest.py create-runbook`, run by me in the main run) | 2026-11-03 00:51 +05:00 | An Oracle record that FSCR creates automatically after project initialization. The name uses "FSCRT " with a space because FSCR derives it from the project name. Oracle shows 2 of its 5 tasks completed. |
| Pricing Administrator data access for `Configuration.TEST` on FSCRT_Quillon Ridge Outfitters West F01 and FSCRT_Brindle Harbor Marine Supply F01 | **You** (not me) | 2026-11-03, before 06:40 +05:00 | Granted so the price lists could be created. I made no security change. Effect seen: the same POST that was rejected at 00:59–01:01 succeeded at 06:43. *Not verified* by a separate read of the grant. |

### Files""")

p.write_text(s, encoding="utf-8")
print("RUN_REPORT.md updated")
