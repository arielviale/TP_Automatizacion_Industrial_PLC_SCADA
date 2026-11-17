@echo off
chcp 65001 > nul
title Iniciando SCADA Industrial...

if not exist "%~dp0SCADA\server\gateway.js" (
    color 0C
    echo ===============================================================================
    echo  [ERROR] No se encontro la carpeta "SCADA" junto a este archivo.
    echo.
    echo  Si descargo el proyecto desde GitHub en un archivo .ZIP, primero debe
    echo  DESCOMPRIMIR / EXTRAER toda la carpeta en su computadora antes de hacer
    echo  doble clic en INICIAR_SCADA.bat.
    echo ===============================================================================
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0SCADA"
call INICIAR_SCADA.bat
