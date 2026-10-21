# -*- coding: utf-8 -*-
"""
Script generador del Informe Técnico Completo de Programación en Lenguaje LADDER (LD)
Trabajo Práctico Integrador — Parte 2: Programación de PLC y Supervisión SCADA
Carrera: Tecnicatura Superior en Mecatrónica — UTN Facultad Regional Paraná
Alumno: Hugo Ariel Martinez · Proyecto PLC: Martinez.smbp
"""

import os
import subprocess
import fitz

OUTPUT_HTML = os.path.abspath("Resolucion/programa_ladder.html")
OUTPUT_PDF = os.path.abspath("Resolucion/Programa_Ladder_Completo_TP_Integrador.pdf")

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Programa en Lenguaje Ladder (LD) — TP Integrador 2 — Hugo Ariel Martinez</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 11mm 13mm 13mm 13mm;
      @bottom-center {
        content: "UTN Paraná · Tecnicatura Superior en Mecatrónica · Automatización Industrial (TP Integrador 2)";
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 7.8pt;
        color: #64748b;
      }
      @bottom-right {
        content: "Pág. " counter(page);
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 8pt;
        font-weight: 700;
        color: #004b87;
      }
    }

    *, *::before, *::after {
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      font-size: 8.4pt;
      line-height: 1.35;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }

    /* Encabezado */
    .header-box {
      border-bottom: 2.5px solid #004b87;
      padding-bottom: 6px;
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }

    .inst-title {
      font-size: 10.8pt;
      font-weight: 800;
      color: #004b87;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      margin: 0 0 2px 0;
    }

    .inst-sub {
      font-size: 8.2pt;
      color: #475569;
      font-weight: 600;
      margin: 0;
    }

    .doc-meta {
      text-align: right;
      font-size: 7.8pt;
      color: #64748b;
      line-height: 1.25;
    }

    .doc-meta b {
      color: #0f172a;
    }

    .main-title {
      font-size: 13.5pt;
      font-weight: 900;
      color: #0f172a;
      margin: 5px 0 2px 0;
      letter-spacing: -0.2px;
      line-height: 1.22;
    }

    .main-subtitle {
      font-size: 9pt;
      color: #0284c7;
      font-weight: 700;
      margin: 0 0 10px 0;
    }

    /* Secciones */
    h2 {
      font-size: 10pt;
      font-weight: 800;
      color: #004b87;
      border-left: 3.5px solid #0284c7;
      padding-left: 7px;
      margin: 10px 0 6px 0;
      background: #f8fafc;
      padding-top: 3px;
      padding-bottom: 3px;
      page-break-after: avoid;
    }

    h3 {
      font-size: 9pt;
      font-weight: 700;
      color: #0f172a;
      margin: 8px 0 5px 0;
      page-break-after: avoid;
    }

    p {
      margin: 0 0 5px 0;
    }

    /* Tablas */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 7.8pt;
      margin: 4px 0 8px 0;
      page-break-inside: avoid;
    }

    th, td {
      border: 1px solid #cbd5e1;
      padding: 3.5px 6px;
      text-align: left;
    }

    th {
      background-color: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
    }

    tr:nth-child(even) {
      background-color: #f8fafc;
    }

    .mono {
      font-family: 'Consolas', 'Courier New', monospace;
      font-weight: 600;
      color: #004b87;
    }

    /* Bloques de Rung Ladder */
    .rung-card {
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      background: #ffffff;
      margin-bottom: 8px;
      page-break-inside: avoid;
      box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }

    .rung-header {
      background: #f1f5f9;
      border-bottom: 1px solid #cbd5e1;
      padding: 4px 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 8.2pt;
    }

    .rung-num {
      font-weight: 800;
      color: #004b87;
    }

    .rung-desc {
      font-weight: 600;
      color: #334155;
    }

    .rung-body {
      padding: 5px 8px;
    }

    .ladder-diagram {
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 7.7pt;
      line-height: 1.22;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 4px 8px;
      margin: 3px 0 4px 0;
      color: #0f172a;
      overflow-x: auto;
      white-space: pre;
    }

    .rung-explanation {
      font-size: 7.8pt;
      color: #475569;
      margin-top: 3px;
      line-height: 1.3;
    }

    .rung-explanation b {
      color: #1e293b;
    }

    .badge-il {
      display: inline-block;
      background: #e0f2fe;
      color: #0369a1;
      font-family: 'Consolas', monospace;
      font-size: 7.5pt;
      padding: 1px 5px;
      border-radius: 3px;
      border: 1px solid #bae6fd;
      margin-top: 3px;
    }

    /* Callouts */
    .callout {
      border-left: 3.5px solid #004b87;
      background: #f0f7ff;
      padding: 6px 10px;
      margin: 8px 0;
      font-size: 8.2pt;
      border-radius: 0 4px 4px 0;
    }

    .callout-warn {
      border-left-color: #f59e0b;
      background: #fffbeb;
    }

    .callout-title {
      font-weight: 700;
      color: #004b87;
      margin-bottom: 2px;
    }

    .callout-warn .callout-title {
      color: #b45309;
    }

    .page-break {
      page-break-before: always;
    }
  </style>
</head>
<body>

  <!-- ==================== PÁGINA 1: PORTADA Y CONFIGURACIÓN ==================== -->
  <div class="header-box">
    <div>
      <div class="inst-title">Universidad Tecnológica Nacional — Facultad Regional Paraná</div>
      <div class="inst-sub">Tecnicatura Superior en Mecatrónica · Cátedra de Automatización Industrial</div>
    </div>
    <div class="doc-meta">
      <b>DOCUMENTO TÉCNICO OFICIAL</b><br>
      Alumno: <b>Hugo Ariel Martinez</b><br>
      Archivo PLC: <b>Martinez.smbp</b><br>
      Fecha: <b>Octubre 2026</b> · Lenguaje: <b>Ladder (LD)</b>
    </div>
  </div>

  <div class="main-title">Programa Completo en Diagrama de Contactos (Ladder - IEC 61131-3)</div>
  <div class="main-subtitle">Automatización de la Línea de Llenado de Celdas de Cereal — Sector Mezcla y Limpieza de Trigo</div>

  <div class="callout">
    <div class="callout-title">MEMORIA TÉCNICA Y ESPECIFICACIÓN DEL PROGRAMA</div>
    El presente documento detalla la totalidad de los <b>51 rungs en lenguaje Ladder</b> que conforman el programa del PLC <b>Schneider Electric Modicon M221 (TM221CE24R)</b>, guardado en el archivo oficial <b><code>Martinez.smbp</code></b> y desarrollado en el entorno <b>EcoStruxure Machine Expert – Basic V1.4</b>.<br>
    Se adopta rigurosamente el criterio de <b>seguridad positiva (fail-safe)</b> para todas las señales críticas de campo (seta de parada de emergencia, contactos auxiliares de guardamotores y pulsador de parada en lógica cableada NC), prioridad absoluta a la desconexión ante fallas, y una arquitectura modular organizada en 7 tareas/secciones (POU).
  </div>

  <h2>1. Configuración de Hardware y Comunicaciones del PLC (Consigna 1.1)</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Parámetro / Módulo</th>
        <th style="width: 38%;">Configuración en Machine Expert Basic</th>
        <th style="width: 40%;">Justificación Técnica e Integración SCADA</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Modelo de Controlador</b></td>
        <td><span class="mono">TM221CE24R</span> (14 DI 24Vdc, 10 DO Relé)</td>
        <td>Controlador con puerto Ethernet RJ45 embebido y 2 entradas analógicas 0–10V.</td>
      </tr>
      <tr>
        <td><b>Puerto Ethernet (ETH1)</b></td>
        <td>Servidor Modbus TCP activo en puerto <span class="mono">502</span></td>
        <td>Permite la conexión directa y lectura/escritura en tiempo real del SCADA web.</td>
      </tr>
      <tr>
        <td><b>Entrada Analógica %IW0.0</b></td>
        <td>Tipo: <span class="mono">0-10 V</span> · Ámbito: <span class="mono">Normal (0..1000)</span></td>
        <td>Conectada al transmisor de presión diferencial del filtro PDT-01 (0..3000 Pa).</td>
      </tr>
      <tr>
        <td><b>Base de Tiempo Timers</b></td>
        <td><span class="mono">1 s</span> en todos los temporizadores (%TM0..%TM8)</td>
        <td>Garantiza resolución estándar y compatibilidad directa de lecturas Modbus.</td>
      </tr>
      <tr>
        <td><b>Contador %C0</b></td>
        <td>Tipo: <span class="mono">CTU</span> · Preset: <span class="mono">6</span></td>
        <td>Monitorea arranques del elevador M3 por ventana horaria (%TM8: 3600 s).</td>
      </tr>
    </tbody>
  </table>

  <h2>2. Convención Simbólica de Gráficos Ladder Utilizada</h2>
  <div style="display: flex; gap: 12px; margin-bottom: 12px;">
    <div style="flex: 1; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px 10px; background: #f8fafc; font-size: 8pt;">
      <b>Contactos y Rieles de Alimentación:</b><br>
      • <span class="mono">||</span> : Riel izquierdo (tensión) / derecho (retorno).<br>
      • <span class="mono">─┤ ├─</span> : Contacto Normalmente Abierto (NA).<br>
      • <span class="mono">─┤/├─</span> : Contacto Normalmente Cerrado (NC).<br>
      • <span class="mono">─┤P├─</span> : Contacto de Detección de Flanco Ascendente.
    </div>
    <div style="flex: 1; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px 10px; background: #f8fafc; font-size: 8pt;">
      <b>Bobinas y Bloques de Operación:</b><br>
      • <span class="mono">─( )─</span> : Bobina Estándar (directa).<br>
      • <span class="mono">─(S)─</span> / <span class="mono">─(R)─</span> : Bobinas de Enclavamiento (SET / RESET).<br>
      • <span class="mono">[ %MW0 := ... ]</span> : Bloque de Asignación / Operación Matemática.<br>
      • <span class="mono">[ %MW0 > 1500 ]</span> : Bloque de Comparación Aritmética.
    </div>
  </div>

  <h2>3. Tabla de Símbolos y Direccionamiento E/S</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 14%;">Dirección</th>
        <th style="width: 18%;">Símbolo</th>
        <th style="width: 48%;">Descripción Funcional del Elemento</th>
        <th style="width: 20%;">Tipo / Polaridad</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><span class="mono">%I0.0</span></td><td><span class="mono">PE_OK</span></td><td>Parada de emergencia en tablero local (seta)</td><td>NC (1 = Segura / OK)</td></tr>
      <tr><td><span class="mono">%I0.1</span></td><td><span class="mono">GM1_OK</span></td><td>Contacto auxiliar de guardamotor ventilador M1</td><td>NC (1 = Cerrado / OK)</td></tr>
      <tr><td><span class="mono">%I0.2</span></td><td><span class="mono">GM2_OK</span></td><td>Contacto auxiliar de guardamotor redler M2</td><td>NC (1 = Cerrado / OK)</td></tr>
      <tr><td><span class="mono">%I0.3</span></td><td><span class="mono">GM3_OK</span></td><td>Contacto auxiliar de guardamotor elevador M3</td><td>NC (1 = Cerrado / OK)</td></tr>
      <tr><td><span class="mono">%I0.4</span></td><td><span class="mono">GIRO_M3</span></td><td>Sensor inductivo de rotación en eje conducido elevador</td><td>NA (1 = Girando)</td></tr>
      <tr><td><span class="mono">%I0.5</span></td><td><span class="mono">LSH_C1</span></td><td>Sensor capacitivo de nivel máximo en Celda 1</td><td>NA (1 = Celda llena)</td></tr>
      <tr><td><span class="mono">%I0.6</span></td><td><span class="mono">LSH_C2</span></td><td>Sensor capacitivo de nivel máximo en Celda 2</td><td>NA (1 = Celda llena)</td></tr>
      <tr><td><span class="mono">%I0.7</span></td><td><span class="mono">PB_RESET</span></td><td>Pulsador físico de rearme / reset de fallas</td><td>NA (1 = Pulsado)</td></tr>
      <tr><td><span class="mono">%I0.8</span></td><td><span class="mono">PB_MARCHA</span></td><td>Pulsador físico de arranque local de la línea</td><td>NA (1 = Pulsado)</td></tr>
      <tr><td><span class="mono">%I0.9</span></td><td><span class="mono">PB_PARADA</span></td><td>Pulsador físico de parada normal local de la línea</td><td>NC (1 = Reposo / 0 = Pulsado)</td></tr>
      <tr><td><span class="mono">%Q0.0</span></td><td><span class="mono">KM1_ASPIR</span></td><td>Contactor de potencia de aspiración/limpieza M1</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%Q0.1</span></td><td><span class="mono">KM2_REDLER</span></td><td>Contactor de potencia de transportador redler M2</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%Q0.2</span></td><td><span class="mono">KM3_ELEV</span></td><td>Contactor de potencia de elevador de cangilones M3</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%Q0.3</span></td><td><span class="mono">YV1_C1</span></td><td>Electroválvula compuerta neumática Celda 1</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%Q0.4</span></td><td><span class="mono">YV2_C2</span></td><td>Electroválvula compuerta neumática Celda 2</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%Q0.5</span></td><td><span class="mono">BOCINA</span></td><td>Sirena acústica de aviso de pre-arranque (5 s)</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%Q0.6</span></td><td><span class="mono">BALIZA</span></td><td>Baliza luminosa (fija = advertencia / intermitente = alarma)</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%Q0.7</span></td><td><span class="mono">PILOTO_MARCHA</span></td><td>Piloto verde tablero (destello = arrancando / fijo = marcha)</td><td>Salida digital relé</td></tr>
      <tr><td><span class="mono">%IW0.0</span></td><td>—</td><td>Señal analógica de presión diferencial PDT-01 (0..10V)</td><td>Palabra de entrada (0..1000)</td></tr>
      <tr><td><span class="mono">%S6</span></td><td><span class="mono">RELOJ_1S</span></td><td>Generador interno de pulsos de reloj (base 1 s)</td><td>Bit del sistema Schneider</td></tr>
    </tbody>
  </table>

  <!-- ==================== PÁGINA 2: SECCIÓN 1 Y SECCIÓN 2 ==================== -->
  <div class="page-break"></div>

  <h2>Sección 1 (POU): Señales Generales del Sistema (Vida y Rearme)</h2>
  
  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 1.1</span>
      <span class="rung-desc">Generación de la Señal de Vida (Watchdog SCADA)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
      %S6                                         %M10
 ||----┤ ├----------------------------------------( )----||
    RELOJ_1S                                      VIDA</div>
      <div class="rung-explanation">
        <b>Funcionamiento:</b> Copia cíclicamente el pulso de 1 segundo de la base de tiempo del sistema (%S6) hacia el bit %M10. El SCADA monitorea las transiciones de este bit; si no varían en más de 3 segundos, se detecta pérdida de comunicación (Heartbeat Timeout).
      </div>
      <div class="badge-il">IL: LD %S6 &nbsp;|&nbsp; ST %M10</div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 1.2</span>
      <span class="rung-desc">Generación del Pulso Interno de Rearme (RESET_FALLAS)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
      %M42                                        %M50
 ||--+-┤ ├-+--------------------------------+-----( )----||
     |CMD_RESET                             |  RESET_FALLAS
     | %I0.7 |                              |     %M42
     +-┤P├---+                              +-----(R)----
      PB_RESET                                 CMD_RESET</div>
      <div class="rung-explanation">
        <b>Funcionamiento:</b> El bit interno %M50 se activa ante una orden de rearme enviada desde el SCADA (%M42) o por el flanco ascendente del pulsador físico local (%I0.7). Inmediatamente desenclava %M42 para retornar la orden remota a 0 en el mismo scan.
      </div>
      <div class="badge-il">IL: LD %M42 &nbsp;|&nbsp; ORR %I0.7 &nbsp;|&nbsp; ST %M50 &nbsp;|&nbsp; R %M42</div>
    </div>
  </div>

  <h2>Sección 2 (POU): Memorización y Rearme de Fallas de Seguridad</h2>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 2.1 y 2.2</span>
      <span class="rung-desc">Memorización y Rearme de Parada de Emergencia (AL_EMERG)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 2.1:
      %I0.0                                       %M20
 ||----┤/├----------------------------------------(S)----||
      PE_OK                                     AL_EMERG

Rung 2.2:
      %M50          %I0.0                         %M20
 ||----┤ ├-----------┤ ├--------------------------(R)----||
   RESET_FALLAS     PE_OK                       AL_EMERG</div>
      <div class="rung-explanation">
        <b>Seguridad Positiva:</b> Al accionarse la seta de emergencia (%I0.0 = 0), el contacto NC se cierra y enclava la alarma %M20 mediante SET. El rearme (RESET en 2.2) solo tiene éxito si el operario ya desenclavó físicamente la seta (%I0.0 = 1) y pulsa Rearme (%M50).
      </div>
      <div class="badge-il">IL 2.1: LDN %I0.0 &nbsp;|&nbsp; S %M20 &nbsp;&nbsp;&nbsp;&nbsp; IL 2.2: LD %M50 &nbsp;|&nbsp; AND %I0.0 &nbsp;|&nbsp; R %M20</div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 2.3 a 2.8</span>
      <span class="rung-desc">Protecciones Térmicas de Guardamotores M1, M2 y M3</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
M1:  LDN %I0.1 (GM1_OK)  ->  S %M21 (AL_M1)   |   LD %M50 AND %I0.1  ->  R %M21
M2:  LDN %I0.2 (GM2_OK)  ->  S %M22 (AL_M2)   |   LD %M50 AND %I0.2  ->  R %M22
M3:  LDN %I0.3 (GM3_OK)  ->  S %M23 (AL_M3)   |   LD %M50 AND %I0.3  ->  R %M23</div>
      <div class="rung-explanation">
        <b>Funcionamiento:</b> Idéntico esquema para los guardamotores térmicos. Si cualquiera se dispara (%I0.x = 0), se memoriza su alarma individual (%M21, %M22 o %M23). El rearme exige obligatoriamente haber rearmado la palanca física del guardamotor antes del pulso %M50.
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 2.9 a 2.11</span>
      <span class="rung-desc">Vigilancia de Deslizamiento o Rotura de Banda en Elevador M3 (%TM5)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 2.9:
      %Q0.2         %I0.4         +--------------+
 ||----┤ ├-----------┤/├----------| IN  %TM5   Q |----||
    KM3_ELEV       GIRO_M3        |  TON  5 s    |
                                  +--------------+
                                      T_GIRO
Rung 2.10: LD %TM5.Q -> S %M24 (AL_GIRO)
Rung 2.11: LD %M50 ANDN %TM5.Q -> R %M24</div>
      <div class="rung-explanation">
        <b>Lógica de Protección:</b> Si el contactor de M3 está energizado (%Q0.2 = 1) y el sensor inductivo en el tambor de retorno indica ausencia de rotación (%I0.4 = 0), el temporizador TON %TM5 temporiza 5 segundos de gracia. Si persiste, enclava la falla crítica AL_GIRO (%M24).
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 2.12</span>
      <span class="rung-desc">Concentrador General de Alarmas (FALLA_GRAL)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
      %M20                                        %M30
 ||--+-┤ ├-----+----------------------------------( )----||
     |AL_EMERG |                               FALLA_GRAL
     | %M21    |
     +-┤ ├-----+  (%M21 AL_M1 / %M22 AL_M2 / %M23 AL_M3)
     |         |
     | %M24    |
     +-┤ ├-----+  (%M24 AL_GIRO / %M25 AL_DP_MUY_ALTA)
     AL_DP_MUY_ALTA</div>
      <div class="rung-explanation">
        <b>Funcionamiento:</b> Función lógica OR de todas las anomalías que obligan a detener inmediatamente la línea productiva y anular el permiso de arranque.
      </div>
      <div class="badge-il">IL: LD %M20 &nbsp;|&nbsp; OR %M21 &nbsp;|&nbsp; OR %M22 &nbsp;|&nbsp; OR %M23 &nbsp;|&nbsp; OR %M24 &nbsp;|&nbsp; OR %M25 &nbsp;|&nbsp; ST %M30</div>
    </div>
  </div>

  <!-- ==================== PÁGINA 3: SECCIÓN 3 Y SECCIÓN 4 ==================== -->
  <div class="page-break"></div>

  <h2>Sección 3 (POU): Validación de Celdas de Destino y Permiso de Marcha</h2>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 3.1 a 3.4</span>
      <span class="rung-desc">Validación de Celda (%MW10) y Detección de Nivel Alto</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 3.1: LD [%MW10 = 1] OR [%MW10 = 2] -> ST %M53 (CELDA_VALIDA)
Rung 3.2:
                         %I0.5
 ||--+-[ %MW10 = 1 ]------┤ ├----+----------------( )----||
     |                  LSH_C1   |             DESTINO_LLENO
     |                   %I0.6   |                %M52
     +-[ %MW10 = 2 ]------┤ ├----+
                        LSH_C2
Rung 3.3: LD %I0.5 -> ST %M27 (AV_C1_LLENA)
Rung 3.4: LD %I0.6 -> ST %M28 (AV_C2_LLENA)</div>
      <div class="rung-explanation">
        <b>Enclavamiento Operativo:</b> Se valida que el registro %MW10 contenga un destino admisible (1 o 2). Si la celda seleccionada tiene su sensor capacitivo activo (LSH_C1 o LSH_C2), se activa DESTINO_LLENO (%M52), bloqueando el arranque y disparando la parada normal.
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 3.5 y 3.6</span>
      <span class="rung-desc">Control de Compuertas Neumáticas de Selección (YV1_C1 / YV2_C2)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
                         %M20                     %Q0.3
 ||----[ %MW10 = 1 ]------┤/├---------------------( )----||
                       AL_EMERG                   YV1_C1

                         %M20                     %Q0.4
 ||----[ %MW10 = 2 ]------┤/├---------------------( )----||
                       AL_EMERG                   YV2_C2</div>
      <div class="rung-explanation">
        <b>Lógica de Posicionamiento:</b> Abre la compuerta neumática hacia la celda preseleccionada siempre que no exista parada de emergencia activa (%M20 = 0).
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 3.7</span>
      <span class="rung-desc">Condición Maestra de Permiso de Arranque (PERMISO)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
      %I0.0      %M30        %M53        %M52        %M9
 ||----┤ ├--------┤/├---------┤ ├---------┤/├--------( )----||
      PE_OK    FALLA_GRAL  CELDA_VALIDA DESTINO_LLENO PERMISO</div>
      <div class="rung-explanation">
        <b>Condición Integral:</b> Se concede permiso de marcha (%M9 = 1) únicamente si la seta está en reposo (%I0.0=1), no hay fallas térmicas o mecánicas (%M30=0), se ha definido una celda válida (%M53=1) y dicha celda no se encuentra llena (%M52=0).
      </div>
      <div class="badge-il">IL: LD %I0.0 &nbsp;|&nbsp; ANDN %M30 &nbsp;|&nbsp; AND %M53 &nbsp;|&nbsp; ANDN %M52 &nbsp;|&nbsp; ST %M9</div>
    </div>
  </div>

  <h2>Sección 4 (POU): Lógica de Marcha, Parada y Cadena de Tiempos</h2>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 4.1 y 4.2</span>
      <span class="rung-desc">Enclavamiento Maestro de Línea (LINEA) — Prioridad a la Desconexión</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 4.1 (SET LINEA):
      %M40                    %M9                 %M5
 ||--+-┤ ├-----+---------------┤ ├----------------(S)----||
     |CMD_MARCHA|            PERMISO              LINEA
     | %I0.8    |
     +-┤P├------+
      PB_MARCHA

Rung 4.2 (RESET LINEA):
      %M41                                        %M5
 ||--+-┤ ├------+---------------------------------(R)----||
     |CMD_PARADA|                                 LINEA
     | %I0.9    |
     +-┤/├------+
     |PB_PARADA |  (%M52 DESTINO_LLENO / %M30 FALLA_GRAL)
     +-┤ ├------+</div>
      <div class="rung-explanation">
        <b>Prioridad de Seguridad:</b> El Rung 4.2 (RESET) se procesa inmediatamente después del Rung 4.1 (SET). Por lo tanto, si la orden de marcha y parada coinciden en el mismo ciclo de scan, <b>siempre prevalece la parada</b>. La apertura del pulsador NC (%I0.9=0), celda llena (%M52) o falla (%M30) cortan la línea instantáneamente.
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 4.3 a 4.8</span>
      <span class="rung-desc">Temporizadores de Pre-arranque, Arranque Escalonado y Vaciado</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 4.4: LD %M5           -> %TM0 (TP  5 s)  T_BOCINA   (Aviso acústico previo)
Rung 4.5: LD %M5 AND %Q0.0 -> %TM1 (TON 5 s)  T_ARR_M2   (Espera arrancar M1 para M2)
Rung 4.6: LD %M5 AND %Q0.1 -> %TM2 (TON 5 s)  T_ARR_M3   (Espera arrancar M2 para M3)
Rung 4.7: LD %Q0.2          -> %TM3 (TOF 20 s) T_VACIADO  (M2 sigue 20 s tras parar M3)
Rung 4.8: LD %Q0.1          -> %TM4 (TOF 30 s) T_BARRIDO  (M1 sigue 30 s tras parar M2)</div>
      <div class="rung-explanation">
        <b>Secuencia Temporal:</b>
        • <b>Arranque:</b> %TM0 suena la bocina durante 5s; al caer %TM0.Q arranca M1. A los 5s de M1 arranca M2 (%TM1). A los 5s de M2 arranca M3 (%TM2).
        • <b>Parada:</b> Al cortar LINEA, M3 cae inmediatamente. %TM3 (TOF) mantiene el redler M2 por 20 s para vaciar el grano transportado. Al caer M2, %TM4 (TOF) mantiene la aspiración M1 por 30 s para limpiar polvillo en suspensión.
      </div>
    </div>
  </div>

  <!-- ==================== PÁGINA 4: SECCIÓN 5 Y SECCIÓN 6 ==================== -->
  <div class="page-break"></div>

  <h2>Sección 5 (POU): Gobierno de Salidas Físicas a Contactores</h2>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 5.1</span>
      <span class="rung-desc">Gobierno del Contactor de Aspiración M1 (%Q0.0 - KM1_ASPIR)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
     %I0.0   %M20    %I0.1   %M21       %M5     %TM0.Q          %Q0.0
 ||---┤ ├-----┤/├-----┤ ├-----┤/├---+----┤ ├------┤/├-----+-----( )----||
     PE_OK  AL_EMERG GM1_OK  AL_M1  |   LINEA   T_BOCINA  |   KM1_ASPIR
                                    |       %TM4.Q        |
                                    +--------┤ ├----------+
                                          T_BARRIDO</div>
      <div class="rung-explanation">
        <b>Lógica de Protección y Marcha:</b> Protegido en serie por seta de emergencia (%I0.0 y %M20) y guardamotor M1 (%I0.1 y %M21). Energiza si LINEA está activa y terminó la bocina (%TM0.Q=0), o bien durante la retención del barrido de parada (%TM4.Q=1).
      </div>
      <div class="badge-il">IL: LD %I0.0 &nbsp;|&nbsp; ANDN %M20 &nbsp;|&nbsp; AND %I0.1 &nbsp;|&nbsp; ANDN %M21 &nbsp;|&nbsp; AND( %M5 ANDN %TM0.Q OR %TM4.Q ) &nbsp;|&nbsp; ST %Q0.0</div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 5.2</span>
      <span class="rung-desc">Gobierno del Contactor del Transportador Redler M2 (%Q0.1 - KM2_REDLER)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
     %I0.0   %M20    %I0.2   %M22       %M5     %TM1.Q          %Q0.1
 ||---┤ ├-----┤/├-----┤ ├-----┤/├---+----┤ ├------┤ ├-----+-----( )----||
     PE_OK  AL_EMERG GM2_OK  AL_M2  |   LINEA   T_ARR_M2  |   KM2_REDLER
                                    |   %Q0.1   %TM3.Q    |
                                    +----┤ ├------┤ ├-----+
                                      KM2_REDLER T_VACIADO</div>
      <div class="rung-explanation">
        <b>Lógica de Operación:</b> Protegido por PE y guardamotor M2. Entra a los 5 s de estar M1 en marcha (%TM1.Q=1). Durante la parada normal, se autosostiene con su propio contacto %Q0.1 en serie con %TM3.Q (TOF 20 s de vaciado).
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 5.3</span>
      <span class="rung-desc">Gobierno del Contactor del Elevador de Cangilones M3 (%Q0.2 - KM3_ELEV)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
   %I0.0  %M20   %I0.3  %M23   %M24   %Q0.1      %M5   %TM2.Q        %Q0.2
 ||-┤ ├----┤/├----┤ ├----┤/├----┤/├----┤ ├--------┤ ├----┤ ├----------( )----||
   PE_OK AL_EMERG GM3_OK AL_M3 AL_GIRO KM2_REDLER LINEA T_ARR_M3     KM3_ELEV</div>
      <div class="rung-explanation">
        <b>Cadena de Seguridad:</b> No tiene retención de vaciado. Requiere en serie: Seta OK, Guardamotor M3 OK, Sensor de Giro OK (%M24=0), Redler M2 en marcha (%Q0.1=1), LINEA activa y temporizador de retardo cumplido (%TM2.Q=1). Se apaga inmediatamente ante cualquier parada.
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 5.4</span>
      <span class="rung-desc">Accionamiento de la Bocina de Pre-arranque (%Q0.5 - BOCINA)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
      %M5          %TM0.Q                         %Q0.5
 ||----┤ ├-----------┤ ├--------------------------( )----||
      LINEA       T_BOCINA                        BOCINA</div>
      <div class="rung-explanation">
        <b>Aviso al Personal:</b> Suena de manera ininterrumpida durante los primeros 5 segundos de iniciada la secuencia de arranque.
      </div>
    </div>
  </div>

  <h2>Sección 6 (POU): Presión Diferencial PDT-01 y Contador de Arranques M3</h2>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 6.1 a 6.6</span>
      <span class="rung-desc">Escalado Analógico y Alarmas del Filtro de Mangas (%IW0.0 / %MW0)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 6.1: LD 1 -> [ %MW0 := %IW0.0 * 3 ]  (Escalado 0..1000 pts a 0..3000 Pa)
Rung 6.2: LD [ %MW0 > 1500 ] -> %TM6 (TON 10 s) T_DP_ALTA
Rung 6.3: LD %TM6.Q          -> ST %M26 (AV_DP_ALTA - Advertencia Filtro Colmatado)
Rung 6.4: LD [ %MW0 > 2000 ] -> %TM7 (TON 10 s) T_DP_MUY_ALTA
Rung 6.5: LD %TM7.Q          -> S %M25 (AL_DP_MUY_ALTA - Falla Crítica)
Rung 6.6: LD %M50 ANDN %TM7.Q -> R %M25 (Rearme seguro tras normalizar presión)</div>
      <div class="rung-explanation">
        <b>Filtro de Ruido y Estabilidad:</b> El multiplicador lineal por 3 escala con precisión la palabra analógica. Los temporizadores TON de 10 s evitan disparos intempestivos debidos a turbulencias transitorias de aire al encender el extractor M1.
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 6.7 a 6.10</span>
      <span class="rung-desc">Contador de Arranques Horarios del Elevador M3 (%C0 / %TM8)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 6.7: LDN %TM8.Q -> %TM8 (TON 3600 s) T_HORA (Ventana cíclica de 1 hora)
Rung 6.8:
      %TM8.Q        +-----------------+
 ||----┤ ├---------| R   %C0         |
      T_HORA        |                 |
      %Q0.2         |  CTU  P = 6     |
 ||----┤ ├---------| CU            D |----||
     KM3_ELEV       +-----------------+
                        C_ARRANQUES
Rung 6.9:  LD [ %C0.V >= 6 ] -> ST %M29 (AV_ARRANQUES - Advertencia de fatiga de motor)
Rung 6.10: LD 1              -> [ %MW1 := %C0.V ] (Telemetría para el SCADA)</div>
      <div class="rung-explanation">
        <b>Protección del Motor del Elevador:</b> La entrada de conteo ascendente (CU) detecta el flanco de subida de %Q0.2 en cada partida. Si se alcanzan 6 arranques en menos de una hora, se enciende la advertencia %M29 y la baliza amarilla. Al cumplirse la hora, %TM8.Q genera un pulso de un solo scan que resetea el contador a 0.
      </div>
    </div>
  </div>

  <!-- ==================== PÁGINA 5: SECCIÓN 7 Y CONCLUSIONES ==================== -->
  <div class="page-break"></div>

  <h2>Sección 7 (POU): Señalización en Tablero Local y Espejo SCADA</h2>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 7.1</span>
      <span class="rung-desc">Comando de la Baliza Luminosa (%Q0.6 - BALIZA)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
      %M30          %S6                           %Q0.6
 ||--+-┤ ├-----------┤ ├-------------+------------( )----||
     |FALLA_GRAL  RELOJ_1S           |            BALIZA
     |                               |
     |  %M30       %M26              |
     +--┤/├----+----┤ ├--------+-----+
     FALLA_GRAL|  AV_DP_ALTA   |
               |   %M27        |
               +----┤ ├--------+  (%M27 C1 / %M28 C2 / %M29 Arranques)</div>
      <div class="rung-explanation">
        <b>Discriminación de Severidad:</b>
        • <b>Intermitente (1 Hz):</b> Si hay cualquier falla crítica (%M30 = 1 en serie con %S6).
        • <b>Fija continua:</b> Si no hay falla crítica (%M30 = 0) pero existe algún aviso activo (filtro colmatado, celda llena o exceso de arranques).
      </div>
      <div class="badge-il">IL: LD %M30 AND %S6 &nbsp;|&nbsp; OR( ( %M26 OR %M27 OR %M28 OR %M29 ) ANDN %M30 ) &nbsp;|&nbsp; ST %Q0.6</div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNG 7.2</span>
      <span class="rung-desc">Comando del Piloto Verde de Marcha (%Q0.7 - PILOTO_MARCHA)</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
      %M5          %Q0.2                          %Q0.7
 ||----┤ ├------+---┤ ├----+----------------------( )----||
      LINEA     | KM3_ELEV |                  PILOTO_MARCHA
                |   %S6    |
                +---┤ ├----+
                  RELOJ_1S</div>
      <div class="rung-explanation">
        <b>Estados del Piloto Verde:</b>
        • <b>Apagado:</b> Línea parada (%M5 = 0).
        • <b>Intermitente (1 Hz):</b> Secuencia de arranque en curso (LINEA activa pero M3 aún no arrancó).
        • <b>Fijo encendido:</b> Línea en régimen permanente (LINEA activa y M3 en marcha).
      </div>
    </div>
  </div>

  <div class="rung-card">
    <div class="rung-header">
      <span class="rung-num">RUNGS 7.3 a 7.8</span>
      <span class="rung-desc">Mapeo de Estados de Salidas a Memoria Interna para Supervisión SCADA</span>
    </div>
    <div class="rung-body">
      <div class="ladder-diagram">
Rung 7.3: LD %Q0.0 -> ST %M0 (EST_M1)     |   Rung 7.6: LD %Q0.3 -> ST %M3 (EST_YV1)
Rung 7.4: LD %Q0.1 -> ST %M1 (EST_M2)     |   Rung 7.7: LD %Q0.4 -> ST %M4 (EST_YV2)
Rung 7.5: LD %Q0.2 -> ST %M2 (EST_M3)     |   Rung 7.8: LD %Q0.5 -> ST %M6 (EST_BOCINA)</div>
      <div class="rung-explanation">
        <b>Aislamiento Modbus:</b> Copia el estado físico de los actuadores hacia las marcas internas %M solicitadas en la consigna para ser leídas por el SCADA sin interferir con las salidas físicas.
      </div>
    </div>
  </div>

  <h2>4. Criterios de Calidad y Buenas Prácticas de Programación Ladder</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 30%;">Principio de Ingeniería</th>
        <th style="width: 70%;">Implementación en el Proyecto Martinez.smbp</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Unicidad de Bobinas Simples</b></td>
        <td>Ninguna salida digital (%Q0.0..%Q0.7) ni marca interna simple (%M0..%M10, %M26..%M30) aparece asignada más de una vez con bobina directa <span class="mono">-( )-</span>, evitando fallas por sobreescritura de ciclo de scan.</td>
      </tr>
      <tr>
        <td><b>Prioridad a la Desconexión</b></td>
        <td>En todas las biestables (LINEA y Alarmas), los rungs con instrucciones <span class="mono">-(R)-</span> se ubican con posterioridad lógica respecto a los <span class="mono">-(S)-</span>, asegurando que ante comandos simultáneos siempre gane el corte seguro.</td>
      </tr>
      <tr>
        <td><b>Rearme Condicionado</b></td>
        <td>Las fallas de emergencia, térmicos y presión no pueden ser rearmadas si la causa física de la anomalía continúa presente en planta, eliminando el riesgo de reconexiones sobre falla.</td>
      </tr>
      <tr>
        <td><b>Trazabilidad y Símbolos</b></td>
        <td>El 100% de las variables operativas cuenta con símbolo unívoco y comentario normalizado, permitiendo un mantenimiento ágil y un enlace Modbus inmediato.</td>
      </tr>
    </tbody>
  </table>

  <!-- Bloque de Firmas -->
  <table style="margin-top: 25px; border: none; page-break-inside: avoid;">
    <tr style="background: none;">
      <td style="border: none; width: 50%; text-align: center; padding-top: 25px;">
        <div style="border-top: 1.5px solid #94a3b8; width: 75%; margin: 0 auto; padding-top: 4px;">
          <b>Hugo Ariel Martinez</b><br>
          Alumno — Tecnicatura Superior en Mecatrónica<br>
          Proyecto PLC: <i>Martinez.smbp</i> · UTN FRP
        </div>
      </td>
      <td style="border: none; width: 50%; text-align: center; padding-top: 25px;">
        <div style="border-top: 1.5px solid #94a3b8; width: 75%; margin: 0 auto; padding-top: 4px;">
          <b>Cátedra de Automatización Industrial</b><br>
          Evaluación de Programación PLC & SCADA<br>
          Año Académico 2026
        </div>
      </td>
    </tr>
  </table>

</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML Ladder generado exitosamente: {OUTPUT_HTML}")

# Renderizar a PDF mediante Microsoft Edge en modo Headless
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    f"file:///{OUTPUT_HTML.replace(os.sep, '/')}"
]

print("Compilando PDF con Microsoft Edge...")
result = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(OUTPUT_PDF):
    file_size = os.path.getsize(OUTPUT_PDF)
    doc = fitz.open(OUTPUT_PDF)
    num_pages = len(doc)
    print(f"PDF generado con éxito: {OUTPUT_PDF}")
    print(f"Páginas: {num_pages} · Tamaño: {file_size / 1024:.1f} KB")
else:
    print("Error al generar el PDF:", result.stderr)
