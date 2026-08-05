@echo off
REM ===========================================================================
REM  Double-click this on your first day, or any time the app will not start.
REM
REM  It looks at what is installed on your laptop and prints a plain-English
REM  list of anything missing, with the link to install it. It changes nothing.
REM ===========================================================================

title Talent Intelligence Platform - checking your setup

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\check-setup.ps1"

if errorlevel 1 pause
