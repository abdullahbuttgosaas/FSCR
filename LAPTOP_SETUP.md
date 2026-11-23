# Laptop setup (one time)

The laptop already has the full folder, unzipped from `Configuration Automation v2.1 (2).zip` (made on the PC on 2026-11-23 at 15:50, before the repo existed). These steps connect that folder to the repo **without changing any of your files**.

1. **Install Git for Windows** (git-scm.com) and **Python 3.12** (python.org; tick "Add to PATH"). Check: `git --version`, `python --version`.
2. **Turn on Windows long paths** (needed: about 6,100 paths here are over 240 characters). In PowerShell **as administrator**:
   `New-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force`
   (The PC already has it on.) Keep the folder at a short place, ideally `E:\GoSaaS\Configuration Automation v2.1` like the PC.
3. **Same git settings as the PC** (normal PowerShell):
   ```
   git config --global core.longpaths true
   git config --global core.autocrlf false
   git config --global core.safecrlf false
   git config --global user.name "Abdullah Butt"
   ```
4. **Connect the folder** (inside the unzipped `Configuration Automation v2.1` folder):
   ```
   git init -b main
   git config core.longpaths true
   git config core.autocrlf false
   git config core.safecrlf false
   git remote add origin https://github.com/abdullahbuttgosaas/FSCR.git
   git fetch origin
   git reset --mixed origin/main
   ```
   `git fetch` opens a GitHub sign-in window the first time; sign in there (Git Credential Manager keeps it; nothing goes in a file). `git reset --mixed` only points git at the repo; it does not touch any file.
5. **Check:** `git status`. Acceptable differences:
   - **"deleted:" for the files the PC added after the zip was made**: `.gitignore`, `.gitattributes`, `README.md`, `CONTEXT.md`, `SYNC_RULES.md`, `CHANGELOG.md`, `BIG_FILES.md`, `LAPTOP_SETUP.md`, `HANDOFF_RESULT.md`, `fscr-signin-values.txt.example`, `Configuration Automation\.session\state.json.example`, `_patches\*`. Bring them in with `git restore -- .gitignore .gitattributes README.md CONTEXT.md SYNC_RULES.md CHANGELOG.md BIG_FILES.md LAPTOP_SETUP.md HANDOFF_RESULT.md fscr-signin-values.txt.example "Configuration Automation/.session/state.json.example" _patches`
   - **"deleted:" for very long paths**: the unzip tool may have skipped files with paths over 260 characters. `git restore -- <path>` brings them back from the repo.
   - **Untracked files**: none expected (ignored folders like `fscr-official-clone\` stay quiet).
   - **"modified:" files**: NOT expected. If any appear, do not restore them; tell Claude (it may be a line-ending change by the unzip tool, or work done on the laptop after the zip).
6. **Re-create the secrets by hand** (they are not in git). Templates with key names only:
   - `fscr-signin-values.txt` from `fscr-signin-values.txt.example` (values from Abdullah's own copy; the zip already has it if it was unzipped whole)
   - `Configuration Automation\.env` from `Configuration Automation\.env.example`
   - `Configuration Automation\.session\state.json`: made by the page's sign-in (`.example` shows the shape)
   - `core\auth\fusionEnv.properties` inside any FSCR copy you use, from `_patches\fusionEnv.properties.example`
   If the zip was unzipped whole, these files are already there; just check they exist and never `git add -f` them.
7. **First message to Claude in this folder:** `Start session.`
