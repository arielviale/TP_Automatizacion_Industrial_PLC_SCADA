# Memoria — Respuestas a las preguntas 1 a 8

**Asignatura:** Automatización Industrial — UTN Facultad Regional Paraná  
**Alumno:** Hugo Ariel Martinez · **Proyecto PLC:** `Martinez.smbp` (Modicon M221)

---

## Pregunta 1 — Dirección Modbus de %M10 en FUXA

**¿Qué número de dirección hubo que cargar en FUXA para leer %M10? Si el valor apareció corrido una posición, explicar la diferencia entre la numeración Modbus que empieza en 0 y la que empieza en 1.**

El servidor Modbus TCP del M221 publica los bits internos **%Mi como *coils*** (funciones 01/05/15) y las palabras
**%MWi como *holding registers*** (funciones 03/06/16). La correspondencia es directa con el índice:
**%M10 → coil con dirección 10** en el protocolo, y %MW10 → holding register 10.

En la trama Modbus la dirección siempre viaja **base 0**: el primer coil es el 0. Pero muchos manuales y
SCADA usan la notación clásica de Modicon **base 1**, donde los coils se numeran 00001…09999 y los holding
registers 40001…49999. En esa notación el coil 0 del protocolo se llama «00001». Por eso el mismo bit puede
aparecer como **10** (base 0, dirección de protocolo) o como **11** (base 1, referencia Modicon).

> **Resultado obtenido:** 
> - En **FUXA**, la dirección depende de cómo interprete el driver Modbus TCP del release instalado: si opera en **base 0**, la dirección directa de protocolo es **10**; si opera en notación Modicon **base 1** (rango 00001–09999), se debe cargar **11** (10 + 1).
> - En nuestra **SCADA Propia**, el stack de comunicaciones (`modbus-serial` sobre Node.js) opera de forma nativa en **base 0** (trama pura Modbus, función 01 en dirección 10). Adicionalmente, el panel de configuración de la SCADA incluye un selector paramétrico de *offset* (0 o 1) para adaptarse sin alterar el código tanto al simulador interno como al servidor Modbus TCP del M221 TM221CE24R.

---

## Pregunta 2 — Pulsador de PARADA cableado NC y usado con contacto NC

**¿Por qué el pulsador de PARADA se cablea NC y en el programa se usa con un contacto NC?**

- **Cableado NC (seguridad positiva):** en reposo el circuito está cerrado y %I0.9 = 1. Si se corta un
  cable, se afloja un borne o falta la alimentación de 24 V, la entrada cae a 0, **igual que si se
  pulsara PARADA**. Así, una falla del cableado termina en una parada (el lado seguro) y nunca deja
  inutilizado el pulsador. Con un NA, un cable cortado dejaría la línea **sin poder pararse** y nadie
  lo notaría hasta necesitarlo.
- **Contacto NC en el programa (`/PB_PARADA`):** el rung 4.2 tiene que *conducir* para resetear LINEA.
  Como la señal vale 1 en reposo y 0 al pulsar (o con el cable cortado), hay que invertirla: el contacto
  NC conduce justamente cuando %I0.9 = 0. Esto **no** es un «doble negado» que anule la seguridad: lo
  que importa es que el estado de reposo sea 1, y que la pérdida de esa señal provoque la parada.

---

## Pregunta 3 — Vaciado del redler con TOF y no con TON

**¿Por qué el vaciado del redler se resuelve con un TOF y no con un TON?**

Hace falta que M2 **siga funcionando 20 s después** de que se detuvo M3. Eso es exactamente un
**retardo a la desconexión**:

- **TOF** (entrada = KM3_ELEV): mientras M3 marcha, Q = 1. Cuando M3 para, la entrada cae, pero Q
  **sigue en 1 durante 20 s** y después cae. Esa salida mantiene KM2 (`KM2_REDLER · T_VACIADO.Q`).
  Un solo bloque y un solo contacto.
- **TON:** su salida recién se activa *después* de que la entrada estuvo en 1 el tiempo del preset, o sea
  que hace un retardo **a la conexión**. Para lograr lo mismo con un TON habría que alimentarlo con
  `/KM3`, agregar un bit de memoria (SET al parar M3 y RESET al vencer) y usar `/TON.Q` para mantener
  M2. Son más rungs, más bits y más posibilidades de error, por ejemplo que el TON quede contando desde
  el arranque, cuando KM3 todavía es 0.

Además, con el TOF el vaciado sólo existe si **M3 llegó a funcionar**: si la parada ocurre antes, el TOF
nunca se activó y M2 para en el acto (no hay trigo que vaciar).

---

## Pregunta 4 — Función del contacto KM2_REDLER en el rung de KM3

**¿Qué función cumple el contacto KM2_REDLER en el rung de KM3? ¿Qué pasaría si no estuviera?**

Es un **enclavamiento de secuencia (interlock)**: el elevador M3 sólo puede funcionar si el redler M2,
que recibe su descarga, está realmente en marcha. Ese contacto hace que:

1. **M3 no pueda arrancar sin M2.**
2. **Si M2 se detiene por cualquier causa** (disparo de su guardamotor, emergencia o un error del
   programa), **M3 se detiene en el mismo scan.** Es el criterio «se detienen el equipo afectado y los
   que lo alimentan» (prueba 5).

**Sin ese contacto:** si salta el guardamotor de M2, KM3 seguiría cerrado hasta que el reset de LINEA
llegue por FALLA_GRAL. Es casi inmediato, pero depende de una cadena más larga (AL_M2 → FALLA_GRAL →
RESET LINEA) en lugar de una condición directa sobre el equipo. Peor todavía: si se modificara el
programa o la falla no estuviera memorizada, el elevador seguiría descargando trigo sobre un redler
detenido. El resultado sería **atoramiento** del redler y de la cabeza del elevador, sobrecarga de
cadena o banda, y riesgo de derrame y de polvo (riesgo de explosión en molinos). El interlock directo
es la protección física, y la falla memorizada es la parte de información y bloqueo.

---

## Pregunta 5 — Marcha local con flanco y no con el contacto directo

**¿Por qué la marcha local usa un flanco y no el contacto directo del pulsador?**

- **Una pulsación = una orden.** El flanco ascendente `↑PB_MARCHA` conduce **un solo scan**, cuando
  el pulsador pasa de 0 a 1. Si el operador lo mantiene apretado (o el pulsador queda trabado), la
  orden no se repite.
- **Evita rearranques automáticos.** Con un contacto directo, si el pulsador queda apretado o trabado y
  la línea para por celda llena, por una falla que después se resetea o por PARADA, LINEA se volvería a
  setear **sola** en cuanto vuelva el PERMISO: la bocina y los motores arrancarían sin una acción
  voluntaria del operador. Con el flanco hace falta **soltar y volver a pulsar**.
- **Evita la pelea SET/RESET.** Si se mantiene MARCHA y se pulsa PARADA, el SET y el RESET de LINEA
  estarían activos a la vez en cada scan. Con el flanco, el SET dura un scan y la parada se impone sin
  ambigüedad.
- **Contador de arranques confiable:** cada arranque real corresponde a una única orden.

(El mismo criterio se aplica a ↑PB_RESET. Las órdenes del SCADA ya son pulsos, porque el PLC las vuelve a 0 con la bobina RESET.)

---

## Pregunta 6 — Escalado ×3 de %IW0.0

**¿Por qué el valor de %IW0.0 se multiplica por 3? Verificar con un ejemplo: ¿cuántos Pa son 600 puntos?**

La entrada analógica en escala «normal» convierte 0–10 V en **0–1000 puntos**, y el transmisor PDT-01
entrega 0–10 V para **0–3000 Pa**. Las dos escalas son lineales y empiezan en cero, así que:

$$\Delta P\,[\text{Pa}] = \text{puntos} \times \frac{3000\ \text{Pa}}{1000\ \text{puntos}} = \text{puntos} \times 3$$

**Ejemplo:** 600 puntos → 600 × 3 = **1800 Pa** (equivale a 6 V en la entrada).
Comprobación con la prueba 9: 600 pts = 1800 Pa > 1500 → aviso; 700 pts = 2100 Pa > 2000 → falla.

La cuenta entra en un entero de 16 bits: el máximo es 1000 × 3 = 3000 < 32 767, así que no hay
desborde. La resolución resultante es de 3 Pa por punto, suficiente para umbrales de 1500 y 2000 Pa.

---

## Pregunta 7 — Retardo de 10 s en las alarmas de ΔP

**¿Para qué sirve el retardo de 10 s en las alarmas de presión diferencial?**

Es un **filtro temporal contra falsas alarmas**. La ΔP de un filtro de mangas no es una señal estable:

- Cada **pulso de limpieza** (aire comprimido que sacude las mangas) produce un **pico transitorio** de ΔP.
- Los **arranques** del ventilador, los cambios de carga de polvo y el ruido eléctrico en la señal
  analógica generan oscilaciones alrededor del umbral.

Con el TON de 10 s, el aviso o la falla sólo aparecen si la ΔP **se mantiene** por encima del umbral
de forma sostenida, que es lo que ocurre cuando el filtro realmente se colmata. Sin el retardo:

- el aviso «parpadearía» en el SCADA y el operador terminaría ignorándolo;
- la falla de 2000 Pa provocaría **paradas innecesarias** de toda la línea. Cada parada suma un
  arranque del elevador, y además el rearranque está limitado a 6 por hora.

---

## Pregunta 8 — Copiar %Q a bits %M para el SCADA

**¿Por qué hay que copiar las salidas %Q a bits %M para verlas en el SCADA?**

1. **Mapa Modbus del M221:** el servidor Modbus TCP del controlador da acceso a la memoria **%M (coils)
   y %MW (registers)**. Las salidas físicas %Q no están en ese mapa de coils, por lo que el SCADA no las
   puede leer directamente. Copiarlas a %M0…%M6 las hace visibles.
2. **Seguridad:** si el SCADA pudiera direccionar %Q, también podría **escribirlas** (función 05) y
   accionar un contactor saltando todos los enclavamientos del programa. Con las copias, el SCADA sólo
   **lee estados** y sólo escribe **órdenes** (CMD_xx, %MW10), que el programa valida con PERMISO.
3. **Mapa ordenado y estable:** todos los estados quedan en un bloque contiguo (%M0…%M6) que se lee con
   una sola petición. Si mañana se recablea un contactor a otra salida, sólo cambia el rung de copia y
   la pantalla del SCADA no se toca.
