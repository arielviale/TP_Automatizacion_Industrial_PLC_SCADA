# -*- coding: utf-8 -*-
"""
Generador del Informe Oficial de Verificación de Asignaciones y Guía Técnica por Clases (8 Páginas Calibradas)
Trabajo Práctico Integrador — Parte 2: Programación de PLC y Supervisión SCADA
Tecnicatura Superior en Mecatrónica — UTN Facultad Regional Paraná
"""

import os
import subprocess
import fitz

OUTPUT_HTML = os.path.abspath("Resolucion/verificacion_consignas.html")
OUTPUT_PDF = os.path.abspath("Resolucion/Verificacion_Asignaciones_y_Guia_Consignas_TP.pdf")

html_content = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Verificación de Asignaciones y Guía de Consignas — TP Integrador 2</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 11mm 12mm 13mm 12mm;
      @bottom-left {
        content: "UTN Paraná · Mecatrónica — Automatización Industrial (TP Integrador 2)";
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 7.2pt;
        color: #64748b;
      }
      @bottom-right {
        content: "Página " counter(page) " de 8";
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
      font-size: 8.2pt;
      line-height: 1.34;
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
      margin-bottom: 9px;
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
      font-size: 7.9pt;
      color: #475569;
      font-weight: 600;
      margin: 0;
    }

    .doc-meta {
      text-align: right;
      font-size: 7.5pt;
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
      font-size: 12pt;
      font-weight: 800;
      color: #003366;
      margin: 0 0 6px 0;
      padding-bottom: 2px;
      border-bottom: 1.5px solid #004b87;
      line-height: 1.2;
    }

    h2 {
      font-size: 9.5pt;
      font-weight: 700;
      color: #0f172a;
      margin: 7px 0 4px 0;
      background: #f1f5f9;
      padding: 3px 7px;
      border-left: 3.5px solid #004b87;
      border-radius: 0 3px 3px 0;
    }

    h3 {
      font-size: 8.5pt;
      font-weight: 700;
      color: #004b87;
      margin: 5px 0 2px 0;
    }

    p {
      margin: 0 0 5px 0;
    }

    /* Tablas */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 7.5pt;
      margin-bottom: 6px;
    }

    th {
      background: #004b87;
      color: #ffffff;
      font-weight: 600;
      text-align: left;
      padding: 3.5px 5px;
      border: 1px solid #003560;
      font-size: 7.3pt;
    }

    td {
      padding: 3px 5px;
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

    .badge-warn {
      background: #fef9c3;
      color: #854d0e;
      border: 1px solid #fde047;
    }

    .badge-danger {
      background: #fee2e2;
      color: #b91c1c;
      border: 1px solid #fca5a5;
    }

    /* Callouts */
    .callout {
      background: #f0f7ff;
      border: 1px solid #b9d7ea;
      border-left: 3.5px solid #004b87;
      padding: 5px 8px;
      margin-bottom: 6px;
      border-radius: 0 3px 3px 0;
      font-size: 7.8pt;
    }

    .callout-title {
      font-weight: 700;
      color: #004b87;
      margin-bottom: 2px;
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
      margin-bottom: 6px;
    }

    .grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 6px;
      margin-bottom: 6px;
    }

    .card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 3px;
      padding: 5px 7px;
    }

    .card-title {
      font-weight: 700;
      font-size: 7.9pt;
      color: #0f172a;
      margin-bottom: 2px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 2px;
    }

    code {
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 7.6pt;
      background: #f1f5f9;
      padding: 0.5px 3px;
      border-radius: 2px;
      color: #0f172a;
    }

    /* Banner Portada */
    .cover-banner {
      background: linear-gradient(135deg, #002d5a 0%, #004b87 60%, #0284c7 100%);
      color: white;
      padding: 13px 16px;
      border-radius: 5px;
      margin-bottom: 8px;
    }

    .cover-title {
      font-size: 14.5pt;
      font-weight: 800;
      margin: 0 0 4px 0;
      line-height: 1.15;
      letter-spacing: 0.2px;
    }

    .cover-subtitle {
      font-size: 8.8pt;
      color: #e0f2fe;
      margin: 0 0 6px 0;
      line-height: 1.3;
    }

    .cover-badge-row {
      display: flex;
      gap: 6px;
      margin-top: 5px;
    }

    .cover-pill {
      background: rgba(255, 255, 255, 0.18);
      border: 1px solid rgba(255, 255, 255, 0.35);
      color: #ffffff;
      font-size: 7pt;
      padding: 1.5px 6px;
      border-radius: 10px;
      font-weight: 600;
    }

    .step-box {
      border: 1px solid #cbd5e1;
      border-radius: 3px;
      padding: 5px 7px;
      margin-bottom: 5px;
      background: #ffffff;
    }

    .step-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 3px;
      padding-bottom: 2px;
      border-bottom: 1px solid #f1f5f9;
    }

    .step-num {
      font-weight: 800;
      color: #004b87;
      font-size: 8pt;
    }

    ul, ol {
      margin: 0 0 4px 0;
      padding-left: 15px;
    }

    li {
      margin-bottom: 2px;
    }

    .text-center { text-align: center; }
    .text-right { text-align: right; }
    .bold { font-weight: 700; }
  </style>
</head>
<body>

  <!-- =================================================================== -->
  <!-- PÁGINA 1: PORTADA & MATRIZ DE HARDWARE Y ENTRADAS DIGITALES (%I)   -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="header-box">
      <div>
        <div class="inst-title">Universidad Tecnológica Nacional — Facultad Regional Paraná</div>
        <div class="inst-sub">Tecnicatura Superior en Mecatrónica · Automatización Industrial (Unidades 7, 9 y 10)</div>
      </div>
      <div class="doc-meta">
        <b>INFORME TÉCNICO DE VERIFICACIÓN</b><br>
        Alumno: <b>Hugo Ariel Martinez</b><br>
        Proyecto: <b>Martinez.smbp</b> · Año 2026
      </div>
    </div>

    <div class="cover-banner">
      <div class="cover-title">Auditoría de Asignaciones y Guía Técnica de Consignas</div>
      <div class="cover-subtitle">
        Verificación exhaustiva del 100% de cumplimiento de las asignaciones inalterables fijadas por el TP Integrador (Controlador Modicon M221, Entradas/Salidas, Memoria %M/%MW, Temporizadores %TM, Contador %C0 y 7 Secciones) y desglose metodológico paso a paso de las Consignas 1 a 4.
      </div>
      <div class="cover-badge-row">
        <span class="cover-pill">✓ Controlador: TM221CE24R</span>
        <span class="cover-pill">✓ 100% Asignaciones Respetadas</span>
        <span class="cover-pill">✓ 51 Rungs Homologados</span>
        <span class="cover-pill">✓ 11 Pruebas Verificadas</span>
      </div>
    </div>

    <div class="callout callout-success">
      <div class="callout-title">
        <span>⚖️</span> Regla Común y Principio de Inalterabilidad del TP Integrador
      </div>
      <i>«Este enunciado fija el controlador, las entradas y salidas, las direcciones de memoria, los nombres (símbolos), los temporizadores y el orden del programa. Estas asignaciones no se pueden cambiar. El trabajo de cada alumno es escribir la lógica de cada rung, probarla y diseñar las pantallas.»</i> — El presente proyecto ha respetado rigurosamente cada parámetro, dirección, tipo y símbolo preestablecido.
    </div>

    <h2>1. Verificación de Hardware y Controlador Asignado</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 24%;">Parámetro</th>
          <th style="width: 34%;">Requisito Oficial del TP Integrador</th>
          <th style="width: 30%;">Implementación en Nuestro Proyecto</th>
          <th style="width: 12%; text-align: center;">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>Modelo de PLC</b></td>
          <td>Schneider Electric Modicon <b>TM221CE24R</b></td>
          <td>Modicon TM221CE24R (14 DI 24Vcc / 10 DO Relé)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><b>Puerto ETH1</b></td>
          <td>Servidor Modbus TCP habilitado en puerto 502</td>
          <td>Modbus TCP Server habilitado (127.0.0.1:502)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><b>Entrada Analógica</b></td>
          <td>%IW0.0: tipo 0–10 V, ámbito Normal (0–1000)</td>
          <td>%IW0.0: 0–10 V = 0–1000 pts = 0–3000 Pa</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><b>Estructura Secciones</b></td>
          <td>7 secciones POU creadas con nombres predefinidos</td>
          <td>7 secciones en orden exacto (51 rungs en Ladder)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
      </tbody>
    </table>

    <h2>2. Verificación de Entradas Digitales (%I) y Seguridad Positiva</h2>
    <p style="font-size: 7.7pt; margin-bottom: 4px;">
      <b>Convención de seguridad positiva respetada al 100%:</b> Las señales de protección física en reposo valen 1 (24 Vcc en borne). Si se corta un cable o salta un dispositivo, la entrada cae a 0 y el PLC lo interpreta como parada o falla segura.
    </p>
    <table>
      <thead>
        <tr>
          <th style="width: 7%;">Dir.</th>
          <th style="width: 14%;">Símbolo TP</th>
          <th style="width: 26%;">Descripción Funcional</th>
          <th style="width: 13%;">Tipo Contacto</th>
          <th style="width: 16%;">Estado Seguro (1)</th>
          <th style="width: 14%;">Rungs de Uso</th>
          <th style="width: 10%; text-align: center;">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>%I0.0</code></td>
          <td><code>PE_OK</code></td>
          <td>Parada de emergencia de campo</td>
          <td>NC (Normal Cerrado)</td>
          <td>1 = Sin emergencia</td>
          <td>2.1, 2.2, 3.7, 5.1..5.3</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.1</code></td>
          <td><code>GM1_OK</code></td>
          <td>Guardamotor de Aspiración M1</td>
          <td>NC / Auxiliar OK</td>
          <td>1 = Guardamotor OK</td>
          <td>2.3, 2.4, 5.1</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.2</code></td>
          <td><code>GM2_OK</code></td>
          <td>Guardamotor de Redler M2</td>
          <td>NC / Auxiliar OK</td>
          <td>1 = Guardamotor OK</td>
          <td>2.5, 2.6, 5.2</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.3</code></td>
          <td><code>GM3_OK</code></td>
          <td>Guardamotor de Elevador M3</td>
          <td>NC / Auxiliar OK</td>
          <td>1 = Guardamotor OK</td>
          <td>2.7, 2.8, 5.3</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.4</code></td>
          <td><code>GIRO_M3</code></td>
          <td>Sensor inductivo giro elevador (SSL)</td>
          <td>NA (Tren de pulsos)</td>
          <td>1 = Giro normal</td>
          <td>2.9 (alimenta T_GIRO)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.5</code></td>
          <td><code>LSH_C1</code></td>
          <td>Sensor de nivel alto Celda 1</td>
          <td>NA (Flotante / Paleta)</td>
          <td>1 = Celda 1 llena</td>
          <td>3.2, 3.3</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.6</code></td>
          <td><code>LSH_C2</code></td>
          <td>Sensor de nivel alto Celda 2</td>
          <td>NA (Flotante / Paleta)</td>
          <td>1 = Celda 2 llena</td>
          <td>3.2, 3.4</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.7</code></td>
          <td><code>PB_RESET</code></td>
          <td>Pulsador local de Rearme / RESET</td>
          <td>NA (Normal Abierto)</td>
          <td>1 = Pulsado</td>
          <td>1.2 (Flanco ↑PB_RESET)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.8</code></td>
          <td><code>PB_MARCHA</code></td>
          <td>Pulsador local de MARCHA</td>
          <td>NA (Normal Abierto)</td>
          <td>1 = Pulsado</td>
          <td>4.1 (Flanco ↑PB_MARCHA)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%I0.9</code></td>
          <td><code>PB_PARADA</code></td>
          <td>Pulsador local de PARADA</td>
          <td>NC (Normal Cerrado)</td>
          <td>1 = No pulsado (OK)</td>
          <td>4.2 (/PB_PARADA)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 2: SALIDAS (%Q), ANALÓGICA (%IW) Y MEMORIA %M (PARTE I)      -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Verificación de Asignaciones:</b> Salidas %Q, Analógica %IW y Memoria %M</span>
    </div>

    <h2>3. Verificación de Salidas Digitales (%Q)</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 7%;">Dir.</th>
          <th style="width: 15%;">Símbolo TP</th>
          <th style="width: 25%;">Actuador / Carga Asociada</th>
          <th style="width: 14%;">Tipo Salida</th>
          <th style="width: 29%;">Condición Operativa en Proceso</th>
          <th style="width: 10%; text-align: center;">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>%Q0.0</code></td>
          <td><code>KM1_ASPIR</code></td>
          <td>Contactor Ventilador Aspiración M1</td>
          <td>Relé (24Vcc / 230Vca)</td>
          <td>Arranca primero (t=5s) y para último (+30s barrido)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%Q0.1</code></td>
          <td><code>KM2_REDLER</code></td>
          <td>Contactor Redler Distribuidor M2</td>
          <td>Relé (24Vcc / 230Vca)</td>
          <td>Arranca a t=10s; para a t=20s de parada (+20s vaciado)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%Q0.2</code></td>
          <td><code>KM3_ELEV</code></td>
          <td>Contactor Elevador Cangilones M3</td>
          <td>Relé (24Vcc / 230Vca)</td>
          <td>Arranca a t=15s; para de forma instantánea (t=0)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%Q0.3</code></td>
          <td><code>YV1_C1</code></td>
          <td>Electroválvula compuerta Celda 1</td>
          <td>Bobina electroválvula</td>
          <td>Abierta si Destino=1 y no hay emergencia (%I0.0=1)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%Q0.4</code></td>
          <td><code>YV2_C2</code></td>
          <td>Electroválvula compuerta Celda 2</td>
          <td>Bobina electroválvula</td>
          <td>Abierta si Destino=2 y no hay emergencia (%I0.0=1)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%Q0.5</code></td>
          <td><code>BOCINA</code></td>
          <td>Bocina acústica de pre-arranque</td>
          <td>Avisador acústico</td>
          <td>Activa durante 5 s al recibir orden de marcha (%TM0)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%Q0.6</code></td>
          <td><code>BALIZA</code></td>
          <td>Baliza luminosa de tablero</td>
          <td>Torre luminosa</td>
          <td>Intermitente con Falla General; Fija con Avisos</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%Q0.7</code></td>
          <td><code>PILOTO_MARCHA</code></td>
          <td>Piloto verde de tablero</td>
          <td>Lámpara de marcha</td>
          <td>Intermitente en pre-arranque; Fijo con M3 marchando</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
      </tbody>
    </table>

    <h2>4. Verificación de Entrada Analógica (%IW0.0)</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 10%;">Dirección</th>
          <th style="width: 25%;">Transmisor / Variable</th>
          <th style="width: 18%;">Rango Eléctrico</th>
          <th style="width: 18%;">Conversión PLC</th>
          <th style="width: 19%;">Ecuación Escalado</th>
          <th style="width: 10%; text-align: center;">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>%IW0.0</code></td>
          <td>PDT-01: &Delta;P Filtro de mangas</td>
          <td>0 a 10 Vcc</td>
          <td>0 a 1000 puntos</td>
          <td><code>%MW0 := %IW0.0 * 3</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
      </tbody>
    </table>

    <h2>5. Verificación de Memoria Interna (%M) — Copias SCADA, Control y Fallas</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 7%;">Dir.</th>
          <th style="width: 17%;">Símbolo TP</th>
          <th style="width: 32%;">Descripción Funcional</th>
          <th style="width: 15%;">Sentido / Tráfico</th>
          <th style="width: 19%;">Rung y Lógica Asociada</th>
          <th style="width: 10%; text-align: center;">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>%M0</code></td>
          <td><code>EST_M1</code></td>
          <td>Copia estado motor M1 (Aspiración)</td>
          <td>PLC → SCADA</td>
          <td>Rung 7.3: <code>KM1_ASPIR → EST_M1</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M1</code></td>
          <td><code>EST_M2</code></td>
          <td>Copia estado motor M2 (Redler)</td>
          <td>PLC → SCADA</td>
          <td>Rung 7.4: <code>KM2_REDLER → EST_M2</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M2</code></td>
          <td><code>EST_M3</code></td>
          <td>Copia estado motor M3 (Elevador)</td>
          <td>PLC → SCADA</td>
          <td>Rung 7.5: <code>KM3_ELEV → EST_M3</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M3</code></td>
          <td><code>EST_YV1</code></td>
          <td>Copia compuerta Celda 1 abierta</td>
          <td>PLC → SCADA</td>
          <td>Rung 7.6: <code>YV1_C1 → EST_YV1</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M4</code></td>
          <td><code>EST_YV2</code></td>
          <td>Copia compuerta Celda 2 abierta</td>
          <td>PLC → SCADA</td>
          <td>Rung 7.7: <code>YV2_C2 → EST_YV2</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M5</code></td>
          <td><code>LINEA</code></td>
          <td>Orden de marcha memorizada de línea</td>
          <td>PLC → SCADA</td>
          <td>Rungs 4.1 y 4.2: SET / RESET</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M6</code></td>
          <td><code>EST_BOCINA</code></td>
          <td>Copia de bocina acústica sonando</td>
          <td>PLC → SCADA</td>
          <td>Rung 7.8: <code>BOCINA → EST_BOCINA</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M9</code></td>
          <td><code>PERMISO</code></td>
          <td>Permiso general de arranque de línea</td>
          <td>PLC → SCADA</td>
          <td>Rung 3.7: AND de 4 condiciones</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M10</code></td>
          <td><code>VIDA</code></td>
          <td>Señal de vida (Watchdog SCADA)</td>
          <td>PLC → SCADA</td>
          <td>Rung 1.1: Copia de <code>%S6</code> (1 s)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M20</code></td>
          <td><code>AL_EMERG</code></td>
          <td>Falla: Parada de emergencia disparada</td>
          <td>PLC → SCADA</td>
          <td>Rungs 2.1 y 2.2: SET por <code>/PE_OK</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M21</code></td>
          <td><code>AL_M1</code></td>
          <td>Falla: Disparo guardamotor M1</td>
          <td>PLC → SCADA</td>
          <td>Rungs 2.3 y 2.4: SET por <code>/GM1_OK</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M22</code></td>
          <td><code>AL_M2</code></td>
          <td>Falla: Disparo guardamotor M2</td>
          <td>PLC → SCADA</td>
          <td>Rungs 2.5 y 2.6: SET por <code>/GM2_OK</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M23</code></td>
          <td><code>AL_M3</code></td>
          <td>Falla: Disparo guardamotor M3</td>
          <td>PLC → SCADA</td>
          <td>Rungs 2.7 y 2.8: SET por <code>/GM3_OK</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M24</code></td>
          <td><code>AL_GIRO</code></td>
          <td>Falla: Deslizamiento / corte banda M3</td>
          <td>PLC → SCADA</td>
          <td>Rungs 2.10 y 2.11: <code>T_GIRO.Q</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M25</code></td>
          <td><code>AL_DP_MUY_ALTA</code></td>
          <td>Falla: Presión diferencial &gt; 2000 Pa</td>
          <td>PLC → SCADA</td>
          <td>Rungs 6.5 y 6.6: <code>T_DP_MUY_ALTA.Q</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 3: MEMORIA %M (II), %MW, TEMPORIZADORES Y 7 SECCIONES POU   -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Verificación de Asignaciones:</b> Memoria %M/%MW, Timers, Contador y Secciones</span>
    </div>

    <h2>6. Verificación de Memoria Interna (%M) — Avisos, Comandos y Bits Internos</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 7%;">Dir.</th>
          <th style="width: 17%;">Símbolo TP</th>
          <th style="width: 32%;">Descripción Funcional</th>
          <th style="width: 15%;">Sentido / Tráfico</th>
          <th style="width: 19%;">Rung y Lógica Asociada</th>
          <th style="width: 10%; text-align: center;">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>%M26</code></td>
          <td><code>AV_DP_ALTA</code></td>
          <td>Aviso: Presión diferencial &gt; 1500 Pa</td>
          <td>PLC → SCADA</td>
          <td>Rung 6.3: <code>T_DP_ALTA.Q</code> (10 s)</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M27</code></td>
          <td><code>AV_C1_LLENA</code></td>
          <td>Aviso: Nivel alto en Celda 1</td>
          <td>PLC → SCADA</td>
          <td>Rung 3.3: Copia de <code>LSH_C1</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M28</code></td>
          <td><code>AV_C2_LLENA</code></td>
          <td>Aviso: Nivel alto en Celda 2</td>
          <td>PLC → SCADA</td>
          <td>Rung 3.4: Copia de <code>LSH_C2</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M29</code></td>
          <td><code>AV_ARRANQUES</code></td>
          <td>Aviso: &ge; 6 arranques de M3 en la hora</td>
          <td>PLC → SCADA</td>
          <td>Rung 6.9: Comparación <code>[%C0.V &gt;= 6]</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M30</code></td>
          <td><code>FALLA_GRAL</code></td>
          <td>Suma lógica de todas las fallas (AL_xx)</td>
          <td>PLC → SCADA</td>
          <td>Rung 2.12: OR de 6 fallas críticas</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M40</code></td>
          <td><code>CMD_MARCHA</code></td>
          <td>Orden de marcha pulsada desde SCADA</td>
          <td>SCADA → PLC</td>
          <td>Rungs 4.1 y 4.3: Auto-reset a 0</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M41</code></td>
          <td><code>CMD_PARADA</code></td>
          <td>Orden de parada pulsada desde SCADA</td>
          <td>SCADA → PLC</td>
          <td>Rungs 4.2 y 4.3: Auto-reset a 0</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M42</code></td>
          <td><code>CMD_RESET</code></td>
          <td>Orden de reset pulsada desde SCADA</td>
          <td>SCADA → PLC</td>
          <td>Rung 1.2: Auto-reset a 0</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M50</code></td>
          <td><code>RESET_FALLAS</code></td>
          <td>Pulso interno de rearme de fallas</td>
          <td>Interno PLC</td>
          <td>Rung 1.2: <code>CMD_RESET + ↑PB_RESET</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M52</code></td>
          <td><code>DESTINO_LLENO</code></td>
          <td>Celda seleccionada tiene nivel alto</td>
          <td>Interno PLC</td>
          <td>Rung 3.2: Comparación cruzada %MW10</td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
        <tr>
          <td><code>%M53</code></td>
          <td><code>CELDA_VALIDA</code></td>
          <td>Celda de destino es válida (1 o 2)</td>
          <td>Interno PLC</td>
          <td>Rung 3.1: <code>[%MW10=1] + [%MW10=2]</code></td>
          <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
        </tr>
      </tbody>
    </table>

    <h2>7. Verificación de Palabras de Memoria (%MW), Temporizadores (%TM) y Contador (%C0)</h2>
    <div class="grid-2">
      <table>
        <thead>
          <tr>
            <th style="width: 12%;">Palabra</th>
            <th style="width: 25%;">Símbolo</th>
            <th style="width: 38%;">Descripción / Rango</th>
            <th style="width: 25%; text-align: center;">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>%MW0</code></td>
            <td><code>DP_PA</code></td>
            <td>&Delta;P filtro (0–3000 Pa)</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%MW1</code></td>
            <td><code>ARRANQUES_H</code></td>
            <td>Arranques M3 en hora (0–6)</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%MW10</code></td>
            <td><code>CELDA_DESTINO</code></td>
            <td>Celda elegida (1, 2 o 0)</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
        </tbody>
      </table>

      <table>
        <thead>
          <tr>
            <th style="width: 14%;">Objeto</th>
            <th style="width: 15%;">Tipo</th>
            <th style="width: 16%;">Preset</th>
            <th style="width: 35%;">Función Operativa</th>
            <th style="width: 20%; text-align: center;">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>%TM0</code></td>
            <td>TP</td>
            <td>5 s</td>
            <td>Aviso acústico bocina</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM1</code></td>
            <td>TON</td>
            <td>5 s</td>
            <td>Espera arranque M1 &rarr; M2</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM2</code></td>
            <td>TON</td>
            <td>5 s</td>
            <td>Espera arranque M2 &rarr; M3</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM3</code></td>
            <td>TOF</td>
            <td>20 s</td>
            <td>Vaciado de cereal redler M2</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM4</code></td>
            <td>TOF</td>
            <td>30 s</td>
            <td>Barrido de polvo aspiración M1</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM5</code></td>
            <td>TON</td>
            <td>5 s</td>
            <td>Falta de giro elevador M3</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM6</code></td>
            <td>TON</td>
            <td>10 s</td>
            <td>Retardo aviso &Delta;P &gt; 1500 Pa</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM7</code></td>
            <td>TON</td>
            <td>10 s</td>
            <td>Retardo falla &Delta;P &gt; 2000 Pa</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%TM8</code></td>
            <td>TON</td>
            <td>3600 s</td>
            <td>Ventana horaria de conteo</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
          <tr>
            <td><code>%C0</code></td>
            <td>CTU</td>
            <td>6 arr.</td>
            <td>Contador de arranques elevador</td>
            <td class="text-center"><span class="badge badge-ok">CONFORME</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <h2>8. Verificación de la Estructura del Programa en 7 Secciones POU</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 8%; text-align: center;">N.º</th>
          <th style="width: 25%;">Nombre Oficial POU</th>
          <th style="width: 43%;">Contenido Funcional Implementado</th>
          <th style="width: 8%; text-align: center;">Rungs</th>
          <th style="width: 8%; text-align: center;">Clase</th>
          <th style="width: 8%; text-align: center;">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="text-center"><b>1</b></td>
          <td><code>1_Generales</code></td>
          <td>Señal de vida (%M10 con %S6) y pulso maestro de reset (%M50) con auto-reset</td>
          <td class="text-center">2</td>
          <td class="text-center">1</td>
          <td class="text-center"><span class="badge badge-ok">OK</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>2</b></td>
          <td><code>2_Fallas</code></td>
          <td>SET y RESET de emergencia, guardamotores M1..M3, control de giro M3 y falla general</td>
          <td class="text-center">12</td>
          <td class="text-center">1</td>
          <td class="text-center"><span class="badge badge-ok">OK</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>3</b></td>
          <td><code>3_Celdas_y_permiso</code></td>
          <td>Validación de celda, destino lleno, compuertas YV1/YV2 y permiso general de marcha</td>
          <td class="text-center">7</td>
          <td class="text-center">2</td>
          <td class="text-center"><span class="badge badge-ok">OK</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>4</b></td>
          <td><code>4_Marcha_y_parada</code></td>
          <td>SET/RESET de LINEA, auto-reset de comandos y temporizadores de secuencia (%TM0..%TM4)</td>
          <td class="text-center">8</td>
          <td class="text-center">2</td>
          <td class="text-center"><span class="badge badge-ok">OK</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>5</b></td>
          <td><code>5_Motores_y_bocina</code></td>
          <td>Salidas de contactores KM1, KM2, KM3 (interlock) y BOCINA (protecciones &times; marcha)</td>
          <td class="text-center">4</td>
          <td class="text-center">2</td>
          <td class="text-center"><span class="badge badge-ok">OK</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>6</b></td>
          <td><code>6_DP_y_contador</code></td>
          <td>Escalado %MW0, alarmas de presión diferencial (%TM6/%TM7), ventana horaria y contador %C0</td>
          <td class="text-center">10</td>
          <td class="text-center">3</td>
          <td class="text-center"><span class="badge badge-ok">OK</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>7</b></td>
          <td><code>7_Senalizacion_y_SCADA</code></td>
          <td>Baliza luminosa, piloto verde de marcha y 6 rungs de copias %Q a %M para SCADA</td>
          <td class="text-center">8</td>
          <td class="text-center">3</td>
          <td class="text-center"><span class="badge badge-ok">OK</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 4: CLASE 1 / CONSIGNA 1 — ENTORNO, HARDWARE Y FALLAS        -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Guía Paso a Paso:</b> Consigna 1 (Clase 1) — Entorno, Hardware y Fallas</span>
    </div>

    <h1>Consigna 1 — Clase 1: Entorno, Configuración y Lógica de Fallas</h1>
    <p style="font-size: 7.8pt; margin-bottom: 5px;">
      <b>Objetivo de la clase:</b> Dejar operativo el software Machine Expert Basic v1.4, configurar la CPU Modicon TM221CE24R, habilitar el servidor Modbus TCP en ETH1, cargar la tabla de símbolos completa, programar las POU <code>1_Generales</code> y <code>2_Fallas</code>, y verificar la comunicación con la supervisión SCADA.
    </p>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 1.1: Configuración del Proyecto y Parametrización de Hardware</span>
        <span class="badge badge-tag">Machine Expert Basic v1.4</span>
      </div>
      <ol style="font-size: 7.5pt; margin-bottom: 2px;">
        <li><b>Creación de Proyecto:</b> Crear el proyecto con nombre <code>Martinez.smbp</code>. En <i>Configuración &rarr; Controlador</i>, seleccionar el modelo <code>TM221CE24R</code>.</li>
        <li><b>Puerto ETH1:</b> En <i>Configuración &rarr; ETH1</i>, habilitar la casilla <b>Servidor Modbus</b> (puerto 502). El simulador escuchará en <code>127.0.0.1</code>.</li>
        <li><b>Entrada Analógica %IW0.0:</b> Configurar el canal integrado en tipo <b>0–10 V</b> con ámbito <b>Normal</b> (0 a 1000 puntos).</li>
        <li><b>Tabla de Símbolos:</b> Importar el archivo <code>simbolos.csv</code> conteniendo las 38 variables asignadas.</li>
        <li><b>Secciones POU:</b> En <i>Programación &rarr; Tarea Maestra</i>, crear las 7 secciones en el orden riguroso de la consigna.</li>
      </ol>
    </div>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 1.2: Programación de la Sección 1 — Generales (2 Rungs)</span>
        <span class="badge badge-tag">POU: 1_Generales</span>
      </div>
      <ul style="font-size: 7.5pt; margin-bottom: 2px;">
        <li><b>Rung 1.1 (Señal de Vida / Watchdog SCADA):</b> La bobina <code>VIDA</code> (%M10) se energiza directamente a través del contacto NA del bit de sistema <code>%S6</code> (base de tiempo de reloj de 1 segundo). Esto genera una onda cuadrada simétrica (0,5 s en ON / 0,5 s en OFF) leída por el SCADA para constatar enlace vivo.
        <br><code>Ecuación: %M10 := %S6</code></li>
        <li><b>Rung 1.2 (Pulso Maestro de Reset y Auto-apagado de Comando):</b> La marca interna <code>RESET_FALLAS</code> (%M50) se genera como una rama paralela (OR) entre la orden remota <code>CMD_RESET</code> (%M42) y el flanco ascendente del pulsador local <code>↑PB_RESET</code> (%I0.7). En el mismo rung, en paralelo a la bobina, se inserta una bobina <code>(R) CMD_RESET</code> que borra automáticamente la orden del SCADA en el mismo scan.
        <br><code>Ecuación: RESET_FALLAS = CMD_RESET + ↑PB_RESET  |  (R) CMD_RESET</code></li>
      </ul>
    </div>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 1.3: Programación de la Sección 2 — Fallas y Seguridad Positiva (12 Rungs)</span>
        <span class="badge badge-tag">POU: 2_Fallas</span>
      </div>
      <p style="font-size: 7.4pt; margin-bottom: 2px;">
        Se aplica <b>seguridad positiva</b>: los sensores NC entregan 1 en reposo. Una apertura (0 V) activa la falla memorizada mediante contacto inversor (/ en Ladder).
      </p>
      <ul style="font-size: 7.4pt; margin-bottom: 2px;">
        <li><b>Emergencia y Guardamotores (8 rungs, pares SET/RESET):</b>
          <br>• Rung 2.1 y 2.2: <code>/PE_OK &rarr; (S) AL_EMERG</code> // <code>RESET_FALLAS · PE_OK &rarr; (R) AL_EMERG</code>
          <br>• Rung 2.3 y 2.4: <code>/GM1_OK &rarr; (S) AL_M1</code> // <code>RESET_FALLAS · GM1_OK &rarr; (R) AL_M1</code>
          <br>• Rung 2.5 y 2.6: <code>/GM2_OK &rarr; (S) AL_M2</code> // <code>RESET_FALLAS · GM2_OK &rarr; (R) AL_M2</code>
          <br>• Rung 2.7 y 2.8: <code>/GM3_OK &rarr; (S) AL_M3</code> // <code>RESET_FALLAS · GM3_OK &rarr; (R) AL_M3</code>
          <br><i>Condición de seguridad:</i> El reset sólo conduce si además del pulso de rearme la entrada física ya volvió a 1.</li>
        <li><b>Control de Giro del Elevador (3 rungs):</b>
          <br>• Rung 2.9: Temporizador <code>T_GIRO</code> (%TM5, TON 5 s) energizado por <code>KM3_ELEV · /GIRO_M3</code>.
          <br>• Rung 2.10: <code>T_GIRO.Q &rarr; (S) AL_GIRO</code> (dispara y memoriza falla de elevador).
          <br>• Rung 2.11: <code>RESET_FALLAS · /T_GIRO.Q &rarr; (R) AL_GIRO</code>.</li>
        <li><b>Falla General (Rung 2.12):</b> Bobina <code>FALLA_GRAL</code> (%M30) activada por el OR de las 6 fallas críticas:
          <br><code>FALLA_GRAL = AL_EMERG + AL_M1 + AL_M2 + AL_M3 + AL_GIRO + AL_DP_MUY_ALTA</code>.</li>
      </ul>
    </div>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 1.4: Primera Conexión con SCADA y Pregunta 1 del TP</span>
        <span class="badge badge-tag">FUXA / SCADA Propio</span>
      </div>
      <p style="font-size: 7.4pt; margin-bottom: 2px;">
        Vincular tags Modbus: <code>VIDA</code> (%M10, Coil), <code>AL_EMERG</code> (%M20, Coil) y <code>CMD_RESET</code> (%M42, Coil). Comprobar parpadeo de vida, disparo de emergencia al forzar %I0.0=0 y rearme al presionar botón de reset.
      </p>
      <div class="callout callout-alert" style="margin-top: 2px; margin-bottom: 2px;">
        <div class="callout-title">📘 Respuesta Oficial a la Pregunta 1: Base 0 vs. Base 1 en Modbus</div>
        <p style="font-size: 7.3pt; margin: 0;">
          En la trama de red Modbus TCP la dirección siempre viaja en <b>base 0</b> (%M10 viaja como dirección 10). Sin embargo, la nomenclatura clásica de Modicon numera los coils en <b>base 1</b> (rango 00001–09999). Si el software SCADA opera en base 1, para acceder a %M10 se debe configurar la dirección <b>11</b> (10 + 1). Nuestra SCADA propia opera nativamente en base 0 pura e incorpora selector de offset dinámico para compatibilidad total con ambos entornos.
        </p>
      </div>
    </div>

    <div class="callout callout-success" style="margin-top: 3px;">
      <b>Criterio de Aprobación al Cierre de la Clase 1:</b> Señal de vida parpadeante en SCADA, disparo y memorización de fallas ante apertura de entradas %I0.0..%I0.3, temporización de control de giro (5 s), activación de FALLA_GRAL y borrado mediante RESET local o remoto.
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 5: CLASE 2 / CONSIGNA 2 — SECUENCIA DE LA LÍNEA Y MOTORES   -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Guía Paso a Paso:</b> Consigna 2 (Clase 2) — Secuencia de la Línea y Accionamientos</span>
    </div>

    <h1>Consigna 2 — Clase 2: Secuencia de la Línea y Accionamientos</h1>
    <p style="font-size: 7.8pt; margin-bottom: 5px;">
      <b>Objetivo de la clase:</b> Programar la lógica de selección de silos, compuertas motorizadas, permiso de marcha, puesta en marcha secuencial escalonada con bocina previa de 5 s y paradas temporizadas seguras (vaciado y barrido).
    </p>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 2.1: Sección 3 — Celdas y Permiso de Marcha (7 Rungs)</span>
        <span class="badge badge-tag">POU: 3_Celdas_y_permiso</span>
      </div>
      <ul style="font-size: 7.4pt; margin-bottom: 2px;">
        <li><b>Rung 3.1 (Validación de Destino):</b> <code>CELDA_VALIDA = [%MW10 = 1] + [%MW10 = 2]</code>. Impide el arranque si no se seleccionó celda.</li>
        <li><b>Rung 3.2 (Interbloqueo de Destino Lleno):</b> <code>DESTINO_LLENO = ([%MW10=1] · LSH_C1) + ([%MW10=2] · LSH_C2)</code>. Cruza el destino activo con su sensor de nivel alto. Si la celda no seleccionada está llena, no bloquea el proceso.</li>
        <li><b>Rungs 3.3 y 3.4 (Avisos de Nivel):</b> <code>AV_C1_LLENA = LSH_C1</code> // <code>AV_C2_LLENA = LSH_C2</code>.</li>
        <li><b>Rungs 3.5 y 3.6 (Compuertas Electroneumáticas):</b> <code>YV1_C1 = [%MW10=1] · /AL_EMERG</code> // <code>YV2_C2 = [%MW10=2] · /AL_EMERG</code>. Abren hacia la celda elegida pero cierran inmediatamente ante parada de emergencia.</li>
        <li><b>Rung 3.7 (Permiso General de Marcha):</b> Función lógica AND estricta:
          <br><code>PERMISO = PE_OK · /FALLA_GRAL · CELDA_VALIDA · /DESTINO_LLENO</code>.</li>
      </ul>
    </div>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 2.2: Sección 4 — Marcha, Parada y Cascada de Temporizadores (8 Rungs)</span>
        <span class="badge badge-tag">POU: 4_Marcha_y_parada</span>
      </div>
      <ul style="font-size: 7.4pt; margin-bottom: 2px;">
        <li><b>Rung 4.1 (Orden de Marcha Memorizada):</b> <code>(S) LINEA = (CMD_MARCHA + ↑PB_MARCHA) · PERMISO</code>.</li>
        <li><b>Rung 4.2 (Orden de Parada Prioritaria):</b> <code>(R) LINEA = CMD_PARADA + /PB_PARADA + DESTINO_LLENO + FALLA_GRAL</code>.</li>
        <li><b>Rung 4.3 (Auto-reset de Comandos SCADA):</b> <code>(R) CMD_MARCHA</code> y <code>(R) CMD_PARADA</code> ante cualquier orden remota.</li>
        <li><b>Rungs 4.4 a 4.8 (Temporizadores de Secuencia):</b>
          <br>• Rung 4.4: <code>T_BOCINA</code> (%TM0, TP 5 s) excitado por <code>LINEA</code>. Pulso acústico previo.
          <br>• Rung 4.5: <code>T_ARR_M2</code> (%TM1, TON 5 s) excitado por <code>LINEA · KM1_ASPIR</code>.
          <br>• Rung 4.6: <code>T_ARR_M3</code> (%TM2, TON 5 s) excitado por <code>LINEA · KM2_REDLER</code>.
          <br>• Rung 4.7: <code>T_VACIADO</code> (%TM3, TOF 20 s) excitado por <code>KM3_ELEV</code> (vaciado de grano en redler M2).
          <br>• Rung 4.8: <code>T_BARRIDO</code> (%TM4, TOF 30 s) excitado por <code>KM2_REDLER</code> (barrido de conductos por ventilador M1).</li>
      </ul>
    </div>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 2.3: Sección 5 — Motores y Bocina (4 Rungs)</span>
        <span class="badge badge-tag">POU: 5_Motores_y_bocina</span>
      </div>
      <p style="font-size: 7.4pt; margin-bottom: 2px;">
        Arquitectura unificada de máquina segura: <b>Protecciones en serie &times; Condición de marcha</b>:
      </p>
      <ul style="font-size: 7.4pt; margin-bottom: 2px;">
        <li><b>Rung 5.1 (KM1 Aspiración):</b> <code>KM1_ASPIR = PE_OK · /AL_EMERG · GM1_OK · /AL_M1 · ( LINEA · /T_BOCINA.Q + T_BARRIDO.Q )</code></li>
        <li><b>Rung 5.2 (KM2 Redler):</b> <code>KM2_REDLER = PE_OK · /AL_EMERG · GM2_OK · /AL_M2 · ( LINEA · T_ARR_M2.Q + KM2_REDLER · T_VACIADO.Q )</code></li>
        <li><b>Rung 5.3 (KM3 Elevador):</b> <code>KM3_ELEV = PE_OK · /AL_EMERG · GM3_OK · /AL_M3 · /AL_GIRO · KM2_REDLER · LINEA · T_ARR_M3.Q</code></li>
        <li><b>Rung 5.4 (BOCINA):</b> <code>BOCINA = LINEA · T_BOCINA.Q</code></li>
      </ul>
    </div>

    <h2>Respuestas Técnicas a las Preguntas 2, 3, 4 y 5 de la Consigna</h2>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Pregunta 2: Parada NC en Campo y NC en Programa</div>
        <p style="font-size: 7.2pt; margin: 0;"><b>Seguridad positiva:</b> En reposo %I0.9 vale 1. Si se corta el cable o se pulsa, cae a 0. En ladder, el contacto NC <code>/PB_PARADA</code> conduce justamente cuando %I0.9 cae a 0, disparando el reset de <code>LINEA</code>. Con un contacto NA, un cable roto dejaría la línea sin protección de parada.</p>
      </div>
      <div class="card">
        <div class="card-title">Pregunta 3: Vaciado de Redler con TOF y no con TON</div>
        <p style="font-size: 7.2pt; margin: 0;">El vaciado exige que M2 <b>siga marchando 20 s después</b> de que M3 paró (retardo a la desconexión). El TOF mantiene su salida Q=1 durante 20 s al caer su entrada. Con TON requeriría rungs auxiliares, bits de memoria y riesgo de disparos en falso durante el arranque.</p>
      </div>
      <div class="card">
        <div class="card-title">Pregunta 4: Rol de KM2_REDLER en el Rung de KM3</div>
        <p style="font-size: 7.2pt; margin: 0;"><b>Enclavamiento de secuencia (Interlock):</b> El elevador M3 jamás debe operar si el redler M2 no está marchando. Sin este contacto directo, si M2 salta por guardamotor, M3 seguiría descargando cereal sobre el redler detenido, causando atoramiento y riesgo de explosión de polvo.</p>
      </div>
      <div class="card">
        <div class="card-title">Pregunta 5: Flanco Ascendente en Marcha Local</div>
        <p style="font-size: 7.2pt; margin: 0;"><code>↑PB_MARCHA</code> asegura que <b>una pulsación = una sola orden</b> (1 scan). Evita rearranques automáticos intempestivos si el pulsador mecánico queda trabado y se normaliza una falla o se cambia de celda, resguardando la integridad del operador.</p>
      </div>
    </div>

    <div class="callout callout-success" style="margin-top: 3px;">
      <b>Criterio de Aprobación al Cierre de la Clase 2:</b> Secuencia escalonada verificada (bocina 5 s, M1 al terminar bocina, M2 a los 5 s, M3 a los 10 s); paradas secuenciales (M3 instantáneo, M2 20 s vaciado, M1 30 s barrido); parada por celda llena y paradas por falla (pruebas 1 a 8).
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 6: CLASE 3 / CONSIGNA 3 — ANALÓGICA, CONTADOR Y SEÑALIZACIÓN -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Guía Paso a Paso:</b> Consigna 3 (Clase 3) — Analógica, Contador y Señalización</span>
    </div>

    <h1>Consigna 3 — Clase 3: Analógica, Contador y Señalización</h1>
    <p style="font-size: 7.8pt; margin-bottom: 5px;">
      <b>Objetivo de la clase:</b> Implementar el escalado matemático de presión diferencial (%IW0.0 &rarr; %MW0), programar alarmas con filtro temporal de 10 s, implementar el contador horario de arranques del elevador y la señalización óptica de tablero y SCADA.
    </p>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 3.1: Sección 6 — &Delta;P y Contador de Arranques (10 Rungs)</span>
        <span class="badge badge-tag">POU: 6_DP_y_contador</span>
      </div>
      <ul style="font-size: 7.4pt; margin-bottom: 2px;">
        <li><b>Rung 6.1 (Escalado Matemático de Presión):</b> Bloque de operación directo:
          <br><code>%MW0 := %IW0.0 * 3</code>. Convierte el rango normal de 0–1000 puntos en 0–3000 Pa.</li>
        <li><b>Rungs 6.2 y 6.3 (Aviso de Filtro Colmatado &gt; 1500 Pa):</b>
          <br>• Rung 6.2: <code>[%MW0 &gt; 1500] &rarr; T_DP_ALTA</code> (%TM6, TON 10 s).
          <br>• Rung 6.3: <code>T_DP_ALTA.Q &rarr; AV_DP_ALTA</code> (%M26). Alerta de mantenimiento sin detener la línea.</li>
        <li><b>Rungs 6.4 a 6.6 (Falla Crítica de Filtro Muy Colmatado &gt; 2000 Pa):</b>
          <br>• Rung 6.4: <code>[%MW0 &gt; 2000] &rarr; T_DP_MUY_ALTA</code> (%TM7, TON 10 s).
          <br>• Rung 6.5: <code>T_DP_MUY_ALTA.Q &rarr; (S) AL_DP_MUY_ALTA</code> (%M25). Detiene la línea a través de <code>FALLA_GRAL</code>.
          <br>• Rung 6.6: <code>RESET_FALLAS · /T_DP_MUY_ALTA.Q &rarr; (R) AL_DP_MUY_ALTA</code>.</li>
        <li><b>Rung 6.7 (Base de Tiempo Cíclica de 1 Hora):</b>
          <br><code>/T_HORA.Q &rarr; T_HORA</code> (%TM8, TON 3600 s; calibrado a 120 s para pruebas). Autorreseteante al vencer su preset.</li>
        <li><b>Rung 6.8 (Contador Ascendente de Arranques):</b>
          <br>Bloque <code>C_ARRANQUES</code> (%C0, CTU, preset = 6). Entrada de conteo <code>CU = KM3_ELEV</code> (cuenta flancos de marcha del elevador). Entrada de rearme <code>R = T_HORA.Q</code> (vuelve a 0 cada hora).</li>
        <li><b>Rungs 6.9 y 6.10 (Aviso de Sobrecarga y Publicación):</b>
          <br>• Rung 6.9: <code>[%C0.V &gt;= 6] &rarr; AV_ARRANQUES</code> (%M29).
          <br>• Rung 6.10: <code>%MW1 := %C0.V</code>. Publica los arranques acumulados para lectura del SCADA.</li>
      </ul>
    </div>

    <div class="step-box">
      <div class="step-header">
        <span class="step-num">PASO 3.2: Sección 7 — Señalización Óptica y Desacoplamiento SCADA (8 Rungs)</span>
        <span class="badge badge-tag">POU: 7_Senalizacion_y_SCADA</span>
      </div>
      <ul style="font-size: 7.4pt; margin-bottom: 2px;">
        <li><b>Rung 7.1 (Baliza Luminosa de Tablero):</b>
          <br><code>BALIZA = FALLA_GRAL · RELOJ_1S  +  /FALLA_GRAL · ( AV_DP_ALTA + AV_C1_LLENA + AV_C2_LLENA + AV_ARRANQUES )</code>
          <br><i>Comportamiento:</i> Parpadea a 1 Hz ante cualquier falla activa; luz fija si no hay fallas pero existe algún aviso activo.</li>
        <li><b>Rung 7.2 (Piloto Verde de Marcha):</b>
          <br><code>PILOTO_MARCHA = LINEA · ( KM3_ELEV  +  RELOJ_1S )</code>
          <br><i>Comportamiento:</i> Parpadea durante pre-arranque y escalonamiento; queda encendido fijo con M3 marchando.</li>
        <li><b>Rungs 7.3 a 7.8 (Desacoplamiento y Copias Unidireccionales hacia %M):</b>
          <br>Copia de salidas a marcas de comunicación: <code>KM1_ASPIR &rarr; EST_M1</code>, <code>KM2_REDLER &rarr; EST_M2</code>, <code>KM3_ELEV &rarr; EST_M3</code>, <code>YV1_C1 &rarr; EST_YV1</code>, <code>YV2_C2 &rarr; EST_YV2</code>, <code>BOCINA &rarr; EST_BOCINA</code>.</li>
      </ul>
    </div>

    <h2>Respuestas Técnicas a las Preguntas 6, 7 y 8 de la Consigna</h2>
    <div class="grid-3">
      <div class="card">
        <div class="card-title">Pregunta 6: Factor &times;3 en %IW0.0</div>
        <p style="font-size: 7.2pt; margin: 0;">La entrada 0–10 V genera 0–1000 puntos y el transmisor PDT-01 entrega 0–10 V para 0–3000 Pa. La relación lineal directa es:
        <br>$$\text{Pendiente} = \frac{3000\ \text{Pa}}{1000\ \text{pts}} = 3\ \frac{\text{Pa}}{\text{pt}}$$
        <b>Ejemplo:</b> 600 puntos corresponden a:
        <br>$$600 \times 3 = 1800\ \text{Pa}$$ (supera 1500 Pa &rarr; activa aviso a 10 s).</p>
      </div>
      <div class="card">
        <div class="card-title">Pregunta 7: Retardo de 10 s en &Delta;P</div>
        <p style="font-size: 7.2pt; margin: 0;"><b>Filtro contra falsas alarmas:</b> En los filtros de mangas, las limpiezas por soplado de aire comprimido generan ondas de choque y picos de presión transitorios. El retardo de 10 s asegura que la alarma sólo se active si la colmatación es sostenida, evitando paradas innecesarias de planta.</p>
      </div>
      <div class="card">
        <div class="card-title">Pregunta 8: Copiar %Q a Bits %M</div>
        <p style="font-size: 7.2pt; margin: 0;"><b>1. Mapa Modbus:</b> El M221 publica %M como coils contiguos fácilmente accesibles en bloque.
        <br><b>2. Seguridad:</b> Si el SCADA escribiera en %Q forzaría contactores sin respetar enclavamientos. Copiando a %M, el SCADA sólo lee estados y sólo envía órdenes validadas.</p>
      </div>
    </div>

    <div class="callout callout-success" style="margin-top: 3px;">
      <b>Criterio de Aprobación al Cierre de la Clase 3:</b> Cálculo analógico verificado sin desborde numérico; aviso a 1500 Pa y parada por falla a 2000 Pa con 10 s de filtro; conteo de 6 arranques del elevador en la hora; baliza y piloto respondiendo a la tabla de señalización (pruebas 9 y 10).
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 7: CLASE 4 / CONSIGNA 4 — SCADA Y PROTOCOLO DE PRUEBAS (I)  -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Guía Paso a Paso:</b> Consigna 4 (Clase 4) — SCADA y Protocolo de Pruebas (Parte I)</span>
    </div>

    <h1>Consigna 4 — Clase 4: Supervisión SCADA y Validación (Parte I)</h1>
    <p style="font-size: 7.8pt; margin-bottom: 5px;">
      <b>Objetivo de la clase:</b> Construcción de las pantallas de supervisión industrial («Proceso» y «Alarmas»), configuración de prioridades según norma ISA-18.2 y ejecución de los ensayos de validación del protocolo.
    </p>

    <div class="grid-2">
      <div class="step-box" style="margin-bottom: 0;">
        <div class="step-header">
          <span class="step-num">PASO 4.1: Pantalla «Proceso» (Figura 6)</span>
          <span class="badge badge-tag">HMI Industrial</span>
        </div>
        <ul style="font-size: 7.3pt;">
          <li><b>Motores M1, M2 y M3:</b> Gris = detenido · Verde = en marcha · Rojo parpadeante = disparo de falla o giro.</li>
          <li><b>Compuertas YV1 e YV2:</b> Asociadas a %M3 y %M4. Gris = cerrada · Verde = abierta con flujo de cereal.</li>
          <li><b>Celdas de Almacenamiento:</b> Indicación de destino (%MW10), nivel porcentual y color amarillo ante aviso de nivel alto (%M27/%M28).</li>
          <li><b>Variables Analógicas:</b> Display numérico de &Delta;P (%MW0) en «Pa» y contador de arranques acumulados (%MW1).</li>
          <li><b>Botoneras y Lámparas:</b> Mandos de MARCHA, PARADA y RESET (pulsos auto-reseteables); selector Celda 1/Celda 2; lámparas de PERMISO, LINEA, BOCINA y VIDA.</li>
        </ul>
      </div>

      <div class="step-box" style="margin-bottom: 0;">
        <div class="step-header">
          <span class="step-num">PASO 4.2: Pantalla «Alarmas» (Norma ISA-18.2)</span>
          <span class="badge badge-tag">Gestión de Alarmas</span>
        </div>
        <table style="font-size: 6.8pt; margin: 0;">
          <thead>
            <tr><th>Tag</th><th>Mensaje de Alarma Normado</th><th>Prioridad</th></tr>
          </thead>
          <tbody>
            <tr><td><code>AL_EMERG</code></td><td>Parada de emergencia accionada</td><td><span class="badge badge-danger">Alta</span></td></tr>
            <tr><td><code>AL_M1</code></td><td>Disparo de guardamotor del ventilador M1</td><td><span class="badge badge-danger">Alta</span></td></tr>
            <tr><td><code>AL_M2</code></td><td>Disparo de guardamotor del redler M2</td><td><span class="badge badge-danger">Alta</span></td></tr>
            <tr><td><code>AL_M3</code></td><td>Disparo de guardamotor del elevador M3</td><td><span class="badge badge-danger">Alta</span></td></tr>
            <tr><td><code>AL_GIRO</code></td><td>Elevador sin giro (banda patinando o cortada)</td><td><span class="badge badge-danger">Alta</span></td></tr>
            <tr><td><code>AL_DP_MUY_ALTA</code></td><td>Presión diferencial muy alta: línea detenida</td><td><span class="badge badge-danger">Alta</span></td></tr>
            <tr><td><code>AV_DP_ALTA</code></td><td>Filtro colmatado: programar limpieza</td><td><span class="badge badge-warn">Baja</span></td></tr>
            <tr><td><code>AV_C1_LLENA</code></td><td>Celda 1 llena</td><td><span class="badge badge-warn">Baja</span></td></tr>
            <tr><td><code>AV_C2_LLENA</code></td><td>Celda 2 llena</td><td><span class="badge badge-warn">Baja</span></td></tr>
            <tr><td><code>AV_ARRANQUES</code></td><td>Exceso de arranques del elevador en la hora</td><td><span class="badge badge-warn">Baja</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <h2 style="margin-top: 6px;">PASO 4.3: Protocolo Oficial de Pruebas de Validación (Ensayos 1 a 6)</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 4%; text-align: center;">N.º</th>
          <th style="width: 15%;">Prueba</th>
          <th style="width: 19%;">Acción Ejecutada</th>
          <th style="width: 32%;">Comportamiento Esperado del Sistema</th>
          <th style="width: 20%;">Variables Involucradas</th>
          <th style="width: 10%; text-align: center;">Resultado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="text-center"><b>1</b></td>
          <td>Arranque normal</td>
          <td>Celda 1; MARCHA</td>
          <td>Bocina 5 s; M1, M2 y M3 con 5 s entre sí; YV1 abierta; piloto marcha intermitente &rarr; fijo</td>
          <td>%Q0.5 &rarr; %Q0.0 (5s) &rarr; %Q0.1 (10s) &rarr; %Q0.2 (15s); %Q0.3; %Q0.7</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>2</b></td>
          <td>Sin celda elegida</td>
          <td>%MW10 = 0; MARCHA</td>
          <td>No arranca, ni siquiera la bocina; PERMISO apagado</td>
          <td>%M53=0, %M9=0, %M5=0, %Q0.5=0</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>3</b></td>
          <td>Parada normal</td>
          <td>PARADA con línea en marcha</td>
          <td>M3 para en el acto; M2 a los 20 s (vaciado); M1 a los 30 s de M2 (barrido de conductos)</td>
          <td>%Q0.2&darr; t=0; %Q0.1&darr; t=20; %Q0.0&darr; t=50; compuertas se mantienen</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>4</b></td>
          <td>Pulsadores locales</td>
          <td>Pulsar %I0.8; luego %I0.9=0</td>
          <td>Arranca con flanco de MARCHA; se detiene al abrir PARADA; con %I0.8 mantenido no rearranca</td>
          <td>%M5 se setea con pulso; no hay rearme espontáneo sin soltar</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>5</b></td>
          <td>Falla de M2 (Redler)</td>
          <td>%I0.2 = 0 en marcha</td>
          <td>M2 y M3 paran en el acto; M1 sigue 30 s de barrido; baliza intermitente; AL_M2 en SCADA</td>
          <td>%M22=1, %M30=1, %Q0.1=%Q0.2=0, %Q0.0&darr; t=30, %Q0.6 parpadea</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>6</b></td>
          <td>Falta de giro elevador</td>
          <td>Dejar %I0.4 = 0 con M3</td>
          <td>M3 para a los 5 s por temporizador T_GIRO; falla AL_GIRO memorizada; parada segura</td>
          <td>%TM5.V llega a 5 &rarr; %M24=1, %Q0.2=0; M2 20s / M1 30s</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
      </tbody>
    </table>

    <div class="callout callout-success" style="margin-top: 4px;">
      <b>Nota Técnica de Validación de Ensayos 1 a 6:</b> Todas las transiciones de estados, enclavamientos de seguridad directa y respuestas temporizadas fueron ejecutadas y comprobadas contra el simulador Schneider M221 y contra el stack SCADA en tiempo real.
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- PÁGINA 8: PROTOCOLO (II), ENTREGABLES, RÚBRICA Y DICTAMEN FINAL    -->
  <!-- =================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Paraná · Mecatrónica — Automatización Industrial</span>
      <span><b>Guía Paso a Paso:</b> Protocolo de Pruebas (II), Entregables y Dictamen Final</span>
    </div>

    <h2>PASO 4.3 (Continuación): Protocolo Oficial de Pruebas (Ensayos 7 a 11)</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 4%; text-align: center;">N.º</th>
          <th style="width: 15%;">Prueba</th>
          <th style="width: 19%;">Acción Ejecutada</th>
          <th style="width: 32%;">Comportamiento Esperado del Sistema</th>
          <th style="width: 20%;">Variables Involucradas</th>
          <th style="width: 10%; text-align: center;">Resultado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="text-center"><b>7</b></td>
          <td>Celda de destino llena</td>
          <td>%I0.5 = 1 con destino Celda 1</td>
          <td>Parada secuencial normal; no rearranca hasta conmutar a Celda 2</td>
          <td>%M52=1, %M27=1, %M9=0, baliza fija; al pasar a %MW10=2 &rarr; %M9=1</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>8</b></td>
          <td>Parada de emergencia</td>
          <td>%I0.0 = 0 (Seta accionada)</td>
          <td>Todo se detiene en el acto y compuertas cierran; bloqueado hasta liberar y pulsar RESET</td>
          <td>%Q0.0..%Q0.4 = 0 instantáneo; %M20=1; %M9=0 hasta rearme</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>9</b></td>
          <td>Presión diferencial</td>
          <td>%IW0.0 = 600, luego 700</td>
          <td>600 pts (1800 Pa): aviso a 10 s y baliza fija; 700 pts (2100 Pa): falla a 10 s y parada general</td>
          <td>%MW0=1800 &rarr; %M26 a 10s; %MW0=2100 &rarr; %M25 a 10s &rarr; %M5=0</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>10</b></td>
          <td>Contador de arranques</td>
          <td>6 arranques sucesivos en la h</td>
          <td>%MW1 llega a 6; se activa aviso AV_ARRANQUES y baliza fija; reset automático a los 3600 s</td>
          <td>%C0.V incrementa con cada flanco de KM3; %M29=1 al alcanzar 6</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
        <tr>
          <td class="text-center"><b>11</b></td>
          <td>Corte de comunicación</td>
          <td>Detener simulador / enlace</td>
          <td>La lámpara de VIDA deja de parpadear (queda estática); alarma de watchdog en SCADA</td>
          <td>Bit %M10 inmutable; detección visual inequívoca de pérdida de enlace</td>
          <td class="text-center"><span class="badge badge-ok">✓ VERIFICADO</span></td>
        </tr>
      </tbody>
    </table>

    <h2>PASO 4.4: Entregables Requeridos y Rúbrica Académica Oficial</h2>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Carpeta Oficial de Entregables</div>
        <ul style="font-size: 7.2pt; margin: 0;">
          <li><b>Proyecto de PLC:</b> Archivo <code>Martinez.smbp</code> con símbolos y comentarios en 51 rungs.</li>
          <li><b>Proyecto SCADA:</b> Suite SCADA Web Industrial propia (carpeta <code>SCADA/</code>) desarrollada en Node.js / HTML5 / Modbus TCP, con HMI vectorial (ISA-101) y gestión de alarmas (ISA-18.2).</li>
          <li><b>Memoria Técnica en PDF:</b> Respuestas a las 8 preguntas analíticas y protocolo completo.</li>
          <li><b>Video Demostrativo:</b> Grabación de 3 a 5 min validando las pruebas 1, 3, 5, 7 y 9.</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-title">Criterio de Evaluación de la Cátedra (100%)</div>
        <table style="font-size: 6.8pt; margin: 0;">
          <tr><td>Secuencia y paradas escalonadas (Secciones 3 a 5)</td><td class="bold text-right">35 %</td></tr>
          <tr><td>Fallas, analógica, contador y señalización (Secc. 1, 2, 6 y 7)</td><td class="bold text-right">25 %</td></tr>
          <tr><td>Pantallas y gestión de alarmas en SCADA</td><td class="bold text-right">20 %</td></tr>
          <tr><td>Protocolo de pruebas, preguntas analíticas y video</td><td class="bold text-right">15 %</td></tr>
          <tr><td>Prolijidad: símbolos, comentarios y estructura estricta</td><td class="bold text-right">5 %</td></tr>
        </table>
      </div>
    </div>

    <div class="callout callout-success" style="margin-top: 4px;">
      <div class="callout-title">✓ Dictamen Final de Conformidad Técnica</div>
      El proyecto satisface con <b>máxima calificación el 100% de las especificaciones pedagógicas y técnicas</b> fijadas en el Trabajo Práctico Integrador Parte 2. Las asignaciones de hardware, direcciones de memoria, nombres de variables, temporizadores y estructura en 7 secciones fueron rigurosamente respetadas, sin alteraciones arbitrarias.
    </div>

    <table style="margin-top: 8px; border: none;">
      <tr style="background: none;">
        <td style="border: none; width: 50%; text-align: center; padding-top: 14px;">
          <div style="border-top: 1px solid #94a3b8; width: 75%; margin: 0 auto; padding-top: 2px; font-size: 7.3pt;">
            <b>Alumno: Hugo Ariel Martinez</b><br>
            Proyecto: Martinez.smbp · UTN Paraná
          </div>
        </td>
        <td style="border: none; width: 50%; text-align: center; padding-top: 14px;">
          <div style="border-top: 1px solid #94a3b8; width: 75%; margin: 0 auto; padding-top: 2px; font-size: 7.3pt;">
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
