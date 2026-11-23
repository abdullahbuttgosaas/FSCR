# DRIVE_REFERENCE — run 10: human-made reference examples for scoring FSCR

Source: Google Drive > Projects > **Customers** (folder id `1Sd3STSIV8Uuvsct8NBZ3GA6_TKo5wrLg`), read on 2026-11-05 in the Claude desktop built-in browser after you signed in. Every access was read-only. Nothing in Drive was created, edited, moved, renamed, shared, commented on or deleted, and no sharing setting was changed.

Tags: **[V]** = verified (I read it directly). **[NV]** = not verified (inferred, partly read, or listing only).

**About the "downloads":** the built-in browser throws away file downloads, so I could not save original .xlsx/.docx/.pdf files. The files in `downloads/` are text captures I made from the Google Sheets HTML view, the Google Docs text export, or the Drive PDF viewer text. They hold cell values and fill colours, but not Excel drawing shapes. I looked at the shapes in Drive's preview for three instance plans (§5). **[V]**

Customer masking in file names: C1 = large PLM customer (Tektronix PLM), C2 = SCM expansion customer (Twelve), C3 = small PLM customer (AMVAC). Original names are kept inside the files and in this report.

---

## 1. Folder map

### 1.1 Top level of "Customers" **[V]**
There are 104 customer/project folders and 4 loose files: `.DS_Store 2`, `Exam topics`, `TEMPLATE WWX ... Weekly Status` (Sheet) and `Untitled spreadsheet`. Plus the reference folder `000 Reference Project Setup`. The full list is in the table in §2.

### 1.2 "000 Reference Project Setup", two levels deep **[V]**
The phase folders are numbered 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15 and 20. There are no folders numbered 12, 13 or 14 at this level. The 20 folder holds its own 01–15 workstream tree.

| Folder | Contents (level 2; level-3 counts in brackets) |
|---|---|
| 0 Pre Implementation Checklist | 01. Checklists/ (01. Scoping Checklist, 02. GoSaaS Project Implementation Methodology, 03. PM Check List, Archive [Pre-Implementation Checklist, Pre-Sales Checklist]); 02. Templates/ (empty) |
| 1 Kickoff | Instance Plan 2022/2023/2024/2025.xlsx; Default Kick Off (slides); 2025 GoSaaS Template Theme; Default RACI; Deliverable RACI; Deliverable Workstream RACI; Default Team List ×2; Key Pain Points Log; Oracle_Cloud_Environment_Usage_Assessment_v5_rev2 (2).xlsx; Resource Plan - Internal Use; Risk Register (Sheet + .xlsx); Session Schedule Template.xlsx; ARCHIVE/ (empty) |
| 2 Training and Workshops | Default Standard Training and Workshop Sessions (Including Labs / Redwood / Inventory / HCM / Food & Beverages); Procurement Pre Implementation Slides; GoSaaS Dataload Process; Innovation Management 25B; Quality Management Cloud 25D; PD and PIM Training Decks/ (3) |
| 3 Configuration | BasicSetup.xlsx; Configuration Issue Tracker.xlsx; Solution Design Document - PLM.docx; Standard Configurations for all Customers; Best Start Templates/ (HCM, IM, PD, PIM, PPM, Products, Quality, Reports, Security, Supplier Portal); Configuration Packages Extracted from ETIA/ (3); Process Documents (Samples)/ (3); Security Migrator/ (3) |
| 4 Data Migration Documents | Data Conversion Strategy, Data Load Flowcharts, Data Migration Overview, DM Issue Tracker, FRD, Final DM Documents.zip; ETS / GIM / PD DM Strategy Documents/; Extract Formats/; FBDI Template Documentation/; Innovation Management/; PIM/ |
| 5 CRP | CRP1/ (EG&C CRP Scripts, EG&C Manager Training); CRP2/ (empty) |
| 6 UAT | Training Materials/ (empty) |
| 7 Test Documents | Scripts/ (CAD Integration, EG&C, ERP Integration, ETS, GIM, IM, PD, PIM, PPM, Quality, Supplier Portal); Test Result Scoreboard/ (4 scorecards) |
| 8 Integration Documents | Architecture/ (ECAD, ERP, FDA, GSI, MCAD); Functional Specifications/ (12: Altium, ERP, ERP(GP), OrCAD, NetSuite, Badging, EBS, EG&C, ETS, Solidworks ×2, Rootstock); Integration Approach/ (ECAD, ERP, FDA, MCAD, PlatformRequirementsChecklist.docx); Integration Mapping Files/; Overview and Workshops/; Security/; Integration Access Pre-Requisites; Integration Questionnaires E-CAD/M-CAD; Integration Team Resources; Functional Specification - PLM Portal.docx |
| 9 Go Live | Cutover Plans/ (Cutover A/B/C.xlsx); Readiness Checklist/ (Go Live Readiness Review PLM.docx, Go Live Readiness Review.docx); Hypercare Document.docx |
| 10 Project Management | Cutover Plan; Project Risk Register; Project Status Update Sheet; PMO Renesas.xlsx; Oracle Cloud Product Ideas.xlsx; Project Plans/ (Project Plan, Copy of Project Plan); Status Reports/ (2 .pptx); Tasks/ (SubFolder, My Tasks, MyTasks, Resource Pool); Templates/ (Project Plan Template, Project Template Blank.mpp, Project Template Standard.docx) |
| 11 Post Go Live Support | GoSaaS Support Helpdesk User Guide.pdf |
| 15 Post Go Live Reports | Complete/ (empty); Oracle Sales/ (2) |
| 20. Reference Large Project Setup - Proposed JCM | 01. Business Engagement - SOWs/ (Links To SOW Documents, Links To Budget Tracker, Pre-Implementation Documents, RACI Of Deliverables); 02. Program and Project Management/ (Program Level, Design, Develop, UAT and Go Live, Post Go Live Support, Orientation & Workshop Recordings, Workstream Recordings, Project Governance Deliverables, Future Project Planning, Archive); 03. OCM and Training/ (3); 04. E2E and Customer Process Documents/ (2); 05. Project Phases Reference Documents/ (Global Design, Detail Design, Development, Test, PGLS and Hypercare); 06. Functional and Configuration/; 07. Automations/; 08. Integrations/; 09. Data Migrations/; 10. Infrastructure/ (each: Deliverables Approved – Project Phases, Deliverables – Active Files, Workstream Working Folders); 11. BI and Reporting/; 13. Extension Applications/; 14. Data Quality/; 15. Post Go Live – HyperCare/ (all four empty); 12. Test/ (Reference & Background, Training & OCM, CRP1, CRP2, GLT – Go Live Testing, UAT) |
| Loose files | 2024 GoSaaS Template Theme; Business Requirements Document (Doc + .docx); Oracle Cloud Implementation Process (+ Copy); GoSaaS Presentation Template ×2; NMT Playbook |

"Reference Large Project Setup - Proposed JCM": I mapped the full folder structure to three levels. All its level-3 workstream folders are empty except the ones listed above. It is a folder taxonomy, not a filled plan. **[V for structure; NV for anything below level 3]** A real customer that adopted this taxonomy is **pSemi**: its folder has `01. Business Engagement - SOWs/…` and `02. Program and Project Management/…`. **[V]**

---

## 2. Customer folders (step 2)

How this table was made: I listed each folder three levels deep and matched file and folder names. Any folder level with 50 or more entries was cut to its first 50 entries (marked "+"). Y means a matching name exists, not that I read the file. Dates are last-modified per Drive. **[V for names and dates; NV for whether each file really is that document type]**

Legend: SOW · PP = project plan (sheet or .mpp) · IP = instance plan · CRP = CRP scripts/folders · INT = integration documents · CHK = readiness or pre-implementation checklist.

| Folder | Modified | Entries | SOW | PP | IP | CRP | INT | CHK |
|---|---|---|---|---|---|---|---|---|
| Accenture | 2024-12-09 | 1 | | | | | Y | |
| Aerovironment - Automus | 2024-07-18 | 347 | Y | Y (.mpp) | | Y | Y | |
| Alcatel Lucent/ ALE | 2024-03-01 | 7 | | Y | | | | |
| Alter G | 2024-12-17 | 2 | | | | | | |
| AMDI | 2024-01-24 | 143 | Y | Y | | Y | Y | Y |
| Ampere Computing | 2025-02-03 | 580+ | Y | Y | Y | Y | Y | Y |
| AMVAC - PLM | 2022-06-13 | 56 | Y | Y | | Y | Y | Y |
| Ancestry | 2023-03-20 | 193 | | Y | Y | Y | Y | |
| Applied Optoelectronics | 2026-08-24 | 500+ | Y | Y | | Y | Y | |
| Archived (many old customers) | 2022-02-09 | 544 | Y | Y | Y | Y | Y | Y |
| Arconic | 2022-06-07 | 0 | | | | | | |
| Argano HCM Projects | 2026-10-23 | 47 | | | | | | |
| ATEC (Alphatec) | 2026-04-16 | 342+ | | | Y | Y | Y | |
| ATEC Spine (Old) | 2026-09-24 | 21 | | | | Y | Y | |
| Ballard Power | 2024-12-07 | 95 | | Y | | | Y | |
| Boxabl | 2026-08-24 | 266 | Y | Y | Y | Y | Y | Y |
| Brooks Automation - Silicon Expert | 2026-08-23 | 202 | Y | Y | | Y | Y | Y |
| BSN - Bank Simpanan Nasional | 2026-04-01 | 12 | | | | | | |
| Charter Next Generation | 2026-08-23 | 139 | | Y | | Y | Y | Y |
| Christie Digital | 2024-07-18 | 438+ | Y | Y | Y (10 versions) | Y | Y | Y |
| Ciena | 2026-01-06 | 231+ | Y | Y | | Y | Y | Y |
| Cirtec | 2022-10-05 | 745 | Y | Y | Y | Y | Y | Y |
| Cisco | 2021-09-21 | 4 | | | | | | |
| Claude Integration Projects | 2026-09-23 | 11 | | | | | | |
| Coast Cutlery | 2025-01-08 | 94 | Y | Y | | Y | Y | Y |
| Cohu | 2026-08-24 | 353+ | Y | Y | | Y | Y | |
| Cohu Demand Planning | 2025-09-23 | 12 | | | | Y | Y | Y |
| Cohu Production Scheduling | 2025-09-23 | 97 | | | | | | |
| Cohu Supply Planning | 2025-09-23 | 12 | | | | Y | Y | Y |
| Curtiss Wright | 2020-09-23 | 36 | | | | | Y | |
| Dexcom | 2026-01-08 | 28 | | Y | | Y | | Y |
| doTERRA | 2025-05-28 | 395 | | | | Y | Y | Y |
| Energy Recovery | 2022-10-09 | 36 | Y | Y | | Y | Y | |
| FB | 2024-12-17 | 5 | | | | Y | | |
| Fluke | 2026-08-23 | 765+ | Y | Y | Y | Y | Y | Y |
| Glaukos | 2026-08-23 | 535+ | Y | Y | Y | Y | Y | Y |
| Gorilla Glue | 2022-05-23 | 37 | | | | | Y | |
| HIID | 2024-12-17 | 2 | | | | | | |
| HME | 2023-10-20 | 8 | | | | | Y | |
| Ice-o-Matic | 2024-12-17 | 2 | | | | | | |
| Insmed Supplier Portal | 2025-12-02 | 0 | | | | | | |
| Intel | 2026-08-23 | 27 | | | | | Y | |
| Intelsat | 2025-06-13 | 3 | | | | | | |
| Intuitive Surgical | 2026-06-03 | 29 | Y | Y | | Y | Y | |
| Kaneka | 2026-08-24 | 39 | Y | | Y (template copy) | | Y | |
| Kodak Alaris | 2024-04-03 | 7 | Y | Y | | | | |
| Krusteaz | 2025-04-17 | 218 | | Y | | Y | Y | Y |
| Logitech | 2023-01-09 | 372 | | | | Y | Y | |
| MacLean Power Systems | 2026-08-23 | 75 | Y | Y | | Y | Y | |
| MACOM | 2026-01-16 | 19 | | | | | | |
| Micross | 2024-03-06 | 314 | Y | Y | | Y | Y | Y |
| Motorola | 2023-10-20 | 68 | Y | Y | | Y | Y | |
| Nissha | 2025-09-01 | 507 | Y | Y | Y | Y | Y | Y |
| Nissha Support | 2026-08-24 | 75 | | Y | | | | |
| NJOY | 2022-08-31 | 36 | Y | | | Y | Y | |
| NKR Continental | 2026-08-24 | 1 | | | | | | |
| Non-Agile Data Files Format | 2022-09-06 | 18 | | | | | | |
| NuSil | 2026-08-24 | 180 | Y | Y | | Y | Y | Y |
| Olympus | 2022-04-29 | 5 | Y | | | | | |
| Omron | 2026-06-03 | 125 | | | Y | Y | Y | Y |
| Otter Products | 2024-01-04 | 47 | Y | | | | Y | Y |
| Panasonic / PCTEL / Philips / QED / Rapid Micro / Project GoStarts | 2021–2024 | 1–5 | | | | | | |
| PowerFleet | 2023-02-14 | 210 | Y | Y | | Y | Y | Y |
| pSemi | 2025-08-15 | 244 | Y | Y | | Y | Y | Y |
| Pure Storage | 2023-02-15 | 38 | Y | Y | | | Y | |
| Ramssol - Ascend | 2026-08-24 | 142 | | Y | | Y | Y | Y |
| Ramssol - KKU | 2026-08-24 | 299 | Y | Y | | | Y | Y |
| Ramssol - UEM Sunrise | 2026-08-24 | 9 | | | | | | |
| Renesas | 2026-08-24 | 571+ | Y | Y | Y | Y | Y | Y |
| Roche | 2024-05-07 | 270 | Y | Y | | Y | Y | Y |
| Roll and Hill | 2023-01-11 | 46 | | | | Y | Y | Y |
| Royal Brunei / Spinnaker / Thermofisher / UEM Edgenta | various | 0 | | | | | | |
| Sally Beauty | 2022-07-13 | 372+ | Y | Y | Y | Y | Y | |
| Samba Nova | 2025-01-08 | 74 | Y | | Y | Y | Y | |
| SambaNova Coupa Integrations | 2024-04-04 | 1 | | | | | Y | |
| Sensata | 2022-12-15 | 69 | Y | | | | | |
| SharkNinja (Oracle ERP/SCM: SWAT, Mexico rollout, AMS) | 2026-10-28 | 275 | Y (5) | | | Y | Y | Y |
| Shockwave | 2023-03-01 | 177 | Y | Y (.mpp ×15) | Y | Y | Y | Y |
| SiTime | 2026-09-15 | 85 | | | Y | Y | Y | |
| SLD Laser | 2024-08-16 | 4 | | | | | | |
| StarLine - LeGrand | 2026-01-12 | 136 | | Y | | Y | Y | Y |
| Tandem Diabetes Care | 2026-02-27 | 408 | Y | Y | Y | Y | Y | Y |
| TDK Lambda | 2025-01-08 | 141+ | Y | Y | | Y | Y | Y |
| Tektronix - Archiver/ETS | 2024-01-24 | 75 | | Y | | Y | Y | Y |
| Tektronix - PLM | 2026-08-24 | 680+ | Y | Y | Y (8) | Y | Y | |
| Thermacell | 2024-12-20 | 333 | | Y | | Y | | Y |
| Trellix | 2026-10-24 | 24 | | | Y | | Y | Y |
| Twelve Projects (Cloud PLM 2023, Cloud SCM Expansion 2024, Cloud EPM 2024) | 2026-08-24 | 156 | Y | Y | Y | Y | Y | Y |
| UNICOM | 2024-03-06 | 254 | Y | Y | Y | Y | Y | Y |
| Unigen | 2024-09-13 | 6 | | Y | | | Y | |
| Vault Pressure Control | 2025-01-08 | 249 | Y | Y (.mpp) | | Y | Y | Y |
| Wabtec | 2022-07-05 | 58 | | Y | | | | |
| WestRock Coffee | 2026-08-24 | 275 | Y | Y | Y | Y | | Y |
| Yayasan Pahang | 2023-11-27 | 34 | Y | | | | Y | |
| Zebra - EG&C | 2022-03-04 | 108 | Y | Y (Sheet + .mpp ×30) | | Y | Y | Y |

Per-customer counts and the full matched file list (with Drive ids) are in `notes/customer_folder_scan.txt`. **[V]**

Observation: most folders are Oracle **PLM Cloud** projects. The ones with SCM / Order Management scope are Twelve (Cloud SCM Expansion 2024), Cohu (Redwood SCM/FIN/PLM/CX, Demand/Supply Planning, Production Scheduling), SharkNinja (ERP enhancement, Mexico rollout), Aerovironment-Automus (Phase 2 Fusion Supply Chain SOW), Pure Storage (Inventory Org / Site Management SOW) and Yayasan Pahang (ERP). **[V for names; NV for depth of scope]**

---

## 3. Files read in full (step 3)

| Item | Status |
|---|---|
| 0 Pre Implementation Checklist: Scoping CheckList, GoSaaS Project Implementation Methodology, PM check list.xlsx, Archive/Pre-Implementation Checklist, Archive/Pre-Sales Checklist | Read in full **[V]** → `downloads/01_checklists_capture.txt` |
| 1 Kickoff sheets (RACI ×3, Team List ×2, Pain Points, Resource Plan, Risk Register, Session Schedule, Env Usage Assessment, Instance Plans 2022–2025) | Read **[V]**. Personal contact data not copied. Slide decks not opened **[NV]**. → `notes/kickoff_and_pm_folder_notes.txt` |
| 10 Project Management sheets (Cutover Plan, Project Risk Register, Project Status Update Sheet, PMO Renesas.xlsx, Project Plans/Project Plan + Copy) | Read **[V]**. Templates/.mpp, .docx, Status .pptx, Tasks/ sheets **not opened [NV]** |
| 20. Reference Large Project Setup - Proposed JCM | Structure mapped three levels deep. It has no filled files to read **[V]** |
| Instance Plan sheets | 29 opened. 25 rendered; 4 did not render (see §8). Shapes checked in preview for 3 **[V]** → `downloads/02…`, `03…` |
| Sheets named "Project Plan" | Reference Project Plan (124 rows), C1 "Project Plan Excel" (706 rows), C3 "AMVAC Project Plan", C2 "Twelve SCM Project Schedule.xlsx" read **[V]**. About 40 other project-plan files (mostly .mpp) were listed only **[NV]** |

---

## 4. The three SOW + delivered-plan pairs (step 4)

| | **A — C2 SCM expansion (Twelve)** | **B — C1 large PLM (Tektronix PLM)** | **C — C3 small PLM (AMVAC)** |
|---|---|---|---|
| SOW file | `Cloud SCM Expansion 2024/08 Project Management/SOW/Twelve - Oracle Cloud SCM Implementation SOW v4 (signed)` (Doc; PDF twin), 24 Jan 2025 **[V]** | `10 PMO/Tektronix PLM Cloud Implementation SOW (v12) (2).pdf`, 22 Apr 2024, 45 pp **[V, read by section]** | `01 Kick Off/AMVAC - PLM Cloud Implementation SOW 23FEB22.pdf`, 9 pp **[V]** |
| Plan file | `08 Project Management/Twelve SCM Project Schedule.xlsx` (6 sheets: SOW Timeline, SCM SOW, SCM Current, CR to AUG, SCM Accelerated, SCM Old) **[V]** | `10 PMO/Archive/Project Plan Excel` (MS Project export, 508 tasks) **[V]** | `10 Project Management/AMVAC Project Plan` (55 tasks) **[V]** |
| Also present | `Twelve Instance Plan 2025.xlsx`, Cutover Plan, CRP Approach, design workshop schedule **[V names]** | Five instance-plan versions + Master **[V]** | none |
| Modules | PIM, Inventory & Cost Mgmt, Self-Service Procurement, Purchasing, Supplier Portal, Manufacturing (process), Maintenance; Sustainability, Expenses (TBD); incremental GL/SLA, AP, AR, PPM, Grants, Cash, FA; Requisitioning/Purchasing BUs added to the enterprise structure **[V]** | PD, PDH, Quality Mgmt Cloud, EG&C/GoCompliance, Supplier Portal (plan), Archiver, PowerTools; up to 10 App Composer customizations **[V]** | PD / PDH (trial data); ARM database hosting **[V]** |
| Environments | SOW: not stated. Instance plan: Production, Test, Development (Dev 2) = 3 **[V]** | Fusion prod, test, dev1, dev3 = **4 pods**, plus EBS dev/test/prod, Enovia test/prod, GoCompliance test/prod, GoCad, Archiver as rows **[V]** | Plan task "Provision PLM DEV, TEST, PROD" = 3 **[V]** |
| Rounds | SOW plan: CRP1 (wk5-6), CRP2 (wk9-10), UAT (wk13), Mock 1/2 data loads. Re-plan "CR to AUG": CRP0, CRP1, CRP2, UAT 3 weeks, Go-Live Ready, HyperCare **[V]** | SOW: "2 CRPs and 1 UAT". Plan: CRP test phase, SIT test phase (the SOW's CRP2), UAT test phase; DM rounds: CRP partial → SIT Round 1 + Delta → UAT Round 1 + Delta → PROD Round 1 + Delta **[V]** | SOW: "1 CRP and 1 UAT". Plan: CRP 9/28–10/5/22, UAT 10/6–10/17, Go-Live 12/19/22 **[V]** |
| Duration | SOW: **12 weeks**. Schedule: 15–16 weeks (Feb 17 → Jun 2, 2025); re-planned to about 27–32 weeks (to Aug 2025) **[V]** | Plan: Oct 4 2024 → Go-Live **Jan 19 2026** → hypercare to Mar 2 2026 (367 working days ≈ 73 weeks); 6 weeks of hypercare in SOW **[V]** | Plan: Mar 17 → Dec 19 2022 ≈ **40 weeks** (SOW points to a separate "AMVAC Resource Plan", not opened) **[V / NV for the resource plan]** |
| Integrations | SOW: "No extensions and integrations are part of the target scope". Conversions: Suppliers. Report: printable PO **[V]** | PD↔EBS, PD↔ECAD, PD↔MCAD, Z2↔PD (bi-directional); RPDB, Sitecore web publish, GENDB licensing DB (uni-directional); OIC-based adapters, JIRA adapter **[V]** | None by GoSaaS (client builds interfaces); plan has "ARM interface in ORACLE" **[V]** |
| Size | ~4,800 hrs, 10 roles **[V]** | Largest; 45-page SOW **[V]** | 667 hrs, 4 roles **[V]** |

Why these three: Twelve is the only pair where SOW, plan and instance plan all exist and the scope is Oracle SCM/procurement. Order Management is not in Twelve's SOW scope; its OM RTM file exists under "98 Files from Twelve". Tektronix PLM is the instance plan you named and the richest plan. AMVAC is a small, completed, end-to-end example. Cohu Redwood (SCM/OM) has a "CX & SCM Project Plan" but I found no matching SOW, so I did not use it **[NV]**.

---

## 5. Instance plan structure (step 5)

Templates in `1 Kickoff/Instance Plan 2022–2025.xlsx`, customer copies, and the C1 Tektronix plans:

- **Grid:** column A holds the environment labels. From column C on, one column per **week** (Monday dates, `30-Sep-24` style), usually covering 12–24 months. Row 1/2 is the header with the customer name in A. **[V]**
- **Header colouring (C1):** weekly header cells are filled **yellow (#ffff00) in Oracle quarterly-update weeks** (e.g. 9–30 Dec 24, 10–31 Mar 25, 2–23 Jun 25, 1–29 Sep 25, 1–29 Dec 25). Grey (#e7e6e6) or blue (#8eaadb) marks other blackout weeks. A row "EA Milestones (Est.)" carries dark-grey cells "EA: D / EA: T / EA: P" (Early Adopter Dev/Test/Prod) **[V]**
- **Rows (environments):** each Oracle pod is a band of 4–7 merged rows. Template: Production, Test, Development. C1: Production - Fusion (prod), Test - Fusion (test), Development - Fusion (dev1), Development - Fusion (dev3). Below the Oracle pods, single-row full-width coloured bars show **non-Oracle environments**: EBS Dev/Test/Prod, Enovia Test/Prod, GoCompliance Prod/Test, GoCad, Archiver (C1); Dell Boomi Dev/Test/Prod (Shockwave); GIM, ETS, M2M Integration, Solidworks Integration (Cirtec); legacy Agile On-Prem Dev and sites (Nissha). Newer 2026 "OCPLM" plans (Samba Nova, SiTime, UNICOM, ATEC) have rows "Oracle Release (In Test)" and "Holiday Weeks" **[V]**
- **Oracle update cohort bar:** one row under the pods. Each release is a merged run of **13 weekly cells** labelled `24C`, `24D`, `25A`, `25B` … with alternating fills (#d9e2f3 / #5b9bd5 in C1; greys #d8d8d8/#bfbfbf/#f2f2f2 in the templates). Partial quarters at the edges are shorter runs **[V]**
- **Cohort key (template text):** "Patch A = Feb, May, Aug, Nov; Refresh B = Mar, Jun, Sep, Dec; C = Apr, Jul, Oct, Jan; LS = A (Dev) + B (Test & Prod); Cutover Non-Prod = 1st Friday; Prod = 3rd Friday." C1 and Samba Nova note that quarterly patches are on the first Friday in Test **[V]**
- **Block types (drawn as Excel shapes, seen in Drive preview):** **[V for Sally, C1, template]**
  - *Configuration* / *Config Dev* — blue rectangle on the Test (or Dev) row
  - *Data Migration / Data Load* — grey or dark-blue rectangle; C1 splits it into *Round 1* and *Delta*
  - *CRP / CRP2/UAT / UAT* — green rounded rectangle on Test; green "UAT" boxes are repeated on the GoCompliance/integration rows to show which systems join UAT
  - *Smoke Test* — small pale-yellow box after a data load
  - *Patch Test* — purple box (Sally) or tall peach box spanning Test + Dev rows (C1), placed in update weeks
  - *Go/NoGo* (green star) and *GoLive* (black star) markers on top rows
  - Arrows: **orange/brown down arrow = Oracle patch/update** applied to a pod; **blue arrow = refresh** (P2T/P2D); **black vertical arrow = data extract**; orange **triangles A/B/C** under the pods mark cohort patch dates
  - Shockwave writes phase names into cells instead: PREP/KICK-OFF, WORKSHOP, CRP1, CRP2, SIT, TRAINING, UAT, VALIDATION, CUTOVER, GO-LIVE, STABILIZATION **[V]**
- **How conflicts are avoided** (from what is visible plus the checklist text): **[NV — inferred from layout and notes, not a written rule]**
  1. Test-cycle blocks are placed between the yellow update weeks; *Patch Test* boxes sit in the update weeks themselves.
  2. Refreshes (P2T) are timed after the Prod patch and before a test cycle ("Refresh P2T – Prior to UAT", "review refresh dates for UAT").
  3. Text actions in the plans: "Request Concurrent Patching", "Request Cohort C", "Right Size Test/Production", "Took this out due to concurrent patching". The PM checklist says "Open SRs to get the update schedule and create instance plan"; the methodology says "Inquire the upgrade plan … so that it doesn't affect the implementation milestones"; the C1 SOW lists "Timing of Oracle Software Update" as a risk, with update deferral as mitigation.
  4. Plans are versioned per re-plan (sheets "As of 2/12/2025", "As of 4/24/2025", "Feb 26 GL" vs "Earlier GL"; Christie Digital has 10 dated files).
- **C1 plan also as tasks:** the project plan has WBS 1.2 "Oracle Quarterly Updates (Cohort C)" with each quarter as a 10-day task holding two 0-day milestones, "Non Production" and "Production" (two weeks apart, date-constrained). Some feed successors **[V]**

---

## 6. Project plan structure (step 6)

| Aspect | Reference "Project Plan" (10 PM/Project Plans) & C1 & C3 | C2 Twelve schedule |
|---|---|---|
| Origin | MS Project export pasted into Google Sheets. .mpp originals exist (Shockwave, Zebra, VPC, Nissha) **[V]** | Hand-drawn weekly Gantt in Excel **[V]** |
| Columns | Project, Task ID, WBS, (Phase), Resource Names, Task Name, Duration, Start, Finish, Status (Complete / Late / Future Task / On Schedule), (Constraint Date), Predecessors, Successors, % Complete, Resource Group, Deadline, Start Slack, (Task Calendar, Ignore Resource Calendar), Task Mode, (WBS Predecessors, WBS Successors) **[V]** | Rows = activity bars; columns = week dates + week numbers **[V]** |
| WBS levels | Reference: 3–4 (e.g. 4.4.2.9); C3: 2; C1: up to 7 (1.3.2.2.1.3.1). Some WBS values were auto-converted to numbers (1.10 → "1.1") **[V]** | none |
| Dependencies | Task-ID lists in Predecessors/Successors, with types and lags (`193SS`, `119FS+3 days`); also WBS-coded predecessors (reference). C1: 273 of 508 tasks have predecessors **[V]** | Implied by bar order only **[V]** |
| Resources | Resource Names (individual or "Client", "Holiday", "Milestone") + Resource Group (SME, Techno-Functional, Client, Milestone) **[V]** | Separate "F&A Resources Available" footer row **[V]** |
| Durations | "N days" (a "?" suffix = estimated), 0-day milestones in yellow-filled rows (`MILESTONE – CRP2 COMPLETE`), holiday rows in orange **[V]** | Weeks spanned by the bar **[V]** |
| % complete | `% Complete` column; summary rows roll up (e.g. 7% at project level) **[V]** | none **[V]** |
| Phase skeleton | Prep & Infrastructure (incl. *Instance Plan*, Refreshes P2T) → Design → Data Evaluation → CRP1 Prep (config, migrator, data load, readiness) → CRP1 → exit criteria → CRP2 → UAT (prep, config, data load, validation, Go/NoGo) → Training → Cutover → Hypercare **[V]** | Kick-off/PIT → Design workshops → CRP0/1/2 (prep, run, fix) → UAT → UAT fix → Go-Live Ready → HyperCare; TTT, Prod data load coordination, config migration **[V]** |

---

## 7. What is in this folder

```
DRIVE_REFERENCE.md
downloads/   (9 read-only text captures, masked names)
  01_checklists_capture.txt            Scoping / Methodology / PM / Pre-Impl / Pre-Sales checklists
  02_instance_plans_all_capture.txt    templates + 25 customer instance plans (structure)
  03_C1_instance_plan_capture.txt      PLM Tektronix Instance Plan (1-31-2025).xlsx, both sheets
  04_C2_scm_project_schedule_capture.txt  Twelve SCM Project Schedule.xlsx, 6 sheets
  05_C1_plm_project_plan_capture.txt   Tektronix "Project Plan Excel" (WBS summary)
  06_C3_small_plm_project_plan_capture.txt  AMVAC Project Plan
  07_C2_scm_sow_capture.txt / 08_C1_plm_sow_capture.txt / 09_C3_small_plm_sow_capture.txt  SOW summaries (rates/amounts omitted)
notes/       customer scan, template captures, kickoff/PM notes, SOW notes
```

---

## 8. Could not open / needs attention

| Item | Issue |
|---|---|
| Any original-file download | The built-in browser discards downloads, so originals were not saved; text captures only. Re-run in Chrome with the extension connected to get the real .xlsx/.pdf files. |
| Tektronix "Copy of PLM Tektronix Master Instance Plan (10_7_2026) with Jan EA Push.xlsx", Trellix OCPLM Instance Plan 11_3_2026.xlsx, Glaukos Instance Plan 2025 (2) (2).xlsx, Omron OCPLM Instance Plan 10_9_2026.xlsx | The Sheets HTML view did not render them (timed out twice). Not read. |
| .mpp project plans (Shockwave, Zebra, VPC, Aerovironment, Nissha Norwalk, reference Templates) | Cannot be rendered in the browser. Not read. |
| AMVAC "AMVAC Resource Plan" (linked from the SOW) | Not opened. |
| Instance-plan shapes for the other ~22 plans | Only cell data captured; shapes not checked in preview. |
| Tektronix SOW pages not listed in §4 | Read by keyword sections, not line by line. |
| Folders with 50+ items at one level (Ampere, Applied Opto, ATEC, Christie, Ciena, Cohu, Fluke, Glaukos, Renesas, Sally, TDK, Tektronix PLM) | Listing cut to the first 50 entries at that level, so some files may be missing from §2. |
| Slides (.pptx / Google Slides: Default Kick Off, status decks, Glaukos instance-plan deck) | Not opened. |
| Access | Nothing returned "no access". Every folder listed opened under your account. |
