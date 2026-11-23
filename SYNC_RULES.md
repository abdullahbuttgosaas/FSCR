# Sync rules (PC <-> laptop)

1. **One machine at a time.** Do not work on both at once.
2. **Pull before work, push after.** Start with "Start session" (runs `git pull`), end with "End session" (Claude commits; Abdullah runs `git push` himself). If a push is refused because the other machine pushed first: `git pull`, fix any conflict, push again. Never force-push.
3. **STATUS.md cards: never overwrite a newer card with an older one.** On a conflict in any `gaps-filled\...\STATUS.md`, compare the `date:` key of both versions:
   - keep the one with the later date;
   - on the same date, keep both: put the other machine's version into the file under a line `conflict: yes` (or save it beside as `STATUS.conflict.md`) and tell Abdullah. Do not guess.
4. **After any merge or pull that changed cards**, run `python rebuild_index.py` in `gaps-filled\` and check the counts it prints (rows should stay 935; "tested" must not go down). Never hand-edit `gap_index.csv` or `gap_progress.tsv`.
5. **Big files (over 50 MB) and ignored files are not in git.** If one is needed on the other machine: zip only that file, tell Abdullah to move it by Google Drive or USB, then update its line in `BIG_FILES.md` (add the machine it now lives on), commit, and Abdullah pushes.
6. **Secrets never go in git** (`fscr-signin-values.txt`, `Configuration Automation\.env`, `Configuration Automation\.session\state.json`, any filled `fusionEnv.properties`, token or cache files). Each machine keeps its own, made by hand from the `.example` templates. Before every commit, check the staged list for them.
7. **Line endings are never converted** (`.gitattributes` has `* -text`; both machines have `core.autocrlf false`). Files must stay byte-identical.
8. **Paths:** keep the folder at the same short place on both machines (`E:\GoSaaS\Configuration Automation v2.1` on the PC). Many paths are over 240 characters; both machines need `core.longpaths true` and Windows long paths enabled.

First time on a machine that has no CLAUDE.md yet: git pull, then read CONTEXT.md and do the Start session steps.
