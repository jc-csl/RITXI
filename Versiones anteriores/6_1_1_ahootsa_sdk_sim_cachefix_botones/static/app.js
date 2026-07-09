console.log("Ahootsa UI JS version 6.1.1 loaded");

let sessionId = localStorage.getItem("ahootsa6_session_id") || crypto.randomUUID();
localStorage.setItem("ahootsa6_session_id", sessionId);

const chat = document.getElementById("chat");
const textInput = document.getElementById("textInput");
const statusBadge = document.getElementById("statusBadge");
const statusText = document.getElementById("statusText");
const robotText = document.getElementById("robotText");
const memoryBoard = document.getElementById("memoryBoard");
const micSelect = document.getElementById("micSelect");
const micLevel = document.getElementById("micLevel");
const micStatus = document.getElementById("micStatus");

let recognition = null;
let listening = false;
let preferredVoice = null;
let selectedMicId = null;
let audioContext = null;
let meterStream = null;

function addMessage(text, who, meta = "") {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.innerHTML = `${escapeHtml(text)}${meta ? `<span class="meta">${escapeHtml(meta)}</span>` : ""}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;" }[c]));
}

function pickVoice() {
  const voices = window.speechSynthesis ? speechSynthesis.getVoices() : [];
  preferredVoice =
    voices.find(v => /spanish|español|es-|es_/i.test(v.lang + " " + v.name)) ||
    voices.find(v => /pablo|helena|alvaro|laura|spanish/i.test(v.name)) ||
    voices[0] ||
    null;
}
if ("speechSynthesis" in window) {
  speechSynthesis.onvoiceschanged = pickVoice;
  pickVoice();
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "es-ES";
  u.rate = 0.95;
  u.pitch = 1.0;
  if (preferredVoice) u.voice = preferredVoice;
  speechSynthesis.speak(u);
}

async function status() {
  try {
    const r = await fetch("/api/status");
    const s = await r.json();
    statusText.textContent = JSON.stringify(s, null, 2);
    if (s.ollama.ok && s.ollama.model_available) {
      statusBadge.textContent = "Local OK";
      statusBadge.style.color = "#137333";
    } else if (s.ollama.ok) {
      statusBadge.textContent = "Ollama OK, modelo no encontrado";
      statusBadge.style.color = "#b54708";
    } else {
      statusBadge.textContent = "Ollama no conectado";
      statusBadge.style.color = "#b42318";
    }
  } catch (e) {
    statusBadge.textContent = "Servidor no disponible";
    statusText.textContent = String(e);
  }
}

async function sendMessage(message) {
  const text = (message || textInput.value).trim();
  if (!text) return;
  textInput.value = "";
  addMessage(text, "user");

  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId })
    });
    const data = await r.json();
    sessionId = data.session_id;
    localStorage.setItem("ahootsa6_session_id", sessionId);
    addMessage(data.reply, "bot", data.source);
    if (data.speak) speak(data.reply);
    if (/hola|buenas|kaixo/i.test(text)) {
      robotAction("saludo", true);
    }
  } catch (e) {
    const msg = "No puedo contactar con el servidor local. Revisa que Ahootsa 6 esté arrancado.";
    addMessage(msg, "bot", "error");
    speak(msg);
  }
}

async function populateMics() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
    micStatus.textContent = "El navegador no permite listar micrófonos.";
    return;
  }
  try {
    // Permission prompt, needed to reveal labels.
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(t => t.stop());

    const devices = await navigator.mediaDevices.enumerateDevices();
    const mics = devices.filter(d => d.kind === "audioinput");
    micSelect.innerHTML = "";
    if (mics.length === 0) {
      micSelect.innerHTML = `<option value="">No hay micrófonos</option>`;
      micStatus.textContent = "No se detectan micrófonos.";
      return;
    }
    for (const mic of mics) {
      const opt = document.createElement("option");
      opt.value = mic.deviceId;
      opt.textContent = mic.label || `Micrófono ${micSelect.length + 1}`;
      micSelect.appendChild(opt);
    }
    selectedMicId = micSelect.value;
    micStatus.textContent = `Micrófono listo: ${micSelect.options[micSelect.selectedIndex]?.textContent || ""}`;
    startMeter();
  } catch (e) {
    micStatus.textContent = "Permiso de micro denegado o no disponible.";
    addMessage("No tengo permiso de micrófono. En Chrome/Edge pulsa el candado de la barra de direcciones y permite el micrófono.", "bot", "micro");
  }
}

async function startMeter() {
  try {
    if (meterStream) meterStream.getTracks().forEach(t => t.stop());
    const constraints = selectedMicId ? { audio: { deviceId: { exact: selectedMicId } } } : { audio: true };
    meterStream = await navigator.mediaDevices.getUserMedia(constraints);
    audioContext = audioContext || new AudioContext();
    const source = audioContext.createMediaStreamSource(meterStream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);

    const data = new Uint8Array(analyser.frequencyBinCount);
    function tick() {
      analyser.getByteTimeDomainData(data);
      let sum = 0;
      for (const v of data) {
        const x = v - 128;
        sum += x * x;
      }
      const rms = Math.sqrt(sum / data.length);
      const pct = Math.min(100, Math.round(rms * 4));
      micLevel.style.width = `${pct}%`;
      requestAnimationFrame(tick);
    }
    tick();
  } catch (e) {
    micStatus.textContent = "No puedo activar medidor de micro.";
  }
}

function setupRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    addMessage("Este navegador no permite reconocimiento de voz. Prueba Chrome/Edge o usa el dictado de Windows con Win + H sobre la caja de texto.", "bot", "sistema");
    return null;
  }
  const rec = new SpeechRecognition();
  rec.lang = "es-ES";
  rec.continuous = false;
  rec.interimResults = true;
  rec.maxAlternatives = 1;

  rec.onstart = () => {
    listening = true;
    document.getElementById("btnMic").textContent = "🎙️ Escuchando...";
    micStatus.textContent = "Escuchando. Habla ahora.";
  };
  rec.onend = () => {
    listening = false;
    document.getElementById("btnMic").textContent = "🎙️ Hablar";
    micStatus.textContent = "Escucha parada.";
  };
  rec.onerror = (e) => {
    micStatus.textContent = `Error micro/STT: ${e.error || "audio"}`;
    addMessage("No he podido convertir tu voz a texto. Revisa permisos de micrófono o usa Win + H en la caja de texto.", "bot", e.error || "audio");
  };
  rec.onresult = (e) => {
    let finalText = "";
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) finalText += t;
      else interim += t;
    }
    if (interim) {
      micStatus.textContent = `Oyendo: ${interim}`;
    }
    if (finalText.trim()) {
      micStatus.textContent = `Reconocido: ${finalText}`;
      sendMessage(finalText);
    }
  };
  return rec;
}

function renderMemory() {
  memoryBoard.innerHTML = "";
  for (let i = 1; i <= 8; i++) {
    const div = document.createElement("div");
    div.className = "card";
    div.textContent = i;
    memoryBoard.appendChild(div);
  }
}

async function startActivity(level) {
  const r = await fetch("/api/activities/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ level, session_id: sessionId })
  });
  const data = await r.json();
  sessionId = data.session_id;
  localStorage.setItem("ahootsa6_session_id", sessionId);
  addMessage(data.reply, "bot", "actividad");
  speak(data.reply);
  robotAction("nod", true);
}

async function startMemory() {
  renderMemory();
  const r = await fetch("/api/memory/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ game: "animales", session_id: sessionId })
  });
  const data = await r.json();
  sessionId = data.session_id;
  addMessage(data.reply, "bot", "memory");
  speak(data.reply);
  robotAction("wiggle", true);
}

async function pickMemory() {
  const first = Number(document.getElementById("cardA").value);
  const second = Number(document.getElementById("cardB").value);
  const r = await fetch("/api/memory/pick", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ first, second, session_id: sessionId })
  });
  const data = await r.json();
  addMessage(`Cartas ${first} y ${second}`, "user");
  addMessage(data.reply, "bot", "memory");
  speak(data.reply);
}

async function robotStatus() {
  try {
    robotText.textContent = "[UI 6.1.1] Consultando estado robot...";
    const r = await fetch("/api/robot/status", { cache: "no-store" });
    const data = await r.json();
    robotText.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    robotText.textContent = `[UI 6.1.1] Error estado robot:\n${String(e)}`;
  }
}

async function robotProbe() {
  try {
    robotText.textContent = "[UI 6.1.1] Probando SDK...";
    const r = await fetch("/api/robot/probe", { method: "POST", cache: "no-store" });
    const data = await r.json();
    robotText.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    robotText.textContent = `[UI 6.1.1] Error en SDK probe:\n${String(e)}`;
  }
}

async function robotAction(action, silent = false) {
  try {
    robotText.textContent = `[UI 6.1.1] Ejecutando ${action}...\nSi este texto aparece, el botón funciona y estamos esperando respuesta del backend.`;
    const r = await fetch(`/api/robot/action/${action}`, { method: "POST", cache: "no-store" });
    const data = await r.json();
    robotText.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    robotText.textContent = `[UI 6.1.1] Error llamando a accion ${action}:\n${String(e)}`;
  }
}

document.getElementById("btnSend").onclick = () => sendMessage();
textInput.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

document.getElementById("btnMic").onclick = async () => {
  await populateMics();
  if (!recognition) recognition = setupRecognition();
  if (!recognition) return;
  if (listening) recognition.stop();
  else recognition.start();
};

micSelect.onchange = () => {
  selectedMicId = micSelect.value;
  startMeter();
};

document.getElementById("btnStop").onclick = () => {
  if ("speechSynthesis" in window) speechSynthesis.cancel();
};

document.getElementById("btnReset").onclick = async () => {
  await fetch("/api/session/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId })
  });
  sessionId = crypto.randomUUID();
  localStorage.setItem("ahootsa6_session_id", sessionId);
  chat.innerHTML = "";
  addMessage("Sesión reiniciada. Te escucho.", "bot", "sistema");
};

document.querySelectorAll(".quick button[data-msg]").forEach(b => {
  b.onclick = () => sendMessage(b.dataset.msg);
});
document.querySelectorAll(".levels button").forEach(b => {
  b.onclick = () => startActivity(b.dataset.level);
});
document.getElementById("btnMemory").onclick = startMemory;
document.getElementById("btnPick").onclick = pickMemory;

document.getElementById("btnRobotStatus").onclick = robotStatus;
document.getElementById("btnRobotProbe").onclick = robotProbe;
document.querySelectorAll("[data-robot]").forEach(b => {
  b.onclick = () => robotAction(b.dataset.robot);
});

renderMemory();
status();
robotStatus();
populateMics();
setInterval(status, 15000);
addMessage("Hola. Soy Ahootsa 6.1.1. Los botones SDK muestran primero EJECUTANDO y luego resultado. Si el micro no transcribe, usa Win + H.", "bot", "sistema");
