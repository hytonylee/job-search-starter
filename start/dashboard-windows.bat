@echo off
rem Double-click this file to open the job search dashboard (Windows).
rem It starts a small local server and opens the page in your browser.
rem Close this window, or press Ctrl+C in it, to stop the dashboard.

cd /d "%~dp0.."

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\app.py
  goto done
)

where python >nul 2>nul
if %errorlevel%==0 (
  python scripts\app.py
  goto done
)

echo Python 3 is not installed.
echo Install it from https://www.python.org/downloads/
echo During the install, tick "Add python.exe to PATH".
echo Then double-click this file again.

:done
echo.
pause
