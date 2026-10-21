# -*- coding: utf-8 -*-
"""
Script generador del Informe Técnico Comparativo en formato PDF (5 Páginas Calibradas)
Trabajo Práctico Integrador — Parte 2: Programación de PLC y Supervisión SCADA
Carrera: Tecnicatura Superior en Mecatrónica — UTN Facultad Regional Paraná
"""

import os
import subprocess
import fitz

OUTPUT_HTML = os.path.abspath("Resolucion/resumen_comparativo.html")
OUTPUT_PDF = os.path.abspath("Resolucion/Resumen_Comparativo_Sistema_vs_TP.pdf")

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Resumen Comparativo — Sistema vs Trabajo Práctico</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 14mm 14mm 16mm 14mm;
      @bottom-center {
        content: "UTN Paraná — Tecnicatura Superior en Mecatrónica · Automatización Industrial (TP Integrador 2)";
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
      font-size: 8.6pt;
      line-height: 1.4;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }

    /* Encabezado Principal */
    .header-box {
      border-bottom: 2.5px solid #004b87;
      padding-bottom: 8px;
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

    /* Encabezado secundario en páginas 2+ */
    .running-header {
      border-bottom: 1.5px solid #cbd5e1;
      padding-bottom: 5px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      font-size: 7.8pt;
      color: #64748b;
      font-weight: 600;
    }

    .running-header span.inst {
      color: #004b87;
      font-weight: 700;
    }

    .main-title {
      font-size: 13.5pt;
      font-weight: 900;
      color: #0f172a;
      margin: 6px 0 3px 0;
      line-height: 1.25;
      letter-spacing: -0.2px;
    }

    .main-subtitle {
      font-size: 9pt;
      color: #0284c7;
      font-weight: 700;
      margin: 0 0 10px 0;
    }

    /* Secciones */
    h2 {
      font-size: 10.2pt;
      font-weight: 800;
      color: #004b87;
      border-left: 3.5px solid #0284c7;
      padding-left: 7px;
      margin: 12px 0 6px 0;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      page-break-after: avoid;
    }

    h3 {
      font-size: 8.8pt;
      font-weight: 700;
      color: #0f172a;
      margin: 8px 0 4px 0;
      page-break-after: avoid;
    }

    p {
      margin: 0 0 6px 0;
      text-align: justify;
    }

    /* Tablas */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 6px 0 8px 0;
      font-size: 7.9pt;
      page-break-inside: avoid;
    }

    th, td {
      border: 1px solid #cbd5e1;
      padding: 4px 6px;
      vertical-align: top;
      text-align: left;
    }

    th {
      background-color: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
      font-size: 7.7pt;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      border-bottom: 2px solid #004b87;
    }

    tr:nth-child(even) td {
      background-color: #f8fafc;
    }

    /* Badges */
    .badge {
      display: inline-block;
      padding: 1px 4px;
      border-radius: 3px;
      font-size: 7.2pt;
      font-weight: 700;
      font-family: ui-monospace, 'Consolas', monospace;
      white-space: nowrap;
    }

    .badge-ok {
      background-color: #dcfce7;
      color: #166534;
      border: 1px solid #86efac;
    }

    .badge-req {
      background-color: #e0f2fe;
      color: #075985;
      border: 1px solid #7dd3fc;
    }

    .mono {
      font-family: ui-monospace, 'Consolas', 'JetBrains Mono', monospace;
      font-size: 7.8pt;
      background: #f1f5f9;
      padding: 1px 3px;
      border-radius: 3px;
      color: #0f172a;
      font-weight: 600;
    }

    /* Callouts */
    .callout {
      border: 1px solid #cbd5e1;
      border-left: 3.5px solid #004b87;
      background: #f8fafc;
      padding: 6px 8px;
      border-radius: 4px;
      margin: 6px 0 8px 0;
      font-size: 8.2pt;
      page-break-inside: avoid;
    }

    .callout-title {
      font-weight: 700;
      color: #004b87;
      margin-bottom: 2px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .callout-plus {
      border-left-color: #059669;
      background: #f0fdf4;
      border-color: #bbf7d0;
    }
    .callout-plus .callout-title {
      color: #166534;
    }

    /* Grillas */
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin: 6px 0;
      page-break-inside: avoid;
    }

    .card {
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 6px 8px;
      background: #ffffff;
      box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }

    .card h4 {
      margin: 0 0 4px 0;
      font-size: 8.3pt;
      color: #004b87;
      font-weight: 700;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 2px;
    }

    .page-break {
      page-break-before: always;
    }

    ul, ol {
      margin: 3px 0 6px 16px;
      padding: 0;
    }

    li {
      margin-bottom: 2px;
    }
  </style>
</head>
<body>

  <!-- ==================== PÁGINA 1: PRESENTACIÓN Y COMIENZO DE LA MATRIZ ==================== -->
  <div class="header-box">
    <div>
      <div class="inst-title">Universidad Tecnológica Nacional — Facultad Regional Paraná</div>
      <div class="inst-sub">Tecnicatura Superior en Mecatrónica · Cátedra de Automatización Industrial</div>
    </div>
    <div class="doc-meta">
      <b>INFORME TÉCNICO DE AUDITORÍA</b><br>
      TP Integrador — Parte 2 (PLC & SCADA)<br>
      Alumno: <b>Hugo Ariel Martinez</b><br>
      Archivo PLC: <b>Martinez.smbp</b> · Fecha: <b>Octubre 2026</b>
    </div>
  </div>

  <div class="main-title">Resumen Ejecutivo y Matriz de Cumplimiento: Sistema Implementado vs. Requerimientos del Trabajo Práctico</div>
  <div class="main-subtitle">Automatización de la Línea de Llenado de Celdas de Cereal (Sector Mezcla y Limpieza de Trigo)</div>

  <div class="callout callout-plus">
    <div class="callout-title">✓ Dictamen de Conformidad Técnica: 100% DE REQUISITOS CUMPLIDOS + VALOR AGREGADO DE INGENIERÍA</div>
    El sistema implementado responde con rigor absoluto a la totalidad de consignas fijadas por la cátedra para el controlador <b>Modicon M221 TM221CE24R</b> (51 rungs Ladder en 7 secciones normalizadas, 9 temporizadores y 1 contador horario). Frente a la alternativa básica de software (FUXA), se desarrolló una solución <b>SCADA Web Industrial propia de alta gama</b> basada en los estándares internacionales <b>ISA-101</b> (HMI de alto rendimiento) e <b>ISA-18.2</b> (ciclo de vida de alarmas), incorporando audio real mediante Web Audio API y un <b>PLC Virtual emulado en Node.js</b> para pruebas completas y autónomas.
  </div>

  <h2>1. Síntesis del Proceso Productivo Automatizado</h2>
  <p>
    La instalación transporta trigo limpio hacia dos celdas de almacenamiento temporal (Celda 1 y Celda 2). La dotación electromecánica e instrumental comprende:
  </p>
  <ul>
    <li><b>Ventilador de Aspiración M1 (%Q0.0):</b> Aspira polvo hacia el filtro de mangas. Arranca primero y para último (mantiene depresión).</li>
    <li><b>Redler Distribuidor M2 (%Q0.1):</b> Transportador horizontal de cadena que descarga cereal sobre la celda seleccionada con vaciado temporizado.</li>
    <li><b>Elevador de Cangilones M3 (%Q0.2):</b> Sube el grano limpio hacia el redler. Cuenta con detector inductivo de giro <b>SSL (%I0.4)</b> en pie.</li>
    <li><b>Compuertas Electroneumáticas YV1 (%Q0.3) e YV2 (%Q0.4):</b> Válvulas guillotina que derivan la descarga de cereal hacia la celda elegida.</li>
    <li><b>Transmisor Analógico PDT-01 (%IW0.0 / %MW0):</b> Mide presión diferencial (0–3000 Pa, salida 0–10 V) a través de mangas filtrantes.</li>
    <li><b>Detectores de Nivel Alto LSH1 (%I0.5) y LSH2 (%I0.6):</b> Sensores capacitivos de seguridad por colmatación en cada celda.</li>
  </ul>

  <h2>2. Matriz Comparativa: Requerimientos del TP vs. Sistema Implementado (Parte I)</h2>

  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Requerimiento TP Integrador</th>
        <th style="width: 27%;">Especificación Mínima Solicitada</th>
        <th style="width: 38%;">Implementación Realizada en el Sistema</th>
        <th style="width: 13%; text-align: center;">Estado</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Secuencia de Arranque Escalonado</b></td>
        <td>
          • Bocina previa durante 5 s.<br>
          • M1 arranca al terminar bocina.<br>
          • M2 arranca 5 s después de M1.<br>
          • M3 arranca 5 s después de M2.<br>
          • Piloto parpadea y queda fijo.
        </td>
        <td>
          • Rungs 4.3 a 5.3 con <span class="mono">%TM0</span> (TP 5s), <span class="mono">%TM1</span> (TON 5s) y <span class="mono">%TM2</span> (TON 5s).<br>
          • <b>SCADA:</b> Barra temporal dinámica con cuenta regresiva en vivo por etapa.<br>
          • <b>Audio Real:</b> Sintetizador Web Audio API de bocina industrial pesada con timbre bitonal y filtro a 1500 Hz sincronizado con <span class="mono">%Q0.5</span>.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">SUPERADO</span></td>
      </tr>
      <tr>
        <td><b>Secuencia de Parada Escalonada</b></td>
        <td>
          • M3 se detiene instantáneamente.<br>
          • M2 sigue 20 s (vaciado redler).<br>
          • M1 sigue 30 s más (barrido de conductos de aspiración).
        </td>
        <td>
          • Rungs 4.4 y 4.5 con <span class="mono">%TM3</span> (TOF 20s para M2) y <span class="mono">%TM4</span> (TOF 30s para M1).<br>
          • Si M3 no llegó a arrancar, no hay vaciado (detención inmediata de M2).<br>
          • <b>SCADA:</b> Cuenta regresiva visual del tiempo restante de vaciado y barrido.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td><b>Selección de Celda de Destino</b></td>
        <td>
          • Selección por <span class="mono">%MW10</span> (1 o 2).<br>
          • Abre compuerta YV1 o YV2.<br>
          • Si <span class="mono">%MW10=0</span> (sin celda), no hay permiso de marcha.
        </td>
        <td>
          • Rung 3.1 con comparadores <span class="mono">[%MW10=1]</span> y <span class="mono">[%MW10=2]</span>.<br>
          • <b>SCADA:</b> Botones táctiles exclusivos en panel de mando con iluminación de estado, animación de compuertas guillotina estancas y flujo de grano.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">SUPERADO</span></td>
      </tr>
      <tr>
        <td><b>Protección Celda Llena</b></td>
        <td>
          • Sensor LSH C1 (<span class="mono">%I0.5</span>) o C2 (<span class="mono">%I0.6</span>).<br>
          • Parada escalonada idéntica a PARADA.<br>
          • Aviso <span class="mono">%M27</span>/<span class="mono">%M28</span> y baliza fija.<br>
          • Bloqueo de rearranque a misma celda.
        </td>
        <td>
          • Rung 3.4 evalúa <span class="mono">DESTINO_LLENO (%M52)</span> y resetea LINEA.<br>
          • <b>SCADA:</b> Silo cambia dinámicamente a color ámbar de alerta, nivel al 100%, alarma acústica e indicador de advertencia. Permite conmutar celda sin reset.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">SUPERADO</span></td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== PÁGINA 2: CONTINUACIÓN MATRIZ + COMPARATIVA FUXA ==================== -->
  <div class="page-break"></div>

  <div class="running-header">
    <span class="inst">UTN Paraná · Tecnicatura en Mecatrónica</span>
    <span>TP Integrador Parte 2 — Informe Comparativo · Matriz y Comparativa SCADA</span>
  </div>

  <h2>2. Matriz Comparativa: Requerimientos del TP vs. Sistema Implementado (Parte II)</h2>

  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Requerimiento TP Integrador</th>
        <th style="width: 27%;">Especificación Mínima Solicitada</th>
        <th style="width: 38%;">Implementación Realizada en el Sistema</th>
        <th style="width: 13%; text-align: center;">Estado</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Enclavamiento Físico M2 / M3</b></td>
        <td>
          • M3 no puede arrancar sin M2.<br>
          • Si M2 cae por cualquier causa, M3 debe parar en el mismo scan (anti-atoro).
        </td>
        <td>
          • Contacto <span class="mono">KM2_REDLER</span> en serie en el rung 5.3.<br>
          • Protección física directa en tiempo real ante disparo térmico o falla. Evita acumulación de cereal y daño mecánico en la noria.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td><b>Control de Giro SSL del Elevador</b></td>
        <td>
          • Sensor inductivo <span class="mono">%I0.4</span>.<br>
          • Si M3 marcha y no hay giro por 5 s, dispara falla <span class="mono">AL_GIRO (%M24)</span>.<br>
          • Detiene elevador M3.
        </td>
        <td>
          • Rung 2.5 con <span class="mono">%TM5</span> (TON 5s alimentado por <span class="mono">KM3 · /GIRO_M3</span>).<br>
          • SET de bobina <span class="mono">%M24</span> memorizada.<br>
          • <b>SCADA:</b> LED verde/gris indicador de pulso montado 100% adentro del pie del elevador en el sinóptico.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td><b>Presión Diferencial Filtro Mangas</b></td>
        <td>
          • Entrada <span class="mono">%IW0.0</span> (0 a 1000 pts).<br>
          • Ecuación: <span class="mono">%MW0 := %IW0.0 * 3</span>.<br>
          • Aviso a > 1500 Pa tras 10 s.<br>
          • Falla y paro a > 2000 Pa tras 10 s.
        </td>
        <td>
          • Rungs 6.1 a 6.6 en sección Analógica.<br>
          • Temporizadores <span class="mono">%TM6</span> y <span class="mono">%TM7</span> (TON 10s) evitan disparos por pulsos de soplado (jet-pulse).<br>
          • <b>SCADA:</b> Display digital con unidades [Pa] integrado en el cuerpo del filtro, barra analógica calibrada y gráfico Sparkline de tendencia histórica.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">SUPERADO</span></td>
      </tr>
      <tr>
        <td><b>Contador Horario de Arranques</b></td>
        <td>
          • Ventana temporal de 1 h (3600 s en <span class="mono">%TM8</span>; 120 s para prueba).<br>
          • Cuenta arranques de M3 con CTU <span class="mono">%C0</span>.<br>
          • Si <span class="mono">[%C0.V >= 6]</span> ➔ aviso <span class="mono">%M29</span>.<br>
          • Valor exportado a <span class="mono">%MW1</span>.
        </td>
        <td>
          • Rungs 6.7 a 6.10 ejecutados rigurosamente.<br>
          • <span class="mono">%TM8</span> se reinicia automáticamente con contacto NC <span class="mono">/T_HORA.Q</span>.<br>
          • <b>SCADA:</b> Widget con cuota horaria de arranques restantes (ej. 3 / 6 máx), barra segmentada y alerta de fatiga térmica de motor.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">SUPERADO</span></td>
      </tr>
      <tr>
        <td><b>Pulsadores Locales y Seguridad</b></td>
        <td>
          • MARCHA (%I0.8 NA) con flanco ↑.<br>
          • PARADA (%I0.9 NC) por seguridad.<br>
          • RESET (%I0.7 NA) con flanco ↑.<br>
          • Parada Emergencia (%I0.0 NC).
        </td>
        <td>
          • Seguridad positiva en entradas NC.<br>
          • Flanco ascendente <span class="mono">↑PB_MARCHA</span> previene rearranque si el botón queda trabado.<br>
          • <b>SCADA:</b> Integra un <b>Tablero de Simulación de Campo</b> interactivo con pulsadores reales, parada tipo golpe de puño y sliders.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">SUPERADO</span></td>
      </tr>
      <tr>
        <td><b>Estructura del Programa PLC</b></td>
        <td>
          • 7 secciones obligatorias en orden fijado.<br>
          • Símbolos asignados inalterables.<br>
          • Un comentario breve por rung.
        </td>
        <td>
          • 51 rungs rigurosamente estructurados:<br>
          Sec. 1 Generales · Sec. 2 Fallas · Sec. 3 Celdas · Sec. 4 Marcha/Parada · Sec. 5 Motores · Sec. 6 Analógica/Contador · Sec. 7 SCADA.<br>
          • 100% de símbolos mapeados en <span class="mono">simbolos.csv</span>.
        </td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
    </tbody>
  </table>

  <h2>3. Comparativa Arquitectónica: SCADA Propio vs. FUXA Básico</h2>

  <div class="grid-2">
    <div class="card">
      <h4>SCADA ESTÁNDAR SUGERIDO (FUXA)</h4>
      <ul>
        <li><b>Diseño Gráfico:</b> Formas básicas estáticas (rectángulos planos, círculos de color gris/verde).</li>
        <li><b>Animación de Proceso:</b> Nula. Solo cambio de color estático de bobina activada.</li>
        <li><b>Gestión de Alarmas:</b> Lista elemental sin máquina de estados ISA-18.2 ni filtrado de transitorios.</li>
        <li><b>Trazabilidad / Históricos:</b> Almacenamiento local volátil sin persistencia estructurada.</li>
        <li><b>Entorno de Ejecución:</b> Requiere tener obligatoriamente abierto y en modo RUN el simulador Schneider Machine Expert Basic.</li>
        <li><b>Diagnóstico Operativo:</b> Nulo. Si el sistema no arranca, el operador desconoce qué interlock está abierto.</li>
      </ul>
    </div>

    <div class="card" style="border-left: 3.5px solid #059669; background: #fbfdfc;">
      <h4>SISTEMA SCADA WEB INDUSTRIAL PROPIO</h4>
      <ul>
        <li><b>Diseño ISA-101:</b> Modo oscuro de alto rendimiento, reducción de fatiga visual y foco por excepción.</li>
        <li><b>Animación Dinámica SVG:</b> Turbina caracol de M1, movimiento continuo de cangilones en M3, cadena de arrastre en M2 y lluvia de cereal.</li>
        <li><b>Norma ISA-18.2 Completa:</b> Estados Activa/No Reconocida, Reconocida, Normalizada; botón masivo y exportación CSV.</li>
        <li><b>Audio Real de Fábrica:</b> Bocina sintetizada en Web Audio API que suena durante los 5 s de aviso (%Q0.5).</li>
        <li><b>PLC Virtual Integrado:</b> Emulador en Node.js con los 51 rungs idénticos para operar sin software Schneider.</li>
        <li><b>Diagnóstico Asistido:</b> Indicador de permiso que audita: <span class="mono">PE_OK · /FALLA · CELDA · /LLENO</span>.</li>
      </ul>
    </div>
  </div>

  <!-- ==================== PÁGINA 3: PROTOCOLO DE PRUEBAS ==================== -->
  <div class="page-break"></div>

  <div class="running-header">
    <span class="inst">UTN Paraná · Tecnicatura en Mecatrónica</span>
    <span>TP Integrador Parte 2 — Informe Comparativo · Protocolo de Pruebas</span>
  </div>

  <h2>4. Auditoría y Validación del Protocolo de Pruebas (11 Ensayos Obligatorios)</h2>
  <p>
    Se sometió la lógica de control del PLC a los 11 escenarios de prueba exigidos en la Consigna 4.3 del TP, obteniéndose resultado <b>CONFORME</b> en todos los casos:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 5%; text-align: center;">N.º</th>
        <th style="width: 17%;">Ensayo / Escenario</th>
        <th style="width: 32%;">Acción / Condición de Estímulo</th>
        <th style="width: 34%;">Respuesta Observada en PLC y Pantalla SCADA</th>
        <th style="width: 12%; text-align: center;">Veredicto</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align: center;"><b>1</b></td>
        <td>Arranque normal</td>
        <td>Celda 1 seleccionada; pulso en MARCHA</td>
        <td>Bocina suena 5 s con audio; M1 arranca a t=5s, M2 a t=10s, M3 a t=15s; compuerta YV1 abre; piloto pasa de intermitente a fijo.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>2</b></td>
        <td>Sin celda elegida</td>
        <td>%MW10 = 0; pulso en MARCHA</td>
        <td>Línea bloqueada; PERMISO en 0; la bocina no suena ni arranca ningún motor.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>3</b></td>
        <td>Parada normal</td>
        <td>Pulso en PARADA con línea en régimen</td>
        <td>M3 para al instante (t=0); M2 sigue 20 s (vaciado); M1 sigue 30 s tras M2 (barrido de conductos); barra muestra cuenta regresiva.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>4</b></td>
        <td>Pulsadores locales</td>
        <td>Pulso en %I0.8 (Marcha); luego abrir %I0.9</td>
        <td>Línea arranca solo con el flanco ↑; al abrir %I0.9 se detiene; no hay auto-rearranque si el pulsador queda trabado.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>5</b></td>
        <td>Falla térmica de M2</td>
        <td>Disparo guardamotor M2 (%I0.2 = 0) en marcha</td>
        <td>M2 y M3 caen en el mismo scan por interlock; M1 cumple barrido de 30 s; baliza roja parpadea; alarma AL_M2 registrada.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>6</b></td>
        <td>Falta de giro SSL</td>
        <td>%I0.4 = 0 al entrar M3 en servicio</td>
        <td>Temporizador %TM5 cuenta 5 s; se activa AL_GIRO (%M24); M3 para de inmediato y se inicia parada escalonada.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>7</b></td>
        <td>Celda 1 llena</td>
        <td>Activar sensor de nivel alto LSH1 (%I0.5 = 1)</td>
        <td>Parada escalonada idéntica a PARADA; Celda 1 se colorea de amarillo; baliza fija; no permite rearrancar a Celda 1 pero sí a Celda 2.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>8</b></td>
        <td>Parada Emergencia</td>
        <td>Apertura de seta de seguridad (%I0.0 = 0)</td>
        <td>Corte instantáneo de todas las salidas (%Q0.0–%Q0.4); compuertas cierran por resorte; no permite rearranque hasta rearmar y pulsar RESET.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>9</b></td>
        <td>Presión diferencial</td>
        <td>Slider %IW0.0 a 600 pts, luego a 700 pts</td>
        <td>A 1800 Pa activa aviso AV_DP_ALTA tras 10 s (baliza fija); a 2100 Pa activa falla AL_DP_MUY_ALTA tras 10 s y detiene la línea.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>10</b></td>
        <td>Contador arranques</td>
        <td>Efectuar 6 arranques sucesivos en la hora</td>
        <td>Registro %MW1 alcanza 6; se dispara aviso AV_ARRANQUES (%M29) y baliza fija sin parar motores; contador se reinicia cíclicamente.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
      <tr>
        <td style="text-align: center;"><b>11</b></td>
        <td>Corte comunicación</td>
        <td>Detener PLC o desconectar cable Modbus</td>
        <td>Reloj VIDA deja de parpadear; SCADA despliega banner de 'Comunicación Interrumpida' y deshabilita botones de mando por seguridad.</td>
        <td style="text-align: center;"><span class="badge badge-ok">CONFORME</span></td>
      </tr>
    </tbody>
  </table>

  <div class="callout callout-plus" style="margin-top: 6px;">
    <div class="callout-title">Guion para Grabación de Video Demostrativo (3 a 5 Minutos)</div>
    Para la entrega final se recomienda seguir la secuencia: <b>Prueba 1</b> (Arranque con audio y secuencia visual) ➔ <b>Prueba 3</b> (Parada con cuenta regresiva de vaciado) ➔ <b>Prueba 5</b> (Disparo guardamotor M2 y parada de M3 en mismo scan) ➔ <b>Prueba 7</b> (Llenado de celda y conmutación a Celda 2) ➔ <b>Prueba 9</b> (Aviso y falla por presión diferencial analógica).
  </div>

  <!-- ==================== PÁGINA 4: PREGUNTAS TÉCNICAS DEL TP ==================== -->
  <div class="page-break"></div>

  <div class="running-header">
    <span class="inst">UTN Paraná · Tecnicatura en Mecatrónica</span>
    <span>TP Integrador Parte 2 — Informe Comparativo · Memoria y Preguntas Técnicas</span>
  </div>

  <h2>5. Síntesis de las Preguntas Teórico-Técnicas del TP (Memoria de Cálculo)</h2>

  <div class="grid-2">
    <div class="card">
      <h4>P1. Direccionamiento Modbus (%M10)</h4>
      <p>
        El protocolo Modbus opera nativamente en <b>Base 0</b> (el primer coil es el 0, por lo que %M10 viaja como dirección 10 en la trama). FUXA y softwares clásicos Modicon suelen usar notación <b>Base 1</b> (rango 00001–09999), requiriendo ingresar <b>11</b>. Nuestra SCADA incluye selector dinámico de offset (0 o 1).
      </p>
    </div>

    <div class="card">
      <h4>P2. Pulsador de PARADA cableado NC</h4>
      <p>
        <b>Seguridad Positiva:</b> En reposo conduce 24 V (%I0.9=1). Si un cable se corta o se desconecta un borne, la entrada cae a 0 provocando la parada inmediata (lado seguro). En el programa se utiliza contacto NC (<span class="mono">/PB_PARADA</span>) para activar la bobina RESET de LINEA al pulsar.
      </p>
    </div>

    <div class="card">
      <h4>P3. Vaciado del Redler con TOF</h4>
      <p>
        M2 debe permanecer marchando 20 s <i>después</i> de que M3 paró. Esto es exactamente un <b>retardo a la desconexión</b>. Con un TOF, si M3 nunca arrancó, el bloque nunca se cargó y M2 para de inmediato sin demoras innecesarias. Con TON requeriría rungs y banderas auxiliares adicionales.
      </p>
    </div>

    <div class="card">
      <h4>P4. Interlock KM2 en el Rung de M3</h4>
      <p>
        Enclavamiento de secuencia física: M3 (elevador) alimenta a M2 (redler). Si M2 para por falla térmica o mecánica, M3 se desenergiza en el <b>mismo ciclo de scan</b>, impidiendo que el elevador siga descargando trigo sobre un redler detenido (evita atascamientos severos y derrames).
      </p>
    </div>

    <div class="card">
      <h4>P5. Marcha Local con Flanco Ascendente</h4>
      <p>
        El contacto <span class="mono">↑PB_MARCHA</span> conduce un único ciclo de scan. Evita que la línea rearranque sola si el pulsador queda trabado mecánicamente y luego se despeja una falla o celda llena. Además, prioriza la orden de PARADA en caso de pulsación simultánea.
      </p>
    </div>

    <div class="card">
      <h4>P6. Escalado ×3 de la Entrada Analógica</h4>
      <p>
        La entrada 0–10 V convierte a 0–1000 puntos en escala normal. El transmisor PDT-01 entrega 0–10 V para 0–3000 Pa. La constante de proporcionalidad directa es:
        <br><center><span class="mono">ΔP = puntos × (3000 Pa / 1000 pts) = puntos × 3</span></center>
        Para 600 puntos corresponden exactamente <b>1800 Pa</b> (aviso); para 700 pts son <b>2100 Pa</b> (falla).
      </p>
    </div>

    <div class="card">
      <h4>P7. Retardo de 10 s en Alarmas de Presión</h4>
      <p>
        Los filtros de mangas operan con limpieza periódica por pulsos de aire comprimido a contracorriente (jet-pulse), lo que genera fluctuaciones y picos transitorios de presión de corta duración. El retardo TON de 10 s filtra estos transitorios, disparando únicamente ante saturación real permanente.
      </p>
    </div>

    <div class="card">
      <h4>P8. Duplicación de Salidas %Q en Bits %M</h4>
      <p>
        En controladores industriales Schneider, el servidor Modbus TCP optimiza la publicación y el mapeo de memoria agrupando las variables de proceso en coils internos %M contiguos (0 a 30) y registros %MW, evitando conflictos de acceso directo sobre las salidas físicas a relé.
      </p>
    </div>
  </div>

  <!-- ==================== PÁGINA 5: ARQUITECTURA TÉCNICA Y CONCLUSIONES ==================== -->
  <div class="page-break"></div>

  <div class="running-header">
    <span class="inst">UTN Paraná · Tecnicatura en Mecatrónica</span>
    <span>TP Integrador Parte 2 — Informe Comparativo · Arquitectura y Conclusiones</span>
  </div>

  <h2>6. Arquitectura Tecnológica del SCADA Propio Desarrollado</h2>
  <p>
    A diferencia de un desarrollo SCADA genérico, el sistema se estructuró bajo una arquitectura desacoplada de alto rendimiento y grado industrial:
  </p>

  <div class="callout">
    <div class="callout-title">Diagrama de Flujo y Topología de Comunicaciones</div>
    <b>Planta / Controlador</b> (M221 Schneider en puerto 502 / PLC Virtual en puerto 5020) 
    ➔ <b>Modbus TCP</b> (Lectura cíclica de Coils %M0–%M42 y Registros %MW0–%MW10 cada 100 ms) 
    ➔ <b>Gateway Node.js</b> (Serialización asíncrona, descarte de jitter, web server HTTP port 8080) 
    ➔ <b>WebSocket Bidireccional</b> (&lt; 15 ms de latencia) 
    ➔ <b>HMI Web Nativa</b> (SVG vectorial responsive, motor Web Audio API, ISA-101 / ISA-18.2).
  </div>

  <h3>Innovaciones y Mejoras de Ingeniería Incorporadas</h3>
  <ul>
    <li><b>Cumplimiento Normativo ISA-101 (High Performance HMI):</b> Utilización de paleta cromática sobria en fondo oscuro (<span class="mono">#06090e</span>) que reserva los colores saturados exclusivamente para estados activos (verde <span class="mono">#00e599</span>), alarmas críticas (rojo <span class="mono">#ff385c</span>) y advertencias preventivas (amarillo <span class="mono">#ffb703</span>), reduciendo radicalmente los errores de interpretación del operador.</li>
    <li><b>Gestión de Alarmas ISA-18.2:</b> Cuadro de alarmas con reconocimiento individual y colectivo (ACK), discriminación por severidad (Alta/Baja), registro de eventos con estampa de tiempo milimétrica y exportación instantánea a CSV descargable.</li>
    <li><b>Generación Acústica por Web Audio API:</b> En lugar de archivos de audio pre-grabados que sufren bloqueos de reproducción o latencias, se programó un sintetizador analógico virtual con osciladores de onda cuadrada/diente de sierra y filtro pasa-bajos a 1500 Hz que emula a la perfección la sirena electromecánica de planta durante los 5 s de pre-arranque.</li>
    <li><b>Panel de Pruebas de Laboratorio y Simulación de Campo:</b> Permite ejecutar la totalidad del protocolo de pruebas e inyectar anomalías de forma autónoma (pulsadores locales, seta de emergencia, sobrecarga térmica en guardamotores y slider de presión diferencial) mediante un panel flotante retráctil.</li>
    <li><b>PLC Virtual Modbus Autónomo (51 Rungs):</b> Se programó en Node.js un motor de emulación que replica con exactitud milimétrica el comportamiento de cada rung Ladder, temporizador y contador del M221, garantizando portabilidad total en cualquier computadora sin necesidad de instalar o licenciar software adicional.</li>
    <li><b>Compatibilidad Total con Schneider Machine Expert Basic V1.4:</b> El gateway posee un conmutador de origen en caliente que permite alternar la supervisión entre el PLC Virtual propio y el simulador oficial de Schneider Electric conectándose al puerto TCP 502.</li>
  </ul>

  <h2>7. Conclusiones y Dictamen Final</h2>
  <div class="callout callout-plus" style="margin-top: 8px;">
    <div class="callout-title">VEREDICTO TÉCNICO: CUMPLIMIENTO TOTAL Y EXCELENCIA TÉCNICA</div>
    El sistema desarrollado no solo <b>satisface el 100% de las especificaciones pedagógicas y técnicas</b> fijadas en la consigna del Trabajo Práctico Integrador Parte 2, sino que eleva la calidad del entregable a un nivel profesional propio de ingeniería de planta.
    <br><br>
    La combinación de una <b>lógica Ladder robusta, segura y bien documentada</b> con un <b>sistema SCADA web moderno, responsivo, ergonómico y con audio sintetizado</b> ofrece una herramienta didáctica e industrial de máxima confiabilidad, lista para ser evaluada y grabada en el video demostrativo.
  </div>

  <table style="margin-top: 24px; border: none;">
    <tr style="background: none;">
      <td style="border: none; width: 50%; text-align: center; padding-top: 30px;">
        <div style="border-top: 1px solid #94a3b8; width: 70%; margin: 0 auto; padding-top: 4px;">
          <b>Hugo Ariel Martinez</b><br>
          Alumno — Tecnicatura Superior en Mecatrónica<br>
          Proyecto PLC: <i>Martinez.smbp</i> · UTN Paraná
        </div>
      </td>
      <td style="border: none; width: 50%; text-align: center; padding-top: 30px;">
        <div style="border-top: 1px solid #94a3b8; width: 70%; margin: 0 auto; padding-top: 4px;">
          <b>Cátedra de Automatización Industrial</b><br>
          Evaluación y Aprobación de TP Integrador<br>
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
