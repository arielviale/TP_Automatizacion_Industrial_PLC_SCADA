# Protocolo de pruebas (Consigna 4.3)

**Asignatura:** Automatización Industrial — UTN Facultad Regional Paraná  
**Alumno:** Hugo Ariel Martinez · **Proyecto PLC:** `Martinez.smbp` (Modicon M221 TM221CE24R)

## Preparación común (antes de cada prueba)

1. En Machine Expert Basic: **Iniciar simulador → Login → Run**.
2. En la ventana del simulador, poner en **1**: `%I0.0` PE_OK, `%I0.1` GM1_OK, `%I0.2` GM2_OK,
   `%I0.3` GM3_OK, `%I0.4` GIRO_M3 y `%I0.9` PB_PARADA. Dejar en 0: `%I0.5`, `%I0.6`, `%I0.7`, `%I0.8`.
3. Pulsar **RESET** (SCADA o un pulso en `%I0.7`) para borrar las fallas memorizadas al arrancar el simulador.
4. `%IW0.0` en 0 (o en un valor menor que 500, o sea menos de 1500 Pa).
5. Elegir celda: botón *Celda 1* del SCADA o `%MW10 = 1` en la tabla de animación.

> Tip: abrir una **tabla de animación** con %Q0.0–%Q0.7, %M5, %M9, %M30, %TM0.V–%TM4.V, %MW0, %MW1 y %MW10
> para medir los tiempos durante las pruebas y el video.

## Tabla de pruebas

| N.º | Prueba | Acción | Resultado esperado | Variables a observar | Obtenido / OK |
|:-:|---|---|---|---|---|
| 1 | Arranque normal | Celda 1; MARCHA | Bocina 5 s; M1, M2 y M3 con 5 s de diferencia; YV1 abierta; piloto intermitente y luego fijo | %Q0.5 → %Q0.0 (t=5) → %Q0.1 (t=10) → %Q0.2 (t=15); %Q0.3=1; %Q0.7 | |
| 2 | Sin celda elegida | %MW10 = 0; MARCHA | No arranca, ni siquiera la bocina; PERMISO apagado | %M53=0, %M9=0, %M5=0, %Q0.5=0 | |
| 3 | Parada normal | PARADA con la línea en marcha | M3 para en el acto; M2 a los 20 s; M1 30 s después de M2 | %Q0.2↓ t=0; %Q0.1↓ t=20; %Q0.0↓ t=50 | |
| 4 | Pulsadores locales | Pulsar %I0.8; luego %I0.9 = 0 | Arranca con el flanco de MARCHA; se detiene al abrir PARADA | %M5 se setea con el flanco; con %I0.8 mantenido no rearranca tras parar | |
| 5 | Falla de M2 | %I0.2 = 0 en marcha | M2 y M3 paran en el acto; M1 sigue 30 s; baliza intermitente | %M22=1, %M30=1, %Q0.1=%Q0.2=0, %Q0.0↓ t=30, %Q0.6 parpadea | |
| 6 | Falta de giro | %I0.4 = 0 al arrancar M3 | M3 para a los 5 s; falla AL_GIRO | %TM5.V llega a 5 → %M24=1, %Q0.2=0; luego M2 20 s / M1 30 s | |
| 7 | Celda llena | %I0.5 = 1 con destino celda 1 | Parada secuencial; no rearranca hasta elegir la celda 2 | %M52=1, %M27=1, %M9=0, baliza fija; con %MW10=2 → %M9=1 | |
| 8 | Emergencia | %I0.0 = 0 | Todo se detiene y las compuertas cierran; no arranca sin RESET | %Q0.0–%Q0.4 = 0; %M20=1; con %I0.0=1 sin RESET, %M9 sigue en 0 | |
| 9 | Presión diferencial | %IW0.0 = 600, luego 700 | 1800 Pa: aviso y baliza fija; 2100 Pa: falla y parada a los 10 s | %MW0=1800 → %M26 a los 10 s; %MW0=2100 → %M25 a los 10 s, %M5=0 | |
| 10 | Contador | 6 arranques seguidos (T_HORA = 120 s) | %MW1 llega a 6; aviso AV_ARRANQUES | %MW1, %M29=1, baliza fija; a los 120 s %MW1 vuelve a 0 | |
| 11 | Comunicación | Detener el simulador (o cortar enlace) | La lámpara VIDA deja de parpadear | Lámpara VIDA fija en gris/apagada; indicador de enlace en rojo y aviso de pérdida de comunicación | |

> [!NOTE]
> **Prueba 10:** cada ciclo MARCHA → M3 en marcha → PARADA tarda unos 12 a 15 s, así que 6 arranques
> ocupan entre 80 y 90 s, muy cerca de la ventana de 120 s. Conviene arrancar la prueba justo después de
> que %TM8.V vuelva a 0 y pulsar PARADA apenas cierre M3 (con eso ya cuenta el arranque). Si no se llega,
> subir el preset temporalmente a 300 s. **Volver a 3600 s antes de entregar.**

## Guion sugerido para el video (3–5 min, pruebas 1, 3, 5, 7 y 9)

| Tiempo | Prueba | Qué mostrar en pantalla |
|---|---|---|
| 0:00–0:20 | Presentación | Pantalla Proceso del SCADA (animaciones activas, VIDA parpadeando) junto con el simulador del PLC / Tablero de campo |
| 0:20–1:00 | 1 | Celda 1 → MARCHA: bocina con ondas de audio, secuencia en barra temporal (M1, M2, M3) y piloto parpadeante a fijo |
| 1:00–1:50 | 3 | PARADA: M3 cae de inmediato, vaciado de M2 (20 s) con cuenta regresiva en barra, y barrido de M1 (30 s) |
| 1:50–2:40 | 5 | Falla M2 (disparo de guardamotor %I0.2 = 0): M2 y M3 caen en el acto, baliza roja intermitente, registro en vista de Alarmas; rearme con RESET |
| 2:40–3:30 | 7 | Celda llena (%I0.5 = 1): silo en amarillo, parada de línea, bloqueo de rearranque en Celda 1; conmutar a Celda 2 y comprobar rearranque |
| 3:30–4:30 | 9 | Presión diferencial: mover slider de %IW0.0 a 600 (1800 Pa) $\rightarrow$ aviso a los 10 s y baliza fija; slider a 700 (2100 Pa) $\rightarrow$ falla a los 10 s y parada general |
