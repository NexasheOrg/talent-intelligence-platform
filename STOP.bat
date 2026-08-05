@echo off
REM Double-click to stop the app. Safe to run even if nothing is running.

title Talent Intelligence Platform - stopping

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop.ps1"

if errorlevel 1 pause
