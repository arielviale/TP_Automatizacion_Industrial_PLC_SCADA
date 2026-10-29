/**
 * CLIENTE SCADA — Lógica de Interfaz de Usuario y Comunicación en Tiempo Real
 * -------------------------------------------------------------------------
 * - Conexión WebSocket permanente con auto-reconexión hacia el gateway
 * - Renderizado dinámico del proceso (animaciones de motores, silos, compuertas, flujos)
 * - Control de botones de mando con confirmación y feedback táctil
 * - Gestión de Alarmas ISA-18.2 (Reconocimiento individual o masivo, sonido acústico opcional)
 * - Actualización de curvas y tendencias históricas (Sparkline PDT-01)
 * - Panel interactivo de simulación de campo para pruebas de laboratorio
 */

'use strict';

// ------------------------------------------------------------------ Variables de Estado y Audio
let ws = null;
let lastSnap = null;
let histData = [];
let dpHistory = []; // Para sparkline (últimos 30 puntos)
let selectedTarget = 'virtual';

// Motor de Audio para Bocina Industrial (%Q0.5 / EST_BOCINA)
let audioCtx = null;
let soundEnabled = true;
let hornPlaying = false;
let hornOsc1 = null;
let hornOsc2 = null;
let hornLfo = null;
let hornGain = null;

function initAudio() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
}

// Desbloquear audio en la primera interacción del usuario con cualquier parte de la pantalla
document.addEventListener('pointerdown', initAudio, { once: false });
document.addEventListener('keydown', initAudio, { once: false });

function startHornSound() {
  if (!soundEnabled) return;
  initAudio();
  if (!audioCtx) return;
  if (hornPlaying) return;

  try {
    hornPlaying = true;
    const now = audioCtx.currentTime;

    hornGain = audioCtx.createGain();
    hornGain.gain.setValueAtTime(0.0001, now);
    hornGain.gain.exponentialRampToValueAtTime(0.3, now + 0.04);

    // Filtro pasa bajos a 1500 Hz para darle tono de bocina pesada de fábrica
    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(1500, now);

    // Tono primario: 420 Hz (tono industrial tipo bocina klaxon)
    hornOsc1 = audioCtx.createOscillator();
    hornOsc1.type = 'sawtooth';
    hornOsc1.frequency.setValueAtTime(420, now);

    // Tono armónico: 525 Hz (tercera mayor para sirena industrial clásica)
    hornOsc2 = audioCtx.createOscillator();
    hornOsc2.type = 'sawtooth';
    hornOsc2.frequency.setValueAtTime(525, now);

    // Vibrato electromecánico rápido (24 Hz)
    hornLfo = audioCtx.createOscillator();
    const lfoGain = audioCtx.createGain();
    hornLfo.frequency.setValueAtTime(24, now);
    lfoGain.gain.setValueAtTime(14, now);
    hornLfo.connect(lfoGain);
    lfoGain.connect(hornOsc1.frequency);
    lfoGain.connect(hornOsc2.frequency);

    hornOsc1.connect(filter);
    hornOsc2.connect(filter);
    filter.connect(hornGain);
    hornGain.connect(audioCtx.destination);

    hornOsc1.start(now);
    hornOsc2.start(now);
    hornLfo.start(now);
  } catch (err) {
    console.warn('Audio horn error:', err);
  }
}

function stopHornSound() {
  if (!hornPlaying || !audioCtx) return;
  try {
    const now = audioCtx.currentTime;
    if (hornGain) {
      hornGain.gain.cancelScheduledValues(now);
      hornGain.gain.setValueAtTime(hornGain.gain.value, now);
      hornGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);
    }
    setTimeout(() => {
      try {
        if (hornOsc1) { hornOsc1.stop(); hornOsc1.disconnect(); }
        if (hornOsc2) { hornOsc2.stop(); hornOsc2.disconnect(); }
        if (hornLfo) { hornLfo.stop(); hornLfo.disconnect(); }
      } catch (e) {}
      hornOsc1 = null; hornOsc2 = null; hornLfo = null; hornGain = null;
      hornPlaying = false;
    }, 70);
  } catch (e) {
    hornPlaying = false;
  }
}

function playHornTestBeep(durationMs = 1000) {
  startHornSound();
  setTimeout(() => {
    stopHornSound();
  }, durationMs);
}

// ------------------------------------------------------------------ Inicialización al Cargar DOM
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initTabs();
  initButtons();
  initFieldPanel();
  initModalConn();
  initWebSocket();
});

// ------------------------------------------------------------------ Reloj de Sala de Control
function initClock() {
  const el = document.getElementById('clock-display');
  const update = () => {
    const d = new Date();
    el.textContent = d.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' }) + 
                     ' ' + d.toLocaleTimeString('es-AR', { hour12: false });
  };
  setInterval(update, 1000);
  update();
}

// ------------------------------------------------------------------ Navegación por Pestañas
function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  const views = document.querySelectorAll('.view');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      views.forEach(v => v.classList.remove('active'));
      
      tab.classList.add('active');
      const targetView = document.getElementById(`view-${tab.dataset.view}`);
      if (targetView) targetView.classList.add('active');
    });
  });
}

// ------------------------------------------------------------------ WebSocket & Gateway
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const url = `${protocol}//${window.location.host}`;
  
  ws = new WebSocket(url);

  ws.onopen = () => {
    console.log('[SCADA Client] Conectado al Gateway');
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.t === 'snap') {
        renderSnapshot(data);
      } else if (data.t === 'hist') {
        renderHistory(data.items);
      } else if (data.t === 'toast') {
        showToast(data.text, data.ok ? 'ok' : 'err');
      }
    } catch (e) {
      console.error('Error parseando mensaje:', e);
    }
  };

  ws.onclose = () => {
    document.getElementById('dot-comm').className = 'dot down';
    document.getElementById('txt-conn-target').textContent = 'Gateway Desconectado';
    document.getElementById('stale-overlay').classList.add('show');
    document.getElementById('stale-reason').textContent = 'Conexión con el servidor Gateway perdida. Reconectando...';
    setTimeout(initWebSocket, 2000);
  };
}

function sendMsg(obj) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(obj));
  } else {
    showToast('Sin conexión con el Gateway', 'err');
  }
}

// ------------------------------------------------------------------ Renderizado del Snapshot
function renderSnapshot(snap) {
  lastSnap = snap;
  const { conn, tags, dp, arranques, celda, alarms, sim, cfg } = snap;

  // 1. Estado de Comunicación Superior
  const dotComm = document.getElementById('dot-comm');
  const txtConn = document.getElementById('txt-conn-target');
  const txtLat = document.getElementById('txt-latency');
  const overlay = document.getElementById('stale-overlay');

  if (conn.status === 'ok') {
    dotComm.className = 'dot ok';
    txtConn.textContent = conn.detail;
    txtLat.textContent = `${conn.latency} ms`;
    overlay.classList.remove('show');
  } else if (conn.status === 'stale') {
    dotComm.className = 'dot stale';
    txtConn.textContent = 'PLC en STOP / Señal VIDA ausente';
    txtLat.textContent = `${conn.latency} ms`;
    overlay.classList.add('show');
    document.getElementById('stale-reason').textContent = 'La señal de reloj VIDA (%M10) dejó de alternar. ¿PLC en STOP?';
  } else {
    dotComm.className = 'dot down';
    txtConn.textContent = 'Falla de Enlace PLC';
    txtLat.textContent = '-- ms';
    overlay.classList.add('show');
    document.getElementById('stale-reason').textContent = conn.detail || 'Sin respuesta Modbus';
  }

  // 2. Variables Analógicas e Indicadores
  const txtDp = document.getElementById('txt-dp-pa');
  const svgDp = document.getElementById('svg-dp-val');
  const needle = document.getElementById('needle-dp');
  txtDp.innerHTML = `${dp} <small>Pa</small>`;
  svgDp.textContent = `${dp} Pa`;

  // Color de DP según umbrales de alarma (1500 aviso, 2000 falla)
  if (dp > 2000) {
    txtDp.className = 'v fault';
  } else if (dp > 1500) {
    txtDp.className = 'v warn';
  } else {
    txtDp.className = 'v';
  }

  // Posición aguja (0 - 3000 Pa -> 0% - 100%)
  const needlePct = Math.min(100, Math.max(0, (dp / 3000) * 100));
  needle.style.left = `${needlePct}%`;

  // Actualizar tendencia (Sparkline)
  updateSparkline(dp);

  // Contador de Arranques (%MW1)
  const txtStarts = document.getElementById('txt-starts-val');
  const boxStarts = document.getElementById('box-starts-segments');
  const warnStarts = document.getElementById('txt-starts-warn');
  txtStarts.innerHTML = `${arranques} <small>/ 6 máx</small>`;
  
  const segments = boxStarts.querySelectorAll('i');
  segments.forEach((seg, idx) => {
    seg.className = idx < arranques ? 'on' : '';
  });
  if (arranques >= 6) {
    boxStarts.classList.add('full');
    warnStarts.style.display = 'inline';
  } else {
    boxStarts.classList.remove('full');
    warnStarts.style.display = 'none';
  }

  // 3. Destino Seleccionado (%MW10)
  const txtDestino = document.getElementById('txt-destino');
  const btnC1 = document.getElementById('btn-celda-1');
  const btnC2 = document.getElementById('btn-celda-2');

  btnC1.classList.toggle('selected', celda === 1);
  btnC2.classList.toggle('selected', celda === 2);

  if (celda === 1) {
    txtDestino.className = '';
    txtDestino.textContent = 'Celda 1 Seleccionada';
  } else if (celda === 2) {
    txtDestino.className = '';
    txtDestino.textContent = 'Celda 2 Seleccionada';
  } else {
    txtDestino.className = 'none';
    txtDestino.textContent = 'Sin celda seleccionada (%MW10 = 0)';
  }

  // 4. Lámparas de Estado
  setLamp('led-permiso', 'val-permiso', tags.PERMISO);
  setLamp('led-linea', 'val-linea', tags.LINEA);
  setLamp('led-bocina', 'val-bocina', tags.EST_BOCINA);
  setLamp('led-vida', 'val-vida', tags.VIDA);

  // Reproducción acústica de Bocina Industrial de Pre-arranque (%Q0.5 / EST_BOCINA)
  if (tags.EST_BOCINA) {
    startHornSound();
  } else {
    stopHornSound();
  }

  // Diagnóstico de por qué no hay permiso de marcha
  const whyBox = document.getElementById('box-why-no-permiso');
  const whyList = document.getElementById('list-permiso-reasons');
  if (!tags.PERMISO) {
    const reasons = [];
    if (!tags.CELDA_VALIDA && celda !== 1 && celda !== 2) reasons.push('Falta seleccionar celda de destino (Celda 1 o Celda 2).');
    if (tags.DESTINO_LLENO || (celda === 1 && tags.AV_C1_LLENA) || (celda === 2 && tags.AV_C2_LLENA)) {
      reasons.push('La celda de destino seleccionada se encuentra LLENA (LSH activo).');
    }
    if (tags.FALLA_GRAL) reasons.push('Hay al menos una falla activa no rearmada (requiere RESET).');
    if (tags.AL_EMERG) reasons.push('Parada de emergencia accionada.');
    
    if (reasons.length > 0) {
      whyBox.classList.add('show');
      whyList.innerHTML = reasons.map(r => `<li>${r}</li>`).join('');
    } else {
      whyBox.classList.remove('show');
    }
  } else {
    whyBox.classList.remove('show');
  }

  // Actualizar estado en el mini-mando del Drawer
  const dqPermiso = document.getElementById('dq-permiso');
  const dqLinea = document.getElementById('dq-linea');
  const dqDest = document.getElementById('dq-dest');
  if (dqPermiso) {
    dqPermiso.textContent = tags.PERMISO ? '1' : '0';
    dqPermiso.className = tags.PERMISO ? 'on' : 'off';
  }
  if (dqLinea) {
    dqLinea.textContent = tags.LINEA ? '1' : '0';
    dqLinea.className = tags.LINEA ? 'on' : 'off';
  }
  if (dqDest) {
    dqDest.textContent = celda === 1 ? 'Celda 1' : (celda === 2 ? 'Celda 2' : '--');
  }

  // Alternar modo de visualización del Drawer según tipo de PLC conectado
  const drawerEl = document.getElementById('drawer-field');
  if (drawerEl) {
    drawerEl.classList.toggle('is-virtual', !!conn.virtual);
    drawerEl.classList.toggle('is-m221', !conn.virtual);
  }

  // Diagnóstico en vivo de señales para Machine Expert Basic
  if (!conn.virtual) {
    const setDiag = (id, isNormal, textOk, textFault) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = isNormal ? textOk : textFault;
      el.className = `st ${isNormal ? 'ok' : 'fault'}`;
    };

    setDiag('diag-i0', !tags.AL_EMERG, '1 (OK)', '0 (Emergencia)');
    setDiag('diag-i1', !tags.AL_M1, '1 (OK)', '0 (Disparado)');
    setDiag('diag-i2', !tags.AL_M2, '1 (OK)', '0 (Disparado)');
    setDiag('diag-i3', !tags.AL_M3, '1 (OK)', '0 (Disparado)');
    setDiag('diag-i4', !tags.AL_GIRO, '1 (Giro OK)', '0 (Sin Giro)');
    setDiag('diag-i9', !tags.AL_EMERG && (tags.LINEA || tags.PERMISO), '1 (Reposo)', 'Normal');
  }

  // 5. Animación del Proceso SVG (Motores, Silos, Caída de Grano)
  updateProcessSVG(tags, celda, sim);

  // 6. Barra de Secuencia de Tiempos y Temporizador de Ventana Horaria (%TM8)
  const effectiveTM = getEffectiveTimers(snap);
  updateSequenceBar(tags, effectiveTM);
  const txtHoraTimer = document.getElementById('txt-hora-timer');
  if (txtHoraTimer && effectiveTM) {
    const t8 = Number(effectiveTM[8]) || 0;
    const mins = Math.floor(t8 / 60);
    const secs = t8 % 60;
    txtHoraTimer.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')} (${t8}/3600 s)`;
  }

  // 7. Lista de Alarmas Activas y Badge
  updateActiveAlarms(alarms);

  // 8. Barra Inferior de Última Alarma
  updateAlarmFooter(alarms);

  // 9. Actualizar Panel de Simulación (Monitoreo de timers siempre activo)
  updateFieldPanelUI(sim, effectiveTM);
}

// ------------------------------------------------------------------ Ayudante de Lámparas
function setLamp(ledId, valId, val) {
  const led = document.getElementById(ledId);
  const v = document.getElementById(valId);
  if (led) led.classList.toggle('on', !!val);
  if (v) v.textContent = val ? '1' : '0';
}

// ------------------------------------------------------------------ SVG y Animaciones
function updateProcessSVG(tags, celda, sim) {
  // Motores M1, M2, M3
  setMotorState('grp-m1', tags.EST_M1, tags.AL_M1);
  setMotorState('grp-m2', tags.EST_M2, tags.AL_M2);
  setMotorState('grp-m3', tags.EST_M3, tags.AL_M3 || tags.AL_GIRO);

  // Flujo en conductos de aspiración y carcasa de M1
  const grpDucts = document.getElementById('grp-ducts');
  if (grpDucts) grpDucts.classList.toggle('running', !!tags.EST_M1);
  const grpM1Struct = document.getElementById('grp-m1-struct');
  if (grpM1Struct) grpM1Struct.classList.toggle('running', !!tags.EST_M1);

  // Elevador M3 Cangilones
  document.getElementById('grp-m3-struct').classList.toggle('running', !!tags.EST_M3);

  // Redler M2 Cadena
  document.getElementById('grp-m2-struct').classList.toggle('running', !!tags.EST_M2);

  // Sensor SSL Giro en pie de elevador
  const ledSsl = document.getElementById('led-ssl');
  if (ledSsl) {
    const sslOk = sim ? !!sim.I[4] : (!!tags.EST_M3 && !tags.AL_GIRO);
    ledSsl.style.fill = sslOk ? 'var(--run)' : '#303f50';
  }

  // Compuertas YV1 y YV2
  const grpYv1 = document.getElementById('grp-yv1');
  const grpYv2 = document.getElementById('grp-yv2');
  grpYv1.classList.toggle('open', !!tags.EST_YV1);
  grpYv2.classList.toggle('open', !!tags.EST_YV2);

  // Caída de grano hacia celdas (Requiere M3, M2 y Compuerta)
  const grainFlowing = tags.EST_M3 && tags.EST_M2;
  grpYv1.classList.toggle('flowing', grainFlowing && !!tags.EST_YV1);
  grpYv2.classList.toggle('flowing', grainFlowing && !!tags.EST_YV2);

  // Niveles en Silos
  const lvl1 = sim ? sim.level[0] : (tags.AV_C1_LLENA ? 100 : 35);
  const lvl2 = sim ? sim.level[1] : (tags.AV_C2_LLENA ? 100 : 10);
  
  setLevelSilo('grain-level-1', 'txt-level-pct-1', lvl1);
  setLevelSilo('grain-level-2', 'txt-level-pct-2', lvl2);

  // Sensores de nivel alto LSH
  document.getElementById('grp-lsh1').classList.toggle('on', !!tags.AV_C1_LLENA);
  document.getElementById('grp-lsh2').classList.toggle('on', !!tags.AV_C2_LLENA);

  // Bocina, Baliza y Piloto Local
  document.getElementById('svg-horn').classList.toggle('on', !!tags.EST_BOCINA);

  const beacon = document.getElementById('svg-beacon');
  const beaconOn = tags.FALLA_GRAL ? (tags.VIDA) : (tags.AV_DP_ALTA || tags.AV_C1_LLENA || tags.AV_C2_LLENA || tags.AV_ARRANQUES);
  beacon.classList.toggle('on', !!beaconOn);
  beacon.classList.toggle('steady', !tags.FALLA_GRAL);

  const pilot = document.getElementById('svg-pilot');
  const pilotOn = tags.LINEA && (tags.EST_M3 || tags.VIDA);
  pilot.classList.toggle('on', !!pilotOn);
}

function setMotorState(grpId, isRunning, isFault) {
  const grp = document.getElementById(grpId);
  if (!grp) return;
  grp.classList.remove('run', 'fault', 'running');
  if (isFault) {
    grp.classList.add('fault');
  } else if (isRunning) {
    grp.classList.add('run', 'running');
  }
}

function setLevelSilo(rectId, textId, pct) {
  const r = document.getElementById(rectId);
  const t = document.getElementById(textId);
  if (r) {
    const val = Math.max(0, Math.min(100, Number(pct) || 0));
    const h = (val / 100) * 209;
    const y = 225 - h;
    r.setAttribute('y', y);
    r.setAttribute('height', h + 10);
  }
  if (t) t.textContent = `${Math.round(pct)} %`;
}

// ------------------------------------------------------------------ Motor de Temporizadores (Telemetría de CPU)
const timerTracker = {
  starts: [null, null, null, null, null, null, null, null, null],
  values: [0, 0, 0, 0, 0, 0, 0, 0, 0],
};

function getEffectiveTimers(snap) {
  if (snap.sim && snap.sim.TM) return snap.sim.TM;

  const tags = snap.tags || {};
  const dp = snap.dp || 0;
  const now = Date.now();
  const presets = [5, 5, 5, 20, 30, 5, 10, 10, 3600];
  const activeConditions = [
    !!tags.EST_BOCINA,                                          // %TM0 Bocina
    !!(tags.LINEA && tags.EST_M1 && !tags.EST_M2),              // %TM1 Arr M2
    !!(tags.LINEA && tags.EST_M2 && !tags.EST_M3),              // %TM2 Arr M3
    !!(!tags.LINEA && tags.EST_M2),                             // %TM3 Vaciado M2 (20s)
    !!(!tags.LINEA && !tags.EST_M2 && tags.EST_M1),            // %TM4 Barrido M1 (30s)
    false,                                                      // %TM5 Giro M3 (en M221 solo discurre ante falla de giro)
    !!(dp > 1500 && !tags.AV_DP_ALTA),                          // %TM6 DP Alta
    !!(dp > 2000 && !tags.AL_DP_MUY_ALTA),                      // %TM7 DP Muy Alta
    !!(snap.conn && snap.conn.status === 'up')                  // %TM8 Hora (ciclo continuo de 3600s con PLC en RUN)
  ];

  for (let i = 0; i < 9; i++) {
    if (activeConditions[i]) {
      if (!timerTracker.starts[i]) timerTracker.starts[i] = now;
      const elapsed = Math.floor((now - timerTracker.starts[i]) / 1000);
      timerTracker.values[i] = i === 8 ? (elapsed % presets[i]) : Math.min(presets[i], elapsed);
    } else {
      timerTracker.starts[i] = null;
      timerTracker.values[i] = 0;
    }
  }
  return timerTracker.values;
}

// ------------------------------------------------------------------ Secuencia de Tiempos
function updateSequenceBar(tags, tm) {
  const sBocina = document.getElementById('seq-bocina');
  const sM1 = document.getElementById('seq-m1');
  const sM2 = document.getElementById('seq-m2');
  const sM3 = document.getElementById('seq-m3');
  const sParada = document.getElementById('seq-parada');

  const tBoc = (tm && tm[0]) || 0;
  const tM2 = (tm && tm[1]) || 0;
  const tM3 = (tm && tm[2]) || 0;
  const tVac = (tm && tm[3]) || 0;
  const tBar = (tm && tm[4]) || 0;

  // Paso 1: Bocina
  if (tags.EST_BOCINA) {
    sBocina.className = 'seq-step now';
    sBocina.querySelector('i').style.width = `${(tBoc / 5) * 100}%`;
    document.getElementById('seq-t-bocina').textContent = `${tBoc}/5 s`;
  } else if (tags.EST_M1 || tags.EST_M2 || tags.EST_M3) {
    sBocina.className = 'seq-step done';
    sBocina.querySelector('i').style.width = '100%';
    document.getElementById('seq-t-bocina').textContent = 'Listo (5 s)';
  } else {
    sBocina.className = 'seq-step';
    sBocina.querySelector('i').style.width = '0%';
    document.getElementById('seq-t-bocina').textContent = '--/5 s';
  }

  // Paso 2: Aspiración M1
  if (tags.EST_M1 && !tags.EST_M2 && tags.LINEA) {
    sM1.className = 'seq-step now';
    sM1.querySelector('i').style.width = `${(tM2 / 5) * 100}%`;
    document.getElementById('seq-t-m1').textContent = `${tM2}/5 s`;
  } else if (tags.EST_M2 || tags.EST_M3) {
    sM1.className = 'seq-step done';
    sM1.querySelector('i').style.width = '100%';
    document.getElementById('seq-t-m1').textContent = 'Listo';
  } else {
    sM1.className = 'seq-step';
    sM1.querySelector('i').style.width = '0%';
    document.getElementById('seq-t-m1').textContent = '--/5 s';
  }

  // Paso 3: Redler M2
  if (tags.EST_M2 && !tags.EST_M3 && tags.LINEA) {
    sM2.className = 'seq-step now';
    sM2.querySelector('i').style.width = `${(tM3 / 5) * 100}%`;
    document.getElementById('seq-t-m2').textContent = `${tM3}/5 s`;
  } else if (tags.EST_M3) {
    sM2.className = 'seq-step done';
    sM2.querySelector('i').style.width = '100%';
    document.getElementById('seq-t-m2').textContent = 'Listo';
  } else {
    sM2.className = 'seq-step';
    sM2.querySelector('i').style.width = '0%';
    document.getElementById('seq-t-m2').textContent = '--/5 s';
  }

  // Paso 4: Elevador M3
  if (tags.EST_M3) {
    sM3.className = 'seq-step done';
    sM3.querySelector('i').style.width = '100%';
    document.getElementById('seq-t-m3').textContent = 'En Régimen';
  } else {
    sM3.className = 'seq-step';
    sM3.querySelector('i').style.width = '0%';
    document.getElementById('seq-t-m3').textContent = 'Detenido';
  }

  // Secuencia de Parada (Vaciado redler 20s y Barrido aspiración 30s)
  if (!tags.LINEA && (tags.EST_M1 || tags.EST_M2)) {
    sParada.className = 'seq-step stop now';
    if (tags.EST_M2) {
      sParada.querySelector('i').style.width = `${(tVac / 20) * 100}%`;
      document.getElementById('seq-t-stop').textContent = `Vaciado M2: ${20 - tVac} s`;
    } else {
      sParada.querySelector('i').style.width = `${(tBar / 30) * 100}%`;
      document.getElementById('seq-t-stop').textContent = `Barrido M1: ${30 - tBar} s`;
    }
  } else {
    sParada.className = 'seq-step';
    sParada.querySelector('i').style.width = '0%';
    document.getElementById('seq-t-stop').textContent = '--';
  }
}

// ------------------------------------------------------------------ Gráfico Sparkline DP
function updateSparkline(val) {
  dpHistory.push(val);
  if (dpHistory.length > 30) dpHistory.shift();

  const svg = document.getElementById('spark-dp');
  if (!svg || dpHistory.length < 2) return;

  const maxVal = 3000;
  const h = 35;
  const w = 100;
  const step = w / (dpHistory.length - 1);

  let d = '';
  dpHistory.forEach((v, i) => {
    const x = i * step;
    const y = h - (Math.min(maxVal, Math.max(0, v)) / maxVal) * (h - 4) - 2;
    d += (i === 0 ? `M ${x},${y}` : ` L ${x},${y}`);
  });

  const path = svg.querySelector('path');
  if (path) path.setAttribute('d', d);
}

// ------------------------------------------------------------------ Botones de Mando
function initButtons() {
  const btnMarcha = document.getElementById('btn-marcha');
  const btnParada = document.getElementById('btn-parada');
  const btnReset = document.getElementById('btn-reset');
  const btnC1 = document.getElementById('btn-celda-1');
  const btnC2 = document.getElementById('btn-celda-2');

  btnMarcha.addEventListener('click', (e) => {
    createRipple(e, btnMarcha);
    sendMsg({ t: 'cmd', name: 'CMD_MARCHA' });
  });

  btnParada.addEventListener('click', (e) => {
    createRipple(e, btnParada);
    sendMsg({ t: 'cmd', name: 'CMD_PARADA' });
  });

  btnReset.addEventListener('click', (e) => {
    createRipple(e, btnReset);
    sendMsg({ t: 'cmd', name: 'CMD_RESET' });
  });

  btnC1.addEventListener('click', () => sendMsg({ t: 'celda', value: 1 }));
  btnC2.addEventListener('click', () => sendMsg({ t: 'celda', value: 2 }));

  document.getElementById('btn-ack-all').addEventListener('click', () => {
    sendMsg({ t: 'ack', id: 'all' });
  });

  // Botón de alternar audio de bocina en barra superior
  const btnToggleSound = document.getElementById('btn-toggle-sound');
  if (btnToggleSound) {
    btnToggleSound.addEventListener('click', () => {
      initAudio();
      soundEnabled = !soundEnabled;
      const ico = document.getElementById('ico-sound');
      const txt = document.getElementById('txt-sound');
      if (ico) ico.textContent = soundEnabled ? '🔊' : '🔇';
      if (txt) txt.textContent = soundEnabled ? 'Bocina: ON' : 'Bocina: MUTE';
      showToast(soundEnabled ? 'Sonido de bocina activado' : 'Bocina silenciada', 'ok');
      if (soundEnabled) playHornTestBeep(350);
    });
  }

  // Clic directo en bocina de planta para prueba de audio manual
  const svgHorn = document.getElementById('svg-horn');
  if (svgHorn) {
    svgHorn.addEventListener('click', () => {
      initAudio();
      if (!soundEnabled) {
        soundEnabled = true;
        const ico = document.getElementById('ico-sound');
        const txt = document.getElementById('txt-sound');
        if (ico) ico.textContent = '🔊';
        if (txt) txt.textContent = 'Bocina: ON';
      }
      playHornTestBeep(1200);
      showToast('Prueba de audio: Bocina de pre-arranque %Q0.5', 'ok');
    });
  }
}

function createRipple(e, btn) {
  const circle = document.createElement('span');
  const diameter = Math.max(btn.clientWidth, btn.clientHeight);
  const radius = diameter / 2;
  const rect = btn.getBoundingClientRect();

  circle.style.width = circle.style.height = `${diameter}px`;
  circle.style.left = `${e.clientX - rect.left - radius}px`;
  circle.style.top = `${e.clientY - rect.top - radius}px`;
  circle.classList.add('ripple');

  const existing = btn.querySelector('.ripple');
  if (existing) existing.remove();
  btn.appendChild(circle);
}

// ------------------------------------------------------------------ Alarmas y Notificaciones
function updateActiveAlarms(alarms) {
  const tbody = document.getElementById('tbody-active-alarms');
  const badge = document.getElementById('badge-alarmas');

  const unackCount = alarms.filter(a => a.st === 'ACT_NO_RECON' || a.st === 'NORM_NO_RECON').length;
  if (unackCount > 0) {
    badge.textContent = unackCount;
    badge.hidden = false;
  } else {
    badge.hidden = true;
  }

  if (alarms.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">No hay alarmas activas en la planta</td></tr>';
    return;
  }

  tbody.innerHTML = alarms.map(a => {
    const timeStr = a.tOn ? new Date(a.tOn).toLocaleTimeString('es-AR') : '--:--';
    const rowClass = a.prio.toLowerCase() + ' ' + a.st;
    
    let stText = 'Activa';
    if (a.st === 'ACT_NO_RECON') stText = 'ACTIVA (SIN ACK)';
    else if (a.st === 'ACT_RECON') stText = 'Activa (Reconocida)';
    else if (a.st === 'NORM_NO_RECON') stText = 'Normalizada (Sin ACK)';

    return `
      <tr class="${rowClass}">
        <td><span class="prio ${a.prio}">${a.prio}</span></td>
        <td class="mono">${a.id}</td>
        <td>${a.text}</td>
        <td class="mono">${timeStr}</td>
        <td><span class="chip ${a.st}">${stText}</span></td>
        <td style="text-align: center;">
          ${!a.acked ? `<button class="btn-s" onclick="ackAlarm('${a.id}')">ACK</button>` : '—'}
        </td>
      </tr>
    `;
  }).join('');
}

window.ackAlarm = function(id) {
  sendMsg({ t: 'ack', id });
};

function updateAlarmFooter(alarms) {
  const footer = document.getElementById('alarmbar-footer');
  const msgBox = document.getElementById('alarmbar-msg');

  if (alarms.length === 0) {
    footer.className = 'alarmbar';
    msgBox.innerHTML = '<span class="txt">(sin alarmas activas)</span>';
    return;
  }

  const highest = alarms[0];
  const isHigh = highest.prio === 'Alta';
  footer.className = `alarmbar ${isHigh ? 'alta' : 'baja'} ${!highest.acked ? 'unack' : ''}`;
  
  const timeStr = new Date(highest.tOn).toLocaleTimeString('es-AR');
  msgBox.innerHTML = `
    <span class="chip ${highest.prio === 'Alta' ? 'ACTIVA' : 'chip-warn'}">${highest.prio.toUpperCase()}</span>
    <span class="txt"><b>[${highest.id}]</b> ${highest.text} — (${timeStr})</span>
  `;
}

// ------------------------------------------------------------------ Historial
function renderHistory(items) {
  histData = items;
  applyHistFilter();
}

function applyHistFilter() {
  const tbody = document.getElementById('tbody-hist-events');
  const filter = document.querySelector('#seg-hist-filter button.active').dataset.filter;
  const query = document.getElementById('input-search-hist').value.toLowerCase();

  const filtered = histData.filter(item => {
    if (filter !== 'all' && item.kind !== filter) return false;
    if (query) {
      const match = (item.text + ' ' + item.id + ' ' + item.detail).toLowerCase();
      if (!match.includes(query)) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">No se encontraron registros</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.slice(0, 150).map(item => {
    const d = new Date(item.t);
    const dateStr = d.toLocaleDateString('es-AR') + ' ' + d.toLocaleTimeString('es-AR');
    let chipKind = item.kind;
    if (item.detail === 'ACTIVA') chipKind = 'ACTIVA';
    else if (item.detail === 'NORMALIZADA') chipKind = 'NORMALIZADA';
    else if (item.detail && item.detail.startsWith('RECONOCIDA')) chipKind = 'RECONOCIDA';
    else chipKind = 'ev';

    return `
      <tr>
        <td class="mono">${dateStr}</td>
        <td><span class="chip ${item.kind === 'alarma' ? 'ACT_RECON' : 'ev'}">${item.kind.toUpperCase()}</span></td>
        <td class="mono">${item.id}</td>
        <td>${item.text}</td>
        <td>${item.prio ? `<span class="prio ${item.prio}">${item.prio}</span>` : '—'}</td>
        <td><span class="chip ${chipKind}">${item.detail || item.kind}</span></td>
      </tr>
    `;
  }).join('');
}

// ------------------------------------------------------------------ Panel de Campo (Drawer)
function initFieldPanel() {
  const drawer = document.getElementById('drawer-field');
  const btnToggle = document.getElementById('btn-toggle-field');
  const btnClose = document.getElementById('btn-close-field');

  btnToggle.addEventListener('click', () => {
    drawer.classList.toggle('open');
    document.body.classList.toggle('drawer-open', drawer.classList.contains('open'));
  });
  btnClose.addEventListener('click', () => {
    drawer.classList.remove('open');
    document.body.classList.remove('drawer-open');
  });

  // Comandos rápidos integrados en el Drawer
  const dqMarcha = document.getElementById('dq-btn-marcha');
  const dqParada = document.getElementById('dq-btn-parada');
  const dqReset = document.getElementById('dq-btn-reset');
  const dqC1 = document.getElementById('dq-btn-c1');
  const dqC2 = document.getElementById('dq-btn-c2');

  if (dqMarcha) dqMarcha.addEventListener('click', () => sendMsg({ t: 'cmd', name: 'CMD_MARCHA' }));
  if (dqParada) dqParada.addEventListener('click', () => sendMsg({ t: 'cmd', name: 'CMD_PARADA' }));
  if (dqReset) dqReset.addEventListener('click', () => sendMsg({ t: 'cmd', name: 'CMD_RESET' }));
  if (dqC1) dqC1.addEventListener('click', () => sendMsg({ t: 'celda', value: 1 }));
  if (dqC2) dqC2.addEventListener('click', () => sendMsg({ t: 'celda', value: 2 }));

  const isVirtual = () => lastSnap && lastSnap.conn && lastSnap.conn.virtual;

  // Switches Entradas Digitales %I0.x
  document.querySelectorAll('[data-toggle]').forEach(sw => {
    sw.addEventListener('click', () => {
      if (!isVirtual()) return;
      const n = parseInt(sw.dataset.toggle);
      const isCurrentlyOn = sw.classList.contains('on');
      sendMsg({ t: 'sim', kind: 'I', n, value: !isCurrentlyOn });
    });
  });

  // Pulsadores NA
  document.querySelectorAll('[data-pulse]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!isVirtual()) return;
      const n = parseInt(btn.dataset.pulse);
      sendMsg({ t: 'sim', kind: 'pulse', n });
    });
  });

  // Slider PDT-01 (%IW0.0)
  const rngIw = document.getElementById('rng-field-iw0');
  rngIw.addEventListener('input', (e) => {
    if (!isVirtual()) return;
    const val = parseInt(e.target.value);
    sendMsg({ t: 'sim', kind: 'IW0', value: val });
  });

  document.querySelectorAll('[data-set-iw]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!isVirtual()) return;
      const val = parseInt(btn.dataset.setIw);
      rngIw.value = val;
      sendMsg({ t: 'sim', kind: 'IW0', value: val });
    });
  });

  // Slider Niveles Silo Manuales
  const rngL1 = document.getElementById('rng-sim-lvl-1');
  const rngL2 = document.getElementById('rng-sim-lvl-2');
  rngL1.addEventListener('input', (e) => {
    if (!isVirtual()) return;
    sendMsg({ t: 'sim', kind: 'level', n: 0, value: parseFloat(e.target.value) });
  });
  rngL2.addEventListener('input', (e) => {
    if (!isVirtual()) return;
    sendMsg({ t: 'sim', kind: 'level', n: 1, value: parseFloat(e.target.value) });
  });

  // Auto Simulación Planta & Fallo de Giro
  const swAuto = document.getElementById('sw-plant-auto');
  const swGiro = document.getElementById('sw-giro-fail');
  swAuto.addEventListener('click', () => {
    if (!isVirtual()) return;
    sendMsg({ t: 'sim', kind: 'plantAuto', value: !swAuto.classList.contains('on') });
  });
  swGiro.addEventListener('click', () => {
    if (!isVirtual()) return;
    sendMsg({ t: 'sim', kind: 'giroFail', value: !swGiro.classList.contains('on') });
  });

  // Filtros Historial
  document.querySelectorAll('#seg-hist-filter button').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('#seg-hist-filter button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      applyHistFilter();
    });
  });
  document.getElementById('input-search-hist').addEventListener('input', applyHistFilter);
  document.getElementById('btn-clear-hist').addEventListener('click', () => {
    if (confirm('¿Vaciar historial de eventos?')) sendMsg({ t: 'clearHist' });
  });
}

function updateFieldPanelUI(sim, effectiveTM) {
  if (sim) {
    // Sincronizar switches con el estado real del PLC
    if (sim.I) {
      sim.I.forEach((val, n) => {
        const sw = document.querySelector(`[data-toggle="${n}"]`);
        if (sw) sw.classList.toggle('on', !!val);
      });
    }

    // Valor PDT-01
    const lblIw = document.getElementById('lbl-field-iw0');
    const lblDp = document.getElementById('lbl-field-dp');
    const rngIw = document.getElementById('rng-field-iw0');
    if (lblIw && !document.activeElement.isSameNode(rngIw) && sim.IW0 !== undefined) {
      rngIw.value = sim.IW0;
      lblIw.textContent = `${sim.IW0} pts (${(sim.IW0 * 0.01).toFixed(1)} V)`;
      lblDp.textContent = `${sim.IW0 * 3} Pa`;
    }

    // Auto Planta & Giro
    if (sim.plantAuto !== undefined) document.getElementById('sw-plant-auto').classList.toggle('on', !!sim.plantAuto);
    if (sim.giroFail !== undefined) document.getElementById('sw-giro-fail').classList.toggle('on', !!sim.giroFail);

    // Niveles Silo
    if (sim.level) {
      document.getElementById('lbl-level-sim-1').textContent = `${Math.round(sim.level[0])}%`;
      document.getElementById('lbl-level-sim-2').textContent = `${Math.round(sim.level[1])}%`;
    }
  }

  // Monitores Timers (SIEMPRE se actualizan en vivo tanto con Machine Expert como con PLC virtual)
  const tm = (sim && sim.TM) ? sim.TM : effectiveTM;
  const presets = [5, 5, 5, 20, 30, 5, 10, 10, 3600];
  if (tm) {
    tm.forEach((v, idx) => {
      const el = document.getElementById(`val-mon-tm${idx}`);
      if (el) el.textContent = idx === 8 ? `${v}s` : `${v}/${presets[idx]}s`;
      const box = document.getElementById(`mon-tm${idx}`);
      if (box) box.classList.toggle('active', v > 0);
    });
  }
}

// ------------------------------------------------------------------ Modal de Configuración
function initModalConn() {
  const modal = document.getElementById('modal-conn');
  const btnOpen = document.getElementById('btn-conn-info');
  const btnClose = document.getElementById('btn-cancel-conn');
  const btnSave = document.getElementById('btn-save-conn');

  const optVirt = document.getElementById('opt-virtual');
  const optMach = document.getElementById('opt-machine');

  btnOpen.addEventListener('click', () => {
    if (lastSnap && lastSnap.cfg) {
      selectedTarget = lastSnap.cfg.target;
      updateTargetSelection();
      document.getElementById('cfg-host').value = lastSnap.cfg.targets.machine.host;
      document.getElementById('cfg-port').value = lastSnap.cfg.targets.machine.port;
      document.getElementById('cfg-offset').value = lastSnap.cfg.offset;
      document.getElementById('cfg-unit').value = lastSnap.cfg.unitId;
    }
    modal.classList.add('show');
  });

  btnClose.addEventListener('click', () => modal.classList.remove('show'));

  optVirt.addEventListener('click', () => { selectedTarget = 'virtual'; updateTargetSelection(); });
  optMach.addEventListener('click', () => { selectedTarget = 'machine'; updateTargetSelection(); });

  function updateTargetSelection() {
    optVirt.classList.toggle('sel', selectedTarget === 'virtual');
    optMach.classList.toggle('sel', selectedTarget === 'machine');
  }

  btnSave.addEventListener('click', () => {
    const host = document.getElementById('cfg-host').value.trim();
    const port = parseInt(document.getElementById('cfg-port').value);
    const offset = parseInt(document.getElementById('cfg-offset').value);
    const unitId = parseInt(document.getElementById('cfg-unit').value);

    sendMsg({
      t: 'config',
      target: selectedTarget,
      machine: { host, port },
      offset,
      unitId
    });

    modal.classList.remove('show');
    showToast('Configuración enviada al Gateway', 'ok');
  });
}

// ------------------------------------------------------------------ Notificaciones Toast
let lastToastText = '';
let lastToastTime = 0;

function showToast(text, type = 'ok') {
  const now = Date.now();
  if (text === lastToastText && now - lastToastTime < 2500) {
    return; // Evitar apilar múltiples toasts idénticos
  }
  lastToastText = text;
  lastToastTime = now;

  const c = document.getElementById('toasts-container');
  if (!c) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = text;
  c.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transition = 'opacity 0.3s';
    setTimeout(() => t.remove(), 300);
  }, 3200);
}
