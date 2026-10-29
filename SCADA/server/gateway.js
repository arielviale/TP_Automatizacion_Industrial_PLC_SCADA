/**
 * GATEWAY SCADA — Línea de llenado de celdas
 * Alumno: Hugo Ariel Martinez · Proyecto PLC: Martinez.smbp
 * -------------------------------------------
 *  Navegador  <──WebSocket──>  gateway (este archivo)  <──Modbus TCP──>  PLC (M221 simulado en
 *                                                                        Machine Expert o PLC virtual)
 *  - Sondeo cíclico de %M0..%M63 (coils) y %MW0..%MW11 (holding registers)
 *  - Escritura de órdenes (CMD_MARCHA / CMD_PARADA / CMD_RESET) y de la celda destino (%MW10)
 *  - Motor de alarmas con estados ISA-18.2 (activa no reconocida, activa reconocida, normalizada no reconocida)
 *  - Supervisión de comunicación: error Modbus + vigilancia de la señal de VIDA
 *  - Historial de alarmas y eventos persistente (data/historial.json)
 */
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const ModbusRTU = require('modbus-serial');
const { WebSocketServer } = require('ws');

const ROOT = path.join(__dirname, '..');
const PUBLIC = path.join(ROOT, 'public');
const DATA = path.join(ROOT, 'data');
fs.mkdirSync(DATA, { recursive: true });

// ------------------------------------------------------------------ Configuración
const CFG_FILE = path.join(DATA, 'config.json');
const defaults = {
  httpPort: 8080,
  startVirtualPlc: true,
  virtualPort: 5020,
  target: 'virtual',                       // 'virtual' | 'machine'
  targets: {
    virtual: { name: 'PLC virtual', host: '127.0.0.1', port: 5020 },
    machine: { name: 'Machine Expert Basic (simulador M221)', host: '127.0.0.1', port: 502 },
  },
  unitId: 1,
  offset: 0,                               // corrimiento de direcciones (base 0 / base 1)
  pollMs: 250,
  vidaTimeoutMs: 3000,
};
let cfg = { ...defaults };
try { cfg = { ...defaults, ...JSON.parse(fs.readFileSync(CFG_FILE, 'utf8')) }; } catch { /* primera ejecución */ }
const saveCfg = () => fs.writeFileSync(CFG_FILE, JSON.stringify(cfg, null, 2));
saveCfg();

// ------------------------------------------------------------------ Tags
const COILS = {
  EST_M1: 0, EST_M2: 1, EST_M3: 2, EST_YV1: 3, EST_YV2: 4, LINEA: 5, EST_BOCINA: 6, PERMISO: 9, VIDA: 10,
  AL_EMERG: 20, AL_M1: 21, AL_M2: 22, AL_M3: 23, AL_GIRO: 24, AL_DP_MUY_ALTA: 25, AV_DP_ALTA: 26,
  AV_C1_LLENA: 27, AV_C2_LLENA: 28, AV_ARRANQUES: 29, FALLA_GRAL: 30, CMD_MARCHA: 40, CMD_PARADA: 41, CMD_RESET: 42,
  RESET_FALLAS: 50, DESTINO_LLENO: 52, CELDA_VALIDA: 53,
};
const COMMANDS = { CMD_MARCHA: 'MARCHA', CMD_PARADA: 'PARADA', CMD_RESET: 'RESET de fallas' };

const ALARMS = [
  { id: 'AL_EMERG', text: 'Parada de emergencia accionada', prio: 'Alta' },
  { id: 'AL_M1', text: 'Disparo de guardamotor del ventilador M1', prio: 'Alta' },
  { id: 'AL_M2', text: 'Disparo de guardamotor del redler M2', prio: 'Alta' },
  { id: 'AL_M3', text: 'Disparo de guardamotor del elevador M3', prio: 'Alta' },
  { id: 'AL_GIRO', text: 'Elevador sin giro (banda patinando o cortada)', prio: 'Alta' },
  { id: 'AL_DP_MUY_ALTA', text: 'Presión diferencial muy alta: línea detenida', prio: 'Alta' },
  { id: 'AV_DP_ALTA', text: 'Filtro colmatado: programar limpieza', prio: 'Baja' },
  { id: 'AV_C1_LLENA', text: 'Celda 1 llena', prio: 'Baja' },
  { id: 'AV_C2_LLENA', text: 'Celda 2 llena', prio: 'Baja' },
  { id: 'AV_ARRANQUES', text: 'Exceso de arranques del elevador en la última hora', prio: 'Baja' },
  { id: 'COMM', text: 'Pérdida de comunicación con el PLC', prio: 'Alta', system: true },
];

// ------------------------------------------------------------------ Estado
const state = {
  conn: { status: 'down', detail: 'Iniciando…', lastOk: 0, latency: 0, virtual: false, errors: 0 },
  tags: {},
  dp: 0, arranques: 0, celda: 0,
  sim: null,
  vidaLast: null, vidaChangedAt: 0,
};
const alarmState = {};
ALARMS.forEach((a) => (alarmState[a.id] = { active: false, acked: true, tOn: 0, tOff: 0, tAck: 0 }));

// ------------------------------------------------------------------ Historial (alarmas + eventos)
const HIST_FILE = path.join(DATA, 'historial.json');
let history = [];
try { history = JSON.parse(fs.readFileSync(HIST_FILE, 'utf8')); } catch { history = []; }
let histDirty = false;
function log(kind, id, text, prio, detail) {
  history.unshift({ t: Date.now(), kind, id, text, prio: prio || '', detail: detail || '' });
  if (history.length > 2000) history.length = 2000;
  histDirty = true;
  broadcast({ t: 'hist', items: history.slice(0, 500) });
}
setInterval(() => { if (histDirty) { fs.writeFile(HIST_FILE, JSON.stringify(history), () => {}); histDirty = false; } }, 3000);

// ------------------------------------------------------------------ Motor de alarmas
function setAlarm(id, active) {
  const a = ALARMS.find((x) => x.id === id); const s = alarmState[id];
  if (active && !s.active) { s.active = true; s.acked = false; s.tOn = Date.now(); s.tOff = 0; log('alarma', id, a.text, a.prio, 'ACTIVA'); }
  else if (!active && s.active) { s.active = false; s.tOff = Date.now(); log('alarma', id, a.text, a.prio, 'NORMALIZADA'); }
}
function ackAlarm(id, who = 'Operador') {
  const s = alarmState[id]; const a = ALARMS.find((x) => x.id === id);
  if (!s || s.acked) return;
  s.acked = true; s.tAck = Date.now(); log('alarma', id, a.text, a.prio, `RECONOCIDA (${who})`);
}
function activeAlarms() {
  return ALARMS.filter((a) => alarmState[a.id].active || !alarmState[a.id].acked).map((a) => {
    const s = alarmState[a.id];
    return { ...a, ...s, st: s.active ? (s.acked ? 'ACT_RECON' : 'ACT_NO_RECON') : 'NORM_NO_RECON' };
  }).sort((x, y) => (x.prio === y.prio ? y.tOn - x.tOn : x.prio === 'Alta' ? -1 : 1));
}

// ------------------------------------------------------------------ Cliente Modbus con cola serializada
let client = null; let connecting = false; let queue = Promise.resolve();
const enqueue = (fn) => (queue = queue.then(fn, fn));
const A = (n) => n + Number(cfg.offset || 0);

async function connect() {
  if (connecting) return; connecting = true;
  const t = cfg.targets[cfg.target];
  try {
    if (client) { try { client.close(() => {}); } catch { /* */ } }
    client = new ModbusRTU();
    client.setTimeout(1000);
    state.conn.detail = `Conectando a ${t.host}:${t.port}…`;
    await client.connectTCP(t.host, { port: t.port });
    client.setID(cfg.unitId);
    // Detección del PLC virtual (firma en HR 130)
    try { const r = await client.readHoldingRegisters(130, 1); state.conn.virtual = r.data[0] === 0x5643; } catch { state.conn.virtual = false; }
    state.conn.status = 'ok'; state.conn.detail = `${t.name} · ${t.host}:${t.port}`;
    state.vidaChangedAt = Date.now();
    log('evento', 'CONN', `Conectado a ${t.name} (${t.host}:${t.port})`, '', state.conn.virtual ? 'PLC virtual' : 'Modbus TCP');
  } catch (e) {
    markDown(`Sin conexión con ${t.host}:${t.port} (${e.code || e.message})`);
  } finally { connecting = false; }
}
function markDown(detail) {
  if (state.conn.status !== 'down') log('evento', 'CONN', 'Comunicación perdida', '', detail);
  state.conn.status = 'down'; state.conn.detail = detail; state.conn.errors++;
  setAlarm('COMM', true);
  try { client && client.close(() => {}); } catch { /* */ }
  client = null;
}

const prevTags = {};
async function poll() {
  if (!client || !client.isOpen) { if (!connecting) await connect(); return; }
  const t0 = Date.now();
  try {
    const coils = await client.readCoils(A(0), 64);
    const regs = await client.readHoldingRegisters(A(0), 12);
    const tags = {};
    for (const [k, n] of Object.entries(COILS)) tags[k] = !!coils.data[n];
    const s16 = (v) => (v > 32767 ? v - 65536 : v);
    state.dp = s16(regs.data[0]); state.arranques = s16(regs.data[1]); state.celda = s16(regs.data[10]);
    if (state.conn.virtual) {
      const sc = await client.readCoils(100, 42);
      const sr = await client.readHoldingRegisters(100, 30);
      state.sim = {
        I: sc.data.slice(0, 14), Q: sc.data.slice(20, 30), plantAuto: sc.data[40], giroFail: sc.data[41],
        IW0: sr.data[0], level: [sr.data[10] / 10, sr.data[11] / 10], TM: sr.data.slice(20, 29), C0: sr.data[29],
      };
    } else state.sim = null;
    state.tags = tags;
    state.conn.latency = Date.now() - t0; state.conn.lastOk = Date.now();

    // Vigilancia de la señal de vida
    if (tags.VIDA !== state.vidaLast) { state.vidaLast = tags.VIDA; state.vidaChangedAt = Date.now(); }
    const vidaOk = Date.now() - state.vidaChangedAt < cfg.vidaTimeoutMs;
    const newStatus = vidaOk ? 'ok' : 'stale';
    if (newStatus !== state.conn.status) {
      if (newStatus === 'stale') log('evento', 'VIDA', 'Señal de vida detenida (PLC en STOP o simulador pausado)', '', '');
      else log('evento', 'VIDA', 'Señal de vida restablecida', '', '');
    }
    state.conn.status = newStatus;
    setAlarm('COMM', !vidaOk);

    // Alarmas de proceso (sólo con datos válidos)
    if (vidaOk) for (const a of ALARMS) if (!a.system) setAlarm(a.id, tags[a.id]);

    // Eventos de proceso
    const ev = (k, on, off) => { if (prevTags[k] !== undefined && prevTags[k] !== tags[k]) log('evento', k, tags[k] ? on : off); };
    ev('LINEA', 'Orden de marcha de la línea (LINEA = 1)', 'Línea detenida (LINEA = 0)');
    ev('EST_M1', 'M1 Ventilador de aspiración: arranque', 'M1 Ventilador de aspiración: parada');
    ev('EST_M2', 'M2 Redler distribuidor: arranque', 'M2 Redler distribuidor: parada');
    ev('EST_M3', 'M3 Elevador de cangilones: arranque', 'M3 Elevador de cangilones: parada');
    Object.assign(prevTags, tags);
  } catch (e) {
    markDown(`Error Modbus: ${e.message || e}`);
  }
}

function loop() { enqueue(poll).finally(() => { broadcastSnap(); setTimeout(loop, cfg.pollMs); }); }

// ------------------------------------------------------------------ Escrituras
function writeCoil(n, v) { return enqueue(async () => { if (!client || !client.isOpen) throw new Error('sin conexión'); await client.writeCoil(n, v); }); }
function writeReg(n, v) { return enqueue(async () => { if (!client || !client.isOpen) throw new Error('sin conexión'); await client.writeRegister(n, v & 0xffff); }); }

async function handle(msg, ws) {
  const reply = (ok, text) => ws.send(JSON.stringify({ t: 'toast', ok, text }));
  try {
    switch (msg.t) {
      case 'cmd': {
        if (!COMMANDS[msg.name]) return;
        await writeCoil(A(COILS[msg.name]), true);
        log('evento', msg.name, `Orden del operador: ${COMMANDS[msg.name]}`, '', 'SCADA');
        if (msg.name === 'CMD_RESET') ALARMS.forEach((a) => { if (!a.system && !alarmState[a.id].active) ackAlarm(a.id, 'RESET'); });
        return reply(true, `Orden ${COMMANDS[msg.name]} enviada`);
      }
      case 'celda': {
        const v = Number(msg.value); if (![0, 1, 2].includes(v)) return;
        await writeReg(A(10), v);
        log('evento', 'CELDA', v ? `Destino seleccionado: celda ${v}` : 'Destino anulado', '', 'SCADA');
        return reply(true, v ? `Destino: celda ${v}` : 'Destino anulado');
      }
      case 'ack': {
        if (msg.id === 'all') ALARMS.forEach((a) => ackAlarm(a.id)); else ackAlarm(msg.id);
        return broadcastSnap();
      }
      case 'sim': { // sólo PLC virtual
        if (!state.conn.virtual) return reply(false, 'El panel de campo sólo funciona con el PLC virtual');
        if (msg.kind === 'I') await writeCoil(100 + msg.n, !!msg.value);
        else if (msg.kind === 'pulse') { await writeCoil(100 + msg.n, true); setTimeout(() => writeCoil(100 + msg.n, false).catch(() => {}), 400); }
        else if (msg.kind === 'IW0') await writeReg(100, Math.max(0, Math.min(1000, Math.round(msg.value))));
        else if (msg.kind === 'plantAuto') await writeCoil(140, !!msg.value);
        else if (msg.kind === 'giroFail') await writeCoil(141, !!msg.value);
        else if (msg.kind === 'level') await writeReg(110 + msg.n, Math.round(msg.value * 10));
        return;
      }
      case 'config': {
        if (msg.target && cfg.targets[msg.target]) cfg.target = msg.target;
        if (msg.machine) cfg.targets.machine = { ...cfg.targets.machine, ...msg.machine, port: Number(msg.machine.port || 502) };
        if (msg.offset !== undefined) cfg.offset = Number(msg.offset) || 0;
        if (msg.unitId !== undefined) cfg.unitId = Number(msg.unitId) || 1;
        saveCfg();
        log('evento', 'CONFIG', `Configuración de comunicación: ${cfg.targets[cfg.target].name}`, '', `offset ${cfg.offset}, unit ${cfg.unitId}`);
        enqueue(async () => { try { client && client.close(() => {}); } catch { /* */ } client = null; state.conn.status = 'down'; state.conn.detail = 'Reconectando…'; });
        return reply(true, 'Configuración aplicada');
      }
      case 'clearHist': history = []; histDirty = true; broadcast({ t: 'hist', items: [] }); return;
    }
  } catch (e) { reply(false, `No se pudo enviar: ${e.message}`); }
}

// ------------------------------------------------------------------ HTTP + WebSocket
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (url === '/api/historial.csv') {
    const rows = [['Fecha', 'Hora', 'Tipo', 'Tag', 'Descripcion', 'Prioridad', 'Estado']]
      .concat(history.map((h) => { const d = new Date(h.t); return [d.toLocaleDateString('es-AR'), d.toLocaleTimeString('es-AR'), h.kind, h.id, h.text, h.prio, h.detail]; }));
    res.writeHead(200, { 'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': 'attachment; filename="historial_scada.csv"' });
    return res.end('\ufeff' + rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(';')).join('\r\n'));
  }
  const file = path.normalize(path.join(PUBLIC, url === '/' ? 'index.html' : url));
  if (!file.startsWith(PUBLIC)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404); return res.end('404'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
    res.end(buf);
  });
});
const wss = new WebSocketServer({ server });
function broadcast(obj) { const s = JSON.stringify(obj); wss.clients.forEach((c) => c.readyState === 1 && c.send(s)); }
function snapshot() {
  return { t: 'snap', now: Date.now(), conn: state.conn, tags: state.tags, dp: state.dp, arranques: state.arranques, celda: state.celda,
    sim: state.sim, alarms: activeAlarms(),
    cfg: { target: cfg.target, targets: cfg.targets, offset: cfg.offset, unitId: cfg.unitId, pollMs: cfg.pollMs } };
}
function broadcastSnap() { broadcast(snapshot()); }
wss.on('connection', (ws) => {
  ws.send(JSON.stringify(snapshot()));
  ws.send(JSON.stringify({ t: 'hist', items: history.slice(0, 500) }));
  ws.on('message', (raw) => { try { handle(JSON.parse(raw), ws); } catch { /* mensaje inválido */ } });
});

// ------------------------------------------------------------------ Arranque
if (cfg.startVirtualPlc) require('./plc-virtual').start(cfg.virtualPort, { host: '127.0.0.1' });
server.listen(cfg.httpPort, () => {
  console.log(`[SCADA] Gateway listo → http://localhost:${cfg.httpPort}`);
  console.log(`[SCADA] Destino: ${cfg.targets[cfg.target].name} (${cfg.targets[cfg.target].host}:${cfg.targets[cfg.target].port})`);
  setTimeout(loop, 300);
});
