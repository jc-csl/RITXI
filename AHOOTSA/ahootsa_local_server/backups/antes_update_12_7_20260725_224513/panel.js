const state = {
  bootstrap: null,
  selectedLevel: "initial",
  prepared: null,
};

const $ = (id) => document.getElementById(id);

function showToast(message, error = false) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.remove("hidden", "error");
  if (error) toast.classList.add("error");
  window.setTimeout(() => toast.classList.add("hidden"), 4200);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const detail = body?.detail || body || `HTTP ${response.status}`;
    throw new Error(detail);
  }
  return body;
}

function setDot(id, running) {
  const dot = $(id);
  dot.classList.toggle("ok", Boolean(running));
  dot.classList.toggle("off", !running);
}

function selectedActivity() {
  const key = $("activitySelect").value;
  return state.bootstrap?.activities?.find((item) => item.key === key);
}

function renderLevelDescription() {
  const activity = selectedActivity();
  const level = activity?.levels?.[state.selectedLevel];
  $("levelDescription").innerHTML = level
    ? `<strong>${level.title}</strong><br>${level.objective}<br><small>Máximo de opciones: ${level.max_options}</small>`
    : "Selecciona una actividad y un nivel.";
}

function setSessionControls(active, prepared = false) {
  $("launchAppButton").disabled = !active || !prepared;
  $("finishButton").disabled = !active;
  document.querySelectorAll(".track").forEach((button) => button.disabled = !active);
  $("sessionBadge").textContent = active ? "Sesión activa" : "Sin sesión";
  $("sessionBadge").className = `badge ${active ? "active" : "neutral"}`;
}

function renderCounters(summary) {
  const counts = summary?.counts || {};
  const labels = [
    ["Adecuadas", counts.adequate || 0],
    ["Parciales", counts.partial || 0],
    ["Incorrectas", counts.incorrect || 0],
    ["Sin respuesta", counts.no_response || 0],
    ["Pistas", counts.hint || 0],
    ["Repeticiones", counts.repeat || 0],
    ["Ejemplos", counts.example || 0],
  ];
  $("liveCounters").innerHTML = labels.map(([label, value]) => `<span class="counter">${label}: <strong>${value}</strong></span>`).join("");
}

function renderActiveSession(active) {
  if (!active) {
    setSessionControls(false, false);
    renderCounters(null);
    return;
  }
  setSessionControls(active.status === "active", Boolean(active.profile_prepared));
  renderCounters(active);
  const activity = active.activity || {};
  $("preparedDetails").classList.remove("hidden");
  $("preparedDetails").innerHTML = `
    <strong>Sesión ${active.session_id}</strong><br>
    Usuario: ${active.user.preferred_name}<br>
    Actividad: ${activity.title || activity.key || "—"}<br>
    Nivel: ${activity.level_title || activity.level || "—"}
  `;
}

async function loadBootstrap() {
  try {
    const data = await api("/panel/api/bootstrap");
    state.bootstrap = data;
    $("version").textContent = data.version;
    setDot("serverDot", data.services.local_server.running);
    setDot("daemonDot", data.services.daemon.running);
    setDot("appDot", data.services.conversation_app.running);

    const userSelect = $("userSelect");
    const previousUser = userSelect.value;
    userSelect.innerHTML = data.users.length
      ? data.users.map((user) => `<option value="${user.external_id}">${user.preferred_name} · ${user.external_id}</option>`).join("")
      : `<option value="">No hay usuarios</option>`;
    if (previousUser && data.users.some((user) => user.external_id === previousUser)) userSelect.value = previousUser;

    const activitySelect = $("activitySelect");
    const previousActivity = activitySelect.value;
    activitySelect.innerHTML = data.activities.map((activity) => `<option value="${activity.key}">${activity.title}</option>`).join("");
    if (previousActivity && data.activities.some((activity) => activity.key === previousActivity)) activitySelect.value = previousActivity;

    renderLevelDescription();
    renderActiveSession(data.active_session);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function prepareSession() {
  const user = $("userSelect").value;
  const activity = $("activitySelect").value;
  const startedBy = $("professionalInput").value.trim() || "Monitor/a";
  if (!user) return showToast("Selecciona o crea una persona usuaria.", true);
  try {
    const result = await api("/panel/api/session/prepare", {
      method: "POST",
      body: JSON.stringify({ user_external_id: user, activity, level: state.selectedLevel, started_by: startedBy }),
    });
    state.prepared = result;
    $("preparedDetails").classList.remove("hidden");
    $("preparedDetails").innerHTML = `
      <strong>Sesión ${result.session_id} preparada</strong><br>
      Perfil activo fijo: <code>${result.profile_name}</code><br>
      Saludo inicial: “${result.greeting}”<br>
      Contexto: <code>${result.context_file}</code>
    `;
    setSessionControls(true, true);
    showToast("Sesión preparada en el perfil fijo ahootsa_session.");
    await loadBootstrap();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function launch(path, label) {
  try {
    const result = await api(path, { method: "POST", body: "{}" });
    showToast(result.message || label);
    window.setTimeout(loadBootstrap, 1800);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function quickEvent(action) {
  try {
    const note = $("eventNote").value.trim() || null;
    const result = await api("/panel/api/session/event", {
      method: "POST",
      body: JSON.stringify({ action, note }),
    });
    $("eventNote").value = "";
    renderCounters(result.summary);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function finishSession() {
  try {
    const result = await api("/panel/api/session/finish", {
      method: "POST",
      body: JSON.stringify({
        note: $("finalNote").value.trim() || null,
        decision: $("decisionSelect").value,
      }),
    });
    setSessionControls(false, false);
    $("sessionBadge").textContent = "Sesión finalizada";
    $("sessionBadge").className = "badge finished";
    $("finalSummary").classList.remove("hidden");
    $("finalSummary").innerHTML = `
      <strong>Sesión ${result.session_id} finalizada</strong><br>
      Duración de actividad: ${result.duration_minutes} min (${result.duration_source})<br>
      Adecuadas: ${result.counts.adequate} · Parciales: ${result.counts.partial} · Incorrectas: ${result.counts.incorrect}<br>
      Sin respuesta: ${result.counts.no_response} · Pistas: ${result.counts.hint} · Repeticiones: ${result.counts.repeat}<br>
      Decisión profesional: ${result.professional_decision || "sin decisión"}
    `;
    showToast("Sesión finalizada y guardada.");
    await loadBootstrap();
  } catch (error) {
    showToast(error.message, true);
  }
}

$("refreshButton").addEventListener("click", loadBootstrap);
$("activitySelect").addEventListener("change", renderLevelDescription);
$("levelSelector").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-level]");
  if (!button) return;
  state.selectedLevel = button.dataset.level;
  document.querySelectorAll(".level").forEach((item) => item.classList.toggle("active", item === button));
  renderLevelDescription();
});
$("prepareButton").addEventListener("click", prepareSession);
$("launchDaemonButton").addEventListener("click", () => launch("/panel/api/launch/daemon", "Daemon iniciado"));
$("launchAppButton").addEventListener("click", () => launch("/panel/api/launch/conversation-app", "Conversation App iniciada"));
$("openOfficialButton").addEventListener("click", () => window.open("http://127.0.0.1:7860", "_blank"));
$("openDocsButton").addEventListener("click", () => window.open("http://127.0.0.1:8100/docs", "_blank"));
$("exampleUserButton").addEventListener("click", async () => {
  try {
    const result = await api("/panel/api/example-user", { method: "POST", body: JSON.stringify({}) });
    showToast(result.created ? "Usuario de ejemplo creado." : "El usuario de ejemplo ya existía.");
    await loadBootstrap();
    $("userSelect").value = result.external_id;
  } catch (error) { showToast(error.message, true); }
});
document.querySelectorAll(".track").forEach((button) => button.addEventListener("click", () => quickEvent(button.dataset.action)));
$("finishButton").addEventListener("click", finishSession);

setSessionControls(false, false);
loadBootstrap();
window.setInterval(loadBootstrap, 6000);
