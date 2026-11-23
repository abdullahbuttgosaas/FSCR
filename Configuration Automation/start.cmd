@echo off
rem Start the page: installs the minimum it needs, then opens it in your browser.
rem Double-click this file. Close this window to stop the page.
setlocal
cd /d "%~dp0"
set "PY=python"
%PY% --version >nul 2>nul || set "PY=py -3"
%PY% --version >nul 2>nul || (
  echo Python is not installed yet. Installing Python 3.12 - please follow the prompts ...
  winget install -e --id Python.Python.3.12
  echo.
  echo When the installation has finished, close this window and double-click start again.
  pause
  exit /b 1
)
echo Getting things ready ...
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
echo Opening the page at http://127.0.0.1:8765  (keep this window open while you use it)
%PY% page\server.py --open
