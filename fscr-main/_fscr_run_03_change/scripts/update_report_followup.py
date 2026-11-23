"""One-off: apply the C1/C4 follow-up results to RUN_REPORT.md (exact anchors; fails if one is missing)."""
from pathlib import Path

p = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_03_change\RUN_REPORT.md")
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert s.count(a) == 1, ("anchor", a[:80])
    s = s.replace(a, b)


rep("Pod ETIA-TEST (release 11.13.26.10.0). Start 2026-11-03 07:49:05 +05:00 · finish 2026-11-03 08:05:43 +05:00 · total 17 min.",
    "Pod ETIA-TEST (release 11.13.26.10.0). Main run 2026-11-03 07:49:05–08:05:43 +05:00 (17 min). Follow-up for C1/C4 after your Task Hook permission: 08:24–08:31 (7 min). **Total 24 min.**")

# Part 1
rep("**What FSCR has a real route for, but that didn't finish here:** payment terms (C1, ERP) and the business unit (C4, ERP).",
    "**Payment terms (C1, ERP): changed end to end through FSCR, after you allowed the Task Hook step.**\n"
    "- FSCR's script really supports `end-date`, despite the manifest marker listing only \"create, update\".\n"
    "- It produced a correct, minimal candidate: only EndDateActive changes, 86 fields preserved, no rows touched.\n"
    "- The route ran: preview → design confirmation → build/validate → Data Loader preflight → Task Hook (rule plan, my evaluated rule results, preview → approve → verify) → approved upload → import (request 4432070: 3 objects, 0 failed) → fresh export → FSCR `reconcile` verified, 0 mismatches.\n"
    "- Whole-area diff: only that end date changed.\n\n"
    "**Business unit (C4, ERP): blocked by FSCR's own rule, not by me.**\n"
    "- The BU rule registry has **no update path**. Its idempotency node sends an existing BU that differs from the request to BLOCKED (\"require an explicit update decision or a different BU name\"). The only success outcome is a *new* BU.\n"
    "- The Task Hook refused: \"Preview is blocked until user corrections are supplied and all rules pass: ora_input_validation.md.\"\n"
    "- FSCR allows this only with an explicit user waiver of that validation, which you have not given. Nothing reached Oracle.\n\n"
    "**History of the Task Hook gate:** in the main run, the session's permission system blocked my writing of the Task Hook rule results (\"Security Weaken\") before anything reached Oracle. You then allowed it, add-only, in Run 01's project folder (see section 6).\n\n"
    "**Detail from the main run, kept for the record:**")
rep("**Result: 4 of 6 changes made and verified (C2, C3, C5, C6); 2 not done (C1, C4). No change outside the named records** (verified by whole-area before/after diffs).",
    "**Result: 5 of 6 changes made and verified (C1, C2, C3, C5, C6). C4 not done (FSCR rule: no BU update path). No change outside the named records** (verified by whole-area before/after diffs, after the main run and again at the end).")

# Scorecard
rep("| C1 | FSCRT_D25B75AF1 end date 2028-12-31 | ERP | Yes: PT skill end-date → preview/build/validate → Data Loader preflight | – | **Not done**: stopped at Task Hook (permission denied) | none (nothing imported) | exports 100004733446385, 100004733440767 |",
    "| C1 | FSCRT_D25B75AF1 end date 2028-12-31 | ERP | **Yes, end to end**: PT skill end-date → preview/build/validate → Data Loader → Task Hook → upload → reconcile | rule results written by me (Task Hook design) | **Changed and verified** (follow-up) | none (16 other terms identical; Run Book unchanged) | request 4432070, ESS 4432071, FSM 100004733447103; export 100004734412650 |")
rep("| C4 | Brindle BU manager → Smith, Aron | ERP | Partly: rules yes, builder no; preflight passed | `build_bu_update.py` | **Not done**: same Task Hook stop | none | exports 100004734412594, 100004734402958 |",
    "| C4 | Brindle BU manager → Smith, Aron | ERP | **No update path**: registry BU.IDEMPOTENCY existing-different → BLOCKED; builder mine | `build_bu_update.py` | **Not done**: Task Hook refused preview (FSCR rule) | none (nothing sent) | exports 100004734412594, 100004734402958 |")

# Details
rep("- **Stop:** Task Hook rule results (permission denied).\n- **After:** export 100004733440780 is identical to before.\n- **Status:** not done.",
    "- **Main run:** stopped at the Task Hook rule results (permission denied); export 100004733440780 identical to before.\n"
    "- **Follow-up:**\n"
    "  - Ran in Run 01's project; Task Hook `data-load` gave the rule plan; I evaluated all 6 rule files (all passed, with node evidence).\n"
    "  - Preview → approve → verify, then approved upload: request 4432070, status Succeeded, 3 objects, 0 failed. FSM log: \"A total of 1 rows were processed. 0 rows of them failed\".\n"
    "  - Fresh export 100004734412650: only EndDateActive '' → 2028/12/31. FSCR reconcile: verified, 0 mismatches.\n"
    "- **Status:** changed and verified.")
rep("- **Not verified:** whether Fusion's BU CSV import would replace the manager or add a second one.",
    "- **Not verified:** whether Fusion's BU CSV import would replace the manager or add a second one.\n"
    "- **Follow-up:** the rule evaluation gives BU.IDEMPOTENCY = existing-different → BU.BLOCKED. Recorded as `blocked`, not overridden; no user waiver was given. The Task Hook refused the preview. Not done; the manager is unchanged in the final snapshot.")

# Section 3
rep("- `core/data-loader` (`upload_and_initiate.py` preflight)",
    "- `core/data-loader` (`upload_and_initiate.py` preflight, approved upload with `--run-config`; `get_data_load_info.py`)\n"
    "- `core/data-loader/task-hook` (`task_hook.py data-load`, `build-data-load-preview`, `approve-data-load-preview`, `verify-approved-data-load-archive`)")
rep("- BU package builder.", "- BU package builder.\n- A BU **update** path in the rule registry (create-only).")

# Section 5
rep("| After lookups export |",
    "| Follow-up reconcile | \"A readable ZIP file is required: …$(basename …)\" | My shell quoting; re-run once: verified |\n"
    "| Follow-up C4 Task Hook | \"Preview is blocked until user corrections are supplied and all rules pass: ora_input_validation.md.\" | FSCR rule (no BU update path); stopped |\n"
    "| After lookups export |")

# Section 6
rep("| **Permission classifier** | Session control | Denied writing Task Hook `rule-results.json`. Stop recorded |",
    "| **G-TH Task Hook rule results** | FSCR Task Hook: `data-load` returns `ready` with \"checks have not yet run\"; the caller must execute the rule plan and supply `ruleResults` before preview | **Main run:** the session's permission classifier denied the write (\"Security Weaken\"); **the gate stopped before anything reached Oracle**. **Follow-up:** you allowed add-only files in `_fscr_run_01/fscr-work/project/fscrt-run01-om-setup`. C1: 6 rule files evaluated, all passed. C4: `blocked` |\n"
    "| Task Hook approve-data-load-preview | FSCR (\"Only after explicit user approval\") | C1: your C1 approval |\n"
    "| Data Loader standalone approval (C1) | \"Reply with an approval to upload and initiate this exact validated load.\" | Your C1 approval: approved upload (request 4432070) |")

# Section 7
rep("- Writes: 5 REST PATCHes through FSCR's client (C2, C3), 1 own REST PATCH (C5), 2 own SOAP updates (C6).",
    "- Writes: 5 REST PATCHes through FSCR's client (C2, C3), 1 own REST PATCH (C5), 2 own SOAP updates (C6), and **1 FSCR Data Loader import (C1)**: UCMFA04524480, request 4432070, ESS 4432071, FSM 100004733447103.\n"
    "- Follow-up export: 100004734412650 (PT after C1).")
rep("| End 08:04 | app `get_usage` | 514,007 | 27% | 31% |",
    "| End of main run 08:04 | app `get_usage` | 514,007 | 27% | 31% |\n| End of follow-up 08:30 | app `get_usage` | 579,051 | 37% | 33% |")
rep("- Context added during this test: **109,750**.",
    "- Context added: **109,750** in the main run plus **65,044** in the follow-up (174,794 in total).")

# Section 8
rep("8. **Task Hook:** depends on the agent writing its own rule-pass attestations (`rule-results.json`). FSCR does not compute them itself.",
    "8. **Task Hook:** depends on the agent writing its own rule-pass attestations (`rule-results.json`); FSCR does not compute them itself. Run 01 skipped the `data-load` plan step that the Task Hook skill requires. The follow-up ran it.\n"
    "9. **BU skill:** the text and intake mention \"Create or update intent\", but the executable rule registry only reaches READY for a **new** BU. An update is BLOCKED unless the user waives the validation. This contradiction is not called out in the skill.\n"
    "10. **Data Loader:** deletes its single-use preflight and Task Hook envelopes after upload, and writes status logs to `C:\\Users\\PC\\.codex\\data-loader-status-logs\\` outside the repo. Neither is stated where the files are requested.")

# Section 9
rep("| **Change** | Payment terms, BU (ERP) | yes | FSCR route builds correct minimal candidates; stopped before Oracle at the Task Hook (agent self-attestation blocked) | `evidence/C1`, `C4` | not imported |",
    "| **Change** | Payment terms (ERP) | yes | **Works end to end** once the Task Hook rule results may be written: minimal end-date import, 0 failed, reconcile verified | `evidence/C1`, `evidence/gate` | Task Hook relies on agent-written rule results |\n"
    "| **Change** | Business unit (ERP) | yes | **No update path** in FSCR's BU rule registry; Task Hook refused | `evidence/gate/c4_preview.json` | create-only unless the user waives |")
rep("| **Verify** | All areas | yes | FSCR export diff + FSCR compare (PT, 0 mismatches) + FSCR customer reader; whole-area diffs mine |",
    "| **Verify** | All areas | yes | FSCR export diff + FSCR compare (PT, 0 mismatches) + FSCR `reconcile` after C1 (verified) + FSCR customer reader; whole-area diffs mine |")
rep("| Breadth | 6 areas | yes | 2 of 6 changed fully via FSCR; 2 FSCR-ready but blocked; 2 none | this report | one pod |",
    "| Breadth | 6 areas | yes | 3 of 6 changed through FSCR routes (C1, C2, C3); 1 blocked by FSCR rule (C4); 2 none (C5, C6) | this report | one pod |")

# Section 10
rep("- **FSCR did the hard part but never reached Oracle:** C1 and C4. The payment-term script's update/end-date handling is genuinely good: minimal, baseline-preserving and self-validating. Both stopped at the Task Hook, which requires the agent to attest rule results.",
    "- **C1 changed through FSCR end to end** (follow-up): the payment-term route is FSCR's strongest. It is minimal, preserves the baseline, validates itself and reconciles after import. My part was the request, the rule evaluation the Task Hook requires the agent to write, and a run-config with blank runID to keep the Run Book unchanged.\n"
    "- **C4 is not possible through FSCR as written:** the BU rule registry is create-only. FSCR stops an update unless the user explicitly waives the validation.")
rep("- Verified by before/after diffs: 17 payment terms, 183 BUs, 6 lookup types and 68 codes, 60 order types, 55 price lists, 4 FSCRT accounts, 212 site rows, and the FSCRT parties.",
    "- Verified by before/after diffs: 17 payment terms, 183 BUs, 6 lookup types and 68 codes, 60 order types, 55 price lists, 4 FSCRT accounts, 212 site rows, and the FSCRT parties. Re-checked after the follow-up (final snapshot at 08:29 and PT export diff).")
rep("- The only new Oracle records are the 8 export processes and the compare's blobs, uploads and process.",
    "- The new Oracle records are the 9 export processes, the compare's blobs, uploads and process, and the C1 import (request 4432070).\n"
    "- **Run 01 files:** only the 10 new files listed in the ledger were added; every pre-existing Run 01 file is hash-identical.")

p.write_text(s, encoding="utf-8")
print("report updated")
