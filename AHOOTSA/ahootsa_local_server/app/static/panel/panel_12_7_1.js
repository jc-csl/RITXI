const state = {
  bootstrap: null,
  selectedLevel: "initial",
  selectedUserId: null,
  selectedUser: null,
  latestReportUrls: null,
  refreshTimer: null,
};

const $ = (id) => document.getElementById(id);

const fieldDefinitions = [
  { key: "name", label: "Nombre completo", scope: "user", required: true },
  { key: "preferred_name", label: "Nombre usado por Aocha", scope: "user" },
  { key: "external_id", label: "Identificador", scope: "user", required: true },
  { key: "language", label: "Idioma", scope: "user", required: true },
  { key: "notes", label: "Notas", scope: "user", multiline: true },
  {
    key: "communication_style",
    label: "Estilo",
    scope: "profile",
    options: [
      ["simple", "Sencillo"],
      ["standard", "Estándar"],
    ],
  },
  {
    key: "speech_speed",
    label: "Velocidad",
    scope: "profile",
    options: [
      ["slow", "Lenta"],
      ["normal", "Normal"],
      ["fast", "Rápida"],
    ],
  },
  {
    key: "response_wait_seconds",
    label: "Espera en segundos",
    scope: "profile",
    type: "number",
    min: 1,
    max: 30,
    step: 0.5,
  },
  {
    key: "preferred_interaction_mode",
    label: "Interacción",
    scope: "profile",
    options: [
      ["voice", "Voz"],
      ["touch", "Táctil"],
      ["mixed", "Mixta"],
    ],
  },
  {
    key: "preferred_reinforcement",
    label: "Refuerzo preferido",
    scope: "profile",
  },
  { key: "interests", label: "Intereses", scope: "profile", multiline: true },
  {
    key: "avoid_topics",
    label: "Temas que evitar",
    scope: "profile",
    multiline: true,
  },
  {
    key: "accessibility_notes",
    label: "Apoyos y accesibilidad",
    scope: "profile",
    multiline: true,
  },
  {
    key: "max_instructions_per_turn",
    label: "Instrucciones por turno",
    scope: "profile",
    type: "number",
    min: 1,
    max: 5,
    step: 1,
  },
];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showToast(message, error = false) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.remove("hidden", "error");
  if (error) toast.classList.add("error");
  window.setTimeout(() => toast.classList.add("hidden"), 4500);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

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
    ? `<strong>${escapeHtml(level.title)}</strong><br>${escapeHtml(level.objective)}<br><small>Máximo de opciones: ${escapeHtml(level.max_options)}</small>`
    : "Selecciona una actividad y un nivel.";
}

function setSessionControls(active, prepared = false) {
  $("launchAppButton").disabled = !active || !prepared;
  $("finishButton").disabled = !active;
  document.querySelectorAll(".track").forEach((button) => {
    button.disabled = !active;
  });

  $("sessionBadge").textContent = active ? "Sesión activa" : "Sin sesión";
  $("sessionBadge").className = `badge ${active ? "active" : "neutral"}`;
}

function renderCounters(summary) {
  const counts = summary?.counts || {};
  const labels = [
    ["A", counts.adequate || 0],
    ["P", counts.partial || 0],
    ["I", counts.incorrect || 0],
    ["SR", counts.no_response || 0],
    ["Pi", counts.hint || 0],
    ["R", counts.repeat || 0],
    ["E", counts.example || 0],
  ];

  $("liveCounters").innerHTML = labels
    .map(
      ([label, value]) =>
        `<span class="counter">${label}: <strong>${value}</strong></span>`,
    )
    .join("");
}

function renderBlockingStatus() {
  const blocking = state.bootstrap?.blocking_state;
  if (!blocking) {
    $("blockingStatus").textContent = "Sin datos";
    return;
  }

  if (blocking.can_prepare) {
    $("blockingStatus").textContent = "Libre para preparar otra sesión";
    $("prepareButton").disabled = false;
  } else if (blocking.database_active_session) {
    $("blockingStatus").textContent =
      `Sesión ${blocking.database_active_session} activa`;
    $("prepareButton").disabled = true;
  } else if (blocking.conversation_app_running) {
    $("blockingStatus").textContent =
      "Conversation App activa; ciérrala o pulsa Liberar";
    $("prepareButton").disabled = true;
  } else {
    $("blockingStatus").textContent =
      "Hay datos de sesión pendientes; pulsa Liberar";
    $("prepareButton").disabled = true;
  }
}

function getFieldValue(definition) {
  if (!state.selectedUser) return null;
  if (definition.scope === "profile") {
    return state.selectedUser.profile?.[definition.key] ?? null;
  }
  return state.selectedUser[definition.key] ?? null;
}

function optionLabel(definition, value) {
  if (!definition.options) return value;
  const option = definition.options.find(([key]) => key === value);
  return option ? option[1] : value;
}

function renderUserFields() {
  const container = $("userFields");
  container.innerHTML = "";

  if (!state.selectedUser) {
    container.innerHTML =
      '<div class="muted-box session-info">Crea o selecciona una persona.</div>';
    return;
  }

  fieldDefinitions.forEach((definition) => {
    const value = getFieldValue(definition);
    const displayValue = optionLabel(definition, value);
    const card = document.createElement("article");
    card.className = "field-card";
    card.dataset.key = definition.key;
    card.dataset.scope = definition.scope;

    card.innerHTML = `
      <span class="field-label">${escapeHtml(definition.label)}</span>
      <div class="field-value ${value === null || value === "" ? "empty" : ""}">
        ${value === null || value === "" ? "Sin información" : escapeHtml(displayValue)}
      </div>
      <div class="field-actions">
        <button type="button" class="edit-field">Editar</button>
        ${
          definition.required
            ? ""
            : '<button type="button" class="clear-field">Vaciar</button>'
        }
      </div>
    `;

    card.addEventListener("dblclick", (event) => {
      if (!event.target.closest("button")) beginFieldEdit(card, definition);
    });

    card.querySelector(".edit-field").addEventListener("click", () => {
      beginFieldEdit(card, definition);
    });

    card.querySelector(".clear-field")?.addEventListener("click", () => {
      clearField(definition);
    });

    container.appendChild(card);
  });
}

function editorControl(definition, value) {
  if (definition.options) {
    const options = definition.options
      .map(
        ([key, label]) =>
          `<option value="${escapeHtml(key)}" ${key === value ? "selected" : ""}>${escapeHtml(label)}</option>`,
      )
      .join("");
    return `<select data-editor>${options}</select>`;
  }

  if (definition.multiline) {
    return `<textarea data-editor rows="3">${escapeHtml(value ?? "")}</textarea>`;
  }

  const type = definition.type || "text";
  const min = definition.min !== undefined ? `min="${definition.min}"` : "";
  const max = definition.max !== undefined ? `max="${definition.max}"` : "";
  const step = definition.step !== undefined ? `step="${definition.step}"` : "";

  return `<input data-editor type="${type}" value="${escapeHtml(value ?? "")}" ${min} ${max} ${step}>`;
}

function beginFieldEdit(card, definition) {
  if (card.classList.contains("editing")) return;

  const value = getFieldValue(definition);
  card.classList.add("editing");
  card.innerHTML = `
    <span class="field-label">${escapeHtml(definition.label)}</span>
    <div class="field-editor">
      ${editorControl(definition, value)}
      <div class="field-editor-actions">
        <button type="button" class="save-field">Guardar</button>
        ${
          definition.required
            ? ""
            : '<button type="button" class="clear-field">Vaciar</button>'
        }
        <button type="button" class="cancel-field">Cancelar</button>
      </div>
    </div>
  `;

  const editor = card.querySelector("[data-editor]");
  editor.focus();
  if (editor.select) editor.select();

  card.querySelector(".save-field").addEventListener("click", () => {
    saveField(definition, editor.value);
  });
  card.querySelector(".cancel-field").addEventListener("click", renderUserFields);
  card.querySelector(".clear-field")?.addEventListener("click", () => {
    clearField(definition);
  });

  editor.addEventListener("keydown", (event) => {
    if (event.key === "Escape") renderUserFields();
    if (event.key === "Enter" && !definition.multiline) {
      event.preventDefault();
      saveField(definition, editor.value);
    }
  });
}

async function saveField(definition, rawValue) {
  if (!state.selectedUserId) return;

  let value = rawValue;
  if (definition.type === "number") {
    value = Number(rawValue);
  } else {
    value = rawValue.trim();
  }

  if (definition.required && (value === "" || value === null)) {
    showToast(`${definition.label} no puede quedar vacío.`, true);
    return;
  }

  const oldId = state.selectedUserId;

  try {
    const path =
      definition.scope === "profile"
        ? `/panel/api/users/${encodeURIComponent(oldId)}/profile`
        : `/panel/api/users/${encodeURIComponent(oldId)}`;

    const result = await api(path, {
      method: "PUT",
      body: JSON.stringify({ [definition.key]: value }),
    });

    state.selectedUserId = result.user.external_id;
    showToast(`${definition.label} guardado.`);
    await loadBootstrap(state.selectedUserId);
  } catch (error) {
    showToast(error.message, true);
    renderUserFields();
  }
}

async function clearField(definition) {
  if (!state.selectedUserId || definition.required) return;
  if (!window.confirm(`¿Vaciar el campo "${definition.label}"?`)) return;

  try {
    const path =
      definition.scope === "profile"
        ? `/panel/api/users/${encodeURIComponent(state.selectedUserId)}/profile`
        : `/panel/api/users/${encodeURIComponent(state.selectedUserId)}`;

    await api(path, {
      method: "PUT",
      body: JSON.stringify({ [definition.key]: null }),
    });

    showToast(`${definition.label} vaciado.`);
    await loadBootstrap(state.selectedUserId);
  } catch (error) {
    showToast(error.message, true);
  }
}

function populateUsers(preferredId = null) {
  const userSelect = $("userSelect");
  const users = state.bootstrap?.users || [];
  const target =
    preferredId ||
    state.selectedUserId ||
    userSelect.value ||
    users[0]?.external_id ||
    null;

  userSelect.innerHTML = users.length
    ? users
        .map(
          (user) =>
            `<option value="${escapeHtml(user.external_id)}">${escapeHtml(user.preferred_name)} · ${escapeHtml(user.external_id)}</option>`,
        )
        .join("")
    : '<option value="">No hay personas</option>';

  if (target && users.some((user) => user.external_id === target)) {
    userSelect.value = target;
  }

  state.selectedUserId = userSelect.value || null;
  state.selectedUser =
    users.find((user) => user.external_id === state.selectedUserId) || null;

  renderUserFields();
}

function populateActivities() {
  const activitySelect = $("activitySelect");
  const activities = state.bootstrap?.activities || [];
  const previous = activitySelect.value;

  activitySelect.innerHTML = activities
    .map(
      (activity) =>
        `<option value="${escapeHtml(activity.key)}">${escapeHtml(activity.title)}</option>`,
    )
    .join("");

  if (previous && activities.some((item) => item.key === previous)) {
    activitySelect.value = previous;
  }

  renderLevelDescription();
}

function renderActiveSession(active) {
  if (!active) {
    setSessionControls(false, false);
    renderCounters(null);
    $("preparedDetails").textContent = "No hay una sesión preparada.";
    return;
  }

  setSessionControls(active.status === "active", Boolean(active.profile_prepared));
  renderCounters(active);

  const activity = active.activity || {};
  $("preparedDetails").innerHTML = `
    <strong>Sesión ${active.session_id}</strong><br>
    ${escapeHtml(active.user.preferred_name)} ·
    ${escapeHtml(activity.title || activity.key || "Sin actividad")} ·
    ${escapeHtml(activity.level_title || activity.level || "Sin nivel")}
  `;

  if (active.user?.external_id) {
    state.selectedUserId = active.user.external_id;
  }
}

async function loadBootstrap(preferredUserId = null) {
  try {
    const data = await api("/panel/api/bootstrap");
    state.bootstrap = data;

    $("version").textContent = data.version;
    setDot("serverDot", data.services.local_server.running);
    setDot("daemonDot", data.services.daemon.running);
    setDot("appDot", data.services.conversation_app.running);

    renderActiveSession(data.active_session);
    populateUsers(preferredUserId);
    populateActivities();
    renderBlockingStatus();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function createUser() {
  const name = $("newName").value.trim();
  if (!name) {
    showToast("Escribe el nombre de la persona.", true);
    return;
  }

  try {
    const result = await api("/panel/api/users", {
      method: "POST",
      body: JSON.stringify({
        name,
        preferred_name: $("newPreferredName").value.trim() || null,
        external_id: $("newExternalId").value.trim() || null,
        language: $("newLanguage").value.trim() || "es",
        notes: $("newNotes").value.trim() || null,
      }),
    });

    $("newUserDialog").close();
    $("newUserForm").reset();
    $("newLanguage").value = "es";
    showToast("Persona creada correctamente.");
    await loadBootstrap(result.user.external_id);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function deleteCurrentUser() {
  if (!state.selectedUserId) {
    showToast("No hay una persona seleccionada.", true);
    return;
  }

  const name = state.selectedUser?.preferred_name || state.selectedUserId;
  if (!window.confirm(`¿Borrar u ocultar la ficha de ${name}?`)) return;

  try {
    const result = await api(
      `/panel/api/users/${encodeURIComponent(state.selectedUserId)}`,
      { method: "DELETE" },
    );

    showToast(result.message);
    state.selectedUserId = null;
    await loadBootstrap();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function prepareSession() {
  const user = $("userSelect").value;
  const activity = $("activitySelect").value;
  const startedBy = $("professionalInput").value.trim() || "Monitor/a";

  if (!user) {
    showToast("Selecciona o crea una persona.", true);
    return;
  }

  try {
    const result = await api("/panel/api/session/prepare", {
      method: "POST",
      body: JSON.stringify({
        user_external_id: user,
        activity,
        level: state.selectedLevel,
        started_by: startedBy,
      }),
    });

    $("preparedDetails").innerHTML = `
      <strong>Sesión ${result.session_id} preparada</strong><br>
      ${escapeHtml(result.preferred_name)} · ${escapeHtml(result.activity_title)} ·
      ${escapeHtml(result.level_title)}
    `;
    showToast("Sesión preparada.");
    await loadBootstrap(user);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function launch(path, label) {
  try {
    const result = await api(path, {
      method: "POST",
      body: "{}",
    });
    showToast(result.message || label);
    window.setTimeout(() => loadBootstrap(), 1800);
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

function renderFinalResult(result) {
  const report = result.report || {};
  const reportOk = Boolean(report.generated);
  state.latestReportUrls = report.urls || null;

  $("sessionBadge").textContent = "Sesión finalizada";
  $("sessionBadge").className = "badge finished";
  $("finalSummary").innerHTML = `
    <strong>Sesión ${result.session_id} finalizada</strong><br>
    Duración: ${escapeHtml(result.duration_minutes)} min ·
    Adecuadas: ${escapeHtml(result.counts?.adequate || 0)} ·
    Parciales: ${escapeHtml(result.counts?.partial || 0)} ·
    Incorrectas: ${escapeHtml(result.counts?.incorrect || 0)}<br>
    ${
      reportOk
        ? "Informe PDF, HTML, JSON y transcripción generados."
        : `Sesión liberada. Aviso del informe: ${escapeHtml(report.error || report.stderr || "no completado")}`
    }
  `;

  $("reportActions").classList.toggle("hidden", !reportOk);
}

async function finishSession() {
  if (!window.confirm(
    "Se cerrará la Conversation App, se finalizará la sesión y se generará el informe. ¿Continuar?",
  )) return;

  $("finishButton").disabled = true;
  $("finishButton").textContent = "Finalizando…";

  try {
    const result = await api("/panel/api/session/finish", {
      method: "POST",
      body: JSON.stringify({
        note: $("finalNote").value.trim() || null,
        decision: $("decisionSelect").value,
      }),
    });

    renderFinalResult(result);
    showToast(
      result.report?.generated
        ? "Sesión finalizada e informe generado."
        : "Sesión finalizada; revisa el aviso del informe.",
      !result.report?.generated,
    );

    await loadBootstrap();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    $("finishButton").textContent =
      "Finalizar, cerrar conversación y generar informe";
    renderBlockingStatus();
  }
}

async function recoverSession() {
  if (!window.confirm(
    "Se cerrará la Conversation App y se limpiará cualquier sesión bloqueada. ¿Continuar?",
  )) return;

  try {
    const result = await api("/panel/api/session/recover", {
      method: "POST",
      body: "{}",
    });

    if (result.session_id) {
      renderFinalResult(result);
    }

    showToast("Bloqueo liberado. Ya se puede preparar otra sesión.");
    await loadBootstrap();
  } catch (error) {
    showToast(error.message, true);
  }
}

function openReport(type) {
  const url = state.latestReportUrls?.[type];
  if (!url) {
    showToast("Ese informe todavía no está disponible.", true);
    return;
  }
  window.open(url, "_blank");
}

$("refreshButton").addEventListener("click", () => loadBootstrap());
$("userSelect").addEventListener("change", () => {
  state.selectedUserId = $("userSelect").value || null;
  state.selectedUser =
    state.bootstrap?.users?.find(
      (user) => user.external_id === state.selectedUserId,
    ) || null;
  renderUserFields();
});

$("activitySelect").addEventListener("change", renderLevelDescription);

$("levelSelector").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-level]");
  if (!button) return;

  state.selectedLevel = button.dataset.level;
  document.querySelectorAll(".level").forEach((item) => {
    item.classList.toggle("active", item === button);
  });
  renderLevelDescription();
});

$("newUserButton").addEventListener("click", () => {
  $("newUserDialog").showModal();
  $("newName").focus();
});

$("saveNewUserButton").addEventListener("click", (event) => {
  event.preventDefault();
  createUser();
});

$("deleteUserButton").addEventListener("click", deleteCurrentUser);

$("exampleUserButton").addEventListener("click", async () => {
  try {
    const result = await api("/panel/api/example-user", {
      method: "POST",
      body: JSON.stringify({}),
    });
    showToast(
      result.created
        ? "Usuario de ejemplo creado."
        : "El usuario de ejemplo ya existía.",
    );
    await loadBootstrap(result.external_id);
  } catch (error) {
    showToast(error.message, true);
  }
});

$("prepareButton").addEventListener("click", prepareSession);
$("launchDaemonButton").addEventListener("click", () =>
  launch("/panel/api/launch/daemon", "Daemon iniciado"),
);
$("launchAppButton").addEventListener("click", () =>
  launch("/panel/api/launch/conversation-app", "Conversation App iniciada"),
);
$("openOfficialButton").addEventListener("click", () =>
  window.open("http://127.0.0.1:7860", "_blank"),
);
$("openDocsButton").addEventListener("click", () =>
  window.open("http://127.0.0.1:8100/docs", "_blank"),
);
$("recoverButton").addEventListener("click", recoverSession);

document.querySelectorAll(".track").forEach((button) => {
  button.addEventListener("click", () => quickEvent(button.dataset.action));
});

$("finishButton").addEventListener("click", finishSession);

document.querySelectorAll("[data-report]").forEach((button) => {
  button.addEventListener("click", () => openReport(button.dataset.report));
});

setSessionControls(false, false);
loadBootstrap();
state.refreshTimer = window.setInterval(() => loadBootstrap(), 7000);
