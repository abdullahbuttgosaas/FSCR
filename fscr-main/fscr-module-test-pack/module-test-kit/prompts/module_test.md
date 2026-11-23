# Prompt: test one module

Fill in the three values, then give the whole text to Claude (Opus 5.5) in this pack's folder.
`{MODULE}` is the tracker row name, `{TRACKER_ROW}` is the row's pillar and position (or just repeat the module name),
and `{INITIALS}` is your initials (2 or 3 letters).

---

Test the FSCR module **{MODULE}** (tracker row: {TRACKER_ROW}). My initials are **{INITIALS}**.

Work in this pack's folder. Follow `module-test-kit/PLAYBOOK.md` step by step, and obey its Rules section
at all times:
- test environment only; I sign in myself with my own Oracle login, and you never type or ask for my password;
- create only records named `FSCRT_{INITIALS}_...`; never edit or delete existing data;
- never print tokens, passwords or user names;
- at most 4 PNG table images, made by `make_images.py`.

Do this:
1. Write the start time. Check `runID` in `core/data-loader/config/env.properties` is empty or mine. Help me sign in
   with FSCR's onboarding and PKCE login. Don't show the values in `fusionEnv.properties`.
2. Coverage: `scope_filter.py --module "{MODULE}"`. It must say "match".
3. Plan: build FSCR's plan for an FSCR project named `FSCRT_{INITIALS}_{MODULE}`. Run `plan_builder.py`. Read Oracle's
   26D documentation for this module, save each page with `fetch_oracle_page.py`, and write `links_input.csv`, where each
   link has a URL and an exact quote, or is marked unverified. Run `plan_builder.py` again with `--links`. Report (a) sourced links
   respected, (b) unverified links out of order and (c) FSCR-stated prerequisites out of order.
4. Run Book: create `FSCRT_{INITIALS}_{MODULE}` with FSCR's `core/runbook`. If the create call times out, do not resend it:
   check later by name and bind it by hand. Run `runbook_check.py`.
5. Six tasks from `sample_candidates.csv`: 2 Skill + route, 2 Route only, 2 Neither (as far as they exist). Load through
   the Data Loader with Task Hook, write the rule results only from real checks, and read back every record. Follow the
   "Known problems" list in the playbook. Do not count tasks that Oracle gives no CSV or API for. Write `six_tasks.csv`.
6. Score with the tracker Guide's exact wording (in the playbook). Give a reason with a number for each score.
7. Write `tracker_row.md` (template, then `SHEET_FILL_GUIDE.md`) until `tracker_row.py check` says PASS. Make the 4 images.
   Write `RESULT.md` from `templates/RESULT.md`. Run `build_evidence.py` until it says PASS, then `secret_scan.py` on
   `evidence/{MODULE}`.
8. Tell me in plain words: the verdict, the scores with their reasons, the evidence folder path, and that I should upload
   `evidence/{MODULE}` to Drive and send Abdullah the folder link (I do not edit the tracker).

**Last step, always, even if something failed:** stop and delete every server or process you started (the sign-in
listener on port 8765, headless browsers, Python scripts). Check that port 8765 is free and nothing from this run is
still running. Write the finish time and minutes in RESULT.md, and confirm the clean-up to me.
