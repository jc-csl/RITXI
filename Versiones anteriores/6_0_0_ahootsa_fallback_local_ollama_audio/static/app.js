
let sessionId = localStorage.getItem("ahootsa6_session_id") || crypto.randomUUID();
localStorage.setItem("ahootsa6_session_id", sessionId);

const chat = document.getElementById("chat");
const textInput = document.getElementById("textInput");
const statusBadge = document.getElementById("statusBadge");
const statusText = document.getElementById("statusText");
const memoryBoard = document.getElementById("memoryBoard");

let recognition = null;
let listening = false;
let preferredVoice = null;

function addMessage(text, who, meta = "") {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.innerHTML = `${escapeHtml(text)}${meta ? `<span class="meta">${escapeHtml(meta)}</span>` : ""}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;" }[c]));
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
  } catch (e) {
    const msg = "No puedo contactar con el servidor local. Revisa que Ahootsa 6 esté arrancado.";
    addMessage(msg, "bot", "error");
    speak(msg);
  }
}

function setupRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    addMessage("Este navegador no permite reconocimiento de voz. Usa Chrome o escribe el texto.", "bot", "sistema");
    return null;
  }
  const rec = new SpeechRecognition();
  rec.lang = "es-ES";
  rec.continuous = false;
  rec.interimResults = false;
  rec.maxAlternatives = 1;

  rec.onstart = () => {
    listening = true;
    document.getElementById("btnMic").textContent = "🎙️ Escuchando...";
  };
  rec.onend = () => {
    listening = false;
    document.getElementById("btnMic").textContent = "🎙️ Hablar";
  };
  rec.onerror = (e) => {
    addMessage("No he podido escuchar bien. Puedes repetir o escribirlo.", "bot", e.error || "audio");
  };
  rec.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    sendMessage(transcript);
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

document.getElementById("btnSend").onclick = () => sendMessage();
textInput.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

document.getElementById("btnMic").onclick = () => {
  if (!recognition) recognition = setupRecognition();
  if (!recognition) return;
  if (listening) recognition.stop();
  else recognition.start();
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

renderMemory();
status();
setInterval(status, 15000);
addMessage("Hola. Soy Ahootsa en modo local. Pulsa Hablar o escribe un mensaje.", "bot", "sistema");
