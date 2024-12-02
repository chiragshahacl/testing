@echo off
call ".\scripts\build-windows-cmd.bat"

REM Execute the .exe file
start "" ".\dist\central-monitoring-desktop Setup 1.0.0.exe"