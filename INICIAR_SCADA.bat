@echo off
chcp 65001 > nul
title SCADA Industrial v2.0 - Llenado de Celdas
color 0B

if not exist "%~dp0SCADA\server\gateway.js" goto :ERR_ZIP

cd /d "%~dp0SCADA"

echo ===============================================================================
echo     UTN Facultad Regional Parana - Tecnicatura Superior en Mecatronica
echo     Automatizacion Industrial - TP Integrador Parte 2 - PLC y SCADA
echo     Alumno: Hugo Ariel Martinez - Proyecto PLC: Martinez.smbp
echo ===============================================================================
echo.

echo [1/3] Verificando entorno de ejecucion Node.js...
where node >nul 2>nul
if errorlevel 1 goto :ERR_NODE

if exist "node_modules\modbus-serial\" goto :DEPS_OK
echo [2/3] Instalando dependencias necesarias por primera vez...
call npm install --no-audit --no-fund
if errorlevel 1 goto :ERR_NPM
goto :START_SERVER

:DEPS_OK
echo [2/3] Dependencias verificadas correctamente.

:START_SERVER
echo [3/3] Iniciando Gateway de Comunicaciones Modbus TCP / WebSocket...
echo.
echo -------------------------------------------------------------------------------
echo  - Servidor SCADA Web:   http://localhost:8080
echo  - Enlace Modbus TCP:    127.0.0.1:5020 [PLC Virtual Integrado - Activo]
echo                          127.0.0.1:502  [Simulador Schneider M221]
echo -------------------------------------------------------------------------------
echo.
echo Abriendo automaticamente http://localhost:8080 en el navegador...
echo No cierre esta ventana mientras utilice el SCADA.
echo ===============================================================================
echo.

node server/gateway.js --open
echo.
pause
exit /b 0

:ERR_ZIP
color 0C
echo ===============================================================================
echo  [ERROR] No se encontro la carpeta "SCADA" junto a este archivo.
echo  Si descargo el proyecto en un archivo .ZIP desde GitHub, primero debe
echo  DESCOMPRIMIR / EXTRAER toda la carpeta antes de ejecutar INICIAR_SCADA.bat
echo ===============================================================================
echo.
pause
exit /b 1

:ERR_NODE
color 0C
echo [ERROR] Node.js no esta instalado o no se encuentra en el PATH del sistema.
echo Por favor descargue e instale Node.js desde https://nodejs.org/
echo.
pause
exit /b 1

:ERR_NPM
color 0C
echo [ERROR] No se pudieron instalar las dependencias de Node.js.
echo.
pause
exit /b 1
