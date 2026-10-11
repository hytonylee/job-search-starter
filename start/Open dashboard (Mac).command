#!/bin/bash
# Double-click this file to open the job search dashboard (macOS).
# It starts a small local server and opens the page in your browser.
# Close this window, or press Ctrl+C in it, to stop the dashboard.

cd "$(dirname "$0")/.." || exit 1

if [ ! -f scripts/app.py ]; then
  echo "This launcher cannot find the rest of the project."
  echo "Keep it inside the project's start folder. If you downloaded a ZIP,"
  echo "unzip the whole folder first, then double-click this file again."
elif ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys' >/dev/null 2>&1; then
  # macOS ships a python3 placeholder that only offers to install Apple's developer tools.
  echo "Python 3 is not ready on this Mac."
  echo "If macOS just offered to install developer tools, accept, wait for it to finish,"
  echo "and double-click this file again. Otherwise install Python from"
  echo "https://www.python.org/downloads/"
elif ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))'; then
  echo "Your Python is too old. This needs Python 3.8 or newer."
  echo "Install a current version from https://www.python.org/downloads/ and try again."
else
  python3 scripts/app.py
fi

echo
read -n 1 -s -r -p "Press any key to close this window."
echo
