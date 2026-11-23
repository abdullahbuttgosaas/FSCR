# Twelve - Oracle Cloud SCM: SOW-only Wave Plan (summary)

This plan uses only the signed SOW (dated January 24, 2025; signed January 28, 2025) and general knowledge of Oracle Cloud projects. No start date was given, so weeks are numbered (Week 1 = the first week after GoSaaS receives the signed SOW). Anything marked **SUGGESTED** is my assumption, not the SOW's. Details are in `01_SOW_ONLY_WAVE_PLAN.xlsx`.

## What the SOW actually says (with section)
- Duration is **12 weeks** (SOW C.8). The SOW also calls this "an aggressive plan" (SOW B, Note).
- Scope: Product Information Management, Inventory & Cost, Self-Service Procurement, Purchasing, Supplier Portal, Manufacturing (process only), Maintenance, Sustainability, plus incremental Financials changes; Expenses only if a design session confirms it (SOW B; B Financials 5.1). The configuration list has 12 areas (SOW B Configurations Scope).
- One report (Printable Purchase Order) and one conversion (Suppliers); no integrations or extensions (SOW B RICE 1-3). Data migration is "minimal" (SOW C.5).
- Twelve tests the functionality (SOW E.1), runs change management (SOW C.4), and moves approved configuration to Production itself (SOW C.10). GoSaaS writes training material and trains the trainers (SOW B Change Management; C.6).
- Environments named in the SOW: only "development and production platforms" (SOW E.6). Financials is already live in production (SOW A).
- Go-live criteria "will be refined during the project" (SOW C.2.1). The SOW never states a go-live week.
- Hours (SOW D): 3,820 hours, $360,300.

## The plans (environments: PROJECT row, DEV, TEST, PROD; DEV/TEST split is SUGGESTED)
**Plan A, squeezed into the SOW's 12 weeks:** design Weeks 1-3; configure in DEV Weeks 3-6 (report and supplier conversion build alongside); move to TEST and load suppliers Week 7; test round 1 Week 8; test round 2 Week 9; user testing and train-the-trainer Weeks 10-11; Twelve moves configuration to Production and go-live Week 12; SUGGESTED hypercare Weeks 13-16 (outside the SOW). 16 weeks drawn.

**Plan B, SUGGESTED longer alternative:** design Weeks 1-4; configure Weeks 3-9; move to TEST Week 10; test round 1 Weeks 11-12; fix week 13; test round 2 Weeks 14-15; user testing Weeks 16-18; dress rehearsal and production migration Week 19; go-live Week 20; hypercare Weeks 21-24. 24 weeks drawn.

## Key SUGGESTED assumptions (all listed as open questions in the workbook)
Three environments (DEV, TEST, PROD); design 3-4 weeks; two system-test rounds; 2-3 weeks of user testing; suppliers only, with 2-3 trial loads; train-the-trainer during user testing; 4 weeks of hypercare; one Oracle quarterly update probably falls inside the project (cohort unknown); 40-hour working weeks.

## Is 12 weeks realistic?
**No, not for a full go-live.** Plan A adds up to exactly 12 weeks (3 design + 3 configure + 1 migrate + 1 + 1 testing + 2 user testing + 1 cutover) with **zero spare time**, test rounds of only one week, and production migration and go-live in the same week. The SOW's own hours also don't fit: the SCM Architect has 640 hours, which is 53.3 hours a week over 12 weeks (16 full-time weeks); the Inventory, Manufacturing/Maintenance and Procurement consultants have 560 hours each, which is 14 full-time weeks each. 12 weeks is plausible only if "duration" means getting the system configured and "Ready to Use" (SOW C.2), with Twelve doing the go-live afterwards (SOW C.10). Under my assumptions, **about 20 weeks to go-live plus 4 weeks of hypercare (Plan B)** is realistic.

## Who produced what
Timelines, environments, assumptions and arithmetic: **Claude alone**. Configuration sizing note (1,491 Oracle setup tasks across the three new SCM offerings, from the FSCR setup-task catalog): **FSCR + Claude**. The FSCR wave-planner and instance-strategy skills are generic placeholder text, so they were not used. Nothing was produced by **FSCR alone**.
