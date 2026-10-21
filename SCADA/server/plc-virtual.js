/**
 * PLC VIRTUAL — Modicon M221 TM221CE24R (emulado)
 * Alumno: Hugo Ariel Martinez · Proyecto PLC: Martinez.smbp
 * ------------------------------------------------
 * Ejecuta exactamente los 51 rungs del programa del TP (Resolucion/01_Programa_PLC.md)
 * con un ciclo de scan: 1) lectura de entradas  2) ejecución rung por rung  3) escritura de salidas
 * 4) comunicaciones (Modbus TCP, atendidas por el event-loop entre scans).
 *
 * Mapa Modbus (igual que el M221):
 *   Coils            0..255   -> %M0..%M255
 *   Holding regs     0..255   -> %MW0..%MW255
 * Extensiones SOLO del PLC virtual (para el panel de simulación de campo):
 *   Coils    100..113  -> %I0.0..%I0.13 (R/W)     Coils 120..129 -> %Q0.0..%Q0.9 (R)
 *   Coil     140       -> modelo de planta automático (R/W)
 *   Coil     141       -> forzar falla de giro (banda cortada) (R/W)
 *   HR       100       -> %IW0.0 (R/W)
 *   HR       110/111   -> nivel celda 1/2 en décimas de % (R/W)
 *   HR       120..128  -> %TM0..%TM8 .V (R)        HR 129 -> %C0.V (R)
 *   HR       130       -> firma 0x5643 ("VC" = Virtual Controller)
 *
 * Nota: las direcciones extendidas se superponen con %M100.. / %MW100.. que el programa no usa.
 */
'use strict';
const ModbusRTU = require('modbus-serial');

// ---------------------------------------------------------------- Memoria del PLC
const I = new Array(14).fill(false);   // imagen de entradas %I0.x
const Q = new Array(10).fill(false);   // imagen de salidas  %Q0.x
const M = new Array(256).fill(false);  // %M
const MW = new Array(256).fill(0);     // %MW
let IW0 = 0;                           // %IW0.0 (0..1000)
const field = {                        // estado "físico" de bornes (lo que cambia el panel de simulación)
  I: [true, true, true, true, false, false, false, false, false, true, false, false, false, false],
  IW0: 300,
};

// ---------------------------------------------------------------- Temporizadores (base 1 s)
class Timer {
  constructor(type, preset) { this.type = type; this.P = preset; this.Q = false; this.V = 0; this._t0 = null; this._prevIn = false; this._active = false; }
  run(IN, now) {
    const P = this.P * 1000;
    if (this.type === 'TON') {
      if (IN) { if (this._t0 === null) this._t0 = now; const e = now - this._t0; this.Q = e >= P; this.V = Math.min(this.P, Math.floor(e / 1000)); }
      else { this._t0 = null; this.Q = false; this.V = 0; }
    } else if (this.type === 'TOF') {
      if (IN) { this.Q = true; this._t0 = null; this.V = 0; }
      else if (this.Q) { if (this._t0 === null) this._t0 = now; const e = now - this._t0; this.V = Math.min(this.P, Math.floor(e / 1000)); if (e >= P) { this.Q = false; this._t0 = null; } }
      else { this.V = 0; }
    } else if (this.type === 'TP') {
      if (IN && !this._prevIn && !this._active) { this._active = true; this._t0 = now; }
      if (this._active) { const e = now - this._t0; this.V = Math.min(this.P, Math.floor(e / 1000)); if (e >= P) { this._active = false; this.Q = false; } else this.Q = true; }
      else { this.Q = false; if (!IN) this.V = 0; }
    }
    this._prevIn = IN;
  }
}
const TM = [
  new Timer('TP', 5),     // %TM0 T_BOCINA
  new Timer('TON', 5),    // %TM1 T_ARR_M2
  new Timer('TON', 5),    // %TM2 T_ARR_M3
  new Timer('TOF', 20),   // %TM3 T_VACIADO
  new Timer('TOF', 30),   // %TM4 T_BARRIDO
  new Timer('TON', 5),    // %TM5 T_GIRO
  new Timer('TON', 10),   // %TM6 T_DP_ALTA
  new Timer('TON', 10),   // %TM7 T_DP_MUY_ALTA
  new Timer('TON', Number(process.env.T_HORA || 3600)), // %TM8 T_HORA
];
const C0 = { V: 0, P: 6, _prevCU: false };

// Flancos ascendentes: cada instrucción ↑ tiene su propia memoria (como en el PLC)
const edgeMem = {};
function rising(key, v) { const r = v && !edgeMem[key]; edgeMem[key] = v; return r; }

// ---------------------------------------------------------------- Símbolos (alias legibles)
const S = {
  get PE_OK() { return I[0]; }, get GM1_OK() { return I[1]; }, get GM2_OK() { return I[2]; }, get GM3_OK() { return I[3]; },
  get GIRO_M3() { return I[4]; }, get LSH_C1() { return I[5]; }, get LSH_C2() { return I[6]; },
  get PB_RESET() { return I[7]; }, get PB_MARCHA() { return I[8]; }, get PB_PARADA() { return I[9]; },
};
const RELOJ_1S = () => (Date.now() % 1000) < 500; // %S6
// Direcciones %M
const A = { EST_M1: 0, EST_M2: 1, EST_M3: 2, EST_YV1: 3, EST_YV2: 4, LINEA: 5, EST_BOCINA: 6, PERMISO: 9, VIDA: 10,
  AL_EMERG: 20, AL_M1: 21, AL_M2: 22, AL_M3: 23, AL_GIRO: 24, AL_DP_MUY_ALTA: 25, AV_DP_ALTA: 26, AV_C1_LLENA: 27,
  AV_C2_LLENA: 28, AV_ARRANQUES: 29, FALLA_GRAL: 30, CMD_MARCHA: 40, CMD_PARADA: 41, CMD_RESET: 42,
  RESET_FALLAS: 50, DESTINO_LLENO: 52, CELDA_VALIDA: 53 };

// ---------------------------------------------------------------- Modelo de planta (opcional)
const plant = { auto: true, giroFail: false, level: [35, 10], giroDelay: 0 };
function plantStep(dt) {
  if (!plant.auto) return;
  const KM2 = Q[1], KM3 = Q[2];
  // Control de giro: aparece 1,2 s después de energizar M3 (salvo banda cortada forzada)
  if (KM3 && !plant.giroFail) { plant.giroDelay += dt; field.I[4] = plant.giroDelay >= 1.2; }
  else { plant.giroDelay = 0; field.I[4] = false; }
  // Llenado: con elevador y redler en marcha, la celda con compuerta abierta sube (≈ 100 % en 120 s, acelerado para demo)
  const flowing = KM3 && KM2 && field.I[4];
  if (flowing && Q[3]) plant.level[0] = Math.min(100, plant.level[0] + dt * 100 / 120);
  if (flowing && Q[4]) plant.level[1] = Math.min(100, plant.level[1] + dt * 100 / 120);
  field.I[5] = plant.level[0] >= 95;
  field.I[6] = plant.level[1] >= 95;
}

// ---------------------------------------------------------------- Programa (51 rungs)
function scan(now) {
  // (1) Lectura de entradas -> imagen
  for (let k = 0; k < 14; k++) I[k] = field.I[k];
  IW0 = Math.max(0, Math.min(1000, Math.round(field.IW0)));

  // ===== Sección 1 — Generales
  M[A.VIDA] = RELOJ_1S();                                                       // 1.1
  { const c = M[A.CMD_RESET] || rising('PB_RESET', S.PB_RESET);                 // 1.2
    M[A.RESET_FALLAS] = c; if (c) M[A.CMD_RESET] = false; }

  // ===== Sección 2 — Fallas
  if (!S.PE_OK) M[A.AL_EMERG] = true;                                           // 2.1
  if (M[A.RESET_FALLAS] && S.PE_OK) M[A.AL_EMERG] = false;                      // 2.2
  if (!S.GM1_OK) M[A.AL_M1] = true;                                             // 2.3
  if (M[A.RESET_FALLAS] && S.GM1_OK) M[A.AL_M1] = false;                        // 2.4
  if (!S.GM2_OK) M[A.AL_M2] = true;                                             // 2.5
  if (M[A.RESET_FALLAS] && S.GM2_OK) M[A.AL_M2] = false;                        // 2.6
  if (!S.GM3_OK) M[A.AL_M3] = true;                                             // 2.7
  if (M[A.RESET_FALLAS] && S.GM3_OK) M[A.AL_M3] = false;                        // 2.8
  TM[5].run(Q[2] && !S.GIRO_M3, now);                                           // 2.9  T_GIRO
  if (TM[5].Q) M[A.AL_GIRO] = true;                                             // 2.10
  if (M[A.RESET_FALLAS] && !TM[5].Q) M[A.AL_GIRO] = false;                      // 2.11
  M[A.FALLA_GRAL] = M[A.AL_EMERG] || M[A.AL_M1] || M[A.AL_M2] || M[A.AL_M3]     // 2.12
    || M[A.AL_GIRO] || M[A.AL_DP_MUY_ALTA];

  // ===== Sección 3 — Celdas y permiso
  const c1 = MW[10] === 1, c2 = MW[10] === 2;
  M[A.CELDA_VALIDA] = c1 || c2;                                                 // 3.1
  M[A.DESTINO_LLENO] = (c1 && S.LSH_C1) || (c2 && S.LSH_C2);                    // 3.2
  M[A.AV_C1_LLENA] = S.LSH_C1;                                                  // 3.3
  M[A.AV_C2_LLENA] = S.LSH_C2;                                                  // 3.4
  Q[3] = c1 && !M[A.AL_EMERG];                                                  // 3.5 YV1_C1
  Q[4] = c2 && !M[A.AL_EMERG];                                                  // 3.6 YV2_C2
  M[A.PERMISO] = S.PE_OK && !M[A.FALLA_GRAL] && M[A.CELDA_VALIDA] && !M[A.DESTINO_LLENO]; // 3.7

  // ===== Sección 4 — Marcha y parada
  if ((M[A.CMD_MARCHA] || rising('PB_MARCHA', S.PB_MARCHA)) && M[A.PERMISO]) M[A.LINEA] = true;      // 4.1
  if (M[A.CMD_PARADA] || !S.PB_PARADA || M[A.DESTINO_LLENO] || M[A.FALLA_GRAL]) M[A.LINEA] = false;  // 4.2
  if (M[A.CMD_MARCHA] || M[A.CMD_PARADA]) { M[A.CMD_MARCHA] = false; M[A.CMD_PARADA] = false; }      // 4.3
  TM[0].run(M[A.LINEA], now);                                                   // 4.4 T_BOCINA (TP)
  TM[1].run(M[A.LINEA] && Q[0], now);                                           // 4.5 T_ARR_M2
  TM[2].run(M[A.LINEA] && Q[1], now);                                           // 4.6 T_ARR_M3
  TM[3].run(Q[2], now);                                                         // 4.7 T_VACIADO (TOF)
  TM[4].run(Q[1], now);                                                         // 4.8 T_BARRIDO (TOF)

  // ===== Sección 5 — Motores y bocina
  Q[0] = S.PE_OK && !M[A.AL_EMERG] && S.GM1_OK && !M[A.AL_M1]                   // 5.1 KM1_ASPIR
    && ((M[A.LINEA] && !TM[0].Q) || TM[4].Q);
  Q[1] = S.PE_OK && !M[A.AL_EMERG] && S.GM2_OK && !M[A.AL_M2]                   // 5.2 KM2_REDLER
    && ((M[A.LINEA] && TM[1].Q) || (Q[1] && TM[3].Q));
  Q[2] = S.PE_OK && !M[A.AL_EMERG] && S.GM3_OK && !M[A.AL_M3] && !M[A.AL_GIRO]  // 5.3 KM3_ELEV
    && Q[1] && M[A.LINEA] && TM[2].Q;
  Q[5] = M[A.LINEA] && TM[0].Q;                                                 // 5.4 BOCINA

  // ===== Sección 6 — ΔP y contador
  MW[0] = IW0 * 3;                                                              // 6.1
  TM[6].run(MW[0] > 1500, now);                                                 // 6.2
  M[A.AV_DP_ALTA] = TM[6].Q;                                                    // 6.3
  TM[7].run(MW[0] > 2000, now);                                                 // 6.4
  if (TM[7].Q) M[A.AL_DP_MUY_ALTA] = true;                                      // 6.5
  if (M[A.RESET_FALLAS] && !TM[7].Q) M[A.AL_DP_MUY_ALTA] = false;               // 6.6
  TM[8].run(!TM[8].Q, now);                                                     // 6.7 T_HORA
  if (TM[8].Q) C0.V = 0;                                                        // 6.8 C_ARRANQUES (R prioritario)
  else if (Q[2] && !C0._prevCU) C0.V = Math.min(9999, C0.V + 1);
  C0._prevCU = Q[2];
  M[A.AV_ARRANQUES] = C0.V >= 6;                                                // 6.9
  MW[1] = C0.V;                                                                 // 6.10

  // ===== Sección 7 — Señalización y SCADA
  const s6 = RELOJ_1S();
  Q[6] = (M[A.FALLA_GRAL] && s6) || (!M[A.FALLA_GRAL] &&                        // 7.1 BALIZA
    (M[A.AV_DP_ALTA] || M[A.AV_C1_LLENA] || M[A.AV_C2_LLENA] || M[A.AV_ARRANQUES]));
  Q[7] = M[A.LINEA] && (Q[2] || s6);                                            // 7.2 PILOTO_MARCHA
  M[A.EST_M1] = Q[0]; M[A.EST_M2] = Q[1]; M[A.EST_M3] = Q[2];                   // 7.3 .. 7.5
  M[A.EST_YV1] = Q[3]; M[A.EST_YV2] = Q[4]; M[A.EST_BOCINA] = Q[5];             // 7.6 .. 7.8
  // (3) escritura de salidas: Q[] ya es la imagen de salida que lee el modelo de planta
}

// ---------------------------------------------------------------- Modbus TCP server
const toU16 = (v) => (v < 0 ? v + 65536 : v) & 0xffff;
const toS16 = (v) => (v > 32767 ? v - 65536 : v);
const vector = {
  getCoil(addr) {
    if (addr >= 100 && addr <= 113) return field.I[addr - 100];
    if (addr >= 120 && addr <= 129) return Q[addr - 120];
    if (addr === 140) return plant.auto;
    if (addr === 141) return plant.giroFail;
    return !!M[addr];
  },
  setCoil(addr, value) {
    if (addr >= 100 && addr <= 113) { field.I[addr - 100] = !!value; return; }
    if (addr === 140) { plant.auto = !!value; return; }
    if (addr === 141) { plant.giroFail = !!value; return; }
    if (addr < 256) M[addr] = !!value;
  },
  getDiscreteInput(addr) { return addr < 14 ? I[addr] : false; },
  getInputRegister(addr) { return addr === 0 ? IW0 : 0; },
  getHoldingRegister(addr) {
    if (addr === 100) return field.IW0;
    if (addr === 110) return Math.round(plant.level[0] * 10);
    if (addr === 111) return Math.round(plant.level[1] * 10);
    if (addr >= 120 && addr <= 128) return TM[addr - 120].V;
    if (addr === 129) return C0.V;
    if (addr === 130) return 0x5643;
    return toU16(MW[addr] || 0);
  },
  setRegister(addr, value) {
    if (addr === 100) { field.IW0 = Math.max(0, Math.min(1000, value)); return; }
    if (addr === 110) { plant.level[0] = Math.max(0, Math.min(100, value / 10)); return; }
    if (addr === 111) { plant.level[1] = Math.max(0, Math.min(100, value / 10)); return; }
    if (addr < 256) MW[addr] = toS16(value);
  },
};

function start(port = 5020, opts = {}) {
  const host = opts.host || '0.0.0.0';
  const server = new ModbusRTU.ServerTCP(vector, { host, port, debug: false, unitID: 255 });
  server.on('socketError', (err) => console.error('[PLC virtual] socket error:', err.message));
  server.on('error', (err) => console.error('[PLC virtual] error:', err.message));
  let last = Date.now();
  setInterval(() => {
    const now = Date.now();
    plantStep((now - last) / 1000);
    scan(now);
    last = now;
  }, 10); // ciclo de scan ≈ 10 ms
  console.log(`[PLC virtual] M221 emulado en ejecución — Modbus TCP ${host}:${port} (T_HORA = ${TM[8].P} s)`);
  return server;
}

module.exports = { start };

if (require.main === module) start(Number(process.env.PLC_PORT || 5020));
