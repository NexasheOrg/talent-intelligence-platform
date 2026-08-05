@echo off
REM ===========================================================================
REM  Double-click this file to run the app. That is the whole instruction.
REM
REM  It checks what you have installed, starts everything, waits until it is
REM  actually ready, and opens the dashboard in your browser. If something is
REM  missing it tells you what to install and where to get it.
REM
REM  No terminal, no commands to memorise. If a black window appears, that is
REM  normal - read it, it is talking to you.
REM ===========================================================================

title Talent Intelligence Platform - starting

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start.ps1"

REM If PowerShell itself could not run, the script above never got to say why.
if errorlevel 1 (
  echo.
  echo   Something went wrong before the app could start.
  echo   Try double-clicking CHECK-MY-SETUP.bat - it explains what is missing.
  echo.
  pause
)
