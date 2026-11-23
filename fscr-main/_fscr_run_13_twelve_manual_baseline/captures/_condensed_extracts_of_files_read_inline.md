# Condensed extracts: files read through the Google Drive connector, shown inline

These files were opened and read in full (VERIFIED). The connector returned their text into the session only, not to disk, so this file holds faithful condensed extracts, not verbatim dumps. Contacts, rates and amounts are left out. Person names appear only where they are part of a role table.

## Twelve Enterprise Structure.pptx
- **Path:** SCM/01 Trainings and Workshops/Design Workshops/Enterprise Structure
- **Drive list date:** Mar 19, 2025
- **Content:** 7 slides: Agenda; Enterprise Structure Objects (the 4 C's; LE/BU rules); BU Function to Module table (18 functions); "Current Twelve Structure"; "Enterprise Structure"; "Business Unit Function Structure".
- **Not readable as text:** slides 5–7 are diagrams (images), so no entity names come through.

## Twelve Enterprise Structure CRP 0.pptx
- **Path:** same folder
- **Drive list date:** Jul 3, 2025
- **Content:** same as above, plus the slides "CRP 0 Structure" and "CRP 1 (TBD) Structure".
- **Not readable as text:** these are image diagrams.

## Twelve - Oracle Fusion - Cost Management Best Start (Google Sheet)
- **Path:** SCM/03 Design Documents/Best Starts
- **Drive list date:** May 6, 2025
- **Cost Books:**
  - Twelve Benefit Cost Book ("Primary Stacks CB")
  - Twelve AirPlant One Cost Book ("Primary Fuel CB")
- **Cost Organizations** (effective 3/1/25):
  - Stacks Cost Org (Twelve_Cost_Org_01, LE Twelve Benefit Corporation)
  - Fuels Cost Org (Twelve_Cost_Org_02, LE Twelve Benefit Corporation)
- **Cost Org Relationships:**
  - Stacks Cost Org → inventory orgs Alameda (mfg plant TRUE) and Berkeley (FALSE); profit center BU Twelve Operations; Twelve Benefit Cost Book; US Ledger.
  - Fuels Cost Org → AirPlant One (mfg plant TRUE); BU Twelve Operations; Twelve AirPlant One Cost Book; US Ledger.
  - Item validation org: Twelve.
- **Cost Profiles:** Perpetual Average, with AirPlant One Asset/Expense C-I-P valuation structures.
- **Other sheets:** Cost Elements (Direct Materials, Direct Labor, Equipment … for AirPlant One manufacturing), Valuation Structure, Overhead pools.

## Cost Management CRP1 - TWELVE (Google Slides)
- **Path:** SCM/03 Design Documents/Cost Management
- **Drive list date:** Apr 16 (2026)
- **Content:**
  - Costing data gathering for Maintenance, Manufacturing and Inventory.
  - Default cost profiles for "AirPlant One Cost Org" and "Twelve Benefit Cost Org".
  - Moses Lake D7566 work definition (CO2 Conversion → E-Jet Creation) with item costing methods.
  - Blender E-Jet Main work definition.

## Twelve CRP1 Manfuacturing Structure.pptx
- **Path:** SCM/03 Design Documents
- **Dates:** created not recorded; Drive list date May 6, 2025
- **Content:** "Air Plant CRP2 Manufacturing Structure". Current vs proposed 2-step structure:
  - 10 CO2 Conversion
  - 20 E-Jet Creation
  - Covers resources, consumption types and reporting.

## Rippling - HR Integration.pptx
- **Path:** SCM/03 Design Documents/Rippling - Oracle HR Integration
- **Drive list date:** May 13, 2025
- **Content:**
  - Integration scope: Rippling → Oracle HCM.
  - Rippling is the system of truth for employees (onboarding/offboarding).
  - Flow: employee data file → OIC (get file, transform/map) → create/update employee in Oracle HCM, with success/failure response.
  - Prerequisites: OIC access, individual and service accounts, optional OIC connectivity agent, HCM access, mapping sheet.
  - Deliverables: FSD, implementation, deployment, integration testing, CRP scripts, CRP/UAT support, production deployment.

## Twelve Project Plan (Google Sheet)
- **Path:** SCM/03 Design Documents/Archive
- **Drive list date:** Aug 14, 2025
- **Project Plan sheet:** about 277 numbered task rows, plus un-numbered configuration-task rows. Columns: Task ID, WBS, Resource, Task Name, Duration, Start, Finish, Status, Predecessors, Successors.
- **Predecessors filled on only 5 rows**, all in onboarding (WBS 1.1–1.3.2: tasks 2←1, 3←2, 4←3, 5←4, 6←4). Successors are filled on task 4 only.
- **All later phases have no predecessors.** That covers Design, CRP0/1/2, UAT, Training and Ready to Use, and many rows show "Missing Dates".
- **Phases (WBS):**
  1. Kickoff/Planning
  2. Pre-Implementation Training (2/11–2/21/25)
  3. Design (2/24–3/21/25; RTM, KDDs, Business Scenarios, Process Flows, Best Start update/sign-off, RICE, Data Migration Mock 1/2)
  4. CRP Preparation (3/17–3/28/25)
  5. Test configurations / CRP1 (3/31–4/4/25)
  6. CRP2 Prep (4/7–4/18/25)
  7. CRP2 phase and UAT Prep (5/5–5/9/25)
  8. UAT (5/12–5/16/25)
  9. End User Training
  10. Ready to Use
- **Configuration task list under 4.7 "Configure test environment"** (counts in the main report): Enterprise Structures 18, Procurement 15, Product Data Hub 4, Sustainability 7, Inventory 28, Maintenance 5 pre-config + 24 config, Manufacturing 12, Costing 14, Payables 23, Supplier Portal 6.
- **Task Completion Summary:** 94 tasks due, 37 completed, 57 overdue (39%), computed against today's date.

## Twelve SCM Project Schedule.xlsx
- **Path:** SCM/08 Project Management
- **Drive list date:** Jul 10, 2025
- **Content:** week-grid schedules with several re-plan versions:
  - **"SOW Timeline"** (16 weeks, Feb-17 → Jun-02): Kick-off/PIT; Design; As-Is Finance capture; CRP1, CRP2, UAT; CRP2/UAT prep; Data Migrations; TTT; End User Training; Go-Live.
  - **"SCM SOW"** (15 weeks, Feb-17 → May-26): Mock 1 / Mock 2; Ready to Use; "F&A Resources Available" every 4 weeks.
  - **"SCM Current" (as of May 14, 2025):** CRP0 Prep, CRP0 (wk of Apr 7), CRP0 Fix, CRP1 Prep, CRP1 (wk of May 12), CRP1 Fix.
  - **"CR to AUG", with CRP2 and 3-week UAT** (to Aug-25): CRP2, UAT, UAT Fix, Go-Live Ready, HyperCare, Production Data Load Coordination, Config Migration.
  - **Variant without CRP2, 2-week UAT.**
  - **Variant to Jul-28:** Extended CRP1 Prep; CRP1; TTT ("actually an extension of CRP to close off the design"); UAT; Go-Live Ready; HyperCare.
  - **"SCM Accelerated":** same as SCM SOW.
  - **"SCM Old"** (12 weeks, Jan-13 → Mar-31): CRP1, CRP2, UAT, Mock 1/2, TTT, EUT, Ready to Use.

## Twelve Cutover Plan.xlsx
- **Path:** SCM/08 Project Management
- **Drive list date:** Aug 18, 2025
- **Content:** 24 numbered milestones (owner, status, start date):
  - **Cutover Preparation** (Aug-19): design configuration sign-off (PROD Best Starts); define processes; define policies & procedures; Go/NoGo decision; cutover communication email; PROD provisioning & admin access; PROD instance readiness check; freeze config changes in DEV2; enable modules in PROD.
  - **Integration Cutover** (Aug-20): HR configurations in PROD; HRIS/OIC integration to PROD; integration validation.
  - **Cutover (Applications)** (Aug-20..27): PROD configuration (Financials, Procurement, Projects, SCM); security configuration; cross-module transaction test in PROD.
  - **Cutover (People)** (Aug-28/29): end-user role assignment confirmation; responsibility & org structure verification; end-user training completion; freeze legacy Coupa.
  - **Go-Live:** Sep-2.
- **Status:** all milestones "Not Started".

## Twelve Cutover Strategy (Google Slides)
- **Path:** SCM/08 Project Management
- **Date:** 08/22/2025
- **Content:**
  - Go means transition to Oracle ERP Cloud SCM + Finance on 09/02/2025; No-Go means stay on Coupa and run the contingency plan.
  - Cutover dimensions: Integration, Reports, Applications, People, Data (RICE), Process, Technology.
  - **Go criteria:** no open high defects; UAT success 100% for key processes; critical configurations successful in PROD; training material repository built.
  - **No-Go triggers:** high-severity open UAT issues; failure of core integration (Rippling HR); Finance/SCM reconciliation gaps.
  - **Business Readiness Checklist:** Business Processes, Infrastructure, Data, People, each High priority, with GoSaaS and Twelve Go/No-Go columns.
  - **Application Checklist:** Financials (GL, AR, CM, FA), AP, Tax, Projects, Procurement, Inventory, Cost Management, Manufacturing, Maintenance, PIM, HRIS/OIC Integration. Each is checked for UAT, end-user training material and production configuration.
  - **Risk:** Financials Best Start review by the Finance team.
  - **Appendix scope:** HCM/OIC integration; Financials (GL, AP, AR, FA, Projects, Sustainability); SCM (PIM, Inventory & Cost, SSP, Purchasing, Supplier Portal, Manufacturing, Maintenance).

## Twelve SCM CRP Approach.pptx
- **Path:** SCM/02 Testing
- **Drive list date:** May 30, 2025
- **Content:**
  - Testing locations, SmartSheet script list and RAID log.
  - CRP1 entry criteria, including AirPlant financial modules in Best Starts, configurations loaded into DEV2, smoke tested, and AirPlantOne inventory and costing orgs re-entered into the AirPlantOne BU.
  - Functional and technical entry criteria tables.
  - Test sequencing CRP0 → CRP1 → UAT.
  - CRP 0/1/2 scope table.
  - CRP1 two-week agenda (May 19–30).

## Twelve SCM UAT Approach.pptx
- **Path:** SCM/02 Testing/3 UAT
- **Drive list date:** Jul 31, 2025
- **Content:** UAT uses Train-the-Trainer lab exercises; TTT agenda Aug 4–8, 2025 (MM 1-22, INV 1-17, MFG 1-10, CM 1-25, PIM 1-9, SUS 1-4, FA 1-4, Projects P2P end to end).

## Twelve - Requirements Gathering Tracker (Google Sheet)
- **Path:** SCM/03 Design Documents/Archive
- **Dates:** created 2024-11-06, modified 2024-12-11 (**BEFORE SOW**)
- **Content:** 8 module rows (SSP, Supplier Portal, Purchasing, Expenses, Payables, Inventory, PIM, Cost Management), with owner, design document, Best Start name and target dates (Nov 9–15, 2024; Cost Best Start Dec 11, 2024).

## Updated Discovery Questions for Twelve 12-Dec - Answers.xlsx
- **Path:** SCM/98 Files from Twelve
- **Dates:** created 2024-12-13, modified 2024-12-16 (**BEFORE SOW**)
- **Content:** Q&A by area (PLM, Maintenance, Inventory, Costing, Manufacturing). Facts relevant to this baseline:
  - **Costing:** average costing; elements electricity, labor, depreciation.
  - **Two production facilities:** Alameda supplies "stacks" to R1.
  - **Systems mentioned:**
    - M-BOM in spreadsheets and a Twelve-built application "Kiwi"
    - readings via laptops/mobile, PLC devices or Aveva PI dashboards
    - "nice to have" integration to PLC equipment
  - **Not an integration landscape:** no integration list or design.

## Twelve Procurement Design Document V1.docx
- **Path:** SCM/03 Design Documents
- **Drive list date:** Nov 20, 2024 (**BEFORE SOW**); change record dated 07-Nov-2024
- **Content:** generic Oracle Procurement foundation design (SSP, Purchasing, Supplier Portal, P2P steps).
- **Gaps:** the Organization Structure section has no Twelve entities. Detail sections say "Details have been provided in the attached File XXX". It ends with "To be edited based on questions answered by the Client".
