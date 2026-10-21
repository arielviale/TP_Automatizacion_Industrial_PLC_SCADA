@echo off
chcp 65001 > nul
title Iniciando SCADA Industrial...
cd /d "%~dp0SCADA"
call INICIAR_SCADA.bat
