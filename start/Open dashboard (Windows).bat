@echo off
rem Double-click this file to open the job search dashboard (Windows).
rem It starts a small local server and opens the page in your browser.
rem Close this window, or press Ctrl+C in it, to stop the dashboard.

cd /d "%~dp0.."

rem Run a one-line check instead of trusting "where": the Microsoft Store
rem placeholder named python.exe exists on PATH but is not Python.
rem The check is written without angle brackets, which batch files treat as redirection.

py -3 -c "import sys; sys.exit(int(not sys.version_info.__ge__((3, 8))))" >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\app.py
  goto done
)

python -c "import sys; sys.exit(int(not sys.version_info.__ge__((3, 8))))" >nul 2>nul
if %errorlevel%==0 (
  python scripts\app.py
  goto done
)

echo Python 3.8 or newer was not found.
echo Install it from https://www.python.org/downloads/
echo During the install, tick "Add python.exe to PATH".
echo Then double-click this file again.

:done
echo.
pause
