#!/bin/bash
# Double-click this file to open the job search dashboard (macOS).
# It starts a small local server and opens the page in your browser.
# Close this window, or press Ctrl+C in it, to stop the dashboard.

cd "$(dirname "$0")/.." || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed."
  echo "Install it from https://www.python.org/downloads/ and double-click this file again."
elif ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))'; then
  echo "Your Python is too old. This needs Python 3.8 or newer."
  echo "Install a current version from https://www.python.org/downloads/ and try again."
else
  python3 scripts/app.py
fi

echo
read -n 1 -s -r -p "Press any key to close this window."
echo
