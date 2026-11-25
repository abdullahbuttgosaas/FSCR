# Dashboard: how to update it (for Claude in any new chat)

When the user says **"update the dashboard"** (or "push the dashboard", "refresh the dashboard"), do every step below yourself. Do not hand steps back to the user. Keep them posted in one short line per step.

**Live site:** https://fscr-gap-dashboard.vercel.app (Vercel project `fscr-gap-dashboard`, deployed from this folder with the Vercel tool, no GitHub).

## Steps

1. **Rebuild the gap index** (the counts come from the `STATUS.md` cards):
   run `python rebuild_index.py` inside `gaps-filled\`. Skip only if it was just run at "End session".
2. **Rebuild the dashboard data:** run `python dashboard\update.py` from the work folder.
   - It prints 5 lines. The last line must say `all checks passed`.
   - If it lists a mismatch (exit code 1), find the cause in the source files, fix it, and run it again. Do not deploy wrong numbers.
3. **Deploy:** run `vercel --prod --yes` inside `dashboard\`, in a Terminal tab the user can see (not a hidden shell; it takes about 10 seconds).
   - If it says you are not signed in: run `vercel login` in a visible tab and ask the user to finish the sign-in in the browser. Only they can do that.
4. **Check:** open https://fscr-gap-dashboard.vercel.app and confirm "Skills available now" matches the number `update.py` printed.
5. **Tell the user** in 3 lines: skills before, skills available now (+gain), and the link.

## Rules

- `dashboard\.env.local` holds a Vercel token. Never print it, open it in chat, commit it or upload it. `.vercelignore` and `.gitignore` already keep it out.
- `.vercelignore` keeps `update.py`, `README.md`, `UPDATE_STEPS.md`, `screenshots` and token files off the live site. Only `index.html` and `data\` are served.
- The dashboard folder must hold no secrets and no names of people, environments, servers or users.
- Do not connect the project to GitHub (Vercel offers it; say no). Do not push to GitHub.
- The user removed these from the page; do not add them back: the "N tested, N written" line under "Skills available now", the tested/written definitions at the bottom, and the "Skills available over time" chart. `history.json` still records one snapshot per day.
- Number definitions are in `README.md` in this folder.
- Optional: a private copy also exists at https://claude.ai/artifact/CeSNAZoWBhF42ifo1pheBH. Update it only if asked.
