@echo off
REM Install Node.js modules
call npm i

REM Build the Electron app
call npx electron-builder