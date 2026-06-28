@echo off
title 2 - DAEMON RITXI / REACHY MINI
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp02_INICIAR_DAEMON_RITXI.ps1"
