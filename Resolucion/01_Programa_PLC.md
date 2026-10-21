# TP Integrador Parte 2 — Programa del PLC (Modicon M221 TM221CE24R)

**Alumno:** Hugo Ariel Martinez · **Proyecto:** `Martinez.smbp` · **Software:** EcoStruxure Machine Expert – Basic V1.4 · **Lenguaje:** Ladder

> Convención usada en este documento
> - `─┤ ├─` contacto NA · `─┤/├─` contacto NC · `─┤P├─` flanco ascendente
> - `─( )─` bobina · `─(S)─` SET · `─(R)─` RESET
> - Arriba de cada elemento va la **dirección** y abajo el **símbolo** (igual que la Figura 5).
> - Para cada rung se da también su equivalente en **Lista de instrucciones (IL)**. En Machine Expert
>   Basic se puede pasar un rung de Ladder a IL y viceversa (botón *Ladder/IL* del rung): sirve para
>   verificar que lo que dibujaron coincide con la ecuación.

---

## 0. Configuración del proyecto (Consigna 1.1)

| Paso | Dónde | Qué hacer |
|---|---|---|
| 1 | *Configuración → Controlador* | Reemplazar el controlador por **TM221CE24R**. |
| 2 | *Configuración → ETH1* | Verificar **Servidor Modbus habilitado** (puerto 502). IP fija opcional; el simulador usa 127.0.0.1. |
| 3 | *Configuración → Entradas analógicas → %IW0.0* | Tipo **0–10 V**, ámbito **Normal** (0…1000). |
| 4 | *Programación → Herramientas → Símbolos* | Cargar la tabla de símbolos (sección 1 de este documento o el archivo [`simbolos.csv`](simbolos.csv)). |
| 5 | *Programación → Temporizadores (%TM)* | Cargar tipo, base de tiempo **1 s** y preset de %TM0…%TM8 (sección 2). |
| 6 | *Programación → Contadores (%C)* | %C0, preset **6**. |
| 7 | *Programación → Tareas → Tarea maestra* | Crear las **7 secciones (POU)** con los nombres de la sección 3 de este documento. |

---

## 1. Tabla de símbolos

### 1.1 Entradas / salidas / analógica

| Dirección | Símbolo | Comentario |
|---|---|---|
| %I0.0 | PE_OK | Parada de emergencia NC – 1 = sin emergencia |
| %I0.1 | GM1_OK | Guardamotor M1 – 1 = OK |
| %I0.2 | GM2_OK | Guardamotor M2 – 1 = OK |
| %I0.3 | GM3_OK | Guardamotor M3 – 1 = OK |
| %I0.4 | GIRO_M3 | Control de giro elevador – 1 = gira normal |
| %I0.5 | LSH_C1 | Nivel alto celda 1 – 1 = llena |
| %I0.6 | LSH_C2 | Nivel alto celda 2 – 1 = llena |
| %I0.7 | PB_RESET | Pulsador RESET NA – 1 = pulsado |
| %I0.8 | PB_MARCHA | Pulsador MARCHA NA – 1 = pulsado |
| %I0.9 | PB_PARADA | Pulsador PARADA NC – 1 = no pulsado |
| %Q0.0 | KM1_ASPIR | Contactor ventilador aspiración M1 |
| %Q0.1 | KM2_REDLER | Contactor redler M2 |
| %Q0.2 | KM3_ELEV | Contactor elevador M3 |
| %Q0.3 | YV1_C1 | Compuerta celda 1 (1 = abierta) |
| %Q0.4 | YV2_C2 | Compuerta celda 2 (1 = abierta) |
| %Q0.5 | BOCINA | Bocina de pre-arranque |
| %Q0.6 | BALIZA | Baliza: intermitente falla / fija aviso |
| %Q0.7 | PILOTO_MARCHA | Piloto verde: intermitente arrancando / fijo en marcha |
| %IW0.0 | — | ΔP filtro PDT-01: 0–10 V = 0–1000 = 0–3000 Pa |
| %S6 | RELOJ_1S | Bit de sistema: reloj de 1 s |

### 1.2 Memoria interna

| Dirección | Símbolo | Comentario | Sentido |
|---|---|---|---|
| %M0 | EST_M1 | M1 en marcha (copia KM1) | PLC → SCADA |
| %M1 | EST_M2 | M2 en marcha | PLC → SCADA |
| %M2 | EST_M3 | M3 en marcha | PLC → SCADA |
| %M3 | EST_YV1 | Compuerta 1 abierta | PLC → SCADA |
| %M4 | EST_YV2 | Compuerta 2 abierta | PLC → SCADA |
| %M5 | LINEA | Orden de marcha memorizada | PLC → SCADA |
| %M6 | EST_BOCINA | Bocina sonando | PLC → SCADA |
| %M9 | PERMISO | Permiso de marcha | PLC → SCADA |
| %M10 | VIDA | Señal de vida (0,5 s) | PLC → SCADA |
| %M20 | AL_EMERG | Falla: emergencia | PLC → SCADA |
| %M21 | AL_M1 | Falla: guardamotor M1 | PLC → SCADA |
| %M22 | AL_M2 | Falla: guardamotor M2 | PLC → SCADA |
| %M23 | AL_M3 | Falla: guardamotor M3 | PLC → SCADA |
| %M24 | AL_GIRO | Falla: control de giro | PLC → SCADA |
| %M25 | AL_DP_MUY_ALTA | Falla: ΔP muy alta | PLC → SCADA |
| %M26 | AV_DP_ALTA | Aviso: ΔP alta | PLC → SCADA |
| %M27 | AV_C1_LLENA | Aviso: celda 1 llena | PLC → SCADA |
| %M28 | AV_C2_LLENA | Aviso: celda 2 llena | PLC → SCADA |
| %M29 | AV_ARRANQUES | Aviso: ≥ 6 arranques/hora | PLC → SCADA |
| %M30 | FALLA_GRAL | Hay alguna falla AL_ | PLC → SCADA |
| %M40 | CMD_MARCHA | Orden de marcha (pulso) | SCADA → PLC |
| %M41 | CMD_PARADA | Orden de parada (pulso) | SCADA → PLC |
| %M42 | CMD_RESET | Orden de reset (pulso) | SCADA → PLC |
| %M50 | RESET_FALLAS | Pulso interno de reset | interno |
| %M52 | DESTINO_LLENO | Celda elegida con nivel alto | interno |
| %M53 | CELDA_VALIDA | Celda elegida es 1 o 2 | interno |
| %MW0 | DP_PA | ΔP del filtro [Pa] | PLC → SCADA |
| %MW1 | ARRANQUES_H | Arranques del elevador en la hora | PLC → SCADA |
| %MW10 | CELDA_DESTINO | Celda de destino (1 o 2) | SCADA → PLC |

> [!NOTE]
> El enunciado deja las %MW sin símbolo («—»). Ponerles un nombre (DP_PA, ARRANQUES_H,
> CELDA_DESTINO) es opcional y no cambia ninguna dirección; si la cátedra lo exige literal, dejarlas vacías.

---

## 2. Temporizadores y contador

| Objeto | Símbolo | Tipo | Base | Preset | Función |
|---|---|---|---|---|---|
| %TM0 | T_BOCINA | **TP** | 1 s | 5 | Aviso acústico de pre-arranque |
| %TM1 | T_ARR_M2 | TON | 1 s | 5 | Espera M1 → M2 |
| %TM2 | T_ARR_M3 | TON | 1 s | 5 | Espera M2 → M3 |
| %TM3 | T_VACIADO | **TOF** | 1 s | 20 | M2 sigue después de parar M3 |
| %TM4 | T_BARRIDO | **TOF** | 1 s | 30 | M1 sigue después de parar M2 |
| %TM5 | T_GIRO | TON | 1 s | 5 | Máx. tiempo M3 sin señal de giro |
| %TM6 | T_DP_ALTA | TON | 1 s | 10 | Retardo aviso ΔP alta |
| %TM7 | T_DP_MUY_ALTA | TON | 1 s | 10 | Retardo falla ΔP muy alta |
| %TM8 | T_HORA | TON | 1 s | 3600 (120 para pruebas) | Ventana de 1 h |
| %C0 | C_ARRANQUES | CTU | — | 6 | Arranques del elevador en la hora |

---

## 3. Programa — 7 secciones, 51 rungs

| Sección | Nombre POU | Rungs | Clase |
|---|---|---|---|
| 1 | `1_Generales` | 2 | 1 |
| 2 | `2_Fallas` | 12 | 1 |
| 3 | `3_Celdas_y_permiso` | 7 | 2 |
| 4 | `4_Marcha_y_parada` | 8 | 2 |
| 5 | `5_Motores_y_bocina` | 4 | 2 |
| 6 | `6_DP_y_contador` | 10 | 3 |
| 7 | `7_Senalizacion_SCADA` | 8 | 3 |

---

### Sección 1 — Generales (Clase 1)

**Rung 1.1 — Señal de vida: VIDA copia el reloj de 1 s para que el SCADA detecte que el PLC está vivo.**
```
      %S6                                         %M10
 ||----┤ ├----------------------------------------( )----||
     RELOJ_1S                                     VIDA
```
```
LD   %S6
ST   %M10
```

**Rung 1.2 — Pulso de reset: RESET_FALLAS con la orden del SCADA o el flanco del pulsador local; borra CMD_RESET.**
```
      %M42                                        %M50
 ||--+-┤ ├-+--------------------------------+-----( )----||
     |CMD_RESET                             |  RESET_FALLAS
     | %I0.7 |                              |     %M42
     +-┤P├---+                              +-----(R)----
      PB_RESET                                 CMD_RESET
```
```
LD   %M42
ORR  %I0.7
ST   %M50
R    %M42
```

---

### Sección 2 — Fallas (Clase 1)

Esquema para cada protección (Ej. 1 y Ej. 2): **SET** cuando la señal cae a 0; **RESET** con
RESET_FALLAS **y** la señal ya normalizada (si la causa sigue presente, el reset no tiene efecto).

**Rung 2.1 — Memoriza la falla de emergencia cuando se acciona la seta (PE_OK = 0).**
```
      %I0.0                                       %M20
 ||----┤/├----------------------------------------(S)----||
      PE_OK                                     AL_EMERG
```
`LDN %I0.0` · `S %M20`

**Rung 2.2 — Borra la falla de emergencia con RESET y la seta desenclavada.**
```
      %M50          %I0.0                         %M20
 ||----┤ ├-----------┤ ├--------------------------(R)----||
   RESET_FALLAS     PE_OK                       AL_EMERG
```
`LD %M50` · `AND %I0.0` · `R %M20`

**Rung 2.3 — Memoriza disparo del guardamotor de M1.**
```
      %I0.1                                       %M21
 ||----┤/├----------------------------------------(S)----||
     GM1_OK                                       AL_M1
```
`LDN %I0.1` · `S %M21`

**Rung 2.4 — Borra la falla de M1 con RESET y guardamotor rearmado.**
```
      %M50          %I0.1                         %M21
 ||----┤ ├-----------┤ ├--------------------------(R)----||
   RESET_FALLAS    GM1_OK                         AL_M1
```
`LD %M50` · `AND %I0.1` · `R %M21`

**Rung 2.5 — Memoriza disparo del guardamotor de M2.**
`LDN %I0.2` · `S %M22`  (mismo dibujo que 2.3 con GM2_OK → AL_M2)

**Rung 2.6 — Borra la falla de M2 con RESET y guardamotor rearmado.**
`LD %M50` · `AND %I0.2` · `R %M22`

**Rung 2.7 — Memoriza disparo del guardamotor de M3.**
`LDN %I0.3` · `S %M23`

**Rung 2.8 — Borra la falla de M3 con RESET y guardamotor rearmado.**
`LD %M50` · `AND %I0.3` · `R %M23`

**Rung 2.9 — T_GIRO cuenta mientras M3 está energizado y no hay señal de giro.**
```
      %Q0.2         %I0.4         +--------------+
 ||----┤ ├-----------┤/├----------| IN  %TM5   Q |----||
    KM3_ELEV       GIRO_M3        |  TON  5 s    |
                                  +--------------+
                                      T_GIRO
```
```
BLK  %TM5
LD   %Q0.2
ANDN %I0.4
IN
END_BLK
```

**Rung 2.10 — Si pasan 5 s sin giro se memoriza la falla AL_GIRO.**
```
     %TM5.Q                                       %M24
 ||----┤ ├----------------------------------------(S)----||
     T_GIRO                                      AL_GIRO
```
`LD %TM5.Q` · `S %M24`

**Rung 2.11 — Borra AL_GIRO con RESET cuando el temporizador ya no está vencido.**
```
      %M50         %TM5.Q                         %M24
 ||----┤ ├-----------┤/├--------------------------(R)----||
   RESET_FALLAS    T_GIRO                        AL_GIRO
```
`LD %M50` · `ANDN %TM5.Q` · `R %M24`

> Al caer AL_GIRO, KM3 se abre → la entrada de T_GIRO cae → T_GIRO.Q = 0, por eso el reset sí es posible.

**Rung 2.12 — FALLA_GRAL: OR de todas las fallas que detienen la línea.**
```
      %M20                                        %M30
 ||--+-┤ ├-----+----------------------------------( )----||
     |AL_EMERG |                               FALLA_GRAL
     | %M21    |
     +-┤ ├-----+
     | AL_M1   |
     | %M22    |
     +-┤ ├-----+
     | AL_M2   |
     | %M23    |
     +-┤ ├-----+
     | AL_M3   |
     | %M24    |
     +-┤ ├-----+
     | AL_GIRO |
     | %M25    |
     +-┤ ├-----+
     AL_DP_MUY_ALTA
```
```
LD   %M20
OR   %M21
OR   %M22
OR   %M23
OR   %M24
OR   %M25
ST   %M30
```

---

### Sección 3 — Celdas y permiso (Clase 2)

**Rung 3.1 — CELDA_VALIDA: la celda elegida en %MW10 es 1 o 2.**
```
 ||--+-[ %MW10 = 1 ]-+----------------------------( )----||
     |               |                         CELDA_VALIDA
     +-[ %MW10 = 2 ]-+                            %M53
```
```
LD   [%MW10 = 1]
OR   [%MW10 = 2]
ST   %M53
```

**Rung 3.2 — DESTINO_LLENO: la celda elegida tiene nivel alto.**
```
                         %I0.5
 ||--+-[ %MW10 = 1 ]------┤ ├----+----------------( )----||
     |                  LSH_C1   |             DESTINO_LLENO
     |                   %I0.6   |                %M52
     +-[ %MW10 = 2 ]------┤ ├----+
                        LSH_C2
```
```
LD   [%MW10 = 1]
AND  %I0.5
OR(  [%MW10 = 2]
AND  %I0.6
)
ST   %M52
```

**Rung 3.3 — Aviso celda 1 llena.**
`LD %I0.5` · `ST %M27`
```
      %I0.5                                       %M27
 ||----┤ ├----------------------------------------( )----||
     LSH_C1                                    AV_C1_LLENA
```

**Rung 3.4 — Aviso celda 2 llena.**
`LD %I0.6` · `ST %M28`

**Rung 3.5 — Abre la compuerta 1 si el destino es la celda 1 y no hay emergencia.**
```
                         %M20                     %Q0.3
 ||----[ %MW10 = 1 ]------┤/├---------------------( )----||
                       AL_EMERG                   YV1_C1
```
`LD [%MW10 = 1]` · `ANDN %M20` · `ST %Q0.3`

**Rung 3.6 — Abre la compuerta 2 si el destino es la celda 2 y no hay emergencia.**
`LD [%MW10 = 2]` · `ANDN %M20` · `ST %Q0.4`

**Rung 3.7 — PERMISO de marcha: sin emergencia, sin fallas, celda válida y no llena.**
```
      %I0.0      %M30        %M53        %M52        %M9
 ||----┤ ├--------┤/├---------┤ ├---------┤/├--------( )----||
      PE_OK    FALLA_GRAL  CELDA_VALIDA DESTINO_LLENO PERMISO
```
```
LD   %I0.0
ANDN %M30
AND  %M53
ANDN %M52
ST   %M9
```

> [!TIP]
> **Primera instancia (llave selectora local):** mientras no esté el SCADA, se puede simular la llave
> de 2 posiciones escribiendo %MW10 = 1 o 2 desde la *Tabla de animación* del simulador. El
> enunciado no asigna una entrada física para la llave, así que **no** se agregan entradas (las
> asignaciones son fijas).

---

### Sección 4 — Marcha y parada (Clase 2)

**Rung 4.1 — SET LINEA con orden de marcha (SCADA o flanco del pulsador local) si hay permiso.**
```
      %M40                    %M9                 %M5
 ||--+-┤ ├-----+---------------┤ ├----------------(S)----||
     |CMD_MARCHA|            PERMISO              LINEA
     | %I0.8    |
     +-┤P├------+
      PB_MARCHA
```
```
LD   %M40
ORR  %I0.8
AND  %M9
S    %M5
```

**Rung 4.2 — RESET LINEA por parada SCADA, pulsador PARADA, celda llena o falla general.**
```
      %M41                                        %M5
 ||--+-┤ ├------+---------------------------------(R)----||
     |CMD_PARADA|                                 LINEA
     | %I0.9    |
     +-┤/├------+
     |PB_PARADA |
     | %M52     |
     +-┤ ├------+
     |DESTINO_LLENO
     | %M30     |
     +-┤ ├------+
     FALLA_GRAL
```
```
LD   %M41
ORN  %I0.9
OR   %M52
OR   %M30
R    %M5
```
> El RESET va **después** del SET: si ambas condiciones están juntas en el mismo scan, gana la parada
> (prioridad a la desconexión = criterio de seguridad).

**Rung 4.3 — Vuelve a 0 las órdenes del SCADA una vez usadas.**
```
      %M40                                        %M40
 ||--+-┤ ├------+------------------------------+--(R)----||
     |CMD_MARCHA|                              | CMD_MARCHA
     | %M41     |                              |  %M41
     +-┤ ├------+                              +--(R)----
     CMD_PARADA                                  CMD_PARADA
```
```
LD   %M40
OR   %M41
R    %M40
R    %M41
```

**Rung 4.4 — T_BOCINA: pulso de 5 s al activarse LINEA.**
```
      %M5          +--------------+
 ||----┤ ├---------| IN  %TM0   Q |----||
      LINEA        |  TP   5 s    |
                   +--------------+
                     T_BOCINA
```
`BLK %TM0` · `LD %M5` · `IN` · `END_BLK`

**Rung 4.5 — T_ARR_M2: 5 s desde que M1 está en marcha.**
```
      %M5          %Q0.0        +--------------+
 ||----┤ ├----------┤ ├---------| IN  %TM1   Q |----||
      LINEA      KM1_ASPIR      |  TON  5 s    |
                                +--------------+
                                   T_ARR_M2
```
`BLK %TM1` · `LD %M5` · `AND %Q0.0` · `IN` · `END_BLK`

**Rung 4.6 — T_ARR_M3: 5 s desde que M2 está en marcha.**
`BLK %TM2` · `LD %M5` · `AND %Q0.1` · `IN` · `END_BLK`

**Rung 4.7 — T_VACIADO: M2 sigue 20 s después de parar M3.**
```
      %Q0.2        +--------------+
 ||----┤ ├---------| IN  %TM3   Q |----||
    KM3_ELEV       |  TOF  20 s   |
                   +--------------+
                     T_VACIADO
```
`BLK %TM3` · `LD %Q0.2` · `IN` · `END_BLK`

**Rung 4.8 — T_BARRIDO: M1 sigue 30 s después de parar M2.**
`BLK %TM4` · `LD %Q0.1` · `IN` · `END_BLK`

---

### Sección 5 — Motores y bocina (Clase 2)

Forma de cada rung: **protecciones en serie** × **condición de marcha**.

**Rung 5.1 — KM1 aspiración: arranca al terminar la bocina, sigue 30 s de barrido.**
```
     %I0.0   %M20    %I0.1   %M21       %M5     %TM0.Q          %Q0.0
 ||---┤ ├-----┤/├-----┤ ├-----┤/├---+----┤ ├------┤/├-----+-----( )----||
     PE_OK  AL_EMERG GM1_OK  AL_M1  |   LINEA   T_BOCINA  |   KM1_ASPIR
                                    |       %TM4.Q        |
                                    +--------┤ ├----------+
                                          T_BARRIDO
```
```
LD   %I0.0
ANDN %M20
AND  %I0.1
ANDN %M21
AND( %M5
ANDN %TM0.Q
OR   %TM4.Q
)
ST   %Q0.0
```

**Rung 5.2 — KM2 redler: arranca 5 s después de M1, sigue 20 s de vaciado.**
```
     %I0.0   %M20    %I0.2   %M22       %M5     %TM1.Q          %Q0.1
 ||---┤ ├-----┤/├-----┤ ├-----┤/├---+----┤ ├------┤ ├-----+-----( )----||
     PE_OK  AL_EMERG GM2_OK  AL_M2  |   LINEA   T_ARR_M2  |   KM2_REDLER
                                    |   %Q0.1   %TM3.Q    |
                                    +----┤ ├------┤ ├-----+
                                      KM2_REDLER T_VACIADO
```
```
LD   %I0.0
ANDN %M20
AND  %I0.2
ANDN %M22
AND( %M5
AND  %TM1.Q
OR(  %Q0.1
AND  %TM3.Q
)
)
ST   %Q0.1
```

**Rung 5.3 — KM3 elevador: arranca 5 s después de M2, para en el acto con PARADA o falla.**
```
   %I0.0  %M20   %I0.3  %M23   %M24   %Q0.1      %M5   %TM2.Q        %Q0.2
 ||-┤ ├----┤/├----┤ ├----┤/├----┤/├----┤ ├--------┤ ├----┤ ├----------( )----||
   PE_OK AL_EMERG GM3_OK AL_M3 AL_GIRO KM2_REDLER LINEA T_ARR_M3     KM3_ELEV
```
```
LD   %I0.0
ANDN %M20
AND  %I0.3
ANDN %M23
ANDN %M24
AND  %Q0.1
AND  %M5
AND  %TM2.Q
ST   %Q0.2
```

**Rung 5.4 — BOCINA suena mientras dura el pulso de T_BOCINA con la línea en marcha.**
```
      %M5          %TM0.Q                         %Q0.5
 ||----┤ ├-----------┤ ├--------------------------( )----||
      LINEA       T_BOCINA                        BOCINA
```
`LD %M5` · `AND %TM0.Q` · `ST %Q0.5`

---

### Sección 6 — ΔP y contador (Clase 3)

**Rung 6.1 — Escalado: ΔP [Pa] = puntos × 3 (0–1000 → 0–3000 Pa).**
```
 ||--------------------------------[ %MW0 := %IW0.0 * 3 ]----||
```
```
LD   1
[%MW0 := %IW0.0 * 3]
```

**Rung 6.2 — T_DP_ALTA: ΔP mayor que 1500 Pa.**
```
 ||----[ %MW0 > 1500 ]------| IN  %TM6  TON 10 s  Q |----||
                                  T_DP_ALTA
```
`BLK %TM6` · `LD [%MW0 > 1500]` · `IN` · `END_BLK`

**Rung 6.3 — Aviso ΔP alta tras 10 s sostenidos (filtro colmatado).**
`LD %TM6.Q` · `ST %M26`

**Rung 6.4 — T_DP_MUY_ALTA: ΔP mayor que 2000 Pa.**
`BLK %TM7` · `LD [%MW0 > 2000]` · `IN` · `END_BLK`

**Rung 6.5 — Memoriza la falla ΔP muy alta tras 10 s sostenidos.**
`LD %TM7.Q` · `S %M25`

**Rung 6.6 — Borra la falla ΔP muy alta con RESET y la presión ya normalizada.**
`LD %M50` · `ANDN %TM7.Q` · `R %M25`

**Rung 6.7 — T_HORA: ventana de 1 h que se reinicia sola al vencer.**
```
     %TM8.Q        +-----------------+
 ||----┤/├---------| IN  %TM8      Q |----||
     T_HORA        |  TON  3600 s    |
                   +-----------------+
                        T_HORA
```
`BLK %TM8` · `LDN %TM8.Q` · `IN` · `END_BLK`

> Al vencer, Q = 1 durante **un solo scan**: en el scan siguiente el contacto NC abre la entrada, el
> TON se reinicia y vuelve a contar. Ese pulso de un scan es el que resetea el contador en 6.8.

**Rung 6.8 — C_ARRANQUES: cuenta cada arranque de M3; se pone a 0 al cumplirse la hora.**
```
     %TM8.Q        +-----------------+
 ||----┤ ├---------| R   %C0         |
     T_HORA        |                 |
     %Q0.2         |  CTU  P = 6     |
 ||----┤ ├---------| CU            D |----||
    KM3_ELEV       +-----------------+
                       C_ARRANQUES
```
```
BLK  %C0
LD   %TM8.Q
R
LD   %Q0.2
CU
END_BLK
```
> La entrada CU del bloque ya detecta **flancos**: cuenta una vez por cada arranque, no mientras M3 está en marcha.

**Rung 6.9 — Aviso de 6 o más arranques en la hora.**
`LD [%C0.V >= 6]` · `ST %M29`

**Rung 6.10 — Copia el valor del contador a %MW1 para el SCADA.**
`LD 1` · `[%MW1 := %C0.V]`

> [!IMPORTANT]
> Para probar, poner temporalmente el preset de %TM8 en **120 s**, y volverlo a **3600 s** antes de entregar.

---

### Sección 7 — Señalización y SCADA (Clase 3)

**Rung 7.1 — BALIZA: intermitente si hay falla; fija si sólo hay avisos.**
```
      %M30          %S6                           %Q0.6
 ||--+-┤ ├-----------┤ ├-------------+------------( )----||
     |FALLA_GRAL  RELOJ_1S           |            BALIZA
     |                               |
     |  %M30       %M26              |
     +--┤/├----+----┤ ├--------+-----+
     FALLA_GRAL|  AV_DP_ALTA   |
               |   %M27        |
               +----┤ ├--------+
               |  AV_C1_LLENA  |
               |   %M28        |
               +----┤ ├--------+
               |  AV_C2_LLENA  |
               |   %M29        |
               +----┤ ├--------+
                  AV_ARRANQUES
```
```
LD   %M30
AND  %S6
OR(  %M26
OR   %M27
OR   %M28
OR   %M29
ANDN %M30
)
ST   %Q0.6
```

**Rung 7.2 — PILOTO_MARCHA: intermitente arrancando, fijo con M3 en marcha.**
```
      %M5          %Q0.2                          %Q0.7
 ||----┤ ├------+---┤ ├----+----------------------( )----||
      LINEA     | KM3_ELEV |                  PILOTO_MARCHA
                |   %S6    |
                +---┤ ├----+
                  RELOJ_1S
```
```
LD   %M5
AND( %Q0.2
OR   %S6
)
ST   %Q0.7
```

**Rungs 7.3 a 7.8 — Copias de las salidas a bits %M para el SCADA.**

| Rung | Comentario | IL |
|---|---|---|
| 7.3 | Estado M1 para SCADA | `LD %Q0.0` · `ST %M0` |
| 7.4 | Estado M2 para SCADA | `LD %Q0.1` · `ST %M1` |
| 7.5 | Estado M3 para SCADA | `LD %Q0.2` · `ST %M2` |
| 7.6 | Compuerta 1 para SCADA | `LD %Q0.3` · `ST %M3` |
| 7.7 | Compuerta 2 para SCADA | `LD %Q0.4` · `ST %M4` |
| 7.8 | Bocina para SCADA | `LD %Q0.5` · `ST %M6` |

```
      %Q0.0                                       %M0
 ||----┤ ├----------------------------------------( )----||
    KM1_ASPIR                                     EST_M1
```

---

## 4. Verificación del programa (checklist antes de simular)

- [ ] **Una sola bobina simple por bit.** Control cruzado: %Q0.0–%Q0.7, %M0–%M6, %M9, %M10, %M26–%M30,
      %M50, %M52, %M53 aparecen como `( )` **una sola vez** cada uno. LINEA, AL_xx, CMD_xx sólo con S/R.
- [ ] Todos los temporizadores con **base 1 s** y el tipo correcto (TP / TON / TOF).
- [ ] Cada rung con su comentario (los títulos en negrita de este documento sirven como comentario).
- [ ] *Programa → Compilar* sin errores ni advertencias.

> [!WARNING]
> **Estado inicial de las entradas en el simulador.** Por la convención de seguridad positiva, al iniciar
> el simulador todas las entradas valen 0: eso equivale a **emergencia accionada, guardamotores
> disparados y PARADA pulsada**. Antes de cada prueba poner en **1**: %I0.0, %I0.1, %I0.2, %I0.3,
> %I0.9, y %I0.4 (giro) para que M3 no caiga por AL_GIRO. Después pulsar RESET para borrar las fallas
> que quedaron memorizadas al arrancar.
