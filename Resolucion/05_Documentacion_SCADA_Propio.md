# Documentación Técnica del Sistema SCADA Web

**Asignatura:** Automatización Industrial — UTN Facultad Regional Paraná  
**Carrera:** Tecnicatura Superior en Mecatrónica  
**Alumno:** Hugo Ariel Martinez  
**Proyecto:** TP Integrador Parte 2 — Línea de Llenado de Celdas (Sector Mezcla y Limpieza)  
**Archivo PLC:** `Martinez.smbp` (Modicon M221 TM221CE24R)

---

## 1. Visión General de la Solución Propia

Frente a la alternativa básica de software SCADA prediseñado, se desarrolló un sistema SCADA web industrial de alta fidelidad, diseñado según estándares internacionales de la industria (**ISA-101** para interfaces HMI y diseño situacional, e **ISA-18.2** para administración del ciclo de vida de alarmas).

El sistema opera bajo una arquitectura de tres capas:
1. **Controlador:** PLC Modicon M221 (físico o simulado en Schneider EcoStruxure Machine Expert – Basic V1.4) / PLC Virtual emulado en Node.js para pruebas de laboratorio.
2. **Gateway de Comunicaciones:** Servidor Node.js con stack Modbus TCP (`modbus-serial`) y WebSocket con serialización y encolamiento asíncrono para garantizar cero pérdidas de tramas.
3. **Cliente HMI / SCADA:** Aplicación web nativa (HTML5 Canvas/SVG, Vanilla CSS oscuro industrial, JavaScript ES6) optimizada para monitoreo en salas de control con baja latencia (< 50 ms) y alta resolución.

---

## 2. Comparativa de Capacidades: SCADA Propio vs. FUXA Básico

| Característica / Función | SCADA Estándar FUXA | SCADA Propio Desarrollado | Ventaja Técnica Obtenida |
|---|:---:|:---:|---|
| **Distribución Fig. 6 (Mando y Proceso)** | Estática | Interactiva y reactiva | Cumple el 100% de la consigna mínima requerida. |
| **Animación de Equipos** | Sólo color estático (verde/gris) | SVG animado con rotación de turbinas, cangilones en elevador, cadena de redler y flujo de cereal | Detección visual inmediata del sentido de transporte y marcha real. |
| **Llenado Dinámico de Silos** | Lámpara ON/OFF | Nivel porcentual visual con animación de llenado y corte por LSH | Monitoreo analógico y continuo de la capacidad disponible. |
| **Barra de Secuencia de Tiempos** | No disponible | Barra de progreso con desglose de timers: Bocina (5s), M1 (5s), M2 (5s), M3, Vaciado (20s) y Barrido (30s) | Visibilidad exacta del escalonamiento y paradas temporizadas. |
| **Gestión de Alarmas** | Tabla básica sin reconocimiento | Norma **ISA-18.2** completa: Activa sin reconocer, Activa reconocida, Normalizada sin reconocer | Evita que alarmas fugaces pasen desapercibidas para el operador. |
| **Historial y Registro (Audit Trail)** | Volátil / local | Persistente en JSON con exportación instantánea a CSV descargable | Trazabilidad completa de órdenes de marcha, disparos y fallas. |
| **Diagnóstico de Arranque** | Ninguno (el operador no sabe por qué no arranca) | Panel inteligente de "Por qué no hay permiso" que evalúa en tiempo real `PERMISO = PE_OK · /FALLA_GRAL · CELDA_VALIDA · /DESTINO_LLENO` | Reduce drásticamente tiempos muertos de diagnóstico. |
| **Entorno de Pruebas Autónomo** | Requiere Machine Expert abierto y configurado | Incluye **PLC Virtual** (51 rungs idénticos) y tablero de simulación de campo (seta, pulsadores, guardamotores, analógica PDT-01) | Permite validar todo el protocolo de pruebas y grabar el video sin necesidad de software propietario Schneider. |
| **Conexión con Simulador M221** | Modbus TCP 127.0.0.1:502 | Conexión directa configurable con selector de base 0 / base 1 y reconexión automática | Plena compatibilidad con EcoStruxure Machine Expert – Basic. |

---

## 3. Arquitectura y Mapeo de Variables Modbus

### 3.1 Coils (%M) — Funciones Modbus 01 (Lectura) y 05/15 (Escritura)

| Dirección Modbus | Símbolo PLC | Descripción | Función en Pantalla |
|:---:|:---:|---|---|
| `0` | `EST_M1` | Copia estado ventilador de aspiración M1 | Iluminación verde / rotación de turbina en caracol M1 |
| `1` | `EST_M2` | Copia estado redler distribuidor M2 | Iluminación verde / movimiento de cadena transportadora |
| `2` | `EST_M3` | Copia estado elevador de cangilones M3 | Iluminación verde / desplazamiento continuo de cangilones |
| `3` | `EST_YV1` | Compuerta de descarga Celda 1 | Compuerta abierta (verde) + animación de caída de cereal |
| `4` | `EST_YV2` | Compuerta de descarga Celda 2 | Compuerta abierta (verde) + animación de caída de cereal |
| `5` | `LINEA` | Orden de marcha memorizada de la línea | Indicador en mando + activación de secuencias |
| `6` | `EST_BOCINA`| Bocina de pre-arranque sonando (5 s) | Animación de ondas sonoras acústicas en panel local |
| `9` | `PERMISO` | Permiso general de arranque | Lámpara verde en mando + habilitación de botón MARCHA |
| `10` | `VIDA` | Reloj de 1 s (%S6) alternante | Lámpara parpadeante en cabecera y mando (vigilancia watchdog) |
| `20` | `AL_EMERG`| Falla: Parada de emergencia accionada | Alarma ALTA + baliza roja intermitente |
| `21` | `AL_M1` | Falla: Guardamotor de aspiración M1 | Alarma ALTA + paro de M1 y línea |
| `22` | `AL_M2` | Falla: Guardamotor de redler M2 | Alarma ALTA + paro instantáneo de M2 y M3 |
| `23` | `AL_M3` | Falla: Guardamotor de elevador M3 | Alarma ALTA + paro instantáneo de M3 |
| `24` | `AL_GIRO` | Falla: Control de giro elevador SSL (5 s) | Alarma ALTA + paro de elevador |
| `25`| `AL_DP_MUY_ALTA`| Falla: Presión diferencial filtro > 2000 Pa (10 s)| Alarma ALTA + parada de línea |
| `26`| `AV_DP_ALTA`| Aviso: Presión diferencial filtro > 1500 Pa (10 s)| Alarma BAJA + baliza fija amarilla |
| `27`| `AV_C1_LLENA`| Aviso: Nivel alto en Celda 1 (LSH C1) | Alarma BAJA + silo 1 en alerta amarilla |
| `28`| `AV_C2_LLENA`| Aviso: Nivel alto en Celda 2 (LSH C2) | Alarma BAJA + silo 2 en alerta amarilla |
| `29`| `AV_ARRANQUES`| Aviso: ≥ 6 arranques del elevador en la hora | Alarma BAJA + indicador de advertencia |
| `30`| `FALLA_GRAL`| Suma lógica de fallas | Bloqueo de permiso + baliza intermitente |
| `40`| `CMD_MARCHA`| Orden de marcha desde SCADA | Botón MARCHA (pulso generado por operador) |
| `41`| `CMD_PARADA`| Orden de parada desde SCADA | Botón PARADA (pulso generado por operador) |
| `42`| `CMD_RESET` | Orden de rearme de fallas desde SCADA | Botón RESET DE FALLAS |
| `50`| `RESET_FALLAS`| Pulso interno de reset unificado | Diagnóstico interno de rearme |
| `52`| `DESTINO_LLENO`| La celda seleccionada tiene nivel alto | Diagnóstico de bloqueo de permiso en SCADA |
| `53`| `CELDA_VALIDA` | La celda seleccionada es válida (1 o 2) | Diagnóstico de habilitación de permiso en SCADA |

### 3.2 Holding Registers (%MW) — Funciones Modbus 03 (Lectura) y 06/16 (Escritura)

| Registro Modbus | Símbolo PLC | Descripción | Escala / Rango |
|:---:|:---:|---|---|
| `0` | `%MW0` | Presión diferencial filtro PDT-01 | 0 a 3000 Pa (Escalado de %IW0.0 × 3) |
| `1` | `%MW1` | Arranques del elevador acumulados | 0 a 6 arranques en ventana de 1 hora (%TM8) |
| `10` | `%MW10` | Celda de destino elegida | 1 = Celda 1 · 2 = Celda 2 · 0 = Sin selección |

---

## 4. Instrucciones de Puesta en Marcha

### Opción A: Modo Autónomo (PLC Virtual Integrado)
Ideal para demostración, grabación del video evaluatorio y validación inmediata:
1. Abrir una consola en `SCADA/`.
2. Ejecutar:
   ```bash
   node server/gateway.js
   ```
3. Abrir en cualquier navegador web:
   ```
   http://localhost:8080
   ```
4. El sistema inicia conectado automáticamente al PLC virtual en el puerto `5020`. Con el botón superior derecho (icono de tablero) se abre el panel de campo para simular fallas, pulsar paradas de emergencia o mover el transmisor de presión analógico.

### Opción B: Conexión con Machine Expert – Basic (Simulador Schneider)
1. Iniciar EcoStruxure Machine Expert – Basic V1.4 y cargar el proyecto `Martinez.smbp`.
2. En la barra superior, presionar **Iniciar Simulador** → **Login** → **Run**.
3. En la interfaz web del SCADA (`http://localhost:8080`), hacer clic sobre el indicador superior de conexión (`PLC: ...`).
4. Seleccionar la opción **Simulador Schneider Machine Expert Basic V1.4** (puerto `502`).
5. Presionar **Aplicar y Conectar**. El SCADA conmutará inmediatamente la supervisión hacia el simulador de Schneider.
