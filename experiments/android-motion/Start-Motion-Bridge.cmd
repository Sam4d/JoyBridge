@echo off
cd /d "%~dp0"
echo JoyBridge Android Motion Lab - experimental, Just Dance Now unverified
JoyBridge-Motion-Lab.exe --check
if errorlevel 1 goto done
JoyBridge-Motion-Lab.exe --list
set /p "joybridge_device=Enter the numeric Joy-Con index shown above: "
rem Validate user input in PowerShell before passing it to the executable.
powershell -NoProfile -Command "if ($env:joybridge_device -notmatch '^\d{1,3}$') { exit 1 }; & '.\JoyBridge-Motion-Lab.exe' --device $env:joybridge_device; exit $LASTEXITCODE"
:done
pause
