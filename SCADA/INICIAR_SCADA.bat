@echo off
chcp 65001 > nul
title SCADA Industrial v2.0 - Llenado de Celdas
color 0B

echo ===============================================================================
echo     UTN Facultad Regional Parana - Tecnicatura Superior en Mecatronica
echo     Automatizacion Industrial - TP Integrador Parte 2 (PLC y SCADA)
echo     Alumno: Hugo Ariel Martinez - Proyecto PLC: Martinez.smbp
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando entorno de ejecucion...
where node >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Node.js no esta instalado o no se encuentra en el PATH del sistema.
    echo Por favor descargue e instale Node.js desde https://nodejs.org/
    echo.
    pause
    exit /b 1
)

if not exist "node_modules\" (
    echo [2/3] Instalando dependencias necesarias (primera ejecucion)...
    call npm install
    if %errorlevel% neq 0 (
        color 0C
        echo [ERROR] No se pudieron instalar las dependencias.
        pause
        exit /b 1
    )
) else (
    echo [2/3] Dependencias verificadas correctamente.
)

echo [3/3] Iniciando Gateway de Comunicaciones Modbus TCP / WebSocket...
echo.
echo -------------------------------------------------------------------------------
echo  - Servidor SCADA Web:   http://localhost:8080
echo  - Enlace Modbus TCP:    127.0.0.1:502 (Simulador Schneider M221)
echo                          127.0.0.1:5020 (PLC Virtual Integrado)
echo -------------------------------------------------------------------------------
echo.
echo Abriendo pantalla del SCADA en su navegador predeterminado...
start http://localhost:8080

echo.
echo Presione [Ctrl + C] en esta ventana cuando desee detener el sistema.
echo ===============================================================================
echo.

node server/gateway.js
pause
