# Run 14, Part 2: Project Intake from the Twelve SOW (FSCR + Claude)

- **Run folder:** `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_14_part2_intake`
- **Input:** No SOW file was attached to the chat. I used the only Twelve SOW found on disk: `C:\Users\PC\Downloads\50513 - Twelve - Oracle Cloud SCM Implementation SOW v4_Twelve-signed_GS signed.pdf`, copied to `input/` (MD5 77241006ca0165557315ca946f4b6c56). Its text matches the description: Twelve, Oracle Cloud SCM Implementation SOW, January 24, 2025. Verified by `work/sow_text.txt`, extracted with pdftotext.
- **Repo:** fresh copy of `fscr-main\fscr-main` → `fscr-main/` (6,120 files). `diff -rq` against the original printed no differences. The original and earlier run folders were not modified. Verified.
- **Paper only:** no Oracle pod, no sign-in, no OAuth, no Fusion/REST calls, no tokens. Verified: the only commands run were local file reads, copies, pdftotext, md5sum and two local Python scripts.
- **Timing (system clock):** start 2026-11-05T19:27:16+05:00 · freeze 19:35:24 · baseline read from 19:35 · report written about 19:38. Verified from `date` output.

## 1. Deliverables and who produced them

| Output | File | Produced by | Notes |
|---|---|---|---|
| 1 Scope | `01_SCOPE.md` | **FSCR + Claude** | FSCR provided the classifier rules, the effective offering/FA catalog (6 offerings resolved; 31 rows: 24 resolved, 7 pending fail-closed) and the workspace. Claude read the SOW and mapped it to catalog codes, and also wrote the document and the checklist structure. FSCR `implementation-scope-intake` and `scope-definition` are empty stubs. |
| 2 Enterprise structure | `02_ENTERPRISE_STRUCTURE.md` | **FSCR + Claude** | FSCR provided the BU design principles, required design evidence, design advisory and cost/inventory-org task names. Claude provided everything else: inventory, cost and item-master org suggestions come from general Oracle practice, because FSCR's SCM skills have no design guidance. FSCR `enterprise-structure-intake` is an empty stub. |
| 3 Integration landscape | `03_INTEGRATION_LANDSCAPE.md` | **Claude alone** | FSCR `integration-landscape-intake` and `shared/integrations/*` are empty stubs. 0 integrations created, per the SOW. |
| Supporting: scope classification | `fscr-main/project/twelve-scm-intake-20261105/artifacts/router/project-objective-classifier/current/scope.json` | FSCR catalog + Claude mapping script (`work/classify_scope.py`) | Offline application of the classifier's "Offering-Scope Resolution" rules |
| Supporting: workspace state | `…/state/project-state.json`, `state/runs/…json`, `objective.json`, token log | FSCR template + Claude | AGENTS.md project discipline. Run Book not applicable (no mutation). |
| Freeze record | `work/freeze_record.txt` | – | MD5 of the 3 outputs |

FSCR parts used (all verified as read): `AGENTS.md`; `router/implementation-router`; `router/project-objective-classifier`; `knowledge/setup-task-catalog/effective/*` (offering catalog, pillar mapping); `pillars/erp/financials/organization-structures/SKILL.md` and `ora-resource/ora_design_advisory.md`; `project/_template`; `knowledge/product-guidance/pillars/scm/*` (link lists only). Confirmed empty placeholders: all 6 `shared/project-intake/*` skills and `shared/integrations/integration-strategy-advisor` (each ~2–3 KB of generic boilerplate).

Team method: only `_fscr_run_10_drive_reference/downloads/01_checklists_capture.txt` was read before the freeze. It is PLM-oriented, so only its general questions applied (customer info, overview, integrations, environments, data migration, planning, test cycles, PM, pre-implementation access). It has no ledger, LE, BU or cost-org recommendations. Those suggestions are labelled "FSCR guidance" or "Claude" instead.

## 2. Freeze (verified, `work/freeze_record.txt`)
- Frozen at 2026-11-05T19:35:24+05:00. Files set read-only. No edits after the freeze.
- `01_SCOPE.md` d5b73e45ac83902f37d9d5ac7f480626
- `02_ENTERPRISE_STRUCTURE.md` 17abdb9166e44cca249bcb203e03b4f6
- `03_INTEGRATION_LANDSCAPE.md` 6b9f369862c76f257a72e456d520e719
- Before the freeze I opened none of: other `_fscr_run_10` files, `_fscr_run_11*`, `_fscr_run_12*`, `_fscr_run_13*`. Verified against my own command history in this session. The listing of the parent folder showed their names only.

## 3. Comparison with the manual baseline (after the freeze)
Source: `_fscr_run_13_twelve_manual_baseline/TWELVE_MANUAL_BASELINE.md` plus captures (condensed extracts, CR #01, CR #02 final, Enterprise Structures Best Start CRP1, Inventory Best Start CRP1, Instance Plan, Kick Off). All were read in this session; quoted facts are verified against those captures. My classifications are judgments.

Categories: **Covered** · **Partly** · **Missed** (findable from the SOW but absent) · **Contradicted** · **NF** = not findable from the SOW (real names, CRs and post-SOW decisions; not counted as misses).

### 3.1 Scope

| # | Manual item | Status | Note |
|---|---|---|---|
| 1 | PIM (3 sub-items) | Covered | S1 |
| 2 | Inventory & Cost (6) | Covered | S2 |
| 3 | Self-Service Procurement (5, Coupa values) | Covered | S3 |
| 4 | Purchasing (2) | Covered | S4 |
| 5 | Supplier Portal (5) | Covered | S5 |
| 6 | Manufacturing (4, process, ready to use) | Covered | S6 |
| 7 | Maintenance (7) | Covered | S7 |
| 8 | Financials remediation GL/AR/PJ/Grants/AP/CM/FA | Covered | F1–F9 |
| 9 | Sustainability new; Expenses subject to a design session | Covered | F4, F5 |
| 10 | Confirm BU structure (Req and Purchasing BUs) | Covered | F3 and Output 2 |
| 11 | Reporting approach OTBI/BIP/FDI/EPM | Covered | F6 |
| 12 | GL support | Covered | F7 |
| 13 | RICE: 1 report, 1 conversion, no integrations or extensions | Covered | §4 |
| 14 | Configuration scope, 12 areas | Covered | §5 |
| 15 | Change management, Train-the-Trainer | Covered | §5 |
| 16 | Exclusions | Covered | §3 (mine also lists supplier onboarding, PROD migration by Twelve) |
| 17 | Assumptions (11) | Covered | §1, §6, §7 |
| 18 | Costs | Covered | §6 (mine adds 3,820 total hours) |
| 19 | Kick-off module list | Covered | §2 |
| 20 | Kick-off phases PIT → Design → Build → CRP1&2/UAT/EUT → Deployment | Partly | Mine suggests CRP1/CRP2/UAT from the checklist; no PIT or EUT |
| 21 | Kick-off tentative KDD list | Partly | KDDs named as a deliverable; no list |
| 22 | CR #01: Expenses removed (Rippling Expense) | NF | I raised it as open Q-S1 |
| 23 | CR #01: Oracle Tax added | NF | Not raised |
| 24 | CR #01: Rippling → HR via OIC | NF | – |
| 25 | CR #01: Projects expanded (types, templates, budgets, assets to FA; SLA ownership) | NF | – |
| 26 | CR #02: go-live Aug 1 → Sep 1 2025, hypercare Sep–Oct | NF | Hypercare raised as Q-P8; 12-week risk flagged |
| 27 | CR #02: AirPlant One BU financials, LEs 001/003 | NF | – |
| 28 | CR #02: Coupa supplier onboarding, open-PO and on-hand conversions, bank wire | NF | Coupa retirement raised as Q-S6/Q-I1 |
| 29 | Updated Plan future items (Stacks/Alameda, CTO, EPM, JV) | NF | – |
| 30 | Pre-SOW proposal: 5-phase plan, sites, Plex | NF | – |

**Scope counts: Covered 19 · Partly 2 · Missed 0 · Contradicted 0 · NF 9 (total 30).**
Mine only (not in the manual scope): FSCR offering and FA codes with ambiguity diagnostics; the SOW's internal inconsistency (Configurations Scope omits AR/CE/FA/Grants); the checklist-based planning table; 17 open questions. Several of mine later proved relevant in other manual documents:
- 12-week timeline risk: the manual schedules went 12 → 15/16 weeks → Sep 1 go-live.
- 3 environments: the Instance Plan has Production, Test and Development (Dev 2).
- Hypercare question: CR #02 added hypercare.
- Expenses question: CR #01 removed Expenses.
- Coupa retirement question: the Cutover Plan has "Freeze Coupa".

### 3.2 Enterprise structure

| # | Manual item | Status | Note |
|---|---|---|---|
| 1 | Ledger Twelve US (USD, COA/calendar "Twelve") | NF | My SUGGESTED "reuse existing US primary ledger, USD" is consistent |
| 2 | Ledger Twelve NL (EUR) | NF | Outside the US project scope; my single-ledger suggestion was scoped to the project |
| 3 | LE Twelve Benefit Corporation (001) | Partly | The name appears in mine as the enterprise/contracting party, not proposed as the LE |
| 4 | LE Twelve Rainier, LLC (003) | NF | – |
| 5 | LE Opus B.V. (002, NL) | NF | – |
| 6 | COA 8 segments | NF | COA impact raised as Q-E3 |
| 7 | Existing BU (Twelve Operations) | Covered | As a placeholder `<EXISTING FINANCE BU>`; name NF |
| 8 | Requisitioning, Procurement and Receiving functions on that same BU (no separate procurement BU) | Covered | Matches my Option A, which FSCR guidance recommended |
| 9 | Default reference set COMMON | Partly | Suggested "existing BU's default set"; name NF |
| 10 | BU AirPlant 1 / AirPlantOne (Rainier LE) | NF | Added via CRP1/CR #02 |
| 11 | Inventory orgs ALA1, BRK1, AirP1, BLE1, AirP2 (+ BLE2 in capture) | **Contradicted** | I stated 2 inventory orgs, one per plant, taken from SOW B 2.2 and C.7. The manual has 5–6. I did not ask whether a plant can hold several inventory orgs. Names NF. |
| 12 | Item master org "Twelve" | Covered | Suggested separate item master org |
| 13 | Inventory orgs under the existing BU and LE | Covered | Suggestion matched (except the later AirPlant org) |
| 14 | Manufacturing-plant flag per org (Alameda Y, Berkeley N, AirPlant One Y) | NF | Raised as Q-E7 |
| 15 | 2 cost orgs (Stacks, Fuels) | **Contradicted** | My suggestion was 1 cost org |
| 16 | 2 cost books (Stacks CB, Fuel CB) | **Contradicted** | My suggestion was 1 primary cost book |
| 17 | Perpetual Average cost profile | Partly | Cost method asked (Q-E8), no answer suggested |
| 18 | AirPlant One asset/expense C-I-P valuation | Partly | Expense vs capitalize asked (Q-E8) |
| 19 | Intercompany orgs | NF | – |
| 20 | Cost orgs under LE Twelve Benefit Corp on the US ledger | Covered | Suggested single LE/ledger |

**Enterprise structure counts: Covered 5 · Partly 4 · Missed 0 · Contradicted 3 · NF 8 (total 20).**
All 3 contradictions are against SUGGESTED or SOW-derived counts, not against stated facts. They show that "2 plants" in the SOW did not mean 2 inventory orgs or 1 cost org.
Mine only: FSCR "Required Design Evidence" per BU; Option B shared-service procurement BU; employee-assignment BU; data access by org; asset books; approval-hierarchy basis; project and grants orgs; future-site sizing; FSCR task names.

### 3.3 Integration landscape

| # | Manual item | Status | Note |
|---|---|---|---|
| 1 | SOW: no integrations or extensions | Covered | – |
| 2 | MES integration excluded | Covered | – |
| 3 | RICE limited to PO report and supplier conversion | Covered | – |
| 4 | Coupa named (pre-SOW system) | Covered | Configuration reference only |
| 5 | CR #01 Rippling → Oracle HCM via OIC (inbound) | NF | My "OIC not needed for this SOW" (Q-I3) was true at SOW time and was superseded by CR #01 |
| 6 | Rippling deck details (system of truth, OIC flow, service accounts, agent) | NF | – |
| 7 | CR #02 international bank wire remediation | NF | Q-I2 asked about existing bank/payroll integrations |
| 8 | CR #02 Coupa open-PO and on-hand conversions; Coupa frozen at cutover | NF | Q-I1 asked about Coupa retirement |
| 9 | Cutover: HRIS/OIC the only integration; No-Go trigger | NF | – |
| 10 | Pre-SOW systems Plex, Kiwi, Aveva PI, PLC | NF | – |
| 11 | B2B XML invoices (NV in the manual) | NF | Not verified in the manual either |

**Integration counts: Covered 4 · Partly 0 · Missed 0 · Contradicted 0 · NF 7 (total 11).**
Mine only: EPM/FDI and Sustainability-upload context; native in-pod flows; checklist integration questions; environment suggestion (consistent with the Instance Plan).

### 3.4 Totals
| Output | Covered | Partly | Missed | Contradicted | NF |
|---|---|---|---|---|---|
| Scope | 19 | 2 | 0 | 0 | 9 |
| Enterprise structure | 5 | 4 | 0 | 3 | 8 |
| Integration landscape | 4 | 0 | 0 | 0 | 7 |
| **All** | **28** | **6** | **0** | **3** | **24** |

## 4. Findings
1. Everything the manual versions took from the SOW was captured. The gap is entirely post-SOW knowledge (CRs, Best Starts, real names), which no SOW-only process can produce.
2. The enterprise structure is the weak spot. The suggestions for cost orgs, cost books and inventory-org count were wrong, and they came from Claude because FSCR has no SCM design guidance. The FSCR BU guidance gave the right answer (one BU with requisitioning, procurement and receiving).
3. FSCR's classifier fails closed on shared functional areas (Enterprise Structure, Payables, Cash, Sustainability, Security). That is correct behaviour, but it means 7 of 31 rows need a person to decide.
4. The GoSaaS checklist is PLM-oriented. It helped with planning questions (environments, test cycles, freeze periods) but gave nothing for ledgers, LEs, BUs or cost orgs.

## 5. Metrics
- **Time taken:** about 11 minutes by system clock (19:27:16 → about 19:38), so far as recorded. Final end time is in the chat summary.
- **Tool calls:** 47 up to and including this report write. Final count is in the chat summary.
- **Output tokens:** not recorded. The agent has no access to exact output-token accounting. Session context at about 19:37 was 194,655 tokens (from the app's usage tool); that is context size, not output tokens.
- **Processes/servers started:** none left running. One background shell copy (`cp -r` + `pip list`) was moved to the background by the tool timeout and stopped with TaskStop after the copy completed (copy verified by diff). No servers were started.
