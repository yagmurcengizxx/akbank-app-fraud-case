const $ = (id) => document.getElementById(id);
const state = { mode: "LIVE_MICROPHONE", session: null, token: null, audioWs: null, eventWs: null, stream: null, context: null, node: null, syntheticTimer: null, logs: [], connectedAt: null, lastPackets: 0, lastRateAt: performance.now(), shouldReconnect: false, reconnectAttempts: 0 };

function apiHeaders(admin = false) {
  const headers = { "Content-Type": "application/json" };
  if (admin) headers["X-Admin-Key"] = $("adminKey").value;
  else if (state.token) headers.Authorization = `Bearer ${state.token}`;
  return headers;
}
function wsUrl(path) { return `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}${path}`; }
function setError(message = "") { $("error").textContent = message; }
function formatDuration(seconds) { const s = Math.max(0, Math.floor(seconds || 0)); return `${String(Math.floor(s / 60)).padStart(2,"0")}:${String(s % 60).padStart(2,"0")}`; }
function formatBytes(value) { if (value < 1024) return `${value} B`; if (value < 1048576) return `${(value / 1024).toFixed(1)} KiB`; return `${(value / 1048576).toFixed(1)} MiB`; }
function safeDate(value) { return value ? new Date(value).toLocaleTimeString() : "—"; }

function renderSession(session) {
  if (!session) return;
  const now = performance.now();
  const delta = Math.max(.001, (now - state.lastRateAt) / 1000);
  const rate = Math.max(0, (session.packetsReceived - state.lastPackets) / delta);
  state.lastPackets = session.packetsReceived; state.lastRateAt = now; state.session = session;
  $("sessionId").textContent = session.sessionId;
  $("sessionStatus").textContent = session.status;
  $("duration").textContent = formatDuration(session.durationSeconds);
  $("packets").textContent = session.packetsReceived.toLocaleString();
  $("bytes").textContent = formatBytes(session.audioBytesReceived);
  $("rms").textContent = session.currentRms.toFixed(4);
  $("peak").textContent = session.peakAmplitude.toFixed(4);
  $("activity").textContent = session.audioActivityCount;
  $("lastPacket").textContent = safeDate(session.lastPacketAt);
  $("rate").textContent = `${rate.toFixed(1)}/s`;
  const level = Math.min(100, Math.max(0, session.currentRms * 260));
  $("meterFill").style.width = `${level}%`; $("level").textContent = `${Math.round(level)}%`;
  $("stopSession").disabled = session.status !== "ACTIVE";
  $("connect").disabled = session.status !== "ACTIVE" || Boolean(state.audioWs);
}

function renderLogs() {
  const host = $("logs"); host.replaceChildren();
  if (!state.logs.length) { const p = document.createElement("p"); p.className = "empty"; p.textContent = "No events yet"; host.append(p); return; }
  for (const event of state.logs.slice(-250)) {
    const row = document.createElement("div"); row.className = "log-row";
    const time = document.createElement("time"); time.textContent = safeDate(event.timestamp);
    const type = document.createElement("strong"); type.textContent = event.type;
    const data = document.createElement("span"); data.textContent = Object.keys(event.data || {}).length ? JSON.stringify(event.data) : "—";
    row.append(time, type, data); host.append(row);
  }
  host.scrollTop = host.scrollHeight;
}

async function refreshSession() {
  if (!state.session || !state.token) return;
  try { const response = await fetch(`/listener/api/sessions/${state.session.sessionId}`, { headers: apiHeaders() }); if (response.ok) renderSession(await response.json()); } catch (_) {}
}

function openEventSocket() {
  if (state.eventWs) state.eventWs.close();
  const ws = new WebSocket(wsUrl(`/listener/ws/events/${state.session.sessionId}?token=${encodeURIComponent(state.token)}`));
  state.eventWs = ws;
  ws.onmessage = ({ data }) => {
    const message = JSON.parse(data); renderSession(message.session);
    if (message.event.type === "SNAPSHOT") state.logs = message.event.data.events || [];
    else state.logs.push(message.event);
    renderLogs();
  };
  ws.onerror = () => setError("Event channel could not connect. Check HTTPS/origin settings.");
}

async function createSession() {
  setError();
  if (!$("consent").checked) { setError("Participant notice and consent confirmation is required."); return; }
  const response = await fetch("/listener/api/sessions", { method: "POST", headers: apiHeaders(true), body: JSON.stringify({ phoneNumber: $("phone").value, riskLabel: $("risk").checked ? "RISKY" : "UNMARKED", mode: state.mode }) });
  const body = await response.json();
  if (!response.ok) { setError(body.detail || "Session could not be created."); return; }
  state.token = body.sessionToken; delete body.sessionToken; state.logs = []; state.lastPackets = 0;
  renderSession(body); openEventSocket(); $("connect").disabled = false;
}

async function listMicrophones() {
  const devices = await navigator.mediaDevices.enumerateDevices(); const select = $("microphones"); select.replaceChildren();
  devices.filter(d => d.kind === "audioinput").forEach((d, i) => { const option = document.createElement("option"); option.value = d.deviceId; option.textContent = d.label || `Microphone ${i + 1}`; select.append(option); });
}

function openAudioSocket(onOpen) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl(`/listener/ws/audio/${state.session.sessionId}?token=${encodeURIComponent(state.token)}`)); ws.binaryType = "arraybuffer"; state.audioWs = ws;
    ws.onopen = () => { $("socketStatus").textContent = "CONNECTED"; state.connectedAt = Date.now(); $("disconnect").disabled = false; $("connect").disabled = true; if (onOpen) onOpen(ws); resolve(ws); };
    ws.onerror = () => reject(new Error("Audio WebSocket connection failed"));
    ws.onclose = (event) => {
      if (state.audioWs === ws) state.audioWs = null; $("socketStatus").textContent = "DISCONNECTED"; $("disconnect").disabled = true; stopSynthetic();
      if (event.code !== 1000 && state.shouldReconnect && state.session?.status === "ACTIVE" && state.reconnectAttempts < 2) {
        state.reconnectAttempts += 1; $("socketStatus").textContent = `RETRY ${state.reconnectAttempts}/2`;
        setTimeout(() => openAudioSocket().catch(error => setError(error.message)), state.reconnectAttempts * 1000);
      } else if (state.session?.status === "ACTIVE") $("connect").disabled = false;
    };
  });
}

async function connect() {
  setError(); state.shouldReconnect = true; state.reconnectAttempts = 0;
  try {
    if (state.mode === "SYNTHETIC_TEST") { $("permission").textContent = "NOT USED"; await openAudioSocket(); return; }
    if (!window.isSecureContext) throw new Error("Microphone requires localhost or a valid HTTPS origin.");
    const constraints = { audio: { channelCount: 1, echoCancellation: false, noiseSuppression: false, autoGainControl: false } };
    if ($("microphones").value) constraints.audio.deviceId = { exact: $("microphones").value };
    const stream = await navigator.mediaDevices.getUserMedia(constraints); state.stream = stream; $("permission").textContent = "GRANTED"; await listMicrophones();
    const context = new AudioContext(); state.context = context; await context.audioWorklet.addModule("/static/audio-worklet.js");
    const source = context.createMediaStreamSource(stream); const node = new AudioWorkletNode(context, "pcm16-encoder", { processorOptions: { targetSampleRate: 16000, frameSize: 320 } }); state.node = node;
    node.port.onmessage = ({ data }) => { if (state.audioWs?.readyState === WebSocket.OPEN) state.audioWs.send(data); };
    source.connect(node); await openAudioSocket();
  } catch (error) { $("permission").textContent = error.name === "NotAllowedError" ? "DENIED" : $("permission").textContent; setError(error.message); await disconnect(false); }
}

function stopSynthetic() { if (state.syntheticTimer) clearInterval(state.syntheticTimer); state.syntheticTimer = null; }
async function disconnect(closeSocket = true) {
  state.shouldReconnect = false; stopSynthetic(); if (closeSocket && state.audioWs) state.audioWs.close(1000, "operator disconnect"); state.audioWs = null;
  if (state.node) { state.node.disconnect(); state.node = null; } if (state.context) { await state.context.close(); state.context = null; }
  if (state.stream) { state.stream.getTracks().forEach(track => track.stop()); state.stream = null; }
  $("socketStatus").textContent = "DISCONNECTED"; $("disconnect").disabled = true; if (state.session?.status === "ACTIVE") $("connect").disabled = false;
}

function sendSynthetic(kind) {
  if (!state.audioWs || state.audioWs.readyState !== WebSocket.OPEN) { setError("Connect the synthetic stream first."); return; }
  stopSynthetic(); let frameIndex = 0; const sampleRate = 16000, size = 320;
  state.syntheticTimer = setInterval(() => {
    if (!state.audioWs || state.audioWs.readyState !== WebSocket.OPEN) return stopSynthetic();
    const pcm = new Int16Array(size);
    for (let i = 0; i < size; i += 1) { const t = (frameIndex * size + i) / sampleRate; let amplitude = 0; if (kind === "tone") amplitude = .35; if (kind === "sweep") amplitude = .04 + .5 * ((Math.sin(t * 2) + 1) / 2); pcm[i] = Math.sin(2 * Math.PI * 440 * t) * amplitude * 32767; }
    state.audioWs.send(pcm.buffer); frameIndex += 1;
    if (frameIndex >= (kind === "silence" ? 75 : 150)) stopSynthetic();
  }, 20);
}

async function stopSession() {
  if (!state.session) return; await disconnect();
  const response = await fetch(`/listener/api/sessions/${state.session.sessionId}/stop`, { method: "POST", headers: apiHeaders() }); if (response.ok) renderSession(await response.json());
}
async function setMode(mode) { if (state.session?.status === "ACTIVE") { setError("Stop the active session before changing mode."); return; } state.mode = mode; document.querySelectorAll(".mode").forEach(b => b.classList.toggle("active", b.dataset.mode === mode)); const synthetic = mode === "SYNTHETIC_TEST"; $("syntheticBanner").classList.toggle("hidden", !synthetic); $("syntheticControls").classList.toggle("hidden", !synthetic); $("microphones").disabled = synthetic; $("permission").textContent = synthetic ? "NOT USED" : "NOT REQUESTED"; }

document.querySelectorAll(".mode").forEach(button => button.addEventListener("click", () => setMode(button.dataset.mode)));
$("startSession").addEventListener("click", createSession); $("stopSession").addEventListener("click", stopSession); $("connect").addEventListener("click", connect); $("disconnect").addEventListener("click", () => disconnect());
document.querySelectorAll("[data-signal]").forEach(button => button.addEventListener("click", () => sendSynthetic(button.dataset.signal)));
$("interrupt").addEventListener("click", () => { state.shouldReconnect = false; if (state.audioWs) state.audioWs.close(1011, "synthetic interruption"); }); $("reconnect").addEventListener("click", connect);
$("clearLogs").addEventListener("click", () => { state.logs = []; renderLogs(); });
$("exportLogs").addEventListener("click", () => { const report = { exportedAt: new Date().toISOString(), sessionId: state.session?.sessionId || null, maskedPhone: state.session?.maskedPhone || null, mode: state.mode, note: "No raw audio, token, or unmasked phone is included.", events: state.logs }; const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: "application/json" })); link.download = `callguard-report-${state.session?.sessionId || "empty"}.json`; link.click(); URL.revokeObjectURL(link.href); });
window.addEventListener("pagehide", () => {
  disconnect(); if (state.eventWs) state.eventWs.close();
  if (state.session?.status === "ACTIVE" && state.token) fetch(`/listener/api/sessions/${state.session.sessionId}/stop`, { method: "POST", headers: apiHeaders(), keepalive: true }).catch(() => {});
});
setInterval(() => { refreshSession(); $("connectedFor").textContent = state.connectedAt && state.audioWs ? formatDuration((Date.now() - state.connectedAt) / 1000) : "00:00"; }, 400);
fetch("/health").then(r => r.json()).then(() => { $("serviceBadge").textContent = "SERVICE ONLINE"; $("serviceBadge").className = "badge ok"; }).catch(() => { $("serviceBadge").textContent = "SERVICE OFFLINE"; $("serviceBadge").className = "badge bad"; });

