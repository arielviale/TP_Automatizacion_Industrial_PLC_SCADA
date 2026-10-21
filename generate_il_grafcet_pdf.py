# -*- coding: utf-8 -*-
"""
Generador del Documento Oficial de Lista de Instrucciones (IL) y Modelado GRAFCET (6 Páginas Calibradas)
Trabajo Práctico Integrador — Parte 2: Programación de PLC Modicon M221
Tecnicatura Superior en Mecatrónica — UTN Facultad Regional Paraná
"""

import os
import subprocess
import fitz

OUTPUT_HTML = os.path.abspath("Resolucion/lista_instrucciones_grafcet.html")
OUTPUT_PDF = os.path.abspath("Resolucion/Lista_de_Instrucciones_y_Grafcet_TP_Integrador.pdf")

html_content = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Lista de Instrucciones (IL) y Modelado GRAFCET — TP Integrador 2</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 11mm 12mm 13mm 12mm;
      @bottom-left {
        content: "UTN Paraná · Mecatrónica — Automatización Industrial (Lista de Instrucciones & GRAFCET)";
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 7.2pt;
        color: #64748b;
      }
      @bottom-right {
        content: "Página " counter(page) " de 6";
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 7.5pt;
        font-weight: 700;
        color: #004b87;
      }
    }

    *, *::before, *::after {
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      font-size: 8.1pt;
      line-height: 1.33;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }

    .page {
      width: 100%;
      height: 272mm;
      max-height: 272mm;
      overflow: hidden;
      page-break-after: always;
      break-after: page;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
    }

    .page:last-child {
      page-break-after: auto;
      break-after: auto;
    }

    /* Encabezado Principal */
    .header-box {
      border-bottom: 2.5px solid #004b87;
      padding-bottom: 5px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }

    .inst-title {
      font-size: 10.5pt;
      font-weight: 800;
      color: #004b87;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      margin: 0 0 1px 0;
    }

    .inst-sub {
      font-size: 7.8pt;
      color: #475569;
      font-weight: 600;
      margin: 0;
    }

    .doc-meta {
      text-align: right;
      font-size: 7.4pt;
      color: #64748b;
      line-height: 1.25;
    }

    .doc-meta b {
      color: #0f172a;
    }

    /* Encabezado Secundario */
    .running-header {
      border-bottom: 1.5px solid #cbd5e1;
      padding-bottom: 4px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      font-size: 7.2pt;
      color: #64748b;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }

    .running-header b {
      color: #004b87;
    }

    /* Títulos */
    h1 {
      font-size: 11.8pt;
      font-weight: 800;
      color: #003366;
      margin: 0 0 6px 0;
      padding-bottom: 2px;
      border-bottom: 1.5px solid #004b87;
      line-height: 1.2;
    }

    h2 {
      font-size: 9.3pt;
      font-weight: 700;
      color: #0f172a;
      margin: 6px 0 3px 0;
      background: #f1f5f9;
      padding: 2.5px 7px;
      border-left: 3.5px solid #004b87;
      border-radius: 0 3px 3px 0;
    }

    h3 {
      font-size: 8.3pt;
      font-weight: 700;
      color: #004b87;
      margin: 4px 0 2px 0;
    }

    p {
      margin: 0 0 4px 0;
    }

    /* Tablas */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 7.4pt;
      margin-bottom: 5px;
    }

    th {
      background: #004b87;
      color: #ffffff;
      font-weight: 600;
      text-align: left;
      padding: 3px 5px;
      border: 1px solid #003560;
      font-size: 7.2pt;
    }

    td {
      padding: 2.5px 5px;
      border: 1px solid #cbd5e1;
      vertical-align: middle;
    }

    tr:nth-child(even) td {
      background-color: #f8fafc;
    }

    /* Badges */
    .badge {
      display: inline-block;
      padding: 1px 4.5px;
      border-radius: 3px;
      font-size: 6.8pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      white-space: nowrap;
    }

    .badge-ok {
      background: #dcfce7;
      color: #15803d;
      border: 1px solid #86efac;
    }

    .badge-tag {
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      font-family: 'Consolas', monospace;
    }

    .badge-grafcet {
      background: #f3e8ff;
      color: #6b21a8;
      border: 1px solid #d8b4fe;
      font-family: 'Consolas', monospace;
    }

    /* Callouts */
    .callout {
      background: #f0f7ff;
      border: 1px solid #b9d7ea;
      border-left: 3.5px solid #004b87;
      padding: 4px 7px;
      margin-bottom: 5px;
      border-radius: 0 3px 3px 0;
      font-size: 7.6pt;
    }

    .callout-title {
      font-weight: 700;
      color: #004b87;
      margin-bottom: 1.5px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .callout-success {
      background: #f0fdf4;
      border-color: #bbf7d0;
      border-left-color: #16a34a;
    }
    .callout-success .callout-title {
      color: #16a34a;
    }

    .callout-alert {
      background: #fffbeb;
      border-color: #fde68a;
      border-left-color: #d97706;
    }
    .callout-alert .callout-title {
      color: #d97706;
    }

    /* Grillas */
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      margin-bottom: 5px;
    }

    .card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 3px;
      padding: 4px 6px;
    }

    .card-title {
      font-weight: 700;
      font-size: 7.7pt;
      color: #0f172a;
      margin-bottom: 2px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 2px;
    }

    code {
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 7.4pt;
      background: #f1f5f9;
      padding: 0.5px 3px;
      border-radius: 2px;
      color: #0f172a;
    }

    /* Banner Portada */
    .cover-banner {
      background: linear-gradient(135deg, #002d5a 0%, #004b87 60%, #0284c7 100%);
      color: white;
      padding: 11px 14px;
      border-radius: 4px;
      margin-bottom: 7px;
    }

    .cover-title {
      font-size: 13.5pt;
      font-weight: 800;
      margin: 0 0 3px 0;
      line-height: 1.15;
    }

    .cover-subtitle {
      font-size: 8.5pt;
      color: #e0f2fe;
      margin: 0 0 5px 0;
      line-height: 1.3;
    }

    .cover-badge-row {
      display: flex;
      gap: 6px;
    }

    .cover-pill {
      background: rgba(255, 255, 255, 0.18);
      border: 1px solid rgba(255, 255, 255, 0.35);
      color: #ffffff;
      font-size: 6.8pt;
      padding: 1.5px 6px;
      border-radius: 10px;
      font-weight: 600;
    }

    /* Bloques de código IL */
    .il-block {
      background: #0f172a;
      color: #e2e8f0;
      font-family: 'Consolas', monospace;
      font-size: 7.1pt;
      line-height: 1.25;
      padding: 4px 6px;
      border-radius: 3px;
      margin: 2px 0;
      border-left: 3px solid #38bdf8;
    }

    .il-kw { color: #38bdf8; font-weight: 700; }
    .il-var { color: #fde047; }
    .il-com { color: #94a3b8; font-style: italic; }

    /* Rung Item en Tabla */
    .rung-row td {
      padding: 2px 4px;
    }

    .rung-num {
      font-weight: 800;
      color: #004b87;
      font-family: 'Consolas', monospace;
      font-size: 7.3pt;
      text-align: center;
    }

    /* Grafcet styling */
    .grafcet-step {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border: 1.8px solid #004b87;
      font-weight: 800;
      background: #ffffff;
      color: #004b87;
      font-size: 8.5pt;
    }

    .grafcet-step-init {
      border: 3.5px double #004b87;
      background: #eff6ff;
    }

    .grafcet-trans {
      display: flex;
      align-items: center;
      margin: 3px 0 3px 12px;
      font-size: 7.2pt;
    }

    .grafcet-bar {
      width: 14px;
      height: 2px;
      background: #004b87;
      margin-right: 6px;
    }

    .grafcet-action {
      background: #f8fafc;
      border: 1.5px solid #004b87;
      padding: 2px 6px;
      margin-left: 6px;
      border-radius: 2px;
      font-size: 7.3pt;
      font-weight: 600;
    }

    .text-center { text-align: center; }
    .text-right { text-align: right; }
    .bold { font-weight: 700; }
  </style>
</head>
<body>

  <!-- =================================================================== -->
  <!-- PÁGINA 1: PORTADA & FUNDAMENTOS DE LISTA DE INSTRUCCIONES (IL)     -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="header-box">
      <div>
        <div class="inst-title">Universidad Tecnológica Nacional — Facultad Regional Paraná</div>
        <div class="inst-sub">Tecnicatura Superior en Mecatrónica · Cátedra de Automatización Industrial</div>
      </div>
      <div class="doc-meta">
        <b>DOCUMENTO TÉCNICO OFICIAL</b><br>
        Alumno: <b>Hugo Ariel Martinez</b><br>
        Proyecto: <b>Martinez.smbp</b> · Año 2026
      </div>
    </div>

    <div class="cover-banner">
      <div class="cover-title">Guía Integral: Lista de Instrucciones (IL) y Modelado GRAFCET</div>
      <div class="cover-subtitle">
        Desglose exhaustivo del programa del PLC en lenguaje de Lista de Instrucciones (Instruction List) para los 51 rungs de las 7 secciones normalizadas, junto con la modelización formal del automatismo en diagrama GRAFCET (SFC) según normas internacionales.
      </div>
      <div class="cover-badge-row">
        <span class="cover-pill">✓ Software: EcoStruxure Machine Expert Basic</span>
        <span class="cover-pill">✓ 51 Rungs en IL</span>
        <span class="cover-pill">✓ Grafcet Nivel 1 y 2</span>
        <span class="cover-pill">✓ Norma IEC 61131-3 / IEC 60848</span>
      </div>
    </div>

    <div class="callout callout-success">
      <div class="callout-title">
        <span>📘</span> Los Tres Lenguajes del EcoStruxure Machine Expert – Basic
      </div>
      Tal como especifica la documentación oficial del controlador Modicon M221 TM221CE24R, el entorno de programación admite tres lenguajes: <b>Diagrama de Contactos (Ladder - LD)</b>, <b>Lista de Instrucciones (Instruction List - IL)</b> y <b>GRAFCET (Sequential Function Chart - SFC)</b>. Si bien la cátedra solicitó el desarrollo en Ladder, la Lista de Instrucciones constituye el lenguaje de máquina intermedio nativo de la CPU, y el botón <i>Ladder/IL</i> del software permite conmutar instantáneamente cada rung para su verificación técnica.
    </div>

    <h2>1. Mnemónicos y Estructura del Lenguaje Lista de Instrucciones (IL)</h2>
    <p style="font-size: 7.7pt; margin-bottom: 4px;">
      El lenguaje IL es un lenguaje textual de bajo nivel basado en un <b>acumulador lógico booleano</b>. Cada línea ejecuta una operación cargando o combinando operandos con el resultado previo.
    </p>

    <table>
      <thead>
        <tr>
          <th style="width: 14%;">Mnemónico</th>
          <th style="width: 25%;">Equivalente en Ladder</th>
          <th style="width: 38%;">Descripción de la Operación Booleana</th>
          <th style="width: 23%;">Ejemplo en M221</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>LD</code> / <code>LDN</code></td>
          <td>Contacto NA / Contacto NC</td>
          <td>Carga el valor del bit (o su negación) en el acumulador booleano</td>
          <td><code>LD %I0.0</code> / <code>LDN %I0.1</code></td>
        </tr>
        <tr>
          <td><code>LDR</code> / <code>LDF</code></td>
          <td>Flanco ascendente / descendente</td>
          <td>Carga un pulso de un ciclo de scan ante flanco (Rising / Falling)</td>
          <td><code>LDR %I0.8</code> (↑PB_MARCHA)</td>
        </tr>
        <tr>
          <td><code>AND</code> / <code>ANDN</code></td>
          <td>Contactos en serie NA / NC</td>
          <td>Operación Y lógica entre el acumulador y la variable indicada</td>
          <td><code>AND %M9</code> / <code>ANDN %M30</code></td>
        </tr>
        <tr>
          <td><code>OR</code> / <code>ORN</code></td>
          <td>Ramas en paralelo NA / NC</td>
          <td>Operación O lógica entre el acumulador y la variable indicada</td>
          <td><code>OR %M40</code> / <code>ORN %I0.9</code></td>
        </tr>
        <tr>
          <td><code>ORR</code> / <code>ORF</code></td>
          <td>Flanco en paralelo</td>
          <td>Operación O lógica con un pulso por flanco de entrada física</td>
          <td><code>ORR %I0.7</code> (↑PB_RESET)</td>
        </tr>
        <tr>
          <td><code>AND(</code> / <code>OR(</code> ... <code>)</code></td>
          <td>Agrupación / ramas complejas</td>
          <td>Abre un subacumulador para resolver paréntesis antes de combinar</td>
          <td><code>AND( %M5 ... )</code></td>
        </tr>
        <tr>
          <td><code>ST</code></td>
          <td>Bobina simple <code>( )</code></td>
          <td>Guarda el acumulador en la variable (Store) sin modificarlo</td>
          <td><code>ST %Q0.0</code> (KM1_ASPIR)</td>
        </tr>
        <tr>
          <td><code>S</code> / <code>R</code></td>
          <td>Bobina SET <code>(S)</code> / RESET <code>(R)</code></td>
          <td>Enclava en 1 (Set) o desenclava en 0 (Reset) si el acumulador vale 1</td>
          <td><code>S %M5</code> / <code>R %M5</code></td>
        </tr>
        <tr>
          <td><code>BLK</code> ... <code>END_BLK</code></td>
          <td>Bloques funcionales (%TM, %C)</td>
          <td>Delimita la parametrización de entradas (IN, R, CU) de timers y contadores</td>
          <td><code>BLK %TM0 ... END_BLK</code></td>
        </tr>
        <tr>
          <td><code>[ ... ]</code></td>
          <td>Bloques de Operación / Comparación</td>
          <td>Ejecuta comparaciones booleanas o asignaciones aritméticas en línea</td>
          <td><code>[%MW0 := %IW0.0 * 3]</code></td>
        </tr>
      </tbody>
    </table>

    <h2>2. Botón Ladder/IL en EcoStruxure Machine Expert – Basic</h2>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">¿Cómo alternar vistas en el editor?</div>
        <p style="font-size: 7.4pt; margin: 0;">
          En la barra superior de cada rung existe el icono <b>[Ladder / IL]</b>. Al presionarlo, el compilador traduce de forma bidireccional y sin pérdida el dibujo gráfico de contactos a código IL estructurado. Si un rung no conmuta, indica un error sintáctico de dibujo en la rama.
        </p>
      </div>
      <div class="card">
        <div class="card-title">Regla de Ejecución y Scan</div>
        <p style="font-size: 7.4pt; margin: 0;">
          El PLC ejecuta el código IL estrictamente de arriba hacia abajo y de izquierda a derecha. Por esta razón de seguridad, el <b>RESET</b> de variables críticas (como <code>LINEA</code> o <code>CMD_MARCHA</code>) se programa en líneas posteriores al <b>SET</b>, garantizando prioridad absoluta a la parada.
        </p>
      </div>
    </div>

    <div class="callout callout-alert" style="margin-top: 3px;">
      <b>Utilidad Didáctica y Profesional:</b>
      La Lista de Instrucciones permite auditar con precisión matemática las condiciones booleanas de enclavamiento, diagnosticar carreras lógicas y verificar la ausencia de ambigüedades en derivaciones paralelas complejas.
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 2: LISTA DE INSTRUCCIONES: SECCIONES 1, 2 Y 3 (CLASES 1 Y 2) -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Lista de Instrucciones (IL):</b> Secc. 1 (Generales), Secc. 2 (Fallas) y Secc. 3 (Celdas)</span>
    </div>

    <h2>Sección 1 — Generales (POU: 1_Generales · Clase 1)</h2>
    <table>
      <thead>
        <tr><th style="width: 8%;">Rung</th><th style="width: 42%;">Función y Ecuación Booleana</th><th style="width: 50%;">Código en Lista de Instrucciones (IL)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="rung-num">1.1</td>
          <td><b>Señal de Vida (Watchdog SCADA):</b> <code>%M10 := %S6</code><br>Copia directa del reloj de 1 segundo a la marca VIDA.</td>
          <td><code>LD %S6</code><br><code>ST %M10</code></td>
        </tr>
        <tr>
          <td class="rung-num">1.2</td>
          <td><b>Pulso de Reset Maestro:</b> <code>%M50 = %M42 + ↑%I0.7</code><br>Genera RESET_FALLAS con orden remota o pulsador; auto-reset de CMD_RESET.</td>
          <td><code>LD %M42</code><br><code>ORR %I0.7</code><br><code>ST %M50</code><br><code>R %M42</code></td>
        </tr>
      </tbody>
    </table>

    <h2>Sección 2 — Fallas y Seguridad Positiva (POU: 2_Fallas · Clase 1)</h2>
    <table>
      <thead>
        <tr><th style="width: 8%;">Rung</th><th style="width: 42%;">Función y Ecuación Booleana</th><th style="width: 50%;">Código en Lista de Instrucciones (IL)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="rung-num">2.1</td>
          <td><b>SET Falla Parada de Emergencia:</b> <code>/PE_OK &rarr; (S) AL_EMERG</code></td>
          <td><code>LDN %I0.0</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>S %M20</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.2</td>
          <td><b>RESET Falla Parada de Emergencia:</b> <code>RESET_FALLAS · PE_OK &rarr; (R) AL_EMERG</code></td>
          <td><code>LD %M50</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>AND %I0.0</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>R %M20</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.3</td>
          <td><b>SET Falla Guardamotor M1 (Aspiración):</b> <code>/GM1_OK &rarr; (S) AL_M1</code></td>
          <td><code>LDN %I0.1</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>S %M21</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.4</td>
          <td><b>RESET Falla Guardamotor M1:</b> <code>RESET_FALLAS · GM1_OK &rarr; (R) AL_M1</code></td>
          <td><code>LD %M50</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>AND %I0.1</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>R %M21</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.5</td>
          <td><b>SET Falla Guardamotor M2 (Redler):</b> <code>/GM2_OK &rarr; (S) AL_M2</code></td>
          <td><code>LDN %I0.2</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>S %M22</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.6</td>
          <td><b>RESET Falla Guardamotor M2:</b> <code>RESET_FALLAS · GM2_OK &rarr; (R) AL_M2</code></td>
          <td><code>LD %M50</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>AND %I0.2</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>R %M22</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.7</td>
          <td><b>SET Falla Guardamotor M3 (Elevador):</b> <code>/GM3_OK &rarr; (S) AL_M3</code></td>
          <td><code>LDN %I0.3</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>S %M23</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.8</td>
          <td><b>RESET Falla Guardamotor M3:</b> <code>RESET_FALLAS · GM3_OK &rarr; (R) AL_M3</code></td>
          <td><code>LD %M50</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>AND %I0.3</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>R %M23</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.9</td>
          <td><b>Temporizador de Giro Elevador:</b> <code>KM3_ELEV · /GIRO_M3 &rarr; T_GIRO (TON 5s)</code></td>
          <td><code>BLK %TM5</code><br><code>LD %Q0.2</code><br><code>ANDN %I0.4</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.10</td>
          <td><b>SET Falla Falta de Giro M3:</b> <code>T_GIRO.Q &rarr; (S) AL_GIRO</code></td>
          <td><code>LD %TM5.Q</code> &nbsp;&nbsp;&nbsp;&nbsp;<code>S %M24</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.11</td>
          <td><b>RESET Falla Falta de Giro M3:</b> <code>RESET_FALLAS · /T_GIRO.Q &rarr; (R) AL_GIRO</code></td>
          <td><code>LD %M50</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>ANDN %TM5.Q</code> &nbsp;&nbsp;&nbsp;&nbsp;<code>R %M24</code></td>
        </tr>
        <tr>
          <td class="rung-num">2.12</td>
          <td><b>Suma Lógica Falla General:</b> <code>FALLA_GRAL = AL_EMERG + AL_M1 + AL_M2 + AL_M3 + AL_GIRO + AL_DP_MUY_ALTA</code></td>
          <td><code>LD %M20</code><br><code>OR %M21</code><br><code>OR %M22</code><br><code>OR %M23</code><br><code>OR %M24</code><br><code>OR %M25</code><br><code>ST %M30</code></td>
        </tr>
      </tbody>
    </table>

    <h2>Sección 3 — Celdas y Permiso (POU: 3_Celdas_y_permiso · Clase 2)</h2>
    <table>
      <thead>
        <tr><th style="width: 8%;">Rung</th><th style="width: 42%;">Función y Ecuación Booleana</th><th style="width: 50%;">Código en Lista de Instrucciones (IL)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="rung-num">3.1</td>
          <td><b>Validación de Celda:</b> <code>CELDA_VALIDA = [%MW10=1] + [%MW10=2]</code></td>
          <td><code>LD [%MW10 = 1]</code><br><code>OR [%MW10 = 2]</code><br><code>ST %M53</code></td>
        </tr>
        <tr>
          <td class="rung-num">3.2</td>
          <td><b>Interbloqueo Destino Lleno:</b> <code>DESTINO_LLENO = ([%MW10=1]·LSH_C1) + ([%MW10=2]·LSH_C2)</code></td>
          <td><code>LD [%MW10 = 1]</code><br><code>AND %I0.5</code><br><code>OR( [%MW10 = 2]</code><br><code>AND %I0.6</code><br><code>)</code><br><code>ST %M52</code></td>
        </tr>
        <tr>
          <td class="rung-num">3.3</td>
          <td><b>Aviso Celda 1 Llena:</b> <code>AV_C1_LLENA = LSH_C1</code></td>
          <td><code>LD %I0.5</code><br><code>ST %M27</code></td>
        </tr>
        <tr>
          <td class="rung-num">3.4</td>
          <td><b>Aviso Celda 2 Llena:</b> <code>AV_C2_LLENA = LSH_C2</code></td>
          <td><code>LD %I0.6</code><br><code>ST %M28</code></td>
        </tr>
        <tr>
          <td class="rung-num">3.5</td>
          <td><b>Compuerta Celda 1:</b> <code>YV1_C1 = [%MW10=1] · /AL_EMERG</code></td>
          <td><code>LD [%MW10 = 1]</code><br><code>ANDN %M20</code><br><code>ST %Q0.3</code></td>
        </tr>
        <tr>
          <td class="rung-num">3.6</td>
          <td><b>Compuerta Celda 2:</b> <code>YV2_C2 = [%MW10=2] · /AL_EMERG</code></td>
          <td><code>LD [%MW10 = 2]</code><br><code>ANDN %M20</code><br><code>ST %Q0.4</code></td>
        </tr>
        <tr>
          <td class="rung-num">3.7</td>
          <td><b>Permiso de Marcha:</b> <code>PERMISO = PE_OK · /FALLA_GRAL · CELDA_VALIDA · /DESTINO_LLENO</code></td>
          <td><code>LD %I0.0</code><br><code>ANDN %M30</code><br><code>AND %M53</code><br><code>ANDN %M52</code><br><code>ST %M9</code></td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 3: LISTA DE INSTRUCCIONES: SECCIONES 4 Y 5 (CLASE 2)        -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Lista de Instrucciones (IL):</b> Secc. 4 (Marcha/Parada) y Secc. 5 (Motores)</span>
    </div>

    <h2>Sección 4 — Marcha, Parada y Cascada de Temporizadores (POU: 4_Marcha_y_parada · Clase 2)</h2>
    <table>
      <thead>
        <tr><th style="width: 8%;">Rung</th><th style="width: 42%;">Función y Ecuación Booleana</th><th style="width: 50%;">Código en Lista de Instrucciones (IL)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="rung-num">4.1</td>
          <td><b>SET Orden de Marcha Memorizada:</b><br><code>(S) LINEA = (CMD_MARCHA + ↑PB_MARCHA) · PERMISO</code></td>
          <td><code>LD %M40</code><br><code>ORR %I0.8</code><br><code>AND %M9</code><br><code>S %M5</code></td>
        </tr>
        <tr>
          <td class="rung-num">4.2</td>
          <td><b>RESET Orden de Marcha Memorizada:</b><br><code>(R) LINEA = CMD_PARADA + /PB_PARADA + DESTINO_LLENO + FALLA_GRAL</code></td>
          <td><code>LD %M41</code><br><code>ORN %I0.9</code><br><code>OR %M52</code><br><code>OR %M30</code><br><code>R %M5</code></td>
        </tr>
        <tr>
          <td class="rung-num">4.3</td>
          <td><b>Auto-reset de Órdenes SCADA:</b><br>Borra automáticamente CMD_MARCHA y CMD_PARADA tras ser evaluadas.</td>
          <td><code>LD %M40</code><br><code>OR %M41</code><br><code>R %M40</code><br><code>R %M41</code></td>
        </tr>
        <tr>
          <td class="rung-num">4.4</td>
          <td><b>Temporizador de Bocina de Pre-arranque:</b><br><code>LINEA &rarr; T_BOCINA (TP 5 s)</code></td>
          <td><code>BLK %TM0</code><br><code>LD %M5</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">4.5</td>
          <td><b>Temporizador de Escalonamiento M1 &rarr; M2:</b><br><code>LINEA · KM1_ASPIR &rarr; T_ARR_M2 (TON 5 s)</code></td>
          <td><code>BLK %TM1</code><br><code>LD %M5</code><br><code>AND %Q0.0</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">4.6</td>
          <td><b>Temporizador de Escalonamiento M2 &rarr; M3:</b><br><code>LINEA · KM2_REDLER &rarr; T_ARR_M3 (TON 5 s)</code></td>
          <td><code>BLK %TM2</code><br><code>LD %M5</code><br><code>AND %Q0.1</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">4.7</td>
          <td><b>Temporizador de Vaciado de Redler M2:</b><br><code>KM3_ELEV &rarr; T_VACIADO (TOF 20 s)</code></td>
          <td><code>BLK %TM3</code><br><code>LD %Q0.2</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">4.8</td>
          <td><b>Temporizador de Barrido de Conductos M1:</b><br><code>KM2_REDLER &rarr; T_BARRIDO (TOF 30 s)</code></td>
          <td><code>BLK %TM4</code><br><code>LD %Q0.1</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
      </tbody>
    </table>

    <h2>Sección 5 — Motores y Bocina (POU: 5_Motores_y_bocina · Clase 2)</h2>
    <p style="font-size: 7.5pt; margin-bottom: 3px;">
      Arquitectura industrial de máxima confiabilidad: <b>Protecciones físicas y lógicas en serie &times; Condición de marcha / parada diferida</b>.
    </p>

    <table>
      <thead>
        <tr><th style="width: 8%;">Rung</th><th style="width: 44%;">Función y Ecuación Booleana</th><th style="width: 48%;">Código en Lista de Instrucciones (IL)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="rung-num">5.1</td>
          <td>
            <b>KM1_ASPIR (Ventilador de Aspiración M1):</b><br>
            <code>KM1_ASPIR = PE_OK · /AL_EMERG · GM1_OK · /AL_M1 · ( LINEA · /T_BOCINA.Q + T_BARRIDO.Q )</code><br>
            <span style="font-size: 7pt; color: #475569;">Arranca inmediatamente al finalizar los 5 s de bocina y sigue 30 s de barrido tras parar M2.</span>
          </td>
          <td>
            <code>LD   %I0.0</code><br>
            <code>ANDN %M20</code><br>
            <code>AND  %I0.1</code><br>
            <code>ANDN %M21</code><br>
            <code>AND( %M5</code><br>
            <code>ANDN %TM0.Q</code><br>
            <code>OR   %TM4.Q</code><br>
            <code>)</code><br>
            <code>ST   %Q0.0</code>
          </td>
        </tr>
        <tr>
          <td class="rung-num">5.2</td>
          <td>
            <b>KM2_REDLER (Redler Distribuidor M2):</b><br>
            <code>KM2_REDLER = PE_OK · /AL_EMERG · GM2_OK · /AL_M2 · ( LINEA · T_ARR_M2.Q + KM2_REDLER · T_VACIADO.Q )</code><br>
            <span style="font-size: 7pt; color: #475569;">Arranca 5 s después de M1; tras parada normal continúa 20 s mediante realimentación de TOF.</span>
          </td>
          <td>
            <code>LD   %I0.0</code><br>
            <code>ANDN %M20</code><br>
            <code>AND  %I0.2</code><br>
            <code>ANDN %M22</code><br>
            <code>AND( %M5</code><br>
            <code>AND  %TM1.Q</code><br>
            <code>OR(  %Q0.1</code><br>
            <code>AND  %TM3.Q</code><br>
            <code>)</code><br>
            <code>)</code><br>
            <code>ST   %Q0.1</code>
          </td>
        </tr>
        <tr>
          <td class="rung-num">5.3</td>
          <td>
            <b>KM3_ELEV (Elevador de Cangilones M3):</b><br>
            <code>KM3_ELEV = PE_OK · /AL_EMERG · GM3_OK · /AL_M3 · /AL_GIRO · KM2_REDLER · LINEA · T_ARR_M3.Q</code><br>
            <span style="font-size: 7pt; color: #475569;">Arranca 5 s después de M2. Interbloqueado en serie con KM2_REDLER (se detiene instantáneamente).</span>
          </td>
          <td>
            <code>LD   %I0.0</code><br>
            <code>ANDN %M20</code><br>
            <code>AND  %I0.3</code><br>
            <code>ANDN %M23</code><br>
            <code>ANDN %M24</code><br>
            <code>AND  %Q0.1</code><br>
            <code>AND  %M5</code><br>
            <code>AND  %TM2.Q</code><br>
            <code>ST   %Q0.2</code>
          </td>
        </tr>
        <tr>
          <td class="rung-num">5.4</td>
          <td>
            <b>BOCINA (Avisador Acústico de Pre-arranque):</b><br>
            <code>BOCINA = LINEA · T_BOCINA.Q</code><br>
            <span style="font-size: 7pt; color: #475569;">Activa la salida de audio únicamente durante los 5 s del pulso inicial del bloque TP.</span>
          </td>
          <td>
            <code>LD   %M5</code><br>
            <code>AND  %TM0.Q</code><br>
            <code>ST   %Q0.5</code>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 4: LISTA DE INSTRUCCIONES: SECCIONES 6 Y 7 (CLASE 3)        -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Lista de Instrucciones (IL):</b> Secc. 6 (&Delta;P y Contador) y Secc. 7 (Señalización/SCADA)</span>
    </div>

    <h2>Sección 6 — &Delta;P y Contador de Arranques (POU: 6_DP_y_contador · Clase 3)</h2>
    <table>
      <thead>
        <tr><th style="width: 8%;">Rung</th><th style="width: 44%;">Función y Ecuación Booleana</th><th style="width: 48%;">Código en Lista de Instrucciones (IL)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="rung-num">6.1</td>
          <td><b>Escalado Matemático de Presión Diferencial:</b><br>Multiplica los puntos crudos (0–1000) por 3 para obtener Pa (0–3000 Pa).</td>
          <td><code>LD 1</code><br><code>[%MW0 := %IW0.0 * 3]</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.2</td>
          <td><b>Temporizador de Retardo Aviso &Delta;P Alta:</b><br>Filtro temporal de 10 s si %MW0 &gt; 1500 Pa (evita falsas alarmas).</td>
          <td><code>BLK %TM6</code><br><code>LD [%MW0 &gt; 1500]</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.3</td>
          <td><b>Bobina de Aviso &Delta;P Alta:</b> <code>AV_DP_ALTA = T_DP_ALTA.Q</code></td>
          <td><code>LD %TM6.Q</code><br><code>ST %M26</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.4</td>
          <td><b>Temporizador Retardo Falla &Delta;P Muy Alta:</b><br>Filtro temporal de 10 s si %MW0 &gt; 2000 Pa sostenidos.</td>
          <td><code>BLK %TM7</code><br><code>LD [%MW0 &gt; 2000]</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.5</td>
          <td><b>SET Falla &Delta;P Muy Alta:</b> <code>T_DP_MUY_ALTA.Q &rarr; (S) AL_DP_MUY_ALTA</code></td>
          <td><code>LD %TM7.Q</code><br><code>S %M25</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.6</td>
          <td><b>RESET Falla &Delta;P Muy Alta:</b> Borra con pulso RESET si presión bajó de 2000.</td>
          <td><code>LD %M50</code><br><code>ANDN %TM7.Q</code><br><code>R %M25</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.7</td>
          <td><b>Ventana Cíclica de 1 Hora:</b> Timer de 3600 s autorreseteante con /T_HORA.Q.</td>
          <td><code>BLK %TM8</code><br><code>LDN %TM8.Q</code><br><code>IN</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.8</td>
          <td><b>Contador Ascendente de Arranques:</b> Preset 6; CU = KM3_ELEV, R = %TM8.Q.</td>
          <td><code>BLK %C0</code><br><code>LD %TM8.Q</code> &nbsp;<code>R</code><br><code>LD %Q0.2</code> &nbsp;&nbsp;<code>CU</code><br><code>END_BLK</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.9</td>
          <td><b>Aviso de Límite de Arranques:</b> <code>AV_ARRANQUES = [%C0.V &ge; 6]</code></td>
          <td><code>LD [%C0.V &gt;= 6]</code><br><code>ST %M29</code></td>
        </tr>
        <tr>
          <td class="rung-num">6.10</td>
          <td><b>Publicación de Conteo a Registro SCADA:</b> <code>%MW1 := %C0.V</code></td>
          <td><code>LD 1</code><br><code>[%MW1 := %C0.V]</code></td>
        </tr>
      </tbody>
    </table>

    <h2>Sección 7 — Señalización Óptica y Desacoplamiento SCADA (POU: 7_Senalizacion_SCADA · Clase 3)</h2>
    <table>
      <thead>
        <tr><th style="width: 8%;">Rung</th><th style="width: 44%;">Función y Ecuación Booleana</th><th style="width: 48%;">Código en Lista de Instrucciones (IL)</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="rung-num">7.1</td>
          <td>
            <b>Baliza Luminosa de Tablero:</b><br>
            <code>BALIZA = FALLA_GRAL · RELOJ_1S + /FALLA_GRAL · ( AV_DP_ALTA + AV_C1_LLENA + AV_C2_LLENA + AV_ARRANQUES )</code><br>
            <span style="font-size: 7pt; color: #475569;">Intermitente a 1 Hz ante cualquier falla; luz fija ante cualquier aviso activo.</span>
          </td>
          <td>
            <code>LD   %M30</code><br>
            <code>AND  %S6</code><br>
            <code>OR(  %M26</code><br>
            <code>OR   %M27</code><br>
            <code>OR   %M28</code><br>
            <code>OR   %M29</code><br>
            <code>ANDN %M30</code><br>
            <code>)</code><br>
            <code>ST   %Q0.6</code>
          </td>
        </tr>
        <tr>
          <td class="rung-num">7.2</td>
          <td>
            <b>Piloto Verde de Marcha:</b><br>
            <code>PILOTO_MARCHA = LINEA · ( KM3_ELEV + RELOJ_1S )</code><br>
            <span style="font-size: 7pt; color: #475569;">Intermitente durante el pre-arranque/escalonamiento; fijo con M3 en marcha.</span>
          </td>
          <td>
            <code>LD   %M5</code><br>
            <code>AND( %Q0.2</code><br>
            <code>OR   %S6</code><br>
            <code>)</code><br>
            <code>ST   %Q0.7</code>
          </td>
        </tr>
        <tr>
          <td class="rung-num">7.3</td>
          <td><b>Copia Estado M1 hacia SCADA:</b> <code>EST_M1 := KM1_ASPIR</code></td>
          <td><code>LD %Q0.0</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>ST %M0</code></td>
        </tr>
        <tr>
          <td class="rung-num">7.4</td>
          <td><b>Copia Estado M2 hacia SCADA:</b> <code>EST_M2 := KM2_REDLER</code></td>
          <td><code>LD %Q0.1</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>ST %M1</code></td>
        </tr>
        <tr>
          <td class="rung-num">7.5</td>
          <td><b>Copia Estado M3 hacia SCADA:</b> <code>EST_M3 := KM3_ELEV</code></td>
          <td><code>LD %Q0.2</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>ST %M2</code></td>
        </tr>
        <tr>
          <td class="rung-num">7.6</td>
          <td><b>Copia Estado Compuerta 1 hacia SCADA:</b> <code>EST_YV1 := YV1_C1</code></td>
          <td><code>LD %Q0.3</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>ST %M3</code></td>
        </tr>
        <tr>
          <td class="rung-num">7.7</td>
          <td><b>Copia Estado Compuerta 2 hacia SCADA:</b> <code>EST_YV2 := YV2_C2</code></td>
          <td><code>LD %Q0.4</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>ST %M4</code></td>
        </tr>
        <tr>
          <td class="rung-num">7.8</td>
          <td><b>Copia Estado Bocina hacia SCADA:</b> <code>EST_BOCINA := BOCINA</code></td>
          <td><code>LD %Q0.5</code> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>ST %M6</code></td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 5: MODELADO FORMAL EN GRAFCET (SFC — NORMA IEC 60848)       -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Modelado GRAFCET:</b> Diagrama Funcional de Secuencia de la Línea (G1)</span>
    </div>

    <h1>Modelado Formal en GRAFCET (Norma IEC 60848 / IEC 61131-3)</h1>
    <p style="font-size: 7.7pt; margin-bottom: 5px;">
      El <b>GRAFCET</b> (Graphe Fonctionnel de Commande Étape-Transition) es el modelo matemático por excelencia para diseñar automatismos secuenciales. Permite describir con total claridad los estados estables del proceso (<b>etapas</b>), las condiciones de evolución (<b>transiciones y receptividades</b>) y las consignas de mando hacia los actuadores (<b>acciones asociadas</b>).
    </p>

    <h2>1. Grafcet Principal de la Secuencia de la Línea (G1)</h2>
    <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 4px; padding: 7px 10px; margin-bottom: 6px;">
      
      <!-- ETAPA 0 -->
      <div style="display: flex; align-items: center;">
        <div class="grafcet-step grafcet-step-init">0</div>
        <div class="grafcet-action" style="border-color: #64748b; color: #475569;">Línea en Reposo / Espera de Orden (LINEA = 0 · Motores Detenidos)</div>
      </div>
      <div class="grafcet-trans">
        <div class="grafcet-bar"></div>
        <div><b>Receptividad 0 &rarr; 1:</b> <code>(CMD_MARCHA + ↑PB_MARCHA) · PERMISO</code> &nbsp;&nbsp;<i>[Orden de marcha con permiso válido]</i></div>
      </div>

      <!-- ETAPA 1 -->
      <div style="display: flex; align-items: center;">
        <div class="grafcet-step">1</div>
        <div class="grafcet-action" style="border-color: #d97706; background: #fffbeb;"><b>BOCINA = 1</b> &nbsp;|&nbsp; Temporizador acústico previo: <code>t1 / X1 / 5 s</code></div>
      </div>
      <div class="grafcet-trans">
        <div class="grafcet-bar"></div>
        <div><b>Receptividad 1 &rarr; 2:</b> <code>t1 / X1 / 5 s</code> &nbsp;&nbsp;<i>[Vencimiento del pulso de bocina de 5 segundos]</i></div>
      </div>

      <!-- ETAPA 2 -->
      <div style="display: flex; align-items: center;">
        <div class="grafcet-step">2</div>
        <div class="grafcet-action" style="border-color: #0284c7; background: #f0f9ff;"><b>KM1_ASPIR = 1</b> (Arranca Aspiración M1) &nbsp;|&nbsp; Temporizador escalonado: <code>t2 / X2 / 5 s</code></div>
      </div>
      <div class="grafcet-trans">
        <div class="grafcet-bar"></div>
        <div><b>Receptividad 2 &rarr; 3:</b> <code>t2 / X2 / 5 s · GM1_OK</code> &nbsp;&nbsp;<i>[Aspiración en régimen + 5 segundos de depresión]</i></div>
      </div>

      <!-- ETAPA 3 -->
      <div style="display: flex; align-items: center;">
        <div class="grafcet-step">3</div>
        <div class="grafcet-action" style="border-color: #0284c7; background: #f0f9ff;"><b>KM1_ASPIR = 1</b> &nbsp;+&nbsp; <b>KM2_REDLER = 1</b> (Arranca Redler M2) &nbsp;|&nbsp; Temporizador: <code>t3 / X3 / 5 s</code></div>
      </div>
      <div class="grafcet-trans">
        <div class="grafcet-bar"></div>
        <div><b>Receptividad 3 &rarr; 4:</b> <code>t3 / X3 / 5 s · GM2_OK</code> &nbsp;&nbsp;<i>[Redler en movimiento + 5 segundos de espera]</i></div>
      </div>

      <!-- ETAPA 4 -->
      <div style="display: flex; align-items: center;">
        <div class="grafcet-step" style="border-color: #16a34a; background: #dcfce7; color: #166534;">4</div>
        <div class="grafcet-action" style="border-color: #16a34a; background: #f0fdf4;"><b>MARCHA PLENA: KM1 = 1 &nbsp;|&nbsp; KM2 = 1 &nbsp;|&nbsp; KM3 = 1 &nbsp;|&nbsp; PILOTO_MARCHA = 1</b> (Transporte continuo)</div>
      </div>
      <div class="grafcet-trans">
        <div class="grafcet-bar"></div>
        <div><b>Receptividad 4 &rarr; 5:</b> <code>CMD_PARADA + /PB_PARADA + DESTINO_LLENO</code> &nbsp;&nbsp;<i>[Orden de parada voluntaria o silo lleno]</i></div>
      </div>

      <!-- ETAPA 5 -->
      <div style="display: flex; align-items: center;">
        <div class="grafcet-step">5</div>
        <div class="grafcet-action" style="border-color: #d97706; background: #fffbeb;"><b>VACIADO: KM3 = 0</b> (Paro instantáneo) &nbsp;|&nbsp; <b>KM1 = 1 &nbsp;|&nbsp; KM2 = 1</b> &nbsp;|&nbsp; <code>t4 / X5 / 20 s</code></div>
      </div>
      <div class="grafcet-trans">
        <div class="grafcet-bar"></div>
        <div><b>Receptividad 5 &rarr; 6:</b> <code>t4 / X5 / 20 s</code> &nbsp;&nbsp;<i>[Vencimiento del tiempo de vaciado del redler (20 s)]</i></div>
      </div>

      <!-- ETAPA 6 -->
      <div style="display: flex; align-items: center;">
        <div class="grafcet-step">6</div>
        <div class="grafcet-action" style="border-color: #d97706; background: #fffbeb;"><b>BARRIDO: KM2 = 0</b> &nbsp;|&nbsp; <b>KM1 = 1</b> (Ventilador limpia mangas y mangas) &nbsp;|&nbsp; <code>t5 / X6 / 30 s</code></div>
      </div>
      <div class="grafcet-trans">
        <div class="grafcet-bar"></div>
        <div><b>Receptividad 6 &rarr; 0:</b> <code>t5 / X6 / 30 s</code> &nbsp;&nbsp;<i>[Fin del barrido de conductos (30 s) &rarr; Retorno al reposo Etapa 0]</i></div>
      </div>

    </div>

    <h2>2. Grafcet Secundario de Compuertas Motorizadas (G2)</h2>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Derivación Celda 1 (G2.1)</div>
        <p style="font-size: 7.3pt; margin: 0;">
          • <b>Etapa 10:</b> Compuerta YV1 cerrada (reposo).<br>
          • <b>Transición 10 &rarr; 11:</b> <code>[%MW10 = 1] · /AL_EMERG</code><br>
          • <b>Etapa 11:</b> <code>YV1_C1 = 1</code> (Compuerta abierta).<br>
          • <b>Transición 11 &rarr; 10:</b> <code>[%MW10 &ne; 1] + AL_EMERG</code>
        </p>
      </div>
      <div class="card">
        <div class="card-title">Derivación Celda 2 (G2.2)</div>
        <p style="font-size: 7.3pt; margin: 0;">
          • <b>Etapa 20:</b> Compuerta YV2 cerrada (reposo).<br>
          • <b>Transición 20 &rarr; 21:</b> <code>[%MW10 = 2] · /AL_EMERG</code><br>
          • <b>Etapa 21:</b> <code>YV2_C2 = 1</code> (Compuerta abierta).<br>
          • <b>Transición 21 &rarr; 20:</b> <code>[%MW10 &ne; 2] + AL_EMERG</code>
        </p>
      </div>
    </div>

    <div class="callout callout-success" style="margin-top: 4px;">
      <b>Correspondencia Biunívoca:</b>
      Cada etapa del GRAFCET $X_i$ coincide exactamente con los estados de los temporizadores de secuencia del programa: Etapa 1 = <code>%TM0.Q</code>, Etapa 2 = <code>%TM0.Q &darr;</code>, Etapa 3 = <code>%TM1.Q</code>, Etapa 4 = <code>%TM2.Q</code>, Etapa 5 = <code>%TM3.Q</code> (TOF vaciado) y Etapa 6 = <code>%TM4.Q</code> (TOF barrido).
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 6: GRAFCET DE SEGURIDAD, TRADUCCIÓN A LADDER/IL Y CONCLUSIÓN -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Modelado GRAFCET:</b> Tratamiento de Fallas, Traducción a Ladder/IL y Conclusión</span>
    </div>

    <h1>Tratamiento de Seguridad en GRAFCET y Traducción al PLC</h1>

    <h2>1. Tratamiento de Fallas y Paradas de Urgencia (GEMMA / Forzado)</h2>
    <p style="font-size: 7.6pt; margin-bottom: 4px;">
      En automatización industrial según la guía <b>GEMMA</b> (Guide d'Étude des Modes de Marches et d'Arrêts), las fallas no son simples transiciones secuenciales, sino <b>forzados estructurales</b> sobre las etapas activas:
    </p>

    <table>
      <thead>
        <tr>
          <th style="width: 20%;">Evento de Falla</th>
          <th style="width: 25%;">Evolución en el GRAFCET</th>
          <th style="width: 40%;">Comportamiento Dinámico de Actuadores</th>
          <th style="width: 15%; text-align: center;">Prioridad</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>Parada de Emergencia (`AL_EMERG`)</b></td>
          <td>Forzado instantáneo a <b>Etapa 0</b>: <code>G1 { 0 }</code></td>
          <td>Corte inmediato de KM1, KM2, KM3 y cierre forzado de compuertas YV1 y YV2. Bloqueo total hasta rearme.</td>
          <td class="text-center"><span class="badge badge-danger">CRÍTICA (1)</span></td>
        </tr>
        <tr>
          <td><b>Disparo Guardamotor M1 (`AL_M1`)</b></td>
          <td>Forzado instantáneo a <b>Etapa 0</b>: <code>G1 { 0 }</code></td>
          <td>Sin ventilación no puede operar ningún equipo. Parada inmediata de toda la línea por enclavamiento.</td>
          <td class="text-center"><span class="badge badge-danger">CRÍTICA (1)</span></td>
        </tr>
        <tr>
          <td><b>Disparo Guardamotor M2 (`AL_M2`)</b></td>
          <td>Bifurcación forzada a <b>Etapa 6</b>: <code>G1 { 6 }</code></td>
          <td>M2 y M3 se detienen en el acto (evita derrame). M1 sigue funcionando 30 s para barrer el polvo remanente.</td>
          <td class="text-center"><span class="badge badge-warn">MEDIA (2)</span></td>
        </tr>
        <tr>
          <td><b>Falta de Giro Elevador (`AL_GIRO`)</b></td>
          <td>Transición inmediata a <b>Etapa 5</b>: <code>G1 { 5 }</code></td>
          <td>Elevador M3 para en el acto. M2 sigue 20 s de vaciado y M1 30 s de barrido para limpiar la línea.</td>
          <td class="text-center"><span class="badge badge-warn">MEDIA (2)</span></td>
        </tr>
        <tr>
          <td><b>&Delta;P Muy Alta &gt; 2000 Pa (`AL_DP_MUY_ALTA`)</b></td>
          <td>Transición a <b>Etapa 5</b> vía <code>FALLA_GRAL</code></td>
          <td>Detiene la alimentación (M3); ejecuta vaciado ordenado de M2 y barrido final de M1.</td>
          <td class="text-center"><span class="badge badge-warn">MEDIA (2)</span></td>
        </tr>
      </tbody>
    </table>

    <h2>2. Metodología de Traducción: De GRAFCET a Ladder y Lista de Instrucciones</h2>
    <p style="font-size: 7.5pt; margin-bottom: 3px;">
      Existen dos métodos estandarizados para implementar un Grafcet en la CPU Modicon M221:
    </p>

    <div class="grid-2">
      <div class="card">
        <div class="card-title">Método A: Bits de Etapa (%Xi con Set/Reset)</div>
        <p style="font-size: 7.2pt; margin: 0;">
          Para cada etapa $n$ se formula:
          <br>• <b>Activación:</b> $A_n = X_{n-1} \cdot \text{Receptividad}_{n-1 \to n} \implies \text{SET } X_n$
          <br>• <b>Desactivación:</b> $D_n = X_{n+1} + \text{Falla} \implies \text{RESET } X_n$
          <br>• <b>Acción:</b> Salida física activada por el contacto de la etapa ($X_n$).
          <br><i>Desventaja:</i> Requiere decenas de rungs auxiliares y gestión manual del estado inicial.
        </p>
      </div>

      <div class="card">
        <div class="card-title">Método B: Lógica Unificada por Actuador (El Método del TP)</div>
        <p style="font-size: 7.2pt; margin: 0;">
          Se utiliza la variable de estado <code>LINEA</code> (%M5) y los temporizadores normados (%TM0..%TM4).
          <br>• Cada motor se escribe en <b>un solo rung físico</b>:
          <br><code>KM_x = Protecciones · ( Condición_Arranque + Mantenimiento_Parada )</code>
          <br><i>Ventaja:</i> Máxima seguridad contra doble bobina, trazabilidad directa y código compacto.
        </p>
      </div>
    </div>

    <h2>3. Cuadro Comparativo de Equivalencias Didácticas</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 22%;">Estado del Grafcet</th>
          <th style="width: 25%;">Variable Ladder Asociada</th>
          <th style="width: 25%;">Instrucción IL Clave</th>
          <th style="width: 28%;">Estado de la Planta</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>Etapa 0 (Reposo)</b></td>
          <td><code>/LINEA</code> (%M5 = 0)</td>
          <td><code>LDN %M5</code></td>
          <td>Motores en 0, permiso evaluándose</td>
        </tr>
        <tr>
          <td><b>Etapa 1 (Pre-aviso)</b></td>
          <td><code>LINEA · T_BOCINA.Q</code> (%TM0)</td>
          <td><code>LD %M5 · AND %TM0.Q</code></td>
          <td>Bocina sonando, personal advertido</td>
        </tr>
        <tr>
          <td><b>Etapa 2 (Aspiración sola)</b></td>
          <td><code>LINEA · /T_BOCINA.Q</code></td>
          <td><code>LD %M5 · ANDN %TM0.Q</code></td>
          <td>M1 crea vacío en mangas de filtro</td>
        </tr>
        <tr>
          <td><b>Etapa 3 (Aspiración + Redler)</b></td>
          <td><code>LINEA · T_ARR_M2.Q</code> (%TM1)</td>
          <td><code>LD %M5 · AND %TM1.Q</code></td>
          <td>M1 + M2 en marcha previa</td>
        </tr>
        <tr>
          <td><b>Etapa 4 (Marcha Plena)</b></td>
          <td><code>LINEA · T_ARR_M3.Q</code> (%TM2)</td>
          <td><code>LD %M5 · AND %TM2.Q</code></td>
          <td>Línea completa produciendo a régimen</td>
        </tr>
        <tr>
          <td><b>Etapa 5 (Vaciado Redler)</b></td>
          <td><code>/KM3 · T_VACIADO.Q</code> (%TM3)</td>
          <td><code>AND( %Q0.1 AND %TM3.Q )</code></td>
          <td>M3 parado; M2 evacua cereal 20 s</td>
        </tr>
        <tr>
          <td><b>Etapa 6 (Barrido Mangas)</b></td>
          <td><code>/KM2 · T_BARRIDO.Q</code> (%TM4)</td>
          <td><code>OR %TM4.Q</code></td>
          <td>M2 parado; M1 aspira polvo 30 s</td>
        </tr>
      </tbody>
    </table>

    <table style="margin-top: 6px; border: none;">
      <tr style="background: none;">
        <td style="border: none; width: 50%; text-align: center; padding-top: 10px;">
          <div style="border-top: 1px solid #94a3b8; width: 75%; margin: 0 auto; padding-top: 2px; font-size: 7.2pt;">
            <b>Alumno: Hugo Ariel Martinez</b><br>
            Proyecto: Martinez.smbp · UTN Paraná
          </div>
        </td>
        <td style="border: none; width: 50%; text-align: center; padding-top: 10px;">
          <div style="border-top: 1px solid #94a3b8; width: 75%; margin: 0 auto; padding-top: 2px; font-size: 7.2pt;">
            <b>Cátedra de Automatización Industrial</b><br>
            Comisión Evaluadora de Trabajos Integradores
          </div>
        </td>
      </tr>
    </table>
  </div>

</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML generado exitosamente: {OUTPUT_HTML}")

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
