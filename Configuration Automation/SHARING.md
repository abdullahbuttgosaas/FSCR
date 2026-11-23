# Sharing this project

Zip the project folder WITHOUT these (they are personal, per-PC or temporary):

| Leave out | Why |
|---|---|
| `.env` | Your Oracle user name and password, pod address and environment label. Anyone with it can sign in as you. Each person creates their own from `.env.example`. |
| `.session/` | Your saved, signed-in Oracle browser session. Works like a password until it expires. |
| `.setup_ok` | Says setup passed on YOUR PC. On another PC it must be missing so Claude runs the setup there. |
| `_work/` (in any folder) | Temporary export/import zips from a run. They contain real Oracle setup data and can be regenerated. Normally deleted automatically; kept only after a failure. |
| `__pycache__/` | Python cache files; rebuilt automatically, PC-specific. |
| tools folder (`%LOCALAPPDATA%\ConfigAutomation\tools`, or `page/_work/tools/` when that can't be written) | Claude's helper and a portable Node.js installed for YOUR user. Large and PC-specific; each PC installs its own. The main one is outside the project anyway; never copy it in. |
| `page/_work/claude_skipped` | Says you chose "Continue without automatic fixes" on YOUR PC. |

Everything else (`common/`, the configuration folders, `CLAUDE.md`, `README.md`,
`requirements.txt`, `.env.example`, `.gitignore`, this file) should be included.

Quick check before zipping (PowerShell, from the project folder):

```
Get-ChildItem -Recurse -Force -Include .env,.setup_ok,state.json,*.zip | Select-Object FullName
Get-ChildItem -Recurse -Force -Directory -Include .session,_work,__pycache__,tools | Select-Object FullName
```

Anything listed there must not go into the zip. The same names are in
`.gitignore`, so a git repository leaves them out automatically.

After unzipping on a new PC: open the folder in Claude and say "set up"
(see "First-run setup" in `CLAUDE.md`).
