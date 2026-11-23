#!/bin/sh
# Start the page (macOS / Linux): installs the minimum it needs, then opens it in your browser.
# Run: sh start.sh   Stop with Ctrl+C.
cd "$(dirname "$0")" || exit 1
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Python is not installed yet. Install Python 3.12 from python.org, then run this again."
  exit 1
fi
echo "Getting things ready ..."
"$PY" -m pip install --quiet --disable-pip-version-check -r requirements.txt
echo "Opening the page at http://127.0.0.1:8765  (keep this window open while you use it)"
exec "$PY" page/server.py --open
