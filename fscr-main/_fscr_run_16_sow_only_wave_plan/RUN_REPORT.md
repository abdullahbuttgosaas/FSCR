# Run 16: SOW-only wave plan for Twelve, compared with the team's final plan

- **Run folder:** `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_16_sow_only_wave_plan`
- **Input:** No SOW was attached to the chat. I used `input\50513 - Twelve - Oracle Cloud SCM Implementation SOW v4_Twelve-signed_GS signed.pdf`, copied from the Run 14 input folder (MD5 77241006ca0165557315ca946f4b6c56). verified
- **Paper only:** no Oracle pod, sign-in, Fusion call, token or server. verified (commands reviewed)
- **Tags:** verified = read from a file by script · not verified = judgment or statement.

## 1. How blindness was kept
- The session that received this task had already seen the team's plans and Run 15 in earlier tasks. So the pre-freeze work was given to a **fresh Claude agent with no memory**. Its brief repeated only the task's pre-freeze rules, with no answer content, and allowed it to read only the SOW and its own FSCR repo copy.
- **What the agent read before the freeze** (from `work\pre_freeze_log.md`):
  - the SOW, via pdftotext into `work\sow_text.txt`
  - in the repo copy: the wave-planner, fusion-instance-strategy and pod-strategy-advisor `SKILL.md` files; `knowledge\README.md`; and the setup-task catalog files (headers, offering task counts, one name search)
  - files it created itself
  - outside the run folder, only the `cp -r` of `fscr-main\fscr-main`
- **Exposure:** none reported. The agent saw a repo folder name, `configuration-baseline-manager`, and did not open it. not verified beyond its log
- **Nudge risk:** the brief listed "training, hypercare" as examples of assumptions to label. That may have nudged the agent to include hypercare. not verified
- **Repo copy:** `diff -rq` against the original shows no differences. verified
- **Freeze:** `work\freeze_record.txt` records Thu Nov 5 21:37:24 PST 2026. The shell's "PST" label is the local clock, UTC+5.
  - `01_SOW_ONLY_WAVE_PLAN.xlsx`: ea60b7e15cc8e3e7ee88cbc3b89f77fb
  - `01_SOW_ONLY_WAVE_PLAN.md`: 0cc00f9cce8e18d02a478b61caaa548b
  - Both MD5s re-checked after the freeze, and both files are read-only. verified

## 2. What the SOW-only plan says (Claude alone; one FSCR + Claude sizing note)
- **Environments:** DEV, TEST and PROD (SUGGESTED). The SOW names only "development and production platforms" (E.6).
- **Plan A, 12 weeks:**
  - design weeks 1–3, configure weeks 3–6
  - SIT 1 in week 8 and SIT 2 in week 9, with no gap
  - UAT and train-the-trainer in weeks 10–11
  - production migration and go-live in week 12
  - hypercare weeks 13–16
- **Plan B, SUGGESTED, 20 weeks:**
  - design weeks 1–4, configure weeks 5–9
  - SIT 1 in weeks 11–12, a fix week 13, SIT 2 in weeks 14–15
  - UAT in weeks 16–18 and a dress rehearsal in week 19
  - go-live in week 20, hypercare weeks 21–24
- **Verdict on 12 weeks:** not realistic.
  - 3+3+1+1+0+1+2+1 = 12 leaves no spare time.
  - SOW hours: the SCM Architect's 640 h means 53.3 h a week over 12 weeks.
  - 22 SUGGESTED assumptions, each with an open question.
- **FSCR:** the wave-planner and instance-strategy skills are placeholders. The catalog gave one sizing note: 1,491 setup tasks across the three new SCM offerings.

## 3. Team's final plan (read after the freeze, by script)
- **Files:** the Drive originals *Twelve SCM Project Schedule.xlsx* and *Twelve Instance Plan 2025.xlsx*. These were downloaded earlier the same day in this session, and their MD5s match the copies in the Desktop wave-plan folder. I read cell values, fills, merged cells, comments and drawings.
- **Schedule workbook:** 6 sheets, including "SOW Timeline" (16 weeks, 17 Feb–2 Jun 2025, go-live in week 16). The "CR to AUG" sheet holds 3 versions and has no drawn shapes. verified
- **Final plan picked: "CR to AUG", version 3 (rows 25–37).** Go-live ready in the week of 25 Aug, hypercare weeks 29–32 (1–26 Sep). This matches CR #02 final (1 Sep) and the Cutover Strategy (2 Sep). The file has no "final" label, so the pick is a judgment. not verified
  - kick-off and training weeks 1–3, design weeks 2–9 (8 weeks)
  - CRP0 in weeks 8–9; CRP1 prep weeks 10–14; CRP1 in weeks 15–16; CRP2 dropped
  - training and process-flow prep weeks 17–20; train-the-trainer in week 22
  - UAT weeks 23–25 (3 weeks); UAT fix weeks 26–27
  - production data load coordination weeks 25–27; config migration weeks 26–27
  - total 32 weeks. verified
- **Instance plan** (drawn shapes, as of 24 Apr): Production / Test / Dev 2, cohort-A update markers, an Eid break, and "Ready to Use" around 11 Jul. verified

## 4. Comparison (19 items; `wave_plan_sow_only_comparison.xlsx`)
**Covered 4 · Partly 8 · Missed 1 · Contradicted 0 · Not in the manual plan 2 · Not findable from the SOW 4.** verified (script count)
- **Covered:** the 3 environments, the phase order, 2 test rounds before UAT, and 4 weeks of hypercare.
- **Partly:**
  - pre-implementation training
  - test-round length (1 week in Plan A, 2 in Plan B, the team 2)
  - gaps (0 or 1 week vs the team's 2–5)
  - UAT (2 or 3 weeks vs 3)
  - train-the-trainer timing
  - production migration time
  - Oracle update weeks (no cohort given)
  - the "Ready to Use" milestone
- **Missed:** the 2-week UAT fix period.
- **Not findable from the SOW:**
  - 8 weeks of design and the September go-live: re-planning and CR #02
  - total weeks: from that re-planning
  - the holiday week: the customer's calendar
- **Not in the manual plan:** mock loads and dress rehearsal; SOW deliverables drawn on the timeline.
- **Against the SOW Timeline (16 weeks):** Plan B is 4 weeks longer. Plan A's 1-week test rounds are shorter than the team's 2.

## 5. Versus Run 15 (given our checklist, rules and start date)
- **Run 15 closer:** 2-week test rounds, gaps, data-load sequence, Oracle update weeks (cohort-A dates fall in the team's marked weeks), and an exact match to the 16-week SOW Timeline.
- **Run 16 closer:** overall length (20 vs 28 weeks), 3-week UAT and 4-week hypercare.
- **The same in both:** 2 test rounds before UAT, 3 environments, and no UAT fix period.
- **Plain answer:** the checklist and rules made the plan closer to the team's SOW-era plan and its test-round mechanics, but not closer to the final plan's length. not verified (judgment)

## 6. Metrics
- **Time:** setup 21:30:04; blind agent 21:30:30 → 21:37:24 (about 7 min); comparison and report to about 21:41, local UTC+5. Total about 12 minutes to this report; the copy to the Desktop followed. verified (shell clock)
- **Tool calls:** blind agent 20 (from the app's usage record). This session's own calls for this task were about 15 by this report; not recorded exactly.
- **Output tokens:** not recorded. The app reported 111,767 tokens in total for the blind agent, input and output combined.
- **Processes:** none left running. The blind agent ran one foreground copy and reported nothing still running.
